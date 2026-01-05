from datetime import datetime, timedelta
import time
import json
import logging
from sqlalchemy.orm import Session
from backend.shared.database import SessionLocal
from backend.features.project.persistence.models import LarkModelTP, LarkModelTCG, TCGRemovedTickets
from backend.shared.integration.lark_client import list_records

# Configure logger
logger = logging.getLogger(__name__)

from ...project.service.anomaly_service import AnomalyService

def get_latest_update_time(db: Session, model_class):
    # Each model is now dedicated to a single table, so no need to filter by table_id
    record = db.query(model_class).order_by(model_class.updated_at.desc()).first()
    if record:
        return record.updated_at
    return None

def normalize_lark_key(key: str) -> str:
    """
    Converts 'Ticket Number' to 'ticket_number'
    Converts 'Due Day (Quarter)' to 'due_day_quarter' (removing parens)
    """
    key = key.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
    return key

def extract_lark_value(value):
    """
    Smart extraction for Lark fields.
    - List of objects (Person/Select) -> Comma separated 'name' or 'text'
    - List of strings -> Comma separated
    - Complex dict -> json dump (fallback)
    """
    if isinstance(value, list):
        if not value:
            return None
        # Check first item type
        first = value[0]
        if isinstance(first, dict):
            # Try to grab readable name
            # Common keys: name (Person, Option), text (Text), id (sometimes)
            extracted = []
            for item in value:
                val = item.get("name") or item.get("text") or item.get("email")
                if val:
                    extracted.append(str(val))
                else:
                    # Fallback to json dump of item if no simple name
                    extracted.append(json.dumps(item, ensure_ascii=False))
            return ", ".join(extracted)
        else:
            return ", ".join([str(v) for v in value])
    
    if isinstance(value, dict):
         # Single object, try to get name/text
         return value.get("name") or value.get("text") or json.dumps(value, ensure_ascii=False)

    return value

def map_fields_to_model(model_instance, lark_fields):
    """
    Iterates over lark_fields, maps to model columns if they exist.
    """
    # Get all valid column names from the model
    # SQLAlchemy inspection or dir()
    valid_columns = {c.name for c in model_instance.__table__.columns}
    
    mapped_count = 0
    for key, value in lark_fields.items():
        # 0. Check for explicit mapping in model
        col_name = None
        if hasattr(model_instance, 'lark_mapping') and key in model_instance.lark_mapping:
            col_name = model_instance.lark_mapping[key]
        else:
            # 1. Normalize key
            col_name = normalize_lark_key(key)
        
        # 2. Check if valid column
        if col_name in valid_columns:
            # Extract/Convert value
            final_val = extract_lark_value(value)
            setattr(model_instance, col_name, final_val)
            mapped_count += 1
        
        # Special case: 'Updated Date' -> 'lark_updated_date' (if logic needed)
        # But 'updated_at' is handled separately usually.
        # In models.py TCG has 'lark_updated_date'.
        if key == "Updated Date" and "lark_updated_date" in valid_columns:
             setattr(model_instance, "lark_updated_date", str(value))
             mapped_count += 1
    
    # Debug: first record only
    if hasattr(model_instance, '_debug_logged'):
        return
    model_instance._debug_logged = True
    logger.debug(f"Mapped {mapped_count}/{len(lark_fields)} fields")
    logger.debug(f"Valid columns: {sorted(valid_columns)}")
    logger.debug("Sample mappings:")
    for key in list(lark_fields.keys())[:5]:
        col_name = normalize_lark_key(key)
        in_model = col_name in valid_columns
        logger.debug(f"  '{key}' -> '{col_name}' [{'✓' if in_model else '✗'}]")


def sync_lark_table(app_token: str, table_id: str, model_class, force_full: bool = False):
    table_name = model_class.__tablename__
    logger.info(f"Starting sync for table: {table_name} ({table_id}) [Force Full: {force_full}]")
    
    db = SessionLocal()
    try:
        latest_timestamp = None
        if not force_full:
                latest_timestamp = get_latest_update_time(db, model_class)
        
        # Prepare filter for incremental sync
        filter_obj = None
        if latest_timestamp and not force_full:
             # Sync records updated since yesterday (buffer for safety)
             one_day_ago_ms = int((datetime.now() - timedelta(days=1)).timestamp() * 1000)
             filter_dt = datetime.fromtimestamp(one_day_ago_ms/1000)
             date_str = filter_dt.strftime('%Y/%m/%d %H:%M:%S')
             # Construct JSON filter object for Lark Search API
             # Requirement: ["ExactDate", timestamp_ms] for DateTime fields with isGreater
             filter_obj = {
                 "conjunction": "and",
                 "conditions": [
                     {
                         "field_name": "Updated Date",
                         "operator": "isGreater",
                         "value": ["ExactDate", one_day_ago_ms]
                     }
                 ]
             }
             logger.info(f"Incremental sync enabled. Filter: Updated Date > {date_str} (Timestamp: {one_day_ago_ms})")
        else:
             logger.info("Full sync: Fetching all records.")

        # Pre-load removed tickets if syncing TCG table
        removed_tickets_set = set()
        if model_class == LarkModelTCG:
            removed = db.query(TCGRemovedTickets.ticket_number).all()
            removed_tickets_set = {r[0] for r in removed}
            if removed_tickets_set:
                logger.info(f"Loaded {len(removed_tickets_set)} removed tickets to ignore.")

        has_more = True
        page_token = None
        total_fetched = 0
        
        while has_more:
             # Pass filter_obj (dict) or None
             resp = list_records(app_token, table_id, filter_obj, page_token)
             
             if not resp or "items" not in resp:
                 logger.warning(f"No items found or error: {resp}")
                 break
                 
             records = resp.get("items", [])
             total_fetched += len(records)
             logger.info(f"Fetched {len(records)} records (Total: {total_fetched})")
             
             for item in records:
                 record_id = item["record_id"]
                 fields = item["fields"]
                 
                 # Check if ticket matches a removed ticket (TCG specific)
                 if model_class == LarkModelTCG:
                     # Attempt to find ticket number from fields
                     # Field name usually 'TCG Tickets' or 'TCG Ticket'
                     # Helper to extract value regardless of exact case/naming if possible, 
                     # but here we need to match what map_fields_to_model does or check raw field.
                     # From models.py: tcg_tickets. Lark field likely "TCG Tickets"
                     raw_ticket_val = fields.get("TCG Tickets") or fields.get("TCG Ticket")
                     if raw_ticket_val:
                         # normalize/extract string value similar to extract_lark_value logic?
                         # Or just check simple string. extract_lark_value handles lists.
                         # Let's use extract_lark_value to be safe on the format
                         ticket_num_str = extract_lark_value(raw_ticket_val)
                         # If it's a list string "TCG-123, TCG-456", might be tricky. usually 1 ticket.
                         # Split and check?
                         # Assuming simple case for now.
                         if ticket_num_str in removed_tickets_set:
                             logger.debug(f"Skipping removed ticket: {ticket_num_str}")
                             continue

                 updated_at_val = fields.get("Updated Date", 0) 
                 
                 existing = db.query(model_class).filter(model_class.record_id == record_id).first()
                 
                 if existing:
                     # Update
                     instance = existing
                     instance.updated_at = updated_at_val
                     # We might want to clear old fields if not utilizing JSON column anymore
                     # Or just overwrite attributes
                 else:
                     # Insert
                     instance = model_class(
                         record_id=record_id,
                         updated_at=updated_at_val
                     )
                     db.add(instance)
                
                 # Perform mapping
                 map_fields_to_model(instance, fields)
                 
                 # Also save raw fields into 'fields' JSON column if it exists in model (LarkBase has it)
                 if hasattr(instance, "fields"):
                     instance.fields = fields

             db.commit()
             
             # Pagination handling
             has_more = resp.get("has_more", False)
             if has_more:
                 page_token = resp.get("page_token")
                 if not page_token:
                     logger.warning("has_more=True but no page_token. Stopping pagination.")
                     break
                 logger.info("Fetching next page...")
             else:
                 logger.info(f"✓ Sync complete. Total: {total_fetched} records")
                 break 
        
        # Trigger Anomaly Detection if syncing TCG (or post-sync generally)
        if model_class == LarkModelTCG or model_class == LarkModelTP:
            logger.info("Triggering Anomaly Detection...")
            try:
                anomaly_service = AnomalyService(db)
                anomaly_service.refresh_anomalies()
                logger.info("Anomaly Detection Finished.")
            except Exception as ae:
                logger.error(f"Anomaly Detection Failed: {ae}")

    except Exception as e:
        logger.error(f"Error executing sync_lark_table: {e}", exc_info=True)
    finally:
        db.close()

def sync_jira_verification():
    """
    Verifies active TCG tickets (not Closed) against Jira.
    If a ticket returns 404 Not Found from Jira, it is deleted from the local DB.
    """
    logger.info("Starting Jira Verification Job...")
    from backend.shared.integration.jira_client import JiraService
    
    jira_service = JiraService()
    if not jira_service.jira:
        logger.warning("Jira Service not configured. Skipping verification.")
        return

    db = SessionLocal()
    try:
        # 1. Fetch active tickets (jira_status != 'Closed')
        # Note: adjust filter if 'Closed' case sensitivity varies (e.g. 'closed', 'Done')
        active_tickets = db.query(LarkModelTCG).filter(LarkModelTCG.jira_status != 'Closed').all()
        logger.info(f"Found {len(active_tickets)} active tickets to verify.")
        
        deleted_count = 0
        verified_count = 0
        
        for ticket in active_tickets:
            ticket_number = ticket.tcg_tickets
            if not ticket_number:
                continue

            # Verify with Jira
            issue = jira_service.get_ticket(ticket_number)
            
            if issue is None:
                # 404 Not Found -> Delete
                logger.warning(f"Ticket {ticket_number} not found in Jira. Deleting from DB and adding to Removed list.")
                
                # Add to Removed Tickets table
                try:
                    removed_ticket = TCGRemovedTickets(
                        ticket_number=ticket_number,
                        deleted_at=int(time.time() * 1000)
                    )
                    db.add(removed_ticket)
                    # Commit strictly after adding to ensure it's saved even if verification crashes later? 
                    # Actually we commit at the end.
                except Exception as e:
                    logger.error(f"Failed to add {ticket_number} to removed list: {e}")

                db.delete(ticket)
                deleted_count += 1
            else:
                verified_count += 1
            
            # Rate limiting / Sleep to be nice
            if verified_count % 10 == 0:
                time.sleep(0.5)

        db.commit()
        logger.info(f"Jira Verification Complete. Verified: {verified_count}, Deleted: {deleted_count}")

    except Exception as e:
        logger.error(f"Error in sync_jira_verification: {e}", exc_info=True)
    finally:
        db.close()

def calculate_tp_completion(db: Session = None):
    """
    Calculates completion percentage for 'In Progress' TP Projects.
    Formula: Count(Closed Tickets) / Count(Total Tickets) * 100
    Updates 'completed_percentage' column in TP_Projects.
    """
    logger.info("Starting TP Completion Calculation Job...")
    
    # If db session is not provided, create a new one (for scheduler usage)
    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True
        
    try:
        # 1. Get all In Progress TPs
        # Note: Checking multiple potential status fields based on models.py
        # jira_status seems to be the main status field for TPs usually, or 'status' if it existed.
        # models.py has 'jira_status'. Requirement says "status 'In Progress'".
        # I will assume jira_status is the one.
        in_progress_tps = db.query(LarkModelTP).filter(LarkModelTP.jira_status == "In Progress").all()
        logger.info(f"Found {len(in_progress_tps)} In Progress TPs to calculate.")
        
        updates_count = 0
        
        for tp in in_progress_tps:
            tp_number = tp.ticket_number
            if not tp_number:
                continue
                
            # 2. Find linked TCG Tickets
            # Assuming LarkModelTCG.tp_number links to LarkModelTP.ticket_number
            tickets = db.query(LarkModelTCG).filter(LarkModelTCG.tp_number == tp_number).all()
            
            total_tickets = len(tickets)
            if total_tickets == 0:
                # No tickets, percentage is 0 (or keep as is? Requirement implies calculation)
                # If no tickets, technically completion is 0% or N/A. Let's set to 0.
                new_percentage = 0
            else:
                # 3. Partition into FE and BE
                # Rule: Component contains "TAD TAC UI" -> FE, Else -> BE
                fe_tickets = []
                be_tickets = []
                
                for t in tickets:
                    comps = t.components or ""
                    if "TAD TAC UI" in comps:
                        fe_tickets.append(t)
                    else:
                        be_tickets.append(t)

                # 4. Calculate FE Stats
                fe_total = len(fe_tickets)
                new_fe_percentage = 0
                new_fe_all_open = False
                
                if fe_total > 0:
                    fe_closed = len([t for t in fe_tickets if t.jira_status == "Closed"])
                    new_fe_percentage = int((fe_closed / fe_total) * 100)
                    
                    # Check if all are Open
                    # Case sensitive check for "Open"
                    fe_open_count = len([t for t in fe_tickets if t.jira_status == "Open"])
                    if fe_open_count == fe_total:
                        new_fe_all_open = True
                else:
                    # No FE tickets -> 0% progress, and technically "all open" is false or n/a? 
                    # If no tasks, then the condition "frontend tasks completed % is 0 and status are all Open" 
                    # might be implicitly true or false depending on interpretation.
                    # If no tasks, % is 0. Status is N/A. Let's set 'all open' to False to avoid blinking if no tasks exist.
                    new_fe_percentage = 0
                    new_fe_all_open = False

                # 5. Calculate BE Stats
                be_total = len(be_tickets)
                new_be_percentage = 0
                if be_total > 0:
                    be_closed = len([t for t in be_tickets if t.jira_status == "Closed"])
                    new_be_percentage = int((be_closed / be_total) * 100)

                
                # 6. Overall Stats (Existing logic, kept consistent but maybe re-calculated from total)
                closed_tickets = [t for t in tickets if t.jira_status == "Closed"]
                closed_count = len(closed_tickets)
                new_percentage = int((closed_count / total_tickets) * 100)
            
            # Update fields
            changed = False
            if tp.completed_percentage != new_percentage:
                tp.completed_percentage = new_percentage
                changed = True
            
            if tp.fe_completed_percentage != new_fe_percentage:
                tp.fe_completed_percentage = new_fe_percentage
                changed = True
                
            if tp.be_completed_percentage != new_be_percentage:
                tp.be_completed_percentage = new_be_percentage
                changed = True
                
            if tp.fe_status_all_open != new_fe_all_open:
                tp.fe_status_all_open = new_fe_all_open
                changed = True

            if changed:
                updates_count += 1
                
        db.commit()
        logger.info(f"TP Completion Calculation Fininshed. Updated {updates_count} records.")
        
    except Exception as e:
        logger.error(f"Error in calculate_tp_completion: {e}", exc_info=True)
    finally:
        if close_session:
            db.close()

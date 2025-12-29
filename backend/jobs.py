from datetime import datetime, timedelta
import time
import json
import logging
from sqlalchemy.orm import Session
from database import SessionLocal
from models import LarkModelTP, LarkModelTCG, TCGRemovedTickets
from lark_service import list_records

# Configure logger
logger = logging.getLogger(__name__)

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
        # 1. Normalize key
        col_name = normalize_lark_key(key)
        
        # 2. Check if specific column exists (e.g., ticket_number)
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
             # Construct JSON filter object for Lark Search API
             filter_obj = {
                 "conjunction": "and",
                 "conditions": [
                     {
                         "field_name": "Updated Date",
                         "operator": "isGreater",
                         "value": [one_day_ago_ms]
                     }
                 ]
             }
             logger.info(f"Incremental sync enabled. Filter: Updated Date > {datetime.fromtimestamp(one_day_ago_ms/1000)}")
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
    from jira_service import JiraService
    
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

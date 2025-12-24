from datetime import datetime, timedelta
import time
import json
from sqlalchemy.orm import Session
from database import SessionLocal
from models import LarkModelTP, LarkModelTCG
from lark_service import list_records

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
    print(f"  [DEBUG] Mapped {mapped_count}/{len(lark_fields)} fields")
    print(f"  [DEBUG] Valid columns: {sorted(valid_columns)}")
    print(f"  [DEBUG] Sample mappings:")
    for key in list(lark_fields.keys())[:5]:
        col_name = normalize_lark_key(key)
        in_model = col_name in valid_columns
        print(f"    '{key}' -> '{col_name}' [{('✓' if in_model else '✗')}]")


def sync_lark_table(app_token: str, table_id: str, model_class, force_full: bool = False):
    table_name = model_class.__tablename__
    print(f"Starting sync for table: {table_name} ({table_id}) [Force Full: {force_full}]")
    
    db = SessionLocal()
    try:
        latest_timestamp = None
        if not force_full:
                latest_timestamp = get_latest_update_time(db, model_class)
        
        # Disable filter - causing API errors with Lark
        filter_str = None
        # if latest_timestamp:
        #     one_day_ago_ms = int((datetime.now() - timedelta(days=1)).timestamp() * 1000)
        #     filter_str = f'CurrentValue.[Updated Date] > {one_day_ago_ms}'
        #     print(f"Incremental sync: {filter_str}")
        # else:
        print("Full sync: Fetching all records with pagination.")

        has_more = True
        page_token = None
        total_fetched = 0
        
        while has_more:
             resp = list_records(app_token, table_id, filter_str, page_token)
             
             if not resp or "items" not in resp:
                 print(f"No items found or error: {resp}")
                 break
                 
             records = resp.get("items", [])
             total_fetched += len(records)
             print(f"Fetched {len(records)} records (Total: {total_fetched}).")
             
             for item in records:
                 record_id = item["record_id"]
                 fields = item["fields"]
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
                     print("Warning: has_more=True but no page_token. Stopping.")
                     break
                 print(f"Fetching next page...")
             else:
                 print(f"✓ Sync complete. Total: {total_fetched} records.")
                 break 

    except Exception as e:
        print(f"Error executing sync_lark_table: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

import os
import sys
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import LarkModelTCG
from jobs import sync_lark_table, get_latest_update_time

# Ensure tables exist (since DB might have been deleted)
Base.metadata.create_all(bind=engine)

def verify_description_sync():
    print("Starting verification for Description field sync...")
    
    # Load env vars for tokens (assuming they are set in env or .env file loaded by app)
    # Since we are running this as a script, we might need to load .env if not present
    from dotenv import load_dotenv
    load_dotenv()
    
    app_token = os.getenv("TP_APP_TOKEN") # Or TCG token if different? user uses TCG_APP_TOKEN
    # Check jobs.py usage or original code. Usually TCG uses TCG_APP_TOKEN
    tcg_app_token = os.getenv("TCG_APP_TOKEN")
    tcg_table_id = os.getenv("TCG_TABLE_ID")
    
    if not tcg_app_token or not tcg_table_id:
        print("Error: TCG_APP_TOKEN or TCG_TABLE_ID not found in environment.")
        return

    print(f"Syncing table {tcg_table_id}...")
    
    # Run Sync (Force Full to ensure we get data)
    sync_lark_table(tcg_app_token, tcg_table_id, LarkModelTCG, force_full=True)
    
    # Check DB
    db = SessionLocal()
    try:
        # Fetch a record with description
        # We don't know which one has it, but we can check if ANY has it not null
        count = db.query(LarkModelTCG).filter(LarkModelTCG.description.isnot(None)).count()
        print(f"Records with Description: {count}")
        
        sample = db.query(LarkModelTCG).filter(LarkModelTCG.description.isnot(None)).first()
        if sample:
            print(f"Sample Record ID: {sample.record_id}")
            print(f"Description Preview: {sample.description[:100]}...")
        else:
            print("No records found with Description populated.")
            
    finally:
        db.close()

if __name__ == "__main__":
    verify_description_sync()

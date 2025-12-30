from dotenv import load_dotenv
import os
import logging
from database import engine, Base, SessionLocal
from models import LarkModelProgram
from jobs import sync_lark_table

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

PROGRAM_APP_TOKEN = os.getenv("PROGRAM_APP_TOKEN")
PROGRAM_TABLE_ID = os.getenv("PROGRAM_TABLE_ID")

if not PROGRAM_APP_TOKEN or not PROGRAM_TABLE_ID:
    print("Error: PROGRAM_APP_TOKEN or PROGRAM_TABLE_ID not set in .env")
    # For verification purpose, we might exit, but let's try to proceed 
    # if the user environment has them set otherwise.
    # If strictly not found, we can't sync.
    exit(1)

print("Creating tables if not exist...")
Base.metadata.create_all(bind=engine)

print(f"Starting Manual Sync for TP_PROGRAM Table: {PROGRAM_TABLE_ID}")
try:
    sync_lark_table(PROGRAM_APP_TOKEN, PROGRAM_TABLE_ID, LarkModelProgram, force_full=True)
    
    # Check count
    db = SessionLocal()
    count = db.query(LarkModelProgram).count()
    print(f"Sync completed. Records in TP_PROGRAM: {count}")
    
    if count > 0:
        first = db.query(LarkModelProgram).first()
        print(f"Sample Record: {first.program_title}")

    db.close()

except Exception as e:
    print(f"Sync failed: {e}")

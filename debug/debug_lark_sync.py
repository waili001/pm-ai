import sys
import os
import logging
from datetime import datetime, timedelta

# Add backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from jobs import sync_lark_table
from models import LarkModelTP, LarkModelTCG
from database import SessionLocal

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sync():
    logger.info("Testing Lark Sync Logic...")
    
    # Load Env
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.getcwd(), 'backend', '.env'))
    
    app_token = os.getenv("MEMBER_APP_TOKEN")
    table_id = os.getenv("MEMBER_TABLE_ID") # Using Member table for test or we can test TP/TCG
    
    # Let's test LarkModelTCG sync specifically as that's where the error was
    # Need correct TABLE ID for TCG. usually in .env LARK_TCG_TABLE_ID?
    # backend/jobs.py uses hardcoded or env vars?
    # Let's look at jobs.py again? No, main.py calls sync_lark_table with specific IDs.
    # I'll just check if I can import and run it with the logic.
    
    # Manually constructing filter to verify format
    one_day_ago_ms = int((datetime.now() - timedelta(days=1)).timestamp() * 1000)
    
    print(f"Generated Timestamp: {one_day_ago_ms}")
    print(f"Expected Date String: {datetime.fromtimestamp(one_day_ago_ms/1000).strftime('%Y/%m/%d %H:%M:%S')}")
    
    # We can try to run the actual sync function if we knew the ID.
    # Since we don't want to break things, let's just print what the code WOULD do.
    # Actually, importing jobs.py and printing the source might be enough to prove what python sees.
    import inspect
    import jobs
    print("Code for sync_lark_table filter logic:")
    lines = inspect.getsource(jobs.sync_lark_table)
    # Print lines around the filter construction
    for i, line in enumerate(lines.split('\n')):
        if "filter_obj =" in line and "{" in line:
            print(f"Line {i}: {line}")
            # Print next few lines
            for j in range(1, 15):
                print(lines.split('\n')[i+j])
            break

if __name__ == "__main__":
    test_sync()

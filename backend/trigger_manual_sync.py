from dotenv import load_dotenv
import os
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Add parent dir to path if needed, but since it's in backend, appending current dir is usually enough if running from backend root?
# Actually better to rely on absolute imports if possible or same sys.path hack
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.features.sync.service.sync_service import sync_lark_table
from backend.features.project.persistence.models import LarkModelTP

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

TP_APP_TOKEN = os.getenv("TP_APP_TOKEN")
TP_TABLE_ID = os.getenv("TP_TABLE_ID")

if not TP_APP_TOKEN or not TP_TABLE_ID:
    print("Error: TP_APP_TOKEN or TP_TABLE_ID not set in .env")
    exit(1)

print(f"Starting Manual Full Sync for TP Table: {TP_TABLE_ID}")
try:
    sync_lark_table(TP_APP_TOKEN, TP_TABLE_ID, LarkModelTP, force_full=True)
    print("Sync completed successfully.")
except Exception as e:
    print(f"Sync failed: {e}")

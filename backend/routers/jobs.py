from fastapi import APIRouter, BackgroundTasks
import os
from jobs import sync_lark_table, sync_jira_verification
from models import LarkModelTP, LarkModelTCG, LarkModelDept, LarkModelMember

router = APIRouter(
    prefix="/api",
    tags=["jobs"]
)

# TP Table Info
TP_APP_TOKEN = os.getenv("TP_APP_TOKEN")
TP_TABLE_ID = os.getenv("TP_TABLE_ID")

# TCG Table Info
TCG_APP_TOKEN = os.getenv("TCG_APP_TOKEN")
TCG_TABLE_ID = os.getenv("TCG_TABLE_ID")

# TCG Dept Info
DPT_APP_TOKEN = os.getenv("DPT_APP_TOKEN")
DPT_TABLE_ID = os.getenv("DPT_TABLE_ID")

# Member Info
MEMBER_APP_TOKEN = os.getenv("MEMBER_APP_TOKEN")
MEMBER_TABLE_ID = os.getenv("MEMBER_TABLE_ID")


def run_sync_jobs_logic(force_full: bool = False):
    """Helper to run sync logic"""
    sync_lark_table(TP_APP_TOKEN, TP_TABLE_ID, LarkModelTP, force_full=force_full)
    sync_lark_table(TCG_APP_TOKEN, TCG_TABLE_ID, LarkModelTCG, force_full=force_full)
    if MEMBER_APP_TOKEN and MEMBER_TABLE_ID:
        sync_lark_table(MEMBER_APP_TOKEN, MEMBER_TABLE_ID, LarkModelMember, force_full=force_full)

@router.post("/jobs/sync")
def trigger_sync():
    """Manually trigger a full sync of all tables."""
    # We run this in background or directly? For simplicity, running directly (blocking) 
    # so we can return status. In production, might want BackgroundTasks.
    # Given the requirements, blocking is fine for immediate feedback.
    try:
        run_sync_jobs_logic(force_full=True)
        return {"status": "success", "message": "Sync jobs triggered successfully (Force Full)."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/jobs/verify-jira")
def trigger_jira_verification():
    """Manually trigger Jira verification to clean up deleted tickets."""
    try:
        sync_jira_verification()
        return {"status": "success", "message": "Jira verification job completed."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/sync/lark/dept")
async def sync_lark_dept(background_tasks: BackgroundTasks, force_full: bool = False):
    if not DPT_APP_TOKEN or not DPT_TABLE_ID:
        return {"message": "DPT_APP_TOKEN or DPT_TABLE_ID not configured", "status": "error"}
    
    background_tasks.add_task(sync_lark_table, DPT_APP_TOKEN, DPT_TABLE_ID, LarkModelDept, force_full)
    return {"message": "Department sync job started in background"}

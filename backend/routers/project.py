from fastapi import APIRouter
from database import SessionLocal
from models import LarkModelTP, LarkModelTCG

router = APIRouter(
    prefix="/api/project",
    tags=["project"]
)

@router.get("/active")
def get_active_tps():
    """Fetch all active TP projects (Status != Closed/Resolved)."""
    db = SessionLocal()
    try:
        # User requirement: "jira status != Closed 或 Resolved"
        # We also filter out empty statuses just in case
        tps = db.query(LarkModelTP).filter(
            LarkModelTP.jira_status != "Closed",
            LarkModelTP.jira_status != "Resolved"
            # potentially filter nulls too: LarkModelTP.jira_status.isnot(None)
        ).all()
        
        results = []
        for tp in tps:
            # Format label for Autocomplete: "TP-123 Title"
            # Handle potential None values safely
            t_num = tp.ticket_number or "Unknown"
            title = tp.title or "No Title"
            label = f"{t_num} {title}"
            
            results.append({
                "id": tp.record_id,
                "ticket_number": t_num,
                "title": title,
                "label": label,
                "status": tp.jira_status
            })
        
        return results
    finally:
        db.close()

@router.get("/{tp_number}/tcg_tickets")
def get_tcg_tickets_by_tp(tp_number: str):
    """Fetch TCG tickets associated with a specific TP number."""
    db = SessionLocal()
    try:
        # Note: tp_number should be exact string match e.g. "TP-3492"
        # Since input might vary case (tp-3492 vs TP-3492), we might want case-insensitive search
        # SQLite is case-insensitive by default for ASCII usually, but let's be safe.
        tickets = db.query(LarkModelTCG).filter(
            LarkModelTCG.tp_number.ilike(f"{tp_number}")
        ).all()
        
        results = []
        for t in tickets:
            results.append({
                "ticket_number": t.tcg_tickets, # Often the key identifier TCG-XXXX
                "title": t.title,
                "assignee": t.assignee,
                "reporter": t.reporter,
                "issue_type": t.issue_type,
                "status": t.jira_status, # For Kanban grouping
                "description": t.description,  # Description field
                "parent_tickets": t.parent_tickets  # Parent tickets reference
            })
            
        return results
    finally:
        db.close()

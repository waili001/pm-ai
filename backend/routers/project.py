from fastapi import APIRouter
from database import SessionLocal
from models import LarkModelTP, LarkModelTCG, LarkModelDept

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

@router.get("/planning")
def get_planning_projects(department: str = None, project_type: str = None):
    """
    Fetch projects for Planning Dashboard with optional filtering.
    - department: string to match (partial match vs exact match TBD, using ilike for now)
    - project_type: exact match
    """
    db = SessionLocal()
    try:
        query = db.query(LarkModelTP)

        if department and department != "ALL":
             # department is stored as Comma separated string potentially
             query = query.filter(LarkModelTP.department.ilike(f"%{department}%"))
        
        if project_type and project_type != "ALL":
             query = query.filter(LarkModelTP.project_type == project_type)

        tps = query.all()
        
        # Logic: Filter out "Closed" projects older than 4 months
        # 4 months ~ 120 days
        import time
        now_ts = int(time.time() * 1000)
        cutoff_ts = now_ts - (120 * 24 * 3600 * 1000)

        results = []
        for tp in tps:
            # Check for Closed filter logic
            if tp.jira_status == "Closed":
                if tp.updated_at and tp.updated_at < cutoff_ts:
                    continue # Skip old closed projects

            # Handle potential None values
            t_num = tp.ticket_number or "Unknown"
            title = tp.title or "No Title"
            
            results.append({
                "id": tp.record_id,
                "ticket_number": t_num,
                "title": title,
                "status": tp.jira_status, # vital for Kanban
                "department": tp.department,
                "project_type": tp.project_type,
                "project_manager": tp.project_manager,
                "released_month": tp.released_month,
                "due_day_quarter": tp.due_day_quarter,
                "icr_count": tp.icr_count,
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

@router.get("/ticket/{ticket_number}")
def get_ticket_details(ticket_number: str):
    """Fetch detailed information for a specific ticket (TCG or TP)."""
    db = SessionLocal()
    try:
        # Search in TCG first (has description)
        tcg = db.query(LarkModelTCG).filter(LarkModelTCG.tcg_tickets == ticket_number).first()
        if tcg:
            return {
                "ticket_number": tcg.tcg_tickets,
                "title": tcg.title,
                "status": tcg.jira_status,
                "assignee": tcg.assignee,
                "reporter": tcg.reporter,
                "description": tcg.description, # TCG has description
                "issue_type": tcg.issue_type
            }

        # Search in TP
        tp = db.query(LarkModelTP).filter(LarkModelTP.ticket_number == ticket_number).first()
        if tp:
            return {
                "ticket_number": tp.ticket_number,
                "title": tp.title,
                "status": tp.jira_status,
                "assignee": tp.project_manager, # Map PM to assignee for TP
                "reporter": "-", # TP might not have explicit reporter mapped
                "description": None, # TP model doesn't currently map description
                "issue_type": "TP"
            }
            
        return None # Or raise 404, but frontend handles null check
    finally:
        db.close()

@router.get("/departments")
def get_departments():
    """Fetch all unique departments."""
    db = SessionLocal()
    try:
        # Fetch distinct departments from LarkModelDept
        depts = db.query(LarkModelDept.department).distinct().filter(LarkModelDept.department != None).all()
        # Flatten result list of tuples [('DeptA',), ('DeptB',)] -> ['DeptA', 'DeptB']
        results = [d[0] for d in depts if d[0]]
        return sorted(results)
    finally:
        db.close()

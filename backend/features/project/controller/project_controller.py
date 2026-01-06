from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.shared.database import SessionLocal, get_db
from backend.features.project.persistence.models import LarkModelTP, LarkModelTCG, LarkModelProgram, TicketAnomaly
from backend.features.system.persistence.models import LarkModelDept
from backend.features.member.persistence.models import LarkModelMember
from backend.features.auth.persistence.models import AdminUser
from backend.shared.dependencies import get_current_user
from typing import List, Optional
from pydantic import BaseModel

class ReorderRequest(BaseModel):
    project_ids: List[str]
    status: str

router = APIRouter(
    prefix="/api/project",
    tags=["Project"]
)

from backend.features.project.service.project_service import ProjectService

@router.get("/dashboard-stats")
def get_dashboard_stats(
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get statistics for Dashboard.
    Current Metric: Closed/Resolved TP counts per Quarter (Last 4 Quarters).
    """
    service = ProjectService(db)
    return service.get_dashboard_stats(department)

@router.get("/closed-tps")
def get_closed_tps(
    quarter: str,
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of Closed TPs for a specific quarter.
    Used for Dashboard drill-down.
    """
    service = ProjectService(db)
    return service.get_closed_tps(quarter, department)

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
                "status": tp.jira_status,
                "department": tp.department, # For filtering
                "participated_dept": tp.participated_dept # For filtering
            })
        
        return results
    finally:
        db.close()

@router.get("/programs")
def get_programs():
    """Fetch all unique program titles."""
    db = SessionLocal()
    try:
        # Fetch distinct program titles
        programs = db.query(LarkModelProgram.program_title).distinct().filter(LarkModelProgram.program_title != None).all()
        results = [p[0] for p in programs if p[0]]
        return sorted(results)
    finally:
        db.close()

@router.get("/planning")
def get_planning_projects(
    program: Optional[str] = None,
    department: Optional[str] = None,
    project_type: Optional[str] = None,
    participated_dept: Optional[str] = None
):
    """
    Get projects for Planning Dashboard.
    Filters: Program, Department, Project Type.
    Logic: 
      - Program: Filter by TP ticket numbers found in TP_PROGRAM for the given title.
      - Department/Type: Direct filter.
      - Closed projects: Hide if older than 4 months.
      - Blocked projects: Exclude projects with jira_status == 'Blocked'.
    """
    db = SessionLocal()
    try:
        query = db.query(LarkModelTP).filter(LarkModelTP.jira_status != "Blocked")

        # 1. Program Filter (First Priority)
        if program and program != "ALL":
             # Find TPs associated with this program
             # TP_PROGRAM.tp contains ticket number (e.g. TP-123)
             program_tps = db.query(LarkModelProgram.tp).filter(LarkModelProgram.program_title == program).all()
             
             # Extract list of ticket numbers, filtering out None
             tp_list = [p[0] for p in program_tps if p[0]]
             
             if not tp_list:
                 # Program selected but no TPs found -> Return empty
                 return []
             
             # Filter main query
             query = query.filter(LarkModelTP.ticket_number.in_(tp_list))

        if department and department != "ALL":
             # department is stored as Comma separated string potentially
             query = query.filter(LarkModelTP.department.ilike(f"%{department}%"))
        
        if project_type and project_type != "ALL":
             query = query.filter(LarkModelTP.project_type == project_type)
        
        if participated_dept and participated_dept != "ALL":
             query = query.filter(
                 LarkModelTP.participated_dept.ilike(f"%{participated_dept}%"),
                 LarkModelTP.department != participated_dept
             )

        tps = query.order_by(LarkModelTP.sort_order.asc()).all()
        
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
                # New Fields
                "released_date": tp.released_date,
                "due_day": tp.due_day,
                "start_date": tp.start_date,
                "sit_date": tp.sit_date,
                "completed_percentage": tp.completed_percentage or 0, # Default to 0
                "fe_completed_percentage": tp.fe_completed_percentage or 0,
                "be_completed_percentage": tp.be_completed_percentage or 0,
                "fe_status_all_open": tp.fe_status_all_open or False,
                "sort_order": tp.sort_order or 0
            })
        
        # Sort by sort_order explicitly (though SQL should handle it if added)
        results.sort(key=lambda x: x["sort_order"])
        
        return results
    finally:
        db.close()

@router.post("/reorder")
def reorder_projects(request: ReorderRequest):
    """Reorder projects within a status column."""
    db = SessionLocal()
    try:
        # Iterate through the list of IDs and update their sort_order
        for index, project_id in enumerate(request.project_ids):
            tp = db.query(LarkModelTP).filter(LarkModelTP.record_id == project_id).first()
            if tp:
                tp.sort_order = index
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

class ReorderTCGRequest(BaseModel):
    status: str
    ticket_ids: List[str]

@router.post("/reorder_tcg")
def reorder_tcg_tickets(request: ReorderTCGRequest):
    """Reorder TCG tickets within a status column."""
    db = SessionLocal()
    try:
        # Iterate through the list of IDs and update their sort_order
        for index, ticket_id in enumerate(request.ticket_ids):
            ticket = db.query(LarkModelTCG).filter(LarkModelTCG.record_id == ticket_id).first()
            if ticket:
                ticket.sort_order = index
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise e
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
        ).order_by(LarkModelTCG.sort_order.asc()).all()
        
        results = []
        for t in tickets:
            results.append({
                "id": t.record_id, # Crucial for drag and drop
                "ticket_number": t.tcg_tickets, # Often the key identifier TCG-XXXX
                "title": t.title,
                "assignee": t.assignee,
                "reporter": t.reporter,
                "issue_type": t.issue_type,
                "status": t.jira_status, # For Kanban grouping
                "description": t.description,  # Description field
                "parent_tickets": t.parent_tickets,  # Parent tickets reference
                "components": t.components, # Component for FE/BE classification
                "sort_order": t.sort_order
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
            # Compute sub-tasks: Find tickets where parent_tickets contains this ticket number
            # Using ilike for robust partial match (e.g. "TCG-123", "TCG-123, TCG-456")
            sub_tasks_query = db.query(LarkModelTCG).filter(
                LarkModelTCG.parent_tickets.ilike(f"%{ticket_number}%")
            ).all()
            
            sub_tasks_details = []
            for t in sub_tasks_query:
                if t.tcg_tickets:
                    sub_tasks_details.append({
                        "ticket_number": t.tcg_tickets,
                        "title": t.title,
                        "status": t.jira_status,
                        "assignee": t.assignee
                    })
            
            # Sort by ticket number
            sub_tasks_details.sort(key=lambda x: x["ticket_number"])

            # 2024-01-06 Enhancement: Fetch TP Info
            tp_info = None
            if tcg.tp_number:
                 tp_model = db.query(LarkModelTP).filter(LarkModelTP.ticket_number == tcg.tp_number).first()
                 if tp_model:
                     tp_info = {
                         "ticket_number": tp_model.ticket_number,
                         "title": tp_model.title,
                         "status": tp_model.jira_status,
                         "due_day": tp_model.due_day
                     }

            return {
                "ticket_number": tcg.tcg_tickets,
                "title": tcg.title,
                "status": tcg.jira_status,
                "assignee": tcg.assignee,
                "reporter": tcg.reporter,
                "description": tcg.description, # TCG has description
                "issue_type": tcg.issue_type,
                "tp_number": tcg.tp_number,
                "tp_info": tp_info, # Return detailed TP info
                "fix_versions": tcg.fix_versions,
                "sub_tasks": sub_tasks_details
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
                "description": tp.description, 
                "released_date": tp.released_date,
                "due_day": tp.due_day,
                "start_date": tp.start_date,
                "sit_date": tp.sit_date,
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

@router.get("/anomalies/my-pending")
def get_my_pending_anomalies(
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if the current user (Manager/PM) has pending anomalies in their department.
    """
    # 1. Identify User in Member Info
    # Use full name or username to match Lark Member
    # Strict matching required
    user_name = current_user.full_name or current_user.username
    if not user_name:
        return {"show_modal": False, "anomalies": []}

    member = db.query(LarkModelMember).filter(
        (LarkModelMember.name == user_name)
    ).first()

    if not member:
        return {"show_modal": False, "anomalies": [], "reason": "Member not found"}

    # 2. Check Role Constraints
    # Target Roles: Manager, Assistant Manager, PM
    # Position field in LarkModelMember
    target_positions = ["Manager", "Assistant Manager", "PM"]
    
    # Simple check: is user's position exactly one of these?
    # Or contains? "Project Manager" -> "PM"? Requirement says "PM". 
    # Assuming exact match or part of string. Let's use exact from requirement first, 
    # but "Project Manager" is more likely in real data. 
    # Let's check for 'Manager' substring or 'PM' substring to be safe but correct?
    # Req: "Manager / Assistant Manager / PM"
    
    user_pos = (member.position or "").strip()
    
    is_eligible = False
    if user_pos in target_positions:
        is_eligible = True
    elif "Project Manager" in user_pos: # Handle "PM" expanded
        is_eligible = True
    
    if not is_eligible:
        return {"show_modal": False, "anomalies": [], "reason": "Role not eligible"}

    # 3. Fetch Anomalies for Department
    user_dept = member.department
    if not user_dept:
         return {"show_modal": False, "anomalies": [], "reason": "No department found"}
         
    anomalies = db.query(TicketAnomaly).filter(
        TicketAnomaly.department == user_dept
    ).order_by(TicketAnomaly.detected_at.desc()).all()
    
    if not anomalies:
        return {"show_modal": False, "anomalies": []}
        
    return {"show_modal": True, "anomalies": anomalies}

@router.get("/anomalies")
def get_ticket_anomalies(department: Optional[str] = None):
    """
    Get all detected ticket anomalies.
    Optional Filter: department
    Default: Excludes 'WRD' department if no filter provided.
    """
    db = SessionLocal()
    try:
        query = db.query(TicketAnomaly)
        
        if department:
            query = query.filter(TicketAnomaly.department == department)
        else:
            # User Requirement (2024-01-06): Default view should exclude 'WRD'
            # Note: case-insensitive check generally safer, but let's stick to standard if consistent
            query = query.filter(TicketAnomaly.department != "WRD")
            
        anomalies = query.order_by(TicketAnomaly.detected_at.desc()).all()
        return anomalies
    finally:
        db.close()

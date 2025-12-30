from fastapi import APIRouter
from sqlalchemy import func, or_, and_
from database import SessionLocal
from models import LarkModelMember, LarkModelTCG, LarkModelTP
from datetime import datetime, timedelta
import logging

router = APIRouter(
    prefix="/api/members",
    tags=["members"]
)

logger = logging.getLogger(__name__)

@router.get("/departments")
def get_departments():
    """Get distinct departments from MEMBER_INFO"""
    db = SessionLocal()
    try:
        # Use distinct on department column
        depts = db.query(LarkModelMember.department).distinct().filter(LarkModelMember.department.isnot(None)).all()
        # depts is list of tuples [('DeptA',), ('DeptB',)]
        result = sorted([d[0] for d in depts if d[0]])
        return result
    finally:
        db.close()

@router.get("/status")
def get_member_status(department: str):
    """
    Get status for all members in a specific department.
    Logic:
    1. List members in dept.
    2. For each member, find active tickets (In Progress) AND recent resolved tickets (> Yesterday 00:00).
    3. Aggregate TP info from these tickets.
    """
    db = SessionLocal()
    try:
        # 1. Get Members
        members = db.query(LarkModelMember).filter(LarkModelMember.department == department).all()
        
        # 00:00 Yesterday timestamp (ms)
        # datetime.now() -> Replace hour/min/sec/microsec to 0 -> minus 1 day
        now = datetime.now()
        today_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_midnight = today_midnight - timedelta(days=1)
        yesterday_ts = int(yesterday_midnight.timestamp() * 1000)
        
        results = []
        
        for m in members:
            member_name = m.name
            if not member_name:
                continue
                
            # 2. Find Tickets
            # Requirement:
            # - Assignee == member AND Status == 'In Progress'
            # - Resolved By == member AND Updated At > Yesterday 00:00 (Using updated_at BigInt)
            
            # Using LIKE for assignee to be safe against lists "User A, User B" 
            # or exact match? Lark Person lists are comma separated strings in our model.
            # Using ILIKE %name% is safer.
            
            tickets = db.query(LarkModelTCG).filter(
                or_(
                    and_(
                        LarkModelTCG.assignee.ilike(f"%{member_name}%"),
                        LarkModelTCG.jira_status == 'In Progress'
                    ),
                    and_(
                        LarkModelTCG.resolved_by.ilike(f"%{member_name}%"),
                        LarkModelTCG.updated_at > yesterday_ts
                    )
                )
            ).all()
            
            current_tps_map = {} # tp_number -> {tp_info}
            ticket_summaries = []
            
            for t in tickets:
                ticket_label = f"{t.tcg_tickets} {t.title}"
                ticket_summaries.append({
                    "number": t.tcg_tickets,
                    "full": ticket_label
                })
                
                tp_num = t.tp_number
                # If TP num is empty, maybe try parent?
                # For now using direct tp_number as primary linkage
                
                if tp_num:
                    if tp_num not in current_tps_map:
                        current_tps_map[tp_num] = {"tp_number": tp_num}
            
            # 3. Resolve TP Dept
            if current_tps_map:
                tp_nums = list(current_tps_map.keys())
                 # Case insensitive lookup if needed, but assuming standard format
                tps = db.query(LarkModelTP).filter(LarkModelTP.ticket_number.in_(tp_nums)).all()
                for tp in tps:
                    if tp.ticket_number in current_tps_map:
                         current_tps_map[tp.ticket_number]["department"] = tp.department
                         current_tps_map[tp.ticket_number]["title"] = tp.title
            
            # Format Result
            tp_display_list = []
            tp_dept_list = []
            
            for tp_data in current_tps_map.values():
                tp_str = f"{tp_data['tp_number']} {tp_data.get('title', '')}"
                tp_display_list.append({
                    "number": tp_data['tp_number'],
                    "full": tp_str
                })
                if tp_data.get('department'):
                    tp_dept_list.append(tp_data['department'])
            
            results.append({
                "department": m.department,
                "member_name": member_name,
                "member_no": m.member_no,
                "team": m.team,
                "position": m.position,
                "current_tps": tp_display_list,
                "in_progress_tickets": ticket_summaries,
                "project_dept": ", ".join(set(tp_dept_list)) # Unique depts
            })
            
        return results

    except Exception as e:
        logger.error(f"Error fetching member status: {e}")
        return []
    finally:
        db.close()

import sys
import os
import logging

# Add backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import SessionLocal
from models import LarkModelTCG, LarkModelMember
from routers.member import get_member_status

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_ticket_status():
    logger.info("Verifying Ticket Status Logic...")
    
    # We need to find a department that has members and tickets
    db = SessionLocal()
    try:
        # Get a department
        dept = db.query(LarkModelMember.department).filter(LarkModelMember.department.isnot(None)).first()
        if not dept:
            logger.warning("No departments found to test.")
            return

        dept_name = dept[0]
        logger.info(f"Testing Department: {dept_name}")
        
        results = get_member_status(dept_name)
        
        for member_data in results:
            tickets = member_data.get("in_progress_tickets", [])
            for t in tickets:
                ticket_num = t['number']
                # Check DB for status
                db_ticket = db.query(LarkModelTCG).filter(LarkModelTCG.tcg_tickets == ticket_num).first()
                if db_ticket:
                    logger.info(f"Ticket: {ticket_num}, Status: {db_ticket.jira_status}")
                    if db_ticket.jira_status != "In Progress":
                        logger.warning(f"  [!] Found NON 'In Progress' ticket: {ticket_num} ({db_ticket.jira_status})")
                    else:
                        logger.info(f"  [OK] In Progress ticket found.")
                else:
                    logger.warning(f"Ticket {ticket_num} not found in DB.")

    finally:
        db.close()

if __name__ == "__main__":
    verify_ticket_status()

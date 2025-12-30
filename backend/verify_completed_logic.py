import sys
import os
import logging
from datetime import datetime, timedelta

# Since we are running in backend dir, current dir is in sys.path
# imports should work directly if we run as 'python3 verify_completed_logic.py'

from database import SessionLocal
from models import LarkModelTCG, LarkModelMember
from sqlalchemy import and_

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_completed_logic():
    logger.info("Verifying 'Completed Last 7 Days' Logic...")
    
    db = SessionLocal()
    try:
        # Calculate timestamp for 7 days ago
        seven_days_ago = datetime.now() - timedelta(days=7)
        seven_days_ago_ts = int(seven_days_ago.timestamp() * 1000)
        logger.info(f"Checking tickets resolved after: {seven_days_ago} (TS: {seven_days_ago_ts})")

        # Find any ticket that matches this condition to verify data exists
        recent_tickets = db.query(LarkModelTCG).filter(
            LarkModelTCG.resolved > seven_days_ago_ts
        ).limit(5).all()
        
        if not recent_tickets:
            logger.warning("No tickets resolved in last 7 days found in DB. Logic might be correct but no data to verify against.")
            return

        logger.info(f"Found {len(recent_tickets)} recent tickets. Validating logic against a member...")
        
        # Pick a member from one of these tickets to simulate lookup
        target_member = None
        for t in recent_tickets:
            if t.resolved_by:
                target_member = t.resolved_by
                break
        
        if not target_member:
            logger.warning("Could not find a ticket with resolved_by in the sample.")
            return

        # Clean member name if it's a list string? Usually it's just a name or "Name, Name".
        # We'll take the first part if comma separated
        target_member_name = target_member.split(',')[0].strip()
        logger.info(f"Testing Member: {target_member_name} (from raw: {target_member})")
        
        member_tickets = db.query(LarkModelTCG).filter(
            and_(
                LarkModelTCG.resolved_by.ilike(f"%{target_member_name}%"),
                LarkModelTCG.resolved > seven_days_ago_ts
            )
        ).all()
        
        logger.info(f"Found {len(member_tickets)} tickets for member {target_member_name} in last 7 days.")
        for t in member_tickets:
            dt = datetime.fromtimestamp(t.resolved/1000)
            logger.info(f" - {t.tcg_tickets} (Resolved: {dt})")
        
        # Verify formatting logic
        count = len(member_tickets)
        if count > 0:
            first = member_tickets[0].tcg_tickets
            display = f"{first}...({count})" if count > 1 else first
            logger.info(f"Simulated Display: {display}")

    finally:
        db.close()

if __name__ == "__main__":
    verify_completed_logic()

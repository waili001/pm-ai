import sys
import os
import logging

# Ensure we are in the correct path context if run from backend/ or root
# If run from backend/, assert that DATABASE_URL etc are available via .env loading if needed, 
# but models/database.py usually handle it.

from database import SessionLocal
from routers.member import get_member_status

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_fix():
    logger.info("Verifying Fix for 'tps' UnboundLocalError...")
    
    # Departments that caused error in logs: GED, CRD, CCD, OPD
    target_depts = ['GED', 'CRD', 'CCD', 'OPD']
    
    for dept in target_depts:
        logger.info(f"Testing Department: {dept}")
        try:
            results = get_member_status(dept)
            logger.info(f"  [OK] Success. Fetched {len(results)} members.")
        except UnboundLocalError as e:
            logger.error(f"  [FAIL] UnboundLocalError caught: {e}")
        except Exception as e:
            logger.error(f"  [FAIL] Other error caught: {e}")

if __name__ == "__main__":
    verify_fix()

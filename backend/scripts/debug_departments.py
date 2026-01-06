from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.features.project.persistence.models import TicketAnomaly, LarkModelTP
# Note: LarkModelDept might not be in the same file or db?
# project_controller imports LarkModelDept. Let's see where it is defined.
# It seems I missed checking where LarkModelDept is defined. It is likely in models.py or separate.
# Let's check models.py content again or search for it.

# Actually, I'll just check what values are in TicketAnomaly and print them.
# The user can tell me if they look right, or I can infer.
# I will also check if I can import LarkModelDept.

from backend.shared.database import SQLALCHEMY_DATABASE_URL
import os
import sys

sys.path.append(os.getcwd())

db_path = "backend/sql_app.db" # This is where ticket_anomalies is
engine = create_engine(f"sqlite:///{db_path}")
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    print("--- TicketAnomaly Departments ---")
    distinct_anom_depts = [r[0] for r in db.query(TicketAnomaly.department).distinct().all()]
    print(distinct_anom_depts)

    print("\n--- Trying to imitate get_departments ---")
    try:
        from backend.features.system.persistence.models import LarkModelDept
        distinct_depts = [r[0] for r in db.query(LarkModelDept.department).distinct().all()]
        print(distinct_depts)
        
        print("\n--- Comparison ---")
        for ad in distinct_anom_depts:
            if ad not in distinct_depts and ad is not None:
                print(f"WARNING: Anomaly Dept '{ad}' not found in Master Dept list")
    except ImportError:
        print("Could not import LarkModelDept. Skipping comparison.")

except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()

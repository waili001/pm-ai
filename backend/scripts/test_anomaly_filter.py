from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.features.project.persistence.models import TicketAnomaly
from backend.shared.database import SQLALCHEMY_DATABASE_URL
import os
import sys

sys.path.append(os.getcwd())

db_path = "backend/sql_app.db"
engine = create_engine(f"sqlite:///{db_path}")
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def test_filter(dept):
    print(f"Testing filter for department: '{dept}'")
    query = db.query(TicketAnomaly)
    if dept:
        query = query.filter(TicketAnomaly.department == dept)
    
    results = query.all()
    print(f"Found {len(results)} records.")
    for r in results:
        print(f" - {r.ticket_number} ({r.department})")

try:
    test_filter("WRD")
    test_filter("") # All
    test_filter("NON_EXISTENT")
finally:
    db.close()

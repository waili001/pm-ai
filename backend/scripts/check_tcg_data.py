from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.features.project.persistence.models import LarkModelTCG
from backend.shared.database import SQLALCHEMY_DATABASE_URL
import os

# Adjust path if needed since we are running from root
if "backend" not in os.getcwd():
    # If running from root, DB might be in backend/sql_app.db or similar
    # But SQLALCHEMY_DATABASE_URL in database.py uses DB_DIR env or "."
    pass

# Direct connection to the file we found earlier
# We found it was 'backend/sql_app.db' (or sql_app.db inside backend folder)
db_path = "backend/sql_app.db"
engine = create_engine(f"sqlite:///{db_path}")
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Get 5 random TCG tickets
    tickets = db.query(LarkModelTCG).limit(5).all()
    print(f"Checking {len(tickets)} tickets...")
    for t in tickets:
        print(f"Ticket: {t.tcg_tickets}")
        print(f"  Component: '{t.components}'")
        print(f"  Department: '{t.department}'")
        print("-" * 20)
finally:
    db.close()

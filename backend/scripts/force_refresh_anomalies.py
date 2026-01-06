from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.features.project.service.anomaly_service import AnomalyService
from backend.shared.database import SQLALCHEMY_DATABASE_URL
import os
import sys

# Add root to sys.path
sys.path.append(os.getcwd())

# Database connection
db_path = "backend/sql_app.db"
engine = create_engine(f"sqlite:///{db_path}")
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    print("Forcing Anomaly Refresh...")
    service = AnomalyService(db)
    service.refresh_anomalies()
    print("Refresh complete.")
    
    # Verify
    from backend.features.project.persistence.models import TicketAnomaly
    anomalies = db.query(TicketAnomaly).all()
    print(f"Total Anomalies: {len(anomalies)}")
    for a in anomalies:
        print(f"Ticket: {a.ticket_number}, Comp: {a.components}, Dept: {a.department}")

except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()

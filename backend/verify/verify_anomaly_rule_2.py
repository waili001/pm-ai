
import sys
import os
import time
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.features.project.service.anomaly_service import AnomalyService
from backend.features.project.persistence.models import Base, LarkModelTP, LarkModelTCG, TicketAnomaly

# Setup In-Memory DB for testing
engine = create_engine('sqlite:///:memory:')
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

def test_rule_2():
    db = SessionLocal()
    service = AnomalyService(db)
    
    # Setup Data
    # 1. TP Project (In Progress)
    tp = LarkModelTP(
        record_id="rec_tp_001",
        ticket_number="TP-001",
        title="Test Project",
        jira_status="In Progress"
    )
    db.add(tp)
    
    # 2. Parent Ticket (In Progress)
    parent = LarkModelTCG(
        record_id="rec_001",
        tcg_tickets="TCG-100",
        tp_number="TP-001",
        title="Parent Ticket",
        jira_status="In Progress",
        issue_type="Change Request",
        assignee="Tester"
    )
    db.add(parent)
    
    # Scenario A: Child is "In Review" -> Should NOT be an anomaly (New Rule: In Review is ACTIVE)
    child_a = LarkModelTCG(
        record_id="rec_002",
        tcg_tickets="TCG-101",
        parent_tickets="TCG-100",
        jira_status="In Review",
        issue_type="Sub-task"
    )
    db.add(child_a)
    db.commit()

    print("--- Scenario A: Parent In Progress, Child In Review ---")
    service.refresh_anomalies()
    anomalies = db.query(TicketAnomaly).all()
    print(f"Anomalies found: {len(anomalies)}")
    
    if len(anomalies) != 0:
        print("FAIL: Expected 0 anomalies for 'In Review' child.")
        sys.exit(1)
    else:
        print("PASS: Correctly identified as NOT active (Wait, In Review is Active, so Parent In Progress + Active Child = OK)")


    # Scenario B: Child is "Closed" -> Should BE an anomaly
    # Update child status to Closed
    child_a.jira_status = "Closed"
    db.commit()
    
    print("\n--- Scenario B: Parent In Progress, Child Closed ---")
    service.refresh_anomalies()
    anomalies = db.query(TicketAnomaly).all()
    print(f"Anomalies found: {len(anomalies)}")

    if len(anomalies) == 1:
        print(f"PASS: Anomaly detected: {anomalies[0].anomaly_reason}")
    else:
        print("FAIL: Expected 1 anomaly for 'Closed' child.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        test_rule_2()
        print("\nAll tests passed!")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

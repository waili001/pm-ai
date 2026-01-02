
import sys
import os
import uuid
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from backend.features.project.persistence.models import LarkModelTP, LarkModelTCG
from backend.shared.database import SQLALCHEMY_DATABASE_URL
from backend.features.sync.service.sync_service import calculate_tp_completion

def verify_logic():
    print("Setting up verification environment...")
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    # 1. Create Dummy Data
    test_tp_number = f"TP-TEST-{uuid.uuid4().hex[:6]}"
    
    # Create TP Project
    tp_project = LarkModelTP(
        record_id=f"rec_{uuid.uuid4().hex[:8]}",
        ticket_number=test_tp_number,
        jira_status="In Progress",
        completed_percentage=0,
        updated_at=int(time.time()*1000)
    )
    db.add(tp_project)
    
    # Create TCG Tickets linked to TP
    # 2 Closed, 3 Open -> Total 5. Expected Percentage: 40%
    statuses = ["Closed", "Closed", "In Progress", "Open", "Blocked"]
    
    for i, status in enumerate(statuses):
        ticket = LarkModelTCG(
            record_id=f"rec_tcg_{uuid.uuid4().hex[:8]}",
            tcg_tickets=f"TCG-{test_tp_number}-{i}",
            tp_number=test_tp_number,
            jira_status=status,
            updated_at=int(time.time()*1000)
        )
        db.add(ticket)
        
    db.commit()
    print(f"Created Test TP: {test_tp_number} with 5 tickets (2 Closed).")
    
    try:
        # 2. Run Logic
        print("Running calculation logic...")
        calculate_tp_completion(db)
        
        # 3. Verify Result
        db.refresh(tp_project)
        print(f"Result Completed Percentage: {tp_project.completed_percentage}")
        
        expected = 40 # 2/5 * 100
        if tp_project.completed_percentage == expected:
            print("SUCCESS: Percentage calculated correctly.")
        else:
            print(f"FAILURE: Expected {expected}, got {tp_project.completed_percentage}")
            sys.exit(1)
            
    finally:
        # 4. Clean up
        print("Cleaning up test data...")
        db.query(LarkModelTCG).filter(LarkModelTCG.tp_number == test_tp_number).delete()
        db.query(LarkModelTP).filter(LarkModelTP.ticket_number == test_tp_number).delete()
        db.commit()
        db.close()

if __name__ == "__main__":
    verify_logic()


import time
from datetime import datetime, timedelta

# Mock logic to simulate backend filtering
def filter_projects(projects):
    filtered = []
    
    # 4 months ago in milliseconds
    # 4 months ~ 120 days
    cutoff_date = datetime.now() - timedelta(days=120)
    cutoff_ts = int(cutoff_date.timestamp() * 1000)
    
    print(f"Cutoff Timestamp: {cutoff_ts} ({cutoff_date})")

    for p in projects:
        status = p.get("jira_status")
        updated_at = p.get("updated_at")
        
        if status == "Closed":
            if updated_at and updated_at < cutoff_ts:
                print(f"Excluding Closed project {p['id']}: updated {updated_at} < {cutoff_ts}")
                continue
        
        filtered.append(p)
    return filtered

if __name__ == "__main__":
    now_ts = int(time.time() * 1000)
    month_ms = 30 * 24 * 3600 * 1000
    
    test_data = [
        {"id": 1, "jira_status": "Open", "updated_at": now_ts - (5 * month_ms)}, # Should keep (Open)
        {"id": 2, "jira_status": "Closed", "updated_at": now_ts - (1 * month_ms)}, # Should keep (Recent Closed)
        {"id": 3, "jira_status": "Closed", "updated_at": now_ts - (5 * month_ms)}, # Should exclude (Old Closed)
        {"id": 4, "jira_status": "Closed", "updated_at": None}, # Should keep (Safety net? Or exclude? Code says < cutoff, None < cutoff is error in Py3. Need safe check)
    ]
    
    print("Test Data:", test_data)
    try:
        results = filter_projects(test_data)
        print("\nResults:", results)
        
        ids = [p["id"] for p in results]
        assert 1 in ids
        assert 2 in ids
        assert 3 not in ids
        print("\nVerification Passed!")
    except Exception as e:
        print(f"\nVerification Failed: {e}")

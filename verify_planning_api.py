
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_planning_api():
    print("Testing /api/project/planning endpoint...")
    
    # 1. Test without filters
    try:
        resp = requests.get(f"{BASE_URL}/api/project/planning")
        if resp.status_code != 200:
            print(f"FAILED: /api/project/planning returned {resp.status_code}")
            print(resp.text)
            sys.exit(1)
        
        data = resp.json()
        print(f"SUCCESS: Fetched {len(data)} projects (no filter).")
        if len(data) > 0:
            print("Sample project:", json.dumps(data[0], indent=2))
    except Exception as e:
        print(f"ERROR: Failed to connect to {BASE_URL}: {e}")
        sys.exit(1)

    # 2. Test with Department filter
    # Assuming there's some data, let's try a common department or just check empty return is 200
    dept = "Tech" 
    resp = requests.get(f"{BASE_URL}/api/project/planning", params={"department": dept})
    if resp.status_code == 200:
        data = resp.json()
        print(f"SUCCESS: Fetched {len(data)} projects with department='{dept}'.")
    else:
        print(f"FAILED: /api/project/planning?department={dept} returned {resp.status_code}")

    # 3. Test with Project Type filter
    ptype = "Project"
    resp = requests.get(f"{BASE_URL}/api/project/planning", params={"project_type": ptype})
    if resp.status_code == 200:
        data = resp.json()
        print(f"SUCCESS: Fetched {len(data)} projects with project_type='{ptype}'.")
    else:
        print(f"FAILED: /api/project/planning?project_type={ptype} returned {resp.status_code}")

if __name__ == "__main__":
    test_planning_api()

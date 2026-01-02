import requests
import sys

BASE_URL = "http://localhost:8000/api"

def verify_auth_endpoints():
    print("Verifying Auth Endpoints...")
    
    # 1. Test Lark Login Redirect
    try:
        resp = requests.get(f"{BASE_URL}/auth/lark/login", allow_redirects=False)
        if resp.status_code == 307 or resp.status_code == 302:
            if "open.larksuite.com" in resp.headers['location']:
                print("✓ Lark Login Redirect OK")
            else:
                 print(f"✗ Lark Login Redirect Failed: Location {resp.headers['location']}")
        else:
             print(f"✗ Lark Login API Failed: Status {resp.status_code}")
    except Exception as e:
        print(f"✗ Lark Login API Error: {e}")

    # 2. Test Local Login (Should fail with 401 for wrong creds, proving endpoint exists)
    try:
        resp = requests.post(f"{BASE_URL}/login", json={"username": "test", "password": "wrongpassword"})
        if resp.status_code == 401:
             print("✓ Local Login Endpoint OK (Correctly rejected invalid creds)")
        else:
             print(f"✗ Local Login Endpoint Failed: Expected 401, got {resp.status_code}")
    except Exception as e:
        print(f"✗ Local Login API Error: {e}")
        
if __name__ == "__main__":
    verify_auth_endpoints()

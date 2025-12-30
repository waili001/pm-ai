import requests
import sys

BASE_URL = "http://localhost:8000"

def verify_reorder():
    url = f"{BASE_URL}/api/project/reorder"
    payload = {
        "status": "In Progress",
        "project_ids": []
    }
    
    print(f"Checking POST {url}...")
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response:", response.json())
            print("SUCCESS: API is reachable.")
        elif response.status_code == 404:
            print("FAILURE: API not found (404).")
            sys.exit(1)
        else:
            print(f"FAILURE: Unexpected status code {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"Error connecting to API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_reorder()

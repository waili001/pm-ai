
import requests
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

BASE_URL = "http://localhost:8000" 

def test_api(token, method, path, expected_code):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}{path}"
    
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json={}) 
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers)
        else:
            print(f"Unsupported method {method}")
            return False

        if resp.status_code == expected_code:
            print(f"[PASS] {method} {path} -> {resp.status_code}")
            return True
        else:
            print(f"[FAIL] {method} {path} -> Expected {expected_code}, Got {resp.status_code}")
            print(f"       Response: {resp.text}")
            return False
    except Exception as e:
        print(f"[ERR] {method} {path}: {e}")
        return False

def verify_rbac():
    print("--- RBAC Verification (Token Injection) ---")
    
    from backend.shared.database import SessionLocal
    from backend.features.auth.persistence.models import AdminUser, Role
    import jwt
    import datetime
    
    # Mock create_access_token
    JWT_SECRET = "super-secret-key"
    JWT_ALGORITHM = "HS256"
    
    def create_access_token(data: dict):
        to_encode = data.copy()
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_jwt

    db = SessionLocal()
    
    # 1. Setup Test Users (Hash doesn't matter since we gen token)
    users_setup = [
        {"username": "waili_test", "role": "SUPER_ADMIN"},
        {"username": "user_test", "role": "USER"},
    ]
    
    tokens = {}
    
    for u in users_setup:
        # Create/Update user
        # We need to ensure role_id is set for RBAC check to work
        # RBAC uses user.role_obj
        
        db_user = db.query(AdminUser).filter(AdminUser.username == u["username"]).first()
        role = db.query(Role).filter(Role.name == u["role"]).first()
        
        if not role:
            print(f"Error: Role {u['role']} not found in DB")
            continue

        if not db_user:
            db_user = AdminUser(
                username=u["username"], 
                password_hash="dummy",
                role_id=role.id,
                role=role.name # legacy
            )
            db.add(db_user)
        else:
            db_user.role_id = role.id
            db_user.role = role.name
            
        db.commit()
        
        # Generate Token
        # Controller does: create_access_token(data={"sub": user.username, "role": user.role})
        # Dependencies get_current_user uses 'sub' to fetch user from DB.
        # So token is valid if user exists in DB.
        tokens[u["role"]] = create_access_token(data={"sub": u["username"], "role": u["role"]})
        print(f"Generated token for {u['role']}")
    
    db.close()
    
    # 2. Verify SUPER_ADMIN
    print("\n[Test Case 1] SUPER_ADMIN Access")
    if "SUPER_ADMIN" in tokens:
        # Roles API
        test_api(tokens["SUPER_ADMIN"], "GET", "/api/system/roles", 200)
    
    # 3. Verify USER (Should fail for System APIs)
    print("\n[Test Case 2] USER Access")
    if "USER" in tokens:
        # Roles API (Config: ROLES required, User role has none)
        test_api(tokens["USER"], "GET", "/api/system/roles", 403)
        
        # New Permissions Test
        # USER has 'PROJECT_PLANNING' by default (from old init script logic? NO, removed in init_rbac?)
        # Let's check init_rbac.py. It creates role but doesn't assign permissions in code anymore?
        # Use simple tests:
        test_api(tokens["USER"], "GET", "/api/data", 403) # DASHBOARD
        test_api(tokens["USER"], "GET", "/api/members/departments", 403) # MEMBER_STATUS
        test_api(tokens["USER"], "GET", "/api/project/active", 403) # PROJECT_BACKLOG (and DASHBOARD)
    
    print("\n[Test Case 3] SUPER_ADMIN New Access")
    if "SUPER_ADMIN" in tokens:
        test_api(tokens["SUPER_ADMIN"], "GET", "/api/data", 200)
        test_api(tokens["SUPER_ADMIN"], "GET", "/api/members/departments", 200)
        test_api(tokens["SUPER_ADMIN"], "GET", "/api/project/active", 200)
        
    print("\nVerification Finished.")

if __name__ == "__main__":
    verify_rbac()

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from backend.shared.database import get_db
from backend.features.auth.persistence.models import AdminUser, AuthProvider
from pydantic import BaseModel
import os
import logging
import requests
import jwt
import time
from datetime import datetime, timedelta
from passlib.context import CryptContext

router = APIRouter(prefix="/api", tags=["Auth"])
logger = logging.getLogger(__name__)

# Config
LARK_APP_ID = os.getenv("LARK_APP_ID")
LARK_APP_SECRET = os.getenv("LARK_APP_SECRET")
LARK_DOMAIN = os.getenv("LARK_DOMAIN", "https://open.larksuite.com")
# LARK_REDIRECT_URI removed - generated dynamically
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key") # TODO: Use Env
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 day

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

from backend.features.auth.persistence.models import Role

def ensure_user_role(db: Session, user: AdminUser):
    # 1. Fetch Roles
    super_admin_role = db.query(Role).filter(Role.name == "SUPER_ADMIN").first()
    user_role = db.query(Role).filter(Role.name == "USER").first()
    
    # 2. Check for Waili -> Super Admin
    if user.username.lower() == "waili":
        if user.role_id != super_admin_role.id:
            logger.info(f"Auto-assigning SUPER_ADMIN to {user.username}")
            user.role_id = super_admin_role.id
            user.role = super_admin_role.name
    
    # 3. Default to USER if no role
    elif not user.role_id:
        if user_role:
             logger.info(f"Auto-assigning USER to {user.username}")
             user.role_id = user_role.id
             user.role = user_role.name

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_tenant_access_token():
    url = f"{LARK_DOMAIN}/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    req_body = {
        "app_id": LARK_APP_ID,
        "app_secret": LARK_APP_SECRET
    }
    try:
        resp = requests.post(url, json=req_body, headers=headers)
        if resp.status_code != 200:
             logger.error(f"Failed to get Tenant Token: {resp.text}")
             return None
        return resp.json().get("tenant_access_token")
    except Exception as e:
        logger.error(f"Exception getting Tenant Token: {e}")
        return None

    except Exception as e:
        logger.error(f"Exception getting Tenant Token: {e}")
        return None

from backend.features.auth.service.rbac_service import RBACService
from backend.shared.dependencies import get_current_user

@router.get("/auth/me")
def get_current_user_info(user: AdminUser = Depends(get_current_user), db: Session = Depends(get_db)):
    rbac = RBACService(db)
    perms = rbac.get_user_permissions(user)
    
    return {
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role_obj.name if user.role_obj else user.role,
        "permissions": perms["page_permissions"],
        "is_super_admin": perms["is_super_admin"]
    }

# Local Login
@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(AdminUser).filter(AdminUser.username == request.username).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    if user.authProvider == AuthProvider.LARK.value:
         raise HTTPException(status_code=403, detail="Please login via Lark")
         
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
        
    # Update last login
    user.last_login = int(time.time() * 1000)
    db.commit()
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer", "username": user.username, "role": user.role}

# Lark Login Redirect
@router.get("/auth/lark/login")
def lark_login(request: Request):
    if not LARK_APP_ID:
        raise HTTPException(status_code=500, detail="Lark config missing")
    
    # Dynamic Redirect URI based on current request
    # Ensure scheme is https if behind weird proxies without proper headers, but usually request.url_for handles it if configured right
    
    # Dynamic Redirect URI based on current request
    req_url = str(request.url)
    logger.info(f"Lark Login Reqeust URL: {req_url}")
    
    # Strategy: Use LARK_REDIRECT_URI env var if available (Simplest & Best for Prod)
    LARK_REDIRECT_URI = os.getenv("LARK_REDIRECT_URI")
    
    if LARK_REDIRECT_URI:
        # Use provided full URI directly
        redirect_uri = LARK_REDIRECT_URI
        logger.info(f"Using LARK_REDIRECT_URI env: {redirect_uri}")
    elif "localhost" not in req_url and "127.0.0.1" not in req_url:
        # Fallback: Guess production based on Request Host if not localhost
        host = request.headers.get("host") or request.url.netloc
        redirect_uri = f"https://{host}/api/auth/lark/callback"
        logger.info(f"Guessed Production HTTPS Redirect URI: {redirect_uri}")
    else:
        # Localhost development
        redirect_uri = str(request.url_for('lark_callback'))
        logger.info(f"Using Localhost Redirect URI: {redirect_uri}")
            
    auth_url = f"{LARK_DOMAIN}/open-apis/authen/v1/authorize?app_id={LARK_APP_ID}&redirect_uri={redirect_uri}&state=RANDOM_STATE"
    return RedirectResponse(auth_url)

# Lark Callback
@router.get("/auth/lark/callback", name="lark_callback")
def lark_callback(request: Request, code: str, state: str = None, gap: str = None,  db: Session = Depends(get_db)):
    # Reconstruct the redirect_uri used in login
    
    # Strategy: Use LARK_REDIRECT_URI env var if available
    LARK_REDIRECT_URI = os.getenv("LARK_REDIRECT_URI")
    req_url = str(request.url)
    
    if LARK_REDIRECT_URI:
        redirect_uri = LARK_REDIRECT_URI
    elif "localhost" not in req_url and "127.0.0.1" not in req_url:
        host = request.headers.get("host") or request.url.netloc
        redirect_uri = f"https://{host}/api/auth/lark/callback"
    else:
        redirect_uri = str(request.url_for('lark_callback'))

    # 1. Get Tenant Access Token
    tenant_access_token = get_tenant_access_token()
    if not tenant_access_token:
         raise HTTPException(status_code=500, detail="Failed to obtain Tenant Access Token")

    # 2. Get User Access Token
    token_url = f"{LARK_DOMAIN}/open-apis/authen/v1/oidc/access_token"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {tenant_access_token}"
    }
    payload = {
        "grant_type": "authorization_code",
        "client_id": LARK_APP_ID,
        "client_secret": LARK_APP_SECRET,
        "code": code,
        "redirect_uri": redirect_uri
    }
    
    resp = requests.post(token_url, json=payload, headers=headers)
    if resp.status_code != 200:
        logger.error(f"Lark Token Error: {resp.text}")
        raise HTTPException(status_code=400, detail="Failed to get Lark token")
        
    data = resp.json()
    if "data" not in data:
         logger.error(f"Lark Token Error Body: {data}")
         raise HTTPException(status_code=400, detail="Invalid Lark token response")

    user_access_token = data["data"]["access_token"]
    
    # 3. Get User Info
    user_info_url = f"{LARK_DOMAIN}/open-apis/authen/v1/user_info"
    user_headers = {"Authorization": f"Bearer {user_access_token}"}
    user_resp = requests.get(user_info_url, headers=user_headers)
    
    if user_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get User Info")
        
    user_data = user_resp.json().get("data", {})
    
    # Logic to determine username (name > en_name > email > user_id)
    username = user_data.get("name") or user_data.get("en_name") or user_data.get("email") or user_data.get("user_id")
    
    # Check if user exists
    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    
    if not user:
        # Auto-provision
        user = AdminUser(
            username=username,
            authProvider=AuthProvider.LARK.value,
            role="USER", # Default legacy
            email=user_data.get("email"),
            full_name=user_data.get("name"),
            lark_user_id=user_data.get("user_id"),
            lark_open_id=user_data.get("open_id")
        )
        db.add(user)
        db.commit() # Commit to get ID
        db.refresh(user)
    else:
        # Update existing
        user.authProvider = AuthProvider.LARK.value
        user.last_login = int(time.time() * 1000)
        db.commit()

    # Ensure Role (For new or existing users)
    ensure_user_role(db, user)
    
    db.commit()
    db.refresh(user)
    
    # Issue JWT
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    
    # Redirect to Frontend
    # Strategy: 
    # 1. Use FRONTEND_URL env var if set (Manual Override)
    # 2. If Localhost, default to http://localhost:5173 (Vite Dev Server)
    # 3. If Production (Same Domain), derive from Request Host
    
    env_frontend = os.getenv("FRONTEND_URL")
    if env_frontend:
         base_url = env_frontend.rstrip("/")
    elif "localhost" in str(request.url) or "127.0.0.1" in str(request.url):
         base_url = "http://localhost:5173"
    else:
         # Production: Use the same host as the backend (served together)
         # Force HTTPS for safety in Prod
         host = request.headers.get("host") or request.url.netloc
         base_url = f"https://{host}"
         
    frontend_url = f"{base_url}/login?token={access_token}"
    return RedirectResponse(frontend_url)

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from backend.shared.database import get_db
# Import AdminUser from the new feature location (Forward reference)
# Note: We assume the running environment has 'backend' in path or we are running as a module
from backend.features.auth.persistence.models import AdminUser
import os
import logging

logger = logging.getLogger(__name__)

# Config - specific to Validation
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key")
JWT_ALGORITHM = "HS256"

# TokenUrl points to the login endpoint, used by OpenAPI docs (Swagger UI)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.warning("Token payload missing 'sub' (username)")
            raise credentials_exception
    except jwt.PyJWTError as e:
        logger.warning(f"JWT Verification Failed: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {e}")
        raise credentials_exception
        
    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    if user is None:
        logger.warning(f"User not found for token: {username}")
        raise credentials_exception
    
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user

from fastapi import Request
from backend.features.auth.service.rbac_service import RBACService

def check_permission(request: Request, user: AdminUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Dependency to check if the current user has permission to access the requested API.
    """
    # Exclude open APIs if any (though get_current_user enforces auth)
    # The login endpoint is usually excluded from get_current_user
    
    service = RBACService(db)
    # Use request.url.path to get the path
    # Note: If app is mounted under /api, path might include it. 
    # Our PERMISSIONS_CONFIG definitions include /api prefix.
    
    if not service.check_api_access(user, request.method, request.url.path):
        logger.warning(f"Permission Denied for user {user.username} on {request.method} {request.url.path}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )


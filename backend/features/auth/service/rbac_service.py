from sqlalchemy.orm import Session
from backend.features.auth.persistence.models import AdminUser, Role, PagePermission, ApiPermission
import re

class RBACService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_permissions(self, user: AdminUser):
        """
        Return a dict with:
        - page_permissions: list of page codes (e.g. ['USER_MANAGEMENT'])
        - api_permissions: list of dicts (method, path)
        """
        if not user.role_obj:
             return {"page_permissions": [], "api_permissions": []}

        # If SUPER_ADMIN, return ALL (or handle logic to bypass)
        # For explicit list, we can fetch all. But better to handle bypass in check_permission.
        # But for frontend, we might want to send a special flag or all codes.
        
        if user.role_obj.name == 'SUPER_ADMIN':
             # Return "ALL" or fetch all codes? 
             # Let's fetch all codes so frontend doesn't need special logic
             all_pages = self.db.query(PagePermission).all()
             return {
                 "page_permissions": [p.code for p in all_pages],
                 # Frontend usually doesn't need API list, but let's be consistent
                 "is_super_admin": True
             }

        # Normal User
        page_perms = user.role_obj.permissions
        return {
            "page_permissions": [p.code for p in page_perms],
            "is_super_admin": False
        }

    def check_api_access(self, user: AdminUser, method: str, path: str) -> bool:
        """
        Check if user has access to this API.
        """
        # 1. Super Admin bypass
        if user.role_obj and user.role_obj.name == 'SUPER_ADMIN':
            return True

        # 2. Check if API is protected at all? 
        # If an API is NOT in ApiPermission table, is it public or denied?
        # Requirement says "One page corresponds to multiple permissions".
        # If we enforce strict RBAC, default should be deny if configured? 
        # But we have many existing APIs. 
        # Let's assume: If API is in PERMISSIONS_CONFIG, it REQUIRES permission.
        # If NOT in config, it's open (or handled by authenticated dependency only).
        
        # However, to be strict: 
        # For now, let's implement: User must have a Page Permission that covers this API.
        
        if not user.role_obj:
            return False

        # Get all API permissions for this user
        # user.role_obj.permissions -> PagePermission -> ApiPermission
        
        # Optimization: Query DB directly? Or load eager? 
        # Given small number of permissions, iterating loaded object is fine.
        
        for page_perm in user.role_obj.permissions:
             for api_perm in page_perm.api_permissions:
                 if api_perm.method == method:
                     # Check Path match (exact or regex?)
                     # For simplicity, assuming exact or simple * wildcards if we implemented them.
                     if api_perm.path == path:
                         return True
                     
                     # Handle /api/users/{id} vs /api/users/123
                     # This requires path matching logic. 
                     # Fast way: Check if configured path regex matches current path.
                     # But simple approach: 
                     # If configured path has {param}, convert to regex.
                     # E.g. /api/users/{id} -> /api/users/[^/]+
                     
                     if self._match_path(api_perm.path, path):
                         return True
                         
        return False

    def _match_path(self, pattern: str, actual: str) -> bool:
        """
        Match URL path with pattern.
        Pattern can contain {param}.
        """
        if pattern == actual:
            return True
            
        # Convert pattern to regex
        # Escape special chars except { }
        regex = "^" + pattern.replace("{", "(?P<").replace("}", ">[^/]+)") + "$"
        # Note: This is a simplistic conversion. 
        # Real implementation might need more robust router matching.
        # Alternatively, we can rely on how we define permissions in config. 
        # If we define `/api/users/{id}`, we expect exact string match if we use Starlette routing?
        # No, actual request path is `/api/users/1`.
        
        # Let's use simple regex replacement for {}
        
        # Escape existing regex chars
        # escaped = re.escape(pattern) # This escapes { } too.
        
        # Manual regex:
        # Split by /, match segments
        
        p_parts = pattern.split('/')
        a_parts = actual.split('/')
        
        if len(p_parts) != len(a_parts):
            return False
            
        for p, a in zip(p_parts, a_parts):
            if p.startswith('{') and p.endswith('}'):
                continue # Matches anything
            if p != a:
                return False
                
        return True

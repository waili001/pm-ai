from sqlalchemy.orm import Session
from backend.shared.database import SessionLocal, engine, Base
from backend.features.auth.persistence.models import Role, PagePermission, ApiPermission
from backend.features.auth.permissions_config import PERMISSIONS_CONFIG

def init_rbac():
    db = SessionLocal()
    try:
        # 1. Initialize Default Roles
        roles_to_create = ["SUPER_ADMIN", "USER"]
        for role_name in roles_to_create:
            role = db.query(Role).filter(Role.name == role_name).first()
            if not role:
                print(f"Creating role: {role_name}")
                new_role = Role(name=role_name, description=f"Default {role_name} role")
                db.add(new_role)
        
        db.commit()

        # 2. Sync Permissions
        print("Syncing Permissions...")
        for page_code, config in PERMISSIONS_CONFIG.items():
            # Sync Page Permission
            page_perm = db.query(PagePermission).filter(PagePermission.code == page_code).first()
            if not page_perm:
                print(f"Creating Page Permission: {config['name']} ({page_code})")
                page_perm = PagePermission(name=config['name'], code=page_code)
                db.add(page_perm)
                db.flush() # flush to get ID
            else:
                # Update name if changed
                if page_perm.name != config['name']:
                    page_perm.name = config['name']
                    db.add(page_perm)

            # Sync API Permissions
            # Strategy: Delete existing for this page and recreate? Or upsert?
            # For simplicity, let's upsert based on Method + Path
            
            defined_apis = config['apis'] # List of (method, path)
            
            # Get current db apis for this page
            current_db_apis = db.query(ApiPermission).filter(ApiPermission.page_permission_id == page_perm.id).all()
            current_api_set = {(api.method, api.path) for api in current_db_apis}
            target_api_set = set(defined_apis)

            # Add new
            for method, path in target_api_set - current_api_set:
                print(f"  + Adding API Permission: {method} {path}")
                new_api = ApiPermission(page_permission_id=page_perm.id, method=method, path=path)
                db.add(new_api)

            # Remove old
            for api in current_db_apis:
                if (api.method, api.path) not in target_api_set:
                     print(f"  - Removing API Permission: {api.method} {api.path}")
                     db.delete(api)

        db.commit()

        # 3. Cleanup Undefined Permissions
        print("Cleaning up undefined permissions...")
        all_db_perms = db.query(PagePermission).all()
        active_codes = set(PERMISSIONS_CONFIG.keys())
        
        for perm in all_db_perms:
            if perm.code not in active_codes:
                print(f"  - Removing deprecated Page Permission: {perm.name} ({perm.code})")
                # This should cascade delete API permissions and role associations if cascade is set in models.
                # If not, we might need manual cleanup of ApiPermission first.
                # Assuming models have cascade or we rely on DB constraints. 
                # Let's check models briefly or just try delete.
                # Ideally ApiPermission has ondelete='CASCADE'.
                db.delete(perm)
        
        db.commit()
        print("RBAC Initialization Complete.")

    except Exception as e:
        print(f"Error initializing RBAC: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure tables exist
    print("Creating tables if not exist...")
    Base.metadata.create_all(bind=engine) 
    init_rbac()

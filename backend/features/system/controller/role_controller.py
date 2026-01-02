from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend.shared.database import get_db
from backend.shared.dependencies import check_permission
from backend.features.auth.persistence.models import Role, PagePermission
from backend.features.auth.permissions_config import PERMISSIONS_CONFIG

router = APIRouter(
    prefix="/api/system/roles",
    tags=["System - Roles"],
    dependencies=[Depends(check_permission)]
)

# Pydantic Models
class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str] = [] # List of Page Codes

class RoleUpdate(BaseModel):
    description: Optional[str] = None
    permissions: List[str] = [] # List of Page Codes

from pydantic import BaseModel

class RoleDTO(BaseModel):
    id: int
    name: str
    description: Optional[str]
    permissions: List[str] # List of codes

    class Config:
        from_attributes = True

class RoleCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str] = []

class RoleUpdateRequest(BaseModel):
    description: Optional[str] = None
    permissions: List[str] = []

@router.get("", response_model=List[RoleDTO])
def get_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    # Map permissions manually to codes
    result = []
    for r in roles:
        codes = [p.code for p in r.permissions]
        result.append(RoleDTO(id=r.id, name=r.name, description=r.description, permissions=codes))
    return result

@router.get("/permissions")
def get_all_permissions(db: Session = Depends(get_db)):
    """List all available page permissions for assignment"""
    count = db.query(PagePermission).count()
    if count == 0:
         # Fallback to config if DB empty (shouldn't happen due to init script)
         return list(PERMISSIONS_CONFIG.keys())
         
    perms = db.query(PagePermission).all()
    return [{"code": p.code, "name": p.name} for p in perms]

@router.post("", response_model=RoleDTO)
def create_role(role_in: RoleCreateRequest, db: Session = Depends(get_db)):
    # Check if exists
    existing = db.query(Role).filter(Role.name == role_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role already exists")
    
    new_role = Role(name=role_in.name, description=role_in.description)
    db.add(new_role)
    db.commit() # Get ID
    
    # Assign Permissions
    if role_in.permissions:
        perms = db.query(PagePermission).filter(PagePermission.code.in_(role_in.permissions)).all()
        new_role.permissions = perms
        db.commit()
    
    codes = [p.code for p in new_role.permissions]
    return RoleDTO(id=new_role.id, name=new_role.name, description=new_role.description, permissions=codes)

@router.put("/{role_id}", response_model=RoleDTO)
def update_role(role_id: int, role_in: RoleUpdateRequest, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    if role.name == "SUPER_ADMIN":
         raise HTTPException(status_code=400, detail="Cannot edit SUPER_ADMIN")

    if role_in.description is not None:
        role.description = role_in.description
    
    # Update Permissions
    # Clear existing and set new
    perms = db.query(PagePermission).filter(PagePermission.code.in_(role_in.permissions)).all()
    role.permissions = perms
    
    db.commit()
    db.refresh(role)
    
    codes = [p.code for p in role.permissions]
    return RoleDTO(id=role.id, name=role.name, description=role.description, permissions=codes)

@router.delete("/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
        
    if role.name in ["SUPER_ADMIN", "USER"]:
        raise HTTPException(status_code=400, detail="Cannot delete default roles")
        
    # Check if assigned to users?
    # Logic: Set users to USER role or block? 
    # For now, block if users exist
    if role.users:
         raise HTTPException(status_code=400, detail="Role is assigned to users. Reassign them first.")
         
    db.delete(role)
    db.commit()
    return {"message": "Role deleted"}

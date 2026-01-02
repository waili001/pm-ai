from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend.shared.database import get_db
from backend.shared.dependencies import check_permission
from backend.features.auth.persistence.models import AdminUser, Role

router = APIRouter(
    prefix="/api/system/users",
    tags=["System - Users"],
    dependencies=[Depends(check_permission)]
)

class UserRoleUpdate(BaseModel):
    role_id: int

class UserDTO(BaseModel):
    id: int
    username: str
    email: Optional[str]
    full_name: Optional[str]
    role: Optional[str] # Role Name
    role_id: Optional[int]
    is_active: bool
    last_login: Optional[int]

    class Config:
        from_attributes = True

@router.get("", response_model=List[UserDTO])
def get_users(db: Session = Depends(get_db)):
    users = db.query(AdminUser).all()
    result = []
    for u in users:
        role_name = u.role_obj.name if u.role_obj else u.role
        result.append(UserDTO(
            id=u.id, 
            username=u.username, 
            email=u.email, 
            full_name=u.full_name,
            role=role_name,
            role_id=u.role_id,
            is_active=u.is_active,
            last_login=u.last_login
        ))
    return result

@router.post("/role")
def assign_role_to_user(
    user_id: int = Body(...), 
    role_id: int = Body(...), 
    db: Session = Depends(get_db)
):
    user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
        
    # Prevent modifying Waili if it's super admin? 
    # Requirement: "Waili" is auto assigned. 
    # If admin tries to change Waili's role, should we allow? 
    # Let's block removing SUPER_ADMIN from Waili if logic dictates strictness.
    # But for now, general assign logic.
    
    if user.username.lower() == 'waili' and role.name != 'SUPER_ADMIN':
         # Warn or Allow? 
         # Given logic: "If login as Waili, auto assign SA". So if we change it here, it will be reset on next login.
         pass
         
    user.role_id = role.id
    user.role = role.name # Update legacy string field
    db.commit()
    
    return {"message": f"Role {role.name} assigned to user {user.username}"}

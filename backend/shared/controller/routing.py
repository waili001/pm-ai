from fastapi import FastAPI, Depends
from backend.shared.dependencies import get_current_user

# Import Routers
# Import Routers
from backend.features.project.controller import project_controller as project
from backend.features.sync.controller import sync_controller as sync
from backend.features.system.controller import system_controller as system
from backend.features.system.controller import role_controller as roles
from backend.features.system.controller import user_controller as users
from backend.features.member.controller import member_controller as member
from backend.features.auth.controller import auth_controller as auth

def register_routes(app: FastAPI):
    app.include_router(project.router, dependencies=[Depends(get_current_user)])
    app.include_router(sync.router, dependencies=[Depends(get_current_user)])
    app.include_router(system.router, dependencies=[Depends(get_current_user)])
    app.include_router(roles.router, dependencies=[Depends(get_current_user)])
    app.include_router(users.router, dependencies=[Depends(get_current_user)])
    app.include_router(member.router, dependencies=[Depends(get_current_user)])
    app.include_router(auth.router)

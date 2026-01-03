import sys
import os
# Add parent directory to path to allow importing 'backend' package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI

from fastapi import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from backend.shared.database import engine, Base
import logging
import os

# Import Routers
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Import needed for sync jobs in lifespan
# Import needed for sync jobs in lifespan
from backend.features.sync.service.sync_service import sync_lark_table, calculate_tp_completion
# Ensure all models are imported for Base.metadata.create_all
from backend.features.project.persistence.models import LarkModelTP, LarkModelTCG, LarkModelProgram
from backend.features.member.persistence.models import LarkModelMember
from backend.features.auth.persistence.models import AdminUser
from backend.features.system.persistence.models import LarkModelDept

# Logging Config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize DB
Base.metadata.create_all(bind=engine)

# Scheduler Setup
scheduler = BackgroundScheduler()

# Env Config for Scheduler
TP_APP_TOKEN = os.getenv("TP_APP_TOKEN")
TP_TABLE_ID = os.getenv("TP_TABLE_ID")
TCG_APP_TOKEN = os.getenv("TCG_APP_TOKEN")
TCG_TABLE_ID = os.getenv("TCG_TABLE_ID")
MEMBER_APP_TOKEN = os.getenv("MEMBER_APP_TOKEN")
MEMBER_TABLE_ID = os.getenv("MEMBER_TABLE_ID")
PROGRAM_APP_TOKEN = os.getenv("PROGRAM_APP_TOKEN")
PROGRAM_TABLE_ID = os.getenv("PROGRAM_TABLE_ID")

def run_sync_jobs(force_full: bool = False):
    logger.info(f"Running sync jobs... (Force Full: {force_full})")
    sync_lark_table(TP_APP_TOKEN, TP_TABLE_ID, LarkModelTP, force_full=force_full)
    sync_lark_table(TP_APP_TOKEN, TP_TABLE_ID, LarkModelTP, force_full=force_full)
    sync_lark_table(TCG_APP_TOKEN, TCG_TABLE_ID, LarkModelTCG, force_full=force_full)
    
    # Program Sync
    if PROGRAM_APP_TOKEN and PROGRAM_TABLE_ID:
        sync_lark_table(PROGRAM_APP_TOKEN, PROGRAM_TABLE_ID, LarkModelProgram, force_full=force_full)

    # Member Info Sync (15 min interval via scheduler)
    if MEMBER_APP_TOKEN and MEMBER_TABLE_ID:
        sync_lark_table(MEMBER_APP_TOKEN, MEMBER_TABLE_ID, LarkModelMember, force_full=force_full)

# Import Startup Scripts
from backend.scripts.migrate_db_rbac import migrate as run_db_migration
from backend.scripts.init_rbac import init_rbac

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run DB Migrations & RBAC Init on startup
    try:
        logger.info("Running DB Migrations...")
        run_db_migration()
        logger.info("Running RBAC Initialization...")
        init_rbac()
    except Exception as e:
        logger.error(f"Startup tasks failed: {e}")
        # Decide if we want to crash or continue. Crashing is safer for schema consistency.
        # raise e 

    # Start scheduler
    # Sync every 15 minutes as per Member Info requirement
    scheduler.add_job(run_sync_jobs, 'interval', minutes=15)
    scheduler.start()
    logger.info("Scheduler started")
    
    # Run once on startup using scheduler (non-blocking)
    from datetime import datetime
    scheduler.add_job(run_sync_jobs, 'date', run_date=datetime.now())
    
    scheduler.add_job(calculate_tp_completion, 'date', run_date=datetime.now())
    scheduler.add_job(calculate_tp_completion, 'interval', hours=1)
    
    
    yield
    
    # Shutdown scheduler
    scheduler.shutdown()
    logger.info("Scheduler shut down")

app = FastAPI(lifespan=lifespan)

# Trust Proxy Headers (for HTTPS on Railway)
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# CORS Configuration
# Allow CORS for local development by default, or specific origins from Env
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_str:
    origins = allowed_origins_str.split(",")
else:
    # Default local development
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

# If on Railway (RAILWAY_PUBLIC_DOMAIN env var exists), maybe add it?
railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
if railway_domain:
    origins.append(f"https://{railway_domain}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # If dynamic/wildcard needed, use ["*"] but be careful with auth
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
from backend.shared.controller.routing import register_routes
register_routes(app)

# Mount Static Files (Production Mode)
if os.path.isdir("static"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
    
    # SPA Fallback
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api"):
            return {"error": "API not found"}
        return FileResponse("static/index.html")

# Run Scheduler (Legacy startup event, prefer lifespan but keeping for compatibility if needed/mixed)
@app.on_event("startup")
async def start_scheduler():
    pass

from fastapi import FastAPI
from fastapi import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from database import engine, Base
import logging
import os

# Import Routers
from routers import project, jobs, system, member

# Import needed for sync jobs in lifespan
from jobs import sync_lark_table
from models import LarkModelTP, LarkModelTCG, LarkModelMember

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
       logging.StreamHandler(),
        logging.FileHandler('backend.log')
    ]
)
# Suppress Lark SDK debug logs
logging.getLogger("Lark").setLevel(logging.WARNING)
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

def run_sync_jobs(force_full: bool = False):
    logger.info(f"Running sync jobs... (Force Full: {force_full})")
    sync_lark_table(TP_APP_TOKEN, TP_TABLE_ID, LarkModelTP, force_full=force_full)
    sync_lark_table(TCG_APP_TOKEN, TCG_TABLE_ID, LarkModelTCG, force_full=force_full)
    # Member Info Sync (15 min interval via scheduler)
    if MEMBER_APP_TOKEN and MEMBER_TABLE_ID:
        sync_lark_table(MEMBER_APP_TOKEN, MEMBER_TABLE_ID, LarkModelMember, force_full=force_full)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start scheduler
    # Sync every 15 minutes as per Member Info requirement
    scheduler.add_job(run_sync_jobs, 'interval', minutes=15)
    scheduler.start()
    logger.info("Scheduler started")
    
    # Run once on startup for immediate data
    run_sync_jobs() # Run immediately on startup
    
    yield
    
    # Shutdown scheduler
    scheduler.shutdown()
    logger.info("Scheduler shut down")

app = FastAPI(lifespan=lifespan)

# Allow CORS for local development
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root Endpoint
@app.get("/")
def read_root():
    return {"message": "Jira verification job started in background"}

# Include Routers
# Include Routers
app.include_router(project.router)
app.include_router(jobs.router)
app.include_router(system.router)
app.include_router(member.router)

# Run Scheduler (Legacy startup event, prefer lifespan but keeping for compatibility if needed/mixed)
@app.on_event("startup")
async def start_scheduler():
    pass

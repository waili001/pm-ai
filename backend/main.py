from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from lark_service import list_records
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from database import engine, Base, SessionLocal
from jobs import sync_lark_table
from models import LarkModelTP, LarkModelTCG

# Initialize DB
Base.metadata.create_all(bind=engine)

# Scheduler Setup
scheduler = BackgroundScheduler()

import os

# TP Table Info
TP_APP_TOKEN = os.getenv("TP_APP_TOKEN")
TP_TABLE_ID = os.getenv("TP_TABLE_ID")

# TCG Table Info
TCG_APP_TOKEN = os.getenv("TCG_APP_TOKEN")
TCG_TABLE_ID = os.getenv("TCG_TABLE_ID")

def run_sync_jobs(force_full: bool = False):
    print(f"Running sync jobs... (Force Full: {force_full})")
    sync_lark_table(TP_APP_TOKEN, TP_TABLE_ID, LarkModelTP, force_full=force_full)
    sync_lark_table(TCG_APP_TOKEN, TCG_TABLE_ID, LarkModelTCG, force_full=force_full)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start scheduler
    scheduler.add_job(run_sync_jobs, 'interval', minutes=30)
    scheduler.start()
    print("Scheduler started.")
    
    # Run once on startup for immediate data
    run_sync_jobs() # Run immediately on startup
    
    yield
    
    # Shutdown scheduler
    scheduler.shutdown()
    print("Scheduler shut down.")

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

@app.post("/api/jobs/sync")
def trigger_sync():
    """Manually trigger a full sync of all tables."""
    # We run this in background or directly? For simplicity, running directly (blocking) 
    # so we can return status. In production, might want BackgroundTasks.
    # Given the requirements, blocking is fine for immediate feedback.
    try:
        run_sync_jobs(force_full=True)
        return {"status": "success", "message": "Sync jobs triggered successfully (Force Full)."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/data")
def get_data():
    return {"data": "This is data from the backend"}

@app.get("/api/lark/{app_token}/{table_id}")
def get_lark_data(app_token: str, table_id: str):
    return list_records(app_token, table_id)

from pydantic import BaseModel
from sqlalchemy import text, inspect

class SqlQuery(BaseModel):
    sql: str
    page: int = 1
    page_size: int = 50

@app.get("/api/db/tables")
def get_tables():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return {"tables": tables}

@app.post("/api/db/query")
def execute_sql_query(query: SqlQuery):
    db = SessionLocal()
    try:
        # Sanitize somewhat or just run (Admin only feature)
        # Using pagination with wrapping
        
        # 1. Get Total Count
        # Assuming simple SELECT query structure for total count wrapper
        count_sql = f"SELECT COUNT(*) FROM ({query.sql})"
        # Note: SQLAlchemy execute needs text() object
        total_count = db.execute(text(count_sql)).scalar()
        
        # 2. Get Data with Limit/Offset
        offset = (query.page - 1) * query.page_size
        paged_sql = f"SELECT * FROM ({query.sql}) LIMIT {query.page_size} OFFSET {offset}"
        result = db.execute(text(paged_sql))
        
        columns = result.keys()
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        
        return {
            "columns": list(columns),
            "data": rows,
            "total": total_count,
            "page": query.page,
            "page_size": query.page_size
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

# --- TP Status Feature APIs ---

@app.get("/api/tp/active")
def get_active_tps():
    """Fetch all active TP projects (Status != Closed/Resolved)."""
    db = SessionLocal()
    try:
        # User requirement: "jira status != Closed 或 Resolved"
        # We also filter out empty statuses just in case
        tps = db.query(LarkModelTP).filter(
            LarkModelTP.jira_status != "Closed",
            LarkModelTP.jira_status != "Resolved"
            # potentially filter nulls too: LarkModelTP.jira_status.isnot(None)
        ).all()
        
        results = []
        for tp in tps:
            # Format label for Autocomplete: "TP-123 Title"
            # Handle potential None values safely
            t_num = tp.ticket_number or "Unknown"
            title = tp.title or "No Title"
            label = f"{t_num} {title}"
            
            results.append({
                "id": tp.record_id,
                "ticket_number": t_num,
                "title": title,
                "label": label,
                "status": tp.jira_status
            })
        
        return results
    finally:
        db.close()

@app.get("/api/tp/{tp_number}/tcg_tickets")
def get_tcg_tickets_by_tp(tp_number: str):
    """Fetch TCG tickets associated with a specific TP number."""
    db = SessionLocal()
    try:
        # Note: tp_number should be exact string match e.g. "TP-3492"
        # Since input might vary case (tp-3492 vs TP-3492), we might want case-insensitive search
        # SQLite is case-insensitive by default for ASCII usually, but let's be safe.
        tickets = db.query(LarkModelTCG).filter(
            LarkModelTCG.tp_number.ilike(f"{tp_number}")
        ).all()
        
        results = []
        for t in tickets:
            results.append({
                "ticket_number": t.tcg_tickets, # Often the key identifier TCG-XXXX
                "title": t.title,
                "assignee": t.assignee,
                "reporter": t.reporter,
                "issue_type": t.issue_type,
                "status": t.jira_status, # For Kanban grouping
                "description": t.description  # Description field
            })
            
        return results
    finally:
        db.close()

import sys
import os

# Add parent directory to path if running as main
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from backend.shared.database import engine
import logging

logger = logging.getLogger(__name__)

def migrate_rbac(conn):
    """Ensure RBAC columns exist."""
    try:
        result = conn.execute(text("PRAGMA table_info(admin_user)"))
        columns = [row.name for row in result]
        
        if 'role_id' not in columns:
            logger.info("Adding 'role_id' column to 'admin_user' table...")
            conn.execute(text("ALTER TABLE admin_user ADD COLUMN role_id INTEGER REFERENCES roles(id)"))
            logger.info("Column 'role_id' added successfully.")
        else:
            logger.info("'role_id' column already exists in 'admin_user'.")
            
    except Exception as e:
        logger.error(f"RBAC Migration failed: {e}")

def migrate_tp_projects(conn):
    """Ensure TP Projects columns exist."""
    try:
        result = conn.execute(text("PRAGMA table_info(tp_projects)"))
        columns = [row.name for row in result]
        
        # Check for participated_dept
        if 'participated_dept' not in columns:
            logger.info("Adding 'participated_dept' column to 'tp_projects' table...")
            conn.execute(text("ALTER TABLE tp_projects ADD COLUMN participated_dept TEXT"))
            logger.info("Column 'participated_dept' added successfully.")
        else:
            logger.info("'participated_dept' column already exists in 'tp_projects'.")

        # Check for other potentially missing columns if any (e.g. completed_percentage, sort_order)
        if 'completed_percentage' not in columns:
             logger.info("Adding 'completed_percentage' column to 'tp_projects' table...")
             conn.execute(text("ALTER TABLE tp_projects ADD COLUMN completed_percentage INTEGER"))
        
        if 'sort_order' not in columns:
             logger.info("Adding 'sort_order' column to 'tp_projects' table...")
             conn.execute(text("ALTER TABLE tp_projects ADD COLUMN sort_order INTEGER DEFAULT 0"))

    except Exception as e:
        logger.error(f"TP Projects Migration failed: {e}")

def run_all_migrations():
    """Run all database migrations."""
    logger.info("--- Starting Database Migrations ---")
    with engine.connect() as conn:
        migrate_rbac(conn)
        migrate_tp_projects(conn)
        conn.commit()
    logger.info("--- Database Migrations Completed ---")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_all_migrations()

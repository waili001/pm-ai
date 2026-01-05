import sqlite3
import os

DB_path = "backend/sql_app.db"  # Correct path based on find command

def migrate():
    print(f"Migrating {DB_path}...")
    conn = sqlite3.connect(DB_path)
    cursor = conn.cursor()
    
    # Check if columns exist
    cursor.execute("PRAGMA table_info(tp_projects)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if "fe_completed_percentage" not in columns:
        print("Adding fe_completed_percentage...")
        cursor.execute("ALTER TABLE tp_projects ADD COLUMN fe_completed_percentage INTEGER DEFAULT 0")
        
    if "be_completed_percentage" not in columns:
        print("Adding be_completed_percentage...")
        cursor.execute("ALTER TABLE tp_projects ADD COLUMN be_completed_percentage INTEGER DEFAULT 0")
        
    if "fe_status_all_open" not in columns:
        print("Adding fe_status_all_open...")
        cursor.execute("ALTER TABLE tp_projects ADD COLUMN fe_status_all_open BOOLEAN DEFAULT 0")
        
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()

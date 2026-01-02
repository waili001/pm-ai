import sqlite3
import os

# Define the database path (adjust if running from different location)
DB_DIR = os.getenv("DB_DIR")
if DB_DIR:
    DB_PATH = os.path.join(DB_DIR, "sql_app.db")
else:
    # Assuming running from project root
    DB_PATH = "backend/sql_app.db"
    # Fallback if running inside backend dir
    if not os.path.exists(DB_PATH) and os.path.exists("sql_app.db"):
        DB_PATH = "sql_app.db"

if not os.path.exists(DB_PATH):
    print(f"Database not found at {DB_PATH}. Skipping migration.")
    exit(0)

print(f"Connecting to database: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Map OldName -> NewName
RENAME_MAP = {
    "AdminUser": "admin_user",
    "TP_Projects": "tp_projects",
    "TCG_Tickets": "tcg_tickets",
    "TCG_REMOVED_TICKETS": "tcg_removed_tickets",
    "TCG_DEPT": "tcg_dept",
    "MEMBER_INFO": "member_info",
    "TP_PROGRAM": "tp_program"
}

def table_exists(table_name):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None

for old_name, new_name in RENAME_MAP.items():
    if table_exists(old_name):
        # Check if already renamed (exact match)
        if table_exists(new_name) and old_name != new_name:
             # If strictly different cases but exists, sqlite might verify loosely
             pass
        
        print(f"Renaming '{old_name}' to '{new_name}'...")
        try:
            # 1. Rename to intermediate
            temp_name = f"{new_name}_tmp_rename"
            cursor.execute(f"ALTER TABLE {old_name} RENAME TO {temp_name}")
            # 2. Rename to final
            cursor.execute(f"ALTER TABLE {temp_name} RENAME TO {new_name}")
            print(f"Success: {old_name} -> {new_name}")
        except Exception as e:
            print(f"Error renaming {old_name}: {e}")
            # Attempt rollback/cleanup if stuck in temp? 
            # Simple script, just print error.
    else:
        # Check if new name exists (already migrated?)
        if table_exists(new_name):
            print(f"Table '{new_name}' already exists (as '{new_name}'). Skipping.")
        else:
            print(f"Table '{old_name}' not found. Skipping.")

conn.commit()
conn.close()
print("Migration completed.")

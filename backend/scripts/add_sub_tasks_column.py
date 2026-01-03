import sqlite3
import os

DB_PATH = "backend/sql_app.db"

def add_column():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(tcg_tickets)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "sub_tasks" not in columns:
            print("Adding 'sub_tasks' column to 'tcg_tickets'...")
            cursor.execute("ALTER TABLE tcg_tickets ADD COLUMN sub_tasks TEXT")
            conn.commit()
            print("Column added successfully.")
        else:
            print("Column 'sub_tasks' already exists.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_column()

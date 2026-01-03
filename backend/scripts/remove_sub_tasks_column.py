import sqlite3
import os

DB_PATH = "backend/sql_app.db"

def remove_column():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(tcg_tickets)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "sub_tasks" in columns:
            print("Removing 'sub_tasks' column from 'tcg_tickets'...")
            try:
                # SQLite 3.35.0+ supports DROP COLUMN
                cursor.execute("ALTER TABLE tcg_tickets DROP COLUMN sub_tasks")
                conn.commit()
                print("Column removed successfully.")
            except sqlite3.OperationalError:
                 print("SQLite version might not support DROP COLUMN directly. Ignoring for now as it doesn't break anything, just unused.")
        else:
            print("Column 'sub_tasks' does not exist.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    remove_column()

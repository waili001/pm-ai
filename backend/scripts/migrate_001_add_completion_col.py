
import sqlite3
import os

# Database path (relative to backend dir)
DB_DIR = os.getenv("DB_DIR")
if DB_DIR:
    DB_PATH = os.path.join(DB_DIR, "sql_app.db")
else:
    DB_PATH = "sql_app.db"

def migrate():
    print(f"Migrating database: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("Attempting to add 'completed_percentage' column to 'TP_Projects'...")
        cursor.execute("ALTER TABLE TP_Projects ADD COLUMN completed_percentage INTEGER")
        conn.commit()
        print("Success: Column added.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Info: Column already exists.")
        else:
            print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

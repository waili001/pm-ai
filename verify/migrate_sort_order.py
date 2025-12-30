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
        cursor.execute("PRAGMA table_info(TP_Projects)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "sort_order" not in columns:
            print("Adding sort_order column to TP_Projects...")
            cursor.execute("ALTER TABLE TP_Projects ADD COLUMN sort_order INTEGER DEFAULT 0")
            conn.commit()
            print("Column added successfully.")
        else:
            print("Column sort_order already exists.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_column()

from sqlalchemy import create_engine, text
import os

# Database Path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", "sql_app.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

def migrate():
    print(f"Connecting to database at {DB_PATH}...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("Checking TCG_Tickets table schema...")
        result = conn.execute(text("PRAGMA table_info(TCG_Tickets)"))
        columns = [row[1] for row in result.fetchall()]
        
        if "sort_order" not in columns:
            print("Adding 'sort_order' column to TCG_Tickets...")
            try:
                conn.execute(text("ALTER TABLE TCG_Tickets ADD COLUMN sort_order INTEGER DEFAULT 0"))
                conn.commit()
                print("Column added successfully.")
            except Exception as e:
                print(f"Error adding column: {e}")
        else:
            print("'sort_order' column already exists.")

if __name__ == "__main__":
    migrate()

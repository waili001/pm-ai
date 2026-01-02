
import sys
import os
from sqlalchemy import text
from backend.shared.database import engine

def migrate():
    print("--- Running RBAC DB Migration ---")
    with engine.connect() as conn:
        # Check if role_id exists
        try:
            # Sqlite pragma
            result = conn.execute(text("PRAGMA table_info(admin_user)"))
            columns = [row.name for row in result]
            
            if 'role_id' not in columns:
                print("Adding 'role_id' column to 'admin_user' table...")
                conn.execute(text("ALTER TABLE admin_user ADD COLUMN role_id INTEGER REFERENCES roles(id)"))
                conn.commit()
                print("Column added successfully.")
            else:
                print("'role_id' column already exists.")
                
            # Check for other changes? Models mismatch?
            # role column might exist as string, we keep it.
            
        except Exception as e:
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()

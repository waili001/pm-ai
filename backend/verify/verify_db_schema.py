
import sys
import os
from sqlalchemy import create_engine, inspect

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database import SQLALCHEMY_DATABASE_URL as DATABASE_URL

def verify_schema():
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    table_name = "TP_Projects"
    if not inspector.has_table(table_name):
        print(f"Error: Table {table_name} does not exist.")
        sys.exit(1)
        
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    target_col = "completed_percentage"
    
    if target_col in columns:
        print(f"Success: Column '{target_col}' exists in table '{table_name}'.")
        sys.exit(0)
    else:
        print(f"Failure: Column '{target_col}' NOT found in table '{table_name}'.")
        print(f"Existing columns: {columns}")
        sys.exit(1)

if __name__ == "__main__":
    verify_schema()

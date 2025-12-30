
import sys
import os

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import LarkModelProgram, LarkModelTP

# Setup DB connection
# Point to backend/sql_app.db
db_path = os.path.join(os.getcwd(), 'backend', 'sql_app.db')
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def inspect_programs():
    print("--- Inspecting TP_PROGRAM ---")
    programs = db.query(LarkModelProgram).limit(5).all()
    for p in programs:
        print(f"ID: {p.record_id}")
        print(f"  Program Title: {p.program_title}")
        print(f"  TP (Raw): {p.tp}")
        print(f"  TP Title: {p.tp_title}")
        print("-" * 20)

    print("\n--- Counting Programs ---")
    count = db.query(LarkModelProgram).count()
    print(f"Total Programs: {count}")

    # Check distinct program titles
    print("\n--- Distinct Program Titles ---")
    titles = db.query(LarkModelProgram.program_title).distinct().all()
    print([t[0] for t in titles])

if __name__ == "__main__":
    try:
        inspect_programs()
    finally:
        db.close()

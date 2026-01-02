from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

# Default to current directory, but allow override (e.g., /app/data for Railway Volume)
DB_DIR = os.getenv("DB_DIR", ".")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'sql_app.db')}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

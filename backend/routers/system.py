from fastapi import APIRouter
from database import engine, SessionLocal
from services.lark_service import list_records
from pydantic import BaseModel
from sqlalchemy import text, inspect

router = APIRouter(
    prefix="/api",
    tags=["system"]
)

class SqlQuery(BaseModel):
    sql: str
    page: int = 1
    page_size: int = 50

@router.get("/data")
def get_data():
    return {"data": "This is data from the backend"}

@router.get("/lark/{app_token}/{table_id}")
def get_lark_data(app_token: str, table_id: str):
    return list_records(app_token, table_id)

@router.get("/db/tables")
def get_tables():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return {"tables": tables}

@router.post("/db/query")
def execute_sql_query(query: SqlQuery):
    db = SessionLocal()
    try:
        # Sanitize somewhat or just run (Admin only feature)
        # Using pagination with wrapping
        
        # 1. Get Total Count
        # Assuming simple SELECT query structure for total count wrapper
        count_sql = f"SELECT COUNT(*) FROM ({query.sql})"
        # Note: SQLAlchemy execute needs text() object
        total_count = db.execute(text(count_sql)).scalar()
        
        # 2. Get Data with Limit/Offset
        offset = (query.page - 1) * query.page_size
        paged_sql = f"SELECT * FROM ({query.sql}) LIMIT {query.page_size} OFFSET {offset}"
        result = db.execute(text(paged_sql))
        
        columns = result.keys()
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        
        return {
            "columns": list(columns),
            "data": rows,
            "total": total_count,
            "page": query.page,
            "page_size": query.page_size
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

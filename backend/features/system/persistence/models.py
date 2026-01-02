from sqlalchemy import Column, Integer, String, BigInteger, Text
from backend.shared.database import Base

class LarkModelDept(Base):
    __tablename__ = "tcg_dept"

    record_id = Column(String, primary_key=True, index=True)
    updated_at = Column(BigInteger)
    
    # Specific Fields
    dept_id = Column(Text)
    department = Column(Text)
    tp_component = Column(String)
    tcg_component = Column(String)
    icr_component = Column(String)

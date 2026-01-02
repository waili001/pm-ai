from sqlalchemy import Column, String, BigInteger
from backend.shared.database import Base

class LarkModelMember(Base):
    __tablename__ = "member_info"
    
    record_id = Column(String, primary_key=True)
    updated_at = Column(BigInteger)
    
    member_no = Column(String)
    name = Column(String)
    department = Column(String)
    position = Column(String)
    team = Column(String)
    remark = Column(String)

    # Lark Field Mapping
    lark_mapping = {
        "No": "member_no",
        "Member": "name", 
        "Department": "department",
        "Position": "position",
        "Team": "team",
        "Remark": "remark"
    }

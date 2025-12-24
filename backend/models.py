from sqlalchemy import Column, Integer, String, BigInteger, Text, JSON
from database import Base

class LarkModelTP(Base):
    __tablename__ = "lark_tp"
    
    record_id = Column(String, primary_key=True, index=True)
    updated_at = Column(BigInteger) # Internal sync tracking
    
    # Specific Fields
    components = Column(Text) # List -> Comma separated string
    current_completion = Column(Integer)
    department = Column(Text) # List -> Comma separated string
    due_day_quarter = Column(String) # JSON -> value text
    icr_count = Column(Integer)
    jira_status = Column(String)
    project_manager = Column(Text) # Person List -> Names
    project_type = Column(String)
    released_month = Column(String) # JSON -> text
    source_id = Column(Text)
    ticket_number = Column(Text)
    title = Column(Text) # List of text -> String


class LarkModelTCG(Base):
    __tablename__ = "lark_tcg"

    record_id = Column(String, primary_key=True, index=True)
    updated_at = Column(BigInteger)

    # Fields matched from Lark Inspection
    assignee = Column(Text)
    description = Column(Text)
    components = Column(Text)
    created = Column(BigInteger) # or String if mapped
    created_quarter = Column(String)
    created_year_month = Column(String)
    department = Column(Text)
    fix_versions = Column(Text)
    issue_type = Column(String)
    jira_status = Column(String)
    relay_or_permission = Column(Text)
    reporter = Column(Text)
    resolved = Column(BigInteger)
    resolved_by = Column(Text)
    resolved_date = Column(String)
    resolved_month = Column(String)
    resolved_quarter = Column(String)
    resolved_week_num = Column(Integer)
    source_id = Column(Text)
    start_date = Column(String)
    tcg_tickets = Column(Text)
    tp_number = Column(Text)
    title = Column(Text)
    lark_updated_date = Column(String) # Mapped from 'Updated Date'

    # Legacy / Unused fields (Kept temporarily or if needed for other logic)
    status = Column(String) 
    product = Column(String)
    priority = Column(String)
    dev_owner = Column(Text) 
    qa_owner = Column(Text) 
    pm_owner = Column(Text) 
    created_date = Column(String) 
    business_priority = Column(String)
    values = Column(Text) 
    iteration = Column(String)
    labels = Column(Text)
    story_points = Column(Integer)


# Deprecated but kept for migration/ref if needed, or can be removed if fresh start
# class LarkRecord(Base):
#     __tablename__ = "lark_records"
# ...

from sqlalchemy import Column, Integer, String, BigInteger, Text, JSON
from database import Base

class LarkModelTP(Base):
    __tablename__ = "TP_Projects"
    
    record_id = Column(String, primary_key=True, index=True)
    updated_at = Column(BigInteger) # Internal sync tracking
    
    # Specific Fields
    components = Column(Text) # List -> Comma separated string
    department = Column(Text) # List -> Comma separated string
    
    # Analysis Fields
    completed_percentage = Column(Integer) # Calculated field: Closed / Total Tickets * 100
    
    current_completion = Column(Integer)
    due_day_quarter = Column(String) # JSON -> value text
    icr_count = Column(Integer)
    jira_status = Column(String)
    project_manager = Column(Text) # Person List -> Names
    project_type = Column(String)
    released_month = Column(String) # JSON -> text
    # New Fields
    released_date = Column(String) # Lark Date (ms) or formatted
    description = Column(Text)
    due_day = Column(String)
    start_date = Column(String)
    sit_date = Column(String)
    
    source_id = Column(Text)
    ticket_number = Column(Text)
    title = Column(Text) # List of text -> String


class LarkModelTCG(Base):
    __tablename__ = "TCG_Tickets"

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
    parent_tickets = Column(Text)  # Parent tickets reference from Lark "Parent Tickets" field
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


class TCGRemovedTickets(Base):
    __tablename__ = "TCG_REMOVED_TICKETS"

    ticket_number = Column(String, primary_key=True, index=True)
    deleted_at = Column(BigInteger)  # Timestamp of deletion


class LarkModelDept(Base):
    __tablename__ = "TCG_DEPT"

    record_id = Column(String, primary_key=True, index=True)
    updated_at = Column(BigInteger)
    
    # Specific Fields
    dept_id = Column(Text)
    department = Column(Text)
    tp_component = Column(String)
    tcg_component = Column(String)
    icr_component = Column(String)


class LarkModelMember(Base):
    __tablename__ = 'MEMBER_INFO'
    
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


class LarkModelProgram(Base):
    __tablename__ = "TP_PROGRAM"
    
    record_id = Column(String, primary_key=True, index=True)
    updated_at = Column(BigInteger)
    
    # Specific Fields
    no = Column(String)
    program_title = Column(Text)
    tp = Column(Text) # List -> Comma separated or Relation ID
    tp_title = Column(Text)
    department = Column(Text)
    tp_status = Column(String)
    progress = Column(String) # or Integer/Float depending on Lark field type, usually Text or Number
    due_day = Column(String) # Date/Time
    description = Column(Text)

    lark_mapping = {
        "No": "no",
        "Program Title": "program_title",
        "TP": "tp",
        "TP Title": "tp_title",
        "Department": "department",
        "TP Status": "tp_status",
        "Progress": "progress",
        "Due Day": "due_day",
        "Description": "description"
    }

"""
Debug script to check actual Lark field names
"""
import os
import sys
sys.path.append('/Users/waili/Work/project-others/pm-ai/backend')

from lark_service import list_records
from dotenv import load_dotenv

load_dotenv('/Users/waili/Work/project-others/pm-ai/backend/.env')

TP_APP_TOKEN = os.getenv("TP_APP_TOKEN")
TP_TABLE_ID = os.getenv("TP_TABLE_ID")

resp = list_records(TP_APP_TOKEN, TP_TABLE_ID)

if resp and "items" in resp:
    first_record = resp["items"][0]
    print("=== First Record Field Names ===")
    for field_name in first_record.get("fields", {}).keys():
        print(f"  - {field_name}")
    
    print("\n=== Sample Field Values ===")
    fields = first_record.get("fields", {})
    for key in list(fields.keys())[:10]:  # First 10 fields
        value = fields[key]
        print(f"{key}: {type(value).__name__} = {str(value)[:100]}")

from dotenv import load_dotenv
import os
import json
import logging
from lark_service import list_records

# Setup basic logging to see libraries output
logging.basicConfig(level=logging.INFO)

load_dotenv()

APP_TOKEN = os.getenv("TP_APP_TOKEN")
TABLE_ID = os.getenv("TP_TABLE_ID")

if not APP_TOKEN or not TABLE_ID:
    print("Error: TP_APP_TOKEN or TP_TABLE_ID not set in .env")
    exit(1)

print(f"Fetching records from Table: {TABLE_ID}")

# Fetch 1 page (up to 20 records default or whatever list_records does)
resp = list_records(APP_TOKEN, TABLE_ID, page_token=None)

if "items" in resp:
    items = resp["items"]
    print(f"Found {len(items)} items.")
    if items:
        # Check for specific fields in the first few items
        targets = ["Released Date", "Description", "Project Manager", "Due Day"]
        
        # Collect all unique keys across all items
        all_keys = set()
        for item in items:
            all_keys.update(item["fields"].keys())
        
        print("\nAll unique keys found in 500 items:")
        print(sorted(list(all_keys)))

        # Check for specific fields in the first few items
        targets = ["Released Date", "Release Date", "Description", "Project Manager", "Due Day", "Due Date"]
        
        
        print("\nSearching for items with non-empty 'Released Date' or 'Due Day':")
        found = False
        for item in items:
            fields = item["fields"]
            rd = fields.get("Released Date")
            dd = fields.get("Due Day")
            if rd or dd:
                print(f"Found Item: {item['record_id']}")
                print(f"  Released Date: {rd} (Type: {type(rd)})")
                print(f"  Due Day: {dd} (Type: {type(dd)})")
                print(f"  Title: {fields.get('Title')}")
                found = True
                break
        
        if not found:
            print("No items with 'Released Date' or 'Due Day' found in this page.")
    else:
        print("Items list is empty.")
else:
    print("No items found or error.")
    print(resp)

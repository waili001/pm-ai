import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *
import os
import json
from dotenv import load_dotenv

# Load env
load_dotenv()


# Load IDs from env
APP_ID = os.getenv("LARK_APP_ID")
APP_SECRET = os.getenv("LARK_APP_SECRET")
TP_APP_TOKEN = os.getenv("TP_APP_TOKEN")
TP_TABLE_ID = os.getenv("TP_TABLE_ID")
TCG_APP_TOKEN = os.getenv("TCG_APP_TOKEN")
TCG_TABLE_ID = os.getenv("TCG_TABLE_ID")
LARK_DOMAIN = os.getenv("LARK_DOMAIN", "https://open.larksuite.com")

def inspect_table_schema(name, app_token, table_id):
    print(f"\n--- Inspecting Schema for {name} ---")
    if not app_token or not table_id:
        print("Skipping: Missing Token or ID")
        return

    client = lark.Client.builder() \
        .app_id(APP_ID) \
        .app_secret(APP_SECRET) \
        .domain(LARK_DOMAIN) \
        .build()

    # Fetch just 1 record to see fields
    req_body = SearchAppTableRecordRequestBody.builder().build()
    request = SearchAppTableRecordRequest.builder() \
        .app_token(app_token) \
        .table_id(table_id) \
        .page_size(1) \
        .request_body(req_body) \
        .build()
    
    resp = client.bitable.v1.app_table_record.search(request)
    
    if not resp.success():
        print(f"FAILED: {resp.msg}")
        return
    
    data = json.loads(lark.JSON.marshal(resp.data))
    if data['items']:
        fields = data['items'][0]['fields']
        print(f"Found {len(fields)} fields. Keys:")
        print(sorted(fields.keys()))
        # for k, v in fields.items():
        #     print(f"  - {k}: {type(v).__name__} (Example: {v})")
    # Inspect Field Meta
    # Inspect Field Meta using SDK
    print("\n--- Field Metadata ---")
    req_fields = ListAppTableFieldRequest.builder() \
        .app_token(app_token) \
        .table_id(table_id) \
        .page_size(100) \
        .build()
    
    resp_fields = client.bitable.v1.app_table_field.list(req_fields)
    
    if resp_fields.success():
        items = resp_fields.data.items
        print(f"Found {len(items)} fields metadata:")
        for f in items:
            # Note: SDK objects might use different attribute access, checking structure via dict/marshal if needed
            # Usually f.field_name, f.field_id
            print(f"Name: {f.field_name}, ID: {f.field_id}, Type: {f.type}")
    else:
        print(f"Failed to fetch fields: {resp_fields.msg}")

if __name__ == "__main__":
    # inspect_table_schema("TP Table", TP_APP_TOKEN, TP_TABLE_ID)
    inspect_table_schema("TCG Table", TCG_APP_TOKEN, TCG_TABLE_ID)



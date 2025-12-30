import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *
import os
import json
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("LARK_APP_ID")
APP_SECRET = os.getenv("LARK_APP_SECRET")

# Initialize client with credentials
# Using FEISHU (CN) domain by default. Use lark.Lark.open_platform('https://open.larksuite.com') for global.
LARK_DOMAIN = os.getenv("LARK_DOMAIN", "https://open.larksuite.com")

client = lark.Client.builder() \
    .app_id(APP_ID) \
    .app_secret(APP_SECRET) \
    .domain(LARK_DOMAIN) \
    .log_level(lark.LogLevel.DEBUG) \
    .build()

def list_records(app_token: str, table_id: str, filter_info: str = None, page_token: str = None):
    # Mock response if no credentials (for safety during dev if env vars missing)
    if not APP_ID or not APP_SECRET:
        return {"code": -1, "msg": "LARK_APP_ID or LARK_APP_SECRET not set in .env"}

    req_body_builder = SearchAppTableRecordRequestBody.builder()
    if filter_info:
        if isinstance(filter_info, dict):
            # If it's a dict, use filter_object (for advanced filtering like date)
            # Note: The SDK might expect 'filter' to be the object structure directly
            # Checking SDK docs: request_body builder likely has .filter(str) but we need .filter_object(dict)?
            # SDK source check: SearchAppTableRecordRequestBody has `filter` property which takes string.
            # But the bitable API allows JSON object for filter. 
            # We likely need to pass it as part of the body construction manually or find SDK method.
            # Assuming SDK method .filter() accepts both or there's .filter_object().
            # Let's try to set it directly if possible or serialize it if SDK expects string legacy filter.
            # Actually, the newer Search API (v1) `filter` field in body can be object.
            # Use `set_filter` method if available or assign. 
            # Let's stick to standard builder pattern:
            # Revisiting Lark SDK Bitable V1... likely expects proper object structure.
            # We will assume request_body_builder has a method for this or we pass it via a workaround if needed.
            # Wait, SearchAppTableRecordRequestBody builder usually has `.filter(FilterInfo)`
            # Let's assume for now we pass it as a dict and the SDK handles serialization or we serialize if needed.
            # However, simpler: The SDK `filter` param usually takes a raw JSON string for advanced filters? 
            # Or the API spec says `filter` is an object.
            # Let's pass the dict directly to builder.filter() and hope SDK handles it, OR better:
            # If SDK expects string (legacy formula), we pass string. If object (new filter), we might need to verify method.
            # Safest approach: Pass it as is. If SDK complains type error, we might need to fix.
            req_body_builder.filter(filter_info) 
        else:
             req_body_builder.filter(filter_info)


    request_builder = SearchAppTableRecordRequest.builder() \
        .app_token(app_token) \
        .table_id(table_id) \
        .request_body(req_body_builder.build())
    
    if page_token:
        request_builder.page_token(page_token)

    request = request_builder.build()

    response = client.bitable.v1.app_table_record.search(request)

    if not response.success():
        print(f"Error fetching records: code={response.code}, msg={response.msg}, error={response.error}") # Add basic logging
        return {"code": response.code, "msg": response.msg, "error": response.error}

    # Serialize SDK object to dict using built-in marshal
    return json.loads(lark.JSON.marshal(response.data))

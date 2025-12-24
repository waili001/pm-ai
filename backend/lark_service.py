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

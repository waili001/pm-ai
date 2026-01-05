from dotenv import load_dotenv
import os
import sys
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.shared.integration.lark_client import client, lark


# Setup environment
load_dotenv(dotenv_path="backend/.env")
APP_TOKEN = os.getenv("TP_APP_TOKEN")
TABLE_ID = os.getenv("TP_TABLE_ID")

if not APP_TOKEN or not TABLE_ID:
    print("Missing env vars")
    exit(1)


request = lark.BaseRequest.builder() \
    .http_method(lark.HttpMethod.GET) \
    .uri(f"/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields") \
    .token_types({lark.AccessTokenType.TENANT}) \
    .build()

resp = client.request(request)
if resp.success():
    data = json.loads(str(resp.raw.content, encoding='utf-8'))
    if "data" in data and "items" in data["data"]:
        print("Table Fields:")
        for field in data["data"]["items"]:
            print(f" - {field['field_name']} (Type: {field['type']})")
    else:
        print("No fields found", data)
else:
    print(f"Error: {resp.code} {resp.msg}")


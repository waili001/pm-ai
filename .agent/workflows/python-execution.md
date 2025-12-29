---
description: Python 腳本執行和資料檢查標準流程
---

# Python 腳本執行標準流程

在此專案中執行 Python 程式碼時的最佳實踐。

## 原則

1. **永遠建立獨立檔案**：避免使用 `python -c "..."` 執行複雜程式碼
2. **必須啟用虛擬環境**：所有需要專案依賴的操作都要先啟用 venv
3. **執行後清理**：臨時檢查腳本用完後應刪除

## 檢查資料庫資料

### 建立檢查腳本

```python
# check_data.py
from database import SessionLocal
from models import LarkModelTCG
import json

db = SessionLocal()
record = db.query(LarkModelTCG).first()

print('=== 資料範例 ===')
if record:
    for col in record.__table__.columns:
        value = getattr(record, col.name)
        print(f'{col.name}: {value}')
else:
    print('No records found')

db.close()
```

### 執行

```bash
cd backend
source venv/bin/activate && python3 check_data.py
```

### 清理

```bash
cd backend
rm check_data.py
```

## 檢查 Lark 欄位

### 建立 Lark 檢查腳本

```python
# check_lark_fields.py
from lark_service import list_records
import json
import os

TCG_APP_TOKEN = os.getenv("TCG_APP_TOKEN")
TCG_TABLE_ID = os.getenv("TCG_TABLE_ID")

print(f"Fetching from TCG Table: {TCG_TABLE_ID}")
resp = list_records(TCG_APP_TOKEN, TCG_TABLE_ID, None, None)

if resp and "items" in resp:
    if len(resp["items"]) > 0:
        first_record = resp["items"][0]
        print("\n=== 欄位列表 ===")
        print(json.dumps(list(first_record["fields"].keys()), indent=2, ensure_ascii=False))
else:
    print("No records found")
```

### 執行

```bash
cd backend
source venv/bin/activate && python3 check_lark_fields.py
```

## 一行指令快速檢查

### 檢查資料表欄位

```bash
cd backend
source venv/bin/activate && python3 -c "from database import SessionLocal; from sqlalchemy import text; db = SessionLocal(); result = db.execute(text('PRAGMA table_info(lark_tcg)')); [print(row[1]) for row in result.fetchall()]; db.close()"
```

### 檢查資料筆數

```bash
cd backend
source venv/bin/activate && python3 -c "from database import SessionLocal; from models import LarkModelTCG; db = SessionLocal(); count = db.query(LarkModelTCG).count(); print(f'Total records: {count}'); db.close()"
```

### 檢查特定欄位值

```bash
cd backend
source venv/bin/activate && python3 -c "from database import SessionLocal; from models import LarkModelTCG; db = SessionLocal(); sample = db.query(LarkModelTCG).first(); print(f'parent_ticket: {sample.parent_ticket}'); db.close()"
```

## 虛擬環境管理

### 啟用虛擬環境

```bash
cd backend
source venv/bin/activate
```

### 檢查虛擬環境是否啟用

```bash
which python3
# 應該顯示：/Users/waili/Work/project-others/pm-ai/backend/venv/bin/python3
```

### 停用虛擬環境

```bash
deactivate
```

## 常見錯誤和解決方案

### ModuleNotFoundError: No module named 'lark_oapi'

**原因**：未啟用虛擬環境

**解決**：
```bash
cd backend
source venv/bin/activate
```

### sqlite3.OperationalError: no such table: lark_tcg

**原因**：使用了錯誤的資料庫檔案路徑

**解決**：確認目前在 `backend` 目錄下，資料庫檔案是 `sql_app.db`

### SyntaxError in python -c command

**原因**：一行指令中的語法太複雜

**解決**：建立獨立的 .py 檔案
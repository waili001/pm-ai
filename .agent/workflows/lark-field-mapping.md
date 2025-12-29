---
description: Lark 欄位同步和映射標準流程
---

# Lark 欄位同步和映射流程

處理 Lark 多維表格欄位映射到資料庫的完整流程。

## 欄位映射機制

### 命名轉換規則

Lark 欄位名稱會經過 `normalize_lark_key()` 函數轉換：

- `"Ticket Number"` → `ticket_number`
- `"Due Day (Quarter)"` → `due_day_quarter`
- `"Created Year-Month"` → `created_year_month`
- `"Parent Ticket"` → `parent_ticket`

**規則**：
1. 轉換為小寫
2. 空格替換為下劃線 `_`
3. 移除括號 `()` 和連字號 `-`

### 值提取規則

`extract_lark_value()` 函數處理不同類型的值：

- **Person 列表**: 提取 `name` 或 `email`
- **Select 列表**: 提取 `text`
- **Text 列表**: 逗號分隔字串
- **單一物件**: 提取 `name` 或 `text`
- **原始值**: 直接使用

## 添加新欄位的完整流程

### 步驟 1: 檢查 Lark 當前欄位

建立檢查腳本確認欄位是否存在：

```bash
cd backend
cat > check_lark_fields.py << 'EOF'
from lark_service import list_records
import json
import os

TCG_APP_TOKEN = os.getenv("TCG_APP_TOKEN")
TCG_TABLE_ID = os.getenv("TCG_TABLE_ID")

resp = list_records(TCG_APP_TOKEN, TCG_TABLE_ID, None, None)

if resp and "items" in resp and len(resp["items"]) > 0:
    first_record = resp["items"][0]
    print("=== Lark 欄位列表 ===")
    for key in sorted(first_record["fields"].keys()):
        print(f"  - {key}")
EOF

source venv/bin/activate && python3 check_lark_fields.py
rm check_lark_fields.py
```

### 步驟 2: 在 Lark 中添加欄位（如需要）

如果 Lark 表格中沒有所需欄位：

1. 前往 Lark 多維表格
2. 添加新欄位（例如 "Parent Ticket"）
3. 設定欄位類型（Text、Select、Person 等）
4. 填充一些測試資料

### 步驟 3: 更新 Model

在 `backend/models.py` 中添加對應欄位：

```python
class LarkModelTCG(Base):
    # ... 其他欄位
    parent_ticket = Column(Text)  # 新增欄位
```

**命名規則**：使用經過 `normalize_lark_key()` 轉換後的名稱

### 步驟 4: 執行資料庫遷移

參考 `database-migration.md` workflow

```bash
cd backend
sqlite3 sql_app.db "ALTER TABLE lark_tcg ADD COLUMN parent_ticket TEXT;"
```

### 步驟 5: 更新 API（如需要）

在 `backend/main.py` 的 API response 中添加新欄位：

```python
results.append({
    # ... 其他欄位
    "parent_ticket": t.parent_ticket
})
```

### 步驟 6: 觸發完整同步

```bash
curl -X POST http://127.0.0.1:8000/api/jobs/sync
```

或等待 30 分鐘自動同步

### 步驟 7: 驗證資料映射

檢查資料是否正確同步：

```bash
cd backend
source venv/bin/activate && python3 -c "from database import SessionLocal; from models import LarkModelTCG; db = SessionLocal(); sample = db.query(LarkModelTCG).first(); print(f'parent_ticket: {sample.parent_ticket}'); db.close()"
```

## 查看映射詳情

### 檢查 normalize 轉換結果

```python
from jobs import normalize_lark_key

# 測試轉換
print(normalize_lark_key("Parent Ticket"))  # parent_ticket
print(normalize_lark_key("Created Year-Month"))  # created_year_month
```

### 檢查值提取邏輯

建立測試腳本查看實際提取的值：

```python
# test_extraction.py
from lark_service import list_records
from jobs import extract_lark_value
import os
import json

TCG_APP_TOKEN = os.getenv("TCG_APP_TOKEN")
TCG_TABLE_ID = os.getenv("TCG_TABLE_ID")

resp = list_records(TCG_APP_TOKEN, TCG_TABLE_ID, None, None)

if resp and "items" in resp and len(resp["items"]) > 0:
    first_record = resp["items"][0]
    
    print("=== 欄位值提取測試 ===")
    for key, value in first_record["fields"].items():
        extracted = extract_lark_value(value)
        print(f"\n{key}:")
        print(f"  原始: {type(value).__name__}")
        print(f"  提取: {extracted}")
```

## 當前 Lark TCG 表格欄位

**最後檢查時間**: 2025-12-24

已確認的欄位：
- Assignee (Person)
- Components (Multi-select)
- Created (Date)
- Created Quarter (Text)
- Created Year-Month (Text)
- Department (Select)
- Description (Text)
- Fix Versions (Text)
- Issue Type (Select)
- JIRA Status (Select)
- Relay or Permission (Select)
- Reporter (Person)
- Resolved (Date)
- Resolved By (Person)
- Resolved Date (Number)
- Resolved Month (Text)
- Resolved Quarter (Text)
- ResolvedWeekNum (Number)
- SourceID (Text)
- Start Date (Date)
- TCG Tickets (Text)
- TP Number (Text)
- Title (Text)
- Updated Date (Date)

**缺少的欄位**: Parent Ticket（需要在 Lark 中手動添加）

## Debug 映射問題

如果欄位沒有正確映射：

1. **檢查欄位名稱轉換**：
   ```python
   from jobs import normalize_lark_key
   print(normalize_lark_key("您的欄位名稱"))
   ```

2. **檢查 Model 是否有該欄位**：
   ```python
   from models import LarkModelTCG
   print([c.name for c in LarkModelTCG.__table__.columns])
   ```

3. **查看同步 Debug 輸出**：
   同步時會輸出映射詳情，檢查 `[DEBUG] Mapped X/Y fields`

4. **手動測試值提取**：
   使用上面的 `test_extraction.py` 腳本

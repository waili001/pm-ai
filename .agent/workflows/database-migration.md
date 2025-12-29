---
description: 資料庫 Schema 遷移標準流程
---

# 資料庫 Schema 遷移標準流程

當需要在資料庫中添加、修改或刪除欄位時，請遵循以下步驟：

## 步驟 1: 修改 Model 定義

編輯 `backend/models.py`，在對應的 Model 類別中添加新欄位：

```python
# 範例：在 LarkModelTCG 中添加新欄位
new_field = Column(Text)  # 或其他適當的類型
```

## 步驟 2: 確認當前資料庫 Schema

在執行任何變更前，先檢查當前的資料庫結構：

```bash
cd backend
sqlite3 sql_app.db "PRAGMA table_info(lark_tcg);"
```

或使用 Python：

```bash
source venv/bin/activate && python3 -c "from database import SessionLocal; from sqlalchemy import text; db = SessionLocal(); result = db.execute(text('PRAGMA table_info(lark_tcg)')); [print(row) for row in result.fetchall()]; db.close()"
```

## 步驟 3: 執行 Schema 遷移

使用 SQLite ALTER TABLE 指令添加欄位：

```bash
cd backend
sqlite3 sql_app.db "ALTER TABLE lark_tcg ADD COLUMN new_field TEXT;"
```

**注意**：
- SQLite 的 ALTER TABLE 功能有限，只能添加欄位，不能修改或刪除
- 如需複雜的 schema 變更，考慮使用 Alembic 或重建資料庫

## 步驟 4: 驗證變更

確認欄位已成功添加：

```bash
cd backend
sqlite3 sql_app.db "PRAGMA table_info(lark_tcg);" | grep new_field
```

應該會看到類似輸出：
```
38|new_field|TEXT|0||0
```

## 步驟 5: 更新 API Response（如需要）

如果新欄位需要透過 API 返回，編輯 `backend/main.py` 中的相應 endpoint：

```python
results.append({
    # ... 其他欄位
    "new_field": t.new_field  # 添加新欄位
})
```

## 步驟 6: 測試

使用 Python 測試資料存取：

```bash
cd backend
source venv/bin/activate && python3 -c "from database import SessionLocal; from models import LarkModelTCG; db = SessionLocal(); sample = db.query(LarkModelTCG).first(); print(f'new_field: {sample.new_field}'); db.close()"
```

## 常見問題

### Q: 如果需要重建整個資料庫？

```bash
cd backend
rm sql_app.db
source venv/bin/activate && python3 -c "from database import engine, Base; Base.metadata.create_all(bind=engine); print('Database recreated')"
```

**警告**: 這會刪除所有現有資料！

### Q: 如何在 Lark 同步時自動填充新欄位？

1. 確保 Lark 表格中有對應的欄位（欄位名稱會經過 `normalize_lark_key()` 轉換）
2. 執行完整同步：POST `/api/jobs/sync`
3. 系統會自動映射欄位並填充資料

### Q: 資料庫檔案在哪裡？

- 檔案位置：`backend/sql_app.db`
- 連線設定：`backend/database.py`
- URL：`sqlite:///./sql_app.db`

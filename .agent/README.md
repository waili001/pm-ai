# PM-AI 專案 Workflows

此目錄包含專案的標準作業流程和最佳實踐。

## 📚 可用的 Workflows

### 1. [資料庫遷移](workflows/database-migration.md)
當需要修改資料庫 schema（添加/修改欄位）時使用

**關鍵步驟**:
- 修改 models.py
- 確認當前 schema
- 執行 SQLite ALTER TABLE
- 驗證變更
- 更新 API

### 2. [Python 腳本執行](workflows/python-execution.md)
在專案中正確執行 Python 程式碼和資料檢查

**關鍵原則**:
- 建立獨立檔案而非一行指令
- 永遠啟用虛擬環境
- 執行後清理臨時檔案

### 3. [Lark 欄位映射](workflows/lark-field-mapping.md)
處理 Lark 多維表格欄位同步到資料庫的完整流程

**關鍵概念**:
- 欄位名稱轉換規則（normalize_lark_key）
- 值提取邏輯（extract_lark_value）
- 完整的新欄位添加流程

### 4. [程式碼修改](workflows/code-modification.md)
使用程式碼修改工具的最佳實踐

**關鍵技巧**:
- 先 view_file 再修改
- 精確匹配 TargetContent
- 多處修改用 multi_replace_file_content

### 5. [移除 Debug Log](workflows/remove-debug-logs.md)
移除程式碼中的 debug 輸出語句

**處理內容**:
- Python `print()` 語句
- JavaScript `console.log()` 語句  
- 區分應保留和應移除的 log
- 替換為適當的 logging 框架

## 🎯 快速參考

### 資料庫相關
```bash
# 資料庫位置
backend/sql_app.db

# 查看 schema
sqlite3 backend/sql_app.db "PRAGMA table_info(lark_tcg);"

# 添加欄位
sqlite3 backend/sql_app.db "ALTER TABLE lark_tcg ADD COLUMN field_name TEXT;"
```

### Python 執行
```bash
# 永遠先啟用虛擬環境
cd backend
source venv/bin/activate

# 執行腳本
python3 your_script.py

# 清理
rm your_script.py
```

### Lark 同步
```bash
# 手動觸發同步
curl -X POST http://127.0.0.1:8000/api/jobs/sync

# 自動同步: 每 30 分鐘
```

## 🔧 專案結構

```
pm-ai/
├── backend/
│   ├── main.py           # FastAPI 應用和 API endpoints
│   ├── models.py         # SQLAlchemy 資料模型
│   ├── database.py       # 資料庫連線設定
│   ├── jobs.py           # Lark 同步任務和欄位映射
│   ├── lark_service.py   # Lark API 呼叫
│   ├── sql_app.db        # SQLite 資料庫
│   └── venv/             # Python 虛擬環境
├── frontend/
│   └── src/
│       ├── pages/
│       │   └── TPStatus.jsx  # TP Kanban 頁面
│       └── utils/
└── .agent/
    └── workflows/        # 此目錄
```

## 💡 使用建議

1. **遇到資料庫問題**: 查看 `database-migration.md`
2. **執行 Python 錯誤**: 查看 `python-execution.md`
3. **Lark 欄位沒同步**: 查看 `lark-field-mapping.md`
4. **程式碼修改失敗**: 查看 `code-modification.md`
5. **移除 debug 語句**: 查看 `remove-debug-logs.md`

## 🚨 常見陷阱

### ❌ ModuleNotFoundError
**原因**: 沒有啟用虛擬環境  
**解決**: `cd backend && source venv/bin/activate`

### ❌ target content not found
**原因**: TargetContent 與實際內容不匹配  
**解決**: 重新 view_file 並精確複製內容

### ❌ no such table
**原因**: 資料庫路徑錯誤  
**解決**: 確認在 backend 目錄下，資料庫是 sql_app.db

### ❌ Lark 欄位沒有同步
**原因**: Lark 表格中沒有該欄位  
**解決**: 先在 Lark 中添加欄位，再觸發同步

## 📝 貢獻新 Workflow

如果發現新的重複性任務或最佳實踐，歡迎添加新的 workflow 文件：

1. 在 `workflows/` 目錄建立新的 `.md` 檔案
2. 使用 YAML frontmatter 定義 description
3. 包含清楚的步驟說明和範例
4. 更新此 README

---

最後更新：2025-12-24

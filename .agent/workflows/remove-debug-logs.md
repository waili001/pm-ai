---
description: 移除程式碼中的 debug log 語句
---

# 移除 Debug Log 語句

在開發過程中，我們經常使用 `print()` 和 `console.log()` 來 debug。這個 workflow 幫助您識別和安全移除這些 debug 語句。

## Debug Log 類型

### Python (Backend)
- `print()` - 標準輸出
- `print(f"...")` - f-string 格式化輸出
- `pprint()` - Pretty print
- Debug 註解：`# DEBUG:`, `# TODO:`, `# FIXME:`

### JavaScript (Frontend)
- `console.log()` - 一般輸出
- `console.debug()` - Debug 輸出
- `console.warn()` - 警告
- `console.error()` - 錯誤（有些應保留）
- `console.table()`, `console.dir()` - 其他 console 方法

## 步驟 1: 搜尋 Debug 語句

### 搜尋 Python print 語句

```bash
cd backend
grep -rn "print(" . --include="*.py" --exclude-dir=venv
```

### 搜尋 JavaScript console 語句

```bash
cd frontend
grep -rn "console\." src/ --include="*.js" --include="*.jsx"
```

### 使用更精確的搜尋

```bash
# 只搜尋 console.log 和 console.debug
cd frontend
grep -rn "console\.\(log\|debug\)" src/
```

## 步驟 2: 分類 Debug 語句

並非所有輸出都應該移除。需要區分：

### ✅ 應該保留的

**Backend (Python)**:
- 錯誤處理中的 print (考慮改用 logging)
- 重要的狀態訊息（建議改用 logging）
- API 回應的錯誤訊息

**Frontend (JavaScript)**:
- `console.error()` - 錯誤訊息（通常保留）
- `console.warn()` - 警告訊息（視情況）
- 錯誤邊界中的 console

### ❌ 應該移除的

**Backend (Python)**:
- 單純的變數輸出：`print(variable)`
- Debug 用的格式化輸出：`print(f"Debug: {value}")`
- 測試用的輸出：`print("Here")`, `print("Test")`
- 開發時的資料檢查：`print(type(x))`, `print(len(y))`

**Frontend (JavaScript)**:
- `console.log()` - 幾乎所有的 log
- `console.debug()` - 所有的 debug
- `console.table()`, `console.dir()` - 開發用的輸出

### ⚠️ 需要評估的

- 包含重要業務邏輯資訊的 log
- 性能監控相關的輸出
- 同步狀態的輸出訊息

## 步驟 3: 檢視並決定

使用 grep 找出所有 debug 語句後，逐一檢視：

```bash
# 產生 debug 語句清單
cd backend
grep -rn "print(" . --include="*.py" --exclude-dir=venv > ../debug_statements.txt

cd ../frontend
grep -rn "console\." src/ >> ../debug_statements.txt
```

然後檢視 `debug_statements.txt`。

## 步驟 4: 移除 Debug 語句

### 方式 1: 手動移除（推薦）

使用編輯器打開檔案，逐一檢視並移除。

**VSCode 技巧**：
1. 使用搜尋功能 (Cmd/Ctrl + Shift + F)
2. 搜尋 `print\(` (使用 regex)
3. 檢視每個結果
4. 刪除不需要的行

### 方式 2: 使用腳本半自動移除

**警告**：這很危險，建議先備份或確保有 Git！

```python
# remove_debug_prints.py
import re
import sys

def remove_debug_prints(file_path):
    """移除明顯的 debug print 語句"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    removed = []
    
    for i, line in enumerate(lines, 1):
        # 檢查是否是明顯的 debug print
        stripped = line.strip()
        
        # 保留非 print 的行
        if not stripped.startswith('print('):
            new_lines.append(line)
            continue
        
        # 保留看起來重要的 print（包含 "error", "warning" 等）
        if any(keyword in stripped.lower() for keyword in ['error', 'warning', 'exception']):
            new_lines.append(line)
            continue
        
        # 移除看起來像 debug 的 print
        if any(keyword in stripped.lower() for keyword in ['debug', 'test', 'here', '===', '---']):
            removed.append((i, line.strip()))
            continue
        
        # 其他情況保留（需要手動檢查）
        new_lines.append(line)
    
    if removed:
        print(f"將移除 {len(removed)} 個 print 語句:")
        for line_num, line in removed[:5]:
            print(f"  Line {line_num}: {line}")
        if len(removed) > 5:
            print(f"  ... 以及其他 {len(removed) - 5} 個")
        
        choice = input("確認移除？(y/N): ")
        if choice.lower() == 'y':
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"✅ 已更新 {file_path}")
        else:
            print("❌ 已取消")
    else:
        print(f"沒有找到需要移除的 debug print 語句")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python remove_debug_prints.py <file.py>")
        sys.exit(1)
    
    remove_debug_prints(sys.argv[1])
```

使用方式：
```bash
python remove_debug_prints.py backend/jobs.py
```

### 方式 3: 替換為 Logging（推薦）

不是移除，而是改用適當的 logging：

**Python Example**:
```python
# 之前
print(f"Starting sync for table: {table_name}")

# 改為
import logging
logger = logging.getLogger(__name__)
logger.info(f"Starting sync for table: {table_name}")
```

**JavaScript Example**:
```javascript
// 之前
console.log('Data fetched:', data);

// 改為 (開發環境才輸出)
if (process.env.NODE_ENV === 'development') {
  console.log('Data fetched:', data);
}
```

## 步驟 5: 驗證

移除後務必測試：

```bash
# 重啟服務
./start.sh

# 測試主要功能
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/api/tp/active

# 檢查前端
# 在瀏覽器打開 http://127.0.0.1:5173
# 檢查 Console 是否還有不必要的輸出
```

## 本專案的 Debug Log 位置

### Backend 常見位置

- `jobs.py` - 同步任務的 debug 輸出
  - `print(f"Starting sync...")` 
  - `print(f"Fetched {len(records)} records")`
  - `print(f"[DEBUG] Mapped...")`
  
- `main.py` - 可能有測試用的 print
  
- `lark_service.py` - Lark API 呼叫的 debug

### Frontend 常見位置

- `src/pages/*.jsx` - 頁面元件中的 console.log
- `src/utils/*.js` - 工具函數中的 debug

## 自動化檢查

可以在 Git pre-commit hook 中加入檢查：

```bash
# .git/hooks/pre-commit
#!/bin/bash

# 檢查是否有 console.log
if git diff --cached --name-only | grep -E '\.(js|jsx)$' | xargs grep -n "console\.log"; then
    echo "❌ 發現 console.log，請移除後再 commit"
    exit 1
fi

# 檢查是否有 debug print
if git diff --cached --name-only | grep -E '\.py$' | xargs grep -n "print.*debug"; then
    echo "❌ 發現 debug print，請移除後再 commit"
    exit 1
fi
```

## 最佳實踐

1. **使用適當的 Logging 框架**
   - Python: 使用 `logging` 模組
   - JavaScript: 使用條件式 console 或 logging 庫

2. **區分環境**
   ```python
   import os
   if os.getenv('DEBUG') == 'true':
       print(f"Debug info: {data}")
   ```

3. **Code Review**
   - Pull Request 前檢查是否有 debug 語句
   - 審查時注意 console.log 和 print

4. **IDE 設定**
   - 設定 ESLint 規則禁止 console.log
   - 使用 pylint 或 flake8 檢查 print 語句

## 快速參考

```bash
# 搜尋所有 print
grep -rn "print(" backend/ --include="*.py" --exclude-dir=venv

# 搜尋所有 console
grep -rn "console\." frontend/src/ --include="*.js" --include="*.jsx"

# 統計數量
grep -r "print(" backend/ --include="*.py" --exclude-dir=venv | wc -l
grep -r "console\." frontend/src/ | wc -l
```

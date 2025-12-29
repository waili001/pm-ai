---
description: 程式碼修改工具使用最佳實踐
---

# 程式碼修改最佳實踐

使用 `replace_file_content` 和 `multi_replace_file_content` 工具的指南。

## 基本原則

1. **先查看再修改**：永遠先用 `view_file` 查看目標區域
2. **精確匹配**：TargetContent 必須完全匹配，包括所有空白和縮排
3. **失敗後重查**：如果替換失敗，重新查看檔案確認實際內容
4. **分解複雜修改**：多處修改使用 `multi_replace_file_content`

## 正確的工作流程

### 步驟 1: 查看目標區域

```
view_file:
  AbsolutePath: /path/to/file.py
  StartLine: 180
  EndLine: 195
```

### 步驟 2: 複製確切內容

從 view_file 輸出中**精確複製**要替換的內容，包括：
- 所有空格和 tab
- 所有縮排
- 所有換行
- 註解

### 步驟 3: 執行替換

```
replace_file_content:
  TargetFile: /path/to/file.py
  StartLine: 183
  EndLine: 191
  TargetContent: |
    # 從 view_file 精確複製的內容
    # 包含所有原始格式
  ReplacementContent: |
    # 新的內容
```

## 常見錯誤和解決方案

### ❌ 錯誤 1: 空白不匹配

**錯誤訊息**: `target content not found in file`

**原因**: TargetContent 的縮排或空白與實際檔案不符

**解決**:
1. 重新 view_file 查看確切內容
2. 確保複製時包含所有不可見字元
3. 檢查是否使用 spaces vs tabs

**範例**:
```python
# ❌ 錯誤 - 縮排不對
    results.append({
        "ticket_number": t.tcg_tickets,

# ✓ 正確 - 從 view_file 複製
            results.append({
                "ticket_number": t.tcg_tickets,
```

### ❌ 錯誤 2: 行號範圍錯誤

**錯誤訊息**: `target content not found in file`

**原因**: StartLine 和 EndLine 範圍內找不到 TargetContent

**解決**:
1. 確認 StartLine 和 EndLine 完全包含 TargetContent
2. 範圍可以大一點，只要包含目標即可
3. 如果不確定，用更大的範圍重新 view_file

### ❌ 錯誤 3: 內容已變更

**錯誤訊息**: `target content not found in file`

**原因**: 之前的修改已經改變了檔案內容

**解決**:
1. 重新 view_file 查看當前內容
2. 使用最新的內容作為 TargetContent

## 多處修改使用 multi_replace_file_content

當需要修改同一檔案的多個不連續區域時：

```
multi_replace_file_content:
  TargetFile: /path/to/file.jsx
  ReplacementChunks:
    - StartLine: 45
      EndLine: 46
      TargetContent: |
        // 第一處修改的目標內容
      ReplacementContent: |
        // 第一處的新內容
      AllowMultiple: false
    
    - StartLine: 131
      EndLine: 145
      TargetContent: |
        // 第二處修改的目標內容
      ReplacementContent: |
        // 第二處的新內容
      AllowMultiple: false
```

## 實際案例：移除功能

### 場景：移除 TP Kanban 的 Hide DEV Task 功能

**步驟 1**: 查看檔案結構
```
view_file_outline:
  AbsolutePath: /path/to/TPStatus.jsx
```

**步驟 2**: 查看相關區域
```
view_file:
  AbsolutePath: /path/to/TPStatus.jsx
  StartLine: 1
  EndLine: 50  # 看 imports 和 state
  
view_file:
  StartLine: 130
  EndLine: 150  # 看過濾邏輯
  
view_file:
  StartLine: 170
  EndLine: 210  # 看 UI 元素
```

**步驟 3**: 分三處修改
```
multi_replace_file_content:
  ReplacementChunks:
    - # 移除 state 定義
    - # 移除過濾邏輯
    - # 移除 UI 元素
```

## 檢查清單

修改前：
- [ ] 已用 view_file 查看目標區域
- [ ] 確認 StartLine 和 EndLine 範圍正確
- [ ] TargetContent 從 view_file 輸出精確複製
- [ ] 檢查縮排和空白字元

修改後：
- [ ] 檢查工具輸出的 diff
- [ ] 如果失敗，重新 view_file 確認內容
- [ ] 必要時運行測試驗證修改

## 快速參考

### 單一連續修改
用 `replace_file_content`

### 多處不連續修改  
用 `multi_replace_file_content`

### 整個檔案重寫
用 `write_to_file` 配合 `Overwrite: true`

### 只看不改
用 `view_file` 或 `view_file_outline`

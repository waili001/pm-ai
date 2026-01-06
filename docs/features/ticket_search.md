# View Ticket (Ticket Search) Feature

此功能允許使用者透過輸入 Ticket Number 查詢並檢視 Ticket 的詳細資訊。支援 TCG 與 TP 兩種類型的 Ticket。

## 功能規格

### 1. 搜尋功能 (Search)
*   **入口**: 
    1. 側邊欄 "Ticket Search" 選單。
    2. **頂部導航欄 (Top Navigation Bar)**: 位於右上角 User Avatar 左側的全域搜尋框。
*   **操作**: 在搜尋框輸入 Ticket Number (例如 `TCG-125906` 或 `TP-4707`) 並按下 Enter 或搜尋按鈕。
*   **結果**:
    *   **側邊欄入口**: 進入 Ticket Search 頁面顯示詳細資訊。
    *   **頂部導航欄 (Top Bar)**: 若搜尋成功，直接彈出 **Ticket Detail Modal** 顯示詳細資訊 (與 Project Backlog 一致)，不離開當前頁面。
    *   系統會記錄最近 10 筆成功的搜尋紀錄。
    *   搜尋歷史以 Chip 形式顯示於搜尋框下方，點擊即可快速搜尋。
    *   搜尋歷史與最後一次搜尋結果會儲存於 LocalStorage (本地端)。

### 2. TCG Ticket 詳細資訊
當搜尋結果為 TCG Ticket 時，顯示以下資訊：
*   **基本資訊**:
    *   Ticket Number Details
    *   Title (標題)
    *   Status (狀態 - 顯示為狀態標籤)
    *   Assignee (經辦人)
    *   Reporter (回報人)
    *   Issue Type (問題類型)
*   **TCG 專屬欄位**:
    *   **Related Project (TP)**: 若此 TCG 票券有對應的 TP，將顯示 TP 的詳細資訊 (Ticket Number, Name, Status, Due Day)。
    *   **Fix Version**: 修復版本。
*   **Description (描述)**:
    *   支援 Jira 格式的標記語法 (Bold, Headers, Code Blocks, Links 等)，並渲染為 HTML 顯示。
*   **Sub-tasks (子任務)**:
    *   系統會自動搜尋將此 Ticket 列為 `Parent Ticket` 的其他 Ticket (Sub-tasks)。
    *   以表格呈現子任務列表，包含：Ticket Number (可點擊跳轉), Title, Status, Assignee。

### 3. TP Ticket 可視性 (TP Visibility)
當搜尋結果為 TP Ticket (Project) 時，顯示以下資訊：
*   **基本資訊**:
    *   Ticket Number
    *   Title (專案標題)
    *   Status (專案狀態 - 顯示為狀態標籤)
    *   Assignee (Project Manager)
*   **TP 專屬欄位 (時程與資訊)**:
    *   **Released Date**: 發布日期。
    *   **Target Date**: 目標日期 (Due Day)。
    *   **Start Date**: 開始日期。
    *   **SIT Date**: SIT 測試日期。
*   **Description (描述)**:
    *   顯示專案描述內容 (支援 HTML 渲染)。

## 權限控管 (RBAC)
*   此功能受 `TICKET_SEARCH` 權限保護。
*   只有被授予此權限的角色 (如 SUPER_ADMIN) 才能在側邊欄看到入口並存取相關 API。

## API 參考
*   `GET /api/project/ticket/{ticket_number}`: 獲取 Ticket 詳細資訊 (包含 TCG 與 TP)。

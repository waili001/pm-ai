# Feature: Product Backlog

## Description
Product Backlog 是一個看板 (Kanban) 介面，用於管理 TCG Tickets。使用者可以在此檢視 Ticket 的詳細資訊、Jira 連結，並透過拖拉方式調整 Ticket 的優先順序。

## View Logic
*   **Kanban View**：
    *   顯示 TCG Tickets，依狀態分欄顯示。
    *   **固定欄位**：不管該狀態下是否有 Ticket，狀態欄位皆需保留顯示 (Open, To Do, In Progress, Resolved, Scheduled, Closed)。
    *   **Drag-and-Drop (拖拉排序)**：
        *   允許使用者在 **同一狀態欄位 (Column)** 內上下拖曳卡片以調整優先順序。
        *   排序結果會儲存至資料庫 (`TCG_Tickets` Table 的 `sort_order` 欄位)。
        *   重新整理頁面後，卡片必須依據 `sort_order` 保持順序。

    *   **Ticket Status & Team Logic (Dev Task Status)**:
        *   **Dev Task 狀態顯示**：
            *   需在 Kanban 卡片上顯示 Change Request (CR) Ticket 所屬 Dev Tasks 的整體狀態。
            *   **[NEW]** 需顯示 Dev Tasks 完成進度百分比 (例如: 50%, 100%)。
            *   **[CONDITION]** 僅當 CR Ticket 狀態為 `In Progress` 時顯示此百分比。
            *   CR Ticket 下可能包含多個 Dev Tickets。
        *   **Detail Dialog UI**:
            *   Ticket Status 與 Sub-task Status 需使用固定顏色標示 (Color Coded Chips)。
        *   **Inconsistent State Highlight (狀態不一致警示)**：
            *   若 Parent Ticket 在 "Finished" 狀態 (Resolved, Scheduled, Closed, Done)。
            *   且 仍有 Sub-tasks 未完成 (狀態非 In Review 或 Closed)。
            *   需 **Highlight** 該 Parent Ticket (例如: 紅色邊框或警示圖示)。
        *   **Team Assignment Rule (團隊歸屬規則)**：
            *   若 Ticket Component 為 `TAD TAC UI`，歸類為 **Frontend (FE) Team**。
            *   否則 (Else)，歸類為 **Backend (API) Team**。
        *   **Task Completion Logic (任務完成判定)**：
            *   若 Dev Task 狀態為 `In Review` 或 `Closed`，則視為 **開發已完成 (Done)**。


## Implementation Details
*   **Database Schema Updates**:
    *   `TCG_Tickets` table: 新增 `sort_order` (Integer, default=0) 欄位。

*   **API Requirements**:
    *   `GET /api/project/{ticket_number}/tcg_tickets`: 回傳列表需依據 `sort_order` 排序。
    *   `POST /api/project/tcg_sort`: 新增 API，接收 Ticket IDs 列表與 Status，更新資料庫中的排序。

*   **UI Requirements**:
    *   使用 `@hello-pangea/dnd` 實作拖拉功能。
    *   拖拉時需有視覺回饋 (Highlight)。
    *   採用 Optimistic UI Update 防止畫面閃爍。

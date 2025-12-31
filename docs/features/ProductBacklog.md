# Feature: Product Backlog

## Description
Product Backlog 是一個看板 (Kanban) 介面，用於管理 TCG Tickets。使用者可以在此檢視 Ticket 的詳細資訊、Jira 連結，並透過拖拉方式調整 Ticket 的優先順序。

## View Logic
*   **Kanban View**：
    *   顯示 TCG Tickets，依狀態分欄顯示。
    *   **固定欄位**：不管該狀態下是否有 Ticket，狀態欄位皆需保留顯示 (Open, To Do, In Progress, In Review, Resolved, Scheduled, Closed)。
    *   **Drag-and-Drop (拖拉排序)**：
        *   允許使用者在 **同一狀態欄位 (Column)** 內上下拖曳卡片以調整優先順序。
        *   排序結果會儲存至資料庫 (`TCG_Tickets` Table 的 `sort_order` 欄位)。
        *   重新整理頁面後，卡片必須依據 `sort_order` 保持順序。

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

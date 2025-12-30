# Feature: Project Planning Dashboard
> 新增一個 dashboard 顯示某一個部門的專案狀態

## Description
*   **新增一個 Menu**：`Project Planning` ，顯示在 Home 下面 且 Product Backlog 上方 的位置。 
*   **定義**：TP 就是指 Project
*   **頁面頂部過濾器**：
    *   選擇 Program (New) - **First Option**
    *   選擇部門 (`Department`)
    *   選擇 Project Type (`ALL` / `Tech` / `Integration` / `ICR` / `Project`)
    *   檢視模式切換：`Kanban` 或 `Gantt` (甘特圖)

### View Logic
*   **Kanban View (看板檢視)**：
    *   根據 TP 的狀態顯示每一個 Column。
    *   **排序順序**：`Open` > `In Review` > `Action Needed` > `In Progress` > `Resolved` > `Closed`
    *   **卡片內容**：
        *   基本資訊：標題、Ticket Link、PM、部門。
        *   **完成度 (Completed Percentage)**：顯示進度條與百分比 (Closed Tickets / Total Tickets)。
        *   **Due Day**：顯示到期日。
    *   **Drag-and-Drop (拖拉排序)**：
        *   允許使用者在 **同一狀態欄位 (Column)** 內上下拖曳卡片以調整優先順序。
        *   排序結果會儲存至資料庫 (`sort_order`)，重新整理後保持順序。

*   **Gantt View (甘特圖檢視)**：
    *   只顯示 `In Progress` 的 Projects。
    *   **時間軸**：起點依據 `Start Date` (若無則推算)，終點依據 `Due Day`。
    *   **排序**：依照 `Due Day` (由近且遠) 排序。
    *   **輔助線**：顯示 "Today" (紅色虛線) 標示今日日期。

## Implementation Details
*   **Department Data Source**: Fetch from `TCG_DEPT` table via `/api/project/departments`.
*   **Database Schema Updates**:
    *   `TP_Projects` table added `completed_percentage` (Int) and `sort_order` (Int).
*   **UI Requirements**:
    *   Dropdowns (Program, Department, Project Type) must have `min-width: 100px` and `max-width: 200px`.
    *   Kanban cards must match the styling of `Project Backlog` (Title, PM, Status, Jira Link).
    *   Ticket Numbers must be clickable links to Jira.
    *   **Persistence**: "Department" and "Project Type" selections must be saved in `localStorage` and restored on page load.
    *   **Department Filter**: Add "ALL" option (Default).
    *   **Data Logic**: For projects with `status="Closed"`, only display if `updated_at` is within the last 4 months.


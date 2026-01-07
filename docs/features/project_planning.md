# Feature: Project Planning Dashboard
> 新增一個 dashboard 顯示某一個部門的專案狀態

## Description
*   **新增一個 Menu**：`Project Planning` ，顯示在 Home 下面 且 Product Backlog 上方 的位置。 
*   **定義**：TP 就是指 Project
*   **頁面頂部過濾器**：
    *   選擇 Program (New) - **First Option** (Default: `ALL`, Empty input reverts to `ALL`)
    *   **排除狀態**：Jira Status 為 `Blocked` 的 TP 不會顯示。
    *   選擇部門 (`Department`) (Default: `ALL`, Empty input reverts to `ALL`)
    *   選擇參與部門 (`Participated Dept`) (Default: `ALL`)
    *   選擇 Project Type (`ALL` / `Tech` / `Integration` / `ICR` / `Project`) (Default: `ALL`)
    *   檢視模式切換：`Kanban` 或 `Gantt` (甘特圖)

### View Logic
*   **Kanban View (看板檢視)**：
    *   根據 TP 的狀態顯示每一個 Column。
    *   **排序順序**：`Open` > `In Review` > `Action Needed` > `In Progress` > `Resolved` > `Closed` (所有狀態欄位皆固定顯示，即使該狀態下無專案)
    *   **卡片內容**：
        *   基本資訊：標題、Ticket Link、PM、部門。
        *   **完成度 (Completed Percentage)**：顯示進度條與百分比 (Closed Tickets / Total Tickets)。
        *   **Due Day**：顯示到期日。
    *   **Drag-and-Drop (拖拉排序)**：
        *   允許使用者在 **同一狀態欄位 (Column)** 內上下拖曳卡片以調整優先順序。
        *   排序結果會儲存至資料庫 (`sort_order`)，重新整理後保持順序。
    *   **互動 (Interaction)**：
        *   點擊卡片將跳轉至 `Product Backlog` 頁面，並自動選取該專案，方便檢視相關 Tickets。

*   **Gantt View (甘特圖檢視)**：
    *   只顯示 `In Progress` 的 Projects。
    *   **時間軸**：起點依據 `Start Date` (若無則推算)，終點依據 `Due Day`。
    *   **排序**：依照 `Due Day` (由近且遠) 排序。
    *   **進度顯示**：
        *   Bar 內部顯示完成度 (Partial Fill)。
        *   Tooltip 顯示具體百分比 (e.g., Progress: 50%)。
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
    *   **Participated Dept Logic**: check if `participated_dept` includes the selected value AND `department` is NOT the selected value. This filters for projects where the department assisted but did not own.


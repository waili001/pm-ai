# Feature: Project Planning Dashboard
> 新增一個 dashboard 顯示某一個部門的專案狀態

## Description
*   **新增一個 Menu**：`Project Planning` ，顯示在 Home 下面 且 Product Backlog 上方 的位置。 
*   **定義**：TP 就是指 Project
*   **頁面頂部過濾器**：
    *   選擇部門 (`Department`)
    *   選擇 Project Type (`ALL` / `Tech` / `Integration` / `ICR` / `Project`)
    *   檢視模式切換：`Kanban` 或 `Gantt` (甘特圖)

### View Logic
*   **Kanban View (看板檢視)**：
    *   根據 TP 的狀態顯示每一個 Column。
    *   **排序順序**：`Open` > `In Review` > `Action Needed` > `In Progress` > `Resolved` > `Closed`

*   **Gantt View (甘特圖檢視)**：
    *   只顯示 `In Progress` 的 Projects。

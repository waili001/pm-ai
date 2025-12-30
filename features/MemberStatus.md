# Feature: Member Status Dashboard
> 新增一個 dashboard 顯示某一個部門底下的組員工作狀態

## Description
*   **頁面最上面有一個 Row**：可以選擇要檢視那一個部門 (from Department)
*   **需記住前一次搜尋的條件 (LocalStorage)**：下次進入頁面自動還原。
*   **頁面寬度需佔滿 (Full Width)**
*   **根據所選擇的部門來顯示組員列表**：每個欄位皆需支援排序
*   **組員列表的欄位**：
    *   部門名稱
    *   組員名稱
    *   職位 (Position)
    *   In-Progress TP
    *   In Progress 的單子

### Field Logic Details
*   **[In-Progress TP] (原 Current Working TP) 的判斷邏輯**：
    1.  查詢 `lark tcg table` 中 `assignee` 為這個組員且狀態為 `in-progress` 的單子。
    2.  查詢 `lark tcg table` 中 `resolved_by` 為這個組員且 `updated_at` 大於昨天 0 點 0 分的單子。
    3.  這個單子的所屬的 TP，或是這個單子的 `parent_tickets` 的單子所屬的 TP。
    4.  **顯示方式**：若有多筆，請換行顯示。格式為 `[TP Department] TP-Ticket Number TP Name`，並設為 **Hyperlink**。
    5.  **點擊行為**：點擊連結後，直接開啟新視窗跳轉至該 Ticket 的 Jira 頁面。

*   **[In-Progress Tickets]**：
    1.  若有多筆，請換行顯示。顯示 `Ticket Number`。
    2.  完整資訊 (Number + Name) 於 **Hover Tooltip** 顯示。
    3.  **點擊行為**：點擊 Ticket Number 後，彈出視窗 (Dialog) 顯示詳細內容：
        *   Ticket Number
        *   Content (Title)
        *   Status
        *   Assignee
        *   Description (需解析 Jira Format 為 HTML)

## Precautions (注意事項)
> [!IMPORTANT]
> 前後端資料結構需嚴格同步。當後端回傳結構變更 (如 String -> Object) 時，前端渲染邏輯 (如 `renderCell`) 必須同步更新，否則會導致 React 渲染錯誤 (`Objects are not valid as a React child`)。

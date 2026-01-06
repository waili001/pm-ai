# Feature: Ticket Anomaly Detection
> 偵測並記錄狀態異常的 Ticket，協助 PM/QA 修正 Jira 狀態。

## Description
*   **功能位置**：獨立頁面 `Ticket Anomaly`。
*   **觸發時機**：每次 `Lark Sync` 完成後自動執行偵測邏輯。
*   **範圍**：僅針對 `TP Status` 為 `In Progress` 的專案進行檢查。

## Anomaly Rules
### Rule 1: Parent Open but Child Active
*   **Target (Parent)**:
    *   `issue_type`: "Change Request" or "Improvement"
    *   `jira_status`: "Open"
*   **Condition (Child)**:
    *   擁有至少一個子單 (Dev Task)。
    *   **任一**子單狀態為：`In Progress`, `In Review`, `Resolved`, `Done`, `Closed`, `Development`, `Testing`, `Review`。
*   **Anomaly Reason**: "Parent is Open but has active children."

### Rule 2: Parent In Progress but Child InActive
*   **Target (Parent)**:
    *   `jira_status`: "In Progress"
*   **Condition (Child)**:
    *   擁有至少一個子單 (Dev Task)。
    *   **所有**子單狀態皆為：`Closed`, `Resolved`, `Done`。 (即沒有 `Open`, `To Do`, `In Progress`, `Development`, `Testing`, `In Review`, `Review`)
*   **Anomaly Reason**: "Parent is In Progress but all children are InActive (Closed/Done)."

## UI Requirements
*   **Unique Page**: `/ticket-anomaly`
*   **Table Columns**:
    *   `Assignee` (Parent Assignee)
    *   `TP Number`
    *   `TP Title`
    *   `Ticket Number` (Parent, Hyperlink to Jira)
    *   `Ticket Title`
    *   `Parent Status` (Expected: Open)
    *   `Anomaly Reason`

## Data Persistence
*   **Table**: `ticket_anomalies`
*   **Update Strategy**:
    *   Sync 結束後 -> 找出所有 In Progress TPs -> 刪除這些 TPs 下舊的 Anomaly 紀錄 -> 插入新偵測到的 Anomalies。

## API
*   `GET /api/project/anomalies`: 取得異常清單。

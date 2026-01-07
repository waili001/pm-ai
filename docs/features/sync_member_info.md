# Feature: Sync Lark Base - Member Information
> 同步 Lark Base 中的 Member Information 到本地資料庫

## Description
*   **同步頻率**：每 15 分鐘同步一次
*   **資料來源**：Lark Base - Member Information Table
*   **資料庫 Table Name**：`MEMBER_INFO`
*   **Environment Variables**：
    *   `MEMBER_APP_TOKEN`
    *   `MEMBER_TABLE_ID`
*   **Lark Base Column Mapping**：
    *   `No`
    *   `Member`
    *   `Department`
    *   `Position`
    *   `Team`
    *   `Remark`
*   **實作範圍**：只需要同步資料到資料庫中，**無需**新增 API 或前端頁面。
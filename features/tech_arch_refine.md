# Feature: Backend Architecture Refinement
> 後端架構優化：檔案組織重構

## Description
*   **Folder Structure**：將相同性質的檔案放入同一個 Folder。
*   **Debug Utilities**：將 Debug 相關工具集中管理。
*   **Lark Integration Layer**：
    *   建立獨立檔案處理與 Lark 的介接邏輯，提供 API 給其他服務使用。
    *   該層級只處理介接邏輯，不處理業務邏輯。
*   **Data Transformation Logic**：
    *   每一個 Lark Base Table 轉 Database Table 的邏輯應獨立為一個檔案。
    *   所有轉換邏輯檔案應集中放置於同一個 Folder。
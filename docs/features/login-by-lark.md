# Lark SSO & Hybrid Authentication Requirements

## 1. 概述 (Overview)
本文件定義系統的驗證機制，支援「Lark SSO」與「本地帳號密碼」並存的混合登入模式。

## 2. 目標 (Goals)
- **混合驗證**: 同時支援 Lark OAuth 2.0 單一登入與傳統帳號密碼登入。
- **Lark 整合**: 提供更流暢的企業登入體驗，並自動建立使用者 (Auto-Provisioning)。
- **權限管控**: 限制 Lark 使用者的密碼操作權限，確保資安一致性。
- **移除訪客**: 廢除「訪客登入」功能，所有存取皆需驗證。

## 3. 系統流程 (System Flow)

### 3.1 登入介面 (Frontend)
- **登入頁面**:
    1.  **Lark 優先 (Default)**: 預設僅顯示 **"Sign in with Lark"** 按鈕，鼓勵企業員工使用 SSO。

### 3.2 驗證流程 (Backend)
#### A. Lark SSO 登入
1.  **發起**: 前端導向 `/api/auth/lark/login` -> 重定向至 Lark 授權頁。
2.  **Callback** (`/api/auth/lark/callback`):
    -   **取得 Tenant Access Token** (Internal App).
    -   **取得 User Access Token** (使用 Tenant Token 驗證).
    -   取得 User Info。
    -   **決定 Username (優先順序)**:
        1.  `name` (Display Name, e.g., "李威")
        2.  `en_name` (e.g., "Wai Li")
        3.  `email`
        4.  `user_id`
        5.  `open_id`
    -   **自動建立/更新使用者**:
        -   若使用者不存在: 建立新 AdminUser，設定 `authProvider='LARK'`。
        -   若使用者已存在 (Username 匹配): 更新 (或維持) `authProvider='LARK'`。
        -   **Super Admin 規則 (Auto-Provision)**:
            -   若 Username (忽略大小寫) 為 `waili` 或以 `waili@` 開頭，自動設定 `role='SUPER_ADMIN'`。
            -   **關鍵更新**: 同時查找 `Role` 表中 `SUPER_ADMIN` 的 ID 並寫入 `roleId` 欄位，確保與 RBAC 系統同步。
            -   其他使用者預設 `role='USER'` 並連結對應 `roleId`。
    -   簽發 JWT (Session)。

### 3.3 登入強制 (Login Enforcement)
-   **路由保護**:
    -   若使用者未登入存取上述路徑，系統將自動重導向至 `/login`。

### 3.4 密碼變更限制
-   **API**: `POST /api/user/change-password`
-   **邏輯**:
    -   檢查當前使用者的 `authProvider`。
    -   若為 `LARK` -> **拒絕變更** (回傳錯誤: "Lark users cannot change password")。
    -   若為 `LOCAL` -> 允許變更。

## 4. API 規格 (API Specifications)

### 4.1 認證 API
-   `POST /api/login`: 本地登入 (恢復此端點)。
-   `GET /api/auth/lark/login`: Lark SSO 發起。
-   `GET /api/auth/lark/callback`: Lark SSO 回調。

## 5. 環境變數 (Configuration)
-   `LARK_APP_ID`
-   `LARK_APP_SECRET`


---
trigger: always_on
---

# 前端 API 開發規範 (Frontend Coding Rules)

## 1. API 請求規範
### 強制使用相對路徑 (Use Relative Paths)
*   前端代碼中的 API 請求 **必須** 使用相對路徑 (例如 `/api/auth/login`)。
*   **禁止** 使用絕對路徑 (例如 `http://localhost:8001/api/...`)。
*   **原因**: 相對路徑能確保代碼在本地開發 (Dev) 與雲端部署 (Prod) 環境下皆能自動適應，無需修改代碼。

## 2. 開發環境配置
### 維護 Vite Proxy
*   必須在 `vite.config.ts` 中配置 `server.proxy`，將 `/api` 請求轉發至後端服務端口 (e.g. 8001)。
*   **原因**: 解決開發環境下的跨域 (CORS) 與路徑對應問題，模擬生產環境的行為。

## 3. 檔案編輯與結構 (Prevention Measures)
### Import 置頂原則
*   修改 `tsx/ts` 檔案時，**必須** 檢查並確保 `import` 語句位於檔案的最開頭。
*   **禁止** 將 `import` 插入在 Component 或 Function 內部。

### 檔案完整性
*   大幅修改 Component 時，務必確保結尾的括號 `}` 沒有被截斷。

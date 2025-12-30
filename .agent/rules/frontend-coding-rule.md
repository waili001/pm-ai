---
trigger: always_on
---

# 前端 API 開發規範 (Frontend API Rules)
強制使用相對路徑 (Use Relative Paths)
前端代碼中的 API 請求 必須 使用相對路徑 (例如 /api/project/active)。
禁止 使用絕對路徑 (例如 http://localhost:8000/api/... 或 http://127.0.0.1:8000/api/...)。
原因：相對路徑能確保代碼在本地開發 (Dev) 與雲端部署 (Prod) 環境下皆能運作，無需修改代碼。

# 維護開發環境代理 (Maintain Vite Proxy)
必須在  vite.config.js
 中配置 server.proxy，將 /api 請求轉發至後端服務端口 (通常是 :8000)。
原因：解決開發環境下的跨域 (CORS) 與路徑對應問題，模擬生產環境的 Nginx 行為。
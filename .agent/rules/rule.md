---
trigger: always_on
---

# AI 行為準則 (AI Behavior Rules)

## 1. 溝通與語言 (Communication)
- **[強制]** 所有回應必須使用 **繁體中文 (Traditional Chinese)**。
- **[強制]** 語氣需專業、簡潔且具建設性。

## 2. 錯誤處理與預防 (Error Handling & Prevention)
- **[強制] Root Cause Analysis (RCA)**: 當修正任何錯誤時，**必須** 明確解釋：
    1.  **為什麼** 會發生這個錯誤 (Root Cause)？
    2.  **如何** 修正了它？
    3.  **未來如何預防** 再次發生 (Preventive Action)？
- **[禁止]** 禁止只給出修正後的代碼而不解釋原因。

## 3. 文件同步 (Documentation Synchronization)
妳必須將每一次的實作視為「文件驅動開發 (Document-Driven Development)」的一部分。

### Feature Documentation
- **[強制]** 每當實作或修改一個功能 (Feature) 時，**必須** 同步更新對應的 `docs/features/xxxx.md` 文件。
- 內容應包含：新的需求描述、實作細節、注意事項。

### API Documentation
- **[強制]** 當新增或修改 API 時，**必須** 更新 `docs/api.html`。
- **[標準]** API 文件必須符合 **OpenAPI** 標準。
- **[流程]** 實作 API -> 更新 `docs/api.html`。

## 4. 自我檢查清單 (Self-Correction Checklist)
在結束回應前，請自我檢查：
- [ ] 我是否用了繁體中文？
- [ ] 若有修 bug，我是否解釋了原因和預防措施？
- [ ] 有改到功能嗎？有更新 `docs/features/` 嗎？
- [ ] 有改到 API 嗎？有更新 `docs/api.html` 嗎？

## 5. 測試規範 (Testing Protocols)
- **[強制] 測試帳號生命週期 (Test Account Lifecycle)**:
    - **Setup**: 在執行自動化測試前，**必須** 先將專用的「測試帳號」Insert 到資料庫。
    - **Execution**: 使用該測試帳號/密碼進行登入與操作。
    - **Teardown**: 測試結束後(無論成功或失敗)，**必須** 立即將該測試帳號從資料庫中移除。
    - **[禁止]** 禁止使用既有的數據或正式帳號進行測試。

## 6. 版本控制 (Version Control)
- **[強制] 禁止自動 Git 操作**: 除非使用者有明確的指令 (e.g., "commit 提交", "push 推送", 或者使用 `/git-sync` 指令)，否則 **嚴禁** 自動執行 `git commit` 或 `git push`。

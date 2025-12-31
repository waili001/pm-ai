---
trigger: manual
---

# Antigravity User Rules (Strict Mode)

1. **Verify Before Deploying (驗證優先)**:
   - 修改第三方 API 相關邏輯時，**禁止**直接依賴主程式重啟驗證。
   - **必須**先撰寫獨立的 Python 腳本 (如 `verify_fix.py`) 模擬 API 呼叫，確認 Response 成功後，才准應用到主程式。

2. **Trust the Error Log (日誌為王)**:
   - 當 Log 顯示的錯誤訊息與你的修復方向矛盾時 (例如你改了A，Log 卻說 B 格式錯誤)，**立即停止**。
   - 不要假設檔案已更新。優先檢查執行環境 (Run Context) 是否有快取或舊進程殘留。

3. **Isolate Variables (變因隔離)**:
   - 遇到 "Api Error" 重複發生兩次以上，請回退到「最小可行版本」(如 Full Sync)，不要在錯誤的基礎上疊加修復。

4. 「在修改複雜結構 (如陣列或物件) 時，請務必先 view_file 確認行號與上下文，並檢查括號 (Braces) 是否成對匹配，避免直接整塊覆寫。」

5. 前後端資料結構需嚴格同步。當後端回傳結構變更 (如 String -> Object) 時，前端渲染邏輯 (如 renderCell) 必須同步更新，否則會導致 React 渲染錯誤 (Objects are not valid as a React child)。

6. 「使用 replace_file_content 時，請務必確認 TargetContent 的範圍精確，且 ReplacementContent 不應包含原本已經存在的周圍程式碼 (除非是為了修改它們)，# Antigravity User Rules (Strict Mode)

7.  Atomic Edits (原子化修改)：
新增功能時，只准「插入」新程式碼，嚴禁刪除或修改原本的程式碼區塊 (除非它直接衝突)。
若覺得舊程式碼有問題，必須另外開一個 Task 專門處理重構，不能夾帶。

8. Minimal Target Content (最小化錨點)：
使用 replace_file_content 時，TargetContent 只能包含「定位點」的前後 1-2 行，不能包含一整大塊既有邏輯。
正確做法：只 Target if current_tps_map: 這兩行，然後在後面 append 新邏輯。
錯誤做法：Target 了 20 行包含迴圈的代碼，然後整塊重寫。

9. 相同類型/職責的檔案要放在同一個目錄:
debug 目錄 放 test/debug 的檔案
verify 目錄放 test/verify 的檔案
service 目錄 放 service 的檔案


### [2025-12-31] Prevention Rules
1. **Log Before Fix (先記錄再修復)**:
   - When debugging API failures, you MUST log the **Request Payload** and **Raw Response Body** before attempting any code fix.
   - Do not guess parameter names; verify them against the raw response.

2. **Null Safety in Data Sync (數據同步的空值安全)**:
   - When syncing data from external APIs (Lark/Bitfinex) to DB, explicitly handle `None`/`null` values.
   - Do not assume a field always exists. Use `.get('field', default)` or explicitly check for existence.

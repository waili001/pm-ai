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

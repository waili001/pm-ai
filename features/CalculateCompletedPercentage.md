# Calculate Completed Percentage

## Goal
每一小時就計算 tp 的完成度，並更新到 tp_projects的table

## Requirements
- 每一小時 計算一次並更新 。
- 系統啟動時 也會觸發此 job 並更新 完成度
- add column on table : tp_projects.  column name : completed_percentage
- 只計算與更新 tp_project 的狀態為 `In Progress` 的 tp
- 計算方式為 統計 tcg_tickets 中 status 為 `Closed` 的單子數量 / 所有單子數量

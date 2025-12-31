---
description: Analyze failures in the conversation and update coding rules to prevent recurrence.
---

1.  **Analyze Conversation History**:
    -   Scan the recent conversation for patterns of "Code Modification" -> "Error/Failure" -> "Fix".
    -   Identify the technical root cause for each failure (e.g., "Import placed inside function", "Env file corrupted", "Path mismatch").

2.  **Formulate Prevention Rules**:
    -   Draft actionable rules to prevent these specific root causes.
    -   Categorize each rule into **Frontend** or **Backend**.

3.  **Update Frontend Rules**:
    -   Target File: `.agent/rules/frontend-coding-rule.md` (Create if missing).
    -   Action: Append the new frontend prevention rules. Use a clear header formatting like `### [Date] Prevention Rules`.

4.  **Update Backend Rules**:
    -   Target File: `.agent/rules/python-coding-rule.md` (Create if missing).
    -   Action: Append the new backend prevention rules. Use a clear header formatting like `### [Date] Prevention Rules`.

5.  **Notify User**:
    -   Summarize the errors found and the specific rules added to each file.
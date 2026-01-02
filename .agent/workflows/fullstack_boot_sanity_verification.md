---
description: Verify the full application stack (Backend API + Frontend Availability)
---

**Role:** DevOps Reliability Engineer (DRE) Agent
**Objective:** Validate system integrity, orchestrate the startup of the Full Stack application, and autonomously resolve runtime errors to ensure the system is operational.

**Context:**
You are operating in a TypeScript/Node.js environment with a Frontend (Vite/React) and Backend (Python/Node/Prisma/SQLite). The user requires the system to be "Ready for Execution."

**Workflow Logic:**

### Phase 1: Static Pre-flight Check (Fail Fast)
1.  **Frontend Type Check:**
    * Action: Execute `cd frontend && npx tsc --noEmit`.
    * *Logic:* If exit code != 0, capture the output.
    * *Auto-Fix:* If error implies missing types or modules, run `npm install` in frontend. If syntax error, HALT and report specific file/line.

2.  **Database Integrity Check:**
    * Action: Execute `sqlite3 backend/sql_app.db "SELECT count(*) FROM member_info;"`.
    * *Logic:* If output is empty or error ("no such table"), trigger `npx prisma migrate dev` to rebuild schema.

### Phase 2: Service Orchestration & Launch
3.  **Start Services:**
    * Action A (Backend): Start the backend server in background mode.
    * Action B (Frontend): Start the frontend dev server in background mode.
    * 

[Image of client-server architecture diagram]


### Phase 3: Runtime Verification & Auto-Healing
4.  **Wait & Probe:** Wait 5 seconds for services to initialize.
5.  **Health Check (Backend):** 
    * *Condition:* If Verify Script fails:
        * **Diagnosis:** Read stderr.
        * **Strategy A (Port Conflict):** If error contains "EADDRINUSE": Find process on port (3000/8080) -> Kill process -> Retry Step 3.
        * **Strategy B (DB Lock):** If error contains "SQLITE_BUSY": Restart Backend service -> Retry Step 3.
        * **Strategy C (Runtime Crash):** If stack trace is present: Output specific error log -> HALT.

6.  **Availability Check (Frontend):**
    * Action: `curl -I http://localhost:5173`.
    * *Condition:* If status != 200 OK:
        * **Strategy:** Check if Vite process is running. If not, restart Frontend.

### Phase 4: Final Reporting
7.  **Generate Report:**
    * Output a summary table showing: Service Status (UP/DOWN), Port Numbers, Database Record Count, and any Auto-Fix actions taken.

**Constraints & Guidelines:**
* **Safety:** Do not delete production data files without explicit user confirmation.
* **Logging:** Show a distinct "🛠️ REPAIRING..." log when an auto-fix is triggered.
* **Timeout:** If services fail to stabilize after 2 repair attempts, abort with a critical error report.

**Output Format:**
Markdown Report with status indicators (✅/❌/⚠️).
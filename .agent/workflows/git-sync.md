---
description: Automated Git Commit and Push
---

---
description: Your Workflow Description
---
> [!CAUTION]
> **STRICT RULE**: This workflow is **FORBIDDEN** from using the `rm` command or any file deletion operations.
> If a step requires cleanup, you must STOP and ask the user for manual intervention.


// turbo-all

1. Check current git status
   // turbo
   > run_command git status

2. Stage all changes
   // turbo
   > run_command git add .

3. Commit changes (Default message "update", modify if needed)
   > run_command git commit -m "update"

4. Push to remote repository
   // turbo
   > run_command git push
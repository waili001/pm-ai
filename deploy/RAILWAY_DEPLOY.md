# Railway Deployment Guide

This project is configured to be deployed as a **Single Service** (Frontend + Backend in one container) on Railway using Docker.

## Prerequisites
- A Railway Account (https://railway.app/)
- GitHub Repository connected to Railway

## Configuration Files
The following files control the deployment:
1.  **Dockerfile**: Multi-stage build script.
    -   Stage 1: Node.js image to build the React Frontend.
    -   Stage 2: Python image to run the FastAPI Backend and serve the built frontend files.
2.  **backend/main.py**: Updated to serve static files (the built frontend) from the `/static` directory.
3.  **backend/requirements.txt**: Python dependencies.

## Environment Variables
Set these variables in your Railway Project Settings:

| Variable | Description |
| :--- | :--- |
| `TP_APP_TOKEN` | Lark Base App Token |
| `TP_TABLE_ID` | Lark Table ID for Projects |
| `TCG_APP_TOKEN` | Lark Base App Token for Tickets |
| `TCG_TABLE_ID` | Lark Table ID for Tickets |
| `PORT` | Railway automatically sets this (usually 8000 for FastAPI) |
| `MEMBER_APP_TOKEN` | Lark Base App Token for Members |
| `MEMBER_TABLE_ID` | Lark Table ID for Members |
| `PROGRAM_APP_TOKEN` | Lark Base App Token for Programs |
| `PROGRAM_TABLE_ID` | Lark Table ID for Programs |
| `JIRA_URL` | JIRA URL |
| `JIRA_API_TOKEN` | JIRA API Token |
| `DB_DIR` | Directory for SQLite DB. Set to `/app/data` when using Volume. |

## Deployment Steps

1.  **Push Code**: Commit and push the `Dockerfile` and updated `backend/main.py`.
2.  **New Service in Railway**:
    -   Click "New Project" -> "Deploy from GitHub repo".
    -   Select this repository.
3.  **Add Volume (Crucial for Persistence)**:
    -   Go to your Service -> "Volumes" tab.
    -   Click "Add Volume".
    -   Mount Path: `/app/data`
4.  **Configure Variables**:
    -   Go to the "Variables" tab.
    -   Add `DB_DIR` with value `/app/data`.
    -   Add all other required environment variables listed above.
5.  **Automatic Build**: Railway will detect the `Dockerfile` and start building.
5.  **Verify**:
    -   Railway will provide a public domain (e.g., `yourapp.up.railway.app`).
    -   Visit the URL. You should see the Frontend.
    -   Visit `/api/docs`. You should see the Backend API Docs.

## Local Development vs. Production
-   **Local**: run `./start.sh` (Frontend runs on 5173, Backend on 8000).
-   **Production**: Docker runs one process (Backend on $PORT), serving Frontend statically.

## Troubleshooting
-   **Build Fails**: Check "Build Logs" in Railway. ensure `npm run build` succeeds locally.
-   **Frontend 404**: Ensure `vite.config.js` builds to the correct output directory (default `dist`) and `Dockerfile` copies it to `/app/static`.

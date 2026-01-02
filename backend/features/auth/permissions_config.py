# Permission Configuration
# This file defines the static mapping of Pages to API Permissions

PERMISSIONS_CONFIG = {
    "ROLES": {
        "name": "Roles",
        "apis": [
            ("GET", "/api/system/roles"),
            ("POST", "/api/system/roles"),
            ("PUT", "/api/system/roles/{id}"),
            ("DELETE", "/api/system/roles/{id}"),
        ]
    },
    "USERS": {
        "name": "Users",
        "apis": [
            ("GET", "/api/system/users"),
            ("POST", "/api/system/users/role"),
        ]
    },
    "JOB_CONFIG": {
        "name": "Job Configuration",
        "apis": [
            ("POST", "/api/jobs/sync"),
            ("POST", "/api/jobs/verify-jira"),
            ("POST", "/api/sync/lark/dept"),
        ]
    },
    "SQLITE_ADMIN": {
        "name": "SQLite Admin",
        "apis": [
            ("GET", "/api/db/tables"),
            ("POST", "/api/db/query"),
        ]
    },
    # Default accessible pages (if any specific permissions needed)
    "PROJECT_PLANNING": {
        "name": "Project Planning",
        "apis": [
             ("GET", "/api/project/planning"), # Example
        ]
    },
    "DASHBOARD": {
        "name": "Dashboard",
        "apis": [
            ("GET", "/api/data"),
            ("GET", "/api/project/active"), # Used in dashboard too? Checks ProjectBacklog.jsx uses it.
            # Confirming /api/project/active is used in Project Backlog. 
            # Dashboard also uses /api/data.
            # If Project Backlog needs it, add it there too? Rationale: A user might have BACKLOG but not DASHBOARD.
        ]
    },
    "MEMBER_STATUS": {
        "name": "Member Status",
        "apis": [
            ("GET", "/api/members/departments"),
            ("GET", "/api/members/status"),
            ("GET", "/api/project/ticket/{ticket_number}"), # For dialog details
        ]
    },
    "PROJECT_BACKLOG": {
        "name": "Project Backlog",
        "apis": [
            ("GET", "/api/project/active"),
            ("GET", "/api/project/{ticket_number}/tcg_tickets"),
            ("POST", "/api/project/reorder_tcg"),
        ]
    }
}

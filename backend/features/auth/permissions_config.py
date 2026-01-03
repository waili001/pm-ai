PERMISSIONS_CONFIG = {
    "HOME": {
        "name": "Home Page",
        "apis": []
    },
    "MEMBER_STATUS": {
        "name": "Member Status & Dashboard",
        "apis": [
            ("GET", "/api/member/status"),
            ("GET", "/api/member/stats"),
            ("GET", "/api/member/holidays"),
            ("POST", "/api/member/status"),
            ("DELETE", "/api/member/status")
        ]
    },
    "PROJECT_BACKLOG": {
        "name": "Project Backlog & Planning",
        "apis": [
             ("GET", "/api/project/active"),
             ("GET", "/api/project/planning"),
             ("GET", "/api/project/programs"),
             ("GET", "/api/project/departments"),
             ("POST", "/api/project/reorder"),
             ("GET", "/api/project/{tp_number}/tcg_tickets"),
             ("POST", "/api/project/reorder_tcg")
        ]
    },
    "SQLITE_ADMIN": {
        "name": "SQLite Database Admin",
        "apis": [
            ("GET", "/api/db/tables"),
            ("POST", "/api/db/query")
        ]
    },
    "ROLE_MANAGEMENT": {
         "name": "Role Management",
         "apis": [
             ("GET", "/api/system/roles"),
             ("POST", "/api/system/roles"),
             ("PUT", "/api/system/roles/{role_id}"),
             ("DELETE", "/api/system/roles/{role_id}"),
             ("GET", "/api/system/roles/permissions"),
             ("GET", "/api/system/users"),
             ("PUT", "/api/system/users/{user_id}/role")
         ]
    },
    "TICKET_SEARCH": {
        "name": "Ticket Search",
        "apis": [
            ("GET", "/api/project/ticket/{ticket_number}")
        ]
    }
}

# Login Reminder Modal (Login Anomaly Reminder)

## Overview
A feature to remind specific roles (Managers, PMs) about pending tasks (Ticket Anomalies) immediately after they log in.

## Requirements

### Trigger Condition
- **Event**: User Login.
- **Roles**: User must hold one of the following positions:
    - Manager
    - Assistant Manager
    - PM
    - (Positions are determined by the `member_info` table synced from Lark)
- **Data Condition**: There are pending Ticket Anomalies associated with the user's **Department**.

### UI Behavior
- Display a Modal (Dialog) overlay on top of the dashboard.
- **Title**: "Pending Anomalies Reminder" (or similar).
- **Content**: A list/table of anomalies requiring attention.
    - Ticket Number
    - Title
    - Anomaly Reason
    - Detected At
- **Actions**:
    - "Close" or "Acknowledge" button.
    - Clicking a ticket might link to the detail page (optional but good UX).

### Logic Details
1.  **User Identification**:
    - System uses the logged-in user's name (`full_name` or `username`) to look up their record in the `member_info` table.
    - Retrieves `department` and `position` from `member_info`.
2.  **Anomaly Query**:
    - Query `ticket_anomalies` table.
    - Filter: `department` equals User's Department.
3.  **Frequency**:
    - Shown once per session (using Session Storage to track) OR every time the main layout is mounted if not dismissed. *Decision: Once per session.*

## API Changes
### `GET /api/project/anomalies/my-pending`
- **Auth**: Required (Headers: Authorization Bearer Token)
- **Response**:
    ```json
    {
      "show_modal": true,
      "anomalies": [
        {
          "ticket_number": "TCG-123",
          "title": "Bug Fix",
          "anomaly_reason": "Status Mismatch",
          "detected_at": 1704520000000
        }
      ]
    }
    ```
- **Scenario - No Access/No Anomalies**:
    ```json
    {
      "show_modal": false,
      "anomalies": []
    }
    ```

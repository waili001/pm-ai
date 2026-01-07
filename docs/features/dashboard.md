# Dashboard Feature Documentation

## 1. Overview
The Dashboard provides a high-level view of project performance and project completion statistics. It serves as the landing page for the application.

## 2. Key Features

### 2.1 Performance Overview Chart
- **Visual**: A column chart displaying "Closed TP Count" grouped by quarter (e.g., "2024 Q4", "2025 Q1").
- **Interaction**: Clicking on a specific quarter bar opens a detailed drill-down modal.
- **Data Source**: Fetches data from `GET /api/project/dashboard-stats`.

### 2.2 ICR Count Overview
- **Visual**: A column chart displaying distinct "ICR Count" (sum of `icr_count` field) for projects of type 'ICR', grouped by quarter.
- **Data Source**: Fetches `icr_data` from `GET /api/project/dashboard-stats`.

### 2.3 Department Filtering
- Allows users to filter dashbaord statistics by department.
- Adjusting the filter reloads the chart data.
- **Default**: "ALL" departments.

### 2.3 Drill-down Details (Quarterly Closed TPs)
- **Trigger**: Click on a quarter bar in the "Performance Overview" chart.
- **Content**:
    - **Summary Stats**: Breakdown of closed TPs by type (Tech, ICR, Project, Other).
    - **Detailed Table**: Lists all closed TPs for the selected quarter.
        - Columns: Ticket No (link to Jira), Title, Department, Type, Manager, Released Date.
- **Data Source**: Fetches detailed list from `GET /api/project/closed-tps`.

### 2.4 Table Features (Inside Drill-down)
- **Sorting**:
    - Users can sort the table by clicking on column headers.
    - Supports ascending and descending order.
    - Default sort: Ticket Number (asc).
    - Special sorting logic for Date columns and String columns.

### 2.5 CSV Export
- **Functionality**: Export the currently displayed list of closed TPs to a CSV file.
- **Format**: Comma-Separated Values, UTF-8 encoded with BOM (for Excel compatibility).
- **Filename**: `Closed_TPs_[Quarter].csv`.
- **Columns Exported**: Ticket No, Title, Department, Type, Manager, Released Date.

## 3. Implementation Details

### Frontend
- **File**: `frontend/src/pages/Home.jsx`
- **Libraries**:
    - `highcharts`, `highcharts-react-official` for charting.
    - `@mui/material` for UI components (Grid, Box, Table, Dialog, etc.).
- **State Management**:
    - Uses local `useState` for handling UI state (loading, modal open, sort order) and data (stats, quarterTPs).

### Backend API
- **Stats Endpoint**: `GET /api/project/dashboard-stats`
    - Returns categories (quarters) and data series (counts) for the chart.
- **Details Endpoint**: `GET /api/project/closed-tps`
    - Accepts `quarter` and `department` query parameters.
    - Returns a list of project objects containing details like `ticket_number`, `title`, `project_type`, etc.

## 4. Future Improvements
- Add more visualization types (e.g., Line chart for trends).
- Implement server-side pagination for the drill-down table if data volume grows significantly.

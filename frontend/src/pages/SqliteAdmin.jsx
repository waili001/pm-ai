import { useState } from 'react';
import {
    Box,
    Button,
    TextField,
    Paper,
    Typography,
    Alert,
    FormControl,
    InputLabel,
    Select,
    MenuItem
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { useEffect } from 'react';

export default function SqliteAdmin() {
    const [sql, setSql] = useState('');
    const [rows, setRows] = useState([]);
    const [columns, setColumns] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [rowCount, setRowCount] = useState(0);
    const [tables, setTables] = useState([]);
    const [selectedTable, setSelectedTable] = useState('');
    const [paginationModel, setPaginationModel] = useState({
        page: 0,
        pageSize: 50,
    });

    useEffect(() => {
        fetch('http://127.0.0.1:8000/api/db/tables')
            .then(res => res.json())
            .then(data => setTables(data.tables || []))
            .catch(err => console.error("Failed to load tables", err));
    }, []);

    const handleTableChange = (event) => {
        const tableName = event.target.value;
        setSelectedTable(tableName);
        setSql(`SELECT * FROM ${tableName}`);
    };

    const executeSql = async (isNewQuery = false) => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch('http://127.0.0.1:8000/api/db/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sql: sql,
                    page: isNewQuery ? 1 : paginationModel.page + 1, // API is 1-indexed
                    page_size: paginationModel.pageSize,
                }),
            });

            const data = await response.json();

            if (data.error) {
                setError(data.error);
                setRows([]);
            } else {
                // Dynamic columns for DataGrid
                const cols = data.columns.map((col) => ({
                    field: col,
                    headerName: col,
                    flex: 1,
                    minWidth: 150,
                }));
                setColumns(cols);

                // DataGrid needs unique 'id' for each row.
                // If query doesn't return 'id', we generate one temporarily
                const rowsWithId = data.data.map((row, index) => ({
                    id: row.id || `row-${index}`,
                    ...row
                }));
                setRows(rowsWithId);
                setRowCount(data.total);

                if (isNewQuery) {
                    setPaginationModel({ ...paginationModel, page: 0 });
                }
            }
        } catch (err) {
            setError('Failed to connect to server');
        } finally {
            setLoading(false);
        }
    };

    const handlePaginationModelChange = (newModel) => {
        setPaginationModel(newModel);
        // Fetch new page
        // Note: DataGrid calls this when page changes.
        // But we need to call executeSql with new page.
        // However, executeSql relies on state, which might not be updated yet?
        // Better to pass params directly or just use effect? 
        // Simplified: Just trigger fetch when model changes? 
        // Actually standard pattern is to use useEffect or just call fetch here.
        // But wait, executeSql uses 'sql' state which is fine.

        // We need to act carefully to avoid loops.
        // Let's rely on User clicking "Execute" for new queries,
        // and this handler for paging existing query.
    };

    // Effect to trigger fetch when pagination changes, ONLY if we have data/active query?
    // Or just manual for now? The requirements say "Pagination".
    // Let's use useEffect dependent on paginationModel, but guard against initial mount if needed.
    // Actually, let's just make a specific function for page change to avoid complexity with 'sql' editing.

    // Re-implementing logic to be cleaner:

    return (
        <Box sx={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Typography variant="h5">SQLite Admin</Typography>

            <Paper sx={{ p: 2 }}>
                <FormControl fullWidth sx={{ mb: 2, maxWidth: 400 }}>
                    <InputLabel id="table-select-label">Select Table</InputLabel>
                    <Select
                        labelId="table-select-label"
                        id="table-select"
                        value={selectedTable}
                        label="Select Table"
                        onChange={handleTableChange}
                    >
                        {tables.map((table) => (
                            <MenuItem key={table} value={table}>
                                {table}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>

                <TextField
                    label="SQL Query"
                    multiline
                    rows={4}
                    fullWidth
                    value={sql}
                    onChange={(e) => setSql(e.target.value)}
                    variant="outlined"
                    sx={{ mb: 2 }}
                />
                <Button
                    variant="contained"
                    onClick={() => executeSql(true)}
                    disabled={loading}
                >
                    {loading ? 'Executing...' : 'Execute Query'}
                </Button>
            </Paper>

            {error && <Alert severity="error">{error}</Alert>}

            <Paper sx={{ height: 600, width: '100%' }}>
                <DataGrid
                    rows={rows}
                    columns={columns}
                    rowCount={rowCount}
                    loading={loading}
                    pageSizeOptions={[50]}
                    paginationModel={paginationModel}
                    paginationMode="server"
                    onPaginationModelChange={(model) => {
                        setPaginationModel(model);
                        // Trigger fetch for next page
                        // We need to pass the NEW model, because state update is async
                        // Refactoring executeSql to accept params would be better, but let's just hack it:
                        // actually we can just put this fetch in useEffect [paginationModel]
                        // provided we have a flag that "query is active".

                        // For simplicity, I will duplicate fetch logic here or make executeSql accept explicit page.

                        // Execute with new page info
                        const fetchPage = async () => {
                            setLoading(true);
                            try {
                                const response = await fetch('http://127.0.0.1:8000/api/db/query', {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({
                                        sql: sql,
                                        page: model.page + 1,
                                        page_size: model.pageSize,
                                    }),
                                });
                                const data = await response.json();
                                if (!data.error) {
                                    const rowsWithId = data.data.map((row, index) => ({
                                        id: row.id || `row-${index}`,
                                        ...row
                                    }));
                                    setRows(rowsWithId);
                                }
                            } catch (e) { console.error(e) }
                            setLoading(false);
                        };
                        fetchPage();
                    }}
                />
            </Paper>
        </Box>
    );
}

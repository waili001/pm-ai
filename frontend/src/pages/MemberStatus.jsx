import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Container,
    Paper,
    FormControl,
    Autocomplete,
    TextField,
    CircularProgress,
    Tooltip,
    Link,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Grid,
    Divider
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { JiraMarkupRenderer } from '../utils/JiraMarkupRenderer';
import { authenticatedFetch } from '../utils/api';

const MemberStatus = () => {
    const [departments, setDepartments] = useState([]);
    const [selectedDept, setSelectedDept] = useState(null);
    const [members, setMembers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [loadingDepts, setLoadingDepts] = useState(false);

    // Dialog State
    const [openDialog, setOpenDialog] = useState(false);
    const [selectedTicket, setSelectedTicket] = useState(null);
    const [loadingTicket, setLoadingTicket] = useState(false);

    const handleTicketClick = async (ticketNumber) => {
        setOpenDialog(true);
        setLoadingTicket(true);
        setSelectedTicket(null); // Clear previous
        try {
            const response = await authenticatedFetch(`/api/project/ticket/${ticketNumber}`);
            if (response.ok) {
                const data = await response.json();
                setSelectedTicket(data);
            } else {
                console.error("Failed to fetch ticket details");
            }
        } catch (error) {
            console.error("Error fetching ticket:", error);
        } finally {
            setLoadingTicket(false);
        }
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
        setSelectedTicket(null);
    };

    // Fetch Departments on Mount
    useEffect(() => {
        const fetchDepts = async () => {
            setLoadingDepts(true);
            try {
                const response = await authenticatedFetch('/api/members/departments');
                if (response.ok) {
                    const data = await response.json();

                    setDepartments(data);

                    // Restore last selected department
                    const lastDept = localStorage.getItem('member_status_last_dept');
                    if (lastDept && data.includes(lastDept)) {
                        setSelectedDept(lastDept);
                    }
                } else {
                    console.error("Failed to fetch departments");
                }
            } catch (error) {
                console.error("Error fetching departments:", error);
            } finally {
                setLoadingDepts(false);
            }
        };
        fetchDepts();
    }, []);

    // Fetch Members when Dept selected
    useEffect(() => {
        if (!selectedDept) {
            setMembers([]);
            return;
        }

        const fetchMembers = async () => {
            setLoading(true);
            try {
                // Encode dept name for URL
                const response = await authenticatedFetch(`/api/members/status?department=${encodeURIComponent(selectedDept)}`);
                if (response.ok) {
                    const data = await response.json();
                    // Add unique ID for DataGrid
                    const rows = data.map((item, index) => ({
                        id: item.member_no || index,
                        ...item
                    }));
                    setMembers(rows);
                } else {
                    console.error("Failed to fetch member status");
                }
            } catch (error) {
                console.error("Error fetching member status:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchMembers();
    }, [selectedDept]);

    const columns = [
        { field: 'department', headerName: 'Department', width: 130 }, // Implicit in filter but good to show
        { field: 'team', headerName: 'Team', width: 130 },
        { field: 'member_name', headerName: 'Member', width: 130 },
        { field: 'position', headerName: 'Position', width: 130 },
        {
            field: 'current_tps',
            headerName: 'In-Progress TP',
            width: 400,
            renderCell: (params) => (
                <Box sx={{ py: 1, display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                    {Array.isArray(params.value) ? params.value.map((item, index) => (
                        <Link
                            key={index}
                            href={`https://jira.tc-gaming.co/jira/browse/${item.number}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            variant="body2"
                            sx={{ textAlign: 'left' }}
                        >
                            {item.department ? `[${item.department}] ` : ''}{item.full}
                        </Link>
                    )) : params.value}
                </Box>
            )
        },

        {
            field: 'in_progress_tickets',
            headerName: 'In Progress Tickets',
            width: 350,
            renderCell: (params) => (
                <Box sx={{ py: 1, display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                    {Array.isArray(params.value) ? params.value.map((item, index) => (
                        <Tooltip key={index} title={item.full} arrow placement="top">
                            <Link
                                component="button"
                                variant="body2"
                                onClick={() => handleTicketClick(item.number)}
                                sx={{ textAlign: 'left', color: 'text.primary', textDecoration: 'underline' }}
                            >
                                {item.number}
                            </Link>
                        </Tooltip>
                    )) : params.value}
                </Box>
            )
        },
        {
            field: 'completed_last_7d',
            headerName: 'Completed (Last 7 Days)',
            width: 250,
            renderCell: (params) => {
                const tickets = params.value || [];
                if (tickets.length === 0) return '-';

                const firstTicket = tickets[0].number;
                const count = tickets.length;
                const displayText = count > 1 ? `${firstTicket}...(${count})` : firstTicket;

                return (
                    <Box sx={{ py: 1, display: 'flex', alignItems: 'center' }}>
                        <Typography variant="body2">{displayText}</Typography>
                    </Box>
                );
            }
        },
    ];

    return (
        <Container maxWidth={false} sx={{ mt: 4, mb: 4 }}>
            <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', minHeight: '80vh' }}>
                <Typography component="h2" variant="h6" color="primary" gutterBottom>
                    Member Status Dashboard
                </Typography>

                <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
                    <FormControl sx={{ minWidth: 300 }}>
                        <Autocomplete
                            options={departments}
                            value={selectedDept}
                            onChange={(event, newValue) => {
                                setSelectedDept(newValue);
                                if (newValue) {
                                    localStorage.setItem('member_status_last_dept', newValue);
                                } else {
                                    localStorage.removeItem('member_status_last_dept');
                                }
                            }}
                            loading={loadingDepts}
                            renderInput={(params) => (
                                <TextField
                                    {...params}
                                    label="Select Department"
                                    InputProps={{
                                        ...params.InputProps,
                                        endAdornment: (
                                            <React.Fragment>
                                                {loadingDepts ? <CircularProgress color="inherit" size={20} /> : null}
                                                {params.InputProps.endAdornment}
                                            </React.Fragment>
                                        ),
                                    }}
                                />
                            )}
                        />
                    </FormControl>
                </Box>

                <Box sx={{ flexGrow: 1, width: '100%', height: '100%' }}>
                    <DataGrid
                        rows={members}
                        columns={columns}
                        pageSize={10}
                        rowsPerPageOptions={[10, 25, 50]}
                        loading={loading}
                        disableSelectionOnClick
                        getRowHeight={() => 'auto'}
                    />
                </Box>
            </Paper>

            {/* Ticket Detail Dialog */}
            <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
                <DialogTitle>
                    {selectedTicket?.ticket_number}
                    <Typography variant="subtitle2" component="span" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                        {selectedTicket?.issue_type} - {selectedTicket?.status}
                    </Typography>
                </DialogTitle>
                <DialogContent dividers>
                    {loadingTicket ? (
                        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                            <CircularProgress />
                        </Box>
                    ) : selectedTicket ? (
                        <>
                            <Typography variant="h6" gutterBottom>
                                {selectedTicket.title}
                            </Typography>

                            <Grid container spacing={2} sx={{ mb: 2 }}>
                                <Grid item xs={6}>
                                    <Typography variant="caption" color="text.secondary">Assignee</Typography>
                                    <Typography variant="body1">{selectedTicket.assignee || "-"}</Typography>
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="caption" color="text.secondary">Reporter</Typography>
                                    <Typography variant="body1">{selectedTicket.reporter || "-"}</Typography>
                                </Grid>
                            </Grid>

                            <Divider sx={{ my: 1 }} />

                            <Typography variant="caption" color="text.secondary" gutterBottom>
                                Description
                            </Typography>
                            {selectedTicket.description ? (
                                <JiraMarkupRenderer text={selectedTicket.description} />
                            ) : (
                                <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                                    No description available.
                                </Typography>
                            )}
                        </>
                    ) : (
                        <Typography>No details found.</Typography>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog}>Close</Button>
                    {selectedTicket && (
                        <Button
                            href={`https://jira.tc-gaming.co/jira/browse/${selectedTicket.ticket_number}`}
                            target="_blank"
                            color="primary"
                        >
                            Open in Jira
                        </Button>
                    )}
                </DialogActions>
            </Dialog>


        </Container>
    );
};

export default MemberStatus;

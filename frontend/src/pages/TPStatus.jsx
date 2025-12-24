import { useState, useEffect } from 'react';
import {
    Box,
    Container,
    Typography,
    Autocomplete,
    TextField,
    Grid,
    Paper,
    Card,
    CardContent,
    CardActionArea,
    Chip,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Switch,
    FormControlLabel,
    Divider,
    Link,
    List,
    ListItem,
    ListItemButton,
    ListItemText
} from '@mui/material';
import { parseJiraMarkup } from '../utils/jiraMarkup';
import { JiraMarkupRenderer } from '../utils/JiraMarkupRenderer';

const STATUS_ORDER = ["Open", "To Do", "In Progress", "In Review", "Resolved", "Closed"];

const STORAGE_KEY = 'tp_kanban_last_selected';
const HISTORY_STORAGE_KEY = 'tp_kanban_recent_history';
const MAX_HISTORY = 10;

export default function TPStatus() {
    const [activeTPs, setActiveTPs] = useState([]);
    const [selectedTP, setSelectedTP] = useState(null);
    const [tickets, setTickets] = useState([]);
    const [loadingTPs, setLoadingTPs] = useState(false);
    const [loadingTickets, setLoadingTickets] = useState(false);
    const [recentHistory, setRecentHistory] = useState([]);

    // Filter State
    const [hideDev, setHideDev] = useState(false);

    // Dialog State
    const [openDialog, setOpenDialog] = useState(false);
    const [selectedTicket, setSelectedTicket] = useState(null);

    // Load recent history from localStorage
    useEffect(() => {
        const stored = localStorage.getItem(HISTORY_STORAGE_KEY);
        if (stored) {
            try {
                setRecentHistory(JSON.parse(stored));
            } catch (e) {
                console.error('Failed to parse history', e);
            }
        }
    }, []);

    // Function to add TP to recent history
    const addToHistory = (tp) => {
        if (!tp || !tp.id) return;

        setRecentHistory(prev => {
            // Remove if already exists
            const filtered = prev.filter(item => item.id !== tp.id);
            // Add to front
            const updated = [tp, ...filtered].slice(0, MAX_HISTORY);
            // Save to localStorage
            localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(updated));
            return updated;
        });
    };

    // Fetch Active TPs on Mount
    useEffect(() => {
        setLoadingTPs(true);
        fetch('http://127.0.0.1:8000/api/tp/active')
            .then(res => res.json())
            .then(data => {
                if (Array.isArray(data)) {
                    setActiveTPs(data);

                    // Restore last selected TP from localStorage
                    const savedId = localStorage.getItem(STORAGE_KEY);
                    if (savedId) {
                        const savedTP = data.find(tp => tp.id === savedId);
                        if (savedTP) {
                            setSelectedTP(savedTP);
                        }
                    }
                }
                setLoadingTPs(false);
            })
            .catch(err => {
                console.error("Error fetching TPs:", err);
                setLoadingTPs(false);
            });
    }, []);

    // Fetch Tickets when TP Selected
    useEffect(() => {
        if (selectedTP && selectedTP.ticket_number) {
            // Save to localStorage
            localStorage.setItem(STORAGE_KEY, selectedTP.id);
            // Add to recent history
            addToHistory(selectedTP);

            setLoadingTickets(true);
            fetch(`http://127.0.0.1:8000/api/tp/${selectedTP.ticket_number}/tcg_tickets`)
                .then(res => res.json())
                .then(data => {
                    if (Array.isArray(data)) {
                        setTickets(data);
                    }
                    setLoadingTickets(false);
                })
                .catch(err => {
                    console.error("Error fetching tickets:", err);
                    setLoadingTickets(false);
                });
        } else {
            setTickets([]);
        }
    }, [selectedTP]);

    // Group Tickets by Status
    const groupedTickets = tickets.reduce((acc, ticket) => {
        // Filter: Hide DEV Task if enabled
        // Note: issue_type might need normalization if case varies
        if (hideDev && ticket.issue_type === 'DEV Task') {
            return acc;
        }

        const status = ticket.status || 'Unknown';
        if (!acc[status]) {
            acc[status] = [];
        }
        acc[status].push(ticket);
        return acc;
    }, {});

    // Determine Columns: predefined order first, then others
    const avaliableStatuses = Object.keys(groupedTickets);
    const kanbanColumns = [
        ...STATUS_ORDER.filter(s => avaliableStatuses.includes(s)),
        ...avaliableStatuses.filter(s => !STATUS_ORDER.includes(s)).sort()
    ];

    const handleCardClick = (ticket) => {
        setSelectedTicket(ticket);
        setOpenDialog(true);
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
        setSelectedTicket(null);
    };

    return (
        <Container maxWidth={false}>
            <Box sx={{ my: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    TP Kanban
                </Typography>

                {/* TP Selector & Filter */}
                <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
                    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
                        <Box sx={{ flexGrow: 1, minWidth: '300px' }}>
                            <Autocomplete
                                fullWidth
                                options={activeTPs}
                                getOptionLabel={(option) => option.label || ""}
                                isOptionEqualToValue={(option, value) => option.id === value.id}
                                value={selectedTP}
                                onChange={(event, newValue) => setSelectedTP(newValue)}
                                loading={loadingTPs}
                                renderInput={(params) => (
                                    <TextField
                                        {...params}
                                        label="Select Active TP Project"
                                        variant="outlined"
                                        helperText="Search by TP Number or Title"
                                    />
                                )}
                            />
                        </Box>
                        <Box sx={{ flexShrink: 0 }}>
                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={hideDev}
                                        onChange={(e) => setHideDev(e.target.checked)}
                                    />
                                }
                                label="Hide DEV Tasks"
                            />
                        </Box>
                    </Box>

                    {/* Recent History */}
                    {recentHistory.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                            <Typography variant="caption" color="text.secondary" gutterBottom>
                                Recent Viewed (Click to select)
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
                                {recentHistory.map((tp) => (
                                    <Chip
                                        key={tp.id}
                                        label={tp.ticket_number}
                                        onClick={() => setSelectedTP(tp)}
                                        size="small"
                                        variant={selectedTP?.id === tp.id ? "filled" : "outlined"}
                                        color={selectedTP?.id === tp.id ? "primary" : "default"}
                                    />
                                ))}
                            </Box>
                        </Box>
                    )}
                </Paper>

                {/* Kanban Board */}
                {selectedTP && (
                    <Box sx={{ flexGrow: 1, overflowX: 'auto' }}>
                        {loadingTickets ? (
                            <Typography>Loading tickets...</Typography>
                        ) : tickets.length === 0 ? (
                            <Typography>No TCG tickets found for this TP.</Typography>
                        ) : (
                            <Grid container spacing={2} wrap="nowrap" sx={{ minWidth: kanbanColumns.length * 300 }}>
                                {kanbanColumns.map(status => (
                                    <Grid item key={status} sx={{ minWidth: 300, maxWidth: 350 }}>
                                        <Paper
                                            sx={{
                                                p: 2,
                                                height: '100%',
                                                bgcolor: '#f5f5f5'
                                            }}
                                        >
                                            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                                                {status} ({groupedTickets[status].length})
                                            </Typography>

                                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                                {groupedTickets[status].map((ticket, index) => (
                                                    <Card key={index} sx={{ mb: 1 }}>
                                                        <CardActionArea onClick={() => handleCardClick(ticket)}>
                                                            <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                                                                <Typography variant="subtitle2" color="primary" sx={{ fontWeight: 'bold', zIndex: 10, position: 'relative' }}>
                                                                    <Link
                                                                        href={`https://jira.tc-gaming.co/jira/browse/${ticket.ticket_number}`}
                                                                        target="_blank"
                                                                        rel="noopener noreferrer"
                                                                        onClick={(e) => e.stopPropagation()}
                                                                        underline="hover"
                                                                        color="inherit"
                                                                    >
                                                                        {ticket.ticket_number}
                                                                    </Link>
                                                                </Typography>
                                                                <Typography variant="body2" sx={{ mb: 1, lineHeight: 1.3 }}>
                                                                    {ticket.title}
                                                                </Typography>

                                                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                                    <Chip
                                                                        label={ticket.assignee || "Unassigned"}
                                                                        size="small"
                                                                        variant="outlined"
                                                                        sx={{ fontSize: '0.7rem', height: 20 }}
                                                                    />
                                                                    <Chip
                                                                        label={ticket.issue_type || "Task"}
                                                                        size="small"
                                                                        color="secondary"
                                                                        sx={{ fontSize: '0.7rem', height: 20 }}
                                                                    />
                                                                </Box>
                                                            </CardContent>
                                                        </CardActionArea>
                                                    </Card>
                                                ))}
                                            </Box>
                                        </Paper>
                                    </Grid>
                                ))}
                            </Grid>
                        )}
                    </Box>
                )}

            </Box>

            {/* Ticket Detail Dialog */}
            <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
                <DialogTitle>
                    {selectedTicket?.ticket_number}
                    <Typography variant="subtitle2" color="text.secondary">
                        {selectedTicket?.issue_type} - {selectedTicket?.status}
                    </Typography>
                </DialogTitle>
                <DialogContent dividers>
                    <Typography variant="h6" gutterBottom>
                        {selectedTicket?.title}
                    </Typography>

                    <Grid container spacing={2} sx={{ mb: 2 }}>
                        <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">Assignee</Typography>
                            <Typography variant="body1">{selectedTicket?.assignee || "-"}</Typography>
                        </Grid>
                        <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">Reporter</Typography>
                            <Typography variant="body1">{selectedTicket?.reporter || "-"}</Typography>
                        </Grid>
                    </Grid>

                    <Divider sx={{ my: 1 }} />

                    <Typography variant="caption" color="text.secondary" gutterBottom>
                        Description
                    </Typography>
                    <JiraMarkupRenderer text={selectedTicket?.description} />

                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog}>Close</Button>
                </DialogActions>
            </Dialog>

        </Container>
    );
}

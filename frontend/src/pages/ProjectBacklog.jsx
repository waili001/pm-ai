import { useState, useEffect } from 'react';
import {
    Box,
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

    Divider,
    Link,
    List,
    ListItem,
    ListItemButton,
    ListItemText
} from '@mui/material';
import { parseJiraMarkup } from '../utils/jiraMarkup';
import { JiraMarkupRenderer } from '../utils/JiraMarkupRenderer';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import { authenticatedFetch } from '../utils/api';

const STATUS_ORDER = ["Open", "To Do", "In Progress", "Resolved", "Scheduled", "Closed"]; // Removed In Review

const STORAGE_KEY = 'project_backlog_last_selected';
const HISTORY_STORAGE_KEY = 'project_backlog_recent_history';
const MAX_HISTORY = 10;

export default function ProjectBacklog() {
    const [activeTPs, setActiveTPs] = useState([]);
    const [selectedTP, setSelectedTP] = useState(null);
    const [tickets, setTickets] = useState([]);
    const [loadingTPs, setLoadingTPs] = useState(false);
    const [loadingTickets, setLoadingTickets] = useState(false);
    const [recentHistory, setRecentHistory] = useState([]);


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
        authenticatedFetch('/api/project/active')
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
            authenticatedFetch(`/api/project/${selectedTP.ticket_number}/tcg_tickets`)
                .then(res => res.json())
                .then(data => {
                    if (Array.isArray(data)) {
                        // 1. Map all tickets by Ticket Number for easy lookup
                        const ticketMap = {};
                        data.forEach(t => {
                            ticketMap[t.ticket_number] = { ...t, childTasks: [] };
                        });

                        // 2. Identify Children and Parents
                        const mainTickets = [];
                        const orphanChildren = []; // Should ideally be none if data is consistent

                        data.forEach(rawTicket => {
                            const ticket = ticketMap[rawTicket.ticket_number];

                            if (ticket.parent_tickets) {
                                // This is a child ticket
                                // handle comma separated parents if necessary, though usually one parent for hierarchy
                                const parents = ticket.parent_tickets.split(',').map(s => s.trim()).filter(s => s);

                                let foundParent = false;
                                parents.forEach(parentId => {
                                    if (ticketMap[parentId]) {
                                        ticketMap[parentId].childTasks.push(ticket);
                                        foundParent = true;
                                    }
                                });

                                if (!foundParent) {
                                    // Parent not in this TP context, decide whether to show or hide.
                                    // User requirement: "hide parent tickets 不為空的 tcg 單"
                                    // So we hide it even if parent is missing from board.
                                    console.warn(`Ticket ${ticket.ticket_number} has parent ${ticket.parent_tickets} but parent not found in current view.`);
                                }
                            } else {
                                // No parent, so it stays on main board
                                mainTickets.push(ticket);
                            }
                        });

                        setTickets(mainTickets);
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
        ...STATUS_ORDER,
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

    const getStatusColor = (status) => {
        const s = (status || "").toLowerCase();
        if (s === "in progress") return "primary";
        if (s === "in review") return "warning";
        if (s === "resolved" || s === "scheduled" || s === "done") return "success";
        if (s === "closed") return "success";
        if (s === "open" || s === "to do") return "default";
        return "default";
    };

    const getIssueTypeColor = (type) => {
        const t = (type || "").toLowerCase();
        if (t === "bug") return "error";
        if (t === "story") return "success";
        if (t === "change request") return "secondary"; // Purple in default MUI, or use custom color logic if needed
        return "default";
    };

    return (
        <Box sx={{ width: '100%', px: 3, py: 0 }}>
            <Box sx={{ my: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    Project Backlog
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
                            <DragDropContext onDragEnd={async (result) => {
                                const { source, destination, draggableId } = result;
                                if (!destination) return;
                                if (source.droppableId === destination.droppableId && source.index === destination.index) return;
                                if (source.droppableId !== destination.droppableId) return; // Same column only

                                const status = source.droppableId;
                                const items = Array.from(groupedTickets[status] || []);
                                const [reorderedItem] = items.splice(source.index, 1);
                                items.splice(destination.index, 0, reorderedItem);

                                const newOrderIds = items.map(t => t.id);

                                // Optimistic Update (avoiding duplication by excluding active items from base list)
                                // 1. Set new sort_order for active items
                                const reorderedItemsWithSort = items.map((t, idx) => ({ ...t, sort_order: idx }));
                                // 2. Filter base list
                                const otherTickets = tickets.filter(t => !newOrderIds.includes(t.id));
                                // 3. Combine
                                const newTickets = [...otherTickets, ...reorderedItemsWithSort];

                                setTickets(newTickets);

                                // API Call
                                authenticatedFetch('/api/project/reorder_tcg', {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({
                                        status: status,
                                        ticket_ids: newOrderIds
                                    })
                                }).catch(err => console.error("Reorder failed", err));
                            }}>
                                <Grid container spacing={2} wrap="nowrap" sx={{ minWidth: kanbanColumns.length * 300 }}>
                                    {kanbanColumns.map(status => (
                                        <Grid item key={status} sx={{ minWidth: 300, maxWidth: 350 }}>
                                            <Droppable droppableId={status}>
                                                {(provided) => (
                                                    <Paper
                                                        ref={provided.innerRef}
                                                        {...provided.droppableProps}
                                                        sx={{
                                                            p: 2,
                                                            height: '100%',
                                                            bgcolor: '#f5f5f5',
                                                            display: 'flex',
                                                            flexDirection: 'column'
                                                        }}
                                                    >
                                                        <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                                                            {status} ({groupedTickets[status]?.length || 0})
                                                        </Typography>

                                                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, flexGrow: 1, minHeight: 100 }}>
                                                            {groupedTickets[status]?.map((ticket, index) => {
                                                                // Inconsistent State Logic
                                                                const isParentFinished = ["Resolved", "Scheduled", "Closed", "Done"].includes(ticket.status);
                                                                const hasIncompleteSubtasks = ticket.childTasks && ticket.childTasks.some(t => !["In Review", "Closed"].includes(t.status));
                                                                const isInconsistent = isParentFinished && hasIncompleteSubtasks;

                                                                return (
                                                                    <Draggable key={ticket.id || ticket.ticket_number} draggableId={ticket.id || ticket.ticket_number} index={index}>
                                                                        {(provided, snapshot) => (
                                                                            <Card
                                                                                ref={provided.innerRef}
                                                                                {...provided.draggableProps}
                                                                                {...provided.dragHandleProps}
                                                                                onClick={() => handleCardClick(ticket)}
                                                                                sx={{
                                                                                    mb: 1,
                                                                                    cursor: 'pointer', // Indicate clickable
                                                                                    backgroundColor: snapshot.isDragging ? '#e3f2fd' : 'background.paper',
                                                                                    border: snapshot.isDragging ? '2px solid #2196f3' : (isInconsistent ? '2px solid #d32f2f' : 'none'),
                                                                                    boxShadow: snapshot.isDragging ? 6 : 1,
                                                                                    transition: 'background-color 0.2s ease, box-shadow 0.2s ease',
                                                                                    ...provided.draggableProps.style,
                                                                                    '&:hover': {
                                                                                        boxShadow: 3 // Hover effect
                                                                                    }
                                                                                }}
                                                                            >
                                                                                <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                                                                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 0.5 }}>
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
                                                                                        <Chip
                                                                                            label={ticket.issue_type || "Task"}
                                                                                            size="small"
                                                                                            color={getIssueTypeColor(ticket.issue_type)}
                                                                                            variant={getIssueTypeColor(ticket.issue_type) === 'default' ? "outlined" : "filled"}
                                                                                            sx={{ fontSize: '0.65rem', height: 18 }}
                                                                                        />
                                                                                    </Box>
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
                                                                                        {ticket.childTasks && ticket.childTasks.length > 0 && (() => {
                                                                                            const stats = {
                                                                                                total: 0,
                                                                                                done: 0,
                                                                                                fe: { total: 0, done: 0 },
                                                                                                be: { total: 0, done: 0 }
                                                                                            };

                                                                                            ticket.childTasks.forEach(t => {
                                                                                                stats.total++;
                                                                                                const isDone = t.status === "In Review" || t.status === "Closed";
                                                                                                if (isDone) stats.done++;

                                                                                                // FE vs BE Logic
                                                                                                // Components is a comma separated string usually, or potentially null
                                                                                                const comps = t.components || "";
                                                                                                if (comps.includes("TAD TAC UI")) {
                                                                                                    stats.fe.total++;
                                                                                                    if (isDone) stats.fe.done++;
                                                                                                } else {
                                                                                                    stats.be.total++;
                                                                                                    if (isDone) stats.be.done++;
                                                                                                }
                                                                                            });

                                                                                            const fePct = stats.fe.total > 0 ? Math.round((stats.fe.done / stats.fe.total) * 100) : 0;
                                                                                            const bePct = stats.be.total > 0 ? Math.round((stats.be.done / stats.be.total) * 100) : 0;

                                                                                            // Condition 1: Parent Finished (Inconsistent State Warning)
                                                                                            if (isParentFinished) {
                                                                                                return (
                                                                                                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                                                                                                        {stats.fe.total > 0 && stats.fe.done < stats.fe.total && (
                                                                                                            <Chip label="FE Pending" size="small" color="error" sx={{ fontSize: '0.65rem', height: 20, fontWeight: 'bold' }} />
                                                                                                        )}
                                                                                                        {stats.be.total > 0 && stats.be.done < stats.be.total && (
                                                                                                            <Chip label="BE Pending" size="small" color="error" sx={{ fontSize: '0.65rem', height: 20, fontWeight: 'bold' }} />
                                                                                                        )}
                                                                                                        <Chip
                                                                                                            label={`Tasks: ${stats.total}`}
                                                                                                            size="small"
                                                                                                            color="default"
                                                                                                            variant="outlined"
                                                                                                            sx={{ fontSize: '0.7rem', height: 20 }}
                                                                                                        />
                                                                                                    </Box>
                                                                                                );
                                                                                            }

                                                                                            // Condition 2: In Progress (Show Progress Split)
                                                                                            if (ticket.status === "In Progress") {
                                                                                                return (
                                                                                                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                                                                                                        {stats.fe.total > 0 && (
                                                                                                            <Chip
                                                                                                                label={`FE: ${fePct}%`}
                                                                                                                size="small"
                                                                                                                color={fePct === 100 ? "success" : "warning"}
                                                                                                                sx={{ fontSize: '0.65rem', height: 20, fontWeight: 'bold' }}
                                                                                                            />
                                                                                                        )}
                                                                                                        {stats.be.total > 0 && (
                                                                                                            <Chip
                                                                                                                label={`BE: ${bePct}%`}
                                                                                                                size="small"
                                                                                                                color={bePct === 100 ? "success" : "warning"}
                                                                                                                sx={{ fontSize: '0.65rem', height: 20, fontWeight: 'bold' }}
                                                                                                            />
                                                                                                        )}
                                                                                                        <Chip
                                                                                                            label={`Tasks: ${stats.total}`}
                                                                                                            size="small"
                                                                                                            color="default"
                                                                                                            variant="outlined"
                                                                                                            sx={{ fontSize: '0.7rem', height: 20 }}
                                                                                                        />
                                                                                                    </Box>
                                                                                                );
                                                                                            }

                                                                                            // Default: Show just task count
                                                                                            return (
                                                                                                <Box sx={{ display: 'flex', gap: 0.5 }}>
                                                                                                    <Chip
                                                                                                        label={`Tasks: ${stats.total}`}
                                                                                                        size="small"
                                                                                                        color="default"
                                                                                                        variant="outlined"
                                                                                                        sx={{ fontSize: '0.7rem', height: 20 }}
                                                                                                    />
                                                                                                </Box>
                                                                                            );
                                                                                        })()}
                                                                                    </Box>
                                                                                </CardContent>
                                                                            </Card>
                                                                        )}
                                                                    </Draggable>
                                                                );
                                                            })}
                                                            {provided.placeholder}
                                                        </Box>
                                                    </Paper>
                                                )}
                                            </Droppable>
                                        </Grid>
                                    ))}
                                </Grid>
                            </DragDropContext>
                        )}
                    </Box>
                )}

            </Box>

            {/* Ticket Detail Dialog */}
            <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
                <DialogTitle>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                            {selectedTicket?.ticket_number}
                            <Chip
                                label={selectedTicket?.issue_type}
                                size="small"
                                color={getIssueTypeColor(selectedTicket?.issue_type)}
                                variant={getIssueTypeColor(selectedTicket?.issue_type) === 'default' ? "outlined" : "filled"}
                            />
                        </Box>
                        <Chip
                            label={selectedTicket?.status}
                            color={getStatusColor(selectedTicket?.status)}
                            size="small"
                        />
                    </Box>
                </DialogTitle>
                <DialogContent dividers sx={{
                    scrollbarWidth: 'none',
                    '&::-webkit-scrollbar': { display: 'none' }
                }}>
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
                {selectedTicket?.childTasks && selectedTicket.childTasks.length > 0 && (
                    <Box sx={{ p: 2, bgcolor: '#f9f9f9', borderTop: '1px solid #e0e0e0' }}>
                        <Typography variant="subtitle2" gutterBottom>
                            Sub Tasks
                        </Typography>
                        <Box sx={{
                            maxHeight: 200,
                            overflowY: 'auto',
                            scrollbarWidth: 'none',
                            '&::-webkit-scrollbar': { display: 'none' }
                        }}>
                            <List dense>
                                {[...selectedTicket.childTasks].sort((a, b) => {
                                    const getStatusWeight = (status) => {
                                        const s = (status || "").toLowerCase();
                                        if (s === "open" || s === "to do") return 1;
                                        if (s === "in progress") return 2;
                                        if (s === "in review") return 3;
                                        if (["resolved", "scheduled", "done", "closed"].includes(s)) return 4;
                                        return 5; // Unknown
                                    };
                                    return getStatusWeight(a.status) - getStatusWeight(b.status);
                                }).map(child => (
                                    <ListItem key={child.ticket_number} disablePadding sx={{ py: 0.5 }}>
                                        <Grid container alignItems="center" spacing={1}>
                                            <Grid item xs={3}>
                                                <Link
                                                    href={`https://jira.tc-gaming.co/jira/browse/${child.ticket_number}`}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    underline="hover"
                                                    sx={{ fontSize: '0.85rem' }}
                                                >
                                                    {child.ticket_number}
                                                </Link>
                                            </Grid>
                                            <Grid item xs={5}>
                                                <Typography variant="body2" noWrap title={child.title}>
                                                    {child.title}
                                                </Typography>
                                            </Grid>
                                            <Grid item xs={2}>
                                                <Typography variant="caption" display="block">
                                                    {child.assignee}
                                                </Typography>
                                            </Grid>
                                            <Grid item xs={2}>
                                                <Chip
                                                    label={child.status}
                                                    size="small"
                                                    color={getStatusColor(child.status)}
                                                    variant="outlined"
                                                    sx={{ height: 16, fontSize: '0.65rem' }}
                                                />
                                            </Grid>
                                        </Grid>
                                    </ListItem>
                                ))}
                            </List>
                        </Box>
                    </Box>
                )}

                <DialogActions>
                    <Button onClick={handleCloseDialog}>Close</Button>
                </DialogActions>
            </Dialog>

        </Box>
    );
}

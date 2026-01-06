import React from 'react';
import {
    Box,
    Typography,
    Grid,
    Chip,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Divider,
    Link,
    List,
    ListItem
} from '@mui/material';
import { JiraMarkupRenderer } from '../utils/JiraMarkupRenderer';

// Helper functions for colors (copied from ProjectBacklog for self-containment or could be moved to utils)
const getStatusColor = (status) => {
    if (!status) return 'default';
    const s = status.toLowerCase();
    if (s === 'open' || s === 'to do') return 'default'; // Grey/Default
    if (s === 'in progress') return 'primary'; // Blue
    if (s === 'resolved' || s === 'done' || s === 'closed') return 'success'; // Green
    if (s === 'scheduled') return 'info'; // Light Blue/Cyan
    if (s === 'in review') return 'warning'; // Orange
    return 'default';
};

const getIssueTypeColor = (type) => {
    if (!type) return 'default';
    const t = type.toLowerCase();
    if (t === 'bug') return 'error';
    if (t === 'story') return 'success';
    if (t === 'task') return 'primary';
    if (t === 'sub-task') return 'default';
    if (t === 'tp') return 'secondary'; // Purple for TP
    return 'default';
};

const TicketDetailModal = ({ open, onClose, ticket }) => {
    if (!ticket) return null;

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                        {ticket.ticket_number}
                        <Chip
                            label={ticket.issue_type}
                            size="small"
                            color={getIssueTypeColor(ticket.issue_type)}
                            variant={getIssueTypeColor(ticket.issue_type) === 'default' ? "outlined" : "filled"}
                        />
                    </Box>
                    <Chip
                        label={ticket.status}
                        color={getStatusColor(ticket.status)}
                        size="small"
                    />
                </Box>
            </DialogTitle>
            <DialogContent dividers sx={{
                scrollbarWidth: 'none',
                '&::-webkit-scrollbar': { display: 'none' }
            }}>
                <Typography variant="h6" gutterBottom>
                    {ticket.title}
                </Typography>

                <Grid container spacing={2} sx={{ mb: 2 }}>
                    <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">Assignee</Typography>
                        <Typography variant="body1">{ticket.assignee || "-"}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">Reporter</Typography>
                        <Typography variant="body1">{ticket.reporter || "-"}</Typography>
                    </Grid>
                </Grid>

                {ticket.tp_info && (
                    <Box sx={{ mb: 2, p: 1.5, bgcolor: '#f5f5f5', borderRadius: 1, border: '1px solid #e0e0e0' }}>
                        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 'bold', display: 'block', mb: 1 }}>
                            Related Project (TP)
                        </Typography>
                        <Grid container spacing={2} alignItems="center">
                            <Grid item xs={3}>
                                <Link
                                    href={`https://jira.tc-gaming.co/jira/browse/${ticket.tp_info.ticket_number}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    underline="hover"
                                    sx={{ fontWeight: 'bold' }}
                                >
                                    {ticket.tp_info.ticket_number}
                                </Link>
                            </Grid>
                            <Grid item xs={5}>
                                <Typography variant="body2" noWrap title={ticket.tp_info.title}>
                                    {ticket.tp_info.title}
                                </Typography>
                            </Grid>
                            <Grid item xs={2}>
                                <Chip
                                    label={ticket.tp_info.status}
                                    color={getStatusColor(ticket.tp_info.status)}
                                    size="small"
                                    variant="outlined"
                                    sx={{ height: 20, fontSize: '0.7rem' }}
                                />
                            </Grid>
                            <Grid item xs={2}>
                                <Typography variant="caption" display="block" color="text.secondary">
                                    Due: {ticket.tp_info.due_day || "-"}
                                </Typography>
                            </Grid>
                        </Grid>
                    </Box>
                )}

                <Divider sx={{ my: 1 }} />

                <Typography variant="caption" color="text.secondary" gutterBottom>
                    Description
                </Typography>
                <JiraMarkupRenderer text={ticket.description} />

            </DialogContent>
            {ticket.childTasks && ticket.childTasks.length > 0 && (
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
                            {[...ticket.childTasks].sort((a, b) => {
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
                <Button onClick={onClose}>Close</Button>
            </DialogActions>
        </Dialog>
    );
};

export default TicketDetailModal;

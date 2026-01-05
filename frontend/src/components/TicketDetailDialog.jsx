
import React from 'react';
import {
    Box,
    Typography,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Grid,
    Divider,
    Chip,
    List,
    ListItem,
    Link
} from '@mui/material';
import { JiraMarkupRenderer } from '../utils/JiraMarkupRenderer';

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
    if (t === "change request") return "secondary";
    return "default";
};

const TicketDetailDialog = ({ open, onClose, ticket }) => {
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

                <Divider sx={{ my: 1 }} />

                <Typography variant="caption" color="text.secondary" gutterBottom>
                    Description
                </Typography>
                <JiraMarkupRenderer text={ticket.description} />

            </DialogContent>
            {/* Show childTasks if available (ProjectBacklog uses this property) */}
            {/* Or sub_tasks if from API /ticket/{number} (ProjectController uses 'sub_tasks') */}
            {/* We should normalize or check both */}
            {((ticket.childTasks && ticket.childTasks.length > 0) || (ticket.sub_tasks && ticket.sub_tasks.length > 0)) && (
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
                            {/* Merge or pick one list. ProjectBacklog uses childTasks, API uses sub_tasks */}
                            {[...(ticket.childTasks || ticket.sub_tasks || [])].sort((a, b) => {
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

export default TicketDetailDialog;

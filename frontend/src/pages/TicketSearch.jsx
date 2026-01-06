import React, { useState, useEffect } from 'react';
import {
    Box,
    TextField,
    Button,
    Card,
    CardContent,
    Typography,
    Grid,
    InputAdornment,
    IconButton,
    Alert,
    CircularProgress,
    Chip,
    Stack
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import HistoryIcon from '@mui/icons-material/History';
import { authenticatedFetch } from '../utils/api';
import { jiraToHtml } from '../utils/jiraFormatter';

import { useNavigate, useLocation, useSearchParams } from 'react-router-dom';

const TicketSearch = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [ticketData, setTicketData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [searched, setSearched] = useState(false);
    const [searchHistory, setSearchHistory] = useState([]);
    const [searchParams, setSearchParams] = useSearchParams();

    // Load history and last search on mount
    useEffect(() => {
        try {
            // Load History
            const history = JSON.parse(localStorage.getItem('ticketSearchHistory') || '[]');
            setSearchHistory(history);

            // Check URL params first
            const queryParam = searchParams.get('q');
            if (queryParam) {
                handleSearch(queryParam);
            } else {
                // Load Last Search Data if no query param
                const savedData = localStorage.getItem('lastTicketSearch');
                if (savedData) {
                    const parsed = JSON.parse(savedData);
                    if (parsed.ticketData && parsed.searchTerm) {
                        setTicketData(parsed.ticketData);
                        setSearchTerm(parsed.searchTerm);
                        setSearched(true);
                    }
                }
            }
        } catch (e) {
            console.error("Failed to load local storage data", e);
        }
    }, [searchParams]); // Depend on searchParams

    const updateHistory = (term) => {
        const cleanTerm = term.trim().toUpperCase();
        let newHistory = searchHistory.filter(item => item !== cleanTerm); // Remove duplicate if exists
        newHistory.unshift(cleanTerm); // Add to front
        newHistory = newHistory.slice(0, 10); // Keep max 10

        setSearchHistory(newHistory);
        localStorage.setItem('ticketSearchHistory', JSON.stringify(newHistory));
    };

    const handleSearch = async (termOverride = null) => {
        let termToSearch = termOverride || searchTerm;
        if (!termToSearch || !termToSearch.trim()) return;

        // Convert to uppercase for query consistency
        termToSearch = termToSearch.trim().toUpperCase();

        // Ensure text field is updated to the clean upper version
        setSearchTerm(termToSearch);

        setLoading(true);
        setError(null);
        setTicketData(null);
        setSearched(true);

        try {
            const response = await authenticatedFetch(`/api/project/ticket/${encodeURIComponent(termToSearch)}`);

            if (response.ok) {
                const data = await response.json();
                if (data) {
                    setTicketData(data);

                    // Update History & Last Search Persistence
                    updateHistory(termToSearch);
                    localStorage.setItem('lastTicketSearch', JSON.stringify({
                        searchTerm: termToSearch.trim(),
                        ticketData: data,
                        timestamp: Date.now()
                    }));

                } else {
                    setError('Ticket not found.');
                }
            } else {
                if (response.status === 404) {
                    setError('Ticket not found.');
                } else {
                    setError(`Error fetching ticket: ${response.statusText}`);
                }
            }
        } catch (err) {
            console.error("Search error:", err);
            setError('An error occurred while searching.');
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    };

    const StatusChip = ({ status }) => {
        let color = 'default';
        if (['Closed', 'Resolved', 'Done'].includes(status)) color = 'success';
        if (['In Progress', 'Development', 'Testing'].includes(status)) color = 'primary';
        if (['Open', 'To Do', 'Backlog'].includes(status)) color = 'warning';

        return <Chip label={status || 'Unknown'} color={color} size="small" />;
    };

    return (
        <Box sx={{ p: 4, maxWidth: 1000, margin: '0 auto' }}>
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, color: 'primary.main', mb: 4 }}>
                Ticket Search
            </Typography>

            {/* Search Section */}
            <Box sx={{ mb: 4 }}>
                <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                    <TextField
                        fullWidth
                        variant="outlined"
                        placeholder="Enter Ticket Number (e.g., TCG-1234 or TP-5678)"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        onKeyPress={handleKeyPress}
                        InputProps={{
                            startAdornment: (
                                <InputAdornment position="start">
                                    <SearchIcon color="action" />
                                </InputAdornment>
                            ),
                        }}
                    />
                    <Button
                        variant="contained"
                        onClick={() => handleSearch()}
                        disabled={loading || !searchTerm.trim()}
                        sx={{ px: 4 }}
                    >
                        {loading ? <CircularProgress size={24} color="inherit" /> : 'Search'}
                    </Button>
                </Box>

                {/* Recent Searches */}
                {searchHistory.length > 0 && (
                    <Stack direction="row" spacing={1} alignItems="center" sx={{ flexWrap: 'wrap', gap: 1 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ mr: 1 }}>
                            <HistoryIcon sx={{ fontSize: 16, verticalAlign: 'text-bottom', mr: 0.5 }} />
                            Recent:
                        </Typography>
                        {searchHistory.map((term, index) => (
                            <Chip
                                key={index}
                                label={term}
                                size="small"
                                onClick={() => handleSearch(term)}
                                sx={{ cursor: 'pointer' }}
                                variant="outlined"
                            />
                        ))}
                    </Stack>
                )}
            </Box>

            {error && (
                <Alert severity="warning" sx={{ mb: 3 }}>
                    {error}
                </Alert>
            )}

            {ticketData && (
                <Card elevation={3} sx={{ borderRadius: 2 }}>
                    <CardContent sx={{ p: 4 }}>
                        <Grid container spacing={3}>

                            <Grid item xs={12} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #eee', pb: 2, mb: 2 }}>
                                <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                                    {ticketData.ticket_number}
                                </Typography>
                                <StatusChip status={ticketData.status} />
                            </Grid>

                            <Grid item xs={12}>
                                <Typography variant="h6" gutterBottom>{ticketData.title}</Typography>
                            </Grid>

                            <Grid item xs={12} md={6}>
                                <Typography variant="subtitle2" color="text.secondary">Assignee</Typography>
                                <Typography variant="body1" gutterBottom>{ticketData.assignee || '-'}</Typography>
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <Typography variant="subtitle2" color="text.secondary">Reporter</Typography>
                                <Typography variant="body1" gutterBottom>{ticketData.reporter || '-'}</Typography>
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <Typography variant="subtitle2" color="text.secondary">Issue Type</Typography>
                                <Typography variant="body1" gutterBottom>{ticketData.issue_type || '-'}</Typography>
                            </Grid>
                            {/* TCG Additional Details */}
                            {ticketData.issue_type !== 'TP' && (
                                <>
                                    <Grid item xs={12} md={6}>
                                        <Typography variant="subtitle2" color="text.secondary">TP Number</Typography>
                                        <Typography variant="body1">{ticketData.tp_number || '-'}</Typography>
                                    </Grid>
                                    <Grid item xs={12} md={6}>
                                        <Typography variant="subtitle2" color="text.secondary">Fix Version</Typography>
                                        <Typography variant="body1">{ticketData.fix_versions || '-'}</Typography>
                                    </Grid>
                                </>
                            )}
                            {/* TP Specific Fields */}
                            {ticketData.issue_type === 'TP' && (
                                <>
                                    <Grid item xs={12} md={6}>
                                        <Typography variant="subtitle2" color="text.secondary">Released Date</Typography>
                                        <Typography variant="body1">{ticketData.released_date || '-'}</Typography>
                                    </Grid>
                                    <Grid item xs={12} md={6}>
                                        <Typography variant="subtitle2" color="text.secondary">Target Date</Typography>
                                        <Typography variant="body1">{ticketData.due_day || '-'}</Typography>
                                    </Grid>
                                </>
                            )}

                            {/* TCG Specific Fields - Description */}
                            {ticketData.description && (
                                <Grid item xs={12} sx={{ mt: 2 }}>
                                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>Description</Typography>
                                    <Box sx={{
                                        bgcolor: '#f5f5f5',
                                        p: 2,
                                        borderRadius: 1,
                                        fontFamily: 'Roboto, Helvetica, Arial, sans-serif',
                                        fontSize: '0.9rem',
                                        maxHeight: 600,
                                        overflow: 'auto',
                                        // Styles for generated HTML
                                        '& h1, & h2, & h3, & h4, & h5, & h6': { mt: 1, mb: 0.5, fontWeight: 'bold' },
                                        '& ul, & ol': { pl: 3, my: 1 },
                                        '& li': { mb: 0.5 },
                                        '& code': { bgcolor: '#e0e0e0', px: 0.5, borderRadius: 0.5, fontFamily: 'monospace' },
                                        '& pre': { bgcolor: '#2d2d2d', color: '#fff', p: 1.5, borderRadius: 1, overflowX: 'auto', my: 1 },
                                        '& pre code': { bgcolor: 'transparent', p: 0, color: 'inherit' },
                                        '& a': { color: 'primary.main', textDecoration: 'none', '&:hover': { textDecoration: 'underline' } },
                                        '& strong': { fontWeight: 600 },
                                        '& em': { fontStyle: 'italic' }
                                    }}
                                        dangerouslySetInnerHTML={{ __html: jiraToHtml(ticketData.description) }}
                                    />
                                </Grid>
                            )}

                            {/* Sub-tasks Section (Below Description) */}
                            {ticketData.sub_tasks && Array.isArray(ticketData.sub_tasks) && ticketData.sub_tasks.length > 0 && (
                                <Grid item xs={12} sx={{ mt: 2, width: '100%' }}>
                                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>Sub-tasks</Typography>
                                    <Box sx={{ bgcolor: '#fff', border: '1px solid #eee', borderRadius: 1, overflow: 'hidden' }}>
                                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                                            <thead>
                                                <tr style={{ backgroundColor: '#f9f9f9', borderBottom: '1px solid #eee' }}>
                                                    <th style={{ padding: '8px 12px', textAlign: 'left', width: '120px' }}>Ticket</th>
                                                    <th style={{ padding: '8px 12px', textAlign: 'left' }}>Title</th>
                                                    <th style={{ padding: '8px 12px', textAlign: 'left', width: '120px' }}>Status</th>
                                                    <th style={{ padding: '8px 12px', textAlign: 'left', width: '150px' }}>Assignee</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {ticketData.sub_tasks.map((task) => (
                                                    <tr key={task.ticket_number} style={{ borderBottom: '1px solid #f0f0f0' }}>
                                                        <td style={{ padding: '8px 12px' }}>
                                                            <Chip
                                                                label={task.ticket_number}
                                                                size="small"
                                                                onClick={() => handleSearch(task.ticket_number)}
                                                                sx={{ cursor: 'pointer', height: 24, fontSize: '0.75rem' }}
                                                            />
                                                        </td>
                                                        <td style={{ padding: '8px 12px' }}>{task.title || '-'}</td>
                                                        <td style={{ padding: '8px 12px' }}><StatusChip status={task.status} /></td>
                                                        <td style={{ padding: '8px 12px' }}>{task.assignee || '-'}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </Box>
                                </Grid>
                            )}


                        </Grid>
                    </CardContent>
                </Card>
            )}

            {!ticketData && searched && !loading && !error && (
                <Box sx={{ textAlign: 'center', mt: 4, color: 'text.secondary' }}>
                    <Typography>No ticket details to display.</Typography>
                </Box>
            )}
        </Box>
    );
};

export default TicketSearch;

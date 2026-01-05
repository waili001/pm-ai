
import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Card,
    CardContent,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Chip,
    Button,
    CircularProgress,
    Alert
} from '@mui/material';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import RefreshIcon from '@mui/icons-material/Refresh';
import { authenticatedFetch } from '../utils/api';


import TicketDetailDialog from '../components/TicketDetailDialog';

const TicketAnomaly = () => {
    const [anomalies, setAnomalies] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Detail Dialog State
    const [detailOpen, setDetailOpen] = useState(false);
    const [selectedTicketDetail, setSelectedTicketDetail] = useState(null);
    const [detailLoading, setDetailLoading] = useState(false);

    const fetchAnomalies = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await authenticatedFetch('/api/project/anomalies');
            if (response.ok) {
                const data = await response.json();
                setAnomalies(data);
            } else {
                setError(`Failed to fetch anomalies: ${response.statusText}`);
            }
        } catch (err) {
            console.error("Error fetching anomalies:", err);
            setError("An error occurred while fetching anomalies.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAnomalies();
    }, []);

    const handleTicketClick = async (ticketNumber) => {
        setDetailOpen(true);
        setDetailLoading(true);
        setSelectedTicketDetail(null);

        try {
            const response = await authenticatedFetch(`/api/project/ticket/${ticketNumber}`);
            if (response.ok) {
                const data = await response.json();
                setSelectedTicketDetail(data);
            } else {
                console.error("Failed to fetch ticket detail");
                // Optionally handle error in UI
            }
        } catch (e) {
            console.error("Error fetching details", e);
        } finally {
            setDetailLoading(false);
        }
    };

    const handleCloseDetail = () => {
        setDetailOpen(false);
        setSelectedTicketDetail(null);
    };

    return (
        <Box sx={{ p: 4, maxWidth: 1200, margin: '0 auto' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
                <Typography variant="h4" sx={{ fontWeight: 600, color: 'text.primary', display: 'flex', alignItems: 'center', gap: 2 }}>
                    <WarningAmberIcon color="warning" sx={{ fontSize: 40 }} />
                    Ticket Anomalies
                </Typography>
                <Button
                    startIcon={<RefreshIcon />}
                    variant="outlined"
                    onClick={fetchAnomalies}
                    disabled={loading}
                >
                    Refresh
                </Button>
            </Box>

            {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

            <Card elevation={3}>
                <CardContent sx={{ p: 0 }}>
                    <TableContainer>
                        <Table>
                            <TableHead sx={{ bgcolor: '#f5f5f5' }}>
                                <TableRow>
                                    <TableCell sx={{ fontWeight: 'bold' }}>Parent Ticket</TableCell>
                                    <TableCell sx={{ fontWeight: 'bold' }}>Title</TableCell>
                                    <TableCell sx={{ fontWeight: 'bold' }}>Assignee</TableCell>
                                    <TableCell sx={{ fontWeight: 'bold' }}>Parent Status</TableCell>
                                    <TableCell sx={{ fontWeight: 'bold' }}>Anomaly Reason</TableCell>
                                    <TableCell sx={{ fontWeight: 'bold' }}>TP Context</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {loading ? (
                                    <TableRow>
                                        <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                                            <CircularProgress />
                                        </TableCell>
                                    </TableRow>
                                ) : anomalies.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={6} align="center" sx={{ py: 4, color: 'text.secondary' }}>
                                            No anomalies detected. Great job!
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    anomalies.map((row) => (
                                        <TableRow
                                            key={row.id}
                                            hover
                                            sx={{ cursor: 'pointer' }}
                                            onClick={() => handleTicketClick(row.ticket_number)}
                                        >
                                            <TableCell>
                                                <Chip
                                                    label={row.ticket_number}
                                                    color="primary"
                                                    variant="outlined"
                                                    sx={{ fontWeight: 'bold', pointerEvents: 'none' }}
                                                />
                                            </TableCell>
                                            <TableCell sx={{ maxWidth: 300 }}>
                                                <Typography variant="body2" noWrap title={row.ticket_title}>
                                                    {row.ticket_title}
                                                </Typography>
                                            </TableCell>
                                            <TableCell>{row.assignee || '-'}</TableCell>
                                            <TableCell>
                                                <Chip label={row.parent_status} size="small" color="warning" />
                                            </TableCell>
                                            <TableCell sx={{ color: 'error.main', maxWidth: 350 }}>
                                                <Typography variant="body2" title={row.anomaly_reason} sx={{ fontSize: '0.875rem' }}>
                                                    {row.anomaly_reason}
                                                </Typography>
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="caption" display="block" color="text.secondary">
                                                    {row.tp_number}
                                                </Typography>
                                                <Typography variant="caption" display="block" color="text.secondary" noWrap sx={{ maxWidth: 150 }} title={row.tp_title}>
                                                    {row.tp_title}
                                                </Typography>
                                            </TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </CardContent>
            </Card>

            <TicketDetailDialog
                open={detailOpen}
                onClose={handleCloseDetail}
                ticket={selectedTicketDetail}
            />
        </Box>
    );
};

export default TicketAnomaly;

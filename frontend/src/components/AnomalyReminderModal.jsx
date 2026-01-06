import React from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Box,
    Alert
} from '@mui/material';
import { useNavigate } from 'react-router-dom';

const AnomalyReminderModal = ({ open, onClose, anomalies }) => {
    const navigate = useNavigate();

    if (!open || !anomalies || anomalies.length === 0) {
        return null;
    }

    const handleNavigate = (ticketNumber) => {
        // Navigate to ticket detail or search page
        // Assuming ticket search page for now with search param? 
        // Or just copy to clipboard / simple display.
        // Let's navigate to ticket-search? Or ticket-detail if exists.
        // The API returns 'ticket_number', let's go to ticket detail if possible, 
        // but we only have a modal for details in many places.
        // Let's just navigate to Ticket Search page for now.
        navigate(`/ticket-search?search=${ticketNumber}`);
        onClose();
    };

    return (
        <Dialog
            open={open}
            onClose={onClose}
            maxWidth="md"
            fullWidth
        >
            <DialogTitle sx={{ bgcolor: 'warning.light', color: 'warning.contrastText' }}>
                Pending Anomalies Reminder
            </DialogTitle>
            <DialogContent sx={{ mt: 2 }}>
                <Box sx={{ mb: 2 }}>
                    <Alert severity="warning">
                        The following tickets in your department have detected anomalies. Please review them.
                    </Alert>
                </Box>
                <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                        <TableHead>
                            <TableRow>
                                <TableCell><strong>Ticket</strong></TableCell>
                                <TableCell><strong>Title</strong></TableCell>
                                <TableCell><strong>Anomaly Reason</strong></TableCell>
                                <TableCell><strong>Detected At</strong></TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {anomalies.map((row) => (
                                <TableRow key={row.id} hover>
                                    <TableCell>
                                        <Button
                                            size="small"
                                            onClick={() => handleNavigate(row.ticket_number)}
                                            sx={{ textTransform: 'none' }}
                                        >
                                            {row.ticket_number}
                                        </Button>
                                    </TableCell>
                                    <TableCell>{row.ticket_title}</TableCell>
                                    <TableCell sx={{ color: 'error.main', fontWeight: 'bold' }}>
                                        {row.anomaly_reason}
                                    </TableCell>
                                    <TableCell>
                                        {new Date(row.detected_at).toLocaleString()}
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="primary" variant="contained">
                    Acknowledge & Close
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default AnomalyReminderModal;

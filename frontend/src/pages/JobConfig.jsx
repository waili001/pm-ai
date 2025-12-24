import { useState } from 'react';
import {
    Box,
    Typography,
    Button,
    Paper,
    Alert,
    CircularProgress,
    Stack
} from '@mui/material';
import { Sync as SyncIcon } from '@mui/icons-material';

export default function JobConfig() {
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);
    const [severity, setSeverity] = useState('info');

    const handleForceSync = async () => {
        setLoading(true);
        setMessage(null);
        try {
            const response = await fetch('http://localhost:8000/api/jobs/sync', {
                method: 'POST',
            });

            const data = await response.json();

            if (response.ok) {
                setMessage(data.message || 'Sync triggered successfully');
                setSeverity('success');
            } else {
                setMessage(data.message || 'Error triggering sync');
                setSeverity('error');
            }
        } catch (error) {
            console.error('Error:', error);
            setMessage('Network error or server unavailable');
            setSeverity('error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box sx={{ maxWidth: 800 }}>
            <Typography variant="h4" gutterBottom>
                Job Configuration
            </Typography>

            <Paper sx={{ p: 4, mt: 3 }}>
                <Stack spacing={3}>
                    <Typography variant="h6">
                        Data Synchronization
                    </Typography>

                    <Typography variant="body1" color="text.secondary">
                        Manually trigger a full synchronization of all Lark tables.
                        This will bypass the incremental check and fetch all records.
                        Use this if you suspect data inconsistency or want to refresh the entire database.
                    </Typography>

                    <Box>
                        <Button
                            variant="contained"
                            color="warning"
                            size="large"
                            startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SyncIcon />}
                            onClick={handleForceSync}
                            disabled={loading}
                        >
                            {loading ? 'Syncing...' : 'Force Sync All Tables'}
                        </Button>
                    </Box>

                    {message && (
                        <Alert severity={severity} sx={{ mt: 2 }}>
                            {message}
                        </Alert>
                    )}
                </Stack>
            </Paper>
        </Box>
    );
}

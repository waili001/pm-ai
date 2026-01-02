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
import { authenticatedFetch } from '../utils/api';

export default function JobConfig() {
    const [loadingSync, setLoadingSync] = useState(false);
    const [loadingVerify, setLoadingVerify] = useState(false);
    const [loadingDept, setLoadingDept] = useState(false);
    const [message, setMessage] = useState(null); // { type: 'success' | 'error', text: string }

    const handleVerifyJira = async () => {
        setLoadingVerify(true);
        setMessage(null);
        try {
            const res = await authenticatedFetch('/api/jobs/verify-jira', {
                method: 'POST',
            });
            const data = await res.json();
            if (res.ok) {
                setMessage({ type: 'success', text: `Jira Verify Started: ${data.message}` });
            } else {
                setMessage({ type: 'error', text: `Error: ${data.message}` });
            }
        } catch (err) {
            console.error('Error:', err);
            setMessage({ type: 'error', text: `Request failed: ${err.message}` });
        } finally {
            setLoadingVerify(false);
        }
    };

    const handleSyncDept = async () => {
        setLoadingDept(true);
        setMessage(null);
        try {
            const res = await authenticatedFetch('/api/sync/lark/dept', {
                method: 'POST',
            });
            const data = await res.json();
            if (res.ok) {
                setMessage({ type: 'success', text: `Dept Sync Started: ${data.message}` });
            } else {
                setMessage({ type: 'error', text: `Error: ${data.message}` });
            }
        } catch (err) {
            console.error('Error:', err);
            setMessage({ type: 'error', text: `Request failed: ${err.message}` });
        } finally {
            setLoadingDept(false);
        }
    };

    const handleForceSync = async () => {
        setLoadingSync(true);
        setMessage(null);
        try {
            const response = await authenticatedFetch('/api/jobs/sync', {
                method: 'POST',
            });

            const data = await response.json();

            if (response.ok) {
                setMessage({ type: 'success', text: data.message || 'Sync triggered successfully' });
            } else {
                setMessage({ type: 'error', text: data.message || 'Error triggering sync' });
            }
        } catch (error) {
            console.error('Error:', error);
            setMessage({ type: 'error', text: 'Network error or server unavailable' });
        } finally {
            setLoadingSync(false);
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
                            color="primary"
                            size="large"
                            startIcon={loadingSync ? <CircularProgress size={20} color="inherit" /> : <SyncIcon />}
                            onClick={handleForceSync}
                            disabled={loadingSync || loadingVerify || loadingDept}
                        >
                            {loadingSync ? 'Syncing...' : 'Force Sync All Tables'}
                        </Button>
                    </Box>

                    {message && message.type === 'success' && (
                        <Alert severity="success" sx={{ mt: 2 }}>
                            {message.text}
                        </Alert>
                    )}
                    {message && message.type === 'error' && (
                        <Alert severity="error" sx={{ mt: 2 }}>
                            {message.text}
                        </Alert>
                    )}
                </Stack>
            </Paper>

            <Paper sx={{ p: 4, mt: 3 }}>
                <Stack spacing={3}>
                    <Typography variant="h6">
                        Jira Verification & Department Sync
                    </Typography>

                    <Typography variant="body1" color="text.secondary">
                        Verify local TCG tickets against Jira. Active tickets that are not found in Jira (404)
                        will be deleted from the local database.
                        Also, manually sync department data from Lark.
                    </Typography>

                    <Stack direction="row" spacing={2}>
                        <Button
                            variant="outlined"
                            color="secondary"
                            size="large"
                            startIcon={loadingVerify ? <CircularProgress size={20} color="inherit" /> : <SyncIcon />}
                            onClick={handleVerifyJira}
                            disabled={loadingVerify || loadingSync || loadingDept}
                        >
                            {loadingVerify ? 'Verifying...' : 'Verify Jira Tickets'}
                        </Button>

                        <Button
                            variant="outlined"
                            color="warning"
                            size="large"
                            startIcon={loadingDept ? <CircularProgress size={20} color="inherit" /> : <SyncIcon />}
                            onClick={handleSyncDept}
                            disabled={loadingDept || loadingSync || loadingVerify}
                        >
                            {loadingDept ? 'Syncing...' : 'Sync Departments'}
                        </Button>
                    </Stack>

                    {message && message.type === 'success' && (
                        <Alert severity="success" sx={{ mt: 2 }}>
                            {message.text}
                        </Alert>
                    )}
                    {message && message.type === 'error' && (
                        <Alert severity="error" sx={{ mt: 2 }}>
                            {message.text}
                        </Alert>
                    )}
                </Stack>
            </Paper>
        </Box>
    );
}

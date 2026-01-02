import { useState, useEffect } from 'react';
import {
    Box, Paper, Typography, Button, Dialog, DialogTitle, DialogContent,
    DialogActions, TextField, Checkbox, FormControlLabel, FormGroup, Alert
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { authenticatedFetch } from '../utils/api';

export default function RoleManagement() {
    const [roles, setRoles] = useState([]);
    const [allPermissions, setAllPermissions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [openDialog, setOpenDialog] = useState(false);
    const [currentRole, setCurrentRole] = useState({ name: '', description: '', permissions: [] });
    const [isEdit, setIsEdit] = useState(false);
    const [error, setError] = useState(null);

    const fetchRoles = () => {
        setLoading(true);
        authenticatedFetch('/api/system/roles')
            .then(res => res.json())
            .then(data => setRoles(data))
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    };

    const PERMISSION_ORDER = [
        'DASHBOARD',
        'PROJECT_PLANNING',
        'PROJECT_BACKLOG',
        'MEMBER_STATUS',
        'SQLITE_ADMIN',
        'JOB_CONFIG',
        'ROLES',
        'USERS'
    ];

    const fetchPermissions = () => {
        authenticatedFetch('/api/system/roles/permissions')
            .then(res => res.json())
            .then(data => {
                const sorted = [...data].sort((a, b) => {
                    const indexA = PERMISSION_ORDER.indexOf(a.code);
                    const indexB = PERMISSION_ORDER.indexOf(b.code);
                    if (indexA === -1) return 1;
                    if (indexB === -1) return -1;
                    return indexA - indexB;
                });
                setAllPermissions(sorted);
            })
            .catch(err => console.error(err));
    };

    useEffect(() => {
        fetchRoles();
        fetchPermissions();
    }, []);

    const handleSave = async () => {
        setError(null);
        try {
            const url = isEdit ? `/api/system/roles/${currentRole.id}` : '/api/system/roles';
            const method = isEdit ? 'PUT' : 'POST';

            const res = await authenticatedFetch(url, {
                method,
                body: JSON.stringify(currentRole)
            });

            if (res.ok) {
                setOpenDialog(false);
                fetchRoles();
            } else {
                const data = await res.json();
                setError(data.detail || 'Failed to save');
            }
        } catch (e) {
            setError('Error saving role');
        }
    };

    const handleDelete = async (id) => {
        if (!confirm("Are you sure?")) return;
        try {
            const res = await authenticatedFetch(`/api/system/roles/${id}`, { method: 'DELETE' });
            if (res.ok) {
                fetchRoles();
            } else {
                const data = await res.json();
                alert(data.detail);
            }
        } catch (e) {
            alert('Error deleting');
        }
    }

    const columns = [
        { field: 'id', headerName: 'ID', width: 70 },
        { field: 'name', headerName: 'Name', width: 150 },
        { field: 'description', headerName: 'Description', width: 250 },
        {
            field: 'permissions',
            headerName: 'Permissions',
            width: 300,
            valueGetter: (params) => params.row?.permissions?.join(', ') || ''
        },
        {
            field: 'actions',
            headerName: 'Actions',
            width: 150,
            renderCell: (params) => (
                <Box>
                    <Button size="small" onClick={() => {
                        setCurrentRole(params.row);
                        setIsEdit(true);
                        setOpenDialog(true);
                    }}>Edit</Button>
                    <Button size="small" color="error" onClick={() => handleDelete(params.row.id)}>Delete</Button>
                </Box>
            )
        }
    ];

    const togglePermission = (code) => {
        setCurrentRole(prev => {
            const perms = prev.permissions.includes(code)
                ? prev.permissions.filter(p => p !== code)
                : [...prev.permissions, code];
            return { ...prev, permissions: perms };
        });
    };

    return (
        <Box sx={{ height: '100%', width: '100%', p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h5">Role Management</Typography>
                <Button variant="contained" onClick={() => {
                    setCurrentRole({ name: '', description: '', permissions: [] });
                    setIsEdit(false);
                    setOpenDialog(true);
                }}>Create Role</Button>
            </Box>

            <Paper sx={{ height: 600 }}>
                <DataGrid
                    rows={roles}
                    columns={columns}
                    loading={loading}
                    disableRowSelectionOnClick
                />
            </Paper>

            <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
                <DialogTitle>{isEdit ? 'Edit Role' : 'Create Role'}</DialogTitle>
                <DialogContent>
                    {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Role Name"
                        fullWidth
                        value={currentRole.name}
                        onChange={(e) => setCurrentRole({ ...currentRole, name: e.target.value })}
                        disabled={isEdit && currentRole.name === 'SUPER_ADMIN'} // Name immutable if SA
                    />
                    <TextField
                        margin="dense"
                        label="Description"
                        fullWidth
                        value={currentRole.description}
                        onChange={(e) => setCurrentRole({ ...currentRole, description: e.target.value })}
                    />

                    <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>Page Permissions</Typography>
                    <FormGroup row>
                        {allPermissions.map(perm => (
                            <FormControlLabel
                                key={perm.code}
                                control={
                                    <Checkbox
                                        checked={currentRole.permissions.includes(perm.code)}
                                        onChange={() => togglePermission(perm.code)}
                                    />
                                }
                                label={perm.name}
                                sx={{ width: '50%' }}
                            />
                        ))}
                    </FormGroup>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
                    <Button onClick={handleSave} variant="contained">Save</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
}

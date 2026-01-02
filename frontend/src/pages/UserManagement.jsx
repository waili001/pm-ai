import { useState, useEffect } from 'react';
import {
    Box, Paper, Typography, Button, Dialog, DialogTitle, DialogContent,
    DialogActions, FormControl, InputLabel, Select, MenuItem, Alert
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { authenticatedFetch } from '../utils/api';

export default function UserManagement() {
    const [users, setUsers] = useState([]);
    const [roles, setRoles] = useState([]);
    const [loading, setLoading] = useState(false);
    const [openDialog, setOpenDialog] = useState(false);
    const [selectedUser, setSelectedUser] = useState(null);
    const [selectedRoleId, setSelectedRoleId] = useState('');
    const [error, setError] = useState(null);

    const fetchUsers = () => {
        setLoading(true);
        authenticatedFetch('/api/system/users')
            .then(res => res.json())
            .then(data => setUsers(data))
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    };

    const fetchRoles = () => {
        authenticatedFetch('/api/system/roles')
            .then(res => res.json())
            .then(data => setRoles(data))
            .catch(err => console.error(err));
    };

    useEffect(() => {
        fetchUsers();
        fetchRoles();
    }, []);

    const handleOpenEdit = (user) => {
        setSelectedUser(user);
        setSelectedRoleId(user.role_id || ''); // Handle user without role or with legacy string role
        // Ideally we should find role ID by name if role_id is null but role string exists.
        // But controller returns role_id.
        // If user.role_id is null but user.role is 'SUPER_ADMIN', we might need to find ID.
        // But 'get_users' returns what is stored.
        // Let's assume role_id is reliable or we map it. 
        if (!user.role_id && user.role) {
            const found = roles.find(r => r.name === user.role);
            if (found) setSelectedRoleId(found.id);
        }

        setError(null);
        setOpenDialog(true);
    };

    const handleSave = async () => {
        setError(null);
        if (!selectedRoleId) {
            setError("Please select a role");
            return;
        }

        try {
            const res = await authenticatedFetch(`/api/system/users/role`, {
                method: 'POST',
                body: JSON.stringify({
                    user_id: selectedUser.id,
                    role_id: selectedRoleId
                })
            });

            if (res.ok) {
                setOpenDialog(false);
                fetchUsers();
            } else {
                const data = await res.json();
                setError(data.detail || 'Failed to save');
            }
        } catch (e) {
            setError('Error saving user role');
        }
    };

    const columns = [
        { field: 'id', headerName: 'ID', width: 70 },
        { field: 'username', headerName: 'Username', width: 150 },
        { field: 'full_name', headerName: 'Full Name', width: 200 },
        { field: 'email', headerName: 'Email', width: 200 },
        { field: 'role', headerName: 'Role', width: 150 }, // Displays role name
        {
            field: 'last_login',
            headerName: 'Last Login',
            width: 200,
            valueGetter: (value, row) => {
                if (!value) return '-';
                return new Date(value).toLocaleString();
            }
        },
        {
            field: 'actions',
            headerName: 'Actions',
            width: 150,
            renderCell: (params) => (
                <Button size="small" onClick={() => handleOpenEdit(params.row)}>Assign Role</Button>
            )
        }
    ];

    return (
        <Box sx={{ height: '100%', width: '100%', p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h5">User Management</Typography>
                <Button variant="outlined" onClick={fetchUsers}>Refresh</Button>
            </Box>

            <Paper sx={{ height: 600 }}>
                <DataGrid
                    rows={users}
                    columns={columns}
                    loading={loading}
                    disableRowSelectionOnClick
                />
            </Paper>

            <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
                <DialogTitle>Assign Role to {selectedUser?.username}</DialogTitle>
                <DialogContent sx={{ minWidth: 400, pt: 2 }}>
                    {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
                    <FormControl fullWidth sx={{ mt: 1 }}>
                        <InputLabel>Role</InputLabel>
                        <Select
                            value={selectedRoleId}
                            label="Role"
                            onChange={(e) => setSelectedRoleId(e.target.value)}
                        >
                            {roles.map(role => (
                                <MenuItem key={role.id} value={role.id}>
                                    {role.name}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
                    <Button onClick={handleSave} variant="contained">Save</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
}

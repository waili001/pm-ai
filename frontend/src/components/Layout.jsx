import { useState } from 'react';
import {
    Box,
    CssBaseline,
    Drawer,
    AppBar,
    Toolbar,
    List,
    Typography,
    Divider,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Collapse,
    Avatar,
    Menu,
    MenuItem,
    IconButton,
    Tooltip
} from '@mui/material';
import {
    Menu as MenuIcon,
    Dashboard,
    AdminPanelSettings,
    Storage,
    ExpandLess,
    ExpandMore,

    Settings,
    Assignment
} from '@mui/icons-material';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';

const drawerWidth = 240;

export default function Layout() {
    const navigate = useNavigate();
    const location = useLocation();
    const [adminOpen, setAdminOpen] = useState(true);

    const [anchorElUser, setAnchorElUser] = useState(null);
    const username = localStorage.getItem('username') || 'User';

    const handleAdminClick = () => {
        setAdminOpen(!adminOpen);
    };

    const handleOpenUserMenu = (event) => {
        setAnchorElUser(event.currentTarget);
    };

    const handleCloseUserMenu = () => {
        setAnchorElUser(null);
    };

    const handleLogout = () => {
        handleCloseUserMenu();
        localStorage.removeItem('auth_token');
        localStorage.removeItem('username');
        navigate('/login');
    };

    return (
        <Box sx={{ display: 'flex' }}>
            <CssBaseline />
            <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
                <Toolbar>
                    <Typography variant="h6" noWrap component="div">
                        TCG Projects Dashboard
                    </Typography>

                    <Box sx={{ flexGrow: 1 }} />

                    <Box sx={{ flexGrow: 0, display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Tooltip title="Open settings">
                            <IconButton onClick={handleOpenUserMenu} sx={{ p: 0 }}>
                                <Avatar alt={username} src="/static/images/avatar/2.jpg">
                                    {username.charAt(0).toUpperCase()}
                                </Avatar>
                            </IconButton>
                        </Tooltip>
                        <Typography variant="subtitle1" component="div" sx={{ display: { xs: 'none', sm: 'block' } }}>
                            {username}
                        </Typography>
                        <Menu
                            sx={{ mt: '45px' }}
                            id="menu-appbar"
                            anchorEl={anchorElUser}
                            anchorOrigin={{
                                vertical: 'top',
                                horizontal: 'right',
                            }}
                            keepMounted
                            transformOrigin={{
                                vertical: 'top',
                                horizontal: 'right',
                            }}
                            open={Boolean(anchorElUser)}
                            onClose={handleCloseUserMenu}
                        >
                            <MenuItem onClick={handleLogout}>
                                <Typography textAlign="center">Logout</Typography>
                            </MenuItem>
                        </Menu>
                    </Box>
                </Toolbar>
            </AppBar>
            <Drawer
                variant="permanent"
                sx={{
                    width: drawerWidth,
                    flexShrink: 0,
                    [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
                }}
            >
                <Toolbar />
                <Box sx={{ overflow: 'auto' }}>
                    <List>
                        <ListItem disablePadding>
                            <ListItemButton
                                selected={location.pathname === '/'}
                                onClick={() => navigate('/')}
                            >
                                <ListItemIcon>
                                    <Dashboard />
                                </ListItemIcon>
                                <ListItemText primary="Home" />
                            </ListItemButton>
                        </ListItem>

                        <ListItem disablePadding>
                            <ListItemButton
                                selected={location.pathname === '/project-planning'}
                                onClick={() => navigate('/project-planning')}
                            >
                                <ListItemIcon>
                                    <Dashboard />
                                </ListItemIcon>
                                <ListItemText primary="Project Planning" />
                            </ListItemButton>
                        </ListItem>



                        <ListItem disablePadding>
                            <ListItemButton
                                selected={location.pathname === '/project-backlog'}
                                onClick={() => navigate('/project-backlog')}
                            >
                                <ListItemIcon>
                                    <Assignment />
                                </ListItemIcon>
                                <ListItemText primary="Project Backlog" />
                            </ListItemButton>
                        </ListItem>

                        <ListItem disablePadding>
                            <ListItemButton
                                selected={location.pathname === '/member-status'}
                                onClick={() => navigate('/member-status')}
                            >
                                <ListItemIcon>
                                    <Dashboard />
                                </ListItemIcon>
                                <ListItemText primary="Member Status" />
                            </ListItemButton>
                        </ListItem>

                        <ListItem disablePadding>
                            <ListItemButton onClick={handleAdminClick}>
                                <ListItemIcon>
                                    <AdminPanelSettings />
                                </ListItemIcon>
                                <ListItemText primary="Admin" />
                                {adminOpen ? <ExpandLess /> : <ExpandMore />}
                            </ListItemButton>
                        </ListItem>

                        <Collapse in={adminOpen} timeout="auto" unmountOnExit>
                            <List component="div" disablePadding>
                                <ListItemButton
                                    sx={{ pl: 4 }}
                                    selected={location.pathname === '/admin/sqlite'}
                                    onClick={() => navigate('/admin/sqlite')}
                                >
                                    <ListItemIcon>
                                        <Storage />
                                    </ListItemIcon>
                                    <ListItemText primary="SQLite" />
                                </ListItemButton>
                                <ListItemButton
                                    sx={{ pl: 4 }}
                                    selected={location.pathname === '/admin/jobs'}
                                    onClick={() => navigate('/admin/jobs')}
                                >
                                    <ListItemIcon>
                                        <Settings />
                                    </ListItemIcon>
                                    <ListItemText primary="Job Configuration" />
                                </ListItemButton>

                            </List>
                        </Collapse>
                    </List>
                </Box>
            </Drawer >
            <Box component="main" sx={{ flexGrow: 1, p: 3, bgcolor: 'background.default', minHeight: '100vh' }}>
                <Toolbar />
                <Outlet />
            </Box>
        </Box >
    );
}

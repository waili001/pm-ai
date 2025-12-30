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
    Collapse
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

    const handleAdminClick = () => {
        setAdminOpen(!adminOpen);
    };

    return (
        <Box sx={{ display: 'flex' }}>
            <CssBaseline />
            <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
                <Toolbar>
                    <Typography variant="h6" noWrap component="div">
                        PM AI Dashboard
                    </Typography>
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

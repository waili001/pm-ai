import { useState, useEffect } from 'react';
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
    Assignment,
    Security,
    People,
    Search as SearchIcon,
    WarningAmber
} from '@mui/icons-material';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import { authenticatedFetch } from '../utils/api';
import TicketDetailModal from './TicketDetailModal';
import AnomalyReminderModal from './AnomalyReminderModal';

const drawerWidth = 240;

export default function Layout() {
    const navigate = useNavigate();
    const location = useLocation();
    const [adminOpen, setAdminOpen] = useState(true);

    const [anchorElUser, setAnchorElUser] = useState(null);
    const [user, setUser] = useState({ username: 'User', permissions: [], is_super_admin: false });

    // Search Modal State
    const [searchModalOpen, setSearchModalOpen] = useState(false);
    const [searchedTicket, setSearchedTicket] = useState(null);

    // Anomaly Reminder State
    const [reminderOpen, setReminderOpen] = useState(false);
    const [pendingAnomalies, setPendingAnomalies] = useState([]);

    useEffect(() => {
        // Fetch User Info & Permissions
        authenticatedFetch('/api/auth/me')
            .then(res => res.json())
            .then(data => {
                setUser(data);
                if (data.username) {
                    localStorage.setItem('username', data.username);
                }
            })
            .catch(err => console.error("Failed to fetch user info", err));
    }, []);

    // Check for Pending Anomalies (Once per session)
    useEffect(() => {
        if (user.username && user.username !== 'User') {
            const hasChecked = sessionStorage.getItem('hasCheckedAnomalies');
            if (!hasChecked) {
                authenticatedFetch('/api/project/anomalies/my-pending')
                    .then(res => res.json())
                    .then(data => {
                        if (data.show_modal) {
                            setPendingAnomalies(data.anomalies);
                            setReminderOpen(true);
                        }
                        sessionStorage.setItem('hasCheckedAnomalies', 'true');
                    })
                    .catch(err => console.error("Failed to check anomalies", err));
            }
        }
    }, [user.username]);

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
        sessionStorage.removeItem('hasCheckedAnomalies'); // Clear session check on logout
        navigate('/login');
    };

    const hasPermission = (code) => {
        if (user.is_super_admin) return true;
        return user.permissions && user.permissions.includes(code);
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
                        {/* Global Ticket Search Bar */}
                        {hasPermission('TICKET_SEARCH') && (
                            <Box sx={{
                                position: 'relative',
                                borderRadius: 1,
                                bgcolor: 'rgba(255, 255, 255, 0.15)',
                                '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.25)' },
                                mr: 2,
                                width: '100%',
                                maxWidth: '250px',
                                display: { xs: 'none', sm: 'block' }
                            }}>
                                <input
                                    placeholder="Search (e.g. TCG-123)..."
                                    onKeyDown={async (e) => {
                                        if (e.key === 'Enter') {
                                            const term = e.target.value.trim();
                                            if (term) {
                                                // navigate(`/ticket-search?q=${encodeURIComponent(term)}`);
                                                // New Requirement: Open Modal
                                                try {
                                                    const res = await authenticatedFetch(`/api/project/ticket/${term.toUpperCase()}`);
                                                    if (res.ok) {
                                                        const data = await res.json();
                                                        if (data) {
                                                            setSearchedTicket(data);
                                                            setSearchModalOpen(true);
                                                            e.target.value = ''; // clear
                                                        } else {
                                                            alert("Ticket not found");
                                                        }
                                                    } else {
                                                        alert("Ticket not found or error occurred");
                                                    }
                                                } catch (err) {
                                                    console.error(err);
                                                    alert("Search failed");
                                                }
                                            }
                                        }
                                    }}
                                    style={{
                                        color: 'inherit',
                                        padding: '8px 8px 8px 40px',
                                        border: 'none',
                                        width: '100%',
                                        background: 'transparent',
                                        outline: 'none',
                                        color: 'white'
                                    }}
                                />
                                <Box sx={{
                                    position: 'absolute',
                                    left: 10,
                                    top: '50%',
                                    transform: 'translateY(-50%)',
                                    pointerEvents: 'none',
                                    display: 'flex',
                                    alignItems: 'center'
                                }}>
                                    <SearchIcon sx={{ color: 'white' }} />
                                </Box>
                            </Box>
                        )}

                        <Tooltip title="Open settings">
                            <IconButton onClick={handleOpenUserMenu} sx={{ p: 0 }}>
                                <Avatar alt={user.username} src="/static/images/avatar/2.jpg">
                                    {user.username ? user.username.charAt(0).toUpperCase() : 'U'}
                                </Avatar>
                            </IconButton>
                        </Tooltip>
                        <Typography variant="subtitle1" component="div" sx={{ display: { xs: 'none', sm: 'block' } }}>
                            {user.username} ({user.role})
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
                        {hasPermission('DASHBOARD') && (
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
                        )}

                        {/* PROJECT_PLANNING Permission or Default? Requirement says based on permissions. 
                            Config has PROJECT_PLANNING. */}
                        {hasPermission('PROJECT_PLANNING') && (
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
                        )}

                        {/* Project Backlog - Assuming Open or same perm? 
                            Not in config. Let's assume open for now or share PROJECT_PLANNING */}
                        {hasPermission('PROJECT_BACKLOG') && (
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
                        )}

                        {hasPermission('MEMBER_STATUS') && (
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
                        )}

                        {/* Ticket Search Link - Protected by TICKET_SEARCH */}
                        {hasPermission('TICKET_SEARCH') && (
                            <>
                                <ListItem disablePadding>
                                    <ListItemButton
                                        selected={location.pathname === '/ticket-search'}
                                        onClick={() => navigate('/ticket-search')}
                                    >
                                        <ListItemIcon>
                                            <SearchIcon />
                                        </ListItemIcon>
                                        <ListItemText primary="Ticket Search" />
                                    </ListItemButton>
                                </ListItem>
                                <ListItem disablePadding>
                                    <ListItemButton
                                        selected={location.pathname === '/ticket-anomaly'}
                                        onClick={() => navigate('/ticket-anomaly')}
                                    >
                                        <ListItemIcon>
                                            <WarningAmber />
                                        </ListItemIcon>
                                        <ListItemText primary="Ticket Anomaly" />
                                    </ListItemButton>
                                </ListItem>
                            </>
                        )}

                        {/* Validating if ANY admin page is accessible to show parent menu */}
                        {(hasPermission('ROLES') || hasPermission('USERS') || hasPermission('JOB_CONFIG') || hasPermission('SQLITE_ADMIN')) && (
                            <>
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
                                        {hasPermission('SQLITE_ADMIN') && (
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
                                        )}

                                        {hasPermission('JOB_CONFIG') && (
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
                                        )}

                                        {hasPermission('ROLES') && (
                                            <ListItemButton
                                                sx={{ pl: 4 }}
                                                selected={location.pathname === '/admin/roles'}
                                                onClick={() => navigate('/admin/roles')}
                                            >
                                                <ListItemIcon>
                                                    <Security />
                                                </ListItemIcon>
                                                <ListItemText primary="Roles" />
                                            </ListItemButton>
                                        )}

                                        {hasPermission('USERS') && (
                                            <ListItemButton
                                                sx={{ pl: 4 }}
                                                selected={location.pathname === '/admin/users'}
                                                onClick={() => navigate('/admin/users')}
                                            >
                                                <ListItemIcon>
                                                    <People />
                                                </ListItemIcon>
                                                <ListItemText primary="Users" />
                                            </ListItemButton>
                                        )}

                                    </List>
                                </Collapse>
                            </>
                        )}
                    </List>
                </Box>
            </Drawer >
            <Box component="main" sx={{ flexGrow: 1, p: 3, bgcolor: 'background.default', minHeight: '100vh' }}>
                <Toolbar />
                <Outlet />
            </Box>

            <TicketDetailModal
                open={searchModalOpen}
                onClose={() => setSearchModalOpen(false)}
                ticket={searchedTicket}
            />

            <AnomalyReminderModal
                open={reminderOpen}
                onClose={() => setReminderOpen(false)}
                anomalies={pendingAnomalies}
            />
        </Box >
    );
}

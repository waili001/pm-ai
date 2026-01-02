
import React, { useState, useEffect } from 'react';
import {
    Box,
    Button,
    Container,
    CssBaseline,
    TextField,
    Typography,
    Card,
    CardContent,
    Link,
    Alert
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';

export default function Login() {
    const navigate = useNavigate();
    const location = useLocation();

    // State
    const [showLocal, setShowLocal] = useState(false);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    // Initial check for token in URL (Lark Callback)
    useEffect(() => {
        const queryParams = new URLSearchParams(window.location.search);
        const token = queryParams.get('token');
        if (token) {
            localStorage.setItem('auth_token', token);
            // Redirect to home or intended page
            navigate('/');
        }
    }, [navigate]);

    const handleLarkLogin = () => {
        window.location.href = '/api/auth/lark/login';
    };

    const handleLocalLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || 'Login failed');
            }

            const data = await res.json();
            localStorage.setItem('auth_token', data.access_token);
            // Optional: Store user info
            localStorage.setItem('username', data.username);
            navigate('/');

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container component="main" maxWidth="xs">
            <CssBaseline />
            <Box
                sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minHeight: '100vh',
                }}
            >
                <Card sx={{ width: '100%', mt: 3, p: 2, boxShadow: 3 }}>
                    <CardContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
                        <Typography component="h1" variant="h5" fontWeight="bold">
                            PM AI Login
                        </Typography>

                        {error && <Alert severity="error" sx={{ width: '100%' }}>{error}</Alert>}

                        {/* Default: Lark Login */}
                        <Button
                            fullWidth
                            variant="contained"
                            color="primary"
                            size="large"
                            onClick={handleLarkLogin}
                            sx={{ mt: 2, bgcolor: '#3370ff', '&:hover': { bgcolor: '#285fd9' } }}
                        >
                            Sign in with Lark
                        </Button>

                        {/* Toggle Local Login */}
                        <Link
                            component="button"
                            variant="body2"
                            onClick={() => setShowLocal(!showLocal)}
                            sx={{ mt: 1 }}
                        >
                            {showLocal ? "Hide Other Methods" : "Other Login Methods"}
                        </Link>

                        {/* Local Login Form */}
                        {showLocal && (
                            <Box component="form" onSubmit={handleLocalLogin} sx={{ mt: 1, width: '100%' }}>
                                <TextField
                                    margin="normal"
                                    required
                                    fullWidth
                                    label="Username"
                                    autoFocus
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                />
                                <TextField
                                    margin="normal"
                                    required
                                    fullWidth
                                    label="Password"
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                                <Button
                                    type="submit"
                                    fullWidth
                                    variant="outlined"
                                    sx={{ mt: 2, mb: 1 }}
                                    disabled={loading}
                                >
                                    {loading ? "Signing in..." : "Sign In"}
                                </Button>
                            </Box>
                        )}
                    </CardContent>
                </Card>
            </Box>
        </Container>
    );
}

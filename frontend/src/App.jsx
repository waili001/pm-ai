import { useState, useEffect } from 'react'
import { Container, Typography, Box, Paper } from '@mui/material'
import { authenticatedFetch } from './utils/api';

import Login from './pages/Login';
import TicketSearch from './pages/TicketSearch';
import TicketAnomaly from './pages/TicketAnomaly';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Layout from './components/Layout';
import SqliteAdmin from './pages/SqliteAdmin';
import ProjectBacklog from './pages/ProjectBacklog';
import ProjectPlanning from './pages/ProjectPlanning';
import JobConfig from './pages/JobConfig';
import MemberStatus from './pages/MemberStatus';
import RoleManagement from './pages/RoleManagement';
import UserManagement from './pages/UserManagement';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('auth_token');
  const location = useLocation();

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

function Home() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    authenticatedFetch('/api/data')
      .then(response => response.json())
      .then(data => {
        setData(data)
        setLoading(false)
      })
      .catch(error => {
        console.error('Error fetching data:', error)
        setLoading(false)
      })
  }, [])

  return (
    <Box sx={{ width: '100%', px: 3, py: 0 }} bgcolor="white">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Backend Connection Status:
          </Typography>
          {loading ? (
            <Typography>Loading...</Typography>
          ) : (
            <Typography color={data ? "success.main" : "error"}>
              {data ? data.data : "Failed to connect to backend"}
            </Typography>
          )}
        </Paper>

      </Box>
    </Box>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route index element={<Home />} />
          <Route path="admin/sqlite" element={<SqliteAdmin />} />
          <Route path="admin/jobs" element={<JobConfig />} />
          <Route path="admin/roles" element={<RoleManagement />} />
          <Route path="admin/users" element={<UserManagement />} />
          <Route path="project-planning" element={<ProjectPlanning />} />
          <Route path="project-backlog" element={<ProjectBacklog />} />
          <Route path="member-status" element={<MemberStatus />} />
          <Route path="ticket-search" element={<TicketSearch />} />
          <Route path="ticket-anomaly" element={<TicketAnomaly />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App

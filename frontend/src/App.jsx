import { useState, useEffect } from 'react'
import { Container, Typography, Box, Paper } from '@mui/material'

import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import SqliteAdmin from './pages/SqliteAdmin'

import JobConfig from './pages/JobConfig'
import TPStatus from './pages/TPStatus'

function Home() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/data')
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
    <Container maxWidth={false}>
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
    </Container>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="admin/sqlite" element={<SqliteAdmin />} />
          <Route path="admin/jobs" element={<JobConfig />} />
          <Route path="tp-status" element={<TPStatus />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App

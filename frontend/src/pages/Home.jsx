import React, { useState, useEffect } from 'react';
import { Box, Paper, Grid, Typography, LinearProgress, Dialog, DialogTitle, DialogContent, IconButton, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button, TableSortLabel } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import DownloadIcon from '@mui/icons-material/Download';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';
import { authenticatedFetch } from '../utils/api';
import DepartmentSelector from '../components/DepartmentSelector';

export default function Home() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(false);
    const [department, setDepartment] = useState('ALL');
    const [error, setError] = useState(null);

    // Drill-down Modal State
    const [modalOpen, setModalOpen] = useState(false);
    const [selectedQuarter, setSelectedQuarter] = useState(null);
    const [quarterTPs, setQuarterTPs] = useState([]);
    const [modalLoading, setModalLoading] = useState(false);

    // Sorting State
    const [order, setOrder] = useState('asc');
    const [orderBy, setOrderBy] = useState('ticket_number');

    useEffect(() => {
        setLoading(true);
        const params = new URLSearchParams();
        if (department && department !== 'ALL') {
            params.append('department', department);
        }

        authenticatedFetch(`/api/project/dashboard-stats?${params.toString()}`)
            .then(res => {
                if (!res.ok) throw new Error('Failed to fetch data');
                return res.json();
            })
            .then(data => {
                setStats(data);
                setLoading(false);
                setError(null);
            })
            .catch(err => {
                console.error("Error fetching dashboard stats:", err);
                setError(err.message);
                setLoading(false);
            });
    }, [department]);

    const handleBarClick = (event) => {
        const quarter = event.point.category;
        setSelectedQuarter(quarter);
        setModalOpen(true);
        setModalLoading(true);

        const params = new URLSearchParams();
        params.append('quarter', quarter);
        if (department && department !== 'ALL') {
            params.append('department', department);
        }

        authenticatedFetch(`/api/project/closed-tps?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                setQuarterTPs(data);
                setModalLoading(false);
            })
            .catch(err => {
                console.error("Error fetching closed TPs:", err);
                setModalLoading(false);
            });
    };

    const handleCloseModal = () => {
        setModalOpen(false);
        setQuarterTPs([]);
        setSelectedQuarter(null);
        setOrder('asc');
        setOrderBy('ticket_number');
    };

    const handleRequestSort = (property) => {
        const isAsc = orderBy === property && order === 'asc';
        setOrder(isAsc ? 'desc' : 'asc');
        setOrderBy(property);
    };

    const handleExportCSV = () => {
        if (!quarterTPs.length) return;

        const headers = ["Ticket No", "Title", "Department", "Type", "Manager", "Released Date"];
        const keys = ["ticket_number", "title", "department", "project_type", "project_manager", "released_date"];

        const csvContent = [
            headers.join(","),
            ...quarterTPs.map(row => keys.map(key => `"${(row[key] || '').toString().replace(/"/g, '""')}"`).join(","))
        ].join("\n");

        // Add BOM (\uFEFF) so Excel opens it as UTF-8 with Chinese characters correctly
        const blob = new Blob(["\uFEFF" + csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", `Closed_TPs_${selectedQuarter}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    // Sorting Helper
    const sortedTPs = React.useMemo(() => {
        return [...quarterTPs].sort((a, b) => {
            if (orderBy === 'released_date') {
                // Date compare
                const dateA = new Date(a.released_date || 0);
                const dateB = new Date(b.released_date || 0);
                return order === 'asc' ? dateA - dateB : dateB - dateA;
            }
            // String compare
            const valA = (a[orderBy] || '').toString().toLowerCase();
            const valB = (b[orderBy] || '').toString().toLowerCase();
            if (valA < valB) return order === 'asc' ? -1 : 1;
            if (valA > valB) return order === 'asc' ? 1 : -1;
            return 0;
        });
    }, [quarterTPs, order, orderBy]);

    // Calculate Summary Stats
    const summaryStats = React.useMemo(() => {
        const total = quarterTPs.length;
        let techCount = 0;
        let icrCount = 0;
        let projectCount = 0;
        let otherCount = 0;

        quarterTPs.forEach(tp => {
            const type = tp.project_type;
            if (type === 'Tech') techCount++;
            else if (type === 'ICR') icrCount++;
            else if (type === 'Project') projectCount++;
            else otherCount++; // 'Other' or empty
        });

        return { total, techCount, icrCount, projectCount, otherCount };
    }, [quarterTPs]);

    const chartOptions = {
        chart: {
            type: 'column',
            backgroundColor: 'transparent',
            spacingBottom: 30,
            spacingLeft: 20
        },
        title: {
            text: 'Closed TP Count',
            style: { fontSize: '14px' }
        },
        xAxis: {
            categories: stats?.categories || [],
            crosshair: true,
            labels: {
                style: { fontSize: '11px' }
            }
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Count'
            },
            allowDecimals: false
        },
        tooltip: {
            shared: true
        },
        plotOptions: {
            column: {
                cursor: 'pointer', // Show functionality
                pointPadding: 0.2,
                borderWidth: 0,
                dataLabels: { enabled: true },
                events: {
                    click: handleBarClick
                }
            }
        },
        series: [{
            name: 'Closed',
            data: stats?.data || [],
            color: '#4caf50'
        }],
        credits: { enabled: false }
    };

    const icrChartOptions = {
        chart: {
            type: 'column',
            backgroundColor: 'transparent',
            spacingBottom: 30,
            spacingLeft: 20
        },
        title: {
            text: 'ICR Count Overview',
            style: { fontSize: '14px' }
        },
        xAxis: {
            categories: stats?.categories || [],
            crosshair: true,
            labels: {
                style: { fontSize: '11px' }
            }
        },
        yAxis: {
            min: 0,
            title: {
                text: 'ICR Count'
            },
            allowDecimals: false
        },
        tooltip: {
            shared: true
        },
        plotOptions: {
            column: {
                pointPadding: 0.2,
                borderWidth: 0,
                dataLabels: { enabled: true }
            }
        },
        series: [{
            name: 'ICR Count',
            data: stats?.icr_data || [],
            color: '#ff9800'
        }],
        credits: { enabled: false }
    };


    const headCells = [
        { id: 'ticket_number', label: 'Ticket No' },
        { id: 'title', label: 'Title' },
        { id: 'department', label: 'Department' },
        { id: 'project_type', label: 'Type' },
        { id: 'project_manager', label: 'Manager' },
        { id: 'released_date', label: 'Released Date' },
    ];

    return (
        <Box sx={{ width: '100%', p: 3 }} bgcolor="#f5f5f5" minHeight="100vh" >
            <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold', color: '#1a237e' }}>
                    Dashboard
                </Typography>
                <Box sx={{ minWidth: 250 }}>
                    <DepartmentSelector
                        label="Filter Department"
                        value={department}
                        onChange={(newVal) => setDepartment(newVal || "ALL")}
                        freeSolo
                    />
                </Box>
            </Box>

            {loading && <LinearProgress sx={{ mb: 2 }} />}
            {error && <Typography color="error" sx={{ mb: 2 }}>{error}</Typography>}

            <Grid container spacing={3}>
                <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                    <Paper elevation={2} sx={{ p: 2, height: '400px', display: 'flex', flexDirection: 'column', borderRadius: 2 }}>
                        <Typography variant="h6" gutterBottom sx={{ fontSize: '1rem', fontWeight: 600 }}>
                            Performance Overview
                        </Typography>
                        <Box sx={{ flexGrow: 1, minHeight: 0 }}>
                            {stats && (
                                <HighchartsReact
                                    highcharts={Highcharts}
                                    options={chartOptions}
                                    containerProps={{ style: { height: "100%" } }}
                                />
                            )}
                        </Box>
                    </Paper>
                </Grid>

                {/* Placeholders */}
                <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                    <Paper elevation={2} sx={{ p: 2, height: '400px', display: 'flex', flexDirection: 'column', borderRadius: 2 }}>
                        <Typography variant="h6" gutterBottom sx={{ fontSize: '1rem', fontWeight: 600 }}>
                            ICR Count Overview
                        </Typography>
                        <Box sx={{ flexGrow: 1, minHeight: 0 }}>
                            {stats && (
                                <HighchartsReact
                                    highcharts={Highcharts}
                                    options={icrChartOptions}
                                    containerProps={{ style: { height: "100%" } }}
                                />
                            )}
                        </Box>
                    </Paper>
                </Grid>
                <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                    <Paper elevation={0} sx={{ p: 2, height: '320px', bgcolor: 'transparent', border: '2px dashed #e0e0e0', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 2 }}>
                        <Typography color="text.secondary">Empty Slot</Typography>
                    </Paper>
                </Grid>
                <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                    <Paper elevation={0} sx={{ p: 2, height: '320px', bgcolor: 'transparent', border: '2px dashed #e0e0e0', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 2 }}>
                        <Typography color="text.secondary">Empty Slot</Typography>
                    </Paper>
                </Grid>
            </Grid>

            {/* Drill-down Modal */}
            <Dialog open={modalOpen} onClose={handleCloseModal} maxWidth="md" fullWidth>
                <DialogTitle>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="h6">Closed TPs - {selectedQuarter}</Typography>
                        <Box>
                            <Button
                                variant="outlined"
                                startIcon={<DownloadIcon />}
                                onClick={handleExportCSV}
                                sx={{ mr: 2 }}
                                disabled={!quarterTPs.length}
                            >
                                Export CSV
                            </Button>
                            <IconButton onClick={handleCloseModal}>
                                <CloseIcon />
                            </IconButton>
                        </Box>
                    </Box>
                </DialogTitle>
                <DialogContent dividers>
                    {modalLoading ? (
                        <LinearProgress />
                    ) : (
                        <Box>
                            {/* Summary Header */}
                            <Paper elevation={0} variant="outlined" sx={{ p: 2, mb: 2, bgcolor: '#f8f9fa' }}>
                                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                                    Total Closed TP Count: {summaryStats.total}
                                </Typography>
                                <Grid container spacing={2}>
                                    <Grid item xs={6} sm={3}>
                                        <Typography variant="body2" color="text.secondary">Closed Tech TP:</Typography>
                                        <Typography variant="h6" color="primary">{summaryStats.techCount}</Typography>
                                    </Grid>
                                    <Grid item xs={6} sm={3}>
                                        <Typography variant="body2" color="text.secondary">Closed Tech ICR:</Typography>
                                        <Typography variant="h6" color="primary">{summaryStats.icrCount}</Typography>
                                    </Grid>
                                    <Grid item xs={6} sm={3}>
                                        <Typography variant="body2" color="text.secondary">Closed Tech Project:</Typography>
                                        <Typography variant="h6" color="primary">{summaryStats.projectCount}</Typography>
                                    </Grid>
                                    <Grid item xs={6} sm={3}>
                                        <Typography variant="body2" color="text.secondary">Closed Tech Other:</Typography>
                                        <Typography variant="h6" color="primary">{summaryStats.otherCount}</Typography>
                                    </Grid>
                                </Grid>
                            </Paper>

                            {/* TP List Table */}
                            <TableContainer component={Paper} elevation={1} sx={{ maxHeight: 800 }}>
                                <Table stickyHeader size="small">
                                    <TableHead>
                                        <TableRow>
                                            {headCells.map((headCell) => (
                                                <TableCell
                                                    key={headCell.id}
                                                    sortDirection={orderBy === headCell.id ? order : false}
                                                >
                                                    <TableSortLabel
                                                        active={orderBy === headCell.id}
                                                        direction={orderBy === headCell.id ? order : 'asc'}
                                                        onClick={() => handleRequestSort(headCell.id)}
                                                    >
                                                        {headCell.label}
                                                    </TableSortLabel>
                                                </TableCell>
                                            ))}
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {sortedTPs.length > 0 ? (
                                            sortedTPs.map((tp) => (
                                                <TableRow key={tp.id} hover>
                                                    <TableCell sx={{ whiteSpace: 'nowrap' }}>
                                                        <a href={`https://jira.tc-gaming.co/jira/browse/${tp.ticket_number}`} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none', color: '#1976d2', fontWeight: 500 }}>
                                                            {tp.ticket_number}
                                                        </a>
                                                    </TableCell>
                                                    <TableCell>{tp.title}</TableCell>
                                                    <TableCell>{tp.department}</TableCell>
                                                    <TableCell>{tp.project_type}</TableCell>
                                                    <TableCell>{tp.project_manager}</TableCell>
                                                    <TableCell>{tp.released_date ? new Date(tp.released_date).toLocaleDateString() : '-'}</TableCell>
                                                </TableRow>
                                            ))
                                        ) : (
                                            <TableRow>
                                                <TableCell colSpan={6} align="center">No TPs found for this quarter.</TableCell>
                                            </TableRow>
                                        )}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        </Box>
                    )}
                </DialogContent>
            </Dialog>
        </Box >
    );
}

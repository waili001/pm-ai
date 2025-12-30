
import React, { useState, useEffect, useMemo } from 'react';
import {
    Box,
    Paper,
    Typography,
    MenuItem,
    Select,
    FormControl,
    InputLabel,
    ToggleButton,
    ToggleButtonGroup,
    Grid,
    Card,
    CardContent,
    Chip,
    Autocomplete,
    TextField,
    Stack,
    Link
} from '@mui/material';
import {
    ViewKanban,
    ViewTimeline,
    Event as EventIcon
} from '@mui/icons-material';

import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';
import Xrange from 'highcharts/modules/xrange';

// Helper to format due day
const formatDueDay = (val) => {
    if (!val) return null;
    // If it's a long timestamp number string
    if (!isNaN(val) && val.toString().length > 10) {
        return new Date(parseInt(val)).toLocaleDateString();
    }
    return val;
};

// Initialize Highcharts module
// Fix for "Xrange is not a function" (ESM/CJS interop)
try {
    if (typeof Xrange === "function") {
        Xrange(Highcharts);
    } else if (Xrange && typeof Xrange.default === "function") {
        Xrange.default(Highcharts);
    } else {
        console.warn("Could not find Xrange function in module:", Xrange);
    }
} catch (e) {
    console.error("Failed to load Highcharts Xrange module", e);
}

const KANBAN_COLUMNS = [
    "Open",
    "In Review",
    "Action Needed",
    "In Progress",
    "Resolved",
    "Closed"
];

const PROJECT_TYPES = ["ALL", "Tech", "Integration", "ICR", "Project"];

export default function ProjectPlanning() {
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(false);

    // Filters
    // Read initial state from localStorage or default
    const [program, setProgram] = useState(() => localStorage.getItem('planning_program') || "ALL");
    const [department, setDepartment] = useState(() => localStorage.getItem('planning_department') || "ALL");
    const [projectType, setProjectType] = useState(() => localStorage.getItem('planning_project_type') || "ALL");
    const [viewMode, setViewMode] = useState("KANBAN"); // KANBAN or GANTT

    // Data Lists
    const [programsList, setProgramsList] = useState([]);
    const [departmentsList, setDepartmentsList] = useState([]);

    // Fetch filters options on mount
    useEffect(() => {
        // Fetch Departments
        fetch('http://127.0.0.1:8000/api/project/departments')
            .then(res => res.json())
            .then(data => {
                setDepartmentsList(["ALL", ...data]);
            })
            .catch(err => console.error("Error fetching departments:", err));

        // Fetch Programs
        fetch('http://127.0.0.1:8000/api/project/programs')
            .then(res => res.json())
            .then(data => {
                setProgramsList(["ALL", ...data]);
            })
            .catch(err => console.error("Error fetching programs:", err));
    }, []);

    // Persistence Effect
    useEffect(() => {
        if (program) localStorage.setItem('planning_program', program);
        if (department) localStorage.setItem('planning_department', department);
        if (projectType) localStorage.setItem('planning_project_type', projectType);
    }, [program, department, projectType]);

    const fetchProjects = () => {
        setLoading(true);
        const params = new URLSearchParams();

        // Pass "ALL" if selected, backend will handle or ignore it. 
        // Or safer: pass empty if "ALL". 
        // Backend implementation plan says backend will handle "ALL", so we can pass it directly 
        // or filter it out here. Let's pass it so backend sees explicit user intent if needed, 
        // OR pass nothing if "ALL" to keep URL clean?
        // Let's pass it because backend `project.py` updated to check `department != "ALL"`.
        if (program && program !== "ALL") params.append("program", program);
        if (department && department !== "ALL") params.append("department", department);
        if (projectType && projectType !== "ALL") params.append("project_type", projectType);

        fetch(`http://127.0.0.1:8000/api/project/planning?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                setProjects(data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Error fetching projects:", err);
                setLoading(false);
            });
    };

    useEffect(() => {
        fetchProjects();
    }, [program, department, projectType]);

    const handleViewChange = (event, newView) => {
        if (newView !== null) {
            setViewMode(newView);
        }
    };

    // --- Kanban View Components ---
    const KanbanBoard = () => {
        // Group projects by status
        const grouped = useMemo(() => {
            const groups = {};
            KANBAN_COLUMNS.forEach(col => groups[col] = []);

            projects.forEach(p => {
                const status = p.status || "Open"; // Default to Open if unknown or map logic?
                // Exact match check from existing Columns
                if (groups[status]) {
                    groups[status].push(p);
                } else {
                    if (groups["Open"]) {
                        groups["Open"].push(p);
                    }
                }
            });
            return groups;
        }, [projects]);

        return (
            <Box sx={{ overflowX: 'auto', height: 'calc(100vh - 200px)', pb: 2 }}>
                <Stack direction="row" spacing={2} sx={{ minWidth: 'fit-content', height: '100%' }}>
                    {KANBAN_COLUMNS.map(col => (
                        <Paper key={col} sx={{ width: 300, minWidth: 300, bgcolor: '#f5f5f5', display: 'flex', flexDirection: 'column' }}>
                            <Box sx={{ p: 2, borderBottom: '1px solid #ddd', bgcolor: '#e0e0e0' }}>
                                <Typography variant="subtitle1" fontWeight="bold">
                                    {col} ({grouped[col]?.length || 0})
                                </Typography>
                            </Box>
                            <Box sx={{ p: 1, overflowY: 'auto', flexGrow: 1 }}>
                                {grouped[col]?.map(project => (
                                    <Card key={project.id} sx={{ mb: 1 }}>
                                        <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 0.5 }}>
                                                <Typography variant="subtitle2" color="primary" sx={{ fontWeight: 'bold', zIndex: 10, position: 'relative' }}>
                                                    <Link
                                                        href={`https://jira.tc-gaming.co/jira/browse/${project.ticket_number}`}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        onClick={(e) => e.stopPropagation()}
                                                        underline="hover"
                                                        color="inherit"
                                                    >
                                                        {project.ticket_number}
                                                    </Link>
                                                </Typography>
                                                {/* Assuming project_type as issue type equivalent for now */}
                                                <Chip
                                                    label={project.project_type || "Project"}
                                                    size="small"
                                                    color="secondary"
                                                    sx={{ fontSize: '0.65rem', height: 18 }}
                                                />
                                            </Box>
                                            <Typography variant="body2" sx={{ mb: 1, lineHeight: 1.3 }}>
                                                {project.title}
                                            </Typography>
                                            {/* Due Day */}
                                            {project.due_day && (
                                                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1, color: 'text.secondary' }}>
                                                    <EventIcon sx={{ fontSize: 14, mr: 0.5 }} />
                                                    <Typography variant="caption" sx={{ fontSize: '0.7rem' }}>
                                                        {formatDueDay(project.due_day)}
                                                    </Typography>
                                                </Box>
                                            )}

                                            <Stack direction="row" justifyContent="space-between" alignItems="center">
                                                <Chip
                                                    label={project.project_manager || "No PM"}
                                                    size="small"
                                                    variant="outlined"
                                                    sx={{ fontSize: '0.7rem', height: 20 }}
                                                />
                                                <Typography variant="caption" color="text.secondary">
                                                    {project.department}
                                                </Typography>
                                            </Stack>
                                        </CardContent>
                                    </Card>
                                ))}
                            </Box>
                        </Paper>
                    ))}
                </Stack>
            </Box>
        );
    };

    // --- Gantt View Components ---
    const GanttChart = () => {
        // Filter: Only "In Progress"
        // Data prep for Highcharts Xrange
        const ganttData = useMemo(() => {
            return projects
                .filter(p => p.status === "In Progress")
                .map((p, index) => {
                    // Logic to determine start/end
                    // due_day_quarter / released_month are all we have.
                    // Fallback to now -> +1 month if null?

                    // Mock dates for visualization if real data is missing
                    // Use a hash of ID to generate deterministic pseudo-random dates within a range?
                    // Better: Use start of current month as default start, and try to parse `due_day_quarter`.

                    const now = new Date().getTime();
                    let start = now;
                    let end = now + (30 * 24 * 3600 * 1000); // +30 days default

                    return {
                        x: start,
                        x2: end,
                        y: index,
                        name: p.title,
                        ticket: p.ticket_number,
                        manager: p.project_manager
                    };
                });
        }, [projects]);

        const options = {
            chart: {
                type: 'xrange',
                height: Math.max(400, ganttData.length * 50 + 100)
            },
            title: { text: null },
            xAxis: {
                type: 'datetime'
            },
            yAxis: {
                title: { text: '' },
                categories: ganttData.map(d => d.ticket),
                reversed: true
            },
            series: [{
                name: 'Projects',
                pointPadding: 0,
                groupPadding: 0,
                borderColor: 'gray',
                pointWidth: 20,
                data: ganttData,
                dataLabels: {
                    enabled: true,
                    formatter: function () {
                        return this.point.name; // Show Title on bar
                    },
                    style: {
                        fontSize: '10px',
                        fontWeight: 'normal',
                        textOutline: 'none'
                    }
                }
            }],
            tooltip: {
                formatter: function () {
                    return '<b>' + this.point.ticket + '</b><br />' +
                        this.point.name + '<br />' +
                        'PM: ' + this.point.manager;
                }
            }
        };

        return (
            <Box sx={{ p: 2 }}>
                {ganttData.length === 0 ? (
                    <Typography>No "In Progress" projects to display.</Typography>
                ) : (
                    <HighchartsReact
                        highcharts={Highcharts}
                        options={options}
                    />
                )}
            </Box>
        );
    };

    return (
        <Box sx={{ p: 3, height: '100%' }}>
            {/* Header / Filters */}
            <Paper sx={{ p: 2, mb: 3 }}>
                <Grid container spacing={2} alignItems="center">
                    {/* Program Filter - 1st Position */}
                    <Grid size={{ xs: 12, md: 1 }}>
                        <Box sx={{ minWidth: 100, maxWidth: 200 }}>
                            <Autocomplete
                                options={programsList}
                                renderInput={(params) => <TextField {...params} label="Program" />}
                                value={program}
                                onChange={(e, newVal) => setProgram(newVal)}
                                freeSolo
                            />
                        </Box>
                    </Grid>

                    {/* Department Filter - 2nd Position */}
                    <Grid size={{ xs: 12, md: 1 }}>
                        <Box sx={{ minWidth: 100, maxWidth: 200 }}>
                            <Autocomplete
                                options={departmentsList}
                                renderInput={(params) => <TextField {...params} label="Department" />}
                                value={department}
                                onChange={(e, newVal) => setDepartment(newVal)}
                                freeSolo
                            />
                        </Box>
                    </Grid>

                    {/* Project Type Filter - 3rd Position */}
                    <Grid size={{ xs: 12, md: 1 }}>
                        <FormControl fullWidth sx={{ minWidth: 100, maxWidth: 200 }}>
                            <InputLabel>Project Type</InputLabel>
                            <Select
                                value={projectType}
                                label="Project Type"
                                onChange={(e) => setProjectType(e.target.value)}
                            >
                                <MenuItem value="ALL">ALL</MenuItem>
                                <MenuItem value="Tech">Tech</MenuItem>
                                <MenuItem value="Integration">Integration</MenuItem>
                                <MenuItem value="ICR">ICR</MenuItem>
                                <MenuItem value="Project">Project</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>

                    <Grid size={{ xs: 12, md: 2 }} sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                        <ToggleButtonGroup
                            value={viewMode}
                            exclusive
                            onChange={handleViewChange}
                            aria-label="view mode"
                        >
                            <ToggleButton value="KANBAN" aria-label="kanban view">
                                <ViewKanban sx={{ mr: 1 }} /> Kanban
                            </ToggleButton>
                            <ToggleButton value="GANTT" aria-label="gantt view">
                                <ViewTimeline sx={{ mr: 1 }} /> Gantt
                            </ToggleButton>
                        </ToggleButtonGroup>
                    </Grid>
                </Grid>
            </Paper>

            {/* Content Content - Depends on View Mode */}
            {viewMode === 'KANBAN' ? (
                <KanbanBoard />
            ) : (
                <GanttChart />
            )}
        </Box>
    );
}

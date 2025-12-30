
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
    Link,
    LinearProgress
} from '@mui/material';
import {
    ViewKanban,
    ViewTimeline,
    Event as EventIcon
} from '@mui/icons-material';

import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';
import Xrange from 'highcharts/modules/xrange';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';

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
        fetch('/api/project/departments')
            .then(res => res.json())
            .then(data => {
                setDepartmentsList(["ALL", ...data]);
            })
            .catch(err => console.error("Error fetching departments:", err));

        // Fetch Programs
        fetch('/api/project/programs')
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

        fetch(`/api/project/planning?${params.toString()}`)
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

        const onDragEnd = async (result) => {
            const { source, destination, draggableId } = result;

            // Dropped outside or no change
            if (!destination) return;
            if (
                source.droppableId === destination.droppableId &&
                source.index === destination.index
            ) {
                return;
            }

            // Only allow same column reordering for now as per requirement
            if (source.droppableId !== destination.droppableId) {
                return;
            }

            const status = source.droppableId;
            const items = Array.from(grouped[status] || []);
            const [reorderedItem] = items.splice(source.index, 1);
            items.splice(destination.index, 0, reorderedItem);

            // Optimistic update
            const newOrderIds = items.map(p => p.id);

            // Update sort_order on the reordered items for consistency
            const reorderedItemsWithSort = items.map((p, idx) => ({
                ...p,
                sort_order: idx
            }));

            // Filter out the items that are part of the current reordered group using ID check
            // Use Set for O(1) lookups if list is large, but array includes is fine here
            const otherProjects = projects.filter(p => !newOrderIds.includes(p.id));

            // Combine others + reordered items
            // Note: This changes the global order of 'projects', putting modified status at the end.
            // But since 'grouped' iterates 'projects' to fill buckets, and buckets are rendered independently,
            // the relative order within the bucket is what matters. This guarantees it.
            const newProjects = [...otherProjects, ...reorderedItemsWithSort];

            setProjects(newProjects);

            // Call API in background
            fetch('/api/project/reorder', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    status: status,
                    project_ids: newOrderIds
                })
            }).catch(error => {
                console.error("Failed to reorder:", error);
                // Optionally revert state here if needed
            });
        };

        return (
            <DragDropContext onDragEnd={onDragEnd}>
                <Box sx={{ overflowX: 'auto', pb: 2 }}>
                    <Stack direction="row" spacing={2} sx={{ minWidth: 'fit-content', height: '100%' }}>
                        {KANBAN_COLUMNS.map(col => (
                            <Droppable key={col} droppableId={col}>
                                {(provided) => (
                                    <Paper
                                        ref={provided.innerRef}
                                        {...provided.droppableProps}
                                        sx={{ width: 300, minWidth: 300, bgcolor: '#f5f5f5', display: 'flex', flexDirection: 'column' }}
                                    >
                                        <Box sx={{ p: 2, borderBottom: '1px solid #ddd', bgcolor: '#e0e0e0' }}>
                                            <Typography variant="subtitle1" fontWeight="bold">
                                                {col} ({grouped[col]?.length || 0})
                                            </Typography>
                                        </Box>
                                        <Box sx={{ p: 1, overflowY: 'auto', flexGrow: 1 }}>
                                            {grouped[col]?.map((project, index) => (
                                                <Draggable key={project.id} draggableId={project.id.toString()} index={index}>
                                                    {(provided, snapshot) => (
                                                        <Card
                                                            ref={provided.innerRef}
                                                            {...provided.draggableProps}
                                                            {...provided.dragHandleProps}
                                                            sx={{
                                                                mb: 1,
                                                                // Highlight styles when dragging
                                                                backgroundColor: snapshot.isDragging ? '#e3f2fd' : 'background.paper',
                                                                border: snapshot.isDragging ? '2px solid #2196f3' : 'none',
                                                                boxShadow: snapshot.isDragging ? 6 : 1,
                                                                transition: 'background-color 0.2s ease, box-shadow 0.2s ease',
                                                                ...provided.draggableProps.style
                                                            }}
                                                        >
                                                            <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                                                                {/* ... Content ... */}
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

                                                                {/* Completed Percentage */}
                                                                {typeof project.completed_percentage === 'number' && (
                                                                    <Box sx={{ mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                                                                        <Box sx={{ width: '100%', mr: 1 }}>
                                                                            <LinearProgress
                                                                                variant="determinate"
                                                                                value={project.completed_percentage}
                                                                                sx={{ height: 6, borderRadius: 3 }}
                                                                            />
                                                                        </Box>
                                                                        <Box sx={{ minWidth: 35 }}>
                                                                            <Typography variant="caption" color="text.secondary">
                                                                                {`${Math.round(project.completed_percentage)}%`}
                                                                            </Typography>
                                                                        </Box>
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
                                                    )}
                                                </Draggable>
                                            ))}
                                            {provided.placeholder}
                                        </Box>
                                    </Paper>
                                )}
                            </Droppable>
                        ))}
                    </Stack>
                </Box>
            </DragDropContext>
        );
    };

    // --- Gantt View Components ---
    // --- Gantt View Components ---
    const GanttChart = () => {

        // Helper to parse date to timestamp
        const getTimestamp = (val) => {
            if (!val) return null;
            if (typeof val === 'number') return val;
            if (!isNaN(val) && val.toString().length > 10) return parseInt(val);
            const d = new Date(val);
            if (!isNaN(d.getTime())) return d.getTime();
            return null;
        };

        // Filter: Only "In Progress"
        // Data prep for Highcharts Xrange
        const ganttData = useMemo(() => {
            const now = new Date().getTime();

            // 1. Filter and Prepare raw data with calculated dates
            const prepared = projects
                .filter(p => p.status === "In Progress")
                .map(p => {
                    let start = getTimestamp(p.start_date);
                    let end = getTimestamp(p.due_day);

                    // Fallbacks
                    if (!start && !end) {
                        start = now;
                        end = now + (30 * 24 * 3600 * 1000); // 30 days
                    } else if (!start) {
                        start = end - (30 * 24 * 3600 * 1000);
                    } else if (!end) {
                        end = start + (30 * 24 * 3600 * 1000);
                    }

                    if (start > end) {
                        // Swap if inverted
                        const temp = start;
                        start = end;
                        end = temp;
                    }

                    return {
                        ...p,
                        _start: start,
                        _end: end
                    };
                });

            // 2. Sort by Due Day (End Date) Ascending
            prepared.sort((a, b) => a._end - b._end);

            // 3. Map to Highcharts format with corrected index y
            return prepared.map((p, index) => ({
                x: p._start,
                x2: p._end,
                y: index,
                name: p.title,
                ticket: p.ticket_number,
                manager: p.project_manager
            }));
        }, [projects]);

        const options = {
            chart: {
                type: 'xrange',
                height: Math.max(400, ganttData.length * 50 + 100)
            },
            title: { text: null },
            xAxis: {
                type: 'datetime',
                plotLines: [{
                    color: '#FF0000',
                    width: 2,
                    value: new Date().getTime(),
                    dashStyle: 'Dash',
                    zIndex: 5
                }]
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
                        return this.point.name;
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
                        'PM: ' + this.point.manager + '<br/>' +
                        'Start: ' + Highcharts.dateFormat('%Y-%m-%d', this.point.x) + '<br/>' +
                        'Due: ' + Highcharts.dateFormat('%Y-%m-%d', this.point.x2);
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
                    <Grid size={{ xs: 12, md: 2 }}>
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

import React, { useState, useEffect } from 'react';
import { Autocomplete, TextField } from '@mui/material';
import { authenticatedFetch } from '../utils/api';

export default function DepartmentSelector({
    value,
    onChange,
    label = "Select Department",
    showAll = true,
    helperText,
    ...props
}) {
    const [departments, setDepartments] = useState([]);

    useEffect(() => {
        authenticatedFetch('/api/project/departments')
            .then(res => res.json())
            .then(data => {
                if (showAll) {
                    setDepartments(["ALL", ...data]);
                } else {
                    setDepartments(data);
                }
            })
            .catch(err => console.error("Error fetching departments:", err));
    }, [showAll]);

    return (
        <Autocomplete
            options={departments}
            value={value}
            onChange={(event, newValue) => {
                onChange(newValue);
            }}
            renderInput={(params) => (
                <TextField
                    {...params}
                    label={label}
                    variant="outlined"
                    helperText={helperText}
                />
            )}
            {...props}
        />
    );
}

import React, { useState } from 'react';
import api from '../../api';
import { toast } from 'react-toastify';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

const ChangePasswordForm = () => {
    const [oldPassword, setOldPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmNewPassword, setConfirmNewPassword] = useState('');
    const [errors, setErrors] = useState({});

    const validatePassword = (password) => {
        const errors = [];
        if (password.length < 8) {
            errors.push("Password must be at least 8 characters long");
        }
        if (!/[A-Z]/.test(password)) {
            errors.push("Password must contain at least one uppercase letter");
        }
        if (!/[a-z]/.test(password)) {
            errors.push("Password must contain at least one lowercase letter");
        }
        if (!/[0-9]/.test(password)) {
            errors.push("Password must contain at least one number");
        }
        return errors;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrors({});

        const newPasswordErrors = validatePassword(newPassword);
        if (newPasswordErrors.length > 0) {
            setErrors({ newPassword: newPasswordErrors });
            newPasswordErrors.forEach(err => toast.error(err));
            return;
        }

        if (newPassword !== confirmNewPassword) {
            setErrors({ confirmNewPassword: ['New passwords do not match.'] });
            toast.error('New passwords do not match.');
            return;
        }

        try {
            const response = await api.post('/api/change-password/', {
                old_password: oldPassword,
                new_password: newPassword,
            });

            if (response.status === 200) {
                toast.success('Password changed successfully!');
                setOldPassword('');
                setNewPassword('');
                setConfirmNewPassword('');
            }
        } catch (error) {
            if (error.response && error.response.status === 400) {
                const { detail, errors, password_requirements } = error.response.data;

                if (errors) {
                    errors.forEach(err => toast.error(err));
                    setErrors({ server: errors });
                } else if (detail) {
                    toast.error(detail);
                    setErrors({ server: [detail] });
                }

                if (password_requirements) {
                    password_requirements.forEach(requirement => toast.info(requirement));
                }
            } else {
                toast.error('Password change failed. Please try again.');
                setErrors({ server: ['An unexpected error occurred. Please try again.'] });
            }
        }
    };

    return (
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2, maxWidth: 400, mx: 'auto' }}>
            <TextField
                label="Old Password"
                type="password"
                value={oldPassword}
                onChange={(e) => setOldPassword(e.target.value)}
                fullWidth
                margin="normal"
                required
                size='small'
                error={!!errors.oldPassword}
                helperText={errors.oldPassword && errors.oldPassword[0]}
            />
            <TextField
                label="New Password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                fullWidth
                margin="normal"
                required
                size='small'
                error={!!errors.newPassword}
                helperText={errors.newPassword && errors.newPassword[0]}
            />
            <TextField
                label="Confirm New Password"
                type="password"
                value={confirmNewPassword}
                onChange={(e) => setConfirmNewPassword(e.target.value)}
                fullWidth
                margin="normal"
                required
                size='small'
                error={!!errors.confirmNewPassword}
                helperText={errors.confirmNewPassword && errors.confirmNewPassword[0]}
            />
            {errors.server && (
                <Typography color="error" variant="body2" sx={{ mt: 1 }}>
                    {errors.server.map((err, index) => (
                        <div key={index}>{err}</div>
                    ))}
                </Typography>
            )}
            <Button
                type="submit"
                variant="contained"
                color="primary"
                style={{
                    backgroundColor: "#135D66",
                }}
                fullWidth
                sx={{ mt: 2 }}
            >
                Change Password
            </Button>
        </Box>
    );
};

export default ChangePasswordForm;
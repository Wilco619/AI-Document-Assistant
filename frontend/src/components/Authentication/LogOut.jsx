import React from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api';
import Button from '@mui/material/Button';
import LogoutIcon from '@mui/icons-material/Logout';
import { ACCESS_TOKEN, REFRESH_TOKEN } from '../../constants';

const LogOut = () => {
    const navigate = useNavigate();

    const handleLogout = async () => {
        try {
            // Get the current refresh token from localStorage
            const refreshToken = localStorage.getItem(REFRESH_TOKEN);
            console.log("Attempting logout...");

            if (refreshToken) {
                // Blacklist the current refresh token on the server
                await api.post('/api/logout/', { refresh: refreshToken });
                console.log("Token blacklisted successfully");
            } else {
                console.log("No refresh token found.");
            }

            // Clear tokens from localStorage
            localStorage.removeItem(ACCESS_TOKEN);
            localStorage.removeItem(REFRESH_TOKEN);

            // Navigate to the login page
            navigate('/');
            console.log("Navigating to login page");
        } catch (error) {
            console.error('Logout failed:', error.response?.data || error.message);

            // Even if the server request fails, clear local storage and redirect
            localStorage.removeItem(ACCESS_TOKEN);
            localStorage.removeItem(REFRESH_TOKEN);
            navigate('/');
            console.log("Logout failed, but tokens cleared and navigating to login page");
        }
    };

    return (
        <Button
            fullWidth={true}
            size='small'
            variant="outlined"
            onClick={handleLogout}
            startIcon={<LogoutIcon />}
        >
            LogOut
        </Button>
    );
};

export default LogOut;
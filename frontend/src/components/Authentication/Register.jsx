import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast, ToastContainer } from 'react-toastify';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Link,
  Grid,
  Avatar,
  CssBaseline
} from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import api from '../../api';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '' // Changed from confirmPassword to match backend
  });
  
  const [errors, setErrors] = useState({});
  const [isButtonActive, setIsButtonActive] = useState(false);
  const navigate = useNavigate();
  
  useEffect(() => {
    const isFormComplete = 
      formData.username.trim() !== '' &&
      formData.email.trim() !== '' &&
      formData.password.trim() !== '' &&
      formData.password_confirm.trim() !== '' &&
      formData.password === formData.password_confirm;
      
    setIsButtonActive(isFormComplete);
  }, [formData]);
  
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters long';
    }
    
    if (formData.password !== formData.password_confirm) {
      newErrors.password_confirm = 'Passwords do not match';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    // Send all form data including password_confirm
    try {
      const response = await api.post('/api/register/', formData);
      navigate('/verify-otp', { state: { userId: response.data.user_id } });
      toast.success('Registration successful. Please verify your email.');
    } catch (error) {
      if (error.response?.data) {
        const errorDetails = error.response.data.details;
        if (typeof errorDetails === 'object') {
          // Handle field-specific errors
          Object.entries(errorDetails).forEach(([field, messages]) => {
            setErrors(prev => ({
              ...prev,
              [field]: Array.isArray(messages) ? messages[0] : messages
            }));
          });
          toast.error('Please correct the errors in the form.');
        } else {
          toast.error(`Registration failed: ${error.response.data.error}`);
        }
      } else {
        toast.error('Registration failed. Please try again.');
      }
    }
  };
  
  return (
    <Container component="main" maxWidth="xs">
      <CssBaseline />
      <Box
        sx={{
          mt: 8,
          mb: 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center'
        }}
      >
        <Avatar sx={{ m: 1, bgcolor: 'primary.main' }}>
          <LockOutlinedIcon />
        </Avatar>
        
        <Typography component="h1" variant="h5">
          Sign Up
        </Typography>
        
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                name="username"
                required
                fullWidth
                label="Username"
                autoFocus
                value={formData.username}
                onChange={handleChange}
                error={!!errors.username}
                helperText={errors.username}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                name="email"
                required
                fullWidth
                label="Email Address"
                type="email"
                value={formData.email}
                onChange={handleChange}
                error={!!errors.email}
                helperText={errors.email}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                name="password"
                required
                fullWidth
                label="Password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                error={!!errors.password}
                helperText={errors.password}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                name="password_confirm"
                required
                fullWidth
                label="Confirm Password"
                type="password"
                value={formData.password_confirm}
                onChange={handleChange}
                error={!!errors.password_confirm}
                helperText={errors.password_confirm}
              />
            </Grid>
          </Grid>
          
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={!isButtonActive}
          >
            Sign Up
          </Button>
          
          <Grid container justifyContent="flex-end">
            <Grid item>
              <Link href="/login" variant="body2">
                Already have an account? Sign in
              </Link>
            </Grid>
          </Grid>
        </Box>
      </Box>
      
      <Box sx={{ mt: 4, mb: 4, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          {'Copyright © '}
          {new Date().getFullYear()}
          {'. All rights reserved.'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          V<strong>1.0</strong>
        </Typography>
      </Box>
      
      <ToastContainer />
    </Container>
  );
};

export default Register;
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import App from './components/App';
import './index.css';
import Login from './components/Authentication/Login';
import Users from './components/Pages/Users';
import Dashboard from './components/Pages/Dashboard';
import ErrorPage from './components/ErrorPage';
import OTPform from './components/Authentication/OTPform';
import AdminRegistrationForm from './components/Authentication/AdminReg';
import AddUser from './components/Pages/AddUser';
import ChangePasswordForm from './components/Authentication/ChangePassword';
import Settings from './components/Authentication/Settings';
import UploadDoc from './components/Pages/Upload';
import DocumentUpload from './components/Authentication/UploadDocuments';
import Register from './components/Authentication/Register';

const Main = () => {
  

  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Login />} />
        <Route path="/verify-otp" element={<OTPform />} />
        <Route path="/register" element={<Register />} />

        {/* Private Routes */}
        
          <Route path="/home" element={<App />}>
            <Route index element={<Navigate to="dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
              <Route path="upload" element={<UploadDoc />}>
                <Route path="DocumentUpload" element={<DocumentUpload />} />
                
              </Route>
            <Route path="users" element={<Users />}>
              <Route path="Registration" element={<AddUser />}>
                
                <Route path="AdminReg" element={<AdminRegistrationForm />} />
                
              </Route>
              
            </Route>
            
            <Route path="settings" element={<Settings />}>
              <Route path="change-password" element={<ChangePasswordForm />} />
            </Route>
          </Route>
        
        {/* Fallback Route */}
        <Route path="*" element={<ErrorPage />} />
      </Routes>
    </Router>
  );
};

const rootElement = document.getElementById('root');
if (rootElement) {
  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <Main />
    </React.StrictMode>
  );
} else {
  console.error('Root element not found');
}

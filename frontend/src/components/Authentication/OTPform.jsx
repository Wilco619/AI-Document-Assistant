import "./Login.css";
import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { toast, ToastContainer } from 'react-toastify';
import api from "../../api";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../../constants";  // Import the constants

const OTPform = () => {
    const [otp, setOtp] = useState('');
    const [isButtonActive, setIsButtonActive] = useState(false);
    const location = useLocation();
    const navigate = useNavigate();
    const userId = location.state?.userId;  // Access userId from location state

    useEffect(() => {
        // Enable the button only if OTP field is not empty
        setIsButtonActive(otp.trim() !== '');
    }, [otp]);

    const handleVerifyOTP = (e) => {
        e.preventDefault();
        if (!isButtonActive) return; // Prevent submission if button is inactive

        api.post('/api/verify-otp/', { otp, user_id: userId })
            .then(response => {
                // Save tokens to local storage using constants
                localStorage.setItem(ACCESS_TOKEN, response.data.access);
                localStorage.setItem(REFRESH_TOKEN, response.data.refresh);
                
                // Redirect based on user type
                if (response.data.user_type === 1) {
                    navigate('/home'); // Redirect to admin dashboard
                } else if (response.data.user_type === 2) {
                    navigate('/home'); // Redirect to staff dashboard
                } else {
                    navigate('/home/'); // Fallback to a common home page
                }
            })
            .catch(error => {
                toast.error('OTP verification failed: ' + (error.response?.data || error));
            });
    };

    return (
        <div className='login-page'>
            <div className="login-container">
                <div className="login-section1">
                    <div className="login-flex-item">
                        <p>Please Enter Your OTP to continue to <span>System</span></p>
                    </div>
                    <div className="login-flex-item1">
                        <img src="/src/assets/login1.png" alt="logo-icon" />
                    </div>
                </div>

                <div className='login-form'>
                    <form onSubmit={handleVerifyOTP}>
                        <input
                            type="number"
                            name="otp"
                            placeholder="Enter OTP"
                            value={otp}
                            onChange={(e) => setOtp(e.target.value)}
                            required
                        />
                        <button 
                            type="submit" 
                            style={{ 
                                backgroundColor: isButtonActive ? '#135D66' : '#6c757da7',
                                cursor: isButtonActive ? 'pointer' : 'not-allowed'
                            }} 
                            disabled={!isButtonActive}
                        >
                            Verify OTP
                        </button>
                    </form>
                </div>
            </div>
            <ToastContainer />
        </div>
    );
};

export default OTPform;

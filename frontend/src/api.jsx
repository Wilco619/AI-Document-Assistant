import axios from "axios";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "./constants";

const apiUrl = "http://localhost:8000/";
// Replace with your actual Django base URL

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL : apiUrl,
  timeout: 10000,
});

// Attach the access token to the headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle 401 errors (Unauthorized)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.code === 'ECONNABORTED') {
      console.error("Request timed out:", error.message);
      return Promise.reject(error); // Handle timeout error appropriately
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN);
        if (!refreshToken) {
          throw new Error("Refresh token not found.");
        }

        // Refresh the token
        const response = await axios.post(`${apiUrl}/api/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;

        // Store the new access token
        localStorage.setItem(ACCESS_TOKEN, access);

        // Update the authorization header with the new token
        api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
        originalRequest.headers['Authorization'] = `Bearer ${access}`;

        // Retry the original request with the new token
        return api(originalRequest);
      } catch (err) {
        console.error("Token refresh failed:", err.response?.data || err.message);

        // Clear tokens and redirect to login or handle error
        localStorage.removeItem(ACCESS_TOKEN);
        localStorage.removeItem(REFRESH_TOKEN);

        // Redirect to login page
        window.location.href = '/home'; // Adjust this path as necessary
        return Promise.reject(err);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
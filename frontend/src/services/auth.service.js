/**
 * Authentication Service
 * Handles user authentication, token management, and API calls
 */
import axios from 'axios';

const API_URL = 'http://localhost:8000/auth';
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

class AuthService {
  /**
   * Register a new user
   */
  async register(username, email, password, fullName = null) {
    try {
      const response = await axios.post(`${API_URL}/register`, {
        username,
        email,
        password,
        full_name: fullName,
        tenant_id: 'default'
      });
      
      console.log('✅ Registration successful:', username);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('❌ Registration failed:', error.response?.data?.detail || error.message);
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed'
      };
    }
  }

  /**
   * Login user
   */
  async login(username, password) {
    try {
      const response = await axios.post(`${API_URL}/login`, {
        username,
        password
      });
      
      const { access_token, user } = response.data;
      
      // Store token and user info
      localStorage.setItem(TOKEN_KEY, access_token);
      localStorage.setItem(USER_KEY, JSON.stringify(user));
      
      console.log('✅ Login successful:', username);
      return {
        success: true,
        token: access_token,
        user
      };
    } catch (error) {
      console.error('❌ Login failed:', error.response?.data?.detail || error.message);
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed'
      };
    }
  }

  /**
   * Logout user
   */
  logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    console.log('✅ Logged out');
  }

  /**
   * Get stored token
   */
  getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  /**
   * Get stored user
   */
  getUser() {
    const userStr = localStorage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!this.getToken();
  }

  /**
   * Verify token with backend
   */
  async verifyToken() {
    const token = this.getToken();
    if (!token) return { valid: false };

    try {
      const response = await axios.post(
        `${API_URL}/verify`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      
      return {
        valid: true,
        user: response.data.user
      };
    } catch (error) {
      console.error('❌ Token verification failed');
      this.logout(); // Clear invalid token
      return { valid: false };
    }
  }

  /**
   * Get current user from backend
   */
  async getCurrentUser() {
    const token = this.getToken();
    if (!token) return null;

    try {
      const response = await axios.get(`${API_URL}/me`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      // Update stored user
      localStorage.setItem(USER_KEY, JSON.stringify(response.data));
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get current user');
      this.logout();
      return null;
    }
  }

  /**
   * Get authorization header
   */
  getAuthHeader() {
    const token = this.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }
}

// Create singleton instance
const authService = new AuthService();

export default authService;










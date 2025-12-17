/**
 * Authentication Service
 * 
 * Handles authentication and token management.
 * 
 * Single Responsibility: Authentication only
 */

const TOKEN_KEY = 'auth_token';
const USER_KEY = 'user_data';

class AuthService {
  /**
   * Login
   * 
   * @param {string} username - Username
   * @param {string} password - Password
   * @returns {Promise<Object>} User data
   */
  async login(username, password) {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return {
          success: false,
          error: errorData.message || errorData.detail || 'Login failed'
        };
      }
      
      const data = await response.json();
      
      // Store token and user data
      this.setToken(data.token);
      this.setUser(data.user);
      
      return {
        success: true,
        token: data.token,
        user: data.user
      };
    } catch (error) {
      return {
        success: false,
        error: error.message || 'Network error. Please try again.'
      };
    }
  }
  
  /**
   * Register
   * 
   * @param {string} username - Username
   * @param {string} email - Email
   * @param {string} password - Password
   * @param {string} fullName - Full name (optional)
   * @returns {Promise<Object>} Registration result
   */
  async register(username, email, password, fullName = null) {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          username, 
          email, 
          password, 
          full_name: fullName 
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return {
          success: false,
          error: errorData.message || errorData.detail || 'Registration failed'
        };
      }
      
      const data = await response.json();
      
      return {
        success: true,
        message: data.message
      };
    } catch (error) {
      return {
        success: false,
        error: error.message || 'Network error. Please try again.'
      };
    }
  }
  
  /**
   * Verify Token
   * 
   * @returns {Promise<Object>} Verification result
   */
  async verifyToken() {
    const token = this.getToken();
    
    if (!token) {
      return { valid: false };
    }
    
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/auth/verify`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });
      
      return { valid: response.ok };
    } catch (error) {
      return { valid: false };
    }
  }
  
  /**
   * Logout
   */
  logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
  
  /**
   * Get auth token
   */
  getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }
  
  /**
   * Set auth token
   */
  setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
  }
  
  /**
   * Get user data
   */
  getUser() {
    const userData = localStorage.getItem(USER_KEY);
    return userData ? JSON.parse(userData) : null;
  }
  
  /**
   * Set user data
   */
  setUser(user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }
  
  /**
   * Check if authenticated
   */
  isAuthenticated() {
    return !!this.getToken();
  }
}

// Export singleton instance as default (for backward compatibility)
const authService = new AuthService();
export default authService;

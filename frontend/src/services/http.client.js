/**
 * HTTP Client
 * 
 * Low-level HTTP communication layer.
 * 
 * Single Responsibility: HTTP requests only
 * Dependency Inversion: Services depend on this abstraction
 */

import axios from 'axios';
import { authService } from './auth.service';

class HttpClient {
  constructor() {
    // Create axios instance
    this.client = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    // Setup interceptors
    this.setupInterceptors();
  }
  
  /**
   * Setup request/response interceptors
   */
  setupInterceptors() {
    // Request interceptor: Add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = authService.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );
    
    // Response interceptor: Handle errors
    this.client.interceptors.response.use(
      (response) => response.data,
      (error) => {
        // Handle auth errors
        if (error.response?.status === 401) {
          authService.logout();
          window.location.href = '/login';
        }
        
        return Promise.reject(error);
      }
    );
  }
  
  /**
   * GET request
   */
  async get(url, config = {}) {
    return await this.client.get(url, config);
  }
  
  /**
   * POST request
   */
  async post(url, data, config = {}) {
    return await this.client.post(url, data, config);
  }
  
  /**
   * PUT request
   */
  async put(url, data, config = {}) {
    return await this.client.put(url, data, config);
  }
  
  /**
   * DELETE request
   */
  async delete(url, config = {}) {
    return await this.client.delete(url, config);
  }
  
  /**
   * Streaming request (returns raw response for streaming)
   */
  async stream(url, data, config = {}) {
    const token = authService.getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
    
    const fullUrl = `${this.client.defaults.baseURL}${url}`;
    
    return await fetch(fullUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
      ...config
    });
  }
}

// Export singleton instance as default (for backward compatibility)
const httpClient = new HttpClient();
export default httpClient;


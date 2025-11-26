/**
 * API Service
 * Handles all HTTP requests to the backend
 */
import axios from 'axios';
import { BehaviorSubject } from 'rxjs';

// API Configuration
const API_CONFIG = {
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 60000, // 60 seconds
  headers: {
    'Content-Type': 'application/json',
  }
};

// Create axios instance
const apiClient = axios.create(API_CONFIG);

// Request state observables
const requestState$ = new BehaviorSubject({
  loading: false,
  error: null,
  requestCount: 0
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log('🌐 API Request:', config.method.toUpperCase(), config.url);
    const currentState = requestState$.getValue();
    requestState$.next({
      loading: true,
      error: null,
      requestCount: currentState.requestCount + 1
    });
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.config.url, response.status);
    requestState$.next({
      loading: false,
      error: null,
      requestCount: requestState$.getValue().requestCount
    });
    return response;
  },
  (error) => {
    console.error('❌ Response Error:', error.response?.status, error.message);
    
    let errorMessage = 'An unknown error occurred';
    
    if (error.code === 'ECONNABORTED') {
      errorMessage = 'Request timeout - the server took too long to respond';
    } else if (error.response) {
      errorMessage = `Server error: ${error.response.status} - ${error.response.data?.detail || error.response.statusText}`;
    } else if (error.request) {
      errorMessage = 'Cannot reach server - make sure the backend is running on port 8000';
    } else {
      errorMessage = error.message;
    }
    
    requestState$.next({
      loading: false,
      error: errorMessage,
      requestCount: requestState$.getValue().requestCount
    });
    
    return Promise.reject(new Error(errorMessage));
  }
);

class ApiService {
  /**
   * Get request state observable
   */
  getRequestState() {
    return requestState$;
  }

  /**
   * Send chat query
   */
  async sendMessage(query, tenantId = 'default') {
    try {
      console.log('💬 Sending message:', { query: query.substring(0, 50) + '...', tenantId });
      const startTime = Date.now();
      
      const response = await apiClient.post('/chat/query', {
        query: query,
        tenant_id: tenantId
      });
      
      const duration = Date.now() - startTime;
      console.log(`✅ Message sent successfully in ${duration}ms`);
      
      return {
        success: true,
        data: response.data,
        duration
      };
    } catch (error) {
      console.error('❌ Failed to send message:', error.message);
      return {
        success: false,
        error: error.message,
        data: null
      };
    }
  }

  /**
   * Upload document
   */
  async uploadDocument(file, module, tenantId = 'default') {
    try {
      console.log('📤 Uploading document:', file.name);
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('module', module);
      formData.append('tenant_id', tenantId);

      const response = await apiClient.post('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 120000 // 2 minutes for file uploads
      });

      console.log('✅ Document uploaded successfully');
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('❌ Failed to upload document:', error.message);
      return {
        success: false,
        error: error.message,
        data: null
      };
    }
  }

  /**
   * Health check
   */
  async healthCheck() {
    try {
      const response = await apiClient.get('/', { timeout: 5000 });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
}

export default new ApiService();


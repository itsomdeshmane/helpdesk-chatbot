/**
 * Chat Service
 * 
 * Handles chat-related API calls following SOLID principles.
 * 
 * Single Responsibility: Chat API communication only
 * Open-Closed: Easy to extend with new chat endpoints
 * Dependency Inversion: Uses httpClient abstraction
 */

import { httpClient } from './http.client';

class ChatService {
  /**
   * Send a chat query
   * 
   * @param {string} query - User query
   * @param {Object} options - Query options
   * @returns {Promise<Object>} Response
   */
  async sendQuery(query, options = {}) {
    const {
      source = 'auto',
      tenant_id = 'default',
      session_id = null,
      connection_string = null,
      signal = null
    } = options;
    
    const body = {
      query,
      source,
      tenant_id,
      session_id,
      connection_string
    };
    
    // Use V2 SOLID endpoint by default, fallback to V1 if needed
    try {
      return await httpClient.post('/chat/smart/v2/query', body, { signal });
    } catch (error) {
      // Fallback to V1 if V2 not available
      if (error.response?.status === 404) {
        console.warn('V2 endpoint not available, using V1');
        return await httpClient.post('/chat/smart/query', body, { signal });
      }
      throw error;
    }
  }
  
  /**
   * Stream a chat query
   * 
   * @param {string} query - User query
   * @param {Object} options - Query options
   * @returns {Promise<Response>} Streaming response
   */
  async streamQuery(query, options = {}) {
    const {
      source = 'auto',
      tenant_id = 'default',
      session_id = null,
      connection_string = null
    } = options;
    
    const body = {
      query,
      source,
      tenant_id,
      session_id,
      connection_string
    };
    
    // Use V2 streaming endpoint, fallback to V1
    try {
      return await httpClient.stream('/chat/smart/v2/stream', body);
    } catch (error) {
      if (error.response?.status === 404) {
        return await httpClient.stream('/chat/streaming', body);
      }
      throw error;
    }
  }
  
  /**
   * Get chat history
   * 
   * @param {string} sessionId - Session ID
   * @returns {Promise<Array>} Message history
   */
  async getHistory(sessionId) {
    return await httpClient.get(`/conversations/${sessionId}`);
  }
  
  /**
   * Submit feedback
   * 
   * @param {Object} feedback - Feedback data
   * @returns {Promise<Object>} Response
   */
  async submitFeedback(feedback) {
    return await httpClient.post('/feedback', feedback);
  }
  
  /**
   * Health check for chat service
   * 
   * @returns {Promise<Object>} Health status
   */
  async healthCheck() {
    try {
      return await httpClient.get('/chat/smart/v2/health');
    } catch (error) {
      // Fallback to root health
      return await httpClient.get('/health');
    }
  }
}

// Export singleton instance as default (for backward compatibility)
const chatService = new ChatService();
export default chatService;


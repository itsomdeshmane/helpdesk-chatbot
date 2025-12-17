/**
 * useChat Hook
 * 
 * Custom hook for chat functionality following SOLID principles.
 * 
 * Single Responsibility: Manages chat state and interactions
 * 
 * Usage:
 *   const { messages, sendMessage, isLoading } = useChat();
 */

import { useState, useCallback, useRef } from 'react';
import { chatService } from '../services/chat.service';

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  
  // Refs for cleanup
  const isMountedRef = useRef(true);
  const abortControllerRef = useRef(null);
  
  /**
   * Send a chat message
   * 
   * @param {string} query - User query
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} Response
   */
  const sendMessage = useCallback(async (query, options = {}) => {
    // Abort any pending request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    abortControllerRef.current = new AbortController();
    
    // Add user message
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: query,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);
    
    try {
      // Call API
      const response = await chatService.sendQuery(query, {
        ...options,
        session_id: sessionId,
        signal: abortControllerRef.current.signal
      });
      
      // Update session ID if returned
      if (response.session_id && !sessionId) {
        setSessionId(response.session_id);
      }
      
      // Add assistant message
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.message,
        source: response.source,
        data: response.data,
        metadata: response.metadata,
        timestamp: new Date().toISOString()
      };
      
      if (isMountedRef.current) {
        setMessages(prev => [...prev, assistantMessage]);
        setIsLoading(false);
      }
      
      return response;
      
    } catch (err) {
      if (err.name === 'AbortError') {
        console.log('Request aborted');
        return null;
      }
      
      if (isMountedRef.current) {
        setError(err.message || 'Failed to send message');
        setIsLoading(false);
        
        // Add error message
        const errorMessage = {
          id: Date.now() + 1,
          role: 'error',
          content: err.message || 'Failed to send message',
          timestamp: new Date().toISOString()
        };
        
        setMessages(prev => [...prev, errorMessage]);
      }
      
      throw err;
    }
  }, [sessionId]);
  
  /**
   * Clear chat history
   */
  const clearChat = useCallback(() => {
    setMessages([]);
    setSessionId(null);
    setError(null);
  }, []);
  
  /**
   * Retry last message
   */
  const retryLastMessage = useCallback(async () => {
    const lastUserMessage = [...messages]
      .reverse()
      .find(msg => msg.role === 'user');
    
    if (lastUserMessage) {
      // Remove failed response
      setMessages(prev => 
        prev.filter(msg => msg.timestamp > lastUserMessage.timestamp)
      );
      
      // Resend
      return await sendMessage(lastUserMessage.content);
    }
  }, [messages, sendMessage]);
  
  // Cleanup on unmount
  useCallback(() => {
    return () => {
      isMountedRef.current = false;
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);
  
  return {
    messages,
    isLoading,
    error,
    sessionId,
    sendMessage,
    clearChat,
    retryLastMessage
  };
};


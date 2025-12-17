/**
 * useChatStream Hook
 * 
 * Custom hook for streaming chat responses.
 * 
 * Single Responsibility: Manages streaming chat state
 * 
 * Usage:
 *   const { stream, isStreaming } = useChatStream();
 */

import { useState, useCallback, useRef } from 'react';
import { chatService } from '../services/chat.service';

export const useChatStream = () => {
  const [streamedContent, setStreamedContent] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  
  const readerRef = useRef(null);
  const isMountedRef = useRef(true);
  
  /**
   * Start streaming a query
   * 
   * @param {string} query - User query
   * @param {Object} options - Additional options
   * @param {Function} onChunk - Callback for each chunk
   * @returns {Promise<void>}
   */
  const streamQuery = useCallback(async (query, options = {}, onChunk = null) => {
    setStreamedContent('');
    setIsStreaming(true);
    setError(null);
    
    try {
      // Call streaming API
      const response = await chatService.streamQuery(query, options);
      
      if (!response.body) {
        throw new Error('Stream not supported');
      }
      
      const reader = response.body.getReader();
      readerRef.current = reader;
      
      const decoder = new TextDecoder();
      let accumulated = '';
      
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        // Decode chunk
        const chunk = decoder.decode(value, { stream: true });
        accumulated += chunk;
        
        if (isMountedRef.current) {
          setStreamedContent(accumulated);
          
          // Call chunk callback
          if (onChunk) {
            onChunk(chunk, accumulated);
          }
        }
      }
      
      if (isMountedRef.current) {
        setIsStreaming(false);
      }
      
      return accumulated;
      
    } catch (err) {
      if (isMountedRef.current) {
        setError(err.message || 'Streaming failed');
        setIsStreaming(false);
      }
      throw err;
    }
  }, []);
  
  /**
   * Stop streaming
   */
  const stopStreaming = useCallback(() => {
    if (readerRef.current) {
      readerRef.current.cancel();
      readerRef.current = null;
    }
    setIsStreaming(false);
  }, []);
  
  /**
   * Clear streamed content
   */
  const clearStream = useCallback(() => {
    setStreamedContent('');
    setError(null);
  }, []);
  
  // Cleanup on unmount
  useCallback(() => {
    return () => {
      isMountedRef.current = false;
      if (readerRef.current) {
        readerRef.current.cancel();
      }
    };
  }, []);
  
  return {
    streamedContent,
    isStreaming,
    error,
    streamQuery,
    stopStreaming,
    clearStream
  };
};


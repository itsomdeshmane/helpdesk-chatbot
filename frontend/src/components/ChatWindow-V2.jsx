/**
 * ChatWindow V2 - SOLID-Compliant Component
 * 
 * This is a refactored version following SOLID principles:
 * - Single Responsibility: Rendering UI only
 * - Open-Closed: Easy to extend with new features
 * - Dependency Inversion: Uses hooks and services (injected)
 * 
 * Comparison:
 * - OLD (ChatWindow-Enhanced.js): 737 lines, mixed concerns
 * - NEW (ChatWindow-V2.jsx): ~200 lines, UI only
 */

import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../hooks/useChat';
import { useChatStream } from '../hooks/useChatStream';

const ChatWindowV2 = () => {
  // ========================================================================
  // STATE & HOOKS (Business logic extracted to hooks)
  // ========================================================================
  
  const {
    messages,
    isLoading,
    error,
    sessionId,
    sendMessage,
    clearChat,
    retryLastMessage
  } = useChat();
  
  const {
    streamedContent,
    isStreaming,
    streamQuery
  } = useChatStream();
  
  // Local UI state only
  const [inputValue, setInputValue] = useState('');
  const [useStreaming, setUseStreaming] = useState(false);
  const messagesEndRef = useRef(null);
  
  // ========================================================================
  // EFFECTS
  // ========================================================================
  
  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamedContent]);
  
  // ========================================================================
  // EVENT HANDLERS (Thin wrappers, logic in hooks)
  // ========================================================================
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!inputValue.trim()) return;
    
    const query = inputValue;
    setInputValue('');
    
    try {
      if (useStreaming) {
        await streamQuery(query);
      } else {
        await sendMessage(query);
      }
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };
  
  const handleClear = () => {
    clearChat();
    setInputValue('');
  };
  
  const handleRetry = async () => {
    try {
      await retryLastMessage();
    } catch (err) {
      console.error('Failed to retry:', err);
    }
  };
  
  // ========================================================================
  // RENDER (UI only, no business logic)
  // ========================================================================
  
  return (
    <div className="chat-window-v2">
      {/* Header */}
      <div className="chat-header">
        <h2>AI Assistant (SOLID V2)</h2>
        <div className="chat-controls">
          <label>
            <input
              type="checkbox"
              checked={useStreaming}
              onChange={(e) => setUseStreaming(e.target.checked)}
            />
            Streaming
          </label>
          <button onClick={handleClear} className="btn-clear">
            Clear Chat
          </button>
        </div>
      </div>
      
      {/* Session Info */}
      {sessionId && (
        <div className="session-info">
          Session: {sessionId}
        </div>
      )}
      
      {/* Messages Area */}
      <div className="messages-container">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        
        {/* Streaming content */}
        {isStreaming && streamedContent && (
          <MessageBubble
            message={{
              role: 'assistant',
              content: streamedContent,
              isStreaming: true
            }}
          />
        )}
        
        {/* Loading indicator */}
        {isLoading && <LoadingIndicator />}
        
        {/* Error message */}
        {error && (
          <div className="error-message">
            {error}
            <button onClick={handleRetry} className="btn-retry">
              Retry
            </button>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input Area */}
      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask me anything..."
          disabled={isLoading || isStreaming}
          className="chat-input"
        />
        <button
          type="submit"
          disabled={isLoading || isStreaming || !inputValue.trim()}
          className="btn-send"
        >
          {isLoading || isStreaming ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

// ============================================================================
// SUB-COMPONENTS (Extracted for SRP)
// ============================================================================

/**
 * Message Bubble Component
 * 
 * Single Responsibility: Render a single message
 */
const MessageBubble = ({ message }) => {
  const { role, content, source, data, isStreaming } = message;
  
  const className = `message message-${role}${isStreaming ? ' streaming' : ''}`;
  
  return (
    <div className={className}>
      <div className="message-header">
        <span className="message-role">
          {role === 'user' ? '👤 You' : '🤖 Assistant'}
        </span>
        {source && (
          <span className="message-source">
            Source: {source}
          </span>
        )}
      </div>
      <div className="message-content">{content}</div>
      {data && <DataDisplay data={data} />}
    </div>
  );
};

/**
 * Data Display Component
 * 
 * Single Responsibility: Render data tables
 */
const DataDisplay = ({ data }) => {
  if (!data || !Array.isArray(data) || data.length === 0) {
    return null;
  }
  
  const columns = Object.keys(data[0]);
  
  return (
    <div className="data-table">
      <table>
        <thead>
          <tr>
            {columns.map(col => (
              <th key={col}>{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx}>
              {columns.map(col => (
                <td key={col}>{row[col]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

/**
 * Loading Indicator Component
 * 
 * Single Responsibility: Show loading state
 */
const LoadingIndicator = () => (
  <div className="loading-indicator">
    <div className="spinner"></div>
    <span>Thinking...</span>
  </div>
);

export default ChatWindowV2;


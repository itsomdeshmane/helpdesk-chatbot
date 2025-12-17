import React, { useState, useEffect, useRef, useCallback, memo } from 'react';
import chatState from '../services/chat.state';
import apiService from '../services/api.service';
import './ChatWindow.css';

// Simple Markdown renderer component (Memoized for performance)
const MarkdownText = memo(({ text }) => {
  // Convert markdown to HTML
  const renderMarkdown = (content) => {
    if (!content) return '';
    
    let html = content;
    
    // Headers
    html = html.replace(/^### (.*$)/gim, '<h4>$1</h4>');
    html = html.replace(/^## (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^# (.*$)/gim, '<h2>$1</h2>');
    
    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Italic
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Code blocks
    html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    
    // Inline code
    html = html.replace(/`(.*?)`/g, '<code>$1</code>');
    
    // Lists
    html = html.replace(/^\s*[-•*]\s+(.*)$/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    
    // Numbered lists
    html = html.replace(/^\s*\d+\.\s+(.*)$/gim, '<li>$1</li>');
    
    // Line breaks
    html = html.replace(/\n\n/g, '</p><p>');
    html = html.replace(/\n/g, '<br/>');
    
    // Wrap in paragraph
    if (!html.startsWith('<')) {
      html = '<p>' + html + '</p>';
    }
    
    return html;
  };
  
  return (
    <div 
      className="markdown-content"
      dangerouslySetInnerHTML={{ __html: renderMarkdown(text) }}
    />
  );
});

// Feedback component (Memoized - won't re-render unless message changes)
const FeedbackButtons = memo(({ message, onFeedback }) => {
  const [feedbackGiven, setFeedbackGiven] = useState(null);
  const [showTextInput, setShowTextInput] = useState(false);
  const [feedbackText, setFeedbackText] = useState('');
  
  const handleFeedback = async (helpful) => {
    setFeedbackGiven(helpful);
    
    if (!helpful) {
      setShowTextInput(true);
    } else {
      await submitFeedback(helpful, '');
    }
  };
  
  const submitFeedback = async (helpful, text) => {
    try {
      await apiService.submitFeedback({
        message_id: message.id?.toString() || Date.now().toString(),
        session_id: chatState.sessionId$.getValue() || 'unknown',
        helpful: helpful,
        rating: helpful ? 5 : 2,
        feedback_text: text,
        feedback_type: helpful ? 'general' : 'incorrect',
        query: message.query || '',
        response: message.content?.substring(0, 500) || ''
      });
      
      if (onFeedback) onFeedback(helpful);
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
    
    setShowTextInput(false);
  };
  
  if (feedbackGiven !== null && !showTextInput) {
    return (
      <div className="feedback-given">
        {feedbackGiven ? '✓ Thanks for the feedback!' : '✓ Feedback recorded'}
      </div>
    );
  }
  
  return (
    <div className="feedback-container">
      {!showTextInput ? (
        <div className="feedback-buttons">
          <span className="feedback-label">Was this helpful?</span>
          <button 
            className="feedback-btn helpful"
            onClick={() => handleFeedback(true)}
            title="Yes, this was helpful"
          >
            👍
          </button>
          <button 
            className="feedback-btn not-helpful"
            onClick={() => handleFeedback(false)}
            title="No, this wasn't helpful"
          >
            👎
          </button>
        </div>
      ) : (
        <div className="feedback-text-input">
          <input
            type="text"
            placeholder="What could be improved?"
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
            className="feedback-input"
          />
          <button 
            className="feedback-submit"
            onClick={() => submitFeedback(false, feedbackText)}
          >
            Submit
          </button>
          <button 
            className="feedback-cancel"
            onClick={() => setShowTextInput(false)}
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
});

// Suggested Questions component (Memoized)
const SuggestedQuestions = memo(({ questions, onSelect }) => {
  if (!questions || questions.length === 0) return null;
  
  return (
    <div className="suggested-questions">
      <div className="suggestions-label">💡 You might also want to ask:</div>
      <div className="suggestions-list">
        {questions.map((question, idx) => (
          <button
            key={idx}
            className="suggestion-chip"
            onClick={() => onSelect(question)}
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
});

// Source Attribution component - DISABLED (answers come only from document chunks)
// No need to memoize as it returns null
const SourceAttribution = ({ sources }) => {
  // Sources display disabled - chatbot only uses document chunks
  return null;
};

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef(null);
  const eventSourceRef = useRef(null);

  // Auto-scroll to bottom (memoized)
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent, scrollToBottom]);

  // Subscribe to state changes
  useEffect(() => {
    const messagesSub = chatState.messages$.subscribe(msgs => {
      setMessages(msgs);
    });

    const loadingSub = chatState.loading$.subscribe(isLoading => {
      setLoading(isLoading);
    });

    // Load conversation history if user is authenticated and no messages
    const loadHistory = async () => {
      try {
        const token = localStorage.getItem('auth_token'); // FIX: Use correct key
        const currentMessages = chatState.messages$.getValue();
        
        if (token && (!currentMessages || currentMessages.length === 0)) {
          console.log('📜 Loading conversation history on mount...');
          
          const conversationService = require('../services/conversation.service').default;
          const recentConv = await conversationService.loadRecentConversation();
          
          if (recentConv.success && recentConv.messages && recentConv.messages.length > 0) {
            chatState.sessionId$.next(recentConv.sessionId);
            
            const messages = [];
            for (const msg of recentConv.messages) {
              messages.push({
                role: 'user',
                content: msg.query,
                timestamp: msg.timestamp,
                id: Date.now() + Math.random()
              });
              messages.push({
                role: 'assistant',
                content: msg.response,
                timestamp: msg.timestamp,
                id: Date.now() + Math.random()
              });
            }
            
            chatState.messages$.next(messages);
            console.log(`✅ Loaded ${recentConv.messages.length} messages from history`);
          }
        }
      } catch (e) {
        console.error('⚠️  Failed to load history on mount:', e);
      }
    };
    
    loadHistory();

    return () => {
      messagesSub.unsubscribe();
      loadingSub.unsubscribe();
      // Clean up any active EventSource
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  // Handle streaming response
  const handleStreamingResponse = useCallback(async (query) => {
    setIsStreaming(true);
    setStreamingContent('');
    
    // Add user message
    chatState.addMessage({ role: 'user', content: query });
    
    try {
      const tenantId = chatState.tenantId$.getValue();
      const sessionId = chatState.sessionId$.getValue();
      
      // Get auth token from localStorage
      const token = localStorage.getItem('auth_token'); // FIX: Use correct key
      
      // Prepare headers with auth token if available
      const headers = {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      // Use fetch with streaming
      const response = await fetch('http://localhost:8000/chat/query/stream', {
        method: 'POST',
        headers: headers,
        mode: 'cors',
        credentials: 'omit',  // Don't send credentials for simple requests
        body: JSON.stringify({
          query: query,
          tenant_id: tenantId,
          session_id: sessionId
        })
      });
      
      // Check if response is OK
      if (!response.ok) {
        throw new Error(`Server error: ${response.status} ${response.statusText}`);
      }
      
      // Extract session ID from response headers
      const newSessionId = response.headers.get('X-Session-ID');
      if (newSessionId && newSessionId !== sessionId) {
        chatState.sessionId$.next(newSessionId);
        console.log('🔐 Session ID received:', newSessionId);
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = '';
      let sources = [];
      let suggestedQuestions = [];
      let receivedSessionId = null;
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6));
              
              switch (data.type) {
                case 'content':
                  fullContent += data.content;
                  setStreamingContent(fullContent);
                  break;
                case 'complete':
                  // Store session ID from complete event
                  if (data.session_id && !receivedSessionId) {
                    receivedSessionId = data.session_id;
                    chatState.sessionId$.next(receivedSessionId);
                    console.log('🔐 Session ID stored:', receivedSessionId);
                  }
                  break;
                case 'sources':
                  sources = data.sources || [];
                  break;
                case 'suggestions':
                  suggestedQuestions = data.suggestions || [];
                  break;
                case 'error':
                  console.error('Stream error:', data.message);
                  fullContent = `Error: ${data.message}`;
                  break;
                default:
                  break;
              }
            } catch (e) {
              // Ignore parsing errors for incomplete chunks
            }
          }
        }
      }
      
      // Add complete assistant message
      chatState.addMessage({
        role: 'assistant',
        content: fullContent,
        sources: sources,
        suggestedQuestions: suggestedQuestions
      });
      
    } catch (error) {
      console.error('Streaming error:', error);
      chatState.addMessage({
        role: 'assistant',
        content: `Error: ${error.message}`,
        isError: true
      });
    } finally {
      setIsStreaming(false);
      setStreamingContent('');
    }
  }, []);

  const handleSend = useCallback(async () => {
    if (!input.trim() || loading || isStreaming) return;

    const query = input;
    setInput('');
    
    // Use streaming by default, fall back to regular if it fails
    try {
      await handleStreamingResponse(query);
    } catch (error) {
      // Fallback to non-streaming
      await chatState.sendMessage(query);
    }
  }, [input, loading, isStreaming, handleStreamingResponse]);

  const handleKeyPress = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }, [handleSend]);

  const handleClear = useCallback(() => {
    if (window.confirm('Clear all messages?')) {
      chatState.clearMessages();
    }
  }, []);
  
  const handleSuggestionClick = useCallback((question) => {
    setInput(question);
  }, []);

  return (
    <div className="chat-container">
      <div className="chat-wrapper">
        {/* Header */}
        <div className="chat-header">
          <div className="header-title">
            <span className="header-icon">🤖</span>
            <span>AI Helpdesk Assistant</span>
          </div>
          <div className="header-badge">v2.0</div>
        </div>

        {/* Messages Area */}
        <div className="messages-area">
          {messages.length === 0 && !isStreaming ? (
            <div className="welcome-screen">
              <div className="welcome-icon">👋</div>
              <h2>Hello! How can I help you today?</h2>
              <p>Ask me anything about the system and I'll find the answer in our documentation.</p>
              <div className="feature-badges">
                <span className="feature-badge">📄 Document Search</span>
                <span className="feature-badge">💬 Context-Aware</span>
                <span className="feature-badge">⚡ Real-time</span>
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, idx) => (
                <div 
                  key={msg.id || idx} 
                  className={`message ${msg.role} ${msg.isError ? 'error' : ''}`}
                >
                  <div className="message-avatar">
                    {msg.role === 'user' ? '👤' : '🤖'}
                  </div>
                  <div className="message-content">
                    {msg.role === 'assistant' ? (
                      <MarkdownText text={msg.content} />
                    ) : (
                      <div className="message-text">{msg.content}</div>
                    )}
                    
                    {/* Source attribution */}
                    {msg.sources && msg.sources.length > 0 && (
                      <SourceAttribution sources={msg.sources} />
                    )}
                    
                    {/* Suggested questions */}
                    {msg.suggestedQuestions && msg.suggestedQuestions.length > 0 && (
                      <SuggestedQuestions 
                        questions={msg.suggestedQuestions}
                        onSelect={handleSuggestionClick}
                      />
                    )}
                    
                    {/* Feedback buttons for assistant messages */}
                    {msg.role === 'assistant' && !msg.isError && (
                      <FeedbackButtons message={msg} />
                    )}
                  </div>
                </div>
              ))}
              
              {/* Streaming message */}
              {isStreaming && streamingContent && (
                <div className="message assistant streaming">
                  <div className="message-avatar">🤖</div>
                  <div className="message-content">
                    <MarkdownText text={streamingContent} />
                    <span className="streaming-cursor">▋</span>
                  </div>
                </div>
              )}
              
              {/* Loading indicator */}
              {(loading || (isStreaming && !streamingContent)) && (
                <div className="message assistant">
                  <div className="message-avatar">🤖</div>
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="input-area">
          {messages.length > 0 && (
            <button 
              onClick={handleClear} 
              className="clear-button"
              title="Clear conversation"
            >
              🗑️
            </button>
          )}
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={loading || isStreaming}
            className="message-input"
          />
          <button
            onClick={handleSend}
            disabled={loading || isStreaming || !input.trim()}
            className="send-button"
          >
            {loading || isStreaming ? '⏳' : '📤'}
          </button>
        </div>
      </div>
    </div>
  );
}

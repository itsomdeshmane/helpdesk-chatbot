import React, { useState, useEffect, useRef, useCallback } from 'react';
import chatState from '../services/chat.state';
import apiService from '../services/api.service';
import Settings from './Settings';
import '../theme.css';
import './ChatWindow-Enhanced.css';

// Simple Markdown renderer component
const MarkdownText = ({ text }) => {
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
};

// Data table component for database results
const DataTable = ({ rows, columns }) => {
  if (!rows || rows.length === 0) return null;
  
  return (
    <div className="data-table-container">
      <div className="table-header">Query Results ({rows.length} rows)</div>
      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              {columns.map((col, idx) => (
                <th key={idx}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIdx) => (
              <tr key={rowIdx}>
                {columns.map((col, colIdx) => (
                  <td key={colIdx}>{row[col]?.toString() || ''}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Feedback component
const FeedbackButtons = ({ message, onFeedback }) => {
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
        {feedbackGiven ? 'Thanks for the feedback!' : 'Feedback recorded'}
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
};

export default function ChatWindowEnhanced({ user, onLogout }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [selectedSource, setSelectedSource] = useState('auto'); // 'auto', 'documents', 'database'
  const [chatSessions, setChatSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent]);

  // Load chat sessions on mount
  useEffect(() => {
    loadChatSessions();
  }, []);

  // Load all chat sessions
  const loadChatSessions = () => {
    const savedSessions = localStorage.getItem('chatSessions');
    if (savedSessions) {
      const sessions = JSON.parse(savedSessions);
      setChatSessions(sessions);
      
      // Load the most recent session
      if (sessions.length > 0 && !currentSessionId) {
        loadSession(sessions[0].id);
      }
    }
  };

  // Create new chat session
  const createNewChat = () => {
    const newSession = {
      id: Date.now().toString(),
      title: 'New Chat',
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    const updatedSessions = [newSession, ...chatSessions];
    setChatSessions(updatedSessions);
    localStorage.setItem('chatSessions', JSON.stringify(updatedSessions));
    
    setCurrentSessionId(newSession.id);
    chatState.messages$.next([]);
    chatState.sessionId$.next(null); // Reset backend session
  };

  // Load a specific session
  const loadSession = (sessionId) => {
    const session = chatSessions.find(s => s.id === sessionId);
    if (session) {
      setCurrentSessionId(sessionId);
      chatState.messages$.next(session.messages || []);
      chatState.sessionId$.next(null); // Reset backend session for new conversation
    }
  };

  // Save current session
  const saveCurrentSession = (newMessages) => {
    if (!currentSessionId) return;
    
    const updatedSessions = chatSessions.map(session => {
      if (session.id === currentSessionId) {
        // Generate title from first user message if still "New Chat"
        let title = session.title;
        if (title === 'New Chat' && newMessages.length > 0) {
          const firstUserMsg = newMessages.find(m => m.role === 'user');
          if (firstUserMsg) {
            title = firstUserMsg.content.substring(0, 50) + (firstUserMsg.content.length > 50 ? '...' : '');
          }
        }
        
        return {
          ...session,
          title,
          messages: newMessages,
          updatedAt: new Date().toISOString()
        };
      }
      return session;
    });
    
    setChatSessions(updatedSessions);
    localStorage.setItem('chatSessions', JSON.stringify(updatedSessions));
  };

  // Delete a session
  const deleteSession = (sessionId) => {
    const updatedSessions = chatSessions.filter(s => s.id !== sessionId);
    setChatSessions(updatedSessions);
    localStorage.setItem('chatSessions', JSON.stringify(updatedSessions));
    
    if (currentSessionId === sessionId) {
      if (updatedSessions.length > 0) {
        loadSession(updatedSessions[0].id);
      } else {
        createNewChat();
      }
    }
  };

  // Subscribe to state changes
  useEffect(() => {
    const messagesSub = chatState.messages$.subscribe(msgs => {
      setMessages(msgs);
      // Save to current session when messages change
      if (currentSessionId && msgs.length > 0) {
        saveCurrentSession(msgs);
      }
    });

    const loadingSub = chatState.loading$.subscribe(isLoading => {
      setLoading(isLoading);
    });

    return () => {
      messagesSub.unsubscribe();
      loadingSub.unsubscribe();
    };
  }, [currentSessionId, chatSessions]);

  // Handle streaming response with source selection
  const handleStreamingResponse = useCallback(async (query, source) => {
    setIsStreaming(true);
    setStreamingContent('');
    
    // Add user message
    chatState.addMessage({ role: 'user', content: query });
    
    try {
      const tenantId = chatState.tenantId$.getValue();
      const sessionId = chatState.sessionId$.getValue();
      const token = localStorage.getItem('auth_token');
      
      const headers = {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      // Use smart chat endpoint with source selection
      const response = await fetch('http://localhost:8000/chat/smart/stream', {
        method: 'POST',
        headers: headers,
        mode: 'cors',
        credentials: 'omit',
        body: JSON.stringify({
          query: query,
          source: source,
          tenant_id: tenantId,
          session_id: sessionId
        })
      });
      
      if (!response.ok) {
        throw new Error(`Server error: ${response.status} ${response.statusText}`);
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = '';
      let dataRows = [];
      let dataColumns = [];
      let receivedSessionId = null;
      let responseSource = null;
      
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
                case 'status':
                  // Show status updates
                  setStreamingContent(`🔄 ${data.content}`);
                  break;
                case 'text':
                  fullContent += data.content;
                  setStreamingContent(fullContent);
                  break;
                case 'data':
                  // Database query results
                  dataRows = data.rows || [];
                  dataColumns = data.columns || [];
                  break;
                case 'complete':
                  if (data.session_id && !receivedSessionId) {
                    receivedSessionId = data.session_id;
                    chatState.sessionId$.next(receivedSessionId);
                  }
                  responseSource = data.source;
                  break;
                case 'error':
                  console.error('Stream error:', data.message);
                  fullContent = `Error: ${data.message}`;
                  break;
                default:
                  break;
              }
            } catch (e) {
              // Ignore parsing errors
            }
          }
        }
      }
      
      // Add complete assistant message
      chatState.addMessage({
        role: 'assistant',
        content: fullContent,
        source: responseSource,
        dataRows: dataRows,
        dataColumns: dataColumns
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

  const handleSend = async () => {
    if (!input.trim() || loading || isStreaming) return;

    const query = input;
    setInput('');
    
    await handleStreamingResponse(query, selectedSource);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClear = () => {
    if (window.confirm('Clear this conversation?')) {
      chatState.clearMessages();
      if (currentSessionId) {
        saveCurrentSession([]);
      }
    }
  };

  const getSourceIcon = (source) => {
    switch (source) {
      case 'documents':
        return '📄';
      case 'database':
        return '💾';
      case 'clarification':
        return '❓';
      default:
        return '🤖';
    }
  };

  const getSourceLabel = (source) => {
    switch (source) {
      case 'documents':
        return 'Knowledge Base';
      case 'database':
        return 'Database Query';
      case 'clarification':
        return 'Need More Info';
      default:
        return 'AI Assistant';
    }
  };

  // Initialize first session if none exists
  useEffect(() => {
    if (chatSessions.length === 0 && !currentSessionId) {
      createNewChat();
    }
  }, []);

  // Apply theme
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const handleThemeChange = (newTheme) => {
    setTheme(newTheme);
  };

  return (
    <div className="chat-container enhanced">
      {/* Settings Modal */}
      <Settings
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        currentTheme={theme}
        onThemeChange={handleThemeChange}
      />

      {/* Sidebar */}
      <div className={`chat-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <button className="new-chat-btn" onClick={createNewChat}>
            + New Chat
          </button>
          <button className="toggle-sidebar-btn" onClick={() => setSidebarOpen(!sidebarOpen)}>
            {sidebarOpen ? '←' : '→'}
          </button>
        </div>
        
        {sidebarOpen && (
          <>
            <div className="sessions-list">
              {chatSessions.map(session => (
                <div
                  key={session.id}
                  className={`session-item ${currentSessionId === session.id ? 'active' : ''}`}
                  onClick={() => loadSession(session.id)}
                >
                  <div className="session-title">{session.title}</div>
                  <div className="session-date">
                    {new Date(session.updatedAt).toLocaleDateString()}
                  </div>
                  <button
                    className="delete-session-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      if (window.confirm('Delete this chat?')) {
                        deleteSession(session.id);
                      }
                    }}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
            
            {/* Settings Button at Bottom */}
            <div className="sidebar-footer">
              <button className="settings-btn" onClick={() => setSettingsOpen(true)}>
                ⚙ Settings
              </button>
            </div>
          </>
        )}
      </div>

      <div className="chat-wrapper">
        {/* Header - ChatGPT Style Layout */}
        <div className="chat-header enhanced">
          {/* Left: Chatbot Name */}
          <div className="header-left">
            <div className="chatbot-name">AI Helpdesk</div>
          </div>
          
          {/* Right: User Info & Logout */}
          <div className="header-right">
            <div className="user-info">
              <span className="user-name">{user?.username || 'User'}</span>
              {user?.role && <span className="user-role">{user.role}</span>}
            </div>
            {onLogout && (
              <button onClick={onLogout} className="logout-btn">
                Logout
              </button>
            )}
          </div>
        </div>

        {/* Messages Area */}
        <div className="messages-area">
          {messages.length === 0 && !isStreaming ? (
            <div className="welcome-screen enhanced">
              <h2>Hello! How can I help you today?</h2>
              <p>I can help you with both documentation and database queries.</p>
              
              <div className="quick-actions">
                <div className="quick-action-card" onClick={() => setSelectedSource('documents')}>
                  <div className="action-title">Documentation</div>
                  <div className="action-desc">Search knowledge base and docs</div>
                </div>
                
                <div className="quick-action-card" onClick={() => setSelectedSource('database')}>
                  <div className="action-title">Database</div>
                  <div className="action-desc">Query data and analytics</div>
                </div>
                
                <div className="quick-action-card" onClick={() => setSelectedSource('auto')}>
                  <div className="action-title">Smart Mode</div>
                  <div className="action-desc">Auto-detect best source</div>
                </div>
              </div>
              
              <div className="feature-badges">
                <span className="feature-badge">Hybrid Search</span>
                <span className="feature-badge">Context-Aware</span>
                <span className="feature-badge">Real-time Streaming</span>
                <span className="feature-badge">Multi-Source</span>
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, idx) => (
                <div 
                  key={msg.id || idx} 
                  className={`message ${msg.role} ${msg.isError ? 'error' : ''} enhanced`}
                >
                  <div className="message-avatar">
                    {msg.role === 'user' ? 'U' : 'A'}
                  </div>
                  <div className="message-content">
                    {msg.source && msg.role === 'assistant' && (
                      <div className="message-source-badge">
                        {getSourceLabel(msg.source)}
                      </div>
                    )}
                    
                    {msg.role === 'assistant' ? (
                      <MarkdownText text={msg.content} />
                    ) : (
                      <div className="message-text">{msg.content}</div>
                    )}
                    
                    {/* Data table for database results */}
                    {msg.dataRows && msg.dataRows.length > 0 && (
                      <DataTable rows={msg.dataRows} columns={msg.dataColumns} />
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
                <div className="message assistant streaming enhanced">
                  <div className="message-avatar">A</div>
                  <div className="message-content">
                    <MarkdownText text={streamingContent} />
                    <span className="streaming-cursor">|</span>
                  </div>
                </div>
              )}
              
              {/* Loading indicator */}
              {(loading || (isStreaming && !streamingContent)) && (
                <div className="message assistant enhanced">
                  <div className="message-avatar">A</div>
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
        <div className="input-area enhanced">
          <select
            value={selectedSource}
            onChange={(e) => setSelectedSource(e.target.value)}
            className="source-dropdown"
            disabled={loading || isStreaming}
          >
            <option value="auto">Auto</option>
            <option value="documents">Documents</option>
            <option value="database">Database</option>
          </select>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything..."
            disabled={loading || isStreaming}
            className="message-input enhanced"
            rows="1"
          />
          <button
            onClick={handleSend}
            disabled={loading || isStreaming || !input.trim()}
            className="send-button enhanced"
          >
            {loading || isStreaming ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
}


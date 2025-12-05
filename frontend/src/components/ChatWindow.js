import React, { useState, useEffect, useRef } from 'react';
import chatState from '../services/chat.state';
import './ChatWindow.css';

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Subscribe to state changes
  useEffect(() => {
    const messagesSub = chatState.messages$.subscribe(msgs => {
      setMessages(msgs);
    });

    const loadingSub = chatState.loading$.subscribe(isLoading => {
      setLoading(isLoading);
    });

    return () => {
      messagesSub.unsubscribe();
      loadingSub.unsubscribe();
    };
  }, []);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const query = input;
    setInput('');
    await chatState.sendMessage(query);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClear = () => {
    if (window.confirm('Clear all messages?')) {
      chatState.clearMessages();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-wrapper">
        {/* Messages Area */}
        <div className="messages-area">
          {messages.length === 0 ? (
            <div className="welcome-screen">
              <div className="welcome-icon">👋</div>
              <h2>Hello! How can I help you today?</h2>
              <p>Ask me anything and I'll do my best to assist you.</p>
            </div>
          ) : (
            <>
              {messages.map((msg, idx) => (
                <div 
                  key={msg.id || idx} 
                  className={`message ${msg.role}`}
                >
                  <div className="message-avatar">
                    {msg.role === 'user' ? '👤' : '🤖'}
                  </div>
                  <div className="message-content">
                    <div className="message-text">{msg.content}</div>
                    {msg.module && (
                      <div className="message-meta">
                        <span className="module-tag">{msg.module}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
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
            disabled={loading}
            className="message-input"
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="send-button"
          >
            {loading ? '⏳' : '📤'}
          </button>
        </div>
      </div>
    </div>
  );
}

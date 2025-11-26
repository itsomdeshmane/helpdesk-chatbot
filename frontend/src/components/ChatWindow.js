import React, { useState, useEffect } from 'react';
import chatState from '../services/chat.state';
import ResponseFormatter from './ResponseFormatter';
import FAQPanel from './FAQPanel';

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [storageInfo, setStorageInfo] = useState(null);
  const [showFAQ, setShowFAQ] = useState(false);

  // Subscribe to state changes
  useEffect(() => {
    console.log('🎯 ChatWindow mounted, subscribing to state');

    // Subscribe to messages
    const messagesSub = chatState.messages$.subscribe(msgs => {
      setMessages(msgs);
    });

    // Subscribe to loading state
    const loadingSub = chatState.loading$.subscribe(isLoading => {
      setLoading(isLoading);
    });

    // Update storage info
    setStorageInfo(chatState.getStorageInfo());

    // Cleanup subscriptions
    return () => {
      console.log('🎯 ChatWindow unmounted, cleaning up subscriptions');
      messagesSub.unsubscribe();
      loadingSub.unsubscribe();
    };
  }, []);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const query = input;
    setInput(''); // Clear input immediately
    
    // Send message through state management
    await chatState.sendMessage(query);
    
    // Update storage info
    setStorageInfo(chatState.getStorageInfo());
  };

  const handleClearChat = () => {
    if (window.confirm('Clear all chat history?')) {
      chatState.clearMessages();
      setStorageInfo(chatState.getStorageInfo());
    }
  };

  const handleExport = () => {
    chatState.exportHistory();
  };

  const handleFAQClick = (question) => {
    setInput(question);
    setShowFAQ(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{ 
      flex: 1, 
      display: 'flex', 
      flexDirection: 'row',
      maxWidth: '1400px',
      margin: '0 auto',
      width: '100%',
      padding: '24px',
      gap: '24px',
      overflow: 'hidden'
    }}>
      {/* Main Chat Area */}
      <div style={{ 
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        minWidth: 0
      }}>
        {/* Storage Info Bar */}
        {storageInfo && storageInfo.messageCount > 0 && (
          <div style={{
            padding: '12px 16px',
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            borderRadius: '12px',
            marginBottom: '16px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            fontSize: '13px',
            color: '#475569',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
            border: '1px solid rgba(255, 255, 255, 0.8)'
          }}>
            <span style={{ 
              fontWeight: '500',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <span style={{ fontSize: '16px' }}>💾</span>
              <span>{storageInfo.messageCount} messages saved ({storageInfo.storageSizeKB}KB)</span>
            </span>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button onClick={() => setShowFAQ(!showFAQ)} style={{
                padding: '8px 16px',
                fontSize: '13px',
                fontWeight: '600',
                background: showFAQ ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'white',
                color: showFAQ ? 'white' : '#667eea',
                border: showFAQ ? 'none' : '2px solid #667eea',
                borderRadius: '8px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: showFAQ ? '0 4px 12px rgba(102, 126, 234, 0.3)' : 'none'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-2px)';
                if (!showFAQ) e.target.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                if (!showFAQ) e.target.style.color = 'white';
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0)';
                if (!showFAQ) e.target.style.background = 'white';
                if (!showFAQ) e.target.style.color = '#667eea';
              }}>
                {showFAQ ? '✕ Hide FAQs' : '💬 FAQs'}
              </button>
              <button onClick={handleExport} style={{
                padding: '8px 16px',
                fontSize: '13px',
                fontWeight: '600',
                background: 'white',
                color: '#10b981',
                border: '2px solid #10b981',
                borderRadius: '8px',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.background = '#10b981';
                e.target.style.color = 'white';
                e.target.style.boxShadow = '0 4px 12px rgba(16, 185, 129, 0.3)';
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0)';
                e.target.style.background = 'white';
                e.target.style.color = '#10b981';
                e.target.style.boxShadow = 'none';
              }}>
                📥 Export
              </button>
              <button onClick={handleClearChat} style={{
                padding: '8px 16px',
                fontSize: '13px',
                fontWeight: '600',
                background: 'white',
                color: '#ef4444',
                border: '2px solid #ef4444',
                borderRadius: '8px',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.background = '#ef4444';
                e.target.style.color = 'white';
                e.target.style.boxShadow = '0 4px 12px rgba(239, 68, 68, 0.3)';
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0)';
                e.target.style.background = 'white';
                e.target.style.color = '#ef4444';
                e.target.style.boxShadow = 'none';
              }}>
                🗑️ Clear
              </button>
            </div>
          </div>
        )}

        <div style={{
          flex: 1,
          overflowY: 'auto',
          marginBottom: '20px',
          borderRadius: '16px',
          padding: '24px',
          background: 'rgba(255, 255, 255, 0.7)',
          backdropFilter: 'blur(10px)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          border: '1px solid rgba(255, 255, 255, 0.9)'
        }}>
          {messages.length === 0 ? (
            <div style={{ 
              textAlign: 'center', 
              color: '#64748b', 
              padding: '40px 20px',
              maxWidth: '600px',
              margin: '0 auto'
            }}>
              <div style={{
                fontSize: '64px',
                marginBottom: '24px',
                animation: 'float 3s ease-in-out infinite'
              }}>👋</div>
              <h2 style={{ 
                fontSize: '32px', 
                marginBottom: '16px',
                fontWeight: '700',
                color: '#1e293b'
              }}>Welcome to AI Helpdesk!</h2>
              <p style={{
                fontSize: '16px',
                marginBottom: '32px',
                color: '#64748b',
                lineHeight: '1.6'
              }}>Ask me anything about your helpdesk topics and I'll provide detailed, helpful answers.</p>
              <div style={{ 
                marginTop: '40px',
                padding: '24px',
                background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
                borderRadius: '16px',
                textAlign: 'left',
                border: '2px solid rgba(102, 126, 234, 0.2)'
              }}>
                <p style={{ 
                  fontWeight: '700', 
                  marginBottom: '20px',
                  fontSize: '18px',
                  color: '#667eea'
                }}>💡 I can help you with:</p>
                <div style={{ 
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                  gap: '16px'
                }}>
                  {[
                    { icon: '📋', text: 'Lists of features and options' },
                    { icon: '🔧', text: 'Step-by-step configuration guides' },
                    { icon: '📖', text: 'Definitions and explanations' },
                    { icon: '⚖️', text: 'Comparisons between options' },
                    { icon: '🔍', text: 'Troubleshooting issues' },
                    { icon: '💬', text: 'Best practices and tips' }
                  ].map((item, idx) => (
                    <div key={idx} style={{
                      padding: '12px 16px',
                      background: 'white',
                      borderRadius: '10px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      fontSize: '14px',
                      color: '#475569',
                      fontWeight: '500',
                      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)'
                    }}>
                      <span style={{ fontSize: '20px' }}>{item.icon}</span>
                      <span>{item.text}</span>
                    </div>
                  ))}
                </div>
              </div>
              <p style={{ 
                fontSize: '13px', 
                marginTop: '32px',
                color: '#94a3b8',
                fontWeight: '500'
              }}>
                💾 Your chat history is automatically saved locally
              </p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={msg.id || idx} style={{
                marginBottom: '20px',
                padding: '20px',
                borderRadius: '16px',
                background: msg.role === 'user' 
                  ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)' 
                  : (msg.isError ? 'rgba(239, 68, 68, 0.1)' : 'white'),
                border: msg.role === 'user' 
                  ? '2px solid rgba(102, 126, 234, 0.3)' 
                  : (msg.isError ? '2px solid rgba(239, 68, 68, 0.3)' : '1px solid rgba(226, 232, 240, 0.8)'),
                boxShadow: msg.role === 'user' 
                  ? '0 4px 16px rgba(102, 126, 234, 0.15)' 
                  : '0 2px 12px rgba(0, 0, 0, 0.08)',
                textAlign: 'left',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = msg.role === 'user' 
                  ? '0 8px 24px rgba(102, 126, 234, 0.2)' 
                  : '0 4px 20px rgba(0, 0, 0, 0.12)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = msg.role === 'user' 
                  ? '0 4px 16px rgba(102, 126, 234, 0.15)' 
                  : '0 2px 12px rgba(0, 0, 0, 0.08)';
              }}>
                <div style={{ 
                  fontWeight: '600', 
                  marginBottom: '12px',
                  color: msg.role === 'user' ? '#667eea' : (msg.isError ? '#ef4444' : '#1e293b'),
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: '8px',
                  fontSize: '14px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                    <span style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '8px',
                      fontSize: '15px'
                    }}>
                      <span style={{ fontSize: '20px' }}>{msg.role === 'user' ? '👤' : '🤖'}</span>
                      <span>{msg.role === 'user' ? 'You' : 'AI Assistant'}</span>
                    </span>
                    {msg.module && <span style={{ 
                      fontSize: '11px',
                      background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                      color: 'white',
                      padding: '4px 10px',
                      borderRadius: '6px',
                      fontWeight: '600',
                      boxShadow: '0 2px 8px rgba(16, 185, 129, 0.3)'
                    }}>
                      {msg.module}
                    </span>}
                  </div>
                  {msg.duration && <span style={{ 
                    fontSize: '12px',
                    color: '#94a3b8',
                    fontWeight: '500',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}>
                    <span>⚡</span>
                    <span>{(msg.duration / 1000).toFixed(1)}s</span>
                  </span>}
                </div>
                {msg.role === 'assistant' && !msg.isError ? (
                  <ResponseFormatter content={msg.content} queryType={msg.queryType} />
                ) : (
                  <div style={{ 
                    whiteSpace: 'pre-wrap',
                    lineHeight: '1.6',
                    color: '#475569',
                    fontSize: '15px'
                  }}>{msg.content}</div>
                )}
              </div>
            ))
          )}
          {loading && (
            <div style={{ 
              textAlign: 'center', 
              padding: '24px',
              background: 'white',
              borderRadius: '16px',
              marginTop: '16px',
              boxShadow: '0 4px 16px rgba(102, 126, 234, 0.15)',
              border: '2px solid rgba(102, 126, 234, 0.2)'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '12px',
                marginBottom: '16px'
              }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  border: '4px solid rgba(102, 126, 234, 0.2)',
                  borderTopColor: '#667eea',
                  animation: 'spin 1s linear infinite'
                }}></div>
                <p style={{ 
                  color: '#667eea', 
                  fontWeight: '600',
                  fontSize: '15px',
                  margin: 0
                }}>Analyzing your question...</p>
              </div>
              <div style={{
                width: '100%',
                height: '6px',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderRadius: '3px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: '40%',
                  height: '100%',
                  background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                  animation: 'loading 1.5s ease-in-out infinite',
                  boxShadow: '0 0 10px rgba(102, 126, 234, 0.5)'
                }}></div>
              </div>
            </div>
          )}
        </div>
        
        <div style={{ 
          display: 'flex', 
          gap: '12px',
          padding: '16px',
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          borderRadius: '16px',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
          border: '1px solid rgba(255, 255, 255, 0.9)'
        }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask anything... (e.g., 'How do I configure inventory?' or 'What are the types of users?')"
            disabled={loading}
            style={{
              flex: 1,
              padding: '16px 20px',
              borderRadius: '12px',
              border: '2px solid #e2e8f0',
              fontSize: '15px',
              transition: 'all 0.3s ease',
              outline: 'none',
              backgroundColor: 'white',
              color: '#1e293b',
              fontFamily: 'inherit'
            }}
            onFocus={(e) => {
              e.target.style.borderColor = '#667eea';
              e.target.style.boxShadow = '0 0 0 4px rgba(102, 126, 234, 0.1)';
            }}
            onBlur={(e) => {
              e.target.style.borderColor = '#e2e8f0';
              e.target.style.boxShadow = 'none';
            }}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            style={{
              padding: '16px 32px',
              background: loading || !input.trim() 
                ? '#cbd5e1' 
                : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
              fontSize: '15px',
              fontWeight: '700',
              transition: 'all 0.3s ease',
              minWidth: '120px',
              boxShadow: loading || !input.trim() 
                ? 'none' 
                : '0 4px 16px rgba(102, 126, 234, 0.4)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}
            onMouseEnter={(e) => {
              if (!loading && input.trim()) {
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.5)';
              }
            }}
            onMouseLeave={(e) => {
              if (!loading && input.trim()) {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 4px 16px rgba(102, 126, 234, 0.4)';
              }
            }}
          >
            {loading ? (
              <>
                <span style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid rgba(255, 255, 255, 0.3)',
                  borderTopColor: 'white',
                  borderRadius: '50%',
                  animation: 'spin 0.8s linear infinite'
                }}></span>
                <span>Sending...</span>
              </>
            ) : (
              <>
                <span>Send</span>
                <span style={{ fontSize: '18px' }}>🚀</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* FAQ Sidebar */}
      {showFAQ && (
        <div style={{ 
          width: '380px',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          animation: 'slideInRight 0.3s ease-out'
        }}>
          <FAQPanel onQuestionClick={handleFAQClick} />
        </div>
      )}
    </div>
  );
}
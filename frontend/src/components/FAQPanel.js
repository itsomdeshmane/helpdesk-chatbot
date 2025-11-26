/**
 * FAQ Panel Component
 * Displays frequently asked questions
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const FAQPanel = ({ onQuestionClick }) => {
  const [faqs, setFaqs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedModule, setSelectedModule] = useState('all');
  const [modules, setModules] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    loadFAQs();
  }, [selectedModule]);

  const loadFAQs = async () => {
    try {
      setLoading(true);
      const url = selectedModule === 'all' 
        ? '/analytics/faq?limit=10'
        : `/analytics/faq?module=${selectedModule}&limit=10`;
      
      const response = await axios.get(url);
      const faqData = response.data.faqs || [];
      setFaqs(faqData);
      setLastUpdated(new Date());
      
      // Extract unique modules from FAQs
      const uniqueModules = [...new Set(faqData.map(faq => faq.module).filter(Boolean))];
      setModules(uniqueModules);
    } catch (error) {
      console.error('Error loading FAQs:', error);
      setFaqs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuestionClick = (question) => {
    if (onQuestionClick) {
      onQuestionClick(question);
    }
  };

  if (loading) {
    return (
      <div style={{ 
        padding: '32px', 
        textAlign: 'center', 
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        borderRadius: '16px',
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)',
        border: '1px solid rgba(255, 255, 255, 0.9)'
      }}>
        <div style={{
          width: '48px',
          height: '48px',
          margin: '0 auto 16px',
          borderRadius: '50%',
          border: '4px solid rgba(102, 126, 234, 0.2)',
          borderTopColor: '#667eea',
          animation: 'spin 1s linear infinite'
        }}></div>
        <p style={{ 
          color: '#667eea', 
          fontWeight: '600',
          fontSize: '14px',
          margin: 0
        }}>Loading FAQs...</p>
      </div>
    );
  }

  return (
    <div style={{ 
      padding: '24px',
      background: 'rgba(255, 255, 255, 0.95)',
      backdropFilter: 'blur(10px)',
      borderRadius: '16px',
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
      border: '1px solid rgba(255, 255, 255, 0.9)',
      height: '100%'
    }}>
      <div style={{
        marginBottom: '24px'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          marginBottom: '12px'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '20px',
            boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)'
          }}>
            💬
          </div>
          <div style={{ flex: 1 }}>
            <h3 style={{ 
              margin: '0',
              fontSize: '20px',
              fontWeight: '700',
              color: '#1e293b'
            }}>
              Top 10 Questions
            </h3>
            <p style={{
              margin: '4px 0 0 0',
              fontSize: '12px',
              color: '#64748b',
              fontWeight: '500'
            }}>
              Most frequently asked by users
            </p>
          </div>
          <button
            onClick={(e) => {
              e.stopPropagation();
              loadFAQs();
            }}
            disabled={loading}
            style={{
              padding: '10px',
              background: loading ? '#e2e8f0' : 'white',
              border: '2px solid #e2e8f0',
              borderRadius: '8px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '16px',
              transition: 'all 0.3s ease',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '40px',
              height: '40px'
            }}
            onMouseEnter={(e) => {
              if (!loading) {
                e.target.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                e.target.style.borderColor = '#667eea';
                e.target.style.transform = 'rotate(180deg)';
              }
            }}
            onMouseLeave={(e) => {
              if (!loading) {
                e.target.style.background = 'white';
                e.target.style.borderColor = '#e2e8f0';
                e.target.style.transform = 'rotate(0deg)';
              }
            }}
            title="Refresh FAQs"
          >
            <span style={{
              display: 'inline-block',
              animation: loading ? 'spin 1s linear infinite' : 'none'
            }}>
              🔄
            </span>
          </button>
        </div>
        
        {/* Module Filter */}
        {modules.length > 0 && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginTop: '16px'
          }}>
            <label style={{
              fontSize: '13px',
              fontWeight: '600',
              color: '#475569'
            }}>
              Filter:
            </label>
            <select
              value={selectedModule}
              onChange={(e) => setSelectedModule(e.target.value)}
              style={{
                flex: 1,
                padding: '8px 12px',
                borderRadius: '8px',
                border: '2px solid #e2e8f0',
                fontSize: '13px',
                fontWeight: '500',
                color: '#1e293b',
                backgroundColor: 'white',
                cursor: 'pointer',
                outline: 'none',
                transition: 'all 0.3s ease'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#667eea';
                e.target.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.1)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#e2e8f0';
                e.target.style.boxShadow = 'none';
              }}
            >
              <option value="all">All Modules</option>
              {modules.map((module) => (
                <option key={module} value={module}>
                  {module}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div>
      {faqs.length === 0 ? (
        <div style={{
          padding: '24px',
          background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)',
          borderRadius: '12px',
          textAlign: 'center',
          border: '2px dashed rgba(102, 126, 234, 0.2)'
        }}>
          <div style={{ fontSize: '40px', marginBottom: '12px' }}>📚</div>
          <p style={{ 
            color: '#64748b', 
            fontSize: '14px',
            lineHeight: '1.6',
            margin: 0
          }}>
            No FAQs available yet. Start asking questions and the most popular ones will appear here!
          </p>
        </div>
      ) : (
        <>
        <div style={{ 
          display: 'flex',
          flexDirection: 'column',
          gap: '12px'
        }}>
          {faqs.map((faq, index) => (
            <div key={index} style={{
              backgroundColor: 'white',
              padding: '16px',
              borderRadius: '12px',
              border: '2px solid #e2e8f0',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)',
              position: 'relative'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#667eea';
              e.currentTarget.style.transform = 'translateX(4px)';
              e.currentTarget.style.boxShadow = '0 4px 16px rgba(102, 126, 234, 0.2)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#e2e8f0';
              e.currentTarget.style.transform = 'translateX(0)';
              e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.05)';
            }}
            onClick={() => handleQuestionClick(faq.question)}>
              {/* Rank Badge */}
              <div style={{
                position: 'absolute',
                top: '-8px',
                left: '-8px',
                width: '28px',
                height: '28px',
                borderRadius: '50%',
                background: index < 3 
                  ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' 
                  : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '12px',
                fontWeight: '700',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
                border: '2px solid white'
              }}>
                {index + 1}
              </div>
              
              <div style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px'
              }}>
                <span style={{
                  fontSize: '20px',
                  minWidth: '28px',
                  marginTop: '2px'
                }}>
                  {index < 3 ? '🔥' : '❓'}
                </span>
                <div style={{ flex: 1 }}>
                  <div style={{
                    fontWeight: '600',
                    color: '#1e293b',
                    fontSize: '14px',
                    marginBottom: '10px',
                    lineHeight: '1.5'
                  }}>
                    {faq.question}
                  </div>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    flexWrap: 'wrap'
                  }}>
                    {faq.module && (
                      <span style={{
                        fontSize: '11px',
                        background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                        color: 'white',
                        padding: '4px 10px',
                        borderRadius: '6px',
                        fontWeight: '600',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        boxShadow: '0 2px 8px rgba(16, 185, 129, 0.2)'
                      }}>
                        <span>📁</span>
                        <span>{faq.module}</span>
                      </span>
                    )}
                    {faq.frequency && (
                      <span style={{
                        fontSize: '11px',
                        background: 'rgba(102, 126, 234, 0.1)',
                        color: '#667eea',
                        padding: '4px 10px',
                        borderRadius: '6px',
                        fontWeight: '600',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}>
                        <span>🔢</span>
                        <span>Asked {faq.frequency}x</span>
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
        </>
      )}
      
      {/* Last Updated Timestamp */}
      {lastUpdated && faqs.length > 0 && (
        <div style={{
          marginTop: '16px',
          padding: '12px',
          background: 'rgba(102, 126, 234, 0.05)',
          borderRadius: '8px',
          textAlign: 'center',
          fontSize: '12px',
          color: '#64748b',
          fontWeight: '500'
        }}>
          <span>🕒 Updated: {lastUpdated.toLocaleTimeString()}</span>
        </div>
      )}
      </div>
    </div>
  );
};

export default FAQPanel;




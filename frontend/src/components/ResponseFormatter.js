/**
 * Response Formatter Component
 * Renders AI responses with proper formatting
 */
import React from 'react';

const ResponseFormatter = ({ content, queryType }) => {
  
  // Function to parse and render formatted content
  const renderFormattedContent = () => {
    const lines = content.split('\n');
    const elements = [];
    let currentList = [];
    let currentListType = null;
    let inCodeBlock = false;
    let codeBlock = [];

    const flushList = () => {
      if (currentList.length > 0) {
        elements.push(
          <ul key={`list-${elements.length}`} style={{ 
            marginLeft: '24px', 
            marginBottom: '16px',
            lineHeight: '1.8',
            listStyleType: 'none',
            paddingLeft: 0
          }}>
            {currentList.map((item, idx) => (
              <li key={idx} style={{ 
                marginBottom: '10px',
                paddingLeft: '28px',
                position: 'relative',
                color: '#475569'
              }}>
                <span style={{
                  position: 'absolute',
                  left: 0,
                  color: '#667eea',
                  fontWeight: 'bold',
                  fontSize: '16px'
                }}>
                  {currentListType === 'numbered' ? `${idx + 1}.` : '•'}
                </span>
                {item}
              </li>
            ))}
          </ul>
        );
        currentList = [];
        currentListType = null;
      }
    };

    lines.forEach((line, idx) => {
      const trimmed = line.trim();

      // Code blocks
      if (trimmed.startsWith('```')) {
        if (inCodeBlock) {
          elements.push(
            <pre key={`code-${elements.length}`} style={{
              background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
              padding: '16px',
              borderRadius: '12px',
              overflow: 'auto',
              marginBottom: '16px',
              fontSize: '13px',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
              border: '1px solid rgba(102, 126, 234, 0.2)'
            }}>
              <code style={{
                color: '#e2e8f0',
                fontFamily: 'Consolas, Monaco, "Courier New", monospace',
                lineHeight: '1.6'
              }}>{codeBlock.join('\n')}</code>
            </pre>
          );
          codeBlock = [];
        }
        inCodeBlock = !inCodeBlock;
        return;
      }

      if (inCodeBlock) {
        codeBlock.push(line);
        return;
      }

      // Step headers (Step 1:, Step 2:, etc.)
      if (/^Step \d+:/i.test(trimmed)) {
        flushList();
        elements.push(
          <div key={`step-${elements.length}`} style={{
            fontWeight: '700',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            marginTop: '20px',
            marginBottom: '12px',
            fontSize: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span style={{
              width: '24px',
              height: '24px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '11px',
              fontWeight: '700',
              flexShrink: 0,
              WebkitTextFillColor: 'white'
            }}>
              {trimmed.match(/\d+/)[0]}
            </span>
            <span>{trimmed}</span>
          </div>
        );
        return;
      }

      // Numbered lists (1. , 2. , etc.)
      if (/^\d+\.\s/.test(trimmed)) {
        if (currentListType !== 'numbered') {
          flushList();
          currentListType = 'numbered';
        }
        currentList.push(trimmed.replace(/^\d+\.\s/, ''));
        return;
      }

      // Bullet points (- , • , *)
      if (/^[-•*]\s/.test(trimmed)) {
        if (currentListType !== 'bullet') {
          flushList();
          currentListType = 'bullet';
        }
        currentList.push(trimmed.replace(/^[-•*]\s/, ''));
        return;
      }

      // Headers (###, ##, #)
      if (trimmed.startsWith('#')) {
        flushList();
        const level = trimmed.match(/^#+/)[0].length;
        const text = trimmed.replace(/^#+\s*/, '');
        elements.push(
          <h3 key={`header-${elements.length}`} style={{
            fontSize: level === 1 ? '20px' : level === 2 ? '18px' : '16px',
            fontWeight: '700',
            marginTop: '20px',
            marginBottom: '12px',
            color: '#1e293b',
            paddingBottom: '8px',
            borderBottom: level === 1 ? '3px solid rgba(102, 126, 234, 0.3)' : 'none'
          }}>
            {text}
          </h3>
        );
        return;
      }

      // Bold text (**text**)
      if (trimmed.includes('**')) {
        flushList();
        const formatted = trimmed.split('**').map((part, i) => 
          i % 2 === 1 ? <strong key={i} style={{ 
            color: '#667eea',
            fontWeight: '700'
          }}>{part}</strong> : part
        );
        elements.push(
          <p key={`bold-${elements.length}`} style={{ 
            marginBottom: '12px', 
            lineHeight: '1.8',
            color: '#475569',
            fontSize: '15px'
          }}>
            {formatted}
          </p>
        );
        return;
      }

      // Empty lines
      if (!trimmed) {
        flushList();
        return;
      }

      // Regular paragraphs
      flushList();
      elements.push(
        <p key={`para-${elements.length}`} style={{ 
          marginBottom: '12px',
          lineHeight: '1.8',
          color: '#475569',
          fontSize: '15px'
        }}>
          {trimmed}
        </p>
      );
    });

    flushList();
    return elements;
  };

  return (
    <div style={{ 
      fontSize: '15px',
      color: '#475569',
      lineHeight: '1.8'
    }}>
      {renderFormattedContent()}
    </div>
  );
};

export default ResponseFormatter;




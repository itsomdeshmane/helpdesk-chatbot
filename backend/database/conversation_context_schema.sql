-- Conversation Context Tracking Table
-- Stores extracted entities, topics, and context from conversations
-- Works dynamically for ANY conversation topic

CREATE TABLE IF NOT EXISTS conversation_context (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    message_order INT NOT NULL COMMENT 'Which message this context is from',
    
    -- Extracted entities/topics (AI-generated)
    main_topic VARCHAR(500) DEFAULT NULL COMMENT 'Primary topic/entity discussed',
    entities JSON DEFAULT NULL COMMENT 'All entities mentioned (JSON array)',
    keywords JSON DEFAULT NULL COMMENT 'Important keywords (JSON array)',
    
    -- Context type classification
    context_type VARCHAR(50) DEFAULT 'general' COMMENT 'module, entity, process, feature, etc.',
    confidence FLOAT DEFAULT 0.0 COMMENT 'AI confidence score (0-1)',
    
    -- Metadata
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_conversation_order (conversation_id, message_order),
    INDEX idx_main_topic (main_topic),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Context resolution cache
-- Speeds up pronoun resolution by caching entity references
CREATE TABLE IF NOT EXISTS context_resolution_cache (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    
    -- What the user said
    pronoun VARCHAR(100) NOT NULL COMMENT 'it, this, that, the module, etc.',
    query_text TEXT NOT NULL COMMENT 'Full query containing the pronoun',
    
    -- What it refers to
    resolved_entity VARCHAR(500) NOT NULL COMMENT 'What the pronoun refers to',
    resolved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- TTL for cache
    expires_at TIMESTAMP DEFAULT NULL,
    
    INDEX idx_conversation_pronoun (conversation_id, pronoun),
    INDEX idx_expires (expires_at),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


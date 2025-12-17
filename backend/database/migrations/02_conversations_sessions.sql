-- ============================================================================
-- MIGRATION: Conversation Sessions
-- ============================================================================
-- Adds conversation session management and multi-turn chat support
-- Version: 2.0
-- Date: 2025-12-03
-- ============================================================================

USE helpdesk_db;

-- Conversations table (tracks sessions)
CREATE TABLE IF NOT EXISTS conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL UNIQUE COMMENT 'Unique session identifier (UUID)',
    tenant_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) DEFAULT NULL COMMENT 'Optional user identification',
    title VARCHAR(500) DEFAULT NULL COMMENT 'Auto-generated conversation title',
    status VARCHAR(50) DEFAULT 'active' COMMENT 'active, archived, expired',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT NULL COMMENT 'Session expiry time',
    INDEX idx_session (session_id),
    INDEX idx_tenant (tenant_id),
    INDEX idx_status (status),
    INDEX idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add conversation support to chat_interactions if not exists
ALTER TABLE chat_interactions
ADD COLUMN IF NOT EXISTS conversation_id INT DEFAULT NULL AFTER id,
ADD COLUMN IF NOT EXISTS message_order INT DEFAULT 0 COMMENT 'Order of message in conversation' AFTER response_time,
ADD COLUMN IF NOT EXISTS context_used TEXT DEFAULT NULL COMMENT 'JSON: previous messages used as context' AFTER message_order;

-- Add indexes if they don't exist
ALTER TABLE chat_interactions
ADD INDEX IF NOT EXISTS idx_conversation (conversation_id),
ADD INDEX IF NOT EXISTS idx_message_order (conversation_id, message_order);

-- Verification
SELECT 'Conversation tables created successfully' AS status;
SELECT COUNT(*) as conversation_count FROM conversations;












-- Migration: Add soft delete support for conversations
-- Allows users to "delete" conversations from their view while keeping data for learning

USE helpdesk_db;

-- Add soft delete columns to conversations table
ALTER TABLE conversations 
ADD COLUMN deleted_by_user BOOLEAN DEFAULT FALSE COMMENT 'User deleted this conversation (soft delete)',
ADD COLUMN deleted_at TIMESTAMP NULL COMMENT 'When user deleted this conversation',
ADD COLUMN permanent_delete_after TIMESTAMP NULL COMMENT 'When to permanently delete (for compliance)';

-- Add index for efficient queries
ALTER TABLE conversations
ADD INDEX idx_deleted_by_user (deleted_by_user, user_id);

-- Update status explanation
ALTER TABLE conversations 
MODIFY COLUMN status VARCHAR(50) DEFAULT 'active' 
COMMENT 'active, archived, expired (deleted_by_user flag used for soft delete)';

COMMIT;

-- Notes:
-- 1. deleted_by_user=TRUE: Hidden from user's view, kept for learning
-- 2. permanent_delete_after: Set to 90 days after deletion for GDPR compliance
-- 3. Background job will hard-delete records after permanent_delete_after date


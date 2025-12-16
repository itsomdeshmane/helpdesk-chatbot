-- ============================================================================
-- MIGRATION: Question Generation & Clarity Detection
-- ============================================================================
-- Adds tables for AI-generated questions and query clarification
-- Version: 4.0
-- Date: 2025-12-03
-- ============================================================================

USE helpdesk_db;

-- Generated questions table for level-wise module questions
CREATE TABLE IF NOT EXISTS generated_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    module_name VARCHAR(100) NOT NULL,
    difficulty_level VARCHAR(20) NOT NULL COMMENT 'beginner, intermediate, advanced',
    question TEXT NOT NULL,
    tenant_id VARCHAR(255) DEFAULT 'default',
    is_active BOOLEAN DEFAULT TRUE,
    times_asked INT DEFAULT 0 COMMENT 'How many times this question was asked',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_module_level (module_name, difficulty_level),
    INDEX idx_tenant (tenant_id),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Query clarifications table to track when clarification was needed
CREATE TABLE IF NOT EXISTS query_clarifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    original_query TEXT NOT NULL,
    clarity_score FLOAT DEFAULT 0.0 COMMENT 'Clarity score 0-1',
    issues TEXT COMMENT 'JSON array of clarity issues',
    clarifying_questions TEXT COMMENT 'JSON array of questions asked',
    user_clarification TEXT COMMENT 'User response to clarification',
    was_resolved BOOLEAN DEFAULT FALSE COMMENT 'Whether user provided clarification',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tenant_created (tenant_id, created_at),
    INDEX idx_resolved (was_resolved)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Verification
SELECT 'Question generation tables created successfully' AS status;
SELECT COUNT(*) as question_count FROM generated_questions;










-- Migration: Add Feedback System Tables
-- Version: 05
-- Description: Create tables for user feedback collection and analytics

-- Feedback table
CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    helpful TINYINT(1) DEFAULT 0,
    rating INT DEFAULT NULL,
    feedback_text TEXT,
    feedback_type VARCHAR(50) DEFAULT 'general',
    query_text TEXT,
    response_text TEXT,
    user_id VARCHAR(255) DEFAULT NULL,
    tenant_id VARCHAR(255) DEFAULT 'default',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_feedback_session (session_id),
    INDEX idx_feedback_helpful (helpful),
    INDEX idx_feedback_type (feedback_type),
    INDEX idx_feedback_tenant (tenant_id),
    INDEX idx_feedback_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Feedback aggregates (for faster analytics)
CREATE TABLE IF NOT EXISTS feedback_daily_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    tenant_id VARCHAR(255) DEFAULT 'default',
    total_feedback INT DEFAULT 0,
    positive_feedback INT DEFAULT 0,
    negative_feedback INT DEFAULT 0,
    avg_rating DECIMAL(3,2) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_date_tenant (date, tenant_id),
    INDEX idx_stats_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Quality metrics table (for tracking answer quality over time)
CREATE TABLE IF NOT EXISTS quality_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255),
    query_text TEXT,
    overall_score DECIMAL(4,3) DEFAULT NULL,
    groundedness_score DECIMAL(4,3) DEFAULT NULL,
    relevance_score DECIMAL(4,3) DEFAULT NULL,
    completeness_score DECIMAL(4,3) DEFAULT NULL,
    confidence_level VARCHAR(20) DEFAULT NULL,
    issues JSON DEFAULT NULL,
    needs_escalation TINYINT(1) DEFAULT 0,
    tenant_id VARCHAR(255) DEFAULT 'default',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_quality_session (session_id),
    INDEX idx_quality_score (overall_score),
    INDEX idx_quality_tenant (tenant_id),
    INDEX idx_quality_escalation (needs_escalation)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cache metrics table (for monitoring cache performance)
CREATE TABLE IF NOT EXISTS cache_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    cache_type VARCHAR(50) NOT NULL,
    hits INT DEFAULT 0,
    misses INT DEFAULT 0,
    hit_rate DECIMAL(5,4) DEFAULT NULL,
    avg_retrieval_time_ms DECIMAL(10,2) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_date_type (date, cache_type),
    INDEX idx_cache_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert initial feedback types
INSERT IGNORE INTO response_patterns (query_type, pattern_template, success_rate, usage_count)
VALUES 
    ('feedback_positive', 'User marked response as helpful', 0.0, 0),
    ('feedback_negative', 'User marked response as not helpful', 0.0, 0),
    ('feedback_incorrect', 'User reported incorrect information', 0.0, 0),
    ('feedback_incomplete', 'User reported incomplete answer', 0.0, 0),
    ('feedback_unclear', 'User reported unclear explanation', 0.0, 0);


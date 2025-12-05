-- ============================================================================
-- Migration 09: Add Missing Tables for Metadata Extraction
-- Description: Add query_patterns and query_keywords tables
-- Date: 2025-12-05
-- ============================================================================

-- Query patterns table (for metadata extractor)
CREATE TABLE IF NOT EXISTS query_patterns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query_type VARCHAR(100) NOT NULL,
    keyword TEXT,
    pattern TEXT,
    tenant_id VARCHAR(255) DEFAULT 'default',
    usage_count INT DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_query_type (query_type),
    INDEX idx_tenant (tenant_id),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Query patterns for better understanding';

-- Query keywords table (for metadata extractor)
CREATE TABLE IF NOT EXISTS query_keywords (
    id INT AUTO_INCREMENT PRIMARY KEY,
    keyword VARCHAR(100) NOT NULL,
    query_type VARCHAR(50) DEFAULT 'general',
    context VARCHAR(255),
    tenant_id VARCHAR(255) DEFAULT 'default',
    priority INT DEFAULT 1,
    usage_count INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_keyword (keyword),
    INDEX idx_keyword (keyword),
    INDEX idx_query_type (query_type),
    INDEX idx_tenant (tenant_id),
    INDEX idx_priority (priority DESC),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Keywords for query classification';

-- Frequently asked questions table
CREATE TABLE IF NOT EXISTS frequently_asked_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question VARCHAR(500) NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(100) DEFAULT 'general',
    tenant_id VARCHAR(255) DEFAULT 'default',
    ask_count INT DEFAULT 0,
    helpful_count INT DEFAULT 0,
    not_helpful_count INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_question (question(255)),
    INDEX idx_category (category),
    INDEX idx_tenant (tenant_id),
    INDEX idx_ask_count (ask_count DESC),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Frequently asked questions from documentation';

-- Verification
-- SELECT COUNT(*) FROM query_patterns;
-- SELECT COUNT(*) FROM query_keywords;
-- SELECT COUNT(*) FROM frequently_asked_questions;


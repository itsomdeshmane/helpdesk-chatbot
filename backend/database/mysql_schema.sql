-- MySQL Schema for Chat History and Training Database

CREATE DATABASE IF NOT EXISTS helpdesk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE helpdesk_db;

-- Chat interactions table
CREATE TABLE IF NOT EXISTS chat_interactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    module VARCHAR(255) DEFAULT NULL,
    helpful INT DEFAULT 0 COMMENT 'User feedback: 1=helpful, 0=neutral, -1=not helpful',
    response_time FLOAT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tenant_created (tenant_id, created_at),
    INDEX idx_module (module)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- FAQ questions table
CREATE TABLE IF NOT EXISTS faq_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(255) DEFAULT NULL,
    module VARCHAR(255) DEFAULT NULL,
    source_document VARCHAR(500) DEFAULT NULL,
    popularity INT DEFAULT 0 COMMENT 'How often this is asked',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_faq_category (category),
    INDEX idx_faq_module (module)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Response patterns table
CREATE TABLE IF NOT EXISTS response_patterns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query_type VARCHAR(255) NOT NULL COMMENT 'list, step-by-step, definition, etc.',
    pattern_template TEXT NOT NULL,
    success_rate FLOAT DEFAULT 0.0,
    usage_count INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Query type patterns table for dynamic keyword detection
CREATE TABLE IF NOT EXISTS query_type_patterns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query_type VARCHAR(100) NOT NULL COMMENT 'Type: list, step-by-step, definition, etc.',
    keyword VARCHAR(255) NOT NULL COMMENT 'Keyword to match in query',
    priority INT DEFAULT 1 COMMENT 'Higher priority = checked first',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_query_type (query_type),
    INDEX idx_active_priority (is_active, priority DESC),
    UNIQUE KEY unique_type_keyword (query_type, keyword)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ERP modules table for dynamic module classification
CREATE TABLE IF NOT EXISTS erp_modules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    module_name VARCHAR(100) NOT NULL COMMENT 'Module name (e.g., Finance, HR, Sales)',
    module_code VARCHAR(50) NOT NULL COMMENT 'Short code for module',
    description TEXT COMMENT 'Description of the module',
    keywords TEXT COMMENT 'Keywords associated with this module (comma-separated)',
    is_active BOOLEAN DEFAULT TRUE,
    priority INT DEFAULT 1 COMMENT 'Display/matching priority',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_module_name (module_name),
    UNIQUE KEY unique_module_code (module_code),
    INDEX idx_active_priority (is_active, priority DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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



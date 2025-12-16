-- ============================================================================
-- COMPLETE DATABASE SCHEMA FOR HELPDESK CHATBOT
-- ============================================================================
-- This file contains the complete database schema with all tables
-- Safe to run multiple times (uses IF NOT EXISTS)
-- Last Updated: December 3, 2025
-- ============================================================================

-- Create database
CREATE DATABASE IF NOT EXISTS helpdesk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE helpdesk_db;

-- ============================================================================
-- SECTION 1: AUTHENTICATION & USERS
-- ============================================================================

-- Users table for authentication and authorization
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role ENUM('admin', 'user', 'viewer') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    tenant_id VARCHAR(50) DEFAULT 'default',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_tenant_id (tenant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- SECTION 2: CONVERSATION MANAGEMENT
-- ============================================================================

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

-- Chat interactions table (linked to conversations)
CREATE TABLE IF NOT EXISTS chat_interactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT DEFAULT NULL COMMENT 'Links to conversations table',
    tenant_id VARCHAR(255) NOT NULL,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    module VARCHAR(255) DEFAULT NULL,
    helpful INT DEFAULT 0 COMMENT 'User feedback: 1=helpful, 0=neutral, -1=not helpful',
    response_time FLOAT DEFAULT NULL,
    message_order INT DEFAULT 0 COMMENT 'Order of message in conversation',
    context_used TEXT DEFAULT NULL COMMENT 'JSON: previous messages used as context',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_conversation (conversation_id),
    INDEX idx_tenant_created (tenant_id, created_at),
    INDEX idx_module (module),
    INDEX idx_message_order (conversation_id, message_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- SECTION 3: AI-POWERED CONTEXT TRACKING
-- ============================================================================

-- Conversation context tracking table (AI-extracted entities and topics)
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

-- Context resolution cache (speeds up pronoun resolution)
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

-- ============================================================================
-- SECTION 4: KNOWLEDGE BASE & FAQ
-- ============================================================================

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

-- ============================================================================
-- SECTION 5: ERP MODULE & ENTITY MANAGEMENT
-- ============================================================================

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

-- ERP entities table for entity recognition in queries
CREATE TABLE IF NOT EXISTS erp_entities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entity_key VARCHAR(50) NOT NULL COMMENT 'Lowercase key for matching (e.g., item, customer)',
    entity_name VARCHAR(100) NOT NULL COMMENT 'Display name (e.g., Item, Customer)',
    entity_type VARCHAR(50) DEFAULT 'general' COMMENT 'Type: transactional, master, reference',
    description TEXT COMMENT 'Description of the entity',
    related_modules TEXT COMMENT 'Comma-separated list of related modules',
    is_active BOOLEAN DEFAULT TRUE,
    priority INT DEFAULT 1 COMMENT 'Matching priority',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_entity_key (entity_key),
    INDEX idx_active_priority (is_active, priority DESC),
    INDEX idx_entity_type (entity_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- SECTION 6: QUESTION GENERATION & CLARITY
-- ============================================================================

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

-- ============================================================================
-- SECTION 7: DEFAULT DATA
-- ============================================================================

-- Insert default ERP entities
INSERT INTO erp_entities (entity_key, entity_name, entity_type, description, related_modules, priority) VALUES
('item', 'Item', 'master', 'Product or service item in the system', 'Inventory,Purchasing,Sales,Manufacturing', 1),
('customer', 'Customer', 'master', 'Customer or client information', 'Sales,CRM,Finance', 1),
('vendor', 'Vendor', 'master', 'Supplier or vendor information', 'Purchasing,Finance', 1),
('supplier', 'Supplier', 'master', 'Supplier information (synonym for vendor)', 'Purchasing,Finance', 1),
('invoice', 'Invoice', 'transactional', 'Sales or purchase invoice', 'Finance,Sales,Purchasing', 1),
('order', 'Order', 'transactional', 'Sales or purchase order', 'Sales,Purchasing', 1),
('purchase', 'Purchase Order', 'transactional', 'Purchase order document', 'Purchasing,Finance', 1),
('sale', 'Sales Order', 'transactional', 'Sales order document', 'Sales,Finance', 1),
('employee', 'Employee', 'master', 'Employee information', 'HR,Payroll', 1),
('user', 'User', 'master', 'System user account', 'General,Administration', 1),
('inventory', 'Inventory', 'reference', 'Stock and inventory items', 'Inventory,Warehouse', 1),
('stock', 'Stock', 'reference', 'Inventory stock levels', 'Inventory,Warehouse', 1),
('product', 'Product', 'master', 'Product information', 'Sales,Inventory,Manufacturing', 1),
('quotation', 'Quotation', 'transactional', 'Sales quotation or quote', 'Sales,CRM', 2),
('warehouse', 'Warehouse', 'master', 'Warehouse location', 'Inventory,Warehouse', 2),
('payment', 'Payment', 'transactional', 'Payment transaction', 'Finance,Sales,Purchasing', 2),
('account', 'Account', 'master', 'Financial account', 'Finance,Accounting', 2),
('report', 'Report', 'reference', 'System report or analytics', 'Reporting,All Modules', 2)
ON DUPLICATE KEY UPDATE
    entity_name = VALUES(entity_name),
    description = VALUES(description);

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================










-- ============================================================================
-- HELPDESK CHATBOT - MASTER DATABASE SCHEMA
-- ============================================================================
-- Complete database schema for AI-powered helpdesk chatbot system
-- Includes: Authentication, Conversations, Metadata Learning, Feedback, Analytics
-- Version: 3.0.0
-- Date: January 17, 2025
-- Safe to run multiple times (uses IF NOT EXISTS)
-- ============================================================================

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS helpdesk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE helpdesk_db;

-- ============================================================================
-- SECTION 1: AUTHENTICATION & USER MANAGEMENT
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='User authentication and authorization';

-- User database connections (encrypted credentials)
CREATE TABLE IF NOT EXISTS user_database_connections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    tenant_id VARCHAR(100) NOT NULL,
    db_type VARCHAR(20) DEFAULT 'mysql' NOT NULL COMMENT 'mysql, postgresql, sqlserver',
    host VARCHAR(255) NOT NULL,
    port INT NOT NULL DEFAULT 3306,
    database_name VARCHAR(100) NOT NULL,
    username VARCHAR(100) NOT NULL,
    encrypted_password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_user_tenant (user_id, tenant_id),
    INDEX idx_tenant (tenant_id),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_tenant_connection (user_id, tenant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Encrypted database connection credentials per user';

-- ============================================================================
-- SECTION 2: CONVERSATION & SESSION MANAGEMENT
-- ============================================================================

-- Conversations table (session tracking)
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Conversation sessions and chat history';

-- Chat interactions (messages within conversations)
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Individual chat messages and interactions';

-- ============================================================================
-- SECTION 3: AI CONTEXT TRACKING & RESOLUTION
-- ============================================================================

-- Conversation context (AI-extracted entities and topics)
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
    
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_conversation_order (conversation_id, message_order),
    INDEX idx_main_topic (main_topic),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='AI-extracted context from conversations';

-- Context resolution cache (pronoun and reference resolution)
CREATE TABLE IF NOT EXISTS context_resolution_cache (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    
    pronoun VARCHAR(100) NOT NULL COMMENT 'it, this, that, the module, etc.',
    query_text TEXT NOT NULL COMMENT 'Full query containing the pronoun',
    resolved_entity VARCHAR(500) NOT NULL COMMENT 'What the pronoun refers to',
    resolved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT NULL,
    
    INDEX idx_conversation_pronoun (conversation_id, pronoun),
    INDEX idx_expires (expires_at),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Cache for pronoun and reference resolution';

-- ============================================================================
-- SECTION 4: KNOWLEDGE BASE & FAQ
-- ============================================================================

-- FAQ questions
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Frequently asked questions';

-- Response patterns
CREATE TABLE IF NOT EXISTS response_patterns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query_type VARCHAR(255) NOT NULL COMMENT 'list, step-by-step, definition, etc.',
    pattern_template TEXT NOT NULL,
    success_rate FLOAT DEFAULT 0.0,
    usage_count INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Response formatting patterns';

-- Query type patterns (dynamic keyword detection)
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Patterns for query type classification';

-- ============================================================================
-- SECTION 5: ERP MODULES & ENTITIES
-- ============================================================================

-- ERP modules
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='ERP module definitions';

-- ERP entities
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='ERP entity definitions for query understanding';

-- ============================================================================
-- SECTION 6: QUESTION GENERATION & CLARIFICATION
-- ============================================================================

-- Generated questions (level-wise module questions)
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='AI-generated questions for modules';

-- Query clarifications
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tracks unclear queries needing clarification';

-- ============================================================================
-- SECTION 7: FEEDBACK & QUALITY METRICS
-- ============================================================================

-- User feedback
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='User feedback on responses';

-- Feedback daily statistics
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Daily aggregated feedback statistics';

-- Quality metrics
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Answer quality tracking metrics';

-- Cache metrics
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Cache performance monitoring';

-- ============================================================================
-- SECTION 8: METADATA LEARNING SYSTEM (AI-Powered)
-- ============================================================================

-- Column metadata (semantic descriptions for database columns)
CREATE TABLE IF NOT EXISTS column_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    connection_id VARCHAR(100) NULL,
    database_name VARCHAR(100) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    column_name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    semantic_type VARCHAR(50) NULL COMMENT 'location, date, amount, identifier, etc.',
    examples TEXT NULL COMMENT 'JSON array of example values',
    is_sensitive BOOLEAN DEFAULT FALSE COMMENT 'Flag for PII/sensitive data',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NULL,
    updated_by VARCHAR(100) NULL,
    
    UNIQUE KEY unique_column_metadata (tenant_id, database_name, table_name, column_name),
    INDEX idx_tenant_db (tenant_id, database_name),
    INDEX idx_tenant_table (tenant_id, database_name, table_name),
    INDEX idx_connection (connection_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Semantic descriptions for database columns';

-- Table metadata
CREATE TABLE IF NOT EXISTS table_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    connection_id VARCHAR(100) NULL,
    database_name VARCHAR(100) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    business_purpose TEXT NULL COMMENT 'Business context and purpose',
    primary_entity VARCHAR(100) NULL COMMENT 'e.g., Customer, Order, Product',
    common_joins TEXT NULL COMMENT 'JSON array of common join patterns',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NULL,
    updated_by VARCHAR(100) NULL,
    
    UNIQUE KEY unique_table_metadata (tenant_id, database_name, table_name),
    INDEX idx_tenant_db (tenant_id, database_name),
    INDEX idx_connection (connection_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Semantic descriptions for database tables';

-- Relationship metadata
CREATE TABLE IF NOT EXISTS relationship_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    connection_id VARCHAR(100) NULL,
    database_name VARCHAR(100) NOT NULL,
    source_table VARCHAR(100) NOT NULL,
    source_column VARCHAR(100) NOT NULL,
    target_table VARCHAR(100) NOT NULL,
    target_column VARCHAR(100) NOT NULL,
    relationship_type VARCHAR(50) NOT NULL COMMENT 'one_to_many, many_to_one, etc.',
    description TEXT NULL,
    is_enforced BOOLEAN DEFAULT FALSE COMMENT 'Whether FK constraint exists',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NULL,
    
    INDEX idx_tenant_source (tenant_id, database_name, source_table),
    INDEX idx_tenant_target (tenant_id, database_name, target_table),
    INDEX idx_connection (connection_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Database relationship metadata';

-- Query patterns (common queries and examples)
CREATE TABLE IF NOT EXISTS query_patterns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    connection_id VARCHAR(100) NULL,
    database_name VARCHAR(100) NOT NULL,
    pattern_name VARCHAR(200) NOT NULL,
    description TEXT NULL,
    example_question TEXT NOT NULL COMMENT 'Natural language question',
    example_sql TEXT NOT NULL COMMENT 'Corresponding SQL',
    tables_involved TEXT NULL COMMENT 'JSON array of table names',
    usage_count INT DEFAULT 0,
    success_count INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NULL,
    
    INDEX idx_tenant_db (tenant_id, database_name),
    INDEX idx_active (tenant_id, is_active),
    INDEX idx_connection (connection_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Common query patterns and examples';

-- Semantic types reference
CREATE TABLE IF NOT EXISTS semantic_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    example_patterns TEXT NULL COMMENT 'JSON array of column name patterns',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Reference table for semantic column types';

-- Query learning data (AI learning from every query)
CREATE TABLE IF NOT EXISTS query_learning_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(100) NULL,
    
    -- Query details
    natural_language_query TEXT NOT NULL,
    generated_sql TEXT NULL,
    tables_used TEXT NULL COMMENT 'JSON array of table names',
    columns_used TEXT NULL COMMENT 'JSON array of column names',
    
    -- Execution results
    execution_success BOOLEAN DEFAULT FALSE,
    execution_time_ms INT NULL,
    rows_returned INT NULL,
    error_message TEXT NULL,
    
    -- User feedback
    user_feedback ENUM('positive', 'negative', 'neutral', 'no_feedback') DEFAULT 'no_feedback',
    user_rating INT NULL COMMENT '1-5 rating',
    user_comment TEXT NULL,
    
    -- Metadata improvements
    needs_metadata_improvement BOOLEAN DEFAULT FALSE,
    suggested_improvements TEXT NULL COMMENT 'JSON with suggestions',
    improvement_applied BOOLEAN DEFAULT FALSE,
    
    -- Context
    source_type VARCHAR(50) NULL COMMENT 'database, documents, clarification',
    confidence_score DECIMAL(5,2) NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_tenant_session (tenant_id, session_id),
    INDEX idx_tenant_user (tenant_id, user_id),
    INDEX idx_success (execution_success, created_at),
    INDEX idx_feedback (user_feedback, created_at),
    INDEX idx_improvement (needs_metadata_improvement, improvement_applied)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Records every query for AI learning';

-- Metadata quality metrics
CREATE TABLE IF NOT EXISTS metadata_quality_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    database_name VARCHAR(100) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    column_name VARCHAR(100) NULL COMMENT 'NULL means table-level metric',
    
    -- Quality metrics
    query_success_count INT DEFAULT 0,
    query_failure_count INT DEFAULT 0,
    positive_feedback_count INT DEFAULT 0,
    negative_feedback_count INT DEFAULT 0,
    
    -- Usage metrics
    times_used INT DEFAULT 0,
    last_used_at TIMESTAMP NULL,
    
    -- Calculated score
    quality_score DECIMAL(5,2) DEFAULT 0.00,
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_metadata_metric (tenant_id, database_name, table_name, column_name),
    INDEX idx_quality (quality_score),
    INDEX idx_usage (times_used, last_used_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Quality and usage tracking for metadata';

-- Metadata improvement suggestions (AI-generated)
CREATE TABLE IF NOT EXISTS metadata_improvement_suggestions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    database_name VARCHAR(100) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    column_name VARCHAR(100) NULL COMMENT 'NULL for table-level suggestions',
    
    -- Current and suggested state
    current_description TEXT NULL,
    suggested_description TEXT NOT NULL,
    suggestion_reason TEXT NULL,
    confidence_score DECIMAL(5,2) NULL,
    
    -- Source
    source_query_id INT NULL,
    based_on_queries_count INT DEFAULT 1,
    
    -- Status
    status ENUM('pending', 'approved', 'rejected', 'applied') DEFAULT 'pending',
    reviewed_by VARCHAR(100) NULL,
    reviewed_at TIMESTAMP NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_tenant_db (tenant_id, database_name),
    INDEX idx_status (status, created_at),
    INDEX idx_confidence (confidence_score DESC),
    FOREIGN KEY (source_query_id) REFERENCES query_learning_data(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='AI-generated metadata improvement suggestions';

-- ============================================================================
-- SECTION 9: DEFAULT DATA & SEED VALUES
-- ============================================================================

-- Insert default semantic types
INSERT INTO semantic_types (type_name, description, example_patterns) VALUES
('identifier', 'Unique identifiers and keys', '["id", "uuid", "key", "code"]'),
('location', 'Geographic location data', '["country", "city", "state", "address", "zip", "postal"]'),
('contact', 'Contact information', '["email", "phone", "mobile", "fax", "website"]'),
('temporal', 'Date and time information', '["date", "time", "timestamp", "created_at", "updated_at"]'),
('financial', 'Monetary and financial data', '["amount", "price", "cost", "total", "tax", "salary"]'),
('quantity', 'Quantities and counts', '["quantity", "count", "stock", "inventory"]'),
('status', 'Status and state flags', '["status", "state", "active", "enabled", "is_active"]'),
('personal', 'Personal information (PII)', '["name", "first_name", "last_name", "age", "gender", "ssn"]'),
('description', 'Descriptive text fields', '["description", "details", "notes", "comment", "remarks"]'),
('category', 'Categories and classifications', '["type", "category", "class", "group", "department"]')
ON DUPLICATE KEY UPDATE description=VALUES(description);

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

-- Insert default feedback types
INSERT IGNORE INTO response_patterns (query_type, pattern_template, success_rate, usage_count) VALUES 
    ('feedback_positive', 'User marked response as helpful', 0.0, 0),
    ('feedback_negative', 'User marked response as not helpful', 0.0, 0),
    ('feedback_incorrect', 'User reported incorrect information', 0.0, 0),
    ('feedback_incomplete', 'User reported incomplete answer', 0.0, 0),
    ('feedback_unclear', 'User reported unclear explanation', 0.0, 0);

-- ============================================================================
-- SECTION 10: VERIFICATION & SUMMARY
-- ============================================================================

SELECT 
    '✅ HELPDESK CHATBOT SCHEMA CREATED SUCCESSFULLY' as status,
    COUNT(*) as total_tables
FROM information_schema.tables 
WHERE table_schema = 'helpdesk_db';

SELECT 
    'ℹ️  TABLES CREATED:' as info,
    GROUP_CONCAT(table_name ORDER BY table_name SEPARATOR ', ') as tables
FROM information_schema.tables 
WHERE table_schema = 'helpdesk_db';

-- ============================================================================
-- END OF MASTER SCHEMA
-- ============================================================================
-- Next Steps:
-- 1. Verify tables: SELECT * FROM information_schema.tables WHERE table_schema='helpdesk_db';
-- 2. Create first user: INSERT INTO users (username, email, password_hash, role) VALUES (...);
-- 3. Auto-discover metadata: POST /metadata/metadata/auto-discover
-- 4. Start using the chatbot!
-- ============================================================================


-- Migration: Create Column Metadata Tables
-- Purpose: Store semantic descriptions for database columns to improve SQL generation
-- Date: 2025-01-17

-- Table for storing column-level metadata
CREATE TABLE IF NOT EXISTS column_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    connection_id VARCHAR(100) NULL,  -- Optional: Link to specific database connection
    database_name VARCHAR(100) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    column_name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    semantic_type VARCHAR(50) NULL,  -- e.g., 'location', 'date', 'amount', 'identifier'
    examples TEXT NULL,  -- JSON array of example values
    is_sensitive BOOLEAN DEFAULT FALSE,  -- Flag for PII/sensitive data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NULL,
    updated_by VARCHAR(100) NULL,
    
    -- Ensure unique constraint per tenant/database/table/column
    UNIQUE KEY unique_column_metadata (tenant_id, database_name, table_name, column_name),
    
    -- Indexes for efficient lookup
    INDEX idx_tenant_db (tenant_id, database_name),
    INDEX idx_tenant_table (tenant_id, database_name, table_name),
    INDEX idx_connection (connection_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Stores semantic descriptions and metadata for database columns';

-- Table for storing table-level metadata
CREATE TABLE IF NOT EXISTS table_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    connection_id VARCHAR(100) NULL,
    database_name VARCHAR(100) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    business_purpose TEXT NULL,  -- What this table is used for in business context
    primary_entity VARCHAR(100) NULL,  -- e.g., 'Customer', 'Order', 'Product'
    common_joins TEXT NULL,  -- JSON array of common join patterns
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NULL,
    updated_by VARCHAR(100) NULL,
    
    -- Ensure unique constraint per tenant/database/table
    UNIQUE KEY unique_table_metadata (tenant_id, database_name, table_name),
    
    -- Indexes
    INDEX idx_tenant_db (tenant_id, database_name),
    INDEX idx_connection (connection_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Stores semantic descriptions and metadata for database tables';

-- Table for storing relationship metadata (foreign keys and semantic relationships)
CREATE TABLE IF NOT EXISTS relationship_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    connection_id VARCHAR(100) NULL,
    database_name VARCHAR(100) NOT NULL,
    
    -- Source table/column
    source_table VARCHAR(100) NOT NULL,
    source_column VARCHAR(100) NOT NULL,
    
    -- Target table/column
    target_table VARCHAR(100) NOT NULL,
    target_column VARCHAR(100) NOT NULL,
    
    relationship_type VARCHAR(50) NOT NULL,  -- 'one_to_many', 'many_to_one', 'many_to_many', 'one_to_one'
    description TEXT NULL,
    is_enforced BOOLEAN DEFAULT FALSE,  -- Whether FK constraint exists
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NULL,
    
    -- Indexes
    INDEX idx_tenant_source (tenant_id, database_name, source_table),
    INDEX idx_tenant_target (tenant_id, database_name, target_table),
    INDEX idx_connection (connection_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Stores relationship metadata between tables';

-- Table for storing common query patterns and examples
CREATE TABLE IF NOT EXISTS query_patterns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    connection_id VARCHAR(100) NULL,
    database_name VARCHAR(100) NOT NULL,
    
    pattern_name VARCHAR(200) NOT NULL,
    description TEXT NULL,
    example_question TEXT NOT NULL,  -- Natural language question
    example_sql TEXT NOT NULL,  -- Corresponding SQL
    tables_involved TEXT NULL,  -- JSON array of table names
    
    usage_count INT DEFAULT 0,
    success_count INT DEFAULT 0,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NULL,
    
    -- Indexes
    INDEX idx_tenant_db (tenant_id, database_name),
    INDEX idx_active (tenant_id, is_active),
    INDEX idx_connection (connection_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Stores common query patterns as examples for SQL generation';

-- Insert some default semantic types reference
CREATE TABLE IF NOT EXISTS semantic_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    example_patterns TEXT NULL,  -- JSON array of column name patterns
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Reference table for semantic column types';

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

-- Table for storing query feedback and learning data
CREATE TABLE IF NOT EXISTS query_learning_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(100) NULL,
    
    -- Query details
    natural_language_query TEXT NOT NULL,
    generated_sql TEXT NULL,
    tables_used TEXT NULL,  -- JSON array of table names
    columns_used TEXT NULL,  -- JSON array of column names
    
    -- Execution results
    execution_success BOOLEAN DEFAULT FALSE,
    execution_time_ms INT NULL,
    rows_returned INT NULL,
    error_message TEXT NULL,
    
    -- User feedback
    user_feedback ENUM('positive', 'negative', 'neutral', 'no_feedback') DEFAULT 'no_feedback',
    user_rating INT NULL,  -- 1-5 rating
    user_comment TEXT NULL,
    
    -- Metadata improvements suggested
    needs_metadata_improvement BOOLEAN DEFAULT FALSE,
    suggested_improvements TEXT NULL,  -- JSON with suggestions
    improvement_applied BOOLEAN DEFAULT FALSE,
    
    -- Context
    source_type VARCHAR(50) NULL,  -- 'database', 'documents', 'clarification'
    confidence_score DECIMAL(5,2) NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_tenant_session (tenant_id, session_id),
    INDEX idx_tenant_user (tenant_id, user_id),
    INDEX idx_success (execution_success, created_at),
    INDEX idx_feedback (user_feedback, created_at),
    INDEX idx_improvement (needs_metadata_improvement, improvement_applied)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Stores query execution data for learning and improvement';

-- Table for tracking metadata quality and usage
CREATE TABLE IF NOT EXISTS metadata_quality_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    database_name VARCHAR(100) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    column_name VARCHAR(100) NULL,  -- NULL means table-level metric
    
    -- Quality metrics
    query_success_count INT DEFAULT 0,
    query_failure_count INT DEFAULT 0,
    positive_feedback_count INT DEFAULT 0,
    negative_feedback_count INT DEFAULT 0,
    
    -- Usage metrics
    times_used INT DEFAULT 0,
    last_used_at TIMESTAMP NULL,
    
    -- Quality score (calculated)
    quality_score DECIMAL(5,2) DEFAULT 0.00,
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Unique constraint
    UNIQUE KEY unique_metadata_metric (tenant_id, database_name, table_name, column_name),
    
    -- Indexes
    INDEX idx_quality (quality_score),
    INDEX idx_usage (times_used, last_used_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tracks quality and usage metrics for metadata';

-- Table for storing metadata improvement suggestions
CREATE TABLE IF NOT EXISTS metadata_improvement_suggestions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    database_name VARCHAR(100) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    column_name VARCHAR(100) NULL,  -- NULL for table-level suggestions
    
    -- Current state
    current_description TEXT NULL,
    
    -- Suggestion
    suggested_description TEXT NOT NULL,
    suggestion_reason TEXT NULL,
    confidence_score DECIMAL(5,2) NULL,
    
    -- Source of suggestion
    source_query_id INT NULL,  -- Reference to query_learning_data
    based_on_queries_count INT DEFAULT 1,
    
    -- Status
    status ENUM('pending', 'approved', 'rejected', 'applied') DEFAULT 'pending',
    reviewed_by VARCHAR(100) NULL,
    reviewed_at TIMESTAMP NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_tenant_db (tenant_id, database_name),
    INDEX idx_status (status, created_at),
    INDEX idx_confidence (confidence_score DESC),
    FOREIGN KEY (source_query_id) REFERENCES query_learning_data(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Stores AI-generated suggestions for improving metadata';


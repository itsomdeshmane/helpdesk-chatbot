-- ============================================================================
-- Migration 08: Smart Tables for Intelligent System
-- Description: Create tables to make the system learn and adapt
-- Date: 2025-12-05
-- ============================================================================

-- ============================================================================
-- 1. DOCUMENT INTELLIGENCE
-- ============================================================================

-- Document categories/topics for better organization
CREATE TABLE IF NOT EXISTS document_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_key VARCHAR(50) NOT NULL UNIQUE,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_category_id INT DEFAULT NULL,
    icon VARCHAR(50) DEFAULT NULL,
    color VARCHAR(20) DEFAULT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_category_id) REFERENCES document_categories(id) ON DELETE SET NULL,
    INDEX idx_active (is_active),
    INDEX idx_parent (parent_category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Document categories for organization and filtering';

-- Document metadata - link documents to categories and track metadata
CREATE TABLE IF NOT EXISTS document_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    category_id INT DEFAULT NULL,
    title VARCHAR(255),
    description TEXT,
    author VARCHAR(100),
    version VARCHAR(50),
    language VARCHAR(10) DEFAULT 'en',
    tags TEXT COMMENT 'Comma-separated tags',
    file_size_kb INT,
    chunk_count INT DEFAULT 0,
    last_indexed_at TIMESTAMP NULL,
    tenant_id VARCHAR(255) DEFAULT 'default',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES document_categories(id) ON DELETE SET NULL,
    INDEX idx_filename (filename),
    INDEX idx_category (category_id),
    INDEX idx_tenant (tenant_id),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Metadata for uploaded/indexed documents';

-- Document relationships - related/prerequisite documents
CREATE TABLE IF NOT EXISTS document_relationships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_document_id INT NOT NULL,
    related_document_id INT NOT NULL,
    relationship_type ENUM('related', 'prerequisite', 'supersedes', 'references') DEFAULT 'related',
    strength FLOAT DEFAULT 1.0 COMMENT 'Relationship strength 0-1',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_document_id) REFERENCES document_metadata(id) ON DELETE CASCADE,
    FOREIGN KEY (related_document_id) REFERENCES document_metadata(id) ON DELETE CASCADE,
    UNIQUE KEY unique_relationship (source_document_id, related_document_id, relationship_type),
    INDEX idx_source (source_document_id),
    INDEX idx_related (related_document_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Relationships between documents';

-- ============================================================================
-- 2. QUERY INTELLIGENCE
-- ============================================================================

-- Synonyms and aliases for better query matching
CREATE TABLE IF NOT EXISTS term_synonyms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    primary_term VARCHAR(100) NOT NULL,
    synonym VARCHAR(100) NOT NULL,
    synonym_type ENUM('exact', 'abbreviation', 'colloquial', 'technical') DEFAULT 'exact',
    language VARCHAR(10) DEFAULT 'en',
    confidence FLOAT DEFAULT 1.0,
    usage_count INT DEFAULT 0,
    tenant_id VARCHAR(255) DEFAULT 'default',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_synonym (primary_term, synonym),
    INDEX idx_primary (primary_term),
    INDEX idx_synonym (synonym),
    INDEX idx_tenant (tenant_id),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Synonyms and aliases for query expansion';

-- Query intent patterns for better understanding
CREATE TABLE IF NOT EXISTS query_intents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    intent_name VARCHAR(100) NOT NULL,
    intent_type ENUM('question', 'command', 'search', 'navigation', 'complaint', 'feedback') DEFAULT 'question',
    pattern TEXT COMMENT 'Regex or keyword pattern',
    example_queries TEXT COMMENT 'Example queries for this intent',
    suggested_response_template TEXT,
    priority INT DEFAULT 1,
    match_count INT DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_intent_type (intent_type),
    INDEX idx_active (is_active),
    INDEX idx_priority (priority DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Query intent patterns for better understanding';

-- Related questions - show users what else they can ask
CREATE TABLE IF NOT EXISTS related_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_query VARCHAR(500) NOT NULL,
    related_query VARCHAR(500) NOT NULL,
    relevance_score FLOAT DEFAULT 1.0,
    co_occurrence_count INT DEFAULT 0 COMMENT 'How often asked together',
    tenant_id VARCHAR(255) DEFAULT 'default',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_source (source_query(255)),
    INDEX idx_tenant (tenant_id),
    INDEX idx_relevance (relevance_score DESC),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Related questions to help users explore';

-- ============================================================================
-- 3. RESPONSE INTELLIGENCE
-- ============================================================================

-- Response templates for consistent, high-quality answers
CREATE TABLE IF NOT EXISTS response_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    template_name VARCHAR(100) NOT NULL,
    template_type ENUM('greeting', 'not_found', 'clarification', 'success', 'error', 'instruction') DEFAULT 'instruction',
    template_text TEXT NOT NULL,
    variables TEXT COMMENT 'JSON array of variable names',
    usage_count INT DEFAULT 0,
    rating FLOAT DEFAULT 0.0 COMMENT 'User rating 0-5',
    language VARCHAR(10) DEFAULT 'en',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_template_type (template_type),
    INDEX idx_active (is_active),
    INDEX idx_rating (rating DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Response templates for consistent answers';

-- Answer quality metrics - track which answers work well
CREATE TABLE IF NOT EXISTS answer_quality_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query_hash VARCHAR(64) NOT NULL COMMENT 'MD5 hash of normalized query',
    query_text VARCHAR(500) NOT NULL,
    answer_hash VARCHAR(64) NOT NULL,
    context_chunks_used INT DEFAULT 0,
    search_score FLOAT DEFAULT 0.0,
    user_helpful_votes INT DEFAULT 0,
    user_unhelpful_votes INT DEFAULT 0,
    avg_response_time_ms INT DEFAULT 0,
    times_shown INT DEFAULT 0,
    click_through_rate FLOAT DEFAULT 0.0,
    tenant_id VARCHAR(255) DEFAULT 'default',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_query_answer (query_hash, answer_hash),
    INDEX idx_query_hash (query_hash),
    INDEX idx_tenant (tenant_id),
    INDEX idx_quality_score ((user_helpful_votes - user_unhelpful_votes) DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Track answer quality and effectiveness';

-- ============================================================================
-- 4. LEARNING & ANALYTICS
-- ============================================================================

-- Search analytics - learn from what users search for
CREATE TABLE IF NOT EXISTS search_analytics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    search_query VARCHAR(500) NOT NULL,
    normalized_query VARCHAR(500) NOT NULL COMMENT 'Lowercase, trimmed version',
    search_type ENUM('direct', 'suggested', 'related', 'autocomplete') DEFAULT 'direct',
    results_count INT DEFAULT 0,
    clicked_result BOOLEAN DEFAULT FALSE,
    result_position INT DEFAULT NULL COMMENT 'Position of clicked result',
    session_id VARCHAR(100),
    user_id VARCHAR(100),
    tenant_id VARCHAR(255) DEFAULT 'default',
    search_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_normalized_query (normalized_query(255)),
    INDEX idx_session (session_id),
    INDEX idx_tenant (tenant_id),
    INDEX idx_timestamp (search_timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Search analytics for learning user behavior';

-- Context patterns - learn conversation patterns
CREATE TABLE IF NOT EXISTS conversation_patterns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pattern_name VARCHAR(100) NOT NULL,
    query_sequence TEXT NOT NULL COMMENT 'JSON array of query types in sequence',
    occurrence_count INT DEFAULT 0,
    avg_resolution_time INT DEFAULT 0 COMMENT 'Average time to resolve in seconds',
    success_rate FLOAT DEFAULT 0.0,
    example_queries TEXT,
    tenant_id VARCHAR(255) DEFAULT 'default',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_pattern_name (pattern_name),
    INDEX idx_tenant (tenant_id),
    INDEX idx_occurrence (occurrence_count DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Learn common conversation patterns';

-- Auto-suggestions - pre-computed popular suggestions
CREATE TABLE IF NOT EXISTS auto_suggestions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    suggestion_text VARCHAR(255) NOT NULL,
    suggestion_type ENUM('query', 'topic', 'feature', 'help') DEFAULT 'query',
    category VARCHAR(100),
    popularity_score FLOAT DEFAULT 0.0,
    click_through_rate FLOAT DEFAULT 0.0,
    times_shown INT DEFAULT 0,
    times_clicked INT DEFAULT 0,
    tenant_id VARCHAR(255) DEFAULT 'default',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_suggestion_text (suggestion_text),
    INDEX idx_type_category (suggestion_type, category),
    INDEX idx_popularity (popularity_score DESC),
    INDEX idx_tenant (tenant_id),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Pre-computed auto-suggestions for quick access';

-- ============================================================================
-- 5. USER FEEDBACK & IMPROVEMENT
-- ============================================================================

-- Enhanced feedback - more structured feedback collection
CREATE TABLE IF NOT EXISTS detailed_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    feedback_category ENUM('accuracy', 'completeness', 'clarity', 'speed', 'relevance', 'other') NOT NULL,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    what_was_good TEXT,
    what_was_missing TEXT,
    suggested_improvement TEXT,
    session_id VARCHAR(100),
    user_id VARCHAR(100),
    tenant_id VARCHAR(255) DEFAULT 'default',
    status ENUM('new', 'reviewed', 'implemented', 'rejected') DEFAULT 'new',
    admin_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (feedback_category),
    INDEX idx_rating (rating),
    INDEX idx_status (status),
    INDEX idx_tenant (tenant_id),
    INDEX idx_created (created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Detailed user feedback for continuous improvement';

-- ============================================================================
-- Insert Default Data
-- ============================================================================

-- Default document categories
INSERT INTO document_categories (category_key, category_name, description, icon, color) VALUES
('getting-started', 'Getting Started', 'Introduction and quick start guides', '🚀', '#4CAF50'),
('how-to', 'How-To Guides', 'Step-by-step instructions', '📖', '#2196F3'),
('troubleshooting', 'Troubleshooting', 'Problem solving and error fixes', '🔧', '#FF9800'),
('reference', 'Reference', 'Technical reference documentation', '📚', '#9C27B0'),
('features', 'Features', 'Feature descriptions and capabilities', '⭐', '#00BCD4'),
('configuration', 'Configuration', 'Setup and configuration guides', '⚙️', '#607D8B'),
('api', 'API Documentation', 'API endpoints and integration', '🔌', '#3F51B5');

-- Default response templates
INSERT INTO response_templates (template_name, template_type, template_text, variables) VALUES
('not_found_default', 'not_found', 'I don''t have information about {{query}} in the loaded documentation. Please check if the relevant document has been uploaded or contact support for assistance.', '["query"]'),
('clarification_needed', 'clarification', 'I need a bit more information to help you. Could you please clarify: {{clarification_points}}?', '["clarification_points"]'),
('greeting_default', 'greeting', 'Hello! I''m here to help you with {{system_name}}. What would you like to know?', '["system_name"]'),
('success_found', 'success', 'I found information about {{topic}}. Here''s what I know:', '["topic"]'),
('multiple_results', 'clarification', 'I found multiple topics related to your question:\n{{topics}}\nWhich one would you like to know more about?', '["topics"]');

-- Default auto-suggestions
INSERT INTO auto_suggestions (suggestion_text, suggestion_type, category, popularity_score) VALUES
('How do I get started?', 'query', 'getting-started', 10.0),
('What features are available?', 'query', 'features', 9.0),
('How to configure settings?', 'query', 'configuration', 8.0),
('Common troubleshooting tips', 'topic', 'troubleshooting', 7.0),
('View all documentation', 'help', 'general', 6.0);

-- Default common synonyms
INSERT INTO term_synonyms (primary_term, synonym, synonym_type, confidence) VALUES
('user', 'account', 'exact', 1.0),
('user', 'profile', 'exact', 1.0),
('create', 'add', 'exact', 1.0),
('create', 'new', 'exact', 0.9),
('delete', 'remove', 'exact', 1.0),
('delete', 'erase', 'exact', 0.8),
('update', 'edit', 'exact', 1.0),
('update', 'modify', 'exact', 1.0),
('update', 'change', 'exact', 0.9),
('view', 'see', 'exact', 1.0),
('view', 'display', 'exact', 1.0),
('view', 'show', 'exact', 1.0),
('configure', 'setup', 'exact', 1.0),
('configure', 'set up', 'exact', 1.0),
('error', 'issue', 'exact', 0.9),
('error', 'problem', 'exact', 0.9),
('help', 'support', 'exact', 1.0),
('help', 'assistance', 'exact', 0.8);

-- ============================================================================
-- Verification Queries
-- ============================================================================
-- SELECT COUNT(*) FROM document_categories;
-- SELECT COUNT(*) FROM document_metadata;
-- SELECT COUNT(*) FROM term_synonyms;
-- SELECT COUNT(*) FROM response_templates;
-- SELECT COUNT(*) FROM auto_suggestions;
-- SHOW TABLES LIKE '%document%' OR LIKE '%query%' OR LIKE '%answer%';


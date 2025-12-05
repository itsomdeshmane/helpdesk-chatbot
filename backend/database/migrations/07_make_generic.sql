-- ============================================================================
-- Migration 07: Make System Generic (Remove ERP-Specific References)
-- Description: Rename erp_entities to system_entities and make it generic
-- Date: 2025-12-05
-- ============================================================================

-- Rename erp_entities table to system_entities for generic use
RENAME TABLE erp_entities TO system_entities;

-- Update table comment to be generic
ALTER TABLE system_entities 
COMMENT = 'Generic system entities for domain-specific recognition (items, customers, features, etc.)';

-- Update column comments to be generic
ALTER TABLE system_entities 
MODIFY COLUMN entity_type VARCHAR(50) DEFAULT 'general' COMMENT 'Type: transactional, reference, configuration, feature';

-- ============================================================================
-- Update default data to be generic examples
-- ============================================================================

-- Clear existing ERP-specific data
TRUNCATE TABLE system_entities;

-- Insert generic sample entities (can be customized per deployment)
INSERT INTO system_entities (entity_key, entity_name, entity_type, description, priority) VALUES
('user', 'User', 'reference', 'System user or account', 3),
('customer', 'Customer', 'reference', 'Customer or client', 3),
('order', 'Order', 'transactional', 'Order or request', 2),
('item', 'Item', 'reference', 'Item, product, or resource', 2),
('document', 'Document', 'reference', 'Document or file', 2),
('report', 'Report', 'feature', 'System report or analytics', 2),
('setting', 'Setting', 'configuration', 'System configuration or setting', 1),
('notification', 'Notification', 'feature', 'System notification or alert', 1);

-- ============================================================================
-- Verification Queries
-- ============================================================================
-- SHOW TABLES LIKE '%entities%';
-- SELECT * FROM system_entities;


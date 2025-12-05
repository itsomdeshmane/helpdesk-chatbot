-- ============================================================================
-- Migration 06: Remove Module-Related Tables and Columns
-- Description: Remove erp_modules table and module_name column from related tables
-- Date: 2025-12-05
-- ============================================================================

-- Drop erp_modules table completely
DROP TABLE IF EXISTS erp_modules;

-- Remove module_name column from generated_questions table
-- First, drop the index that references module_name
ALTER TABLE generated_questions 
DROP INDEX IF EXISTS idx_module_level;

-- Now drop the module_name column
ALTER TABLE generated_questions 
DROP COLUMN IF EXISTS module_name;

-- Create new index without module_name
ALTER TABLE generated_questions 
ADD INDEX idx_difficulty_level (difficulty_level);

-- Clean up system_entities table - remove related_modules column (if exists from old erp_entities)
ALTER TABLE IF EXISTS erp_entities 
DROP COLUMN IF EXISTS related_modules;

-- Also handle if table was already renamed
ALTER TABLE IF EXISTS system_entities 
DROP COLUMN IF EXISTS related_modules;

-- ============================================================================
-- Verification Queries (Run these manually to verify the migration)
-- ============================================================================
-- SHOW TABLES LIKE '%module%';
-- DESCRIBE generated_questions;
-- DESCRIBE erp_entities;


-- Migration: Add db_type column to support multiple database types
-- Date: 2025-12-16
-- Description: Adds db_type column to user_database_connections table for MySQL, PostgreSQL, and SQL Server support

-- Check if column already exists before adding
SET @col_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'user_database_connections'
    AND COLUMN_NAME = 'db_type'
);

-- Add db_type column if it doesn't exist
SET @sql = IF(
    @col_exists = 0,
    'ALTER TABLE user_database_connections ADD COLUMN db_type VARCHAR(20) DEFAULT ''mysql'' NOT NULL AFTER tenant_id',
    'SELECT "db_type column already exists" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Show result
SELECT 
    CASE 
        WHEN @col_exists = 0 THEN 'db_type column added successfully'
        ELSE 'db_type column already exists'
    END AS result;

-- Verify the change
DESCRIBE user_database_connections;


-- Add db_type column to user_database_connections table
-- Run this SQL in your MySQL database

-- Add the db_type column
ALTER TABLE user_database_connections 
ADD COLUMN db_type VARCHAR(20) DEFAULT 'mysql' NOT NULL 
AFTER tenant_id;

-- Verify it was added
DESCRIBE user_database_connections;

-- Show success message
SELECT 'db_type column added successfully!' as status;


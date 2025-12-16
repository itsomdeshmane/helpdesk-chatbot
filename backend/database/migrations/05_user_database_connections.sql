-- User Database Connections Table
-- Stores user-specific database connection information securely

CREATE TABLE IF NOT EXISTS user_database_connections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    tenant_id VARCHAR(100) NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INT NOT NULL DEFAULT 3306,
    database_name VARCHAR(100) NOT NULL,
    username VARCHAR(100) NOT NULL,
    encrypted_password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_user_tenant (user_id, tenant_id),
    INDEX idx_tenant (tenant_id),
    
    -- Foreign key constraint
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Ensure one connection per user per tenant
    UNIQUE KEY unique_user_tenant_connection (user_id, tenant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Stores encrypted database connection credentials for users';

-- Add index for efficient queries
CREATE INDEX idx_created_at ON user_database_connections(created_at);


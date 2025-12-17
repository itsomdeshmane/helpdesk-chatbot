"""
Create user_database_connections table
"""
import pymysql
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

def create_table():
    """Create the user_database_connections table"""
    try:
        # Connect to database
        connection = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        print("Creating user_database_connections table...")
        
        # Create table
        cursor.execute("""
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
                
                INDEX idx_user_tenant (user_id, tenant_id),
                INDEX idx_tenant (tenant_id),
                INDEX idx_created_at (created_at),
                
                UNIQUE KEY unique_user_tenant_connection (user_id, tenant_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            COMMENT='Stores encrypted database connection credentials for users'
        """)
        
        connection.commit()
        print("✅ Table 'user_database_connections' created successfully!")
        
        # Verify table exists
        cursor.execute("SHOW TABLES LIKE 'user_database_connections'")
        result = cursor.fetchone()
        if result:
            print("✅ Table verified in database")
            
            # Show table structure
            cursor.execute("DESCRIBE user_database_connections")
            columns = cursor.fetchall()
            print("\nTable structure:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_table()




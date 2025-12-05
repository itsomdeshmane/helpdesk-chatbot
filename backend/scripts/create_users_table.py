"""
Create users table with authentication and authorization support
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_manager

def create_users_table():
    """Create users table with roles and permissions"""
    
    print("\n" + "="*80)
    print("🔐 CREATING USERS TABLE FOR AUTHENTICATION")
    print("="*80)
    
    # SQL to create users table
    create_table_sql = """
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
    """
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn._conn.cursor()
            
            # Create users table
            print("\n📊 Creating 'users' table...")
            cursor.execute(create_table_sql)
            conn._conn.commit()
            print("   ✅ 'users' table created successfully")
            
            # Check if admin user exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
            admin_exists = cursor.fetchone()[0] > 0
            
            if not admin_exists:
                # Create default admin user
                print("\n👤 Creating default admin user...")
                from passlib.hash import bcrypt
                
                admin_password = bcrypt.hash("admin123")  # Change this in production!
                
                insert_admin_sql = """
                INSERT INTO users (username, email, password_hash, full_name, role, tenant_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_admin_sql, (
                    'admin',
                    'admin@example.com',
                    admin_password,
                    'System Administrator',
                    'admin',
                    'default'
                ))
                conn._conn.commit()
                print("   ✅ Admin user created")
                print("   📧 Email: admin@example.com")
                print("   🔑 Password: admin123")
                print("   ⚠️  IMPORTANT: Change this password in production!")
            else:
                print("\n   ℹ️  Admin user already exists")
            
            cursor.close()
        
        print("\n" + "="*80)
        print("✅ USERS TABLE SETUP COMPLETE!")
        print("="*80)
        print("\n📋 User Roles:")
        print("   • admin  - Full access to all features")
        print("   • user   - Can chat and view own history")
        print("   • viewer - Read-only access")
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error creating users table: {e}")
        raise

if __name__ == "__main__":
    create_users_table()


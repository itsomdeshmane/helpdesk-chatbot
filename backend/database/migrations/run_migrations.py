"""
Master Database Migration Runner
Runs all SQL migration scripts in order
"""
import sys
import os
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import mysql.connector
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

def get_connection():
    """Get MySQL connection"""
    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        charset='utf8mb4',
        collation='utf8mb4_unicode_ci'
    )

def create_database_if_not_exists(conn):
    """Ensure database exists"""
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cursor.execute(f"USE {MYSQL_DATABASE}")
    cursor.close()
    print(f"✅ Using database: {MYSQL_DATABASE}")

def create_migrations_table(conn):
    """Create table to track applied migrations"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            migration_name VARCHAR(255) NOT NULL UNIQUE,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_migration_name (migration_name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    conn.commit()
    cursor.close()
    print("✅ Migrations tracking table ready")

def get_applied_migrations(conn):
    """Get list of already applied migrations"""
    cursor = conn.cursor()
    cursor.execute("SELECT migration_name FROM schema_migrations")
    applied = {row[0] for row in cursor.fetchall()}
    cursor.close()
    return applied

def mark_migration_applied(conn, migration_name):
    """Mark a migration as applied"""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO schema_migrations (migration_name) VALUES (%s) ON DUPLICATE KEY UPDATE applied_at = CURRENT_TIMESTAMP",
        (migration_name,)
    )
    conn.commit()
    cursor.close()

def run_sql_file(conn, filepath, migration_name):
    """Run a SQL file"""
    print(f"\n{'='*80}")
    print(f"📄 Running: {migration_name}")
    print(f"{'='*80}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Split by semicolon and execute each statement
    statements = [s.strip() for s in sql_content.split(';') if s.strip()]
    
    cursor = conn.cursor()
    success_count = 0
    
    for statement in statements:
        # Skip comments and empty statements
        if statement.startswith('--') or not statement:
            continue
        
        try:
            cursor.execute(statement)
            success_count += 1
        except mysql.connector.Error as e:
            # Ignore "already exists" errors
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print(f"   ℹ️  Skipping: Already exists")
            else:
                print(f"   ⚠️  Warning: {e}")
    
    conn.commit()
    cursor.close()
    print(f"✅ Executed {success_count} statements successfully")
    
    # Mark as applied
    mark_migration_applied(conn, migration_name)

def run_all_migrations(force=False):
    """
    Run all migration scripts in order
    
    Args:
        force: If True, runs all migrations even if already applied
    """
    migrations_dir = Path(__file__).parent
    
    # Define migration order
    migrations = [
        '00_complete_schema.sql',
        '01_users_authentication.sql',
        '02_conversations_sessions.sql',
        '03_context_tracking.sql',
        '04_question_generation.sql'
    ]
    
    print("\n" + "="*80)
    print("🚀 DATABASE MIGRATION RUNNER")
    print("="*80)
    print(f"Database: {MYSQL_DATABASE}")
    print(f"Host: {MYSQL_HOST}:{MYSQL_PORT}")
    print(f"Total migrations: {len(migrations)}")
    print("="*80)
    
    try:
        # Connect to MySQL
        print("\n📡 Connecting to MySQL...")
        conn = get_connection()
        print("✅ Connected successfully")
        
        # Create database if needed
        create_database_if_not_exists(conn)
        
        # Create migrations tracking table
        create_migrations_table(conn)
        
        # Get already applied migrations
        applied_migrations = get_applied_migrations(conn)
        print(f"\n📊 Previously applied: {len(applied_migrations)} migrations")
        
        # Run migrations
        skipped = 0
        applied = 0
        
        for migration_file in migrations:
            migration_path = migrations_dir / migration_file
            
            if not migration_path.exists():
                print(f"\n⚠️  Warning: {migration_file} not found, skipping...")
                continue
            
            if migration_file in applied_migrations and not force:
                print(f"\n⏭️  Skipping: {migration_file} (already applied)")
                skipped += 1
                continue
            
            try:
                run_sql_file(conn, migration_path, migration_file)
                applied += 1
            except Exception as e:
                print(f"\n❌ Error running {migration_file}: {e}")
                if not force:
                    raise
        
        conn.close()
        
        # Summary
        print("\n" + "="*80)
        print("✅ MIGRATION COMPLETE!")
        print("="*80)
        print(f"📊 Summary:")
        print(f"   • Total migrations: {len(migrations)}")
        print(f"   • Applied: {applied}")
        print(f"   • Skipped: {skipped}")
        print(f"   • Total in database: {len(applied_migrations) + applied}")
        print("\n💡 Next steps:")
        print("   1. Verify tables were created: python test_mysql_connection.py")
        print("   2. Restart your backend server")
        print("   3. Test the application")
        print("="*80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_status():
    """Show migration status"""
    print("\n" + "="*80)
    print("📊 MIGRATION STATUS")
    print("="*80)
    
    try:
        conn = get_connection()
        create_database_if_not_exists(conn)
        create_migrations_table(conn)
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT migration_name, applied_at 
            FROM schema_migrations 
            ORDER BY applied_at
        """)
        
        migrations = cursor.fetchall()
        
        if migrations:
            print(f"\n✅ Applied migrations ({len(migrations)}):")
            for migration_name, applied_at in migrations:
                print(f"   • {migration_name}")
                print(f"     Applied: {applied_at}")
        else:
            print("\n❌ No migrations applied yet")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Migration Runner')
    parser.add_argument('--force', action='store_true', help='Force run all migrations even if already applied')
    parser.add_argument('--status', action='store_true', help='Show migration status')
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
    else:
        success = run_all_migrations(force=args.force)
        sys.exit(0 if success else 1)












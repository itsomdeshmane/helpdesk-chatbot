"""
Test MySQL connection and database setup
Run this script to verify MySQL configuration
"""
from database.db_manager import db_manager

def test_connection():
    """Test MySQL connection and basic operations"""
    print("🔍 Testing MySQL Connection...")
    print("=" * 60)
    
    try:
        # Test connection
        with db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT VERSION()")
            result = cursor.fetchone()
            if result:
                print(f"✅ Connected to MySQL: {result['VERSION()']}")
            
            # Test tables exist
            cursor = conn.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"\n📊 Found {len(tables)} tables:")
            for table in tables:
                table_name = list(table.values())[0]
                cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                count = cursor.fetchone()['count']
                print(f"   - {table_name}: {count} records")
        
        # Test save interaction
        print("\n🧪 Testing save interaction...")
        db_manager.save_interaction(
            tenant_id="test",
            query="Test query from test script",
            response="Test response",
            module="Testing",
            response_time=0.5
        )
        print("✅ Successfully saved test interaction")
        
        # Test get recent interactions
        print("\n📖 Testing get recent interactions...")
        interactions = db_manager.get_recent_interactions("test", limit=5)
        print(f"✅ Retrieved {len(interactions)} interactions")
        
        print("\n" + "=" * 60)
        print("🎉 All tests passed! MySQL is working correctly.")
        print("\n💡 Your application is now using MySQL database.")
        print(f"   Database: helpdesk_db")
        print(f"   Host: localhost:3306")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure MySQL server is running")
        print("   2. Check credentials in .env file")
        print("   3. Ensure user has permissions to create databases")
        print("\n   Run this command in MySQL to grant permissions:")
        print("   GRANT ALL PRIVILEGES ON helpdesk_db.* TO 'root'@'localhost';")

if __name__ == "__main__":
    test_connection()


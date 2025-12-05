"""
Quick Clear Database - Simple version
Clears all chat history and keeps structure/entities
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def quick_clear():
    """Clear only chat history data, keep entities and structure"""
    print("\n" + "="*70)
    print("QUICK DATABASE CLEAR - Chat History Only")
    print("="*70 + "\n")
    
    try:
        from database.db_manager import db_manager
        
        # Tables to clear (keep entities and structure)
        tables_to_clear = [
            'chat_interactions',
            'query_clarifications',
            'generated_questions'
        ]
        
        with db_manager.get_connection() as conn:
            print("Clearing chat history tables...\n")
            
            for table in tables_to_clear:
                try:
                    # Get count before clearing
                    cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table}")
                    result = cursor.fetchone()
                    count = result['count'] if result else 0
                    
                    # Clear the table
                    conn.execute(f"DELETE FROM {table}")
                    conn.commit()
                    
                    print(f"  ✅ Cleared {table:<30} ({count} records)")
                    
                except Exception as e:
                    print(f"  ⚠️  Error with {table}: {e}")
            
            print("\n" + "="*70)
            print("✅ Chat history cleared successfully!")
            print("="*70)
            print("\nPreserved:")
            print("  • ERP entities (items, customers, etc.)")
            print("  • ERP modules configuration")
            print("  • Database structure")
            print("="*70 + "\n")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. MySQL server is running")
        print("  2. Database credentials are correct in .env")
        print("  3. Database has been initialized")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Quick clear chat history')
    parser.add_argument('--yes', '-y', action='store_true',
                       help='Skip confirmation')
    args = parser.parse_args()
    
    if not args.yes:
        print("\n⚠️  This will clear all chat history and generated questions.")
        print("   ERP entities and modules will be preserved.")
        response = input("\nContinue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("❌ Cancelled")
            sys.exit(0)
    
    quick_clear()


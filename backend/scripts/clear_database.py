"""
Clear Database Script
Safely clears all data from the helpdesk database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_manager
import argparse

def get_all_tables(conn):
    """Get list of all tables in the database"""
    try:
        cursor = conn.execute("SHOW TABLES")
        tables = cursor.fetchall()
        return [list(table.values())[0] for table in tables]
    except Exception as e:
        print(f"❌ Error getting tables: {e}")
        return []


def get_table_count(conn, table_name):
    """Get row count for a table"""
    try:
        cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        result = cursor.fetchone()
        return result['count'] if result else 0
    except Exception as e:
        print(f"⚠️  Error counting {table_name}: {e}")
        return 0


def clear_table(conn, table_name):
    """Clear all data from a table"""
    try:
        conn.execute(f"DELETE FROM {table_name}")
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error clearing {table_name}: {e}")
        return False


def truncate_table(conn, table_name):
    """Truncate a table (faster than DELETE)"""
    try:
        conn.execute(f"TRUNCATE TABLE {table_name}")
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error truncating {table_name}: {e}")
        return False


def drop_table(conn, table_name):
    """Drop a table completely"""
    try:
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error dropping {table_name}: {e}")
        return False


def show_database_status():
    """Show current database status"""
    print("\n" + "="*70)
    print("DATABASE STATUS")
    print("="*70)
    
    try:
        with db_manager.get_connection() as conn:
            tables = get_all_tables(conn)
            
            if not tables:
                print("No tables found in database")
                return
            
            total_records = 0
            print(f"\nFound {len(tables)} tables:\n")
            
            for table in tables:
                count = get_table_count(conn, table)
                total_records += count
                print(f"  📊 {table:<30} {count:>8} records")
            
            print(f"\n{'Total:':<33} {total_records:>8} records")
            print("="*70)
            
    except Exception as e:
        print(f"❌ Error: {e}")


def clear_all_data(method='delete', skip_entities=False):
    """
    Clear all data from all tables
    
    Args:
        method: 'delete' or 'truncate' or 'drop'
        skip_entities: If True, skip clearing erp_entities table
    """
    print("\n" + "="*70)
    print(f"CLEARING DATABASE (method: {method.upper()})")
    print("="*70)
    
    try:
        with db_manager.get_connection() as conn:
            tables = get_all_tables(conn)
            
            if not tables:
                print("No tables found")
                return
            
            # Skip entities table if requested
            if skip_entities and 'erp_entities' in tables:
                tables.remove('erp_entities')
                print("\nℹ️  Skipping 'erp_entities' table (keep default entities)")
            
            success_count = 0
            failed_count = 0
            
            print(f"\nClearing {len(tables)} tables...\n")
            
            for table in tables:
                count = get_table_count(conn, table)
                
                if method == 'truncate':
                    success = truncate_table(conn, table)
                elif method == 'drop':
                    success = drop_table(conn, table)
                else:  # delete
                    success = clear_table(conn, table)
                
                if success:
                    success_count += 1
                    action = 'Dropped' if method == 'drop' else 'Cleared'
                    print(f"  ✅ {action} {table:<25} ({count} records)")
                else:
                    failed_count += 1
                    print(f"  ❌ Failed  {table:<25}")
            
            print(f"\n{'='*70}")
            print(f"Results: {success_count} succeeded, {failed_count} failed")
            print(f"{'='*70}")
            
            # Reinitialize tables if dropped
            if method == 'drop':
                print("\n🔄 Reinitializing database tables...")
                db_manager.init_database()
                print("✅ Database reinitialized with fresh schema")
                
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Clear helpdesk database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clear_database.py --status              # Show database status
  python clear_database.py --clear               # Clear all data
  python clear_database.py --clear --truncate    # Clear with TRUNCATE (faster)
  python clear_database.py --drop                # Drop and recreate all tables
  python clear_database.py --clear --keep-entities  # Keep entity data
        """
    )
    
    parser.add_argument('--status', action='store_true',
                       help='Show database status without clearing')
    parser.add_argument('--clear', action='store_true',
                       help='Clear all data from tables')
    parser.add_argument('--truncate', action='store_true',
                       help='Use TRUNCATE instead of DELETE (faster)')
    parser.add_argument('--drop', action='store_true',
                       help='Drop all tables and recreate')
    parser.add_argument('--keep-entities', action='store_true',
                       help='Keep erp_entities table data')
    parser.add_argument('--yes', '-y', action='store_true',
                       help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    # Show status if requested or no action specified
    if args.status or not (args.clear or args.drop):
        show_database_status()
        if not (args.clear or args.drop):
            print("\nℹ️  Use --clear or --drop to modify database")
            print("   Use --help for more options")
        return
    
    # Show current status before clearing
    show_database_status()
    
    # Confirmation prompt
    if not args.yes:
        print("\n⚠️  WARNING: This will delete data from the database!")
        
        if args.drop:
            print("   This will DROP all tables and recreate them.")
        elif args.truncate:
            print("   This will TRUNCATE all tables (fast delete).")
        else:
            print("   This will DELETE all records from all tables.")
        
        if args.keep_entities:
            print("   The 'erp_entities' table will be preserved.")
        
        response = input("\nAre you sure you want to continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("❌ Cancelled")
            return
    
    # Determine method
    if args.drop:
        method = 'drop'
    elif args.truncate:
        method = 'truncate'
    else:
        method = 'delete'
    
    # Clear database
    clear_all_data(method=method, skip_entities=args.keep_entities)
    
    # Show final status
    if method != 'drop':
        print("\n" + "="*70)
        print("FINAL STATUS")
        print("="*70)
        show_database_status()
    
    print("\n✅ Database cleanup completed!")


if __name__ == "__main__":
    main()


"""
Installation script for SQL improvements
Automatically sets up the enhanced system
"""
import os
import shutil
from pathlib import Path


def main():
    """Install SQL improvements"""
    print("=" * 60)
    print("SQL Improvements Installation Script")
    print("=" * 60)
    print()
    
    # Step 1: Create data directory
    print("Step 1: Creating data directory...")
    data_dir = Path("backend/data")
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created: {data_dir}")
    print()
    
    # Step 2: Backup original service
    print("Step 2: Backing up original database_query_service.py...")
    original_service = Path("backend/llm/database_query_service.py")
    backup_service = Path("backend/llm/database_query_service_backup.py")
    
    if original_service.exists():
        if not backup_service.exists():
            shutil.copy2(original_service, backup_service)
            print(f"✅ Backup created: {backup_service}")
        else:
            print(f"⚠️  Backup already exists: {backup_service}")
    else:
        print(f"⚠️  Original service not found: {original_service}")
    print()
    
    # Step 3: Check if all new modules exist
    print("Step 3: Verifying new modules...")
    required_modules = [
        "backend/llm/sql_cache.py",
        "backend/llm/schema_cache.py",
        "backend/llm/model_selector.py",
        "backend/llm/connection_pool.py",
        "backend/llm/result_cache.py",
        "backend/llm/fuzzy_matcher.py",
        "backend/llm/query_learner.py",
        "backend/llm/sql_monitoring.py",
        "backend/llm/error_handler.py",
        "backend/llm/database_query_service_enhanced.py",
        "backend/routers/sql_admin.py"
    ]
    
    all_exist = True
    for module in required_modules:
        if Path(module).exists():
            print(f"✅ {module}")
        else:
            print(f"❌ {module} - NOT FOUND")
            all_exist = False
    print()
    
    if not all_exist:
        print("⚠️  Some modules are missing. Please ensure all files are present.")
        return
    
    # Step 4: Choose integration method
    print("Step 4: Choose integration method:")
    print("  1. Direct replacement (recommended)")
    print("  2. Side-by-side testing")
    print("  3. Skip (I'll do it manually)")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        # Direct replacement
        print("\nReplacing database_query_service.py with enhanced version...")
        enhanced_service = Path("backend/llm/database_query_service_enhanced.py")
        
        if enhanced_service.exists():
            shutil.copy2(enhanced_service, original_service)
            print(f"✅ Replaced: {original_service}")
            print(f"   Original backed up to: {backup_service}")
        else:
            print(f"❌ Enhanced service not found: {enhanced_service}")
    
    elif choice == "2":
        print("\n✅ Enhanced service kept as separate file")
        print("   You can import it as: from llm.database_query_service_enhanced import get_enhanced_database_query_service")
    
    else:
        print("\n⏭️  Skipped integration")
    
    print()
    
    # Step 5: Update app.py instructions
    print("Step 5: Update app.py")
    print("-" * 60)
    print("Add the following lines to backend/app.py:")
    print()
    print("  # Import")
    print("  from routers import sql_admin")
    print()
    print("  # Add router")
    print("  app.include_router(sql_admin.router)")
    print()
    print("Would you like me to update app.py automatically? (y/n): ", end="")
    
    update_app = input().strip().lower()
    
    if update_app == 'y':
        app_file = Path("backend/app.py")
        if app_file.exists():
            content = app_file.read_text()
            
            # Check if already added
            if "sql_admin" in content:
                print("⚠️  sql_admin already imported in app.py")
            else:
                # Add import
                if "from routers import" in content:
                    content = content.replace(
                        "from routers import",
                        "from routers import sql_admin,",
                        1
                    )
                    
                    # Add router
                    if "app.include_router" in content:
                        # Find last router include
                        lines = content.split('\n')
                        insert_line = None
                        for i, line in enumerate(lines):
                            if "app.include_router" in line:
                                insert_line = i + 1
                        
                        if insert_line:
                            lines.insert(insert_line, "app.include_router(sql_admin.router)")
                            content = '\n'.join(lines)
                    
                    app_file.write_text(content)
                    print("✅ Updated app.py")
                else:
                    print("⚠️  Could not auto-update. Please update manually.")
        else:
            print(f"❌ app.py not found: {app_file}")
    else:
        print("⏭️  Skipped app.py update. Please update manually.")
    
    print()
    
    # Step 6: Summary
    print("=" * 60)
    print("Installation Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Review MIGRATION_GUIDE.md for detailed instructions")
    print("  2. Review SQL_IMPROVEMENTS_DOCUMENTATION.md for features")
    print("  3. Start your server: python backend/app.py")
    print("  4. Test admin endpoint: http://localhost:8000/api/sql-admin/stats")
    print("  5. Run test_improvements.py to validate")
    print()
    print("For rollback:")
    print(f"  cp {backup_service} {original_service}")
    print()
    print("Happy optimizing! 🚀")
    print()


if __name__ == "__main__":
    main()


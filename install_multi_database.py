"""
Multi-Database Support Installation Script
Automatically sets up multi-database capabilities
"""
import subprocess
import sys
from pathlib import Path


def main():
    """Install multi-database support"""
    print("=" * 60)
    print("Multi-Database Support Installation")
    print("=" * 60)
    print()
    
    # Step 1: Check if files exist
    print("Step 1: Verifying files...")
    required_files = [
        "backend/llm/db_adapters.py",
        "backend/llm/multi_db_connection_pool.py",
        "backend/routers/database_settings.py",
        "frontend/src/components/DatabaseSettings.js",
        "frontend/src/components/DatabaseSettings.css",
        "backend/requirements-databases.txt"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            all_exist = False
    print()
    
    if not all_exist:
        print("⚠️  Some files are missing. Please ensure all files are present.")
        return
    
    # Step 2: Install dependencies
    print("Step 2: Install database drivers")
    print("-" * 60)
    print("Choose database drivers to install:")
    print("  1. All (MySQL + PostgreSQL + SQL Server)")
    print("  2. MySQL only")
    print("  3. PostgreSQL only")
    print("  4. SQL Server only")
    print("  5. MySQL + PostgreSQL")
    print("  6. Skip (I'll install manually)")
    print()
    
    choice = input("Enter choice (1-6): ").strip()
    
    if choice != "6":
        packages = []
        
        if choice in ["1", "2", "5"]:
            packages.extend(["pymysql==1.1.0", "cryptography==41.0.7"])
        
        if choice in ["1", "3", "5"]:
            packages.append("psycopg2-binary==2.9.9")
        
        if choice in ["1", "4"]:
            packages.append("pyodbc==5.0.1")
        
        if packages:
            print(f"\nInstalling: {', '.join(packages)}")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install"
                ] + packages)
                print("✅ Database drivers installed successfully!")
            except subprocess.CalledProcessError as e:
                print(f"❌ Installation failed: {e}")
                print("You can install manually: pip install -r backend/requirements-databases.txt")
    else:
        print("⏭️  Skipped driver installation")
    
    print()
    
    # Step 3: Update app.py
    print("Step 3: Update backend/app.py")
    print("-" * 60)
    print("Add the following lines to backend/app.py:")
    print()
    print("  # Import")
    print("  from routers import database_settings")
    print()
    print("  # Add router")
    print("  app.include_router(database_settings.router)")
    print()
    
    update_app = input("Would you like me to update app.py automatically? (y/n): ").strip().lower()
    
    if update_app == 'y':
        app_file = Path("backend/app.py")
        if app_file.exists():
            content = app_file.read_text()
            
            # Check if already added
            if "database_settings" in content:
                print("⚠️  database_settings already imported in app.py")
            else:
                # Add import
                if "from routers import" in content:
                    content = content.replace(
                        "from routers import",
                        "from routers import database_settings,",
                        1
                    )
                    
                    # Add router
                    lines = content.split('\n')
                    insert_line = None
                    for i, line in enumerate(lines):
                        if "app.include_router" in line:
                            insert_line = i + 1
                    
                    if insert_line:
                        lines.insert(insert_line, "app.include_router(database_settings.router)")
                        content = '\n'.join(lines)
                    
                    app_file.write_text(content)
                    print("✅ Updated app.py")
                else:
                    print("⚠️  Could not auto-update. Please update manually.")
        else:
            print(f"❌ app.py not found: {app_file}")
    else:
        print("⏭️  Skipped app.py update")
    
    print()
    
    # Step 4: Frontend routing
    print("Step 4: Update frontend routing")
    print("-" * 60)
    print("Add DatabaseSettings to your frontend routing (e.g., App.js):")
    print()
    print("  import DatabaseSettings from './components/DatabaseSettings';")
    print()
    print("  // In your routes:")
    print("  <Route path='/settings/database' element={<DatabaseSettings />} />")
    print()
    input("Press Enter when done...")
    print()
    
    # Step 5: Create data directory
    print("Step 5: Creating data directory...")
    data_dir = Path("backend/data")
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created: {data_dir}")
    print()
    
    # Step 6: ODBC driver reminder
    if choice in ["1", "4"]:
        print("⚠️  SQL Server Support - ODBC Driver Required")
        print("-" * 60)
        print("To use SQL Server, you must install Microsoft ODBC Driver 17:")
        print()
        print("Windows:")
        print("  Download from: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")
        print()
        print("Linux:")
        print("  sudo apt-get install unixodbc-dev")
        print("  # Then follow Microsoft's installation guide")
        print()
        print("Mac:")
        print("  brew install unixodbc")
        print("  brew tap microsoft/mssql-release")
        print("  brew install msodbcsql17")
        print()
        input("Press Enter to continue...")
        print()
    
    # Summary
    print("=" * 60)
    print("Installation Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Review MULTI_DATABASE_GUIDE.md for detailed documentation")
    print("  2. Restart your backend: python backend/app.py")
    print("  3. Restart your frontend: npm start (in frontend directory)")
    print("  4. Navigate to: http://localhost:3000/settings/database")
    print("  5. Add your first database connection!")
    print()
    print("Supported databases:")
    print("  🐬 MySQL (Port: 3306)")
    print("  🐘 PostgreSQL (Port: 5432)")
    print("  🗄️  SQL Server (Port: 1433)")
    print()
    print("Happy connecting! 🚀")
    print()


if __name__ == "__main__":
    main()


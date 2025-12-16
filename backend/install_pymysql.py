"""
Script to install and verify pymysql
"""
import subprocess
import sys

print("=" * 60)
print("Installing PyMySQL...")
print("=" * 60)

# Install pymysql
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymysql", "--quiet"])
    print("✅ Installation command executed")
except Exception as e:
    print(f"❌ Installation failed: {e}")
    sys.exit(1)

# Verify installation
print("\n" + "=" * 60)
print("Verifying installation...")
print("=" * 60)

try:
    import pymysql
    print(f"✅ PyMySQL successfully imported!")
    print(f"   Version: {pymysql.__version__}")
    print(f"   Location: {pymysql.__file__}")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("SUCCESS! PyMySQL is installed and working.")
print("=" * 60)
print("\nYou can now start the backend server:")
print("  python -m uvicorn app:app --reload --port 8000")


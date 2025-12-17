"""
Generate encryption key for the application
Run this script and copy the output to your .env file
"""
from cryptography.fernet import Fernet

# Generate a new encryption key
key = Fernet.generate_key().decode()

print("=" * 60)
print("ENCRYPTION KEY GENERATED")
print("=" * 60)
print()
print("Copy this line to your .env file:")
print()
print(f"ENCRYPTION_KEY={key}")
print()
print("=" * 60)
print()
print("IMPORTANT:")
print("1. Add this to backend/.env file")
print("2. Keep this key secret and secure")
print("3. If you change the key, existing encrypted data cannot be decrypted")
print("4. For production, store this key securely (e.g., secrets manager)")
print()
print("=" * 60)




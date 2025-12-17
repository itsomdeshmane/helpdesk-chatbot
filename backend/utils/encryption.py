"""
Encryption utilities for sensitive data
Uses Fernet (symmetric encryption) from cryptography library
"""
import os
import base64
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

# Get encryption key from environment or generate one
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    logger.warning("ENCRYPTION_KEY not found in environment. Using generated key (NOT for production!)")
    # Generate a key (for development only)
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    logger.info(f"Generated encryption key: {ENCRYPTION_KEY}")
    logger.info("Add this to your .env file as ENCRYPTION_KEY for production")


def get_cipher():
    """Get Fernet cipher instance"""
    try:
        # If key is base64 encoded Fernet key
        if len(ENCRYPTION_KEY) == 44:  # Standard Fernet key length
            key = ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY
        else:
            # Derive key from password using PBKDF2
            salt = b'helpdesk_salt_v1'  # In production, use a random salt per installation
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(ENCRYPTION_KEY.encode()))
        
        return Fernet(key)
    except Exception as e:
        logger.error(f"Error creating cipher: {e}")
        # Fallback: generate a new key
        key = Fernet.generate_key()
        return Fernet(key)


def encrypt_value(plaintext: str) -> str:
    """
    Encrypt a string value
    
    Args:
        plaintext: String to encrypt
        
    Returns:
        Base64 encoded encrypted string
    """
    try:
        cipher = get_cipher()
        encrypted = cipher.encrypt(plaintext.encode())
        return encrypted.decode()
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        raise


def decrypt_value(encrypted_text: str) -> str:
    """
    Decrypt an encrypted string
    
    Args:
        encrypted_text: Base64 encoded encrypted string
        
    Returns:
        Decrypted plaintext string
    """
    try:
        cipher = get_cipher()
        decrypted = cipher.decrypt(encrypted_text.encode())
        return decrypted.decode()
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        raise


def generate_encryption_key() -> str:
    """Generate a new Fernet encryption key"""
    return Fernet.generate_key().decode()


if __name__ == "__main__":
    # Test encryption/decryption
    test_value = "my_secret_password123"
    print(f"Original: {test_value}")
    
    encrypted = encrypt_value(test_value)
    print(f"Encrypted: {encrypted}")
    
    decrypted = decrypt_value(encrypted)
    print(f"Decrypted: {decrypted}")
    
    print(f"\nTest {'PASSED' if decrypted == test_value else 'FAILED'}")
    
    # Generate a new key for production
    print(f"\nGenerated encryption key for production:\n{generate_encryption_key()}")




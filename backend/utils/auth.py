"""
Authentication utilities for JWT token generation and password hashing
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import re
import jwt
from passlib.hash import bcrypt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import (
    JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_HOURS,
    PASSWORD_MIN_LENGTH, PASSWORD_REQUIRE_UPPERCASE,
    PASSWORD_REQUIRE_DIGITS, PASSWORD_REQUIRE_SPECIAL
)

# JWT Configuration from centralized config
SECRET_KEY = JWT_SECRET_KEY
ALGORITHM = JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = JWT_EXPIRATION_HOURS * 60

# Required auth - raises 403 if no token
security = HTTPBearer()

# Optional auth - doesn't raise error if no token
security_optional = HTTPBearer(auto_error=False)

class AuthUtils:
    """Authentication utility functions"""
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password strength according to security policy
        
        Returns:
            (is_valid, error_message)
        """
        if len(password) < PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
        
        if PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if PASSWORD_REQUIRE_DIGITS and not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character (!@#$%^&*...)"
        
        # Check for common weak passwords
        weak_passwords = ['password', '12345678', 'qwerty', 'admin123', 'password123']
        if password.lower() in weak_passwords:
            return False, "Password is too common. Please choose a stronger password"
        
        return True, None
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return bcrypt.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Dict:
        """Decode and verify a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict:
    """
    Dependency to get current authenticated user from JWT token
    Usage: user = Depends(get_current_user)
    """
    token = credentials.credentials
    
    try:
        payload = AuthUtils.decode_token(token)
        
        # Check if token has expired
        if datetime.utcnow().timestamp() > payload.get("exp", 0):
            raise HTTPException(status_code=401, detail="Token has expired")
        
        # Return user data from token
        return {
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "tenant_id": payload.get("tenant_id")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication credentials: {str(e)}")


def require_role(required_role: str):
    """
    Dependency to check if user has required role
    Usage: user = Depends(require_role("admin"))
    """
    def role_checker(current_user: Dict = Depends(get_current_user)) -> Dict:
        user_role = current_user.get("role", "viewer")
        
        # Role hierarchy: admin > user > viewer
        role_hierarchy = {"admin": 3, "user": 2, "viewer": 1}
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=403, 
                detail=f"Insufficient permissions. Required role: {required_role}"
            )
        
        return current_user
    
    return role_checker


# Optional authentication (doesn't fail if no token)
def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Security(security_optional)) -> Optional[Dict]:
    """
    Optional authentication - returns None if no token provided
    Uses security_optional which has auto_error=False to prevent 403 when no token is provided
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None
    except Exception:
        return None



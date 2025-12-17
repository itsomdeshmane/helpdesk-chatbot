"""
Authentication router - handles user registration, login, and verification
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from database.db_manager import db_manager
from utils.auth import AuthUtils, get_current_user

router = APIRouter(tags=["Authentication"])

# Request/Response Models
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=200)
    tenant_id: str = Field("default", max_length=100)

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    tenant_id: str
    is_active: bool
    created_at: str


@router.post("/register", response_model=UserResponse, summary="Register a new user")
async def register(request: RegisterRequest):
    """
    Register a new user
    
    - **username**: Unique username (3-50 characters, alphanumeric + underscore/hyphen only)
    - **email**: Valid email address
    - **password**: Strong password (minimum 8 characters, must include uppercase, digit, special char)
    - **full_name**: Optional full name
    - **tenant_id**: Organization/tenant identifier
    """
    try:
        # Validate password strength FIRST
        is_valid, error_msg = AuthUtils.validate_password(request.password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        with db_manager.get_connection() as conn:
            # Check if username already exists
            cursor = conn.execute("SELECT id FROM users WHERE username = %s", (request.username,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Username already registered")
            
            # Check if email already exists
            cursor = conn.execute("SELECT id FROM users WHERE email = %s", (request.email,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Email already registered")
            
            # Hash password (already validated)
            password_hash = AuthUtils.hash_password(request.password)
            
            # Insert new user
            insert_sql = """
            INSERT INTO users (username, email, password_hash, full_name, role, tenant_id, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor = conn.execute(insert_sql, (
                request.username,
                request.email,
                password_hash,
                request.full_name,
                'user',  # Default role
                request.tenant_id,
                True
            ))
            conn._conn.commit()
            
            user_id = cursor._cursor.lastrowid
            
            # Fetch created user
            cursor = conn.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
        
        print(f"✅ New user registered: {request.username} ({request.email})")
        
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "tenant_id": user["tenant_id"],
            "is_active": user["is_active"],
            "created_at": user["created_at"].isoformat() if user["created_at"] else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Registration error: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/login", response_model=LoginResponse, summary="Login user")
async def login(request: LoginRequest):
    """
    Login with username and password
    
    Returns JWT access token on success
    """
    try:
        with db_manager.get_connection() as conn:
            # Find user by username
            cursor = conn.execute(
                "SELECT * FROM users WHERE username = %s",
                (request.username,)
            )
            user = cursor.fetchone()
            
            if not user:
                raise HTTPException(status_code=401, detail="Invalid username or password")
            
            # Verify password
            if not AuthUtils.verify_password(request.password, user["password_hash"]):
                raise HTTPException(status_code=401, detail="Invalid username or password")
            
            # Check if user is active
            if not user["is_active"]:
                raise HTTPException(status_code=403, detail="User account is deactivated")
            
            # Update last login
            conn.execute(
                "UPDATE users SET last_login = %s WHERE id = %s",
                (datetime.utcnow(), user["id"])
            )
            conn._conn.commit()
        
        # Create JWT token
        token_data = {
            "user_id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "tenant_id": user["tenant_id"]
        }
        access_token = AuthUtils.create_access_token(token_data)
        
        print(f"✅ User logged in: {request.username} (Role: {user['role']})")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "tenant_id": user["tenant_id"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@router.get("/me", response_model=UserResponse, summary="Get current user")
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information
    
    Requires: Valid JWT token in Authorization header
    """
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM users WHERE id = %s", (current_user["user_id"],))
            user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "tenant_id": user["tenant_id"],
            "is_active": user["is_active"],
            "created_at": user["created_at"].isoformat() if user["created_at"] else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify", summary="Verify JWT token")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """
    Verify if JWT token is valid
    
    Returns user information if token is valid
    """
    return {
        "valid": True,
        "user": current_user
    }


@router.post("/logout", summary="Logout user")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout current user
    
    Note: JWT tokens are stateless, so logout is handled on the client side
    by removing the token. This endpoint is for logging purposes.
    """
    print(f"✅ User logged out: {current_user['username']}")
    return {"message": "Logged out successfully"}


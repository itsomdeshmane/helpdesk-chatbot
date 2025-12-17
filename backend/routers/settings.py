"""
Settings Router - User settings and database connection management
"""
from fastapi import APIRouter, Body, Depends, HTTPException
from typing import Optional, Dict, Any
import logging
import pymysql
from pymysql.cursors import DictCursor
import mysql.connector

from utils.auth import get_current_user
from utils.encryption import encrypt_value, decrypt_value
from database.db_manager import DatabaseManager
from llm.db_adapters import get_database_adapter

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Settings"], prefix="/settings")

# Initialize database manager
db_manager = DatabaseManager()


@router.get("/database-connection", summary="Get user's database connection settings")
async def get_database_connection(
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's saved database connection settings
    Password is never returned for security
    """
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT db_type, host, port, database_name, username
                FROM user_database_connections
                WHERE user_id = %s AND tenant_id = %s
                LIMIT 1
                """,
                (current_user['user_id'], current_user['tenant_id'])
            )
            
            result = cursor.fetchone()
            
            if result:
                return {
                    "success": True,
                    "data": {
                        "db_type": result.get('db_type', 'mysql'),  # Default to mysql for backward compatibility
                        "host": result['host'],
                        "port": result['port'],
                        "database": result['database_name'],
                        "username": result['username']
                        # Never return password
                    }
                }
            else:
                return {
                    "success": True,
                    "data": None
                }
    except Exception as e:
        logger.error(f"Error fetching database connection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/database-connection", summary="Save database connection settings")
async def save_database_connection(
    db_type: str = Body(default="mysql"),
    host: str = Body(...),
    port: int = Body(...),
    database: str = Body(...),
    username: str = Body(...),
    password: str = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Save or update user's database connection settings
    Supports MySQL, PostgreSQL, and SQL Server
    Password is encrypted before storage
    """
    try:
        with db_manager.get_connection() as conn:
            # Encrypt password before storage
            encrypted_password = encrypt_value(password)
            
            # Check if connection already exists
            cursor = conn.execute(
                """
                SELECT id FROM user_database_connections
                WHERE user_id = %s AND tenant_id = %s
                LIMIT 1
                """,
                (current_user['user_id'], current_user['tenant_id'])
            )
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing connection (include db_type)
                conn.execute(
                    """
                    UPDATE user_database_connections
                    SET db_type = %s, host = %s, port = %s, database_name = %s,
                        username = %s, encrypted_password = %s,
                        updated_at = NOW()
                    WHERE user_id = %s AND tenant_id = %s
                    """,
                    (db_type, host, port, database, username, encrypted_password,
                     current_user['user_id'], current_user['tenant_id'])
                )
            else:
                # Insert new connection (include db_type)
                conn.execute(
                    """
                    INSERT INTO user_database_connections
                    (user_id, tenant_id, db_type, host, port, database_name, username, encrypted_password)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (current_user['user_id'], current_user['tenant_id'], db_type,
                     host, port, database, username, encrypted_password)
                )
            
            conn.commit()
            
            logger.info(f"{db_type.upper()} database connection saved for user {current_user['username']}")
            
            return {
                "success": True,
                "message": f"{db_type.upper()} database connection saved successfully"
            }
    except Exception as e:
        logger.error(f"Error saving database connection: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-database-connection", summary="Test database connection")
async def test_database_connection(
    db_type: str = Body(default="mysql"),
    host: str = Body(...),
    port: int = Body(...),
    database: str = Body(...),
    username: str = Body(...),
    password: str = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Test database connection with provided credentials
    Supports MySQL, PostgreSQL, and SQL Server
    Does not save the connection
    """
    logger.info(f"Testing {db_type} connection for user {current_user.get('username', 'unknown')}")
    logger.info(f"Connection details: host={host}, port={port}, database={database}, username={username}")
    
    try:
        # Get appropriate database adapter
        adapter = get_database_adapter(db_type)
        
        # Create connection config
        connection_config = {
            'host': host,
            'port': port,
            'database': database,
            'user': username,
            'password': password
        }
        
        # Attempt to connect
        connection = adapter.create_connection(connection_config)
        
        logger.info("Connection established, testing with query...")
        
        # Test with a simple query
        if db_type == 'mysql':
            cursor = connection.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            cursor.close()
        elif db_type == 'postgresql':
            cursor = connection.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            cursor.close()
        elif db_type == 'sqlserver':
            cursor = connection.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            cursor.close()
        
        logger.info(f"Test query result: {result}")
        
        connection.close()
        
        logger.info(f"✅ {db_type.upper()} connection test successful for user {current_user.get('username', 'unknown')}")
        
        return {
            "success": True,
            "message": f"{db_type.upper()} connection successful"
        }
    except ValueError as e:
        # Unsupported database type
        error_msg = str(e)
        logger.warning(f"❌ Unsupported database type: {error_msg}")
        return {
            "success": False,
            "message": f"Unsupported database type: {db_type}"
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Error testing {db_type} connection: {error_msg}", exc_info=True)
        return {
            "success": False,
            "message": f"Connection Error: {error_msg}"
        }


@router.get("/user-connection-string", summary="Get user's connection string")
async def get_user_connection_string(
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's database connection as a connection string
    Used internally by the app to connect to user's database
    Includes db_type for multi-database support
    """
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT db_type, host, port, database_name, username, encrypted_password
                FROM user_database_connections
                WHERE user_id = %s AND tenant_id = %s
                LIMIT 1
                """,
                (current_user['user_id'], current_user['tenant_id'])
            )
            
            result = cursor.fetchone()
            
            if result:
                # Decrypt password
                password = decrypt_value(result['encrypted_password'])
                
                # Get database type (default to mysql for backward compatibility)
                db_type = result.get('db_type', 'mysql')
                
                # Build connection string
                connection_string = (
                    f"host={result['host']};"
                    f"port={result['port']};"
                    f"database={result['database_name']};"
                    f"user={result['username']};"
                    f"password={password}"
                )
                
                return {
                    "success": True,
                    "db_type": db_type,
                    "connection_string": connection_string
                }
            else:
                return {
                    "success": False,
                    "message": "No database connection configured"
                }
    except Exception as e:
        logger.error(f"Error getting connection string: {e}")
        raise HTTPException(status_code=500, detail=str(e))



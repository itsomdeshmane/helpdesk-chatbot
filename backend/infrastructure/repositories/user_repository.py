"""
User Repository
Handles persistence of user data and connections
"""

import logging
from typing import List, Optional, Dict, Any
from core.interfaces.repository import IRepository
from core.interfaces.database import IDatabaseConnection

logger = logging.getLogger(__name__)


class UserRepository(IRepository[Dict[str, Any]]):
    """
    Repository for user data persistence
    
    Following Repository Pattern:
    - Abstracts data access for users
    - Handles user connections and settings
    
    Following SOLID:
    - SRP: Single responsibility - user data access
    - DIP: Depends on IDatabaseConnection interface
    """
    
    def __init__(self, db: IDatabaseConnection):
        """
        Initialize user repository
        
        Args:
            db: Database connection (system database)
        """
        self._db = db
        logger.info("User Repository initialized")
    
    async def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID
        
        Args:
            user_id: User identifier
            
        Returns:
            User data if found, None otherwise
        """
        try:
            query = """
                SELECT user_id, username, email, role, tenant_id, is_active, created_at
                FROM users
                WHERE user_id = %s
            """
            results = await self._db.execute_query(query, (user_id,))
            
            return results[0] if results else None
            
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def get_all(
        self,
        filter: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all users matching filter
        
        Args:
            filter: Optional filter (e.g., {"tenant_id": "x"})
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of users
        """
        try:
            query = "SELECT user_id, username, email, role, tenant_id, is_active FROM users WHERE 1=1"
            params = []
            
            if filter:
                if 'tenant_id' in filter:
                    query += " AND tenant_id = %s"
                    params.append(filter['tenant_id'])
                if 'role' in filter:
                    query += " AND role = %s"
                    params.append(filter['role'])
                if 'is_active' in filter:
                    query += " AND is_active = %s"
                    params.append(filter['is_active'])
            
            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            return await self._db.execute_query(query, tuple(params))
            
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []
    
    async def add(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add new user
        
        Args:
            user: User data dictionary
            
        Returns:
            Added user data
        """
        try:
            query = """
                INSERT INTO users
                (user_id, username, email, password_hash, role, tenant_id, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            await self._db.execute_non_query(
                query,
                (
                    user['user_id'],
                    user['username'],
                    user['email'],
                    user['password_hash'],
                    user.get('role', 'user'),
                    user['tenant_id'],
                    user.get('is_active', True)
                )
            )
            
            logger.info(f"Added user {user['user_id']}")
            return user
            
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            raise
    
    async def update(self, user: Dict[str, Any]) -> bool:
        """
        Update existing user
        
        Args:
            user: User data with user_id
            
        Returns:
            True if successful
        """
        try:
            query = """
                UPDATE users
                SET email = %s, role = %s, is_active = %s
                WHERE user_id = %s
            """
            await self._db.execute_non_query(
                query,
                (user['email'], user.get('role'), user.get('is_active'), user['user_id'])
            )
            
            logger.info(f"Updated user {user['user_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False
    
    async def delete(self, user_id: str) -> bool:
        """
        Delete user
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful
        """
        try:
            await self._db.execute_non_query(
                "DELETE FROM users WHERE user_id = %s",
                (user_id,)
            )
            
            logger.info(f"Deleted user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False
    
    async def exists(self, user_id: str) -> bool:
        """
        Check if user exists
        
        Args:
            user_id: User identifier
            
        Returns:
            True if exists
        """
        try:
            query = "SELECT COUNT(*) as count FROM users WHERE user_id = %s"
            results = await self._db.execute_query(query, (user_id,))
            return results[0]['count'] > 0 if results else False
        except:
            return False
    
    async def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user by username
        
        Args:
            username: Username
            
        Returns:
            User data if found
        """
        try:
            query = """
                SELECT user_id, username, email, password_hash, role, tenant_id, is_active
                FROM users
                WHERE username = %s
            """
            results = await self._db.execute_query(query, (username,))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None
    
    async def get_user_database_connection(
        self,
        user_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get user's saved database connection
        
        Args:
            user_id: User identifier
            tenant_id: Tenant identifier
            
        Returns:
            Connection data if found
        """
        try:
            query = """
                SELECT host, port, database_name, username, encrypted_password
                FROM user_database_connections
                WHERE user_id = %s AND tenant_id = %s
                LIMIT 1
            """
            results = await self._db.execute_query(query, (user_id, tenant_id))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error getting user database connection: {e}")
            return None
    
    async def save_user_database_connection(
        self,
        user_id: str,
        tenant_id: str,
        connection_data: Dict[str, Any]
    ) -> bool:
        """
        Save user's database connection
        
        Args:
            user_id: User identifier
            tenant_id: Tenant identifier
            connection_data: Connection details
            
        Returns:
            True if successful
        """
        try:
            # Check if connection exists
            existing = await self.get_user_database_connection(user_id, tenant_id)
            
            if existing:
                # Update
                query = """
                    UPDATE user_database_connections
                    SET host = %s, port = %s, database_name = %s, 
                        username = %s, encrypted_password = %s
                    WHERE user_id = %s AND tenant_id = %s
                """
            else:
                # Insert
                query = """
                    INSERT INTO user_database_connections
                    (user_id, tenant_id, host, port, database_name, username, encrypted_password)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
            
            params = (
                connection_data['host'],
                connection_data['port'],
                connection_data['database_name'],
                connection_data['username'],
                connection_data['encrypted_password'],
                user_id,
                tenant_id
            ) if existing else (
                user_id,
                tenant_id,
                connection_data['host'],
                connection_data['port'],
                connection_data['database_name'],
                connection_data['username'],
                connection_data['encrypted_password']
            )
            
            await self._db.execute_non_query(query, params)
            
            logger.info(f"Saved database connection for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving user database connection: {e}")
            return False


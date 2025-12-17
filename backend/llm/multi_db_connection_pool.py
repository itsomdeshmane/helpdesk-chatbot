"""
Multi-Database Connection Pool - Supports MySQL, PostgreSQL, SQL Server
Enhanced connection pooling with database adapter pattern
"""
import logging
import threading
import time
from typing import Dict, Optional
from queue import Queue, Empty
from contextlib import contextmanager

from llm.db_adapters import get_database_adapter, DatabaseType

logger = logging.getLogger(__name__)


class MultiDBConnectionPool:
    """
    Thread-safe connection pool supporting multiple database types
    
    Supports:
    - MySQL (via pymysql)
    - PostgreSQL (via psycopg2)
    - SQL Server (via pyodbc)
    """
    
    def __init__(
        self,
        db_type: str,
        connection_config: Dict,
        pool_size: int = 5,
        max_overflow: int = 10,
        connection_timeout: int = 30,
        recycle_time: int = 3600
    ):
        """
        Initialize multi-database connection pool
        
        Args:
            db_type: Database type ('mysql', 'postgresql', 'sqlserver')
            connection_config: Database connection parameters
            pool_size: Number of connections to maintain
            max_overflow: Additional connections allowed when pool exhausted
            connection_timeout: Connection timeout in seconds
            recycle_time: Recycle connections after N seconds
        """
        self.db_type = db_type.lower()
        self.config = connection_config
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.connection_timeout = connection_timeout
        self.recycle_time = recycle_time
        
        # Get database adapter
        self.adapter = get_database_adapter(self.db_type)
        
        self.pool: Queue = Queue(maxsize=pool_size + max_overflow)
        self.lock = threading.Lock()
        
        # Metrics
        self.created_connections = 0
        self.recycled_connections = 0
        self.active_connections = 0
        self.peak_connections = 0
        
        # Initialize pool
        self._initialize_pool()
        
        logger.info(f"✅ Multi-DB Connection Pool initialized: {self.db_type}, size={pool_size}, max_overflow={max_overflow}")
    
    def _create_connection(self):
        """Create a new database connection using appropriate adapter"""
        try:
            conn = self.adapter.create_connection(self.config)
            
            # Store metadata
            conn._pool_created_at = time.time()
            conn._pool_db_type = self.db_type
            
            self.created_connections += 1
            logger.debug(f"Created new {self.db_type} connection (total: {self.created_connections})")
            
            return conn
        except Exception as e:
            logger.error(f"Failed to create {self.db_type} connection: {e}")
            raise
    
    def _initialize_pool(self):
        """Initialize the connection pool with connections"""
        for i in range(self.pool_size):
            try:
                conn = self._create_connection()
                self.pool.put(conn)
            except Exception as e:
                logger.error(f"Failed to initialize connection {i+1}: {e}")
                # Continue with fewer connections
    
    def _is_connection_alive(self, conn) -> bool:
        """Check if connection is still alive"""
        try:
            # Database-specific ping/test
            if self.db_type == DatabaseType.MYSQL.value:
                conn.ping(reconnect=False)
                return True
            elif self.db_type == DatabaseType.POSTGRESQL.value:
                # PostgreSQL: try a simple query
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                return True
            elif self.db_type == DatabaseType.SQLSERVER.value:
                # SQL Server: check connection
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                return True
            else:
                return True
        except:
            return False
    
    def _should_recycle(self, conn) -> bool:
        """Check if connection should be recycled"""
        if not hasattr(conn, '_pool_created_at'):
            return True
        
        age = time.time() - conn._pool_created_at
        return age > self.recycle_time
    
    def _close_connection(self, conn):
        """Close database connection"""
        try:
            if self.db_type == DatabaseType.MYSQL.value:
                conn.close()
            elif self.db_type == DatabaseType.POSTGRESQL.value:
                conn.close()
            elif self.db_type == DatabaseType.SQLSERVER.value:
                conn.close()
        except Exception as e:
            logger.error(f"Error closing {self.db_type} connection: {e}")
    
    def _get_cursor(self, conn):
        """Get cursor with appropriate settings for database type"""
        if self.db_type == DatabaseType.MYSQL.value:
            # MySQL: already using DictCursor from connection
            return conn.cursor()
        elif self.db_type == DatabaseType.POSTGRESQL.value:
            # PostgreSQL: use RealDictCursor for dict results
            import psycopg2.extras
            return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        elif self.db_type == DatabaseType.SQLSERVER.value:
            # SQL Server: regular cursor, convert to dict manually
            return conn.cursor()
        else:
            return conn.cursor()
    
    @contextmanager
    def get_connection(self, timeout: float = 5.0):
        """
        Get a connection from the pool (context manager)
        
        Args:
            timeout: Maximum time to wait for a connection
            
        Yields:
            Database connection
            
        Example:
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users")
        """
        conn = None
        start_time = time.time()
        
        try:
            # Try to get connection from pool
            try:
                conn = self.pool.get(timeout=timeout)
            except Empty:
                logger.warning(f"{self.db_type} pool exhausted, creating overflow connection")
                conn = self._create_connection()
            
            with self.lock:
                self.active_connections += 1
                self.peak_connections = max(self.peak_connections, self.active_connections)
            
            # Check if connection is still alive
            if not self._is_connection_alive(conn):
                logger.warning(f"Dead {self.db_type} connection detected, creating new one")
                self._close_connection(conn)
                conn = self._create_connection()
            
            # Check if connection should be recycled
            elif self._should_recycle(conn):
                logger.debug(f"Recycling old {self.db_type} connection")
                self._close_connection(conn)
                conn = self._create_connection()
                self.recycled_connections += 1
            
            # Yield connection for use
            yield conn
            
        except Exception as e:
            logger.error(f"{self.db_type} connection error: {e}")
            # Close bad connection
            if conn:
                try:
                    self._close_connection(conn)
                except:
                    pass
                conn = None
            raise
            
        finally:
            # Return connection to pool
            with self.lock:
                self.active_connections -= 1
            
            if conn and self._is_connection_alive(conn):
                try:
                    # Rollback any uncommitted transactions
                    conn.rollback()
                    
                    # Return to pool
                    self.pool.put_nowait(conn)
                except:
                    # Pool full, close connection
                    try:
                        self._close_connection(conn)
                    except:
                        pass
            
            elapsed = (time.time() - start_time) * 1000
            logger.debug(f"{self.db_type} connection checkout took {elapsed:.1f}ms")
    
    def close_all(self):
        """Close all connections in the pool"""
        logger.info(f"Closing all {self.db_type} connections in pool")
        
        closed = 0
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
                self._close_connection(conn)
                closed += 1
            except Empty:
                break
            except Exception as e:
                logger.error(f"Error closing {self.db_type} connection: {e}")
        
        logger.info(f"Closed {closed} {self.db_type} connections")
    
    def get_stats(self) -> Dict[str, any]:
        """Get pool statistics"""
        return {
            'db_type': self.db_type,
            'pool_size': self.pool_size,
            'max_overflow': self.max_overflow,
            'available_connections': self.pool.qsize(),
            'active_connections': self.active_connections,
            'peak_connections': self.peak_connections,
            'created_connections': self.created_connections,
            'recycled_connections': self.recycled_connections,
            'utilization': f"{(self.active_connections / (self.pool_size + self.max_overflow) * 100):.1f}%"
        }


# Global connection pools (one per database type + connection string)
_connection_pools: Dict[str, MultiDBConnectionPool] = {}
_pools_lock = threading.Lock()


def get_multi_db_connection_pool(
    db_type: str,
    connection_config: Dict,
    pool_size: int = 5,
    max_overflow: int = 10
) -> MultiDBConnectionPool:
    """
    Get or create a connection pool for the given database type and configuration
    
    Args:
        db_type: Database type ('mysql', 'postgresql', 'sqlserver')
        connection_config: Database connection parameters
        pool_size: Number of connections to maintain
        max_overflow: Additional connections when pool exhausted
        
    Returns:
        MultiDBConnectionPool instance
    """
    global _connection_pools
    
    # Create a unique key for this configuration
    key_parts = [
        db_type.lower(),
        connection_config.get('host', 'localhost'),
        str(connection_config.get('port', '')),
        connection_config.get('database', ''),
        connection_config.get('user', '')
    ]
    pool_key = ':'.join(key_parts)
    
    with _pools_lock:
        if pool_key not in _connection_pools:
            logger.info(f"Creating new {db_type} connection pool for: {pool_key}")
            _connection_pools[pool_key] = MultiDBConnectionPool(
                db_type,
                connection_config,
                pool_size=pool_size,
                max_overflow=max_overflow
            )
        
        return _connection_pools[pool_key]


def close_all_pools():
    """Close all connection pools"""
    global _connection_pools
    
    with _pools_lock:
        for pool_key, pool in _connection_pools.items():
            logger.info(f"Closing pool: {pool_key}")
            pool.close_all()
        
        _connection_pools.clear()


def get_pool_stats() -> Dict[str, Dict]:
    """Get statistics for all connection pools"""
    global _connection_pools
    
    with _pools_lock:
        return {
            pool_key: pool.get_stats()
            for pool_key, pool in _connection_pools.items()
        }


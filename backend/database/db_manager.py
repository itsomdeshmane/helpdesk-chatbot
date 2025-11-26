"""
Database manager for chat history and training data - MySQL version
"""
import mysql.connector
from mysql.connector import Error, pooling
from pathlib import Path
from datetime import datetime
import json
from contextlib import contextmanager

# Import MySQL config
try:
    from config import (
        MYSQL_HOST,
        MYSQL_PORT,
        MYSQL_USER,
        MYSQL_PASSWORD,
        MYSQL_DATABASE
    )
except ImportError:
    # Fallback to defaults if config not available
    MYSQL_HOST = "localhost"
    MYSQL_PORT = 3306
    MYSQL_USER = "root"
    MYSQL_PASSWORD = ""
    MYSQL_DATABASE = "helpdesk_db"

class DatabaseManager:
    def __init__(self):
        """Initialize database manager with connection pool"""
        self.connection_pool = None
        self.create_database_if_not_exists()
        self.init_connection_pool()
        self.init_database()
    
    def create_database_if_not_exists(self):
        """Create database if it doesn't exist"""
        try:
            temp_connection = mysql.connector.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            cursor = temp_connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            temp_connection.commit()
            cursor.close()
            temp_connection.close()
            print(f"✅ Database '{MYSQL_DATABASE}' ready", flush=True)
        except Error as e:
            print(f"❌ Error creating database: {e}", flush=True)
    
    def init_connection_pool(self):
        """Initialize MySQL connection pool"""
        try:
            self.connection_pool = pooling.MySQLConnectionPool(
                pool_name="helpdesk_pool",
                pool_size=5,
                pool_reset_session=True,
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci',
                autocommit=False
            )
            print(f"✅ MySQL connection pool initialized successfully", flush=True)
            print(f"   Host: {MYSQL_HOST}:{MYSQL_PORT}", flush=True)
            print(f"   Database: {MYSQL_DATABASE}", flush=True)
        except Error as e:
            print(f"❌ Error creating MySQL connection pool: {e}", flush=True)
            print(f"   Please check your MySQL credentials and ensure MySQL server is running.", flush=True)
            self.connection_pool = None
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool (context manager)"""
        connection = None
        try:
            if self.connection_pool is None:
                raise Error("Connection pool not initialized")
            
            connection = self.connection_pool.get_connection()
            
            # Create a dict-like cursor
            class DictCursor:
                def __init__(self, cursor):
                    self._cursor = cursor
                    self._results = []
                
                def execute(self, query, params=None):
                    self._cursor.execute(query, params or ())
                    return self
                
                def fetchone(self):
                    row = self._cursor.fetchone()
                    if row:
                        columns = [desc[0] for desc in self._cursor.description]
                        return dict(zip(columns, row))
                    return None
                
                def fetchall(self):
                    rows = self._cursor.fetchall()
                    if rows:
                        columns = [desc[0] for desc in self._cursor.description]
                        return [dict(zip(columns, row)) for row in rows]
                    return []
            
            # Wrap connection to provide dict-like cursor
            class ConnectionWrapper:
                def __init__(self, conn):
                    self._conn = conn
                
                def execute(self, query, params=None):
                    cursor = self._conn.cursor()
                    return DictCursor(cursor).execute(query, params)
                
                def commit(self):
                    self._conn.commit()
                
                def rollback(self):
                    self._conn.rollback()
                
                def close(self):
                    self._conn.close()
            
            yield ConnectionWrapper(connection)
            
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Database error: {e}", flush=True)
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def init_database(self):
        """Initialize database with schema"""
        try:
            # Initialize tables using manual creation method (more reliable)
            with self.get_connection() as conn:
                self._create_tables_manually(conn)
        except Error as e:
            print(f"❌ Error initializing database: {e}", flush=True)
        except Exception as e:
            print(f"❌ Unexpected error initializing database: {e}", flush=True)
    
    def _create_tables_manually(self, conn):
        """Create tables manually if schema file is not found"""
        tables = [
            """CREATE TABLE IF NOT EXISTS chat_interactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tenant_id VARCHAR(255) NOT NULL,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                module VARCHAR(255) DEFAULT NULL,
                helpful INT DEFAULT 0,
                response_time FLOAT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_tenant_created (tenant_id, created_at),
                INDEX idx_module (module)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
            
            """CREATE TABLE IF NOT EXISTS faq_questions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                category VARCHAR(255) DEFAULT NULL,
                module VARCHAR(255) DEFAULT NULL,
                source_document VARCHAR(500) DEFAULT NULL,
                popularity INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_faq_category (category),
                INDEX idx_faq_module (module)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
            
            """CREATE TABLE IF NOT EXISTS response_patterns (
                id INT AUTO_INCREMENT PRIMARY KEY,
                query_type VARCHAR(255) NOT NULL,
                pattern_template TEXT NOT NULL,
                success_rate FLOAT DEFAULT 0.0,
                usage_count INT DEFAULT 0
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"""
        ]
        
        cursor = conn._conn.cursor()
        for table_sql in tables:
            cursor.execute(table_sql)
        cursor.close()
        conn.commit()
        print("✅ Tables created manually", flush=True)
    
    def save_interaction(self, tenant_id: str, query: str, response: str, module: str = None, response_time: float = None):
        """Save chat interaction"""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    """INSERT INTO chat_interactions 
                       (tenant_id, query, response, module, response_time) 
                       VALUES (%s, %s, %s, %s, %s)""",
                    (tenant_id, query, response, module, response_time)
                )
                conn.commit()
        except Error as e:
            print(f"Error saving interaction: {e}", flush=True)
    
    def get_recent_interactions(self, tenant_id: str, limit: int = 10):
        """Get recent interactions for context"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT query, response, module, created_at 
                       FROM chat_interactions 
                       WHERE tenant_id = %s 
                       ORDER BY created_at DESC 
                       LIMIT %s""",
                    (tenant_id, limit)
                )
                return cursor.fetchall()
        except Error as e:
            print(f"Error getting interactions: {e}", flush=True)
            return []
    
    def get_frequently_asked_questions(self, tenant_id: str = "default", limit: int = 10, module: str = None):
        """
        Get frequently asked questions from chat history.
        Groups similar questions and returns top N by frequency.
        """
        try:
            with self.get_connection() as conn:
                # Build query based on filters
                query = """
                    SELECT 
                        LOWER(TRIM(query)) as normalized_query,
                        query as original_query,
                        module,
                        COUNT(*) as frequency,
                        MAX(created_at) as last_asked
                    FROM chat_interactions
                    WHERE tenant_id = %s
                        AND CHAR_LENGTH(query) > 10
                """
                params = [tenant_id]
                
                if module:
                    query += " AND module = %s"
                    params.append(module)
                
                query += """
                    GROUP BY normalized_query
                    ORDER BY frequency DESC, last_asked DESC
                    LIMIT %s
                """
                params.append(limit)
                
                cursor = conn.execute(query, tuple(params))
                results = cursor.fetchall()
                
                # Format FAQs
                faqs = []
                for row in results:
                    faqs.append({
                        "question": row['original_query'],
                        "frequency": row['frequency'],
                        "module": row['module'],
                        "last_asked": str(row['last_asked']) if row['last_asked'] else None
                    })
                
                return faqs
        except Error as e:
            print(f"Error getting FAQs: {e}", flush=True)
            return []
    
    def get_module_statistics(self, tenant_id: str = "default"):
        """Get statistics by module"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT 
                        module, 
                        COUNT(*) as count,
                        AVG(response_time) as avg_time
                       FROM chat_interactions 
                       WHERE tenant_id = %s AND module IS NOT NULL
                       GROUP BY module
                       ORDER BY count DESC""",
                    (tenant_id,)
                )
                return cursor.fetchall()
        except Error as e:
            print(f"Error getting module stats: {e}", flush=True)
            return []

# Singleton instance
db_manager = DatabaseManager()

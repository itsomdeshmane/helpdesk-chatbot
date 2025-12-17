"""
Database Settings Router - Manage multi-database connections
Supports MySQL, PostgreSQL, SQL Server
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import logging
import json
from pathlib import Path

from llm.db_adapters import DatabaseAdapterFactory, get_database_adapter
from llm.multi_db_connection_pool import get_multi_db_connection_pool

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/database-settings",
    tags=["Database Settings"]
)


class DatabaseConnection(BaseModel):
    """Database connection configuration"""
    name: str = Field(..., description="Connection name")
    db_type: str = Field(..., description="Database type (mysql, postgresql, sqlserver)")
    host: str = Field(default="localhost", description="Database host")
    port: Optional[int] = Field(default=None, description="Database port (default per DB type)")
    database: str = Field(..., description="Database name")
    user: str = Field(..., description="Database user")
    password: str = Field(..., description="Database password")
    is_default: bool = Field(default=False, description="Set as default connection")


class ConnectionTestRequest(BaseModel):
    """Test database connection"""
    db_type: str
    host: str
    port: Optional[int] = None
    database: str
    user: str
    password: str


class DatabaseConnectionsManager:
    """Manage saved database connections"""
    
    def __init__(self, config_file: str = "data/db_connections.json"):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.connections: Dict[str, dict] = self._load_connections()
    
    def _load_connections(self) -> Dict[str, dict]:
        """Load connections from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load connections: {e}")
                return {}
        return {}
    
    def _save_connections(self):
        """Save connections to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.connections, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save connections: {e}")
            raise
    
    def add_connection(self, connection: DatabaseConnection) -> dict:
        """Add or update a connection"""
        # Validate database type
        supported = DatabaseAdapterFactory.get_supported_databases()
        if connection.db_type.lower() not in supported:
            raise ValueError(f"Unsupported database type: {connection.db_type}. Supported: {supported}")
        
        # Set default port if not provided
        if connection.port is None:
            default_ports = DatabaseAdapterFactory.get_default_ports()
            connection.port = default_ports.get(connection.db_type.lower())
        
        # If this is set as default, unset others
        if connection.is_default:
            for conn_name, conn_data in self.connections.items():
                conn_data['is_default'] = False
        
        # Store connection (don't save password in plain text in production!)
        self.connections[connection.name] = {
            'db_type': connection.db_type.lower(),
            'host': connection.host,
            'port': connection.port,
            'database': connection.database,
            'user': connection.user,
            'password': connection.password,  # TODO: Encrypt in production
            'is_default': connection.is_default
        }
        
        self._save_connections()
        
        logger.info(f"✅ Saved database connection: {connection.name} ({connection.db_type})")
        
        # Return without password
        result = self.connections[connection.name].copy()
        result['password'] = '****' if result['password'] else ''
        return result
    
    def get_connection(self, name: str) -> Optional[dict]:
        """Get a connection by name"""
        return self.connections.get(name)
    
    def get_all_connections(self, include_passwords: bool = False) -> List[dict]:
        """Get all connections"""
        connections = []
        for name, conn in self.connections.items():
            conn_data = conn.copy()
            conn_data['name'] = name
            if not include_passwords:
                conn_data['password'] = '****' if conn_data['password'] else ''
            connections.append(conn_data)
        return connections
    
    def get_default_connection(self) -> Optional[dict]:
        """Get the default connection"""
        for name, conn in self.connections.items():
            if conn.get('is_default', False):
                result = conn.copy()
                result['name'] = name
                return result
        return None
    
    def delete_connection(self, name: str):
        """Delete a connection"""
        if name in self.connections:
            del self.connections[name]
            self._save_connections()
            logger.info(f"🗑️  Deleted database connection: {name}")
        else:
            raise KeyError(f"Connection not found: {name}")
    
    def test_connection(self, config: dict) -> dict:
        """Test a database connection"""
        try:
            adapter = get_database_adapter(config['db_type'])
            
            # Set default port if not provided
            if config.get('port') is None:
                default_ports = DatabaseAdapterFactory.get_default_ports()
                config['port'] = default_ports.get(config['db_type'].lower())
            
            # Try to create connection
            conn = adapter.create_connection(config)
            
            # Test query based on database type
            if config['db_type'] == 'mysql':
                cursor = conn.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                cursor.close()
            elif config['db_type'] == 'postgresql':
                cursor = conn.cursor()
                cursor.execute("SELECT version()")
                version = cursor.fetchone()
                cursor.close()
            elif config['db_type'] == 'sqlserver':
                cursor = conn.cursor()
                cursor.execute("SELECT @@VERSION")
                version = cursor.fetchone()
                cursor.close()
            else:
                version = None
            
            conn.close()
            
            return {
                'success': True,
                'message': 'Connection successful!',
                'version': str(version) if version else 'Unknown'
            }
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {
                'success': False,
                'message': f'Connection failed: {str(e)}',
                'error': str(e)
            }


# Global manager instance
_manager = DatabaseConnectionsManager()


@router.get("/supported-databases")
async def get_supported_databases():
    """Get list of supported database types"""
    return {
        "success": True,
        "databases": DatabaseAdapterFactory.get_supported_databases(),
        "default_ports": DatabaseAdapterFactory.get_default_ports()
    }


@router.get("/connections")
async def list_connections():
    """List all saved database connections"""
    try:
        connections = _manager.get_all_connections(include_passwords=False)
        return {
            "success": True,
            "count": len(connections),
            "connections": connections
        }
    except Exception as e:
        logger.error(f"Failed to list connections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connections/default")
async def get_default_connection():
    """Get the default database connection"""
    try:
        conn = _manager.get_default_connection()
        if conn:
            # Remove password from response
            conn['password'] = '****' if conn['password'] else ''
            return {
                "success": True,
                "connection": conn
            }
        else:
            return {
                "success": False,
                "message": "No default connection set"
            }
    except Exception as e:
        logger.error(f"Failed to get default connection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connections/{name}")
async def get_connection(name: str):
    """Get a specific database connection"""
    try:
        conn = _manager.get_connection(name)
        if conn:
            # Remove password from response
            result = conn.copy()
            result['name'] = name
            result['password'] = '****' if result['password'] else ''
            return {
                "success": True,
                "connection": result
            }
        else:
            raise HTTPException(status_code=404, detail=f"Connection not found: {name}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get connection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/connections")
async def create_connection(connection: DatabaseConnection):
    """Create or update a database connection"""
    try:
        result = _manager.add_connection(connection)
        return {
            "success": True,
            "message": f"Connection '{connection.name}' saved successfully",
            "connection": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create connection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/connections/{name}")
async def delete_connection(name: str):
    """Delete a database connection"""
    try:
        _manager.delete_connection(name)
        return {
            "success": True,
            "message": f"Connection '{name}' deleted successfully"
        }
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete connection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-connection")
async def test_connection(request: ConnectionTestRequest):
    """Test a database connection"""
    try:
        config = {
            'db_type': request.db_type.lower(),
            'host': request.host,
            'port': request.port,
            'database': request.database,
            'user': request.user,
            'password': request.password
        }
        
        result = _manager.test_connection(config)
        return result
        
    except Exception as e:
        logger.error(f"Connection test error: {e}")
        return {
            "success": False,
            "message": f"Test failed: {str(e)}",
            "error": str(e)
        }


@router.get("/connection-string-format/{db_type}")
async def get_connection_string_format(db_type: str):
    """Get connection string format for a database type"""
    try:
        adapter = get_database_adapter(db_type)
        return {
            "success": True,
            "db_type": db_type,
            "format": adapter.get_connection_string_format()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get connection string format: {e}")
        raise HTTPException(status_code=500, detail=str(e))


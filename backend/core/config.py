"""
Enhanced Configuration Module - SOLID-Compliant
Centralized configuration management with validation
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class OpenAIConfig(BaseSettings):
    """OpenAI configuration"""
    openai_api_key: str
    gpt_model: str = "gpt-4"
    embedding_model: str = "text-embedding-3-small"
    gpt_temperature: float = 0.2
    gpt_max_tokens: int = 500
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Convenience properties with original names
    @property
    def api_key(self) -> str:
        return self.openai_api_key
    
    @property
    def model(self) -> str:
        return self.gpt_model
    
    @property
    def temperature(self) -> float:
        return self.gpt_temperature
    
    @property
    def max_tokens(self) -> int:
        return self.gpt_max_tokens


class PineconeConfig(BaseSettings):
    """Pinecone vector database configuration"""
    pinecone_api_key: Optional[str] = None
    pinecone_index_name: str = "erp-helpdesk"
    use_pinecone: bool = False
    
    @field_validator("use_pinecone", mode="before")
    @classmethod
    def parse_use_pinecone(cls, v):
        if isinstance(v, str):
            return v.lower() == "true"
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Convenience properties
    @property
    def api_key(self) -> Optional[str]:
        return self.pinecone_api_key
    
    @property
    def index_name(self) -> str:
        return self.pinecone_index_name


class SystemDatabaseConfig(BaseSettings):
    """System MySQL database configuration (from environment)"""
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = "helpdesk_db"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Convenience properties
    @property
    def host(self) -> str:
        return self.mysql_host
    
    @property
    def port(self) -> int:
        return self.mysql_port
    
    @property
    def user(self) -> str:
        return self.mysql_user
    
    @property
    def password(self) -> str:
        return self.mysql_password
    
    @property
    def database(self) -> str:
        return self.mysql_database


class RedisConfig(BaseSettings):
    """Redis cache configuration"""
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db: int = 0
    
    # Cache TTL settings (in seconds)
    cache_embedding_ttl: int = 86400
    cache_search_ttl: int = 3600
    cache_response_ttl: int = 1800
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Convenience properties
    @property
    def host(self) -> str:
        return self.redis_host
    
    @property
    def port(self) -> int:
        return self.redis_port
    
    @property
    def password(self) -> Optional[str]:
        return self.redis_password
    
    @property
    def db(self) -> int:
        return self.redis_db
    
    @property
    def embedding_ttl(self) -> int:
        return self.cache_embedding_ttl
    
    @property
    def search_ttl(self) -> int:
        return self.cache_search_ttl
    
    @property
    def response_ttl(self) -> int:
        return self.cache_response_ttl


class SearchConfig(BaseSettings):
    """Search configuration"""
    use_hybrid_search: bool = True
    hybrid_search_alpha: float = 0.6
    use_query_rewriting: bool = True
    search_top_k: int = 5
    
    @field_validator("use_hybrid_search", "use_query_rewriting", mode="before")
    @classmethod
    def parse_bool(cls, v):
        if isinstance(v, str):
            return v.lower() == "true"
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Convenience property
    @property
    def top_k(self) -> int:
        return self.search_top_k


class FeatureFlags(BaseSettings):
    """Feature flags"""
    enable_streaming: bool = True
    enable_source_attribution: bool = True
    enable_quality_scoring: bool = True
    enable_suggestions: bool = True
    enable_feedback: bool = True
    
    @field_validator("*", mode="before")
    @classmethod
    def parse_bool(cls, v):
        if isinstance(v, str):
            return v.lower() == "true"
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class SecurityConfig(BaseSettings):
    """Security configuration"""
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # CORS Configuration
    environment: str = "development"
    cors_origins: str = "http://localhost:4200,http://localhost:3000"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Convenience property to return as list
    def get_cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list"""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.cors_origins if isinstance(self.cors_origins, list) else [self.cors_origins]


class AppConfig:
    """
    Main application configuration
    
    Aggregates all configuration sections
    Following SOLID:
    - SRP: Each config class has single responsibility
    - OCP: Can add new config sections without modification
    - ISP: Segregated interfaces for different config areas
    """
    
    def __init__(self):
        """Initialize configuration"""
        self.openai = OpenAIConfig()
        self.pinecone = PineconeConfig()
        self.system_database = SystemDatabaseConfig()
        self.redis = RedisConfig()
        self.search = SearchConfig()
        self.features = FeatureFlags()
        self.security = SecurityConfig()
        
        # Validate critical settings
        self._validate()
    
    def _validate(self):
        """Validate configuration"""
        errors = []
        
        # Critical checks
        if not self.openai.api_key:
            errors.append("OPENAI_API_KEY is required")
        
        if self.pinecone.use_pinecone and not self.pinecone.api_key:
            errors.append("PINECONE_API_KEY is required when USE_PINECONE=true")
        
        # Security checks
        if self.security.environment == "production":
            if len(self.security.jwt_secret_key) < 32:
                errors.append("JWT_SECRET_KEY should be at least 32 characters in production")
            
            cors_list = self.security.get_cors_origins_list()
            if not cors_list or "*" in cors_list:
                errors.append("CORS_ORIGINS must be explicitly set in production (no wildcards)")
        
        if errors:
            raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {error}" for error in errors))
    
    def to_dict(self):
        """Convert configuration to dictionary (for debugging)"""
        return {
            "openai": {
                "model": self.openai.model,
                "embedding_model": self.openai.embedding_model,
                "temperature": self.openai.temperature,
                "max_tokens": self.openai.max_tokens,
                "api_key": "***" + self.openai.api_key[-4:] if self.openai.api_key else None
            },
            "pinecone": {
                "use_pinecone": self.pinecone.use_pinecone,
                "index_name": self.pinecone.index_name,
                "api_key": "***" + self.pinecone.api_key[-4:] if self.pinecone.api_key else None
            },
            "system_database": {
                "host": self.system_database.host,
                "port": self.system_database.port,
                "database": self.system_database.database
            },
            "search": {
                "use_hybrid_search": self.search.use_hybrid_search,
                "top_k": self.search.top_k
            },
            "features": {
                "streaming": self.features.enable_streaming,
                "source_attribution": self.features.enable_source_attribution,
                "quality_scoring": self.features.enable_quality_scoring
            },
            "security": {
                "environment": self.security.environment,
                "cors_origins": self.security.get_cors_origins_list()
            }
        }


# Global configuration instance (will be injected via DI in refactored code)
app_config = AppConfig()


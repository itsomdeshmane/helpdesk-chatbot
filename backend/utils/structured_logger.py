"""
Structured Logging Utility
Replaces print() statements with proper logging
Production-ready with JSON formatting for log aggregation
"""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
import os

# Get log level from environment
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "text")  # "text" or "json"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs JSON for production
    """
    
    def format(self, record: logging.LogRecord) -> str:
        if LOG_FORMAT == "json":
            # JSON format for production (easy to parse by log aggregators)
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }
            
            # Add exception info if present
            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)
            
            # Add extra fields if present
            if hasattr(record, 'extra'):
                log_data.update(record.extra)
            
            return json.dumps(log_data)
        else:
            # Human-readable format for development
            # Add emoji for visual distinction
            emoji_map = {
                "DEBUG": "🐛",
                "INFO": "ℹ️ ",
                "WARNING": "⚠️ ",
                "ERROR": "❌",
                "CRITICAL": "🔥"
            }
            emoji = emoji_map.get(record.levelname, "📝")
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            return f"{emoji} {timestamp} [{record.levelname}] {record.name}: {record.getMessage()}"


class AppLogger:
    """
    Application logger with convenience methods
    """
    
    def __init__(self, name: str = "helpdesk"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(console_handler)
        
        # File handler (optional)
        log_file = os.getenv("LOG_FILE")
        if log_file:
            try:
                os.makedirs(os.path.dirname(log_file), exist_ok=True)
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(logging.INFO)
                file_handler.setFormatter(StructuredFormatter())
                self.logger.addHandler(file_handler)
            except Exception as e:
                print(f"Warning: Could not create log file {log_file}: {e}")
        
        # Don't propagate to root logger
        self.logger.propagate = False
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, exc_info=None, **kwargs):
        """Log error message"""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)
    
    def critical(self, message: str, exc_info=None, **kwargs):
        """Log critical message"""
        self.logger.critical(message, exc_info=exc_info, extra=kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback"""
        self.logger.exception(message, extra=kwargs)
    
    # Convenience methods with context
    def api_request(self, method: str, path: str, status: int, duration_ms: float, **kwargs):
        """Log API request"""
        self.info(
            f"{method} {path} -> {status} ({duration_ms:.0f}ms)",
            method=method,
            path=path,
            status=status,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def db_query(self, query_type: str, duration_ms: float, rows: int = None, **kwargs):
        """Log database query"""
        msg = f"DB {query_type} ({duration_ms:.0f}ms)"
        if rows is not None:
            msg += f" - {rows} rows"
        self.debug(msg, query_type=query_type, duration_ms=duration_ms, rows=rows, **kwargs)
    
    def llm_call(self, model: str, duration_ms: float, tokens: int = None, **kwargs):
        """Log LLM API call"""
        msg = f"LLM {model} ({duration_ms:.0f}ms)"
        if tokens:
            msg += f" - {tokens} tokens"
        self.info(msg, model=model, duration_ms=duration_ms, tokens=tokens, **kwargs)
    
    def user_action(self, action: str, user_id: str = None, **kwargs):
        """Log user action"""
        msg = f"User action: {action}"
        if user_id:
            msg += f" (user: {user_id})"
        self.info(msg, action=action, user_id=user_id, **kwargs)


# Global logger instance
_logger = None

def get_logger(name: str = "helpdesk") -> AppLogger:
    """
    Get or create logger instance
    """
    global _logger
    if _logger is None:
        _logger = AppLogger(name)
        _logger.info(f"Logger initialized - Level: {LOG_LEVEL}, Format: {LOG_FORMAT}, Environment: {ENVIRONMENT}")
    return _logger


# Convenience functions for backward compatibility
def log_info(message: str, **kwargs):
    """Log info message"""
    get_logger().info(message, **kwargs)

def log_error(message: str, **kwargs):
    """Log error message"""
    get_logger().error(message, **kwargs)

def log_warning(message: str, **kwargs):
    """Log warning message"""
    get_logger().warning(message, **kwargs)

def log_debug(message: str, **kwargs):
    """Log debug message"""
    get_logger().debug(message, **kwargs)


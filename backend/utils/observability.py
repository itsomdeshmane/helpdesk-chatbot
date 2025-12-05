"""
Observability Module - Production Ready
Provides structured logging, metrics, and tracing for the chatbot
"""

import os
import sys
import json
import time
import uuid
import threading
import functools
from datetime import datetime
from typing import Any, Dict, Optional, Callable
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from logging.handlers import RotatingFileHandler
import traceback


class LogLevel(Enum):
    """Log levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LogContext:
    """Context for a log entry"""
    request_id: str = ""
    session_id: str = ""
    tenant_id: str = ""
    user_id: str = ""
    operation: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Metrics:
    """Metrics data structure"""
    latency_ms: float = 0.0
    tokens_used: int = 0
    documents_searched: int = 0
    cache_hit: bool = False
    success: bool = True
    error_type: str = ""


class StructuredLogger:
    """
    Production-ready structured logger with JSON output.
    Supports context propagation, metrics, and multiple output targets.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern for logger"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the structured logger"""
        if self._initialized:
            return
        
        self._initialized = True
        self._context = threading.local()
        
        # Get log configuration from environment
        self.log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.log_format = os.getenv('LOG_FORMAT', 'json')  # 'json' or 'text'
        self.log_file = os.getenv('LOG_FILE', 'logs/helpdesk.log')
        
        # Create logs directory
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Setup Python logger
        self._logger = logging.getLogger('helpdesk')
        self._logger.setLevel(getattr(logging, self.log_level, logging.INFO))
        
        # Remove existing handlers
        self._logger.handlers = []
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self._get_formatter())
        self._logger.addHandler(console_handler)
        
        # File handler with rotation
        try:
            file_handler = RotatingFileHandler(
                self.log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(self._get_formatter())
            self._logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not create log file handler: {e}", flush=True)
        
        # Metrics storage (in-memory, should be replaced with proper metrics system)
        self._metrics = {
            'requests_total': 0,
            'requests_success': 0,
            'requests_failed': 0,
            'latency_sum_ms': 0.0,
            'cache_hits': 0,
            'cache_misses': 0,
            'tokens_used': 0
        }
        self._metrics_lock = threading.Lock()
        
        print(f"✅ Structured logger initialized (level={self.log_level}, format={self.log_format})", flush=True)
    
    def _get_formatter(self) -> logging.Formatter:
        """Get the appropriate formatter based on configuration"""
        if self.log_format == 'json':
            return JsonFormatter()
        else:
            return logging.Formatter(
                '%(asctime)s - %(levelname)s - [%(request_id)s] %(message)s'
            )
    
    def _get_context(self) -> LogContext:
        """Get the current context"""
        if not hasattr(self._context, 'current'):
            self._context.current = LogContext()
        return self._context.current
    
    def set_context(self, **kwargs):
        """Set context values"""
        ctx = self._get_context()
        for key, value in kwargs.items():
            if hasattr(ctx, key):
                setattr(ctx, key, value)
            else:
                ctx.extra[key] = value
    
    def clear_context(self):
        """Clear the current context"""
        self._context.current = LogContext()
    
    @contextmanager
    def context(self, **kwargs):
        """Context manager for temporary context"""
        old_context = self._get_context()
        new_context = LogContext(
            request_id=old_context.request_id,
            session_id=old_context.session_id,
            tenant_id=old_context.tenant_id,
            user_id=old_context.user_id,
            operation=old_context.operation,
            extra=dict(old_context.extra)
        )
        
        for key, value in kwargs.items():
            if hasattr(new_context, key):
                setattr(new_context, key, value)
            else:
                new_context.extra[key] = value
        
        self._context.current = new_context
        try:
            yield
        finally:
            self._context.current = old_context
    
    def _log(self, level: LogLevel, message: str, **extra):
        """Internal log method"""
        ctx = self._get_context()
        
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': level.value,
            'log_message': message,  # Renamed to avoid conflict with LogRecord
            'request_id': ctx.request_id or str(uuid.uuid4())[:8],
            'session_id': ctx.session_id,
            'tenant_id': ctx.tenant_id,
            'user_id': ctx.user_id,
            'operation': ctx.operation,
            **ctx.extra,
            **extra
        }
        
        # Remove conflicting keys that LogRecord uses internally
        reserved_keys = {'message', 'msg', 'args', 'exc_info', 'exc_text', 'stack_info',
                        'levelno', 'levelname', 'pathname', 'filename', 'module',
                        'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                        'thread', 'threadName', 'processName', 'process', 'name'}
        
        # Filter out reserved keys and empty values
        safe_extra = {k: v for k, v in log_data.items() if v and k not in reserved_keys}
        
        # Log based on level
        log_method = getattr(self._logger, level.value)
        
        if self.log_format == 'json':
            # For JSON format, pass the full log_data as the message
            log_method(log_data)
        else:
            # For text format, just log the message with safe extra data
            log_method(message, extra=safe_extra)
    
    def debug(self, message: str, **extra):
        """Log debug message"""
        self._log(LogLevel.DEBUG, message, **extra)
    
    def info(self, message: str, **extra):
        """Log info message"""
        self._log(LogLevel.INFO, message, **extra)
    
    def warning(self, message: str, **extra):
        """Log warning message"""
        self._log(LogLevel.WARNING, message, **extra)
    
    def error(self, message: str, **extra):
        """Log error message"""
        if 'exception' not in extra:
            extra['traceback'] = traceback.format_exc()
        self._log(LogLevel.ERROR, message, **extra)
    
    def critical(self, message: str, **extra):
        """Log critical message"""
        if 'exception' not in extra:
            extra['traceback'] = traceback.format_exc()
        self._log(LogLevel.CRITICAL, message, **extra)
    
    # ===== Metrics =====
    
    def record_request(self, success: bool, latency_ms: float, cache_hit: bool = False, tokens: int = 0):
        """Record request metrics"""
        with self._metrics_lock:
            self._metrics['requests_total'] += 1
            if success:
                self._metrics['requests_success'] += 1
            else:
                self._metrics['requests_failed'] += 1
            self._metrics['latency_sum_ms'] += latency_ms
            if cache_hit:
                self._metrics['cache_hits'] += 1
            else:
                self._metrics['cache_misses'] += 1
            self._metrics['tokens_used'] += tokens
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        with self._metrics_lock:
            metrics = dict(self._metrics)
            total = metrics['requests_total']
            if total > 0:
                metrics['success_rate'] = metrics['requests_success'] / total
                metrics['avg_latency_ms'] = metrics['latency_sum_ms'] / total
                cache_total = metrics['cache_hits'] + metrics['cache_misses']
                if cache_total > 0:
                    metrics['cache_hit_rate'] = metrics['cache_hits'] / cache_total
            return metrics
    
    def reset_metrics(self):
        """Reset metrics counters"""
        with self._metrics_lock:
            for key in self._metrics:
                self._metrics[key] = 0 if isinstance(self._metrics[key], int) else 0.0


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON"""
        if isinstance(record.msg, dict):
            log_data = dict(record.msg)
            # Rename log_message back to message for JSON output
            if 'log_message' in log_data:
                log_data['message'] = log_data.pop('log_message')
            if 'log_module' in log_data:
                log_data['module'] = log_data.pop('log_module')
        else:
            log_data = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'level': record.levelname.lower(),
                'message': record.getMessage()
            }
        
        return json.dumps(log_data, default=str)


# ===== Decorators =====

def log_operation(operation_name: str = None):
    """
    Decorator to log function execution with timing.
    
    Usage:
        @log_operation("search_documents")
        def search_documents(query):
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            op_name = operation_name or func.__name__
            
            with logger.context(operation=op_name):
                start_time = time.time()
                
                logger.info(f"Starting {op_name}")
                
                try:
                    result = func(*args, **kwargs)
                    latency_ms = (time.time() - start_time) * 1000
                    
                    logger.info(
                        f"Completed {op_name}",
                        latency_ms=latency_ms,
                        success=True
                    )
                    logger.record_request(True, latency_ms)
                    
                    return result
                    
                except Exception as e:
                    latency_ms = (time.time() - start_time) * 1000
                    
                    logger.error(
                        f"Failed {op_name}: {str(e)}",
                        latency_ms=latency_ms,
                        error_type=type(e).__name__,
                        success=False
                    )
                    logger.record_request(False, latency_ms)
                    
                    raise
        
        return wrapper
    return decorator


def log_async_operation(operation_name: str = None):
    """
    Decorator to log async function execution with timing.
    
    Usage:
        @log_async_operation("async_search")
        async def search_documents(query):
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger = get_logger()
            op_name = operation_name or func.__name__
            
            with logger.context(operation=op_name):
                start_time = time.time()
                
                logger.info(f"Starting {op_name}")
                
                try:
                    result = await func(*args, **kwargs)
                    latency_ms = (time.time() - start_time) * 1000
                    
                    logger.info(
                        f"Completed {op_name}",
                        latency_ms=latency_ms,
                        success=True
                    )
                    logger.record_request(True, latency_ms)
                    
                    return result
                    
                except Exception as e:
                    latency_ms = (time.time() - start_time) * 1000
                    
                    logger.error(
                        f"Failed {op_name}: {str(e)}",
                        latency_ms=latency_ms,
                        error_type=type(e).__name__,
                        success=False
                    )
                    logger.record_request(False, latency_ms)
                    
                    raise
        
        return wrapper
    return decorator


@contextmanager
def timed_operation(operation_name: str):
    """
    Context manager for timing operations.
    
    Usage:
        with timed_operation("database_query") as timer:
            result = db.query(...)
        print(f"Query took {timer.elapsed_ms}ms")
    """
    class Timer:
        def __init__(self):
            self.start_time = time.time()
            self.end_time = None
            self.elapsed_ms = 0.0
    
    timer = Timer()
    logger = get_logger()
    
    logger.debug(f"Starting timed operation: {operation_name}")
    
    try:
        yield timer
    finally:
        timer.end_time = time.time()
        timer.elapsed_ms = (timer.end_time - timer.start_time) * 1000
        logger.debug(
            f"Completed timed operation: {operation_name}",
            latency_ms=timer.elapsed_ms
        )


# ===== Request ID Middleware Helper =====

def generate_request_id() -> str:
    """Generate a unique request ID"""
    return str(uuid.uuid4())[:16]


# ===== Singleton Access =====

_logger_instance: Optional[StructuredLogger] = None


def get_logger() -> StructuredLogger:
    """Get the singleton logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = StructuredLogger()
    return _logger_instance


def init_logger(**config):
    """Initialize the logger with custom configuration"""
    for key, value in config.items():
        os.environ[key.upper()] = str(value)
    
    global _logger_instance
    _logger_instance = None
    return get_logger()


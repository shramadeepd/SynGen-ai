"""
Logging configuration and utilities for the SynGen AI application.
Provides structured logging with context information and error tracking.
"""
import logging
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import os
from functools import wraps
import traceback

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
        # In production, add file handler: logging.FileHandler("app.log")
    ]
)

# Create logger
logger = logging.getLogger("syngen-ai")

# Set level based on environment
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logger.setLevel(getattr(logging, LOG_LEVEL))

class LogContext:
    """Context manager for request-scoped logging with consistent request_id"""
    def __init__(self, context: Dict[str, Any] = None):
        self.context = context or {}
        self.request_id = self.context.get("request_id", str(uuid.uuid4()))
        self.start_time = time.time()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.log_exception(exc_val)
        duration_ms = round((time.time() - self.start_time) * 1000)
        self.log_info(f"Request completed in {duration_ms}ms", {"duration_ms": duration_ms})
    
    def log_info(self, message: str, extra: Dict[str, Any] = None):
        """Log an INFO level message with context"""
        extra_data = {**self.context, **(extra or {}), "request_id": self.request_id}
        logger.info(message, extra={"data": extra_data})
        
    def log_error(self, message: str, extra: Dict[str, Any] = None):
        """Log an ERROR level message with context"""
        extra_data = {**self.context, **(extra or {}), "request_id": self.request_id}
        logger.error(message, extra={"data": extra_data})
        
    def log_warning(self, message: str, extra: Dict[str, Any] = None):
        """Log a WARNING level message with context"""
        extra_data = {**self.context, **(extra or {}), "request_id": self.request_id}
        logger.warning(message, extra={"data": extra_data})
        
    def log_debug(self, message: str, extra: Dict[str, Any] = None):
        """Log a DEBUG level message with context"""
        extra_data = {**self.context, **(extra or {}), "request_id": self.request_id}
        logger.debug(message, extra={"data": extra_data})
        
    def log_exception(self, exception: Exception, extra: Dict[str, Any] = None):
        """Log an exception with traceback and context"""
        extra_data = {
            **self.context, 
            **(extra or {}), 
            "request_id": self.request_id,
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "traceback": traceback.format_exc()
        }
        logger.error(f"Exception: {str(exception)}", extra={"data": extra_data})

def log_execution_time(func):
    """Decorator to log function execution time"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Started {func.__name__}", extra={
                "data": {
                    "request_id": request_id,
                    "function": func.__name__,
                    "timestamp": datetime.now().isoformat()
                }
            })
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", extra={
                "data": {
                    "request_id": request_id,
                    "function": func.__name__,
                    "exception": str(e),
                    "traceback": traceback.format_exc()
                }
            })
            raise
        finally:
            duration_ms = round((time.time() - start_time) * 1000)
            logger.info(f"Completed {func.__name__}", extra={
                "data": {
                    "request_id": request_id,
                    "function": func.__name__,
                    "duration_ms": duration_ms,
                    "timestamp": datetime.now().isoformat()
                }
            })
    
    return wrapper

class QueryLogger:
    """Class for logging SQL queries and their metrics"""
    def __init__(self):
        self.logger = logger
    
    def log_query(self, 
                  query: str, 
                  duration_ms: float, 
                  rows_returned: int, 
                  user_id: Optional[str] = None,
                  question: Optional[str] = None):
        """Log SQL query execution details"""
        log_data = {
            "query": query,
            "duration_ms": duration_ms,
            "rows_returned": rows_returned,
            "timestamp": datetime.now().isoformat(),
            "request_id": str(uuid.uuid4())
        }
        
        if user_id:
            log_data["user_id"] = user_id
        
        if question:
            log_data["question"] = question
            
        self.logger.info(f"SQL query executed in {duration_ms}ms, returned {rows_returned} rows", 
                         extra={"data": log_data})
        
        # In production, you might want to store this in a database table
        # for analytics and performance monitoring
        
    def log_error(self, query: str, error: str, user_id: Optional[str] = None):
        """Log SQL query execution errors"""
        log_data = {
            "query": query,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "request_id": str(uuid.uuid4())
        }
        
        if user_id:
            log_data["user_id"] = user_id
            
        self.logger.error(f"SQL query error: {error}", extra={"data": log_data})

# Create singleton instances
query_logger = QueryLogger()
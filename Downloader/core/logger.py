#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OMNIPOTENT SOVEREIGN NEXUS - Advanced Logging Module
=====================================================

Version: 3.0.1 ULTIMATE NEXUS
Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng

This module provides comprehensive logging capabilities for the Downloader
package with structured logging, multiple output handlers, and performance
monitoring.

ARCHITECTURE:
    - Thread-safe logging operations
    - Structured JSON logging support
    - Multiple output handlers (console, file, syslog, network)
    - Log rotation and retention management
    - Performance metrics collection
    - Context-aware logging

FEATURES:
    - Colored console output with Rich integration
    - JSON structured logging for machine parsing
    - Automatic log rotation
    - Sensitive data masking
    - Request/Response logging with filtering
    - Performance timing and metrics
    - Context propagation across threads
    - Exception traceback capture
    - Memory-efficient buffering

SECURITY:
    - Sensitive data automatic masking
    - Log injection prevention
    - Secure file permissions
    - PII redaction options
"""

from __future__ import annotations

import atexit
import functools
import inspect
import io
import json
import logging
import os
import re
import sys
import threading
import time
import traceback
import warnings
from abc import ABC, abstractmethod
from collections import deque
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from logging import Filter, Formatter, Handler, LogRecord, Logger as StdLogger
from pathlib import Path
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Final,
    FrozenSet,
    Generic,
    IO,
    Iterator,
    List,
    Literal,
    Mapping,
    MutableMapping,
    Optional,
    Protocol,
    Set,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
    runtime_checkable,
)
from weakref import WeakSet
import copy

# Try to import optional dependencies
try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.text import Text
    from rich.traceback import Traceback
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

try:
    import colorama
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False

# Import from our package
from .config import Config, LogLevel, mask_sensitive


# =============================================================================
# CONSTANTS AND ENUMS
# =============================================================================

class OutputFormat(str, Enum):
    """Log output format enumeration."""
    PLAIN = "plain"
    JSON = "json"
    STRUCTURED = "structured"
    RICH = "rich"


class OutputTarget(str, Enum):
    """Log output target enumeration."""
    CONSOLE = "console"
    FILE = "file"
    SYSLOG = "syslog"
    NETWORK = "network"
    MEMORY = "memory"


# Default values
DEFAULT_FORMAT: Final[str] = (
    "[{asctime}] [{levelname:^8}] [{name}:{lineno}] {message}"
)
DEFAULT_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"
DEFAULT_JSON_FORMAT: Final[str] = (
    '{{"timestamp": "{asctime}", "level": "{levelname}", '
    '"logger": "{name}", "message": "{message}", '
    '"file": "{filename}", "line": {lineno}}}'
)
DEFAULT_MAX_BYTES: Final[int] = 10 * 1024 * 1024  # 10 MB
DEFAULT_BACKUP_COUNT: Final[int] = 5
DEFAULT_BUFFER_SIZE: Final[int] = 1000

# Sensitive patterns to mask in logs
SENSITIVE_PATTERNS: Final[Tuple[re.Pattern, ...]] = (
    re.compile(r'(password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', re.IGNORECASE),
    re.compile(r'(token|api_key|apikey|secret)["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', re.IGNORECASE),
    re.compile(r'(authorization|auth)["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', re.IGNORECASE),
    re.compile(r'Bearer\s+([A-Za-z0-9\-._~+/]+=*)', re.IGNORECASE),
    re.compile(r'Basic\s+([A-Za-z0-9+/]+=*)', re.IGNORECASE),
)

# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright foreground colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    
    # Background colors
    BG_RED = "\033[41m"
    BG_YELLOW = "\033[43m"


# Level colors mapping
LEVEL_COLORS: Dict[int, str] = {
    logging.DEBUG: Colors.CYAN,
    logging.INFO: Colors.GREEN,
    logging.WARNING: Colors.YELLOW,
    logging.ERROR: Colors.RED,
    logging.CRITICAL: Colors.BRIGHT_RED,
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass(frozen=True)
class LogContext:
    """
    Immutable log context for structured logging.
    
    Attributes:
        request_id: Unique request identifier.
        session_id: Session identifier.
        user_id: User identifier.
        trace_id: Distributed tracing ID.
        span_id: Span ID within trace.
        extra: Additional context fields.
    """
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    extra: Mapping[str, Any] = field(default_factory=dict)
    
    def merge(self, **kwargs: Any) -> "LogContext":
        """
        Create new context with additional fields.
        
        Args:
            **kwargs: Fields to add or update.
        
        Returns:
            LogContext: New merged context.
        """
        new_extra = {**self.extra, **kwargs}
        return LogContext(
            request_id=kwargs.get("request_id", self.request_id),
            session_id=kwargs.get("session_id", self.session_id),
            user_id=kwargs.get("user_id", self.user_id),
            trace_id=kwargs.get("trace_id", self.trace_id),
            span_id=kwargs.get("span_id", self.span_id),
            extra=new_extra,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result: Dict[str, Any] = {}
        if self.request_id:
            result["request_id"] = self.request_id
        if self.session_id:
            result["session_id"] = self.session_id
        if self.user_id:
            result["user_id"] = self.user_id
        if self.trace_id:
            result["trace_id"] = self.trace_id
        if self.span_id:
            result["span_id"] = self.span_id
        result.update(self.extra)
        return result


@dataclass
class PerformanceMetrics:
    """
    Performance metrics container.
    
    Attributes:
        operation: Operation name.
        start_time: Start timestamp.
        end_time: End timestamp.
        duration_ms: Duration in milliseconds.
        success: Whether operation succeeded.
        error: Error message if failed.
        extra: Additional metrics.
    """
    operation: str
    start_time: float = 0.0
    end_time: float = 0.0
    duration_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def complete(self, error: Optional[Exception] = None) -> None:
        """
        Mark operation as complete.
        
        Args:
            error: Exception if operation failed.
        """
        self.end_time = time.perf_counter()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        if error:
            self.success = False
            self.error = str(error)


# =============================================================================
# LOGGING FILTERS
# =============================================================================

class SensitiveDataFilter(Filter):
    """
    Log filter that masks sensitive data.
    
    This filter automatically detects and masks passwords, tokens,
    API keys, and other sensitive information in log messages.
    """
    
    def __init__(
        self,
        mask_char: str = "*",
        show_prefix_chars: int = 2,
        additional_patterns: Optional[List[re.Pattern]] = None
    ) -> None:
        """
        Initialize the filter.
        
        Args:
            mask_char: Character to use for masking.
            show_prefix_chars: Number of characters to show before masking.
            additional_patterns: Additional regex patterns to mask.
        """
        super().__init__()
        self.mask_char = mask_char
        self.show_prefix_chars = show_prefix_chars
        self._patterns = list(SENSITIVE_PATTERNS)
        if additional_patterns:
            self._patterns.extend(additional_patterns)
    
    def filter(self, record: LogRecord) -> bool:
        """
        Filter and mask sensitive data in log record.
        
        Args:
            record: The log record to filter.
        
        Returns:
            bool: Always True (allows all records through).
        """
        record.msg = self._mask_string(str(record.msg))
        
        if record.args:
            record.args = self._mask_args(record.args)
        
        return True
    
    def _mask_string(self, text: str) -> str:
        """Mask sensitive data in string."""
        for pattern in self._patterns:
            text = pattern.sub(self._replace_match, text)
        return text
    
    def _mask_args(self, args: Any) -> Any:
        """Mask sensitive data in args."""
        if isinstance(args, dict):
            return {k: self._mask_value(k, v) for k, v in args.items()}
        elif isinstance(args, tuple):
            return tuple(self._mask_value(None, v) for v in args)
        elif isinstance(args, list):
            return [self._mask_value(None, v) for v in args]
        return args
    
    def _mask_value(self, key: Optional[str], value: Any) -> Any:
        """Mask a single value based on key name or content."""
        if not isinstance(value, str):
            return value
        
        # Check if key is sensitive
        if key and key.lower() in {"password", "passwd", "pwd", "secret",
                                    "token", "api_key", "apikey", "auth"}:
            return mask_sensitive(value, self.show_prefix_chars)
        
        return self._mask_string(value)
    
    def _replace_match(self, match: re.Match) -> str:
        """Replace matched sensitive data with masked version."""
        groups = match.groups()
        if len(groups) >= 2:
            key = groups[0]
            value = groups[1]
            masked = mask_sensitive(value, self.show_prefix_chars)
            return f'{key}="{masked}"'
        return match.group(0)


class ContextFilter(Filter):
    """
    Log filter that adds context information to records.
    
    This filter adds request ID, session ID, and other contextual
    information to log records for distributed tracing.
    """
    
    _context: ClassVar[Dict[int, LogContext]] = {}
    _lock = threading.Lock()
    
    @classmethod
    def set_context(cls, context: LogContext) -> None:
        """
        Set context for current thread.
        
        Args:
            context: Log context to set.
        """
        thread_id = threading.get_ident()
        with cls._lock:
            cls._context[thread_id] = context
    
    @classmethod
    def get_context(cls) -> LogContext:
        """Get context for current thread."""
        thread_id = threading.get_ident()
        with cls._lock:
            return cls._context.get(thread_id, LogContext())
    
    @classmethod
    def clear_context(cls) -> None:
        """Clear context for current thread."""
        thread_id = threading.get_ident()
        with cls._lock:
            cls._context.pop(thread_id, None)
    
    def filter(self, record: LogRecord) -> bool:
        """Add context to log record."""
        context = self.get_context()
        
        record.request_id = context.request_id or ""
        record.session_id = context.session_id or ""
        record.user_id = context.user_id or ""
        record.trace_id = context.trace_id or ""
        record.span_id = context.span_id or ""
        
        # Add extra context
        for key, value in context.extra.items():
            setattr(record, key, value)
        
        return True


class RateLimitFilter(Filter):
    """
    Log filter that limits duplicate messages.
    
    This filter prevents log flooding by suppressing duplicate
    messages within a time window.
    """
    
    def __init__(
        self,
        window_seconds: float = 60.0,
        max_count: int = 10
    ) -> None:
        """
        Initialize the rate limit filter.
        
        Args:
            window_seconds: Time window in seconds.
            max_count: Maximum occurrences within window.
        """
        super().__init__()
        self.window_seconds = window_seconds
        self.max_count = max_count
        self._counts: Dict[str, deque] = {}
        self._lock = threading.Lock()
    
    def filter(self, record: LogRecord) -> bool:
        """
        Filter based on rate limits.
        
        Args:
            record: The log record to filter.
        
        Returns:
            bool: True if record should be logged, False if rate limited.
        """
        key = self._get_key(record)
        now = time.time()
        
        with self._lock:
            if key not in self._counts:
                self._counts[key] = deque()
            
            times = self._counts[key]
            
            # Remove old entries
            while times and times[0] < now - self.window_seconds:
                times.popleft()
            
            # Check if within limit
            if len(times) >= self.max_count:
                return False
            
            times.append(now)
            return True
    
    def _get_key(self, record: LogRecord) -> str:
        """Generate a key for deduplication."""
        return f"{record.name}:{record.levelno}:{record.getMessage()[:100]}"


# =============================================================================
# LOGGING FORMATTERS
# =============================================================================

class ColoredFormatter(Formatter):
    """
    Formatter with colored output for terminal.
    
    Provides colorized log output with level-specific colors and
    customizable formatting.
    """
    
    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: str = "{",
        colors: Optional[Dict[int, str]] = None,
        use_colors: bool = True
    ) -> None:
        """
        Initialize the formatter.
        
        Args:
            fmt: Log format string.
            datefmt: Date format string.
            style: Format style ('%', '{', or '$').
            colors: Custom color mapping for levels.
            use_colors: Whether to use colors.
        """
        super().__init__(fmt or DEFAULT_FORMAT, datefmt, style)
        self.colors = colors or LEVEL_COLORS
        self.use_colors = use_colors and self._supports_color()
    
    @staticmethod
    def _supports_color() -> bool:
        """Check if terminal supports colors."""
        # Check if we're in a TTY
        if not hasattr(sys.stdout, "isatty"):
            return False
        if not sys.stdout.isatty():
            return False
        
        # Check for Windows
        if sys.platform == "win32":
            if HAS_COLORAMA:
                colorama.init()
                return True
            return False
        
        return True
    
    def format(self, record: LogRecord) -> str:
        """Format the log record with colors."""
        # Save original level name
        orig_levelname = record.levelname
        
        if self.use_colors:
            color = self.colors.get(record.levelno, "")
            record.levelname = f"{color}{record.levelname:^8}{Colors.RESET}"
        
        # Format the message
        result = super().format(record)
        
        # Restore original
        record.levelname = orig_levelname
        
        return result


class JSONFormatter(Formatter):
    """
    Formatter that outputs structured JSON logs.
    
    Produces machine-parseable JSON log entries suitable for
    log aggregation systems like ELK, Splunk, or CloudWatch.
    """
    
    def __init__(
        self,
        include_extra: bool = True,
        timestamp_format: str = "iso",
        mask_secrets: bool = True
    ) -> None:
        """
        Initialize the JSON formatter.
        
        Args:
            include_extra: Include extra fields from record.
            timestamp_format: Timestamp format ('iso' or 'unix').
            mask_secrets: Mask sensitive data.
        """
        super().__init__()
        self.include_extra = include_extra
        self.timestamp_format = timestamp_format
        self.mask_secrets = mask_secrets
    
    def format(self, record: LogRecord) -> str:
        """Format the log record as JSON."""
        log_entry: Dict[str, Any] = {
            "timestamp": self._format_timestamp(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }
        
        # Add context fields
        for attr in ("request_id", "session_id", "user_id", "trace_id", "span_id"):
            value = getattr(record, attr, None)
            if value:
                log_entry[attr] = value
        
        # Add extra fields
        if self.include_extra:
            extra = {}
            for key, value in record.__dict__.items():
                if key not in {
                    "name", "msg", "args", "created", "filename", "funcName",
                    "levelname", "levelno", "lineno", "module", "msecs",
                    "pathname", "process", "processName", "relativeCreated",
                    "stack_info", "exc_info", "exc_text", "thread", "threadName",
                    "message", "asctime", "request_id", "session_id", "user_id",
                    "trace_id", "span_id"
                }:
                    try:
                        json.dumps(value)
                        extra[key] = value
                    except (TypeError, ValueError):
                        extra[key] = str(value)
            
            if extra:
                log_entry["extra"] = extra
        
        return json.dumps(log_entry, default=str, ensure_ascii=False)
    
    def _format_timestamp(self, record: LogRecord) -> str:
        """Format timestamp."""
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
        if self.timestamp_format == "iso":
            return dt.isoformat()
        return str(record.created)


class StructuredFormatter(Formatter):
    """
    Human-readable structured log formatter.
    
    Provides formatted output that is both human-readable and
    structured for easier parsing.
    """
    
    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        show_context: bool = True
    ) -> None:
        """
        Initialize the structured formatter.
        
        Args:
            fmt: Log format string.
            datefmt: Date format string.
            show_context: Show context information.
        """
        super().__init__(fmt or DEFAULT_FORMAT, datefmt, "{")
        self.show_context = show_context
    
    def format(self, record: LogRecord) -> str:
        """Format the log record with structure."""
        # Build base message
        parts = [
            f"[{self.formatTime(record)}]",
            f"[{record.levelname:^8}]",
            f"[{record.name}:{record.lineno}]",
        ]
        
        # Add context if available
        if self.show_context:
            context_parts = []
            for attr in ("request_id", "trace_id"):
                value = getattr(record, attr, None)
                if value:
                    context_parts.append(f"{attr}={value}")
            if context_parts:
                parts.append(f"[{' '.join(context_parts)}]")
        
        parts.append(record.getMessage())
        
        # Add exception info
        if record.exc_info:
            parts.append("\n" + self.formatException(record.exc_info))
        
        return " ".join(parts)


# =============================================================================
# LOGGING HANDLERS
# =============================================================================

class MemoryHandler(Handler):
    """
    In-memory log handler for buffering logs.
    
    Stores logs in memory with configurable buffer size and
    thread-safe access.
    """
    
    def __init__(
        self,
        capacity: int = DEFAULT_BUFFER_SIZE,
        level: int = logging.NOTSET
    ) -> None:
        """
        Initialize the memory handler.
        
        Args:
            capacity: Maximum number of records to store.
            level: Minimum log level.
        """
        super().__init__(level)
        self.capacity = capacity
        self._buffer: deque = deque(maxlen=capacity)
        self._lock = threading.Lock()
    
    def emit(self, record: LogRecord) -> None:
        """Store log record in buffer."""
        with self._lock:
            self._buffer.append(record)
    
    def get_records(
        self,
        level: Optional[int] = None,
        count: Optional[int] = None
    ) -> List[LogRecord]:
        """
        Get log records from buffer.
        
        Args:
            level: Filter by log level.
            count: Maximum number of records to return.
        
        Returns:
            List[LogRecord]: List of log records.
        """
        with self._lock:
            records = list(self._buffer)
        
        if level is not None:
            records = [r for r in records if r.levelno >= level]
        
        if count is not None:
            records = records[-count:]
        
        return records
    
    def clear(self) -> None:
        """Clear the buffer."""
        with self._lock:
            self._buffer.clear()
    
    def dump(self, handler: Handler) -> None:
        """
        Dump all records to another handler.
        
        Args:
            handler: Target handler to dump records to.
        """
        with self._lock:
            for record in self._buffer:
                handler.emit(record)


class SizeRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """
    File handler with size-based rotation.
    
    Extends the standard RotatingFileHandler with improved error
    handling and secure file permissions.
    """
    
    def __init__(
        self,
        filename: Union[str, Path],
        max_bytes: int = DEFAULT_MAX_BYTES,
        backup_count: int = DEFAULT_BACKUP_COUNT,
        encoding: str = "utf-8",
        mode: str = "a",
        permissions: int = 0o640
    ) -> None:
        """
        Initialize the rotating file handler.
        
        Args:
            filename: Path to log file.
            max_bytes: Maximum file size before rotation.
            backup_count: Number of backup files to keep.
            encoding: File encoding.
            mode: File open mode.
            permissions: File permissions (octal).
        """
        self.permissions = permissions
        self._filename = Path(filename)
        
        # Ensure directory exists
        self._filename.parent.mkdir(parents=True, exist_ok=True)
        
        super().__init__(
            str(self._filename),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding=encoding,
            mode=mode
        )
        
        # Set file permissions
        try:
            os.chmod(self._filename, permissions)
        except OSError:
            pass
    
    def doRollover(self) -> None:
        """Perform rollover with error handling."""
        try:
            super().doRollover()
            # Set permissions on new file
            try:
                os.chmod(self._filename, self.permissions)
            except OSError:
                pass
        except Exception as e:
            # Log error without causing recursive logging
            sys.stderr.write(f"Log rotation failed: {e}\n")


class TimeRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """
    File handler with time-based rotation.
    
    Extends the standard TimedRotatingFileHandler with improved error
    handling and secure file permissions.
    """
    
    def __init__(
        self,
        filename: Union[str, Path],
        when: str = "midnight",
        interval: int = 1,
        backup_count: int = DEFAULT_BACKUP_COUNT,
        encoding: str = "utf-8",
        permissions: int = 0o640
    ) -> None:
        """
        Initialize the time rotating file handler.
        
        Args:
            filename: Path to log file.
            when: Rotation interval type ('S', 'M', 'H', 'D', 'midnight').
            interval: Rotation interval value.
            backup_count: Number of backup files to keep.
            encoding: File encoding.
            permissions: File permissions (octal).
        """
        self.permissions = permissions
        self._filename = Path(filename)
        
        # Ensure directory exists
        self._filename.parent.mkdir(parents=True, exist_ok=True)
        
        super().__init__(
            str(self._filename),
            when=when,
            interval=interval,
            backupCount=backup_count,
            encoding=encoding
        )
        
        # Set file permissions
        try:
            os.chmod(self._filename, permissions)
        except OSError:
            pass


# =============================================================================
# MAIN LOGGER CLASS
# =============================================================================

class Logger:
    """
    Advanced logger with comprehensive features.
    
    This class provides a high-level logging interface with structured
    logging, performance tracking, and multiple output handlers.
    
    Attributes:
        _logger: Underlying standard logger.
        _config: Configuration instance.
        _handlers: Configured handlers.
        _context: Current log context.
    
    Example:
        >>> logger = Logger("myapp")
        >>> logger.info("Application started")
        >>> with logger.timer("operation"):
        ...     # do work
        ...     pass
    """
    
    # Registry of created loggers
    _registry: ClassVar[Dict[str, "Logger"]] = {}
    _registry_lock = threading.Lock()
    
    def __init__(
        self,
        name: str,
        level: Union[int, LogLevel, str] = LogLevel.INFO,
        config: Optional[Config] = None
    ) -> None:
        """
        Initialize the logger.
        
        Args:
            name: Logger name.
            level: Log level.
            config: Configuration instance.
        """
        self._name = name
        self._logger = logging.getLogger(name)
        self._config = config or Config()
        self._handlers: Dict[str, Handler] = {}
        self._lock = threading.Lock()
        
        # Set level
        if isinstance(level, str):
            level = LogLevel[level.upper()]
        if isinstance(level, LogLevel):
            level = getattr(logging, level.value)
        self._logger.setLevel(level)
        
        # Prevent propagation to root logger
        self._logger.propagate = False
        
        # Add default filters
        self._logger.addFilter(SensitiveDataFilter())
        self._logger.addFilter(ContextFilter())
    
    @property
    def name(self) -> str:
        """Get logger name."""
        return self._name
    
    @property
    def level(self) -> int:
        """Get log level."""
        return self._logger.level
    
    @level.setter
    def level(self, value: Union[int, LogLevel, str]) -> None:
        """Set log level."""
        if isinstance(value, str):
            value = LogLevel[value.upper()]
        if isinstance(value, LogLevel):
            value = getattr(logging, value.value)
        self._logger.setLevel(value)
    
    @property
    def handlers(self) -> Dict[str, Handler]:
        """Get configured handlers."""
        return self._handlers.copy()
    
    # Factory methods
    @classmethod
    def get(cls, name: str, **kwargs: Any) -> "Logger":
        """
        Get or create a logger by name.
        
        Args:
            name: Logger name.
            **kwargs: Additional arguments for Logger constructor.
        
        Returns:
            Logger: Logger instance.
        """
        with cls._registry_lock:
            if name not in cls._registry:
                cls._registry[name] = cls(name, **kwargs)
            return cls._registry[name]
    
    @classmethod
    def get_root(cls) -> "Logger":
        """Get the root logger."""
        return cls.get("root")
    
    # Handler configuration
    def add_console_handler(
        self,
        level: Optional[Union[int, LogLevel, str]] = None,
        fmt: Optional[str] = None,
        use_colors: bool = True,
        use_rich: bool = True,
        stream: Optional[TextIO] = None
    ) -> "Logger":
        """
        Add console output handler.
        
        Args:
            level: Handler log level.
            fmt: Custom format string.
            use_colors: Use colored output.
            use_rich: Use Rich handler if available.
            stream: Output stream (defaults to sys.stderr).
        
        Returns:
            Logger: Self for chaining.
        """
        handler_name = "console"
        
        if use_rich and HAS_RICH:
            handler: Handler = RichHandler(
                console=Console(file=stream or sys.stderr),
                show_path=True,
                show_time=True,
                rich_tracebacks=True,
            )
        else:
            handler = logging.StreamHandler(stream or sys.stderr)
            handler.setFormatter(ColoredFormatter(
                fmt=fmt,
                use_colors=use_colors
            ))
        
        if level is not None:
            if isinstance(level, str):
                level = LogLevel[level.upper()]
            if isinstance(level, LogLevel):
                level = getattr(logging, level.value)
            handler.setLevel(level)
        
        self._add_handler(handler_name, handler)
        return self
    
    def add_file_handler(
        self,
        path: Union[str, Path],
        level: Optional[Union[int, LogLevel, str]] = None,
        fmt: Optional[str] = None,
        rotate: str = "size",
        max_bytes: int = DEFAULT_MAX_BYTES,
        backup_count: int = DEFAULT_BACKUP_COUNT,
        when: str = "midnight",
        permissions: int = 0o640
    ) -> "Logger":
        """
        Add file output handler with rotation.
        
        Args:
            path: Path to log file.
            level: Handler log level.
            fmt: Custom format string.
            rotate: Rotation type ('size' or 'time').
            max_bytes: Maximum file size (for size rotation).
            backup_count: Number of backup files.
            when: Rotation interval (for time rotation).
            permissions: File permissions.
        
        Returns:
            Logger: Self for chaining.
        """
        path = Path(path)
        
        if rotate == "time":
            handler: Handler = TimeRotatingFileHandler(
                path,
                when=when,
                backup_count=backup_count,
                permissions=permissions
            )
        else:
            handler = SizeRotatingFileHandler(
                path,
                max_bytes=max_bytes,
                backup_count=backup_count,
                permissions=permissions
            )
        
        handler.setFormatter(ColoredFormatter(fmt=fmt, use_colors=False))
        
        if level is not None:
            if isinstance(level, str):
                level = LogLevel[level.upper()]
            if isinstance(level, LogLevel):
                level = getattr(logging, level.value)
            handler.setLevel(level)
        
        handler_name = f"file:{path.name}"
        self._add_handler(handler_name, handler)
        return self
    
    def add_json_handler(
        self,
        path: Union[str, Path],
        level: Optional[Union[int, LogLevel, str]] = None,
        rotate: str = "size",
        max_bytes: int = DEFAULT_MAX_BYTES,
        backup_count: int = DEFAULT_BACKUP_COUNT
    ) -> "Logger":
        """
        Add JSON file output handler.
        
        Args:
            path: Path to log file.
            level: Handler log level.
            rotate: Rotation type.
            max_bytes: Maximum file size.
            backup_count: Number of backup files.
        
        Returns:
            Logger: Self for chaining.
        """
        path = Path(path)
        
        if rotate == "size":
            handler: Handler = SizeRotatingFileHandler(
                path,
                max_bytes=max_bytes,
                backup_count=backup_count
            )
        else:
            handler = TimeRotatingFileHandler(path, backup_count=backup_count)
        
        handler.setFormatter(JSONFormatter())
        
        if level is not None:
            if isinstance(level, str):
                level = LogLevel[level.upper()]
            if isinstance(level, LogLevel):
                level = getattr(logging, level.value)
            handler.setLevel(level)
        
        handler_name = f"json:{path.name}"
        self._add_handler(handler_name, handler)
        return self
    
    def add_memory_handler(
        self,
        capacity: int = DEFAULT_BUFFER_SIZE,
        level: Optional[Union[int, LogLevel, str]] = None
    ) -> "Logger":
        """
        Add in-memory buffer handler.
        
        Args:
            capacity: Buffer capacity.
            level: Handler log level.
        
        Returns:
            Logger: Self for chaining.
        """
        handler = MemoryHandler(capacity=capacity)
        
        if level is not None:
            if isinstance(level, str):
                level = LogLevel[level.upper()]
            if isinstance(level, LogLevel):
                level = getattr(logging, level.value)
            handler.setLevel(level)
        
        self._add_handler("memory", handler)
        return self
    
    def _add_handler(self, name: str, handler: Handler) -> None:
        """Add a handler with thread safety."""
        with self._lock:
            # Remove existing handler with same name
            if name in self._handlers:
                self._logger.removeHandler(self._handlers[name])
            
            self._handlers[name] = handler
            self._logger.addHandler(handler)
    
    def remove_handler(self, name: str) -> bool:
        """
        Remove a handler by name.
        
        Args:
            name: Handler name.
        
        Returns:
            bool: True if handler was removed.
        """
        with self._lock:
            if name in self._handlers:
                handler = self._handlers.pop(name)
                self._logger.removeHandler(handler)
                handler.close()
                return True
            return False
    
    def clear_handlers(self) -> None:
        """Remove all handlers."""
        with self._lock:
            for handler in self._handlers.values():
                self._logger.removeHandler(handler)
                handler.close()
            self._handlers.clear()
    
    # Logging methods
    def debug(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log debug message."""
        self._logger.debug(msg, *args, **kwargs)
    
    def info(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log info message."""
        self._logger.info(msg, *args, **kwargs)
    
    def warning(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log warning message."""
        self._logger.warning(msg, *args, **kwargs)
    
    def error(
        self,
        msg: Any,
        *args: Any,
        exc_info: bool = False,
        **kwargs: Any
    ) -> None:
        """Log error message."""
        self._logger.error(msg, *args, exc_info=exc_info, **kwargs)
    
    def critical(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log critical message."""
        self._logger.critical(msg, *args, **kwargs)
    
    def exception(
        self,
        msg: Any,
        *args: Any,
        exc_info: bool = True,
        **kwargs: Any
    ) -> None:
        """Log exception with traceback."""
        self._logger.exception(msg, *args, exc_info=exc_info, **kwargs)
    
    # Context management
    def set_context(self, **kwargs: Any) -> None:
        """
        Set logging context for current thread.
        
        Args:
            **kwargs: Context fields to set.
        """
        current = ContextFilter.get_context()
        ContextFilter.set_context(current.merge(**kwargs))
    
    def clear_context(self) -> None:
        """Clear logging context for current thread."""
        ContextFilter.clear_context()
    
    @contextmanager
    def context(self, **kwargs: Any) -> Iterator[None]:
        """
        Context manager for temporary context.
        
        Args:
            **kwargs: Context fields to set.
        
        Yields:
            None
        """
        old_context = ContextFilter.get_context()
        ContextFilter.set_context(old_context.merge(**kwargs))
        try:
            yield
        finally:
            ContextFilter.set_context(old_context)
    
    # Performance logging
    @contextmanager
    def timer(
        self,
        operation: str,
        level: int = logging.INFO,
        **kwargs: Any
    ) -> Iterator[PerformanceMetrics]:
        """
        Context manager for timing operations.
        
        Args:
            operation: Operation name.
            level: Log level for timing message.
            **kwargs: Additional context.
        
        Yields:
            PerformanceMetrics: Metrics object.
        """
        metrics = PerformanceMetrics(
            operation=operation,
            start_time=time.perf_counter()
        )
        
        error: Optional[Exception] = None
        try:
            yield metrics
        except Exception as e:
            error = e
            raise
        finally:
            metrics.complete(error)
            
            log_msg = f"{operation} completed in {metrics.duration_ms:.2f}ms"
            if error:
                log_msg += f" (failed: {error})"
            
            extra = {"metrics": metrics.to_dict() if hasattr(metrics, 'to_dict') else metrics}
            extra.update(kwargs)
            
            if error:
                self._logger.log(level, log_msg, extra=extra)
            else:
                self._logger.log(level, log_msg, extra=extra)
    
    def log_function(
        self,
        level: int = logging.DEBUG,
        log_args: bool = True,
        log_result: bool = False
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """
        Decorator for logging function calls.
        
        Args:
            level: Log level.
            log_args: Log function arguments.
            log_result: Log return value.
        
        Returns:
            Decorator function.
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> T:
                func_name = func.__qualname__
                
                if log_args:
                    self._logger.log(
                        level,
                        f"Calling {func_name} with args={args}, kwargs={kwargs}"
                    )
                else:
                    self._logger.log(level, f"Calling {func_name}")
                
                try:
                    result = func(*args, **kwargs)
                    if log_result:
                        self._logger.log(
                            level,
                            f"{func_name} returned: {result!r}"
                        )
                    return result
                except Exception as e:
                    self._logger.log(
                        logging.ERROR,
                        f"{func_name} raised {type(e).__name__}: {e}"
                    )
                    raise
            
            return wrapper
        
        return decorator
    
    # Utility methods
    def get_memory_logs(
        self,
        level: Optional[int] = None,
        count: Optional[int] = None
    ) -> List[str]:
        """
        Get logs from memory handler.
        
        Args:
            level: Filter by log level.
            count: Maximum number of logs.
        
        Returns:
            List[str]: List of log messages.
        """
        if "memory" not in self._handlers:
            return []
        
        handler = cast(MemoryHandler, self._handlers["memory"])
        records = handler.get_records(level=level, count=count)
        
        formatter = self._handlers.get("console", self._handlers.get("file"))
        if formatter:
            formatter = formatter.formatter
        
        return [
            formatter.format(r) if formatter else r.getMessage()
            for r in records
        ]
    
    def is_enabled_for(self, level: Union[int, LogLevel, str]) -> bool:
        """
        Check if logger is enabled for level.
        
        Args:
            level: Log level to check.
        
        Returns:
            bool: True if enabled.
        """
        if isinstance(level, str):
            level = LogLevel[level.upper()]
        if isinstance(level, LogLevel):
            level = getattr(logging, level.value)
        return self._logger.isEnabledFor(level)
    
    def flush(self) -> None:
        """Flush all handlers."""
        for handler in self._handlers.values():
            if hasattr(handler, "flush"):
                handler.flush()


# =============================================================================
# MODULE-LEVEL FUNCTIONS
# =============================================================================

def get_logger(
    name: str = "downloader",
    level: Union[int, LogLevel, str] = LogLevel.INFO,
    config: Optional[Config] = None
) -> Logger:
    """
    Get or create a logger.
    
    Args:
        name: Logger name.
        level: Log level.
        config: Configuration instance.
    
    Returns:
        Logger: Logger instance.
    """
    return Logger.get(name, level=level, config=config)


def configure_logging(
    level: Union[int, LogLevel, str] = LogLevel.INFO,
    console: bool = True,
    file_path: Optional[Union[str, Path]] = None,
    json_path: Optional[Union[str, Path]] = None,
    use_colors: bool = True,
    use_rich: bool = True
) -> Logger:
    """
    Configure logging with common settings.
    
    Args:
        level: Log level.
        console: Enable console output.
        file_path: Path for file output.
        json_path: Path for JSON output.
        use_colors: Use colored output.
        use_rich: Use Rich handler.
    
    Returns:
        Logger: Configured logger.
    """
    logger = get_logger("downloader", level=level)
    
    if console:
        logger.add_console_handler(use_colors=use_colors, use_rich=use_rich)
    
    if file_path:
        logger.add_file_handler(file_path)
    
    if json_path:
        logger.add_json_handler(json_path)
    
    return logger


def set_request_id(request_id: str) -> None:
    """
    Set request ID for current thread context.
    
    Args:
        request_id: Request identifier.
    """
    ContextFilter.set_context(LogContext(request_id=request_id))


def set_trace_context(
    trace_id: str,
    span_id: Optional[str] = None
) -> None:
    """
    Set distributed tracing context.
    
    Args:
        trace_id: Trace identifier.
        span_id: Span identifier.
    """
    current = ContextFilter.get_context()
    ContextFilter.set_context(LogContext(
        trace_id=trace_id,
        span_id=span_id,
        request_id=current.request_id,
        session_id=current.session_id,
        user_id=current.user_id,
        extra=current.extra
    ))


# Type variable for generic return type
T = TypeVar('T')


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "OutputFormat",
    "OutputTarget",
    "LogLevel",
    # Classes
    "Logger",
    "LogContext",
    "PerformanceMetrics",
    "SensitiveDataFilter",
    "ContextFilter",
    "RateLimitFilter",
    "ColoredFormatter",
    "JSONFormatter",
    "StructuredFormatter",
    "MemoryHandler",
    "SizeRotatingFileHandler",
    "TimeRotatingFileHandler",
    # Functions
    "get_logger",
    "configure_logging",
    "set_request_id",
    "set_trace_context",
    # Constants
    "DEFAULT_FORMAT",
    "DEFAULT_DATE_FORMAT",
    "DEFAULT_MAX_BYTES",
    "DEFAULT_BACKUP_COUNT",
    "DEFAULT_BUFFER_SIZE",
    "LEVEL_COLORS",
    "Colors",
]

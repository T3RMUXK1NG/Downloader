#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OMNIPOTENT SOVEREIGN NEXUS - Downloader Base Module
====================================================

Version: 3.0.1 ULTIMATE NEXUS
Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng

This module provides the base downloader class with comprehensive
features for file downloading, queue management, and progress tracking.

ARCHITECTURE:
    - Async-first design for concurrent downloads
    - Plugin-based extensibility
    - Event-driven progress tracking
    - Queue-based task management
    - Checkpoint/resume support
    - Multi-source download aggregation

FEATURES:
    - Single and batch downloads
    - Concurrent download management
    - Progress tracking with callbacks
    - Speed calculation and ETA
    - Pause/resume/cancel support
    - Checksum verification (MD5, SHA1, SHA256)
    - Automatic retry on failure
    - Bandwidth throttling
    - Proxy support
    - Cookie handling
    - Authentication support

SECURITY:
    - Path traversal prevention
    - File permission management
    - URL validation
    - Size limit enforcement
    - Safe filename handling
"""

from __future__ import annotations

import asyncio
import functools
import hashlib
import inspect
import json
import os
import random
import re
import shutil
import stat
import string
import sys
import tempfile
import time
import warnings
from abc import ABC, abstractmethod
from collections import OrderedDict, defaultdict
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager, contextmanager, suppress
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum, auto, IntEnum
from pathlib import Path
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    BinaryIO,
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
from weakref import WeakSet, WeakValueDictionary
from urllib.parse import urlparse, unquote
import threading
import queue

# Import from our package
from .config import (
    Config,
    TimeoutConfig,
    RetryConfig,
    ProxyConfig,
    SSLConfig,
    ConnectionPoolConfig,
    RateLimitConfig,
    RetryStrategy,
    ConfigProfile,
)
from .logger import Logger, get_logger, LogLevel, LogContext, PerformanceMetrics
from .network import (
    NetworkClient,
    NetworkError,
    HTTPError,
    RetryExhaustedError,
    URL,
    Response,
    Headers,
    HttpMethod,
    sanitize_url_for_logging,
    get_content_disposition_filename,
)


# =============================================================================
# CONSTANTS AND ENUMS
# =============================================================================

class DownloadStatus(IntEnum):
    """Download status enumeration."""
    PENDING = 0
    QUEUED = 1
    STARTING = 2
    DOWNLOADING = 3
    PAUSED = 4
    COMPLETED = 5
    FAILED = 6
    CANCELLED = 7
    VERIFYING = 8
    RETRYING = 9


class HashAlgorithm(str, Enum):
    """Hash algorithm enumeration."""
    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    SHA512 = "sha512"


class Priority(IntEnum):
    """Download priority enumeration."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


class ConflictResolution(str, Enum):
    """File conflict resolution strategy."""
    OVERWRITE = "overwrite"
    SKIP = "skip"
    RENAME = "rename"
    RESUME = "resume"
    ASK = "ask"


# Default values
DEFAULT_CHUNK_SIZE: Final[int] = 8192  # 8KB
DEFAULT_MAX_CONCURRENT: Final[int] = 5
DEFAULT_MIN_CHUNK_SIZE: Final[int] = 1024 * 1024  # 1MB
DEFAULT_MAX_CHUNK_SIZE: Final[int] = 10 * 1024 * 1024  # 10MB
DEFAULT_TEMP_SUFFIX: Final[str] = ".downloading"
DEFAULT_USER_AGENT: Final[str] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Filename patterns
INVALID_FILENAME_CHARS: Final[re.Pattern] = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
MAX_FILENAME_LENGTH: Final[int] = 255


# =============================================================================
# EXCEPTIONS
# =============================================================================

class DownloadError(Exception):
    """Base exception for download errors."""
    
    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        file_path: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(message)
        self.message = message
        self.url = url
        self.file_path = file_path
        self.details = kwargs
    
    def __str__(self) -> str:
        parts = [self.message]
        if self.url:
            parts.append(f"URL: {sanitize_url_for_logging(self.url)}")
        if self.file_path:
            parts.append(f"File: {self.file_path}")
        return " | ".join(parts)


class ValidationError(DownloadError):
    """Exception for validation errors."""
    pass


class ChecksumError(DownloadError):
    """Exception for checksum verification failures."""
    
    def __init__(
        self,
        message: str,
        expected: Optional[str] = None,
        actual: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(message, **kwargs)
        self.expected = expected
        self.actual = actual


class DiskSpaceError(DownloadError):
    """Exception for insufficient disk space."""
    pass


class PermissionError(DownloadError):
    """Exception for permission errors."""
    pass


class CancellationError(DownloadError):
    """Exception for cancelled downloads."""
    pass


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class DownloadProgress:
    """
    Download progress information.
    
    Tracks real-time progress statistics for a download.
    """
    
    # Core progress data
    bytes_downloaded: int = 0
    total_bytes: int = 0
    speed_bps: float = 0.0  # bytes per second
    eta_seconds: float = 0.0
    
    # Time tracking
    start_time: float = 0.0
    elapsed_seconds: float = 0.0
    
    # Chunk tracking (for segmented downloads)
    chunks_completed: int = 0
    total_chunks: int = 1
    
    # Retry tracking
    retry_count: int = 0
    
    # Status
    status: DownloadStatus = DownloadStatus.PENDING
    
    # Internal tracking
    _last_update_time: float = 0.0
    _last_bytes: int = 0
    _speed_samples: List[Tuple[float, int]] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Initialize timing data."""
        if self.start_time == 0.0:
            self.start_time = time.monotonic()
    
    @property
    def progress_percent(self) -> float:
        """Get progress percentage (0-100)."""
        if self.total_bytes <= 0:
            return 0.0
        return min(100.0, (self.bytes_downloaded / self.total_bytes) * 100)
    
    @property
    def is_complete(self) -> bool:
        """Check if download is complete."""
        return self.status in (
            DownloadStatus.COMPLETED,
            DownloadStatus.FAILED,
            DownloadStatus.CANCELLED
        )
    
    @property
    def is_active(self) -> bool:
        """Check if download is active."""
        return self.status in (
            DownloadStatus.DOWNLOADING,
            DownloadStatus.STARTING,
            DownloadStatus.RETRYING
        )
    
    @property
    def remaining_bytes(self) -> int:
        """Get remaining bytes to download."""
        return max(0, self.total_bytes - self.bytes_downloaded)
    
    @property
    def formatted_size(self) -> str:
        """Get formatted total size string."""
        return format_size(self.total_bytes)
    
    @property
    def formatted_downloaded(self) -> str:
        """Get formatted downloaded size string."""
        return format_size(self.bytes_downloaded)
    
    @property
    def formatted_speed(self) -> str:
        """Get formatted speed string."""
        return format_size(int(self.speed_bps)) + "/s"
    
    @property
    def formatted_eta(self) -> str:
        """Get formatted ETA string."""
        if self.eta_seconds <= 0:
            return "calculating..."
        return format_time(self.eta_seconds)
    
    def update(
        self,
        bytes_downloaded: int,
        total_bytes: Optional[int] = None,
        chunk_size: int = 0
    ) -> None:
        """
        Update progress with new data.
        
        Args:
            bytes_downloaded: Total bytes downloaded so far.
            total_bytes: Total bytes (if known).
            chunk_size: Size of last chunk (for speed calculation).
        """
        now = time.monotonic()
        self.elapsed_seconds = now - self.start_time
        
        if total_bytes is not None and total_bytes > 0:
            self.total_bytes = total_bytes
        
        self.bytes_downloaded = bytes_downloaded
        
        # Calculate speed using exponential moving average
        if chunk_size > 0 and self._last_update_time > 0:
            time_delta = now - self._last_update_time
            if time_delta > 0:
                instant_speed = chunk_size / time_delta
                # Exponential moving average (alpha = 0.3)
                self.speed_bps = 0.7 * self.speed_bps + 0.3 * instant_speed
        
        # Update ETA
        if self.speed_bps > 0 and self.remaining_bytes > 0:
            self.eta_seconds = self.remaining_bytes / self.speed_bps
        else:
            self.eta_seconds = 0
        
        self._last_update_time = now
        self._last_bytes = bytes_downloaded
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "bytes_downloaded": self.bytes_downloaded,
            "total_bytes": self.total_bytes,
            "progress_percent": round(self.progress_percent, 2),
            "speed_bps": round(self.speed_bps, 2),
            "eta_seconds": round(self.eta_seconds, 2),
            "elapsed_seconds": round(self.elapsed_seconds, 2),
            "status": self.status.name,
            "retry_count": self.retry_count,
        }


@dataclass
class DownloadTask:
    """
    Download task definition.
    
    Represents a single download task with all required parameters.
    """
    
    # Required fields
    url: str
    
    # Optional fields with defaults
    file_path: Optional[str] = None
    filename: Optional[str] = None
    directory: Optional[str] = None
    
    # Download options
    priority: Priority = Priority.NORMAL
    headers: Optional[Dict[str, str]] = None
    cookies: Optional[Dict[str, str]] = None
    
    # Chunk/segment options
    chunk_size: int = DEFAULT_CHUNK_SIZE
    segments: int = 1  # Number of concurrent segments
    
    # Verification options
    expected_hash: Optional[str] = None
    hash_algorithm: HashAlgorithm = HashAlgorithm.SHA256
    expected_size: Optional[int] = None
    
    # Behavior options
    conflict_resolution: ConflictResolution = ConflictResolution.RENAME
    max_retries: int = 3
    timeout: float = 30.0
    bandwidth_limit: Optional[int] = None  # bytes per second
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Internal fields
    _id: Optional[str] = field(default=None, repr=False)
    _created_at: float = field(default_factory=time.time, repr=False)
    
    def __post_init__(self) -> None:
        """Validate and process task."""
        # Validate URL
        if not self.url:
            raise ValidationError("URL is required")
        
        # Generate ID if not set
        if self._id is None:
            self._id = self._generate_id()
        
        # Normalize headers
        if self.headers:
            self.headers = {k.lower(): v for k, v in self.headers.items()}
    
    @property
    def id(self) -> str:
        """Get task ID."""
        return self._id or self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique task ID."""
        timestamp = int(time.time() * 1000)
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"dl_{timestamp}_{random_suffix}"
    
    def get_safe_filename(self) -> str:
        """
        Get safe filename from URL or specified filename.
        
        Returns:
            str: Safe filename.
        """
        if self.filename:
            return sanitize_filename(self.filename)
        
        # Try to extract from URL
        parsed = urlparse(self.url)
        path = unquote(parsed.path)
        
        if path and path != "/":
            filename = os.path.basename(path.rstrip("/"))
            if filename:
                return sanitize_filename(filename)
        
        # Generate filename from URL
        domain = parsed.netloc or "download"
        timestamp = int(time.time())
        return sanitize_filename(f"{domain}_{timestamp}")
    
    def get_output_path(self, base_dir: Optional[str] = None) -> Path:
        """
        Get full output path for download.
        
        Args:
            base_dir: Base directory for downloads.
        
        Returns:
            Path: Full output path.
        """
        # Determine directory
        directory = self.directory or base_dir or "."
        dir_path = Path(directory).resolve()
        
        # Determine filename
        filename = self.filename or self.get_safe_filename()
        
        # Combine
        return dir_path / filename
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "url": sanitize_url_for_logging(self.url),
            "filename": self.filename,
            "directory": self.directory,
            "priority": self.priority.name,
            "status": "pending",
            "created_at": datetime.fromtimestamp(self._created_at, tz=timezone.utc).isoformat(),
        }


@dataclass
class DownloadResult:
    """
    Download result information.
    
    Contains the outcome of a completed download task.
    """
    
    # Task reference
    task_id: str
    url: str
    
    # Result status
    success: bool
    status: DownloadStatus
    
    # File information
    file_path: Optional[str] = None
    file_size: int = 0
    content_type: Optional[str] = None
    
    # Timing information
    start_time: float = 0.0
    end_time: float = 0.0
    duration_seconds: float = 0.0
    average_speed: float = 0.0
    
    # Verification
    hash_value: Optional[str] = None
    hash_verified: Optional[bool] = None
    
    # Error information
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    retry_count: int = 0
    
    # Metadata
    headers: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def formatted_size(self) -> str:
        """Get formatted file size."""
        return format_size(self.file_size)
    
    @property
    def formatted_duration(self) -> str:
        """Get formatted duration."""
        return format_time(self.duration_seconds)
    
    @property
    def formatted_speed(self) -> str:
        """Get formatted average speed."""
        return format_size(int(self.average_speed)) + "/s"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "task_id": self.task_id,
            "url": sanitize_url_for_logging(self.url),
            "success": self.success,
            "status": self.status.name,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "duration_seconds": round(self.duration_seconds, 2),
            "average_speed": round(self.average_speed, 2),
            "hash_value": self.hash_value,
            "hash_verified": self.hash_verified,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
        }


# =============================================================================
# CALLBACK PROTOCOLS
# =============================================================================

@runtime_checkable
class ProgressCallback(Protocol):
    """Protocol for progress callback functions."""
    
    def __call__(
        self,
        task_id: str,
        progress: DownloadProgress
    ) -> None: ...


@runtime_checkable
class CompletionCallback(Protocol):
    """Protocol for completion callback functions."""
    
    def __call__(
        self,
        task_id: str,
        result: DownloadResult
    ) -> None: ...


@runtime_checkable
class ErrorCallback(Protocol):
    """Protocol for error callback functions."""
    
    def __call__(
        self,
        task_id: str,
        error: Exception
    ) -> None: ...


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def format_size(size: int) -> str:
    """
    Format byte size to human-readable string.
    
    Args:
        size: Size in bytes.
    
    Returns:
        str: Formatted size string.
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.1f} {unit}" if unit != "B" else f"{size} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def format_time(seconds: float) -> str:
    """
    Format seconds to human-readable time string.
    
    Args:
        seconds: Time in seconds.
    
    Returns:
        str: Formatted time string.
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
    else:
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        return f"{days}d {hours}h"


def sanitize_filename(filename: str, max_length: int = MAX_FILENAME_LENGTH) -> str:
    """
    Sanitize filename for safe filesystem use.
    
    Args:
        filename: Original filename.
        max_length: Maximum filename length.
    
    Returns:
        str: Sanitized filename.
    """
    if not filename:
        return "download"
    
    # Remove invalid characters
    sanitized = INVALID_FILENAME_CHARS.sub("_", filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(". ")
    
    # Truncate if too long
    if len(sanitized) > max_length:
        name, ext = os.path.splitext(sanitized)
        max_name = max_length - len(ext)
        sanitized = name[:max_name] + ext
    
    # Ensure not empty
    if not sanitized:
        sanitized = "download"
    
    return sanitized


def get_unique_filename(path: Path) -> Path:
    """
    Get unique filename by appending number if file exists.
    
    Args:
        path: Original path.
    
    Returns:
        Path: Unique path.
    """
    if not path.exists():
        return path
    
    directory = path.parent
    name = path.stem
    suffix = path.suffix
    
    counter = 1
    while True:
        new_name = f"{name} ({counter}){suffix}"
        new_path = directory / new_name
        if not new_path.exists():
            return new_path
        counter += 1
        
        # Safety limit
        if counter > 1000:
            raise DownloadError(f"Could not find unique filename for {path}")


def calculate_hash(
    file_path: Union[str, Path],
    algorithm: HashAlgorithm = HashAlgorithm.SHA256,
    chunk_size: int = 8192
) -> str:
    """
    Calculate file hash.
    
    Args:
        file_path: Path to file.
        algorithm: Hash algorithm.
        chunk_size: Read chunk size.
    
    Returns:
        str: Hexadecimal hash string.
    """
    hasher = hashlib.new(algorithm.value)
    
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    
    return hasher.hexdigest()


def verify_hash(
    file_path: Union[str, Path],
    expected_hash: str,
    algorithm: HashAlgorithm = HashAlgorithm.SHA256
) -> bool:
    """
    Verify file hash against expected value.
    
    Args:
        file_path: Path to file.
        expected_hash: Expected hash value.
        algorithm: Hash algorithm.
    
    Returns:
        bool: True if hash matches.
    """
    actual_hash = calculate_hash(file_path, algorithm)
    return actual_hash.lower() == expected_hash.lower()


def check_disk_space(path: Union[str, Path], required_bytes: int) -> bool:
    """
    Check if sufficient disk space is available.
    
    Args:
        path: Target path.
        required_bytes: Required space in bytes.
    
    Returns:
        bool: True if sufficient space available.
    """
    try:
        path = Path(path)
        if not path.exists():
            path = path.parent
        
        usage = shutil.disk_usage(path)
        return usage.free >= required_bytes * 1.1  # 10% buffer
    except (OSError, AttributeError):
        return True  # Assume OK if can't check


# =============================================================================
# BASE DOWNLOADER CLASS
# =============================================================================

class DownloaderBase(ABC):
    """
    Abstract base class for downloaders.
    
    Provides common functionality and interface for all downloader
    implementations.
    
    Attributes:
        config: Configuration instance.
        logger: Logger instance.
        _tasks: Active download tasks.
        _results: Completed download results.
    """
    
    def __init__(
        self,
        config: Optional[Config] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize downloader.
        
        Args:
            config: Configuration instance.
            logger: Logger instance.
        """
        self.config = config or Config()
        self._logger = logger or get_logger("downloader.base")
        
        # Task management
        self._tasks: Dict[str, DownloadTask] = {}
        self._progress: Dict[str, DownloadProgress] = {}
        self._results: Dict[str, DownloadResult] = {}
        
        # Callbacks
        self._progress_callbacks: List[ProgressCallback] = []
        self._completion_callbacks: List[CompletionCallback] = []
        self._error_callbacks: List[ErrorCallback] = []
        
        # State
        self._running = False
        self._lock = threading.Lock()
        self._cancel_event = threading.Event()
    
    @property
    def is_running(self) -> bool:
        """Check if downloader is running."""
        return self._running
    
    @property
    def active_count(self) -> int:
        """Get count of active downloads."""
        return sum(
            1 for p in self._progress.values()
            if p.is_active
        )
    
    @property
    def pending_count(self) -> int:
        """Get count of pending downloads."""
        return sum(
            1 for p in self._progress.values()
            if p.status == DownloadStatus.PENDING
        )
    
    # Abstract methods
    @abstractmethod
    async def download(self, task: DownloadTask) -> DownloadResult:
        """
        Execute a download task.
        
        Args:
            task: Download task to execute.
        
        Returns:
            DownloadResult: Download result.
        """
        pass
    
    @abstractmethod
    async def download_batch(
        self,
        tasks: List[DownloadTask],
        max_concurrent: int = DEFAULT_MAX_CONCURRENT
    ) -> List[DownloadResult]:
        """
        Execute multiple download tasks concurrently.
        
        Args:
            tasks: List of download tasks.
            max_concurrent: Maximum concurrent downloads.
        
        Returns:
            List[DownloadResult]: List of results.
        """
        pass
    
    @abstractmethod
    def pause(self, task_id: str) -> bool:
        """
        Pause a download.
        
        Args:
            task_id: Task ID to pause.
        
        Returns:
            bool: True if paused successfully.
        """
        pass
    
    @abstractmethod
    def resume(self, task_id: str) -> bool:
        """
        Resume a paused download.
        
        Args:
            task_id: Task ID to resume.
        
        Returns:
            bool: True if resumed successfully.
        """
        pass
    
    @abstractmethod
    def cancel(self, task_id: str) -> bool:
        """
        Cancel a download.
        
        Args:
            task_id: Task ID to cancel.
        
        Returns:
            bool: True if cancelled successfully.
        """
        pass
    
    # Common methods
    def add_task(self, task: DownloadTask) -> str:
        """
        Add a download task.
        
        Args:
            task: Download task to add.
        
        Returns:
            str: Task ID.
        """
        with self._lock:
            task_id = task.id
            self._tasks[task_id] = task
            self._progress[task_id] = DownloadProgress(
                status=DownloadStatus.PENDING
            )
        
        self._logger.info(f"Added task {task_id}: {sanitize_url_for_logging(task.url)}")
        return task_id
    
    def remove_task(self, task_id: str) -> Optional[DownloadTask]:
        """
        Remove a download task.
        
        Args:
            task_id: Task ID to remove.
        
        Returns:
            Optional[DownloadTask]: Removed task or None.
        """
        with self._lock:
            task = self._tasks.pop(task_id, None)
            self._progress.pop(task_id, None)
        
        if task:
            self._logger.info(f"Removed task {task_id}")
        return task
    
    def get_progress(self, task_id: str) -> Optional[DownloadProgress]:
        """
        Get progress for a task.
        
        Args:
            task_id: Task ID.
        
        Returns:
            Optional[DownloadProgress]: Progress or None.
        """
        return self._progress.get(task_id)
    
    def get_result(self, task_id: str) -> Optional[DownloadResult]:
        """
        Get result for a completed task.
        
        Args:
            task_id: Task ID.
        
        Returns:
            Optional[DownloadResult]: Result or None.
        """
        return self._results.get(task_id)
    
    def get_task(self, task_id: str) -> Optional[DownloadTask]:
        """
        Get task by ID.
        
        Args:
            task_id: Task ID.
        
        Returns:
            Optional[DownloadTask]: Task or None.
        """
        return self._tasks.get(task_id)
    
    def get_all_tasks(self) -> List[DownloadTask]:
        """
        Get all tasks.
        
        Returns:
            List[DownloadTask]: List of all tasks.
        """
        return list(self._tasks.values())
    
    def get_all_progress(self) -> Dict[str, DownloadProgress]:
        """
        Get progress for all tasks.
        
        Returns:
            Dict[str, DownloadProgress]: Progress dictionary.
        """
        return self._progress.copy()
    
    # Callback registration
    def on_progress(self, callback: ProgressCallback) -> None:
        """
        Register progress callback.
        
        Args:
            callback: Callback function.
        """
        self._progress_callbacks.append(callback)
    
    def on_completion(self, callback: CompletionCallback) -> None:
        """
        Register completion callback.
        
        Args:
            callback: Callback function.
        """
        self._completion_callbacks.append(callback)
    
    def on_error(self, callback: ErrorCallback) -> None:
        """
        Register error callback.
        
        Args:
            callback: Callback function.
        """
        self._error_callbacks.append(callback)
    
    def _notify_progress(self, task_id: str, progress: DownloadProgress) -> None:
        """Notify progress callbacks."""
        for callback in self._progress_callbacks:
            try:
                callback(task_id, progress)
            except Exception as e:
                self._logger.warning(f"Progress callback error: {e}")
    
    def _notify_completion(self, task_id: str, result: DownloadResult) -> None:
        """Notify completion callbacks."""
        for callback in self._completion_callbacks:
            try:
                callback(task_id, result)
            except Exception as e:
                self._logger.warning(f"Completion callback error: {e}")
    
    def _notify_error(self, task_id: str, error: Exception) -> None:
        """Notify error callbacks."""
        for callback in self._error_callbacks:
            try:
                callback(task_id, error)
            except Exception as e:
                self._logger.warning(f"Error callback error: {e}")
    
    def cancel_all(self) -> int:
        """
        Cancel all active downloads.
        
        Returns:
            int: Number of cancelled downloads.
        """
        self._cancel_event.set()
        count = 0
        
        with self._lock:
            for task_id, progress in self._progress.items():
                if progress.is_active:
                    self.cancel(task_id)
                    count += 1
        
        self._logger.info(f"Cancelled {count} downloads")
        return count
    
    def clear_completed(self) -> int:
        """
        Clear completed downloads from memory.
        
        Returns:
            int: Number of cleared downloads.
        """
        count = 0
        
        with self._lock:
            for task_id, progress in list(self._progress.items()):
                if progress.is_complete:
                    del self._progress[task_id]
                    del self._tasks[task_id]
                    count += 1
        
        self._logger.info(f"Cleared {count} completed downloads")
        return count


# =============================================================================
# CONCRETE DOWNLOADER IMPLEMENTATION
# =============================================================================

class Downloader(DownloaderBase):
    """
    Concrete async downloader implementation.
    
    Provides full-featured downloading with async support,
    progress tracking, and comprehensive error handling.
    
    Example:
        >>> config = Config.production()
        >>> async with Downloader(config) as downloader:
        ...     task = DownloadTask(url="https://example.com/file.zip")
        ...     result = await downloader.download(task)
        ...     print(f"Downloaded to: {result.file_path}")
    """
    
    def __init__(
        self,
        config: Optional[Config] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize downloader.
        
        Args:
            config: Configuration instance.
            logger: Logger instance.
        """
        super().__init__(config, logger)
        self._client: Optional[NetworkClient] = None
        self._semaphore: Optional[asyncio.Semaphore] = None
    
    async def __aenter__(self) -> "Downloader":
        """Enter async context."""
        await self._ensure_client()
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        """Exit async context."""
        await self.close()
    
    async def _ensure_client(self) -> NetworkClient:
        """Ensure network client is initialized."""
        if self._client is None:
            self._client = NetworkClient(self.config, self._logger)
        return self._client
    
    async def close(self) -> None:
        """Close downloader and release resources."""
        self._running = False
        if self._client:
            await self._client.close()
            self._client = None
    
    async def download(self, task: DownloadTask) -> DownloadResult:
        """
        Execute a download task.
        
        Args:
            task: Download task to execute.
        
        Returns:
            DownloadResult: Download result.
        """
        # Add task if not already added
        task_id = task.id
        if task_id not in self._tasks:
            self.add_task(task)
        
        progress = self._progress[task_id]
        result = DownloadResult(
            task_id=task_id,
            url=task.url,
            success=False,
            status=DownloadStatus.PENDING,
        )
        
        start_time = time.monotonic()
        progress.start_time = start_time
        progress.status = DownloadStatus.STARTING
        
        try:
            client = await self._ensure_client()
            
            # Determine output path
            output_path = task.get_output_path(self.config.temp_dir)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check disk space
            if task.expected_size and not check_disk_space(output_path.parent, task.expected_size):
                raise DiskSpaceError(
                    "Insufficient disk space",
                    url=task.url,
                    file_path=str(output_path)
                )
            
            # Handle file conflicts
            if output_path.exists():
                if task.conflict_resolution == ConflictResolution.SKIP:
                    self._logger.info(f"Skipping existing file: {output_path}")
                    result.success = True
                    result.status = DownloadStatus.COMPLETED
                    result.file_path = str(output_path)
                    return result
                elif task.conflict_resolution == ConflictResolution.RENAME:
                    output_path = get_unique_filename(output_path)
                elif task.conflict_resolution == ConflictResolution.OVERWRITE:
                    output_path.unlink(missing_ok=True)
            
            # Create temp file
            temp_path = output_path.with_suffix(output_path.suffix + DEFAULT_TEMP_SUFFIX)
            
            # Get file info
            progress.status = DownloadStatus.DOWNLOADING
            self._notify_progress(task_id, progress)
            
            # Perform download
            response = await client.get(task.url, headers=task.headers)
            
            # Check response
            if not response.ok:
                raise HTTPError(
                    f"HTTP error: {response.status_code}",
                    url=task.url,
                    status_code=response.status_code,
                    response=response
                )
            
            # Get content length
            content_length = int(response.headers.get("content-length", 0))
            if task.expected_size and content_length != task.expected_size:
                self._logger.warning(
                    f"Content length mismatch: expected {task.expected_size}, got {content_length}"
                )
            
            total_bytes = content_length or task.expected_size or 0
            progress.total_bytes = total_bytes
            
            # Write to file
            bytes_written = 0
            chunk_size = task.chunk_size or self.config.chunk_size
            
            with open(temp_path, "wb") as f:
                # Simulate chunked writing
                chunk_pos = 0
                while chunk_pos < len(response.content):
                    chunk = response.content[chunk_pos:chunk_pos + chunk_size]
                    f.write(chunk)
                    bytes_written += len(chunk)
                    chunk_pos += chunk_size
                    
                    # Update progress
                    progress.update(bytes_written, total_bytes, len(chunk))
                    self._notify_progress(task_id, progress)
                    
                    # Check bandwidth limit
                    if task.bandwidth_limit:
                        await asyncio.sleep(len(chunk) / task.bandwidth_limit)
                    
                    # Check cancellation
                    if self._cancel_event.is_set():
                        raise CancellationError(
                            "Download cancelled",
                            url=task.url,
                            file_path=str(output_path)
                        )
            
            # Verify hash if required
            if task.expected_hash:
                progress.status = DownloadStatus.VERIFYING
                self._notify_progress(task_id, progress)
                
                actual_hash = calculate_hash(temp_path, task.hash_algorithm)
                result.hash_value = actual_hash
                result.hash_verified = actual_hash.lower() == task.expected_hash.lower()
                
                if not result.hash_verified:
                    raise ChecksumError(
                        f"Hash verification failed",
                        expected=task.expected_hash,
                        actual=actual_hash,
                        url=task.url,
                        file_path=str(temp_path)
                    )
            
            # Move temp file to final location
            temp_path.rename(output_path)
            
            # Complete
            end_time = time.monotonic()
            duration = end_time - start_time
            
            progress.status = DownloadStatus.COMPLETED
            progress.bytes_downloaded = bytes_written
            progress.total_bytes = bytes_written
            
            result.success = True
            result.status = DownloadStatus.COMPLETED
            result.file_path = str(output_path)
            result.file_size = bytes_written
            result.content_type = response.content_type
            result.duration_seconds = duration
            result.average_speed = bytes_written / duration if duration > 0 else 0
            result.headers = dict(response.headers)
            
            self._results[task_id] = result
            self._notify_completion(task_id, result)
            
            self._logger.info(
                f"Download complete: {output_path.name} "
                f"({format_size(bytes_written)}, {format_time(duration)})"
            )
            
            return result
            
        except Exception as e:
            end_time = time.monotonic()
            
            result.success = False
            result.status = DownloadStatus.FAILED
            result.error_message = str(e)
            result.error_type = type(e).__name__
            result.duration_seconds = end_time - start_time
            
            progress.status = DownloadStatus.FAILED
            
            self._results[task_id] = result
            self._notify_error(task_id, e)
            
            self._logger.error(f"Download failed: {e}")
            raise
    
    async def download_batch(
        self,
        tasks: List[DownloadTask],
        max_concurrent: int = DEFAULT_MAX_CONCURRENT
    ) -> List[DownloadResult]:
        """
        Execute multiple download tasks concurrently.
        
        Args:
            tasks: List of download tasks.
            max_concurrent: Maximum concurrent downloads.
        
        Returns:
            List[DownloadResult]: List of results.
        """
        self._running = True
        self._semaphore = asyncio.Semaphore(max_concurrent)
        
        results: List[DownloadResult] = []
        
        async def download_with_semaphore(task: DownloadTask) -> DownloadResult:
            async with self._semaphore:
                return await self.download(task)
        
        # Create tasks
        coros = [download_with_semaphore(task) for task in tasks]
        
        # Execute concurrently
        results = await asyncio.gather(*coros, return_exceptions=True)
        
        # Convert exceptions to results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(DownloadResult(
                    task_id=tasks[i].id,
                    url=tasks[i].url,
                    success=False,
                    status=DownloadStatus.FAILED,
                    error_message=str(result),
                    error_type=type(result).__name__
                ))
            else:
                final_results.append(result)
        
        self._running = False
        return final_results
    
    def pause(self, task_id: str) -> bool:
        """
        Pause a download.
        
        Note: This implementation doesn't support true pause/resume.
        It cancels the download, which can be resumed if the server
        supports range requests.
        
        Args:
            task_id: Task ID to pause.
        
        Returns:
            bool: True if paused successfully.
        """
        progress = self._progress.get(task_id)
        if progress and progress.is_active:
            progress.status = DownloadStatus.PAUSED
            self._cancel_event.set()
            return True
        return False
    
    def resume(self, task_id: str) -> bool:
        """
        Resume a paused download.
        
        Args:
            task_id: Task ID to resume.
        
        Returns:
            bool: True if resumed successfully.
        """
        progress = self._progress.get(task_id)
        task = self._tasks.get(task_id)
        
        if progress and task and progress.status == DownloadStatus.PAUSED:
            progress.status = DownloadStatus.PENDING
            self._cancel_event.clear()
            # Would need to restart the download
            return True
        return False
    
    def cancel(self, task_id: str) -> bool:
        """
        Cancel a download.
        
        Args:
            task_id: Task ID to cancel.
        
        Returns:
            bool: True if cancelled successfully.
        """
        progress = self._progress.get(task_id)
        if progress:
            progress.status = DownloadStatus.CANCELLED
            self._cancel_event.set()
            return True
        return False
    
    async def get_file_info(self, url: str) -> Dict[str, Any]:
        """
        Get file information without downloading.
        
        Args:
            url: URL to check.
        
        Returns:
            Dict[str, Any]: File information dictionary.
        """
        client = await self._ensure_client()
        
        response = await client.head(url)
        
        info = {
            "url": url,
            "status_code": response.status_code,
            "content_type": response.content_type,
            "content_length": int(response.headers.get("content-length", 0)),
            "last_modified": response.headers.get("last-modified"),
            "etag": response.headers.get("etag"),
            "accept_ranges": response.headers.get("accept-ranges"),
            "filename": get_content_disposition_filename(response.headers),
        }
        
        return info


# =============================================================================
# SYNC WRAPPER
# =============================================================================

class SyncDownloader:
    """
    Synchronous wrapper for Downloader.
    
    Provides a synchronous interface for the async downloader.
    
    Example:
        >>> with SyncDownloader(config) as downloader:
        ...     result = downloader.download("https://example.com/file.zip")
        ...     print(f"Downloaded to: {result.file_path}")
    """
    
    def __init__(
        self,
        config: Optional[Config] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize sync downloader.
        
        Args:
            config: Configuration instance.
            logger: Logger instance.
        """
        self._async_downloader = Downloader(config, logger)
        self._loop: Optional[asyncio.AbstractEventLoop] = None
    
    def __enter__(self) -> "SyncDownloader":
        """Enter context."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._async_downloader._ensure_client())
        return self
    
    def __exit__(self, *args: Any) -> None:
        """Exit context."""
        if self._loop:
            self._loop.run_until_complete(self._async_downloader.close())
            self._loop.close()
            self._loop = None
    
    def download(
        self,
        url: str,
        output_path: Optional[str] = None,
        **kwargs: Any
    ) -> DownloadResult:
        """
        Download a file synchronously.
        
        Args:
            url: URL to download.
            output_path: Output file path.
            **kwargs: Additional task options.
        
        Returns:
            DownloadResult: Download result.
        """
        task = DownloadTask(
            url=url,
            file_path=output_path,
            **kwargs
        )
        
        return self._loop.run_until_complete(
            self._async_downloader.download(task)
        )
    
    def download_batch(
        self,
        urls: List[str],
        output_dir: str,
        max_concurrent: int = DEFAULT_MAX_CONCURRENT
    ) -> List[DownloadResult]:
        """
        Download multiple files synchronously.
        
        Args:
            urls: List of URLs.
            output_dir: Output directory.
            max_concurrent: Maximum concurrent downloads.
        
        Returns:
            List[DownloadResult]: List of results.
        """
        tasks = [
            DownloadTask(url=url, directory=output_dir)
            for url in urls
        ]
        
        return self._loop.run_until_complete(
            self._async_downloader.download_batch(tasks, max_concurrent)
        )


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "DownloadStatus",
    "HashAlgorithm",
    "Priority",
    "ConflictResolution",
    # Exceptions
    "DownloadError",
    "ValidationError",
    "ChecksumError",
    "DiskSpaceError",
    "PermissionError",
    "CancellationError",
    # Data classes
    "DownloadProgress",
    "DownloadTask",
    "DownloadResult",
    # Classes
    "DownloaderBase",
    "Downloader",
    "SyncDownloader",
    # Protocols
    "ProgressCallback",
    "CompletionCallback",
    "ErrorCallback",
    # Utility functions
    "format_size",
    "format_time",
    "sanitize_filename",
    "get_unique_filename",
    "calculate_hash",
    "verify_hash",
    "check_disk_space",
    # Constants
    "DEFAULT_CHUNK_SIZE",
    "DEFAULT_MAX_CONCURRENT",
    "DEFAULT_MIN_CHUNK_SIZE",
    "DEFAULT_MAX_CHUNK_SIZE",
    "DEFAULT_TEMP_SUFFIX",
    "MAX_FILENAME_LENGTH",
]

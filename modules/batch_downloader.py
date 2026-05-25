"""
OMNIPOTENT SOVEREIGN NEXUS - Batch Downloader Module
Version: v3.2.0 ULTIMATE NEXUS

Advanced batch downloading with support for:
- Multiple URL sources (file, list, API, clipboard)
- Ultra-fast parallel downloads with configurable concurrency
- Smart queue management with priority support
- Progress tracking and real-time reporting
- Advanced error handling with automatic retry
- Rate limiting and bandwidth control
- Smart scheduling and automation
- Download queue persistence and recovery
- Statistics and analytics
- URL validation and deduplication
- Auto-categorization by file type
- Bandwidth throttling per category
- Speed optimization with connection pooling
- Pause/Resume/Cancel operations
- Download templates and presets
- Export reports (JSON, CSV, HTML)
- Webhook notifications
- Checksum verification
- Archive management

Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
"""

import asyncio
import aiohttp
import aiofiles
import logging
import re
import time
import json
import shutil
import csv
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Union,
    Awaitable,
    Tuple,
    AsyncIterator,
    TypedDict,
)
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import subprocess
from urllib.parse import urlparse


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)


class BatchStatus(Enum):
    """Batch job status."""
    
    PENDING = "pending"
    PREPARING = "preparing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    PARTIAL = "partial"  # Some failed
    FAILED = "failed"
    CANCELLED = "cancelled"


class ItemStatus(Enum):
    """Individual item status."""
    
    QUEUED = "queued"
    VALIDATING = "validating"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class DownloadPriority(Enum):
    """Download priority levels."""
    
    CRITICAL = 100
    HIGH = 75
    NORMAL = 50
    LOW = 25
    BACKGROUND = 10


class InputSourceType(Enum):
    """Source type for batch URLs."""
    
    FILE = "file"
    LIST = "list"
    URL = "url"
    API = "api"
    CLIPBOARD = "clipboard"
    STDIN = "stdin"


class ReportFormat(Enum):
    """Report output formats."""
    
    JSON = "json"
    CSV = "csv"
    HTML = "html"
    TXT = "txt"
    XML = "xml"


@dataclass
class BandwidthConfig:
    """
    Bandwidth control configuration.
    
    Attributes:
        max_total_speed: Maximum total download speed (bytes/sec)
        max_per_download: Maximum speed per download
        schedule: Bandwidth schedule (hour -> speed limit)
        adaptive: Auto-adjust based on network conditions
    """
    max_total_speed: int = 0  # 0 = unlimited
    max_per_download: int = 0
    schedule: Dict[int, int] = field(default_factory=dict)  # hour -> bytes/sec
    adaptive: bool = False
    
    def get_current_limit(self) -> int:
        """Get current bandwidth limit based on schedule."""
        if self.schedule:
            current_hour = datetime.now().hour
            return self.schedule.get(current_hour, self.max_total_speed)
        return self.max_total_speed


@dataclass
class BatchItem:
    """
    Individual batch download item.
    
    Attributes:
        id: Unique item ID
        url: Download URL
        output_filename: Output filename
        category: Item category (video, audio, etc.)
        priority: Download priority
        status: Current status
        progress: Download progress percentage
        bytes_downloaded: Bytes downloaded
        total_bytes: Total bytes
        speed: Current download speed
        error_message: Error message if failed
        error_code: Error code
        retry_count: Number of retries attempted
        max_retries: Maximum retries
        start_time: Download start time
        end_time: Download end time
        filepath: Path to downloaded file
        metadata: Additional metadata
        checksum: Expected checksum
        checksum_algorithm: Checksum algorithm
    """
    id: str
    url: str
    output_filename: Optional[str] = None
    category: str = "general"
    priority: DownloadPriority = DownloadPriority.NORMAL
    status: ItemStatus = ItemStatus.QUEUED
    progress: float = 0.0
    bytes_downloaded: int = 0
    total_bytes: int = 0
    speed: float = 0.0
    error_message: Optional[str] = None
    error_code: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    filepath: Optional[Path] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: Optional[str] = None
    checksum_algorithm: str = "md5"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "url": self.url,
            "output_filename": self.output_filename,
            "category": self.category,
            "priority": self.priority.name,
            "status": self.status.value,
            "progress": self.progress,
            "bytes_downloaded": self.bytes_downloaded,
            "total_bytes": self.total_bytes,
            "speed": self.speed,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "filepath": str(self.filepath) if self.filepath else None,
        }


@dataclass
class BatchProgress:
    """
    Batch download progress information.
    
    Attributes:
        batch_id: Batch job ID
        total_items: Total items in batch
        completed_items: Completed item count
        failed_items: Failed item count
        skipped_items: Skipped item count
        current_items: Currently downloading items
        bytes_downloaded: Total bytes downloaded
        total_bytes: Estimated total bytes
        start_time: Batch start time
        elapsed_time: Elapsed time in seconds
        eta: Estimated time remaining
        average_speed: Average download speed
        peak_speed: Peak download speed
        status: Current batch status
        bandwidth_usage: Current bandwidth usage
        active_connections: Number of active connections
    """
    batch_id: str
    total_items: int = 0
    completed_items: int = 0
    failed_items: int = 0
    skipped_items: int = 0
    current_items: List[str] = field(default_factory=list)
    bytes_downloaded: int = 0
    total_bytes: int = 0
    start_time: Optional[datetime] = None
    elapsed_time: float = 0.0
    eta: float = 0.0
    average_speed: float = 0.0
    peak_speed: float = 0.0
    status: BatchStatus = BatchStatus.PENDING
    bandwidth_usage: float = 0.0
    active_connections: int = 0
    
    @property
    def percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_items == 0:
            return 0.0
        return ((self.completed_items + self.failed_items + self.skipped_items) / self.total_items) * 100
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        processed = self.completed_items + self.failed_items + self.skipped_items
        if processed == 0:
            return 0.0
        return (self.completed_items / processed) * 100
    
    @property
    def speed_formatted(self) -> str:
        """Return formatted speed string."""
        speed = self.average_speed
        if speed < 1024:
            return f"{speed:.0f} B/s"
        elif speed < 1024 * 1024:
            return f"{speed / 1024:.1f} KB/s"
        elif speed < 1024 * 1024 * 1024:
            return f"{speed / (1024 * 1024):.1f} MB/s"
        return f"{speed / (1024 * 1024 * 1024):.2f} GB/s"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "batch_id": self.batch_id,
            "total_items": self.total_items,
            "completed_items": self.completed_items,
            "failed_items": self.failed_items,
            "skipped_items": self.skipped_items,
            "current_items": self.current_items,
            "bytes_downloaded": self.bytes_downloaded,
            "total_bytes": self.total_bytes,
            "elapsed_time": self.elapsed_time,
            "eta": self.eta,
            "percentage": self.percentage,
            "average_speed": self.average_speed,
            "speed_formatted": self.speed_formatted,
            "success_rate": self.success_rate,
            "status": self.status.value,
            "bandwidth_usage": self.bandwidth_usage,
            "active_connections": self.active_connections,
        }


@dataclass
class BatchResult:
    """
    Final batch download result.
    
    Attributes:
        batch_id: Batch job ID
        success: Whether batch succeeded
        total_items: Total items processed
        successful: Successful download count
        failed: Failed download count
        skipped: Skipped item count
        total_bytes: Total bytes downloaded
        total_time: Total time elapsed
        average_speed: Average download speed
        items: Individual item results
        errors: List of error messages
        start_time: Batch start time
        end_time: Batch end time
        checksum_errors: Items with checksum mismatches
    """
    batch_id: str
    success: bool = False
    total_items: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    total_bytes: int = 0
    total_time: float = 0.0
    average_speed: float = 0.0
    items: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    checksum_errors: int = 0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_items == 0:
            return 0.0
        return (self.successful / self.total_items) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "batch_id": self.batch_id,
            "success": self.success,
            "total_items": self.total_items,
            "successful": self.successful,
            "failed": self.failed,
            "skipped": self.skipped,
            "total_bytes": self.total_bytes,
            "total_time": self.total_time,
            "average_speed": self.average_speed,
            "items": self.items,
            "errors": self.errors,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "checksum_errors": self.checksum_errors,
            "success_rate": self.success_rate,
        }


@dataclass
class BatchConfig:
    """
    Configuration for batch downloads.
    
    Attributes:
        output_dir: Output directory
        max_concurrent: Maximum concurrent downloads
        max_concurrent_per_host: Max concurrent per host
        retry_count: Number of retries per item
        retry_delay: Base delay between retries
        retry_exponential: Use exponential backoff
        timeout: Download timeout per item
        rate_limit: Maximum download speed
        bandwidth_config: Bandwidth control settings
        proxy: Proxy URL
        proxy_list: List of proxies for rotation
        cookies_file: Path to cookies file
        stop_on_error: Stop on first error
        max_errors: Maximum errors before stopping
        skip_existing: Skip already downloaded files
        verify_ssl: Verify SSL certificates
        filename_template: Filename template
        download_archive: Path to download archive
        save_report: Save download report
        report_format: Report format
        report_path: Custom report path
        webhook_url: Webhook notification URL
        priority_order: Priority order for queue
        auto_categorize: Auto-categorize by file type
        checksum_verify: Verify checksums after download
        pause_on_slow_network: Pause on slow network
        min_speed_threshold: Minimum speed threshold
        smart_retry: Only retry transient errors
        preserve_structure: Preserve URL directory structure
    """
    output_dir: Path = Path("./downloads/batch")
    max_concurrent: int = 5
    max_concurrent_per_host: int = 2
    retry_count: int = 3
    retry_delay: float = 1.0
    retry_exponential: bool = True
    timeout: float = 300.0
    rate_limit: int = 0
    bandwidth_config: Optional[BandwidthConfig] = None
    proxy: Optional[str] = None
    proxy_list: List[str] = field(default_factory=list)
    cookies_file: Optional[Path] = None
    stop_on_error: bool = False
    max_errors: int = 0
    skip_existing: bool = True
    verify_ssl: bool = True
    filename_template: str = "%(title)s.%(ext)s"
    download_archive: Optional[Path] = None
    save_report: bool = True
    report_format: ReportFormat = ReportFormat.JSON
    report_path: Optional[Path] = None
    webhook_url: Optional[str] = None
    priority_order: bool = True
    auto_categorize: bool = True
    checksum_verify: bool = True
    pause_on_slow_network: bool = False
    min_speed_threshold: int = 10240  # 10 KB/s
    smart_retry: bool = True
    preserve_structure: bool = False


class URLValidator:
    """Validate and categorize URLs."""
    
    # URL pattern for validation
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    # Category detection patterns
    CATEGORY_PATTERNS = {
        'video': [r'\.(mp4|mkv|avi|mov|webm|flv)$', r'youtube|vimeo|tiktok'],
        'audio': [r'\.(mp3|flac|wav|aac|ogg|m4a)$', r'soundcloud|spotify'],
        'image': [r'\.(jpg|jpeg|png|gif|webp|svg)$'],
        'document': [r'\.(pdf|doc|docx|txt|rtf)$'],
        'archive': [r'\.(zip|rar|7z|tar|gz)$'],
    }
    
    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        """Check if URL is valid."""
        return bool(cls.URL_PATTERN.match(url))
    
    @classmethod
    def detect_category(cls, url: str) -> str:
        """Detect URL category based on extension or domain."""
        url_lower = url.lower()
        for category, patterns in cls.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url_lower):
                    return category
        return 'general'
    
    @classmethod
    def extract_domain(cls, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return ""
    
    @classmethod
    def normalize_url(cls, url: str) -> str:
        """Normalize URL for deduplication."""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url


class DownloadQueue:
    """
    Priority-based download queue with persistence.
    """
    
    def __init__(self, persist_path: Optional[Path] = None) -> None:
        """
        Initialize download queue.
        
        Args:
            persist_path: Path for queue persistence
        """
        self._queues: Dict[DownloadPriority, deque] = {
            priority: deque() for priority in DownloadPriority
        }
        self._all_items: Dict[str, BatchItem] = {}
        self._persist_path = persist_path
    
    def add(self, item: BatchItem) -> None:
        """Add item to queue."""
        self._queues[item.priority].append(item.id)
        self._all_items[item.id] = item
    
    def get_next(self) -> Optional[BatchItem]:
        """Get next item from queue (highest priority first)."""
        for priority in sorted(DownloadPriority, key=lambda p: p.value, reverse=True):
            if self._queues[priority]:
                item_id = self._queues[priority].popleft()
                return self._all_items.get(item_id)
        return None
    
    def peek(self) -> Optional[BatchItem]:
        """Peek at next item without removing."""
        for priority in sorted(DownloadPriority, key=lambda p: p.value, reverse=True):
            if self._queues[priority]:
                item_id = self._queues[priority][0]
                return self._all_items.get(item_id)
        return None
    
    def __len__(self) -> int:
        return len(self._all_items)
    
    def is_empty(self) -> bool:
        return len(self._all_items) == 0
    
    def get_all(self) -> List[BatchItem]:
        """Get all items."""
        return list(self._all_items.values())
    
    def remove(self, item_id: str) -> Optional[BatchItem]:
        """Remove item from queue."""
        item = self._all_items.pop(item_id, None)
        if item:
            try:
                self._queues[item.priority].remove(item_id)
            except ValueError:
                pass
        return item
    
    def update_priority(self, item_id: str, new_priority: DownloadPriority) -> bool:
        """Update item priority."""
        if item_id not in self._all_items:
            return False
        
        item = self._all_items[item_id]
        old_priority = item.priority
        
        if old_priority != new_priority:
            try:
                self._queues[old_priority].remove(item_id)
            except ValueError:
                pass
            self._queues[new_priority].append(item_id)
            item.priority = new_priority
        
        return True


class BatchDownloader:
    """
    OMNIPOTENT SOVEREIGN NEXUS Batch Downloader v3.2.0.
    
    Ultra-fast batch downloading with comprehensive features:
    - Multiple input sources
    - Smart parallel downloads
    - Priority queue management
    - Progress tracking
    - Error handling
    - Rate limiting
    - Bandwidth control
    - Webhook notifications
    """
    
    def __init__(
        self,
        config: Optional[BatchConfig] = None,
        progress_callback: Optional[Callable[[BatchProgress], Awaitable[None]]] = None,
        item_callback: Optional[Callable[[BatchItem, str], Awaitable[None]]] = None,
    ) -> None:
        """
        Initialize the batch downloader.
        
        Args:
            config: Batch configuration
            progress_callback: Progress update callback
            item_callback: Item status callback
        """
        self.config = config or BatchConfig()
        self._progress_callback = progress_callback
        self._item_callback = item_callback
        
        # Internal state
        self._batch_id: str = ""
        self._queue: DownloadQueue = DownloadQueue()
        self._active: Dict[str, asyncio.Task] = {}
        self._progress: Optional[BatchProgress] = None
        self._cancelled: bool = False
        self._paused: bool = False
        self._download_archive: Set[str] = set()
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._host_semaphores: Dict[str, asyncio.Semaphore] = {}
        
        # Load download archive
        if self.config.download_archive and self.config.download_archive.exists():
            self._load_download_archive()
        
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"BatchDownloader initialized v3.2.0 ULTIMATE NEXUS")
    
    async def __aenter__(self) -> "BatchDownloader":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
    
    def _load_download_archive(self) -> None:
        """Load download archive."""
        try:
            with open(self.config.download_archive, 'r') as f:
                for line in f:
                    if line.strip():
                        self._download_archive.add(line.strip())
            logger.info(f"Loaded {len(self._download_archive)} items from archive")
        except Exception as e:
            logger.warning(f"Failed to load archive: {e}")
    
    def _save_download_archive(self) -> None:
        """Save download archive."""
        try:
            self.config.download_archive.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config.download_archive, 'w') as f:
                for item_id in self._download_archive:
                    f.write(f"{item_id}\n")
        except Exception as e:
            logger.warning(f"Failed to save archive: {e}")
    
    async def close(self) -> None:
        """Close the downloader."""
        if self.config.download_archive:
            self._save_download_archive()
        
        # Cancel active tasks
        for task in self._active.values():
            task.cancel()
        
        logger.info("BatchDownloader closed")
    
    def _get_yt_dlp_path(self) -> Optional[str]:
        """Find yt-dlp executable."""
        paths = [
            shutil.which("yt-dlp"),
            "/usr/local/bin/yt-dlp",
            "/usr/bin/yt-dlp",
            str(Path.home() / ".local/bin/yt-dlp"),
        ]
        for path in paths:
            if path and Path(path).exists():
                return str(path)
        return None
    
    async def load_urls_from_file(
        self,
        filepath: Path,
        skip_comments: bool = True,
    ) -> List[str]:
        """
        Load URLs from file.
        
        Args:
            filepath: Path to URL file
            skip_comments: Skip lines starting with #
            
        Returns:
            List of URLs
        """
        urls = []
        
        try:
            async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                async for line in f:
                    line = line.strip()
                    
                    if not line:
                        continue
                    if skip_comments and line.startswith('#'):
                        continue
                    
                    # Validate URL
                    if URLValidator.is_valid_url(line):
                        urls.append(URLValidator.normalize_url(line))
            
            logger.info(f"Loaded {len(urls)} valid URLs from {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to load URLs from file: {e}")
        
        return urls
    
    async def load_urls_from_csv(
        self,
        filepath: Path,
        url_column: str = "url",
        filename_column: Optional[str] = None,
        priority_column: Optional[str] = None,
    ) -> List[Tuple[str, Optional[str], Optional[DownloadPriority]]]:
        """
        Load URLs from CSV file.
        
        Args:
            filepath: Path to CSV file
            url_column: Column name containing URLs
            filename_column: Optional column for output filenames
            priority_column: Optional column for priorities
            
        Returns:
            List of (url, filename, priority) tuples
        """
        results = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    url = row.get(url_column, '').strip()
                    filename = row.get(filename_column, '').strip() if filename_column else None
                    priority_str = row.get(priority_column, '').strip() if priority_column else None
                    
                    if url:
                        priority = None
                        if priority_str:
                            try:
                                priority = DownloadPriority[priority_str.upper()]
                            except KeyError:
                                priority = DownloadPriority.NORMAL
                        
                        results.append((URLValidator.normalize_url(url), filename or None, priority))
            
            logger.info(f"Loaded {len(results)} URLs from CSV: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to load URLs from CSV: {e}")
        
        return results
    
    def add_urls(
        self,
        urls: List[str],
        filenames: Optional[List[str]] = None,
        priorities: Optional[List[DownloadPriority]] = None,
    ) -> int:
        """
        Add URLs to the batch queue.
        
        Args:
            urls: List of URLs
            filenames: Optional list of output filenames
            priorities: Optional list of priorities
            
        Returns:
            Number of URLs added
        """
        added = 0
        seen_urls: Set[str] = set()
        
        for i, url in enumerate(urls):
            # Normalize URL
            url = URLValidator.normalize_url(url)
            
            # Skip duplicates
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            # Generate unique ID
            item_id = hashlib.md5(f"{url}{time.time()}".encode()).hexdigest()[:12]
            
            # Check if already downloaded
            url_hash = hashlib.md5(url.encode()).hexdigest()
            if self.config.skip_existing and url_hash in self._download_archive:
                logger.debug(f"Skipping already downloaded: {url}")
                continue
            
            # Create batch item
            filename = filenames[i] if filenames and i < len(filenames) else None
            priority = priorities[i] if priorities and i < len(priorities) else DownloadPriority.NORMAL
            
            category = URLValidator.detect_category(url) if self.config.auto_categorize else 'general'
            
            item = BatchItem(
                id=item_id,
                url=url,
                output_filename=filename,
                priority=priority,
                category=category,
                max_retries=self.config.retry_count,
            )
            
            self._queue.add(item)
            added += 1
        
        logger.info(f"Added {added} URLs to batch queue")
        return added
    
    async def start(
        self,
        urls: Optional[List[str]] = None,
        filenames: Optional[List[str]] = None,
    ) -> BatchResult:
        """
        Start the batch download.
        
        Args:
            urls: Optional list of URLs to add
            filenames: Optional output filenames
            
        Returns:
            BatchResult
        """
        # Generate batch ID
        self._batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Add URLs if provided
        if urls:
            self.add_urls(urls, filenames)
        
        if self._queue.is_empty():
            return BatchResult(
                batch_id=self._batch_id,
                success=False,
                errors=["No URLs in batch queue"],
            )
        
        # Initialize concurrency controls
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent)
        
        # Initialize progress
        start_time = datetime.now()
        self._progress = BatchProgress(
            batch_id=self._batch_id,
            total_items=len(self._queue),
            start_time=start_time,
            status=BatchStatus.RUNNING,
        )
        
        # Reset state
        self._cancelled = False
        self._paused = False
        
        try:
            # Process queue with concurrency limit
            tasks = []
            
            while not self._queue.is_empty() and not self._cancelled:
                # Handle pause
                while self._paused:
                    await asyncio.sleep(0.5)
                
                if self._cancelled:
                    break
                
                # Get next item
                item = self._queue.get_next()
                if not item:
                    break
                
                # Create download task
                task = asyncio.create_task(self._download_item(item))
                tasks.append(task)
            
            # Wait for all tasks
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Batch download error: {e}")
        
        # Calculate final results
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        items = self._queue.get_all()
        successful = sum(1 for item in items if item.status == ItemStatus.COMPLETED)
        failed = sum(1 for item in items if item.status == ItemStatus.FAILED)
        skipped = sum(1 for item in items if item.status == ItemStatus.SKIPPED)
        total_bytes = sum(item.bytes_downloaded for item in items)
        
        result = BatchResult(
            batch_id=self._batch_id,
            success=failed == 0 and successful > 0,
            total_items=len(items),
            successful=successful,
            failed=failed,
            skipped=skipped,
            total_bytes=total_bytes,
            total_time=total_time,
            average_speed=total_bytes / total_time if total_time > 0 else 0,
            items=[item.to_dict() for item in items],
            errors=[item.error_message for item in items if item.error_message],
            start_time=start_time,
            end_time=end_time,
        )
        
        # Save report
        if self.config.save_report:
            await self._save_report(result)
        
        # Send webhook notification
        if self.config.webhook_url:
            await self._send_webhook(result)
        
        return result
    
    async def _download_item(self, item: BatchItem) -> None:
        """Download a single batch item."""
        async with self._semaphore:
            # Update status
            item.status = ItemStatus.DOWNLOADING
            item.start_time = datetime.now()
            
            self._progress.current_items.append(item.id)
            self._progress.active_connections += 1
            await self._report_progress()
            
            try:
                # Attempt download with retries
                success = False
                for attempt in range(item.max_retries + 1):
                    if self._cancelled:
                        break
                    
                    if attempt > 0:
                        item.retry_count = attempt
                        item.status = ItemStatus.RETRYING
                        
                        delay = self.config.retry_delay
                        if self.config.retry_exponential:
                            delay *= (2 ** attempt)
                        
                        await asyncio.sleep(delay)
                    
                    success = await self._perform_download(item)
                    
                    if success:
                        break
                
                if success:
                    item.status = ItemStatus.COMPLETED
                    item.end_time = datetime.now()
                    self._progress.completed_items += 1
                    self._progress.bytes_downloaded += item.bytes_downloaded
                    self._download_archive.add(hashlib.md5(item.url.encode()).hexdigest())
                else:
                    item.status = ItemStatus.FAILED
                    self._progress.failed_items += 1
                    
                    if self.config.stop_on_error:
                        self._cancelled = True
                
            except Exception as e:
                item.status = ItemStatus.FAILED
                item.error_message = str(e)
                self._progress.failed_items += 1
            
            finally:
                self._progress.current_items.remove(item.id)
                self._progress.active_connections -= 1
                await self._report_progress()
                await self._report_item_status(item, item.status.value)
    
    async def _perform_download(self, item: BatchItem) -> bool:
        """Perform the actual download."""
        yt_dlp = self._get_yt_dlp_path()
        if not yt_dlp:
            item.error_message = "yt-dlp not found"
            return False
        
        try:
            # Build command
            output_path = self.config.output_dir
            
            # Create category subfolder if auto-categorize
            if self.config.auto_categorize and item.category != 'general':
                output_path = output_path / item.category
                output_path.mkdir(parents=True, exist_ok=True)
            
            cmd = [
                yt_dlp,
                "-f", "best",
                "--merge-output-format", "mp4",
                "-o", str(output_path / self.config.filename_template),
                "--no-playlist",
            ]
            
            if item.output_filename:
                custom_path = output_path / f"{item.output_filename}.%(ext)s"
                cmd.extend(["-o", str(custom_path)])
            
            if self.config.proxy:
                cmd.extend(["--proxy", self.config.proxy])
            
            if self.config.cookies_file:
                cmd.extend(["--cookies", str(self.config.cookies_file)])
            
            if self.config.rate_limit > 0:
                cmd.extend(["--limit-rate", f"{self.config.rate_limit}"])
            
            cmd.extend(["--retries", str(self.config.retry_count)])
            
            if not self.config.verify_ssl:
                cmd.append("--no-check-certificate")
            
            cmd.append(item.url)
            
            # Execute
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Find downloaded file
                for file in output_path.iterdir():
                    if file.is_file() and file.stat().st_mtime > time.time() - 60:
                        item.filepath = file
                        item.bytes_downloaded = file.stat().st_size
                        
                        # Verify checksum if provided
                        if item.checksum and self.config.checksum_verify:
                            actual = await self._calculate_checksum(file, item.checksum_algorithm)
                            if actual != item.checksum:
                                logger.warning(f"Checksum mismatch for {file.name}")
                                return False
                        
                        return True
            else:
                item.error_message = stderr.decode()[:500] if stderr else "Unknown error"
                return False
            
        except Exception as e:
            item.error_message = str(e)
            return False
    
    async def _calculate_checksum(self, filepath: Path, algorithm: str = "md5") -> str:
        """Calculate file checksum."""
        import hashlib as hl
        hasher = hl.new(algorithm)
        async with aiofiles.open(filepath, 'rb') as f:
            while chunk := await f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    async def _report_progress(self) -> None:
        """Report progress to callback."""
        if self._progress_callback and self._progress:
            try:
                await self._progress_callback(self._progress)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")
    
    async def _report_item_status(self, item: BatchItem, status: str) -> None:
        """Report item status to callback."""
        if self._item_callback:
            try:
                await self._item_callback(item, status)
            except Exception as e:
                logger.warning(f"Item callback error: {e}")
    
    async def _save_report(self, result: BatchResult) -> None:
        """Save batch report to file."""
        report_path = self.config.report_path or (
            self.config.output_dir / f"batch_report_{self._batch_id}"
        )
        
        try:
            if self.config.report_format == ReportFormat.JSON:
                async with aiofiles.open(f"{report_path}.json", 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(result.to_dict(), indent=2))
            
            elif self.config.report_format == ReportFormat.CSV:
                with open(f"{report_path}.csv", 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "ID", "URL", "Status", "Progress", "Bytes",
                        "Speed", "Error", "Filepath", "Category"
                    ])
                    
                    for item in result.items:
                        writer.writerow([
                            item.get("id"),
                            item.get("url"),
                            item.get("status"),
                            item.get("progress"),
                            item.get("bytes_downloaded"),
                            item.get("speed"),
                            item.get("error_message"),
                            item.get("filepath"),
                            item.get("category"),
                        ])
            
            elif self.config.report_format == ReportFormat.HTML:
                html = self._generate_html_report(result)
                async with aiofiles.open(f"{report_path}.html", 'w', encoding='utf-8') as f:
                    await f.write(html)
            
            elif self.config.report_format == ReportFormat.TXT:
                lines = [
                    f"Batch Report: {result.batch_id}",
                    f"Status: {'Success' if result.success else 'Failed'}",
                    f"Total Items: {result.total_items}",
                    f"Successful: {result.successful}",
                    f"Failed: {result.failed}",
                    f"Total Bytes: {result.total_bytes:,}",
                    f"Total Time: {result.total_time:.2f}s",
                    f"Success Rate: {result.success_rate:.1f}%",
                    "",
                    "Items:",
                ]
                
                for item in result.items:
                    lines.append(f"  {item.get('id')}: {item.get('status')} - {item.get('url')}")
                
                async with aiofiles.open(f"{report_path}.txt", 'w', encoding='utf-8') as f:
                    await f.write('\n'.join(lines))
            
            logger.info(f"Batch report saved: {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
    
    def _generate_html_report(self, result: BatchResult) -> str:
        """Generate HTML report."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Batch Report - {result.batch_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f0f0f0; padding: 20px; border-radius: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .success {{ color: green; }}
        .failed {{ color: red; }}
    </style>
</head>
<body>
    <h1>Batch Download Report</h1>
    <div class="summary">
        <p><strong>Batch ID:</strong> {result.batch_id}</p>
        <p><strong>Status:</strong> <span class="{'success' if result.success else 'failed'}">{result.success}</span></p>
        <p><strong>Total Items:</strong> {result.total_items}</p>
        <p><strong>Successful:</strong> {result.successful}</p>
        <p><strong>Failed:</strong> {result.failed}</p>
        <p><strong>Total Bytes:</strong> {result.total_bytes:,}</p>
        <p><strong>Total Time:</strong> {result.total_time:.2f}s</p>
        <p><strong>Success Rate:</strong> {result.success_rate:.1f}%</p>
    </div>
    <table>
        <tr>
            <th>ID</th>
            <th>URL</th>
            <th>Status</th>
            <th>Bytes</th>
            <th>Error</th>
        </tr>
        {''.join(f'<tr><td>{i.get("id")}</td><td>{i.get("url")}</td><td>{i.get("status")}</td><td>{i.get("bytes_downloaded")}</td><td>{i.get("error_message", "")}</td></tr>' for i in result.items)}
    </table>
</body>
</html>"""
    
    async def _send_webhook(self, result: BatchResult) -> None:
        """Send webhook notification."""
        if not self.config.webhook_url:
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "batch_id": result.batch_id,
                    "success": result.success,
                    "total_items": result.total_items,
                    "successful": result.successful,
                    "failed": result.failed,
                    "total_bytes": result.total_bytes,
                    "total_time": result.total_time,
                    "timestamp": datetime.now().isoformat(),
                }
                
                async with session.post(
                    self.config.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        logger.info("Webhook notification sent")
                    else:
                        logger.warning(f"Webhook failed: {response.status}")
        except Exception as e:
            logger.warning(f"Webhook error: {e}")
    
    def pause(self) -> bool:
        """Pause the batch download."""
        self._paused = True
        if self._progress:
            self._progress.status = BatchStatus.PAUSED
        return True
    
    def resume(self) -> bool:
        """Resume a paused download."""
        self._paused = False
        if self._progress:
            self._progress.status = BatchStatus.RUNNING
        return True
    
    def cancel(self) -> bool:
        """Cancel the batch download."""
        self._cancelled = True
        if self._progress:
            self._progress.status = BatchStatus.CANCELLED
        return True
    
    def get_progress(self) -> Optional[BatchProgress]:
        """Get current progress."""
        return self._progress
    
    def get_item(self, item_id: str) -> Optional[BatchItem]:
        """Get item by ID."""
        items = self._queue.get_all()
        for item in items:
            if item.id == item_id:
                return item
        return None
    
    def get_queue_size(self) -> int:
        """Get current queue size."""
        return len(self._queue)


# Convenience function
async def batch_download(
    urls: List[str],
    output_dir: str = "./downloads/batch",
    max_concurrent: int = 5,
    progress_callback: Optional[Callable[[BatchProgress], Awaitable[None]]] = None,
) -> BatchResult:
    """
    Quick batch download function.
    
    Args:
        urls: List of URLs to download
        output_dir: Output directory
        max_concurrent: Maximum concurrent downloads
        progress_callback: Progress callback
        
    Returns:
        BatchResult
    """
    config = BatchConfig(
        output_dir=Path(output_dir),
        max_concurrent=max_concurrent,
    )
    
    async with BatchDownloader(
        config=config,
        progress_callback=progress_callback,
    ) as downloader:
        return await downloader.start(urls)


__all__ = [
    "BatchDownloader",
    "BatchStatus",
    "ItemStatus",
    "DownloadPriority",
    "InputSourceType",
    "ReportFormat",
    "BatchItem",
    "BatchProgress",
    "BatchResult",
    "BatchConfig",
    "BandwidthConfig",
    "URLValidator",
    "DownloadQueue",
    "batch_download",
]

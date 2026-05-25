"""
OMNIPOTENT SOVEREIGN NEXUS - Batch Downloader Module
Version: v3.0.1 ULTIMATE NEXUS

Advanced batch downloading with support for:
- Multiple URL sources (file, list, API)
- Parallel downloads with configurable concurrency
- Progress tracking and reporting
- Error handling and retry mechanisms
- Rate limiting and bandwidth control
- Scheduling and automation
- Download queue management
- Statistics and reporting

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
)
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import subprocess


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)


class BatchStatus(Enum):
    """Batch job status."""
    
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ItemStatus(Enum):
    """Individual item status."""
    
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class InputSourceType(Enum):
    """Source type for batch URLs."""
    
    FILE = "file"
    LIST = "list"
    URL = "url"
    API = "api"
    STDIN = "stdin"


@dataclass
class BatchItem:
    """
    Individual batch download item.
    
    Attributes:
        id: Unique item ID
        url: Download URL
        output_filename: Output filename
        status: Current status
        progress: Download progress percentage
        bytes_downloaded: Bytes downloaded
        total_bytes: Total bytes
        speed: Current download speed
        error_message: Error message if failed
        retry_count: Number of retries attempted
        start_time: Download start time
        end_time: Download end time
        filepath: Path to downloaded file
        metadata: Additional metadata
    """
    id: str
    url: str
    output_filename: Optional[str] = None
    status: ItemStatus = ItemStatus.QUEUED
    progress: float = 0.0
    bytes_downloaded: int = 0
    total_bytes: int = 0
    speed: float = 0.0
    error_message: Optional[str] = None
    retry_count: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    filepath: Optional[Path] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "url": self.url,
            "output_filename": self.output_filename,
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
            "metadata": self.metadata,
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
        current_item: Current item being processed
        bytes_downloaded: Total bytes downloaded
        total_bytes: Estimated total bytes
        start_time: Batch start time
        elapsed_time: Elapsed time in seconds
        eta: Estimated time remaining
        average_speed: Average download speed
        status: Current batch status
    """
    batch_id: str
    total_items: int = 0
    completed_items: int = 0
    failed_items: int = 0
    skipped_items: int = 0
    current_item: Optional[str] = None
    bytes_downloaded: int = 0
    total_bytes: int = 0
    start_time: Optional[datetime] = None
    elapsed_time: float = 0.0
    eta: float = 0.0
    average_speed: float = 0.0
    status: BatchStatus = BatchStatus.PENDING
    
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "batch_id": self.batch_id,
            "total_items": self.total_items,
            "completed_items": self.completed_items,
            "failed_items": self.failed_items,
            "skipped_items": self.skipped_items,
            "current_item": self.current_item,
            "bytes_downloaded": self.bytes_downloaded,
            "total_bytes": self.total_bytes,
            "elapsed_time": self.elapsed_time,
            "eta": self.eta,
            "percentage": self.percentage,
            "average_speed": self.average_speed,
            "success_rate": self.success_rate,
            "status": self.status.value,
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
        items: Individual item results
        errors: List of error messages
        start_time: Batch start time
        end_time: Batch end time
    """
    batch_id: str
    success: bool = False
    total_items: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    total_bytes: int = 0
    total_time: float = 0.0
    items: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
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
            "items": self.items,
            "errors": self.errors,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "success_rate": self.success_rate,
        }


@dataclass
class BatchConfig:
    """
    Configuration for batch downloads.
    
    Attributes:
        output_dir: Output directory
        max_concurrent: Maximum concurrent downloads
        retry_count: Number of retries per item
        retry_delay: Base delay between retries
        timeout: Download timeout per item
        rate_limit: Maximum download speed
        proxy: Proxy URL
        cookies_file: Path to cookies file
        stop_on_error: Stop on first error
        max_errors: Maximum errors before stopping
        skip_existing: Skip already downloaded files
        verify_ssl: Verify SSL certificates
        filename_template: Filename template
        download_archive: Path to download archive
        save_report: Save download report
        report_format: Report format (json, csv, txt)
        schedule_time: Scheduled start time
        repeat_interval: Repeat interval in seconds
    """
    output_dir: Path = Path("./downloads/batch")
    max_concurrent: int = 3
    retry_count: int = 3
    retry_delay: float = 1.0
    timeout: float = 300.0
    rate_limit: int = 0
    proxy: Optional[str] = None
    cookies_file: Optional[Path] = None
    stop_on_error: bool = False
    max_errors: int = 0
    skip_existing: bool = True
    verify_ssl: bool = True
    filename_template: str = "%(title)s.%(ext)s"
    download_archive: Optional[Path] = None
    save_report: bool = True
    report_format: str = "json"
    schedule_time: Optional[datetime] = None
    repeat_interval: int = 0


class BatchDownloader:
    """
    OMNIPOTENT SOVEREIGN NEXUS Batch Downloader.
    
    Advanced batch downloading with comprehensive features:
    - Multiple input sources
    - Parallel downloads
    - Progress tracking
    - Error handling
    - Rate limiting
    - Scheduling
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
        self._items: Dict[str, BatchItem] = {}
        self._queue: deque = deque()
        self._active: Set[str] = set()
        self._progress: Optional[BatchProgress] = None
        self._cancelled: bool = False
        self._paused: bool = False
        self._download_archive: Set[str] = set()
        
        # Load download archive
        if self.config.download_archive and self.config.download_archive.exists():
            self._load_download_archive()
        
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"BatchDownloader initialized v3.0.1 ULTIMATE NEXUS")
    
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
        logger.info("BatchDownloader closed")
    
    def _get_yt_dlp_path(self) -> Optional[str]:
        """Find yt-dlp executable."""
        paths = [
            shutil.which("yt-dlp"),
            "/usr/local/bin/yt-dlp",
            "/usr/bin/yt-dlp",
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
                    
                    # Skip empty lines and comments
                    if not line:
                        continue
                    if skip_comments and line.startswith('#'):
                        continue
                    
                    urls.append(line)
            
            logger.info(f"Loaded {len(urls)} URLs from {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to load URLs from file: {e}")
        
        return urls
    
    async def load_urls_from_csv(
        self,
        filepath: Path,
        url_column: str = "url",
        filename_column: Optional[str] = None,
    ) -> List[Tuple[str, Optional[str]]]:
        """
        Load URLs from CSV file.
        
        Args:
            filepath: Path to CSV file
            url_column: Column name containing URLs
            filename_column: Optional column for output filenames
            
        Returns:
            List of (url, filename) tuples
        """
        results = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    url = row.get(url_column, '').strip()
                    filename = row.get(filename_column, '').strip() if filename_column else None
                    
                    if url:
                        results.append((url, filename or None))
            
            logger.info(f"Loaded {len(results)} URLs from CSV: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to load URLs from CSV: {e}")
        
        return results
    
    def add_urls(
        self,
        urls: List[str],
        filenames: Optional[List[str]] = None,
    ) -> int:
        """
        Add URLs to the batch queue.
        
        Args:
            urls: List of URLs
            filenames: Optional list of output filenames
            
        Returns:
            Number of URLs added
        """
        added = 0
        
        for i, url in enumerate(urls):
            # Generate unique ID
            item_id = f"item_{len(self._items) + 1:04d}"
            
            # Check if already downloaded
            url_hash = self._hash_url(url)
            if self.config.skip_existing and url_hash in self._download_archive:
                logger.debug(f"Skipping already downloaded: {url}")
                continue
            
            # Create batch item
            filename = filenames[i] if filenames and i < len(filenames) else None
            
            item = BatchItem(
                id=item_id,
                url=url,
                output_filename=filename,
            )
            
            self._items[item_id] = item
            self._queue.append(item_id)
            added += 1
        
        logger.info(f"Added {added} URLs to batch queue")
        return added
    
    def _hash_url(self, url: str) -> str:
        """Generate hash for URL."""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()
    
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
        
        if not self._items:
            return BatchResult(
                batch_id=self._batch_id,
                success=False,
                errors=["No URLs in batch queue"],
            )
        
        # Initialize progress
        start_time = datetime.now()
        self._progress = BatchProgress(
            batch_id=self._batch_id,
            total_items=len(self._items),
            start_time=start_time,
            status=BatchStatus.RUNNING,
        )
        
        # Reset state
        self._cancelled = False
        self._paused = False
        
        try:
            # Process queue with concurrency limit
            semaphore = asyncio.Semaphore(self.config.max_concurrent)
            tasks = []
            
            while self._queue and not self._cancelled:
                # Handle pause
                while self._paused:
                    await asyncio.sleep(0.5)
                
                if self._cancelled:
                    break
                
                item_id = self._queue.popleft()
                task = asyncio.create_task(
                    self._download_item(item_id, semaphore)
                )
                tasks.append(task)
            
            # Wait for all tasks
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Batch download error: {e}")
        
        # Calculate final results
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        successful = sum(1 for item in self._items.values() if item.status == ItemStatus.COMPLETED)
        failed = sum(1 for item in self._items.values() if item.status == ItemStatus.FAILED)
        skipped = sum(1 for item in self._items.values() if item.status == ItemStatus.SKIPPED)
        total_bytes = sum(item.bytes_downloaded for item in self._items.values())
        
        result = BatchResult(
            batch_id=self._batch_id,
            success=failed == 0 and successful > 0,
            total_items=len(self._items),
            successful=successful,
            failed=failed,
            skipped=skipped,
            total_bytes=total_bytes,
            total_time=total_time,
            items=[item.to_dict() for item in self._items.values()],
            errors=[item.error_message for item in self._items.values() if item.error_message],
            start_time=start_time,
            end_time=end_time,
        )
        
        # Save report
        if self.config.save_report:
            await self._save_report(result)
        
        return result
    
    async def _download_item(
        self,
        item_id: str,
        semaphore: asyncio.Semaphore,
    ) -> None:
        """Download a single batch item."""
        item = self._items[item_id]
        
        async with semaphore:
            # Update status
            item.status = ItemStatus.DOWNLOADING
            item.start_time = datetime.now()
            
            self._active.add(item_id)
            self._progress.current_item = item.url
            await self._report_progress()
            
            try:
                # Attempt download with retries
                success = False
                for attempt in range(self.config.retry_count + 1):
                    if self._cancelled:
                        break
                    
                    if attempt > 0:
                        item.retry_count = attempt
                        item.status = ItemStatus.RETRYING
                        await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
                    
                    success = await self._perform_download(item)
                    
                    if success:
                        break
                
                if success:
                    item.status = ItemStatus.COMPLETED
                    item.end_time = datetime.now()
                    self._progress.completed_items += 1
                    self._download_archive.add(self._hash_url(item.url))
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
                self._active.discard(item_id)
                self._progress.bytes_downloaded += item.bytes_downloaded
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
            output_path = self.config.output_dir / self.config.filename_template
            
            cmd = [
                yt_dlp,
                "-f", "bestvideo+bestaudio/best",
                "--merge-output-format", "mp4",
                "-o", str(output_path),
                "--no-playlist",
            ]
            
            if item.output_filename:
                custom_path = self.config.output_dir / f"{item.output_filename}.%(ext)s"
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
                for file in self.config.output_dir.iterdir():
                    if file.is_file() and file.stat().st_mtime > time.time() - 60:
                        item.filepath = file
                        item.bytes_downloaded = file.stat().st_size
                        break
                
                return True
            else:
                item.error_message = stderr.decode()[:500] if stderr else "Unknown error"
                return False
            
        except Exception as e:
            item.error_message = str(e)
            return False
    
    async def _report_progress(self) -> None:
        """Report progress to callback."""
        if self._progress_callback and self._progress:
            try:
                await self._progress_callback(self._progress)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")
    
    async def _report_item_status(
        self,
        item: BatchItem,
        status: str,
    ) -> None:
        """Report item status to callback."""
        if self._item_callback:
            try:
                await self._item_callback(item, status)
            except Exception as e:
                logger.warning(f"Item callback error: {e}")
    
    async def _save_report(self, result: BatchResult) -> None:
        """Save batch report to file."""
        report_path = self.config.output_dir / f"batch_report_{self._batch_id}"
        
        try:
            if self.config.report_format == "json":
                async with aiofiles.open(f"{report_path}.json", 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(result.to_dict(), indent=2))
            
            elif self.config.report_format == "csv":
                with open(f"{report_path}.csv", 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "ID", "URL", "Status", "Progress", "Bytes",
                        "Speed", "Error", "Filepath"
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
                        ])
            
            elif self.config.report_format == "txt":
                async with aiofiles.open(f"{report_path}.txt", 'w', encoding='utf-8') as f:
                    lines = [
                        f"Batch Report: {result.batch_id}",
                        f"Status: {'Success' if result.success else 'Failed'}",
                        f"Total Items: {result.total_items}",
                        f"Successful: {result.successful}",
                        f"Failed: {result.failed}",
                        f"Skipped: {result.skipped}",
                        f"Total Bytes: {result.total_bytes:,}",
                        f"Total Time: {result.total_time:.2f}s",
                        f"Success Rate: {result.success_rate:.1f}%",
                        "",
                        "Items:",
                    ]
                    
                    for item in result.items:
                        lines.append(f"  {item.get('id')}: {item.get('status')} - {item.get('url')}")
                    
                    await f.write('\n'.join(lines))
            
            logger.info(f"Batch report saved: {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
    
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
        return self._items.get(item_id)
    
    def get_all_items(self) -> Dict[str, BatchItem]:
        """Get all items."""
        return self._items.copy()


# Convenience function
async def batch_download(
    urls: List[str],
    output_dir: str = "./downloads/batch",
    max_concurrent: int = 3,
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
    "InputSourceType",
    "BatchItem",
    "BatchProgress",
    "BatchResult",
    "BatchConfig",
    "batch_download",
]

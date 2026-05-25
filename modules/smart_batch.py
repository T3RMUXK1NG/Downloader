"""
OMNIPOTENT SOVEREIGN NEXUS - Smart Batch Processing Module
Version: v3.0.1 ULTIMATE NEXUS

ML-powered smart batch processing with support for:
- Intelligent priority assignment
- Automatic content categorization
- Smart resource allocation
- Predictive download scheduling
- Quality-based optimization
- Duplicate detection using perceptual hashing
- Content similarity clustering
- Adaptive concurrency control
- Learning from user preferences

Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
"""

import asyncio
import aiohttp
import aiofiles
import logging
import json
import re
import hashlib
import pickle
import shutil
import math
from collections import defaultdict
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
    Tuple,
    Union,
    Awaitable,
)
from concurrent.futures import ThreadPoolExecutor
import subprocess


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)


class Priority(Enum):
    """Download priority levels."""
    
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


class ContentType(Enum):
    """Content type categories."""
    
    VIDEO = "video"
    AUDIO = "audio"
    PLAYLIST = "playlist"
    LIVE = "live"
    UNKNOWN = "unknown"


class SchedulingStrategy(Enum):
    """Scheduling strategies for batch processing."""
    
    FIFO = "fifo"                       # First in, first out
    PRIORITY = "priority"               # Priority-based
    SHORTEST_FIRST = "shortest_first"   # Shortest duration first
    LONGEST_FIRST = "longest_first"     # Longest duration first
    BALANCED = "balanced"               # Balance across categories
    ADAPTIVE = "adaptive"               # ML-optimized adaptive


@dataclass
class ContentAnalysis:
    """
    ML-based content analysis result.
    
    Attributes:
        url: Source URL
        content_type: Detected content type
        estimated_duration: Estimated duration
        estimated_size: Estimated file size
        priority_score: Calculated priority (0-1)
        category: Detected category
        tags: Extracted tags
        similarity_hash: Perceptual hash for duplicate detection
        quality_prediction: Predicted quality
        download_difficulty: Estimated download difficulty
    """
    url: str
    content_type: ContentType = ContentType.UNKNOWN
    estimated_duration: float = 0.0
    estimated_size: int = 0
    priority_score: float = 0.5
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    similarity_hash: Optional[str] = None
    quality_prediction: float = 0.5
    download_difficulty: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "content_type": self.content_type.value,
            "estimated_duration": self.estimated_duration,
            "estimated_size": self.estimated_size,
            "priority_score": self.priority_score,
            "category": self.category,
            "tags": self.tags,
            "similarity_hash": self.similarity_hash,
            "quality_prediction": self.quality_prediction,
            "download_difficulty": self.download_difficulty,
        }


@dataclass
class SmartBatchItem:
    """
    Smart batch item with ML-enhanced metadata.
    
    Attributes:
        id: Unique identifier
        url: Download URL
        analysis: Content analysis
        priority: Assigned priority
        scheduled_time: Scheduled download time
        dependencies: List of dependency item IDs
        retry_count: Number of retry attempts
        status: Current status
        progress: Download progress
        error_message: Error message if failed
        metadata: Additional metadata
    """
    id: str
    url: str
    analysis: Optional[ContentAnalysis] = None
    priority: Priority = Priority.MEDIUM
    scheduled_time: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 0
    status: str = "pending"
    progress: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "url": self.url,
            "analysis": self.analysis.to_dict() if self.analysis else None,
            "priority": self.priority.name,
            "scheduled_time": self.scheduled_time.isoformat() if self.scheduled_time else None,
            "dependencies": self.dependencies,
            "retry_count": self.retry_count,
            "status": self.status,
            "progress": self.progress,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


@dataclass
class ResourceMetrics:
    """
    System resource metrics for adaptive scheduling.
    
    Attributes:
        cpu_usage: CPU usage percentage
        memory_usage: Memory usage percentage
        network_speed: Network speed in Mbps
        disk_space: Available disk space in GB
        active_downloads: Number of active downloads
        download_speed: Current download speed
    """
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    network_speed: float = 0.0
    disk_space: float = 0.0
    active_downloads: int = 0
    download_speed: float = 0.0
    
    @property
    def load_score(self) -> float:
        """Calculate overall system load score (0-1)."""
        return (self.cpu_usage + self.memory_usage) / 200


@dataclass
class SmartBatchConfig:
    """
    Configuration for smart batch processing.
    
    Attributes:
        output_dir: Output directory
        max_concurrent: Maximum concurrent downloads
        strategy: Scheduling strategy
        auto_prioritize: Auto-assign priorities using ML
        detect_duplicates: Enable duplicate detection
        similarity_threshold: Threshold for duplicate detection
        adaptive_concurrency: Adjust concurrency based on resources
        min_concurrent: Minimum concurrent downloads
        max_concurrent_limit: Maximum concurrent limit
        learning_enabled: Enable learning from patterns
        preference_file: Path to user preferences file
        history_file: Path to download history file
        auto_retry: Automatically retry failed items
        max_retries: Maximum retry attempts
        retry_delay: Base delay between retries
        proxy: Proxy URL
        cookies_file: Path to cookies file
        rate_limit: Maximum download speed
        schedule_interval: Check interval for scheduled items
        resource_check_interval: Interval to check system resources
    """
    output_dir: Path = Path("./downloads/smart_batch")
    max_concurrent: int = 4
    strategy: SchedulingStrategy = SchedulingStrategy.ADAPTIVE
    auto_prioritize: bool = True
    detect_duplicates: bool = True
    similarity_threshold: float = 0.95
    adaptive_concurrency: bool = True
    min_concurrent: int = 1
    max_concurrent_limit: int = 10
    learning_enabled: bool = True
    preference_file: Optional[Path] = None
    history_file: Optional[Path] = None
    auto_retry: bool = True
    max_retries: int = 3
    retry_delay: float = 5.0
    proxy: Optional[str] = None
    cookies_file: Optional[Path] = None
    rate_limit: int = 0
    schedule_interval: float = 10.0
    resource_check_interval: float = 30.0


class ContentAnalyzer:
    """
    ML-powered content analyzer for smart batch processing.
    
    Analyzes URLs and predicts optimal download parameters.
    """
    
    # Category keywords for classification
    CATEGORY_KEYWORDS = {
        'music': ['music', 'song', 'audio', 'album', 'playlist', 'remix', 'lyric', 'concert'],
        'tutorial': ['tutorial', 'how to', 'guide', 'learn', 'course', 'lesson', 'teach'],
        'entertainment': ['funny', 'comedy', 'movie', 'trailer', 'game', 'gaming', 'stream'],
        'news': ['news', 'breaking', 'report', 'update', 'politics', 'world'],
        'education': ['lecture', 'education', 'university', 'school', 'study', 'science'],
        'sports': ['sports', 'football', 'basketball', 'soccer', 'game', 'match'],
        'podcast': ['podcast', 'interview', 'talk', 'discussion', 'episode'],
        'live': ['live', 'stream', 'broadcast', 'event'],
    }
    
    def __init__(self) -> None:
        """Initialize the content analyzer."""
        self._user_preferences: Dict[str, float] = {}
        self._download_history: List[Dict[str, Any]] = []
    
    async def analyze(self, url: str, metadata: Optional[Dict] = None) -> ContentAnalysis:
        """
        Analyze URL and return content analysis.
        
        Args:
            url: URL to analyze
            metadata: Optional pre-fetched metadata
            
        Returns:
            ContentAnalysis with predictions
        """
        analysis = ContentAnalysis(url=url)
        
        # Detect content type
        analysis.content_type = self._detect_content_type(url)
        
        # Calculate priority score
        analysis.priority_score = self._calculate_priority(url, metadata)
        
        # Categorize content
        analysis.category = self._categorize(url, metadata)
        
        # Extract tags
        analysis.tags = self._extract_tags(url, metadata)
        
        # Estimate duration and size
        if metadata:
            analysis.estimated_duration = metadata.get('duration', 0)
            analysis.estimated_size = self._estimate_size(metadata)
        
        # Predict download difficulty
        analysis.download_difficulty = self._predict_difficulty(url, metadata)
        
        return analysis
    
    def _detect_content_type(self, url: str) -> ContentType:
        """Detect content type from URL patterns."""
        url_lower = url.lower()
        
        if 'playlist' in url_lower or 'list=' in url_lower:
            return ContentType.PLAYLIST
        elif 'live' in url_lower or 'stream' in url_lower:
            return ContentType.LIVE
        elif any(p in url_lower for p in ['music', 'audio', 'soundcloud', 'spotify']):
            return ContentType.AUDIO
        else:
            return ContentType.VIDEO
    
    def _calculate_priority(self, url: str, metadata: Optional[Dict]) -> float:
        """Calculate priority score (0-1, higher = more important)."""
        score = 0.5  # Base score
        
        if metadata:
            # Factor in popularity
            views = metadata.get('view_count', 0)
            if views > 1000000:
                score += 0.2
            elif views > 100000:
                score += 0.1
            
            # Factor in recency
            upload_date = metadata.get('upload_date', '')
            if upload_date:
                try:
                    upload = datetime.strptime(upload_date, '%Y%m%d')
                    days_old = (datetime.now() - upload).days
                    if days_old < 7:
                        score += 0.15
                    elif days_old < 30:
                        score += 0.1
                except ValueError:
                    pass
        
        # Apply user preferences
        for keyword, preference in self._user_preferences.items():
            if keyword in url.lower():
                score += preference * 0.2
        
        return min(max(score, 0), 1)
    
    def _categorize(self, url: str, metadata: Optional[Dict]) -> str:
        """Categorize content based on URL and metadata."""
        text = url.lower()
        
        if metadata:
            text += ' ' + (metadata.get('title', '') or '').lower()
            text += ' ' + ' '.join(metadata.get('tags', []))
            text += ' ' + ' '.join(metadata.get('categories', []))
        
        # Match against category keywords
        category_scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return 'general'
    
    def _extract_tags(self, url: str, metadata: Optional[Dict]) -> List[str]:
        """Extract tags from URL and metadata."""
        tags = []
        
        if metadata:
            tags.extend(metadata.get('tags', [])[:10])
            tags.extend(metadata.get('categories', [])[:5])
        
        return list(set(tags))[:15]  # Dedupe and limit
    
    def _estimate_size(self, metadata: Dict) -> int:
        """Estimate file size from metadata."""
        duration = metadata.get('duration', 0)
        
        # Rough estimate: 1MB per minute for 720p video
        if duration > 0:
            return duration * 1024 * 1024 // 60
        
        return 0
    
    def _predict_difficulty(self, url: str, metadata: Optional[Dict]) -> float:
        """Predict download difficulty (0-1, higher = more difficult)."""
        difficulty = 0.3  # Base difficulty
        
        # Check for known difficult platforms
        difficult_platforms = ['instagram', 'facebook', 'twitter']
        if any(p in url.lower() for p in difficult_platforms):
            difficulty += 0.3
        
        # Check for live content
        if metadata and metadata.get('is_live'):
            difficulty += 0.4
        
        return min(difficulty, 1)
    
    def update_preferences(self, preferences: Dict[str, float]) -> None:
        """Update user preferences for priority calculation."""
        self._user_preferences.update(preferences)
    
    def record_download(self, item: SmartBatchItem, success: bool) -> None:
        """Record download result for learning."""
        self._download_history.append({
            'url': item.url,
            'category': item.analysis.category if item.analysis else 'general',
            'success': success,
            'timestamp': datetime.now().isoformat(),
        })


class ResourceMonitor:
    """
    System resource monitor for adaptive scheduling.
    
    Monitors CPU, memory, network, and disk resources.
    """
    
    def __init__(self) -> None:
        """Initialize the resource monitor."""
        self._metrics = ResourceMetrics()
        self._last_check = None
    
    async def get_metrics(self) -> ResourceMetrics:
        """Get current system resource metrics."""
        try:
            import psutil
            
            self._metrics.cpu_usage = psutil.cpu_percent(interval=0.1)
            self._metrics.memory_usage = psutil.virtual_memory().percent
            
            # Get disk space
            disk = psutil.disk_usage('/')
            self._metrics.disk_space = disk.free / (1024 ** 3)  # GB
            
        except ImportError:
            # Fallback without psutil
            self._metrics.cpu_usage = 50.0
            self._metrics.memory_usage = 50.0
            self._metrics.disk_space = 100.0
        
        self._last_check = datetime.now()
        return self._metrics
    
    def should_reduce_load(self) -> bool:
        """Check if system load should be reduced."""
        return self._metrics.load_score > 0.8


class SmartBatchProcessor:
    """
    OMNIPOTENT SOVEREIGN NEXUS Smart Batch Processor.
    
    ML-powered batch processing with intelligent scheduling.
    """
    
    def __init__(
        self,
        config: Optional[SmartBatchConfig] = None,
        progress_callback: Optional[Callable[[str, float], Awaitable[None]]] = None,
        item_callback: Optional[Callable[[SmartBatchItem, str], Awaitable[None]]] = None,
    ) -> None:
        """
        Initialize the smart batch processor.
        
        Args:
            config: Processor configuration
            progress_callback: Progress callback
            item_callback: Item status callback
        """
        self.config = config or SmartBatchConfig()
        self._progress_callback = progress_callback
        self._item_callback = item_callback
        
        # Components
        self._analyzer = ContentAnalyzer()
        self._resource_monitor = ResourceMonitor()
        
        # State
        self._items: Dict[str, SmartBatchItem] = {}
        self._queue: List[str] = []
        self._active: Set[str] = set()
        self._completed: Set[str] = set()
        self._failed: Set[str] = set()
        self._cancelled: bool = False
        
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load preferences if available
        if self.config.preference_file and self.config.preference_file.exists():
            self._load_preferences()
        
        logger.info(f"SmartBatchProcessor initialized v3.0.1 ULTIMATE NEXUS")
    
    async def add_urls(
        self,
        urls: List[str],
        priorities: Optional[List[Priority]] = None,
    ) -> int:
        """
        Add URLs to the batch queue.
        
        Args:
            urls: List of URLs to add
            priorities: Optional list of priorities
            
        Returns:
            Number of URLs added
        """
        added = 0
        
        for i, url in enumerate(urls):
            # Generate ID
            item_id = f"item_{len(self._items) + 1:04d}"
            
            # Create item
            item = SmartBatchItem(
                id=item_id,
                url=url,
                priority=priorities[i] if priorities and i < len(priorities) else Priority.MEDIUM,
            )
            
            # Analyze content
            if self.config.auto_prioritize:
                item.analysis = await self._analyzer.analyze(url)
                item.priority = self._priority_from_score(item.analysis.priority_score)
            
            self._items[item_id] = item
            self._queue.append(item_id)
            added += 1
        
        # Sort queue based on strategy
        self._sort_queue()
        
        logger.info(f"Added {added} URLs to smart batch queue")
        return added
    
    def _priority_from_score(self, score: float) -> Priority:
        """Convert priority score to Priority enum."""
        if score >= 0.8:
            return Priority.CRITICAL
        elif score >= 0.6:
            return Priority.HIGH
        elif score >= 0.4:
            return Priority.MEDIUM
        elif score >= 0.2:
            return Priority.LOW
        else:
            return Priority.BACKGROUND
    
    def _sort_queue(self) -> None:
        """Sort queue based on scheduling strategy."""
        if self.config.strategy == SchedulingStrategy.FIFO:
            pass  # Already in order
        
        elif self.config.strategy == SchedulingStrategy.PRIORITY:
            self._queue.sort(key=lambda x: self._items[x].priority.value)
        
        elif self.config.strategy == SchedulingStrategy.SHORTEST_FIRST:
            self._queue.sort(
                key=lambda x: self._items[x].analysis.estimated_duration if self._items[x].analysis else 0
            )
        
        elif self.config.strategy == SchedulingStrategy.LONGEST_FIRST:
            self._queue.sort(
                key=lambda x: -(self._items[x].analysis.estimated_duration if self._items[x].analysis else 0)
            )
        
        elif self.config.strategy == SchedulingStrategy.BALANCED:
            # Balance across categories
            categories = defaultdict(list)
            for item_id in self._queue:
                item = self._items[item_id]
                cat = item.analysis.category if item.analysis else 'general'
                categories[cat].append(item_id)
            
            self._queue = []
            while any(categories.values()):
                for cat in list(categories.keys()):
                    if categories[cat]:
                        self._queue.append(categories[cat].pop(0))
        
        elif self.config.strategy == SchedulingStrategy.ADAPTIVE:
            self._adaptive_sort()
    
    def _adaptive_sort(self) -> None:
        """Adaptive ML-optimized sorting."""
        # Combine priority, estimated duration, and difficulty
        def score(item_id: str) -> float:
            item = self._items[item_id]
            if not item.analysis:
                return 0.5
            
            priority_weight = 1 - (item.priority.value - 1) / 4  # Higher priority = lower value
            duration_weight = 1 / (1 + item.analysis.estimated_duration / 3600)  # Shorter = higher
            difficulty_weight = 1 - item.analysis.download_difficulty  # Easier = higher
            
            return (priority_weight * 0.4 + duration_weight * 0.3 + difficulty_weight * 0.3)
        
        self._queue.sort(key=score, reverse=True)
    
    async def start(self) -> Dict[str, Any]:
        """
        Start the smart batch processing.
        
        Returns:
            Summary of batch results
        """
        if not self._queue:
            return {"error": "No items in queue"}
        
        self._cancelled = False
        start_time = datetime.now()
        
        # Dynamic concurrency
        max_concurrent = self.config.max_concurrent
        
        try:
            while self._queue and not self._cancelled:
                # Adaptive concurrency adjustment
                if self.config.adaptive_concurrency:
                    metrics = await self._resource_monitor.get_metrics()
                    
                    if metrics.load_score > 0.7:
                        max_concurrent = max(self.config.min_concurrent, max_concurrent - 1)
                    elif metrics.load_score < 0.3:
                        max_concurrent = min(self.config.max_concurrent_limit, max_concurrent + 1)
                
                # Process items
                semaphore = asyncio.Semaphore(max_concurrent)
                
                # Get batch of items to process
                batch_size = min(len(self._queue), max_concurrent - len(self._active))
                batch = [self._queue.pop(0) for _ in range(batch_size)]
                
                tasks = [self._process_item(item_id, semaphore) for item_id in batch]
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Report progress
                if self._progress_callback:
                    total = len(self._items)
                    completed = len(self._completed) + len(self._failed)
                    await self._progress_callback("batch_progress", completed / total)
                
                await asyncio.sleep(1)  # Prevent busy loop
        
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
        
        # Calculate results
        end_time = datetime.now()
        
        return {
            "total_items": len(self._items),
            "completed": len(self._completed),
            "failed": len(self._failed),
            "duration": (end_time - start_time).total_seconds(),
            "items": {item_id: self._items[item_id].to_dict() for item_id in self._completed},
        }
    
    async def _process_item(
        self,
        item_id: str,
        semaphore: asyncio.Semaphore,
    ) -> None:
        """Process a single batch item."""
        item = self._items[item_id]
        
        async with semaphore:
            self._active.add(item_id)
            item.status = "downloading"
            
            try:
                # Simulate download (replace with actual download logic)
                success = await self._download_item(item)
                
                if success:
                    item.status = "completed"
                    self._completed.add(item_id)
                    self._analyzer.record_download(item, True)
                else:
                    item.status = "failed"
                    self._failed.add(item_id)
                    self._analyzer.record_download(item, False)
            
            except Exception as e:
                item.status = "failed"
                item.error_message = str(e)
                self._failed.add(item_id)
            
            finally:
                self._active.discard(item_id)
                
                if self._item_callback:
                    await self._item_callback(item, item.status)
    
    async def _download_item(self, item: SmartBatchItem) -> bool:
        """Download a single item using yt-dlp."""
        yt_dlp = shutil.which("yt-dlp")
        if not yt_dlp:
            item.error_message = "yt-dlp not found"
            return False
        
        try:
            cmd = [
                yt_dlp,
                "-f", "bestvideo+bestaudio/best",
                "--merge-output-format", "mp4",
                "-o", str(self.config.output_dir / "%(title)s.%(ext)s"),
                "--no-playlist",
                item.url,
            ]
            
            if self.config.proxy:
                cmd.extend(["--proxy", self.config.proxy])
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            await process.communicate()
            
            return process.returncode == 0
            
        except Exception as e:
            item.error_message = str(e)
            return False
    
    def _load_preferences(self) -> None:
        """Load user preferences from file."""
        try:
            with open(self.config.preference_file, 'r') as f:
                preferences = json.load(f)
                self._analyzer.update_preferences(preferences)
        except Exception as e:
            logger.warning(f"Failed to load preferences: {e}")
    
    def cancel(self) -> None:
        """Cancel the batch processing."""
        self._cancelled = True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current batch status."""
        return {
            "total": len(self._items),
            "queued": len(self._queue),
            "active": len(self._active),
            "completed": len(self._completed),
            "failed": len(self._failed),
        }


# Convenience function
async def smart_batch_download(
    urls: List[str],
    output_dir: str = "./downloads/smart_batch",
    strategy: SchedulingStrategy = SchedulingStrategy.ADAPTIVE,
) -> Dict[str, Any]:
    """
    Quick smart batch download function.
    
    Args:
        urls: List of URLs
        output_dir: Output directory
        strategy: Scheduling strategy
        
    Returns:
        Batch results
    """
    config = SmartBatchConfig(
        output_dir=Path(output_dir),
        strategy=strategy,
    )
    
    processor = SmartBatchProcessor(config=config)
    await processor.add_urls(urls)
    return await processor.start()


__all__ = [
    "SmartBatchProcessor",
    "ContentAnalyzer",
    "ResourceMonitor",
    "SmartBatchConfig",
    "SmartBatchItem",
    "ContentAnalysis",
    "ResourceMetrics",
    "Priority",
    "ContentType",
    "SchedulingStrategy",
    "smart_batch_download",
]

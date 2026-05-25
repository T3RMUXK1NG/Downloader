"""
OMNIPOTENT SOVEREIGN NEXUS - Analytics Module
Version: v3.0.1 ULTIMATE NEXUS

Download analytics with support for:
- Download statistics tracking
- Bandwidth monitoring
- Success rate analysis
- Platform usage analytics
- Time-based analysis
- Report generation
- Data visualization
- Export capabilities

Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
"""

import asyncio
import logging
import time
import hashlib
import json
import csv
from abc import ABC, abstractmethod
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
    Tuple,
    Union,
    Awaitable,
)
from collections import defaultdict


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)


class TimePeriod(Enum):
    """Time period for analytics."""
    
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL = "all"


class DownloadStatus(Enum):
    """Download status for tracking."""
    
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    IN_PROGRESS = "in_progress"


class ReportFormat(Enum):
    """Report output formats."""
    
    JSON = "json"
    CSV = "csv"
    HTML = "html"
    TEXT = "text"


@dataclass
class DownloadRecord:
    """
    Single download record.
    
    Attributes:
        id: Record ID
        url: Download URL
        platform: Platform detected
        filename: Output filename
        file_size: File size in bytes
        duration: Download duration in seconds
        speed: Average speed in bytes/sec
        status: Download status
        error: Error message if failed
        timestamp: Download timestamp
        quality: Quality setting
        format: Format setting
        retry_count: Number of retries
        metadata: Additional metadata
    """
    id: str
    url: str
    platform: str
    filename: str
    file_size: int
    duration: float
    speed: float
    status: DownloadStatus
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    quality: Optional[str] = None
    format: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "url": self.url,
            "platform": self.platform,
            "filename": self.filename,
            "file_size": self.file_size,
            "duration": round(self.duration, 2),
            "speed": round(self.speed, 2),
            "status": self.status.value,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
            "quality": self.quality,
            "format": self.format,
            "retry_count": self.retry_count,
        }


@dataclass
class PlatformStats:
    """
    Platform-specific statistics.
    
    Attributes:
        platform: Platform name
        total_downloads: Total downloads
        successful: Successful downloads
        failed: Failed downloads
        total_size: Total bytes downloaded
        total_duration: Total time spent
        average_speed: Average speed
        success_rate: Success rate percentage
    """
    platform: str
    total_downloads: int = 0
    successful: int = 0
    failed: int = 0
    total_size: int = 0
    total_duration: float = 0.0
    average_speed: float = 0.0
    success_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "platform": self.platform,
            "total_downloads": self.total_downloads,
            "successful": self.successful,
            "failed": self.failed,
            "total_size": self.total_size,
            "total_duration": round(self.total_duration, 2),
            "average_speed": round(self.average_speed, 2),
            "success_rate": round(self.success_rate, 2),
        }


@dataclass
class TimeBasedStats:
    """
    Time-based statistics.
    
    Attributes:
        period: Time period
        timestamp: Period start timestamp
        downloads: Number of downloads
        bytes: Bytes downloaded
        duration: Total duration
        success_rate: Success rate
    """
    period: TimePeriod
    timestamp: datetime
    downloads: int = 0
    bytes: int = 0
    duration: float = 0.0
    success_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "period": self.period.value,
            "timestamp": self.timestamp.isoformat(),
            "downloads": self.downloads,
            "bytes": self.bytes,
            "duration": round(self.duration, 2),
            "success_rate": round(self.success_rate, 2),
        }


@dataclass
class AnalyticsSummary:
    """
    Complete analytics summary.
    
    Attributes:
        total_downloads: Total downloads
        successful_downloads: Successful downloads
        failed_downloads: Failed downloads
        total_bytes: Total bytes downloaded
        total_duration: Total download time
        average_speed: Average download speed
        success_rate: Overall success rate
        platform_stats: Per-platform statistics
        daily_stats: Daily statistics
    """
    total_downloads: int = 0
    successful_downloads: int = 0
    failed_downloads: int = 0
    cancelled_downloads: int = 0
    total_bytes: int = 0
    total_duration: float = 0.0
    average_speed: float = 0.0
    success_rate: float = 0.0
    platform_stats: Dict[str, PlatformStats] = field(default_factory=dict)
    daily_stats: List[TimeBasedStats] = field(default_factory=list)
    
    @property
    def formatted_total_size(self) -> str:
        """Get formatted total size."""
        return self._format_bytes(self.total_bytes)
    
    @property
    def formatted_total_duration(self) -> str:
        """Get formatted total duration."""
        hours = int(self.total_duration // 3600)
        minutes = int((self.total_duration % 3600) // 60)
        return f"{hours}h {minutes}m"
    
    @staticmethod
    def _format_bytes(size: int) -> str:
        """Format bytes to human readable."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_downloads": self.total_downloads,
            "successful_downloads": self.successful_downloads,
            "failed_downloads": self.failed_downloads,
            "cancelled_downloads": self.cancelled_downloads,
            "total_bytes": self.total_bytes,
            "total_duration": round(self.total_duration, 2),
            "average_speed": round(self.average_speed, 2),
            "success_rate": round(self.success_rate, 2),
            "platform_stats": {k: v.to_dict() for k, v in self.platform_stats.items()},
        }


@dataclass
class ReportConfig:
    """
    Report generation configuration.
    
    Attributes:
        period: Time period to cover
        format: Output format
        include_platforms: Include platform breakdown
        include_timeline: Include time-based data
        output_path: Output file path
    """
    period: TimePeriod = TimePeriod.MONTH
    format: ReportFormat = ReportFormat.JSON
    include_platforms: bool = True
    include_timeline: bool = True
    output_path: Optional[Path] = None


class Analytics:
    """
    OMNIPOTENT SOVEREIGN NEXUS Download Analytics.
    
    Comprehensive analytics tracking with:
    - Download statistics
    - Platform usage
    - Time-based analysis
    - Report generation
    """
    
    def __init__(
        self,
        data_path: Optional[Path] = None,
    ) -> None:
        """
        Initialize analytics.
        
        Args:
            data_path: Path to store analytics data
        """
        self._data_path = data_path or Path("./analytics")
        self._records: List[DownloadRecord] = []
        self._session_stats: Dict[str, Any] = defaultdict(float)
        self._lock = asyncio.Lock()
        
        self._data_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Analytics initialized v3.0.1 ULTIMATE NEXUS")
    
    async def record_download(
        self,
        url: str,
        platform: str,
        filename: str,
        file_size: int,
        duration: float,
        status: DownloadStatus,
        error: Optional[str] = None,
        quality: Optional[str] = None,
        format: Optional[str] = None,
        retry_count: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DownloadRecord:
        """
        Record a download event.
        
        Args:
            url: Download URL
            platform: Platform name
            filename: Output filename
            file_size: File size in bytes
            duration: Download duration
            status: Download status
            error: Error message
            quality: Quality setting
            format: Format setting
            retry_count: Retry count
            metadata: Additional metadata
            
        Returns:
            DownloadRecord
        """
        record_id = hashlib.md5(f"{url}{time.time()}".encode()).hexdigest()[:12]
        
        speed = file_size / duration if duration > 0 else 0
        
        record = DownloadRecord(
            id=record_id,
            url=url,
            platform=platform,
            filename=filename,
            file_size=file_size,
            duration=duration,
            speed=speed,
            status=status,
            error=error,
            timestamp=datetime.now(),
            quality=quality,
            format=format,
            retry_count=retry_count,
            metadata=metadata or {},
        )
        
        async with self._lock:
            self._records.append(record)
        
        logger.debug(f"Recorded download: {record_id}")
        return record
    
    def get_summary(
        self,
        period: TimePeriod = TimePeriod.ALL,
    ) -> AnalyticsSummary:
        """
        Get analytics summary.
        
        Args:
            period: Time period to analyze
            
        Returns:
            AnalyticsSummary
        """
        now = datetime.now()
        records = self._filter_by_period(period, now)
        
        if not records:
            return AnalyticsSummary()
        
        summary = AnalyticsSummary()
        
        # Calculate totals
        summary.total_downloads = len(records)
        summary.successful_downloads = len([r for r in records if r.status == DownloadStatus.SUCCESS])
        summary.failed_downloads = len([r for r in records if r.status == DownloadStatus.FAILED])
        summary.cancelled_downloads = len([r for r in records if r.status == DownloadStatus.CANCELLED])
        summary.total_bytes = sum(r.file_size for r in records)
        summary.total_duration = sum(r.duration for r in records)
        
        if summary.total_downloads > 0:
            summary.success_rate = (summary.successful_downloads / summary.total_downloads) * 100
        
        if summary.total_duration > 0:
            summary.average_speed = summary.total_bytes / summary.total_duration
        
        # Platform stats
        platform_data = defaultdict(lambda: {"count": 0, "success": 0, "failed": 0, "bytes": 0, "duration": 0.0})
        
        for record in records:
            platform_data[record.platform]["count"] += 1
            platform_data[record.platform]["bytes"] += record.file_size
            platform_data[record.platform]["duration"] += record.duration
            
            if record.status == DownloadStatus.SUCCESS:
                platform_data[record.platform]["success"] += 1
            elif record.status == DownloadStatus.FAILED:
                platform_data[record.platform]["failed"] += 1
        
        for platform, data in platform_data.items():
            stats = PlatformStats(platform=platform)
            stats.total_downloads = data["count"]
            stats.successful = data["success"]
            stats.failed = data["failed"]
            stats.total_size = data["bytes"]
            stats.total_duration = data["duration"]
            
            if stats.total_downloads > 0:
                stats.success_rate = (stats.successful / stats.total_downloads) * 100
            if stats.total_duration > 0:
                stats.average_speed = stats.total_size / stats.total_duration
            
            summary.platform_stats[platform] = stats
        
        return summary
    
    def _filter_by_period(
        self,
        period: TimePeriod,
        now: datetime,
    ) -> List[DownloadRecord]:
        """Filter records by time period."""
        if period == TimePeriod.ALL:
            return self._records
        
        thresholds = {
            TimePeriod.HOUR: timedelta(hours=1),
            TimePeriod.DAY: timedelta(days=1),
            TimePeriod.WEEK: timedelta(weeks=1),
            TimePeriod.MONTH: timedelta(days=30),
            TimePeriod.YEAR: timedelta(days=365),
        }
        
        threshold = thresholds.get(period, timedelta(days=1))
        cutoff = now - threshold
        
        return [r for r in self._records if r.timestamp >= cutoff]
    
    def get_platform_stats(
        self,
        platform: Optional[str] = None,
        period: TimePeriod = TimePeriod.ALL,
    ) -> Union[PlatformStats, Dict[str, PlatformStats]]:
        """
        Get platform statistics.
        
        Args:
            platform: Specific platform or all
            period: Time period
            
        Returns:
            PlatformStats or dict of stats
        """
        summary = self.get_summary(period)
        
        if platform:
            return summary.platform_stats.get(platform, PlatformStats(platform=platform))
        
        return summary.platform_stats
    
    def get_timeline(
        self,
        period: TimePeriod = TimePeriod.DAY,
        days: int = 7,
    ) -> List[TimeBasedStats]:
        """
        Get time-based statistics.
        
        Args:
            period: Time granularity
            days: Number of days
            
        Returns:
            List of TimeBasedStats
        """
        now = datetime.now()
        timeline = []
        
        for i in range(days):
            if period == TimePeriod.DAY:
                start = (now - timedelta(days=i)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
            else:
                start = now - timedelta(days=i)
            
            end = start + timedelta(days=1) if period == TimePeriod.DAY else start + timedelta(hours=1)
            
            day_records = [
                r for r in self._records
                if start <= r.timestamp < end
            ]
            
            if day_records:
                stats = TimeBasedStats(
                    period=period,
                    timestamp=start,
                    downloads=len(day_records),
                    bytes=sum(r.file_size for r in day_records),
                    duration=sum(r.duration for r in day_records),
                )
                
                successful = len([r for r in day_records if r.status == DownloadStatus.SUCCESS])
                stats.success_rate = (successful / stats.downloads * 100) if stats.downloads > 0 else 0
                
                timeline.append(stats)
        
        return sorted(timeline, key=lambda x: x.timestamp)
    
    def get_top_downloads(
        self,
        by: str = "size",
        limit: int = 10,
        period: TimePeriod = TimePeriod.ALL,
    ) -> List[DownloadRecord]:
        """
        Get top downloads by criteria.
        
        Args:
            by: Criteria (size, duration, speed)
            limit: Maximum results
            period: Time period
            
        Returns:
            List of DownloadRecord
        """
        records = self._filter_by_period(period, datetime.now())
        
        if by == "size":
            return sorted(records, key=lambda r: r.file_size, reverse=True)[:limit]
        elif by == "duration":
            return sorted(records, key=lambda r: r.duration, reverse=True)[:limit]
        elif by == "speed":
            return sorted(records, key=lambda r: r.speed, reverse=True)[:limit]
        
        return records[:limit]
    
    def generate_report(
        self,
        config: ReportConfig,
    ) -> Path:
        """
        Generate analytics report.
        
        Args:
            config: Report configuration
            
        Returns:
            Path to generated report
        """
        summary = self.get_summary(config.period)
        timeline = self.get_timeline() if config.include_timeline else []
        
        output_path = config.output_path or self._data_path / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if config.format == ReportFormat.JSON:
            output_path = output_path.with_suffix(".json")
            self._write_json_report(output_path, summary, timeline)
        
        elif config.format == ReportFormat.CSV:
            output_path = output_path.with_suffix(".csv")
            self._write_csv_report(output_path, summary)
        
        elif config.format == ReportFormat.TEXT:
            output_path = output_path.with_suffix(".txt")
            self._write_text_report(output_path, summary, timeline)
        
        logger.info(f"Generated report: {output_path}")
        return output_path
    
    def _write_json_report(
        self,
        path: Path,
        summary: AnalyticsSummary,
        timeline: List[TimeBasedStats],
    ) -> None:
        """Write JSON format report."""
        data = {
            "generated_at": datetime.now().isoformat(),
            "summary": summary.to_dict(),
            "timeline": [t.to_dict() for t in timeline],
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _write_csv_report(
        self,
        path: Path,
        summary: AnalyticsSummary,
    ) -> None:
        """Write CSV format report."""
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                "Platform", "Downloads", "Successful", "Failed",
                "Total Size", "Total Duration", "Avg Speed", "Success Rate"
            ])
            
            # Data
            for platform, stats in summary.platform_stats.items():
                writer.writerow([
                    platform,
                    stats.total_downloads,
                    stats.successful,
                    stats.failed,
                    stats.total_size,
                    round(stats.total_duration, 2),
                    round(stats.average_speed, 2),
                    round(stats.success_rate, 2),
                ])
    
    def _write_text_report(
        self,
        path: Path,
        summary: AnalyticsSummary,
        timeline: List[TimeBasedStats],
    ) -> None:
        """Write text format report."""
        lines = [
            "=" * 60,
            "RS TOOLKIT - Download Analytics Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            "",
            "SUMMARY",
            "-" * 40,
            f"Total Downloads: {summary.total_downloads}",
            f"Successful: {summary.successful_downloads}",
            f"Failed: {summary.failed_downloads}",
            f"Success Rate: {summary.success_rate:.1f}%",
            f"Total Downloaded: {summary.formatted_total_size}",
            f"Total Time: {summary.formatted_total_duration}",
            f"Average Speed: {summary.average_speed / 1024:.1f} KB/s",
            "",
            "PLATFORM BREAKDOWN",
            "-" * 40,
        ]
        
        for platform, stats in summary.platform_stats.items():
            lines.extend([
                f"  {platform}:",
                f"    Downloads: {stats.total_downloads}",
                f"    Success Rate: {stats.success_rate:.1f}%",
                f"    Total Size: {stats.total_size / (1024*1024):.1f} MB",
                "",
            ])
        
        with open(path, 'w') as f:
            f.write('\n'.join(lines))
    
    def export_data(
        self,
        output_path: Path,
        format: ReportFormat = ReportFormat.JSON,
    ) -> bool:
        """
        Export all analytics data.
        
        Args:
            output_path: Output file path
            format: Export format
            
        Returns:
            True if successful
        """
        try:
            if format == ReportFormat.JSON:
                data = {
                    "records": [r.to_dict() for r in self._records],
                    "exported_at": datetime.now().isoformat(),
                }
                
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=2)
            
            elif format == ReportFormat.CSV:
                with open(output_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=[
                        "id", "url", "platform", "filename", "file_size",
                        "duration", "speed", "status", "timestamp"
                    ])
                    writer.writeheader()
                    for record in self._records:
                        writer.writerow(record.to_dict())
            
            logger.info(f"Exported data to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            return False
    
    def import_data(
        self,
        input_path: Path,
    ) -> int:
        """
        Import analytics data.
        
        Args:
            input_path: Input file path
            
        Returns:
            Number of records imported
        """
        try:
            with open(input_path, 'r') as f:
                data = json.load(f)
            
            count = 0
            for record_data in data.get("records", []):
                record = DownloadRecord(
                    id=record_data["id"],
                    url=record_data["url"],
                    platform=record_data["platform"],
                    filename=record_data["filename"],
                    file_size=record_data["file_size"],
                    duration=record_data["duration"],
                    speed=record_data["speed"],
                    status=DownloadStatus(record_data["status"]),
                    error=record_data.get("error"),
                    timestamp=datetime.fromisoformat(record_data["timestamp"]),
                    quality=record_data.get("quality"),
                    format=record_data.get("format"),
                    retry_count=record_data.get("retry_count", 0),
                )
                self._records.append(record)
                count += 1
            
            logger.info(f"Imported {count} records from {input_path}")
            return count
            
        except Exception as e:
            logger.error(f"Import error: {e}")
            return 0
    
    def clear_data(
        self,
        before: Optional[datetime] = None,
    ) -> int:
        """
        Clear analytics data.
        
        Args:
            before: Clear records before this date (all if None)
            
        Returns:
            Number of records cleared
        """
        if before is None:
            count = len(self._records)
            self._records.clear()
            return count
        
        before_count = len(self._records)
        self._records = [r for r in self._records if r.timestamp >= before]
        return before_count - len(self._records)


# Convenience functions
def create_analytics(data_path: Optional[str] = None) -> Analytics:
    """
    Create analytics instance.
    
    Args:
        data_path: Path for analytics data
        
    Returns:
        Analytics
    """
    return Analytics(Path(data_path) if data_path else None)


# Export all public classes and functions
__all__ = [
    "Analytics",
    "TimePeriod",
    "DownloadStatus",
    "ReportFormat",
    "DownloadRecord",
    "PlatformStats",
    "TimeBasedStats",
    "AnalyticsSummary",
    "ReportConfig",
    "create_analytics",
]

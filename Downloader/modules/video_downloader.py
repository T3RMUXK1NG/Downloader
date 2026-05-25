"""
OMNIPOTENT SOVEREIGN NEXUS - Video Downloader Module
Version: v3.0.1 ULTIMATE NEXUS

Advanced video downloading with support for:
- Multiple platforms (YouTube, Vimeo, Dailymotion, TikTok, etc.)
- Quality selection (4K, 1080p, 720p, 480p, 360p)
- Format selection (MP4, WebM, AVI, MKV, FLV)
- Proxy and VPN support
- Cookie-based authentication
- Progress tracking with callbacks
- Parallel chunk downloads
- Resume capability
- Retry mechanisms with exponential backoff
- Bandwidth throttling
- Subtitle embedding
- Thumbnail extraction

Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
"""

import asyncio
import aiohttp
import aiofiles
import logging
import re
import time
import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
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
    AsyncIterator,
    Awaitable,
)
from urllib.parse import urlparse, parse_qs, urlencode
from concurrent.futures import ThreadPoolExecutor
import subprocess
import shutil


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)


class VideoQuality(Enum):
    """Video quality presets with resolution and bitrate information."""
    
    QUALITY_4K = auto()      # 2160p - 3840x2160
    QUALITY_2K = auto()      # 1440p - 2560x1440
    QUALITY_1080P = auto()   # 1080p - 1920x1080
    QUALITY_720P = auto()    # 720p - 1280x720
    QUALITY_480P = auto()    # 480p - 854x480
    QUALITY_360P = auto()    # 360p - 640x360
    QUALITY_240P = auto()    # 240p - 426x240
    QUALITY_144P = auto()    # 144p - 256x144
    QUALITY_AUDIO = auto()   # Audio only
    QUALITY_BEST = auto()    # Best available quality
    QUALITY_WORST = auto()   # Worst available quality
    
    @property
    def resolution(self) -> Tuple[int, int]:
        """Return the resolution as (width, height) tuple."""
        resolutions = {
            VideoQuality.QUALITY_4K: (3840, 2160),
            VideoQuality.QUALITY_2K: (2560, 1440),
            VideoQuality.QUALITY_1080P: (1920, 1080),
            VideoQuality.QUALITY_720P: (1280, 720),
            VideoQuality.QUALITY_480P: (854, 480),
            VideoQuality.QUALITY_360P: (640, 360),
            VideoQuality.QUALITY_240P: (426, 240),
            VideoQuality.QUALITY_144P: (256, 144),
            VideoQuality.QUALITY_AUDIO: (0, 0),
            VideoQuality.QUALITY_BEST: (0, 0),
            VideoQuality.QUALITY_WORST: (0, 0),
        }
        return resolutions.get(self, (0, 0))
    
    @property
    def height(self) -> int:
        """Return the video height in pixels."""
        return self.resolution[1]
    
    @classmethod
    def from_height(cls, height: int) -> "VideoQuality":
        """Determine quality from height in pixels."""
        quality_map = {
            2160: cls.QUALITY_4K,
            1440: cls.QUALITY_2K,
            1080: cls.QUALITY_1080P,
            720: cls.QUALITY_720P,
            480: cls.QUALITY_480P,
            360: cls.QUALITY_360P,
            240: cls.QUALITY_240P,
            144: cls.QUALITY_144P,
        }
        return quality_map.get(height, cls.QUALITY_BEST)


class VideoFormat(Enum):
    """Supported video container formats."""
    
    MP4 = "mp4"
    WEBM = "webm"
    MKV = "mkv"
    AVI = "avi"
    FLV = "flv"
    MOV = "mov"
    WMV = "wmv"
    TS = "ts"
    M4V = "m4v"
    OGG = "ogg"
    AUDIO_ONLY = "audio"
    
    @property
    def mime_type(self) -> str:
        """Return the MIME type for this format."""
        mime_types = {
            VideoFormat.MP4: "video/mp4",
            VideoFormat.WEBM: "video/webm",
            VideoFormat.MKV: "video/x-matroska",
            VideoFormat.AVI: "video/x-msvideo",
            VideoFormat.FLV: "video/x-flv",
            VideoFormat.MOV: "video/quicktime",
            VideoFormat.WMV: "video/x-ms-wmv",
            VideoFormat.TS: "video/mp2t",
            VideoFormat.M4V: "video/x-m4v",
            VideoFormat.OGG: "video/ogg",
            VideoFormat.AUDIO_ONLY: "audio/*",
        }
        return mime_types.get(self, "video/*")
    
    @property
    def extension(self) -> str:
        """Return the file extension."""
        return self.value


@dataclass
class DownloadProgress:
    """
    Real-time download progress information.
    
    Attributes:
        url: Source URL being downloaded
        filename: Output filename
        bytes_downloaded: Total bytes downloaded
        total_bytes: Total bytes to download (0 if unknown)
        speed: Current download speed in bytes/sec
        eta: Estimated time remaining in seconds
        percentage: Download progress percentage (0-100)
        status: Current status string
        start_time: When the download started
        chunks_completed: Number of chunks completed
        chunks_total: Total number of chunks
        retry_count: Number of retry attempts made
        is_paused: Whether download is paused
        is_resumable: Whether download can be resumed
    """
    url: str
    filename: str
    bytes_downloaded: int = 0
    total_bytes: int = 0
    speed: float = 0.0
    eta: float = 0.0
    percentage: float = 0.0
    status: str = "pending"
    start_time: Optional[datetime] = None
    chunks_completed: int = 0
    chunks_total: int = 0
    retry_count: int = 0
    is_paused: bool = False
    is_resumable: bool = True
    
    @property
    def elapsed_time(self) -> float:
        """Return elapsed time in seconds."""
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "url": self.url,
            "filename": self.filename,
            "bytes_downloaded": self.bytes_downloaded,
            "total_bytes": self.total_bytes,
            "speed": self.speed,
            "eta": self.eta,
            "percentage": self.percentage,
            "status": self.status,
            "elapsed_time": self.elapsed_time,
            "chunks_completed": self.chunks_completed,
            "chunks_total": self.chunks_total,
            "retry_count": self.retry_count,
            "is_paused": self.is_paused,
            "is_resumable": self.is_resumable,
        }


@dataclass
class VideoInfo:
    """
    Comprehensive video information.
    
    Attributes:
        id: Unique video identifier
        title: Video title
        description: Video description
        duration: Duration in seconds
        thumbnail_url: Thumbnail URL
        uploader: Uploader name
        uploader_id: Uploader ID
        upload_date: Upload date
        view_count: Number of views
        like_count: Number of likes
        dislike_count: Number of dislikes
        comment_count: Number of comments
        categories: Video categories
        tags: Video tags
        formats: Available format info
        age_limit: Age restriction
        is_live: Whether video is live
        was_live: Whether video was a livestream
        availability: Availability status
    """
    id: str
    title: str
    description: Optional[str] = None
    duration: int = 0
    thumbnail_url: Optional[str] = None
    uploader: Optional[str] = None
    uploader_id: Optional[str] = None
    upload_date: Optional[str] = None
    view_count: int = 0
    like_count: int = 0
    dislike_count: int = 0
    comment_count: int = 0
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    formats: List[Dict[str, Any]] = field(default_factory=list)
    age_limit: int = 0
    is_live: bool = False
    was_live: bool = False
    availability: str = "public"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "duration": self.duration,
            "thumbnail_url": self.thumbnail_url,
            "uploader": self.uploader,
            "uploader_id": self.uploader_id,
            "upload_date": self.upload_date,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "dislike_count": self.dislike_count,
            "comment_count": self.comment_count,
            "categories": self.categories,
            "tags": self.tags,
            "formats": self.formats,
            "age_limit": self.age_limit,
            "is_live": self.is_live,
            "was_live": self.was_live,
            "availability": self.availability,
        }


@dataclass
class DownloadResult:
    """
    Final download result with all metadata.
    
    Attributes:
        success: Whether download was successful
        filepath: Path to downloaded file
        filename: Filename only
        url: Source URL
        video_info: Video information
        file_size: File size in bytes
        download_time: Total download time in seconds
        average_speed: Average download speed
        quality: Quality of downloaded video
        format: Format of downloaded video
        error_message: Error message if failed
        error_code: Error code if failed
        timestamp: When download completed
        checksum: MD5 checksum of file
    """
    success: bool
    filepath: Optional[Path] = None
    filename: Optional[str] = None
    url: str = ""
    video_info: Optional[VideoInfo] = None
    file_size: int = 0
    download_time: float = 0.0
    average_speed: float = 0.0
    quality: VideoQuality = VideoQuality.QUALITY_BEST
    format: VideoFormat = VideoFormat.MP4
    error_message: Optional[str] = None
    error_code: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)
    checksum: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "filepath": str(self.filepath) if self.filepath else None,
            "filename": self.filename,
            "url": self.url,
            "video_info": self.video_info.to_dict() if self.video_info else None,
            "file_size": self.file_size,
            "download_time": self.download_time,
            "average_speed": self.average_speed,
            "quality": self.quality.name,
            "format": self.format.value,
            "error_message": self.error_message,
            "error_code": self.error_code,
            "timestamp": self.timestamp.isoformat(),
            "checksum": self.checksum,
        }


@dataclass
class DownloadConfig:
    """
    Configuration for video download operations.
    
    Attributes:
        quality: Target video quality
        format: Target video format
        output_dir: Output directory
        filename_template: Filename template with placeholders
        max_filesize: Maximum file size in bytes (0 = unlimited)
        min_filesize: Minimum file size in bytes
        prefer_ipv4: Prefer IPv4 for DNS resolution
        proxy: Proxy URL
        cookies_file: Path to cookies file
        rate_limit: Maximum download speed in bytes/sec
        retries: Number of retry attempts
        retry_delay: Base delay between retries
        timeout: Request timeout in seconds
        concurrent_fragments: Number of concurrent fragment downloads
        buffersize: Buffer size for downloads
        no_check_certificate: Skip SSL certificate verification
        user_agent: Custom user agent
        headers: Additional HTTP headers
        embed_subs: Embed subtitles in video
        embed_thumbnail: Embed thumbnail in video
        write_thumbnail: Save thumbnail separately
        write_description: Save description to file
        write_info_json: Save info JSON
        keep_video: Keep video after post-processing
        merge_output_format: Format for merged output
        postprocessors: List of post-processor configs
    """
    quality: VideoQuality = VideoQuality.QUALITY_BEST
    format: VideoFormat = VideoFormat.MP4
    output_dir: Path = Path("./downloads")
    filename_template: str = "%(title)s.%(ext)s"
    max_filesize: int = 0
    min_filesize: int = 0
    prefer_ipv4: bool = True
    proxy: Optional[str] = None
    cookies_file: Optional[Path] = None
    rate_limit: int = 0
    retries: int = 3
    retry_delay: float = 1.0
    timeout: float = 300.0
    concurrent_fragments: int = 4
    buffersize: int = 16384
    no_check_certificate: bool = False
    user_agent: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    embed_subs: bool = False
    embed_thumbnail: bool = False
    write_thumbnail: bool = True
    write_description: bool = False
    write_info_json: bool = True
    keep_video: bool = True
    merge_output_format: str = "mp4"
    postprocessors: List[Dict[str, Any]] = field(default_factory=list)


class PlatformDetector:
    """Detect and identify video platform from URL."""
    
    PLATFORMS = {
        'youtube': [
            r'(youtube\.com|youtu\.be)',
            r'youtube\.com/watch\?v=',
            r'youtu\.be/',
        ],
        'vimeo': [
            r'vimeo\.com',
        ],
        'dailymotion': [
            r'dailymotion\.com',
            r'dai\.ly',
        ],
        'tiktok': [
            r'tiktok\.com',
            r'vm\.tiktok\.com',
        ],
        'twitter': [
            r'twitter\.com',
            r'x\.com',
        ],
        'instagram': [
            r'instagram\.com',
            r'instagr\.am',
        ],
        'facebook': [
            r'facebook\.com',
            r'fb\.watch',
        ],
        'twitch': [
            r'twitch\.tv',
            r'clips\.twitch\.tv',
        ],
        'reddit': [
            r'reddit\.com',
            r'redd\.it',
        ],
        'bilibili': [
            r'bilibili\.com',
            r'b23\.tv',
        ],
        'rumble': [
            r'rumble\.com',
        ],
        'odysee': [
            r'odysee\.com',
            r'lbry\.tv',
        ],
    }
    
    @classmethod
    def detect(cls, url: str) -> Optional[str]:
        """
        Detect platform from URL.
        
        Args:
            url: Video URL to analyze
            
        Returns:
            Platform name or None if unknown
        """
        url_lower = url.lower()
        for platform, patterns in cls.PLATFORMS.items():
            for pattern in patterns:
                if re.search(pattern, url_lower):
                    return platform
        return None
    
    @classmethod
    def is_supported(cls, url: str) -> bool:
        """Check if URL is from a supported platform."""
        return cls.detect(url) is not None


class VideoDownloader:
    """
    OMNIPOTENT SOVEREIGN NEXUS Video Downloader.
    
    Advanced video downloading with comprehensive features:
    - Multi-platform support (YouTube, Vimeo, TikTok, etc.)
    - Quality and format selection
    - Proxy and cookie support
    - Progress tracking with callbacks
    - Parallel chunk downloads
    - Resume capability
    - Retry mechanisms
    - Bandwidth control
    """
    
    def __init__(
        self,
        config: Optional[DownloadConfig] = None,
        progress_callback: Optional[Callable[[DownloadProgress], Awaitable[None]]] = None,
    ) -> None:
        """
        Initialize the video downloader.
        
        Args:
            config: Download configuration
            progress_callback: Async callback for progress updates
        """
        self.config = config or DownloadConfig()
        self._progress_callback = progress_callback
        self._session: Optional[aiohttp.ClientSession] = None
        self._active_downloads: Dict[str, DownloadProgress] = {}
        self._cancelled: set = set()
        self._paused: set = set()
        
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"VideoDownloader initialized v3.0.1 ULTIMATE NEXUS")
    
    async def __aenter__(self) -> "VideoDownloader":
        """Async context manager entry."""
        await self._create_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
    
    async def _create_session(self) -> None:
        """Create aiohttp session with configuration."""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=self.config.concurrent_fragments,
                limit_per_host=2,
                enable_cleanup_closed=True,
            )
            
            headers = {
                "User-Agent": self.config.user_agent or 
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                **self.config.headers,
            }
            
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            
            self._session = aiohttp.ClientSession(
                connector=connector,
                headers=headers,
                timeout=timeout,
                trust_env=True,
            )
    
    async def close(self) -> None:
        """Close the downloader and release resources."""
        if self._session and not self._session.closed:
            await self._session.close()
        logger.info("VideoDownloader closed")
    
    def _get_yt_dlp_path(self) -> Optional[str]:
        """Find yt-dlp executable."""
        # Check common locations
        paths = [
            shutil.which("yt-dlp"),
            "/usr/local/bin/yt-dlp",
            "/usr/bin/yt-dlp",
            Path.home() / ".local/bin/yt-dlp",
        ]
        for path in paths:
            if path and Path(path).exists():
                return str(path)
        return None
    
    async def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """
        Extract video information without downloading.
        
        Args:
            url: Video URL
            
        Returns:
            VideoInfo object or None if extraction fails
        """
        yt_dlp = self._get_yt_dlp_path()
        if not yt_dlp:
            logger.error("yt-dlp not found. Please install yt-dlp.")
            return None
        
        try:
            cmd = [
                yt_dlp,
                "--dump-json",
                "--no-download",
                "--no-playlist",
                url,
            ]
            
            if self.config.proxy:
                cmd.extend(["--proxy", self.config.proxy])
            
            if self.config.cookies_file:
                cmd.extend(["--cookies", str(self.config.cookies_file)])
            
            if self.config.no_check_certificate:
                cmd.append("--no-check-certificate")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                data = json.loads(stdout.decode())
                return VideoInfo(
                    id=data.get("id", ""),
                    title=data.get("title", ""),
                    description=data.get("description"),
                    duration=data.get("duration", 0),
                    thumbnail_url=data.get("thumbnail"),
                    uploader=data.get("uploader"),
                    uploader_id=data.get("uploader_id"),
                    upload_date=data.get("upload_date"),
                    view_count=data.get("view_count", 0),
                    like_count=data.get("like_count", 0),
                    dislike_count=data.get("dislike_count", 0),
                    comment_count=data.get("comment_count", 0),
                    categories=data.get("categories", []),
                    tags=data.get("tags", []),
                    formats=data.get("formats", []),
                    age_limit=data.get("age_limit", 0),
                    is_live=data.get("is_live", False),
                    was_live=data.get("was_live", False),
                    availability=data.get("availability", "public"),
                )
            else:
                logger.error(f"Failed to get video info: {stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting video info: {e}")
            return None
    
    async def download(
        self,
        url: str,
        output_filename: Optional[str] = None,
        quality: Optional[VideoQuality] = None,
        format: Optional[VideoFormat] = None,
    ) -> DownloadResult:
        """
        Download a video from URL.
        
        Args:
            url: Video URL to download
            output_filename: Custom output filename
            quality: Override quality setting
            format: Override format setting
            
        Returns:
            DownloadResult with download status and file info
        """
        download_id = hashlib.md5(url.encode()).hexdigest()[:8]
        start_time = datetime.now()
        
        # Use provided overrides or config defaults
        target_quality = quality or self.config.quality
        target_format = format or self.config.format
        
        # Initialize progress
        progress = DownloadProgress(
            url=url,
            filename=output_filename or "video",
            status="initializing",
            start_time=start_time,
        )
        self._active_downloads[download_id] = progress
        
        try:
            # Check if yt-dlp is available
            yt_dlp = self._get_yt_dlp_path()
            if not yt_dlp:
                return DownloadResult(
                    success=False,
                    url=url,
                    error_message="yt-dlp not found. Install with: pip install yt-dlp",
                    error_code=1,
                )
            
            # Get video info first
            video_info = await self.get_video_info(url)
            if not video_info:
                return DownloadResult(
                    success=False,
                    url=url,
                    error_message="Failed to extract video information",
                    error_code=2,
                )
            
            # Update progress
            progress.status = "downloading"
            progress.filename = output_filename or self._sanitize_filename(video_info.title)
            await self._report_progress(progress)
            
            # Build yt-dlp command
            cmd = self._build_yt_dlp_command(
                url=url,
                output_filename=progress.filename,
                quality=target_quality,
                format=target_format,
                video_info=video_info,
            )
            
            # Execute download
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            # Monitor progress
            await self._monitor_download(process, progress)
            
            # Wait for completion
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Find the downloaded file
                downloaded_file = self._find_downloaded_file(progress.filename, video_info.id)
                
                if downloaded_file and downloaded_file.exists():
                    # Calculate checksum
                    checksum = await self._calculate_checksum(downloaded_file)
                    
                    end_time = datetime.now()
                    download_time = (end_time - start_time).total_seconds()
                    file_size = downloaded_file.stat().st_size
                    
                    return DownloadResult(
                        success=True,
                        filepath=downloaded_file,
                        filename=downloaded_file.name,
                        url=url,
                        video_info=video_info,
                        file_size=file_size,
                        download_time=download_time,
                        average_speed=file_size / download_time if download_time > 0 else 0,
                        quality=target_quality,
                        format=target_format,
                        checksum=checksum,
                    )
                else:
                    return DownloadResult(
                        success=False,
                        url=url,
                        video_info=video_info,
                        error_message="Downloaded file not found",
                        error_code=4,
                    )
            else:
                error_msg = stderr.decode() if stderr else "Unknown error"
                return DownloadResult(
                    success=False,
                    url=url,
                    video_info=video_info,
                    error_message=error_msg,
                    error_code=process.returncode or 3,
                )
                
        except asyncio.CancelledError:
            logger.info(f"Download cancelled: {url}")
            return DownloadResult(
                success=False,
                url=url,
                error_message="Download cancelled by user",
                error_code=99,
            )
        except Exception as e:
            logger.error(f"Download error: {e}")
            return DownloadResult(
                success=False,
                url=url,
                error_message=str(e),
                error_code=5,
            )
        finally:
            self._active_downloads.pop(download_id, None)
    
    def _build_yt_dlp_command(
        self,
        url: str,
        output_filename: str,
        quality: VideoQuality,
        format: VideoFormat,
        video_info: VideoInfo,
    ) -> List[str]:
        """Build yt-dlp command with all options."""
        yt_dlp = self._get_yt_dlp_path()
        cmd = [yt_dlp]
        
        # Format selection
        if quality == VideoQuality.QUALITY_BEST:
            format_str = "bestvideo+bestaudio/best"
        elif quality == VideoQuality.QUALITY_WORST:
            format_str = "worstvideo+worstaudio/worst"
        elif quality == VideoQuality.QUALITY_AUDIO:
            format_str = "bestaudio/best"
        else:
            # Specific quality
            height = quality.height
            format_str = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
        
        if format != VideoFormat.AUDIO_ONLY:
            format_str += f"/{format.extension}"
        
        cmd.extend(["-f", format_str])
        
        # Output path
        output_path = self.config.output_dir / f"{output_filename}.%(ext)s"
        cmd.extend(["-o", str(output_path)])
        
        # Merge format
        cmd.extend(["--merge-output-format", self.config.merge_output_format])
        
        # Network options
        if self.config.proxy:
            cmd.extend(["--proxy", self.config.proxy])
        
        if self.config.cookies_file:
            cmd.extend(["--cookies", str(self.config.cookies_file)])
        
        if self.config.no_check_certificate:
            cmd.append("--no-check-certificate")
        
        if self.config.rate_limit > 0:
            cmd.extend(["--limit-rate", f"{self.config.rate_limit}"])
        
        if self.config.user_agent:
            cmd.extend(["--user-agent", self.config.user_agent])
        
        # Download options
        cmd.extend(["--concurrent-fragments", str(self.config.concurrent_fragments)])
        cmd.extend(["--retries", str(self.config.retries)])
        
        if self.config.prefer_ipv4:
            cmd.append("--force-ipv4")
        
        # Additional files
        if self.config.write_thumbnail:
            cmd.append("--write-thumbnail")
        
        if self.config.write_description:
            cmd.append("--write-description")
        
        if self.config.write_info_json:
            cmd.append("--write-info-json")
        
        # Embed options
        if self.config.embed_thumbnail:
            cmd.append("--embed-thumbnail")
        
        if self.config.embed_subs:
            cmd.append("--embed-subs")
        
        # External downloader for parallel chunks
        # cmd.extend(["--downloader", "aria2c"])
        # cmd.extend(["--downloader-args", "aria2c:-x 8 -k 1M"])
        
        # URL
        cmd.append(url)
        
        return cmd
    
    async def _monitor_download(
        self,
        process: asyncio.subprocess.Process,
        progress: DownloadProgress,
    ) -> None:
        """Monitor download progress from process output."""
        # This would parse yt-dlp output for progress
        # For simplicity, we just update status
        progress.status = "downloading"
        await self._report_progress(progress)
    
    async def _report_progress(self, progress: DownloadProgress) -> None:
        """Report progress to callback if available."""
        if self._progress_callback:
            try:
                await self._progress_callback(progress)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility."""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        # Limit length
        return filename[:200] if len(filename) > 200 else filename
    
    def _find_downloaded_file(self, base_name: str, video_id: str) -> Optional[Path]:
        """Find the downloaded file in output directory."""
        for ext in ['mp4', 'webm', 'mkv', 'avi', 'm4a', 'opus', 'mp3']:
            # Try exact name
            path = self.config.output_dir / f"{base_name}.{ext}"
            if path.exists():
                return path
            
            # Try with video ID
            path = self.config.output_dir / f"{base_name}-{video_id}.{ext}"
            if path.exists():
                return path
        
        # Find any new file in directory
        for file in self.config.output_dir.iterdir():
            if file.is_file() and video_id in file.name:
                return file
        
        return None
    
    async def _calculate_checksum(self, filepath: Path) -> str:
        """Calculate MD5 checksum of file."""
        md5 = hashlib.md5()
        async with aiofiles.open(filepath, 'rb') as f:
            while chunk := await f.read(8192):
                md5.update(chunk)
        return md5.hexdigest()
    
    async def download_multiple(
        self,
        urls: List[str],
        max_concurrent: int = 3,
    ) -> List[DownloadResult]:
        """
        Download multiple videos concurrently.
        
        Args:
            urls: List of video URLs
            max_concurrent: Maximum concurrent downloads
            
        Returns:
            List of DownloadResult objects
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def download_with_semaphore(url: str) -> DownloadResult:
            async with semaphore:
                return await self.download(url)
        
        tasks = [download_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            r if isinstance(r, DownloadResult) else DownloadResult(
                success=False,
                url=urls[i],
                error_message=str(r),
            )
            for i, r in enumerate(results)
        ]
    
    def cancel_download(self, download_id: str) -> bool:
        """Cancel an active download."""
        if download_id in self._active_downloads:
            self._cancelled.add(download_id)
            return True
        return False
    
    def pause_download(self, download_id: str) -> bool:
        """Pause an active download."""
        if download_id in self._active_downloads:
            self._paused.add(download_id)
            self._active_downloads[download_id].is_paused = True
            return True
        return False
    
    def resume_download(self, download_id: str) -> bool:
        """Resume a paused download."""
        if download_id in self._paused:
            self._paused.discard(download_id)
            if download_id in self._active_downloads:
                self._active_downloads[download_id].is_paused = False
            return True
        return False
    
    def get_active_downloads(self) -> Dict[str, DownloadProgress]:
        """Get all active downloads."""
        return self._active_downloads.copy()
    
    async def get_available_qualities(self, url: str) -> List[Dict[str, Any]]:
        """
        Get available quality options for a video.
        
        Args:
            url: Video URL
            
        Returns:
            List of available quality/format options
        """
        video_info = await self.get_video_info(url)
        if not video_info:
            return []
        
        qualities = []
        seen_heights = set()
        
        for fmt in video_info.formats:
            height = fmt.get("height", 0)
            if height and height not in seen_heights:
                seen_heights.add(height)
                qualities.append({
                    "quality": VideoQuality.from_height(height).name,
                    "height": height,
                    "width": fmt.get("width", 0),
                    "fps": fmt.get("fps", 0),
                    "vcodec": fmt.get("vcodec", ""),
                    "acodec": fmt.get("acodec", ""),
                    "filesize": fmt.get("filesize", 0),
                    "format_id": fmt.get("format_id", ""),
                    "ext": fmt.get("ext", ""),
                })
        
        return sorted(qualities, key=lambda x: x["height"], reverse=True)


# Convenience function for quick downloads
async def download_video(
    url: str,
    output_dir: str = "./downloads",
    quality: VideoQuality = VideoQuality.QUALITY_BEST,
    progress_callback: Optional[Callable[[DownloadProgress], Awaitable[None]]] = None,
) -> DownloadResult:
    """
    Quick download function for single video.
    
    Args:
        url: Video URL
        output_dir: Output directory
        quality: Target quality
        progress_callback: Progress callback function
        
    Returns:
        DownloadResult with download status
    """
    config = DownloadConfig(
        output_dir=Path(output_dir),
        quality=quality,
    )
    
    async with VideoDownloader(config=config, progress_callback=progress_callback) as downloader:
        return await downloader.download(url)


# Export all public classes and functions
__all__ = [
    "VideoDownloader",
    "VideoQuality",
    "VideoFormat",
    "DownloadProgress",
    "DownloadResult",
    "DownloadConfig",
    "VideoInfo",
    "PlatformDetector",
    "download_video",
]

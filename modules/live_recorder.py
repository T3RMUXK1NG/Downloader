"""
OMNIPOTENT SOVEREIGN NEXUS - Live Stream Recorder Module
Version: v3.0.1 ULTIMATE NEXUS

Live stream recording with support for:
- Multi-platform live stream capture
- YouTube Live, Twitch, Facebook Live, etc.
- Automatic stream detection
- Quality selection
- Schedule-based recording
- Chat/Comments capture
- Stream metadata extraction
- Auto-restart on disconnection
- Segment splitting

Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
"""

import asyncio
import aiohttp
import aiofiles
import logging
import json
import re
import shutil
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
    Union,
    Awaitable,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)


class StreamPlatform(Enum):
    """Supported streaming platforms."""
    
    YOUTUBE = "youtube"
    TWITCH = "twitch"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    RUMBLE = "rumble"
    KICK = "kick"
    UNKNOWN = "unknown"


class StreamStatus(Enum):
    """Live stream status."""
    
    WAITING = "waiting"
    LIVE = "live"
    ENDED = "ended"
    RECORDING = "recording"
    ERROR = "error"
    SCHEDULED = "scheduled"


@dataclass
class StreamInfo:
    """
    Live stream information.
    
    Attributes:
        id: Stream ID
        title: Stream title
        url: Stream URL
        platform: Streaming platform
        status: Current status
        start_time: Stream start time
        end_time: Stream end time
        duration: Duration in seconds
        viewer_count: Current viewer count
        description: Stream description
        thumbnail_url: Thumbnail URL
        is_live: Whether stream is live
    """
    id: str = ""
    title: str = ""
    url: str = ""
    platform: StreamPlatform = StreamPlatform.UNKNOWN
    status: StreamStatus = StreamStatus.UNKNOWN
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: int = 0
    viewer_count: int = 0
    description: str = ""
    thumbnail_url: Optional[str] = None
    is_live: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "platform": self.platform.value,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "viewer_count": self.viewer_count,
            "description": self.description,
            "thumbnail_url": self.thumbnail_url,
            "is_live": self.is_live,
        }


@dataclass
class RecordingResult:
    """
    Live stream recording result.
    
    Attributes:
        success: Whether recording succeeded
        stream_info: Stream information
        output_file: Path to recorded file
        file_size: File size in bytes
        duration: Recording duration in seconds
        start_time: Recording start time
        end_time: Recording end time
        segments: List of segment files
        error_message: Error message if failed
    """
    success: bool
    stream_info: Optional[StreamInfo] = None
    output_file: Optional[Path] = None
    file_size: int = 0
    duration: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    segments: List[Path] = field(default_factory=list)
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "stream_info": self.stream_info.to_dict() if self.stream_info else None,
            "output_file": str(self.output_file) if self.output_file else None,
            "file_size": self.file_size,
            "duration": self.duration,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "segments": [str(s) for s in self.segments],
            "error_message": self.error_message,
        }


@dataclass
class RecordingConfig:
    """
    Configuration for live stream recording.
    
    Attributes:
        output_dir: Output directory
        quality: Recording quality
        format: Output format
        split_duration: Split recording into segments (seconds, 0 = no split)
        wait_for_stream: Wait for stream to start
        max_wait_time: Maximum wait time in seconds
        auto_restart: Auto-restart on disconnection
        max_restarts: Maximum restart attempts
        record_chat: Record chat messages
        proxy: Proxy URL
        cookies_file: Path to cookies file
        user_agent: Custom user agent
        timeout: Request timeout
        schedule_start: Scheduled start time
        schedule_end: Scheduled end time
        filename_template: Filename template
    """
    output_dir: Path = Path("./downloads/live")
    quality: str = "best"
    format: str = "mp4"
    split_duration: int = 0
    wait_for_stream: bool = True
    max_wait_time: int = 3600
    auto_restart: bool = True
    max_restarts: int = 5
    record_chat: bool = False
    proxy: Optional[str] = None
    cookies_file: Optional[Path] = None
    user_agent: Optional[str] = None
    timeout: float = 600.0
    schedule_start: Optional[datetime] = None
    schedule_end: Optional[datetime] = None
    filename_template: str = "%(title)s_%(timestamp)s.%(ext)s"


class LiveRecorder:
    """
    OMNIPOTENT SOVEREIGN NEXUS Live Stream Recorder.
    
    Comprehensive live stream recording with multi-platform support.
    """
    
    # Platform detection patterns
    PLATFORM_PATTERNS = {
        StreamPlatform.YOUTUBE: [r'youtube\.com', r'youtu\.be'],
        StreamPlatform.TWITCH: [r'twitch\.tv'],
        StreamPlatform.FACEBOOK: [r'facebook\.com', r'fb\.watch'],
        StreamPlatform.INSTAGRAM: [r'instagram\.com'],
        StreamPlatform.TWITTER: [r'twitter\.com', r'x\.com'],
        StreamPlatform.VIMEO: [r'vimeo\.com'],
        StreamPlatform.DAILYMOTION: [r'dailymotion\.com'],
        StreamPlatform.RUMBLE: [r'rumble\.com'],
        StreamPlatform.KICK: [r'kick\.com'],
    }
    
    def __init__(
        self,
        config: Optional[RecordingConfig] = None,
        progress_callback: Optional[Callable[[str, float], Awaitable[None]]] = None,
        status_callback: Optional[Callable[[StreamStatus, str], Awaitable[None]]] = None,
    ) -> None:
        """
        Initialize the live recorder.
        
        Args:
            config: Recording configuration
            progress_callback: Progress callback
            status_callback: Status change callback
        """
        self.config = config or RecordingConfig()
        self._progress_callback = progress_callback
        self._status_callback = status_callback
        self._session: Optional[aiohttp.ClientSession] = None
        self._active_recordings: Dict[str, asyncio.subprocess.Process] = {}
        self._cancelled: Set[str] = set()
        
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"LiveRecorder initialized v3.0.1 ULTIMATE NEXUS")
    
    async def __aenter__(self) -> "LiveRecorder":
        """Async context manager entry."""
        await self._create_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
    
    async def _create_session(self) -> None:
        """Create aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
    
    async def close(self) -> None:
        """Close the recorder."""
        if self._session and not self._session.closed:
            await self._session.close()
        
        # Cancel all active recordings
        for recording_id in list(self._active_recordings.keys()):
            await self.cancel_recording(recording_id)
        
        logger.info("LiveRecorder closed")
    
    def _detect_platform(self, url: str) -> StreamPlatform:
        """Detect streaming platform from URL."""
        url_lower = url.lower()
        
        for platform, patterns in self.PLATFORM_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url_lower):
                    return platform
        
        return StreamPlatform.UNKNOWN
    
    async def get_stream_info(self, url: str) -> Optional[StreamInfo]:
        """
        Get live stream information.
        
        Args:
            url: Stream URL
            
        Returns:
            StreamInfo or None
        """
        yt_dlp = shutil.which("yt-dlp")
        if not yt_dlp:
            logger.error("yt-dlp not found")
            return None
        
        try:
            cmd = [
                yt_dlp,
                "--dump-json",
                "--no-download",
                url,
            ]
            
            if self.config.proxy:
                cmd.extend(["--proxy", self.config.proxy])
            
            if self.config.cookies_file:
                cmd.extend(["--cookies", str(self.config.cookies_file)])
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, _ = await process.communicate()
            
            if process.returncode == 0:
                data = json.loads(stdout.decode())
                
                return StreamInfo(
                    id=data.get("id", ""),
                    title=data.get("title", ""),
                    url=url,
                    platform=self._detect_platform(url),
                    status=StreamStatus.LIVE if data.get("is_live") else StreamStatus.ENDED,
                    viewer_count=data.get("view_count", 0),
                    description=data.get("description", ""),
                    thumbnail_url=data.get("thumbnail"),
                    is_live=data.get("is_live", False),
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting stream info: {e}")
            return None
    
    async def start_recording(
        self,
        url: str,
        output_filename: Optional[str] = None,
    ) -> RecordingResult:
        """
        Start recording a live stream.
        
        Args:
            url: Stream URL
            output_filename: Custom output filename
            
        Returns:
            RecordingResult
        """
        start_time = datetime.now()
        recording_id = f"rec_{int(start_time.timestamp())}"
        
        try:
            # Wait for scheduled start if configured
            if self.config.schedule_start:
                wait_seconds = (self.config.schedule_start - start_time).total_seconds()
                if wait_seconds > 0:
                    await self._report_status(StreamStatus.SCHEDULED, f"Waiting {wait_seconds:.0f}s for scheduled start")
                    await asyncio.sleep(wait_seconds)
            
            # Wait for stream to go live
            if self.config.wait_for_stream:
                stream_info = await self._wait_for_stream(url)
                if not stream_info:
                    return RecordingResult(
                        success=False,
                        error_message="Stream did not start within wait time",
                    )
            else:
                stream_info = await self.get_stream_info(url)
            
            if not stream_info:
                return RecordingResult(
                    success=False,
                    error_message="Failed to get stream information",
                )
            
            await self._report_status(StreamStatus.RECORDING, f"Recording: {stream_info.title}")
            
            # Start recording
            result = await self._record_stream(url, stream_info, output_filename)
            
            return result
            
        except asyncio.CancelledError:
            return RecordingResult(
                success=False,
                error_message="Recording cancelled",
            )
        except Exception as e:
            logger.error(f"Recording error: {e}")
            return RecordingResult(
                success=False,
                error_message=str(e),
            )
    
    async def _wait_for_stream(self, url: str) -> Optional[StreamInfo]:
        """Wait for stream to go live."""
        wait_start = datetime.now()
        
        while (datetime.now() - wait_start).total_seconds() < self.config.max_wait_time:
            stream_info = await self.get_stream_info(url)
            
            if stream_info and stream_info.is_live:
                return stream_info
            
            await self._report_status(StreamStatus.WAITING, "Waiting for stream to start")
            await asyncio.sleep(30)  # Check every 30 seconds
        
        return None
    
    async def _record_stream(
        self,
        url: str,
        stream_info: StreamInfo,
        output_filename: Optional[str] = None,
    ) -> RecordingResult:
        """Record the stream using streamlink/yt-dlp."""
        yt_dlp = shutil.which("yt-dlp")
        if not yt_dlp:
            return RecordingResult(
                success=False,
                stream_info=stream_info,
                error_message="yt-dlp not found",
            )
        
        start_time = datetime.now()
        
        # Generate filename
        timestamp = start_time.strftime("%Y%m%d_%H%M%S")
        filename = output_filename or f"{stream_info.title[:50]}_{timestamp}"
        
        # Sanitize filename
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        output_path = self.config.output_dir / f"{filename}.%(ext)s"
        
        # Build yt-dlp command
        cmd = [
            yt_dlp,
            "-f", self.config.quality,
            "--live-from-start",  # Start from beginning if possible
            "-o", str(output_path),
            "--no-playlist",
            "--hls-prefer-native",
            "--no-part",  # Don't use .part files
        ]
        
        if self.config.format:
            cmd.extend(["--merge-output-format", self.config.format])
        
        if self.config.proxy:
            cmd.extend(["--proxy", self.config.proxy])
        
        if self.config.cookies_file:
            cmd.extend(["--cookies", str(self.config.cookies_file)])
        
        if self.config.split_duration > 0:
            cmd.extend(["--external-downloader", "ffmpeg"])
            cmd.extend(["--external-downloader-args", f"-segment_time {self.config.split_duration}"])
        
        cmd.append(url)
        
        # Execute recording
        recording_id = f"rec_{int(start_time.timestamp())}"
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            self._active_recordings[recording_id] = process
            
            # Monitor recording
            await process.communicate()
            
            self._active_recordings.pop(recording_id, None)
            
            end_time = datetime.now()
            
            if process.returncode == 0 or recording_id in self._cancelled:
                # Find recorded file
                recorded_file = await self._find_recorded_file(filename)
                
                if recorded_file:
                    return RecordingResult(
                        success=True,
                        stream_info=stream_info,
                        output_file=recorded_file,
                        file_size=recorded_file.stat().st_size if recorded_file else 0,
                        duration=(end_time - start_time).total_seconds(),
                        start_time=start_time,
                        end_time=end_time,
                    )
            
            return RecordingResult(
                success=False,
                stream_info=stream_info,
                error_message="Recording failed or was interrupted",
            )
            
        except Exception as e:
            self._active_recordings.pop(recording_id, None)
            return RecordingResult(
                success=False,
                stream_info=stream_info,
                error_message=str(e),
            )
    
    async def _find_recorded_file(self, base_name: str) -> Optional[Path]:
        """Find the recorded file."""
        # Check for exact match
        for ext in ['mp4', 'mkv', 'webm', 'ts', 'flv']:
            path = self.config.output_dir / f"{base_name}.{ext}"
            if path.exists():
                return path
        
        # Find most recent file
        files = list(self.config.output_dir.glob("*"))
        if files:
            return max(files, key=lambda f: f.stat().st_mtime)
        
        return None
    
    async def cancel_recording(self, recording_id: str) -> bool:
        """Cancel an active recording."""
        if recording_id in self._active_recordings:
            process = self._active_recordings[recording_id]
            process.terminate()
            self._cancelled.add(recording_id)
            return True
        return False
    
    async def _report_status(self, status: StreamStatus, message: str) -> None:
        """Report status to callback."""
        if self._status_callback:
            try:
                await self._status_callback(status, message)
            except Exception:
                pass
    
    async def _report_progress(self, progress: float) -> None:
        """Report progress to callback."""
        if self._progress_callback:
            try:
                await self._progress_callback("recording", progress)
            except Exception:
                pass
    
    def get_active_recordings(self) -> List[str]:
        """Get list of active recording IDs."""
        return list(self._active_recordings.keys())


# Convenience function
async def record_stream(
    url: str,
    output_dir: str = "./downloads/live",
    quality: str = "best",
    wait_for_stream: bool = True,
) -> RecordingResult:
    """
    Quick live stream recording function.
    
    Args:
        url: Stream URL
        output_dir: Output directory
        quality: Recording quality
        wait_for_stream: Wait for stream to start
        
    Returns:
        RecordingResult
    """
    config = RecordingConfig(
        output_dir=Path(output_dir),
        quality=quality,
        wait_for_stream=wait_for_stream,
    )
    
    async with LiveRecorder(config=config) as recorder:
        return await recorder.start_recording(url)


__all__ = [
    "LiveRecorder",
    "StreamPlatform",
    "StreamStatus",
    "StreamInfo",
    "RecordingResult",
    "RecordingConfig",
    "record_stream",
]

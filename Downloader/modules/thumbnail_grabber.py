"""
OMNIPOTENT SOVEREIGN NEXUS - Thumbnail Grabber Module
Version: v3.0.1 ULTIMATE NEXUS

Advanced thumbnail extraction with support for:
- Multiple platforms (YouTube, Vimeo, Dailymotion, etc.)
- Multiple quality options (Maxres, High, Medium, Low, Default)
- Multiple format support (JPG, PNG, WebP)
- Batch extraction from playlists
- Automatic resizing and conversion
- Proxy support
- Local file extraction from video files

Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
"""

import asyncio
import aiohttp
import aiofiles
import logging
import re
import time
import hashlib
import shutil
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
    Awaitable,
    BinaryIO,
)
from io import BytesIO
from PIL import Image
import subprocess


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)


class ThumbnailQuality(Enum):
    """Thumbnail quality/size options."""
    
    MAXRES = auto()      # Maximum resolution (3840x2160 or higher)
    SD = auto()          # Standard definition (640x480)
    HQ = auto()          # High quality (480x360)
    MQ = auto()          # Medium quality (320x180)
    DEFAULT = auto()     # Default quality (120x90)
    ORIGINAL = auto()    # Original quality (as uploaded)
    
    @property
    def resolution(self) -> Tuple[int, int]:
        """Return expected resolution."""
        resolutions = {
            ThumbnailQuality.MAXRES: (3840, 2160),
            ThumbnailQuality.SD: (640, 480),
            ThumbnailQuality.HQ: (480, 360),
            ThumbnailQuality.MQ: (320, 180),
            ThumbnailQuality.DEFAULT: (120, 90),
            ThumbnailQuality.ORIGINAL: (0, 0),  # Variable
        }
        return resolutions.get(self, (0, 0))


class ThumbnailFormat(Enum):
    """Supported thumbnail formats."""
    
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    BMP = "bmp"
    TIFF = "tiff"
    GIF = "gif"
    
    @property
    def mime_type(self) -> str:
        """Return MIME type."""
        mime_types = {
            ThumbnailFormat.JPG: "image/jpeg",
            ThumbnailFormat.JPEG: "image/jpeg",
            ThumbnailFormat.PNG: "image/png",
            ThumbnailFormat.WEBP: "image/webp",
            ThumbnailFormat.BMP: "image/bmp",
            ThumbnailFormat.TIFF: "image/tiff",
            ThumbnailFormat.GIF: "image/gif",
        }
        return mime_types.get(self, "image/jpeg")
    
    @property
    def extension(self) -> str:
        """Return file extension."""
        return self.value
    
    @property
    def pil_format(self) -> str:
        """Return PIL format string."""
        pil_formats = {
            ThumbnailFormat.JPG: "JPEG",
            ThumbnailFormat.JPEG: "JPEG",
            ThumbnailFormat.PNG: "PNG",
            ThumbnailFormat.WEBP: "WEBP",
            ThumbnailFormat.BMP: "BMP",
            ThumbnailFormat.TIFF: "TIFF",
            ThumbnailFormat.GIF: "GIF",
        }
        return pil_formats.get(self, "JPEG")


@dataclass
class ThumbnailResult:
    """
    Thumbnail extraction result.
    
    Attributes:
        success: Whether extraction succeeded
        filepath: Path to saved thumbnail
        filename: Filename
        url: Source URL or video path
        video_id: Video ID
        quality: Thumbnail quality
        format: Thumbnail format
        width: Image width
        height: Image height
        file_size: File size in bytes
        error_message: Error message if failed
        timestamp: Extraction timestamp
        checksum: File checksum
    """
    success: bool
    filepath: Optional[Path] = None
    filename: Optional[str] = None
    url: str = ""
    video_id: str = ""
    quality: ThumbnailQuality = ThumbnailQuality.ORIGINAL
    format: ThumbnailFormat = ThumbnailFormat.JPG
    width: int = 0
    height: int = 0
    file_size: int = 0
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    checksum: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "filepath": str(self.filepath) if self.filepath else None,
            "filename": self.filename,
            "url": self.url,
            "video_id": self.video_id,
            "quality": self.quality.name,
            "format": self.format.value,
            "width": self.width,
            "height": self.height,
            "file_size": self.file_size,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
            "checksum": self.checksum,
        }


@dataclass
class ThumbnailConfig:
    """
    Configuration for thumbnail extraction.
    
    Attributes:
        output_dir: Output directory
        filename_template: Filename template
        quality: Target quality
        format: Target format
        resize: Optional resize dimensions (width, height)
        maintain_aspect: Maintain aspect ratio when resizing
        optimize: Optimize output image
        quality_percent: JPEG/WebP quality percentage
        proxy: Proxy URL
        timeout: Request timeout
        retries: Number of retries
        extract_embedded: Extract embedded thumbnails from video files
        ffmpeg_path: Path to ffmpeg
    """
    output_dir: Path = Path("./downloads/thumbnails")
    filename_template: str = "%(id)s_%(quality)s.%(ext)s"
    quality: ThumbnailQuality = ThumbnailQuality.MAXRES
    format: ThumbnailFormat = ThumbnailFormat.JPG
    resize: Optional[Tuple[int, int]] = None
    maintain_aspect: bool = True
    optimize: bool = True
    quality_percent: int = 95
    proxy: Optional[str] = None
    timeout: float = 30.0
    retries: int = 3
    extract_embedded: bool = True
    ffmpeg_path: Optional[str] = None


class ThumbnailGrabber:
    """
    OMNIPOTENT SOVEREIGN NEXUS Thumbnail Grabber.
    
    Advanced thumbnail extraction with comprehensive features:
    - Multi-platform URL support
    - Multiple quality options
    - Format conversion
    - Resizing and optimization
    - Batch extraction
    - Local video file support
    """
    
    # Platform-specific thumbnail URL patterns
    THUMBNAIL_PATTERNS = {
        'youtube': {
            'patterns': [
                r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
                r'youtu\.be/([a-zA-Z0-9_-]{11})',
                r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            ],
            'url_template': 'https://img.youtube.com/vi/{id}/{quality}.jpg',
            'quality_map': {
                ThumbnailQuality.MAXRES: 'maxresdefault',
                ThumbnailQuality.SD: 'sddefault',
                ThumbnailQuality.HQ: 'hqdefault',
                ThumbnailQuality.MQ: 'mqdefault',
                ThumbnailQuality.DEFAULT: 'default',
            }
        },
        'vimeo': {
            'patterns': [r'vimeo\.com/(\d+)'],
            'api_url': 'https://vimeo.com/api/v2/video/{id}.json',
        },
        'dailymotion': {
            'patterns': [r'dailymotion\.com/video/([a-zA-Z0-9]+)'],
            'url_template': 'https://www.dailymotion.com/thumbnail/video/{id}',
        },
    }
    
    def __init__(
        self,
        config: Optional[ThumbnailConfig] = None,
        progress_callback: Optional[Callable[[str, float], Awaitable[None]]] = None,
    ) -> None:
        """
        Initialize the thumbnail grabber.
        
        Args:
            config: Extraction configuration
            progress_callback: Progress callback (url, percentage)
        """
        self.config = config or ThumbnailConfig()
        self._progress_callback = progress_callback
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ThumbnailGrabber initialized v3.0.1 ULTIMATE NEXUS")
    
    async def __aenter__(self) -> "ThumbnailGrabber":
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
            connector = aiohttp.TCPConnector(limit=10)
            
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                trust_env=True,
            )
    
    async def close(self) -> None:
        """Close the grabber."""
        if self._session and not self._session.closed:
            await self._session.close()
        logger.info("ThumbnailGrabber closed")
    
    def _extract_video_id(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract video ID and platform from URL.
        
        Returns:
            Tuple of (video_id, platform)
        """
        url_lower = url.lower()
        
        for platform, data in self.THUMBNAIL_PATTERNS.items():
            for pattern in data['patterns']:
                match = re.search(pattern, url_lower)
                if match:
                    return match.group(1), platform
        
        return None, None
    
    def _get_thumbnail_url(
        self,
        video_id: str,
        platform: str,
        quality: ThumbnailQuality,
    ) -> Optional[str]:
        """Get thumbnail URL for video ID."""
        if platform == 'youtube':
            data = self.THUMBNAIL_PATTERNS['youtube']
            quality_name = data['quality_map'].get(quality, 'hqdefault')
            return data['url_template'].format(id=video_id, quality=quality_name)
        
        elif platform == 'vimeo':
            # Vimeo requires API call
            return None
        
        elif platform == 'dailymotion':
            data = self.THUMBNAIL_PATTERNS['dailymotion']
            return data['url_template'].format(id=video_id)
        
        return None
    
    async def get_thumbnail_url(
        self,
        url: str,
        quality: ThumbnailQuality = ThumbnailQuality.MAXRES,
    ) -> Optional[str]:
        """
        Get direct thumbnail URL from video URL.
        
        Args:
            url: Video URL
            quality: Desired quality
            
        Returns:
            Direct thumbnail URL or None
        """
        video_id, platform = self._extract_video_id(url)
        
        if not video_id or not platform:
            # Try using yt-dlp for other platforms
            return await self._get_thumbnail_url_yt_dlp(url)
        
        if platform == 'vimeo':
            return await self._get_vimeo_thumbnail_url(video_id)
        
        return self._get_thumbnail_url(video_id, platform, quality)
    
    async def _get_thumbnail_url_yt_dlp(self, url: str) -> Optional[str]:
        """Get thumbnail URL using yt-dlp."""
        yt_dlp = shutil.which("yt-dlp")
        if not yt_dlp:
            return None
        
        try:
            process = await asyncio.create_subprocess_exec(
                yt_dlp,
                "--get-thumbnail",
                "--no-download",
                url,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, _ = await process.communicate()
            
            if process.returncode == 0:
                return stdout.decode().strip()
            
        except Exception as e:
            logger.warning(f"Failed to get thumbnail URL: {e}")
        
        return None
    
    async def _get_vimeo_thumbnail_url(self, video_id: str) -> Optional[str]:
        """Get Vimeo thumbnail URL via API."""
        try:
            async with self._session.get(
                f"https://vimeo.com/api/v2/video/{video_id}.json"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        return data[0].get('thumbnail_large')
        except Exception as e:
            logger.warning(f"Failed to get Vimeo thumbnail: {e}")
        
        return None
    
    async def grab(
        self,
        url: str,
        output_filename: Optional[str] = None,
        quality: Optional[ThumbnailQuality] = None,
        format: Optional[ThumbnailFormat] = None,
    ) -> ThumbnailResult:
        """
        Grab thumbnail from URL.
        
        Args:
            url: Video URL
            output_filename: Custom output filename
            quality: Override quality
            format: Override format
            
        Returns:
            ThumbnailResult
        """
        target_quality = quality or self.config.quality
        target_format = format or self.config.format
        
        try:
            # Get video ID
            video_id, platform = self._extract_video_id(url)
            
            if not video_id:
                # Try yt-dlp
                thumbnail_url = await self._get_thumbnail_url_yt_dlp(url)
                if not thumbnail_url:
                    return ThumbnailResult(
                        success=False,
                        url=url,
                        error_message="Could not extract video ID or thumbnail URL",
                    )
                video_id = hashlib.md5(url.encode()).hexdigest()[:8]
            else:
                # Get direct thumbnail URL
                thumbnail_url = self._get_thumbnail_url(video_id, platform, target_quality)
                
                if not thumbnail_url and platform == 'vimeo':
                    thumbnail_url = await self._get_vimeo_thumbnail_url(video_id)
                
                if not thumbnail_url:
                    return ThumbnailResult(
                        success=False,
                        url=url,
                        video_id=video_id,
                        error_message="Could not construct thumbnail URL",
                    )
            
            # Download thumbnail
            image_data = await self._download_image(thumbnail_url)
            
            if not image_data:
                return ThumbnailResult(
                    success=False,
                    url=url,
                    video_id=video_id,
                    error_message="Failed to download thumbnail",
                )
            
            # Process image
            image = await self._process_image(image_data, target_format)
            
            if not image:
                return ThumbnailResult(
                    success=False,
                    url=url,
                    video_id=video_id,
                    error_message="Failed to process image",
                )
            
            # Generate filename
            filename = output_filename or self._generate_filename(
                video_id, target_quality, target_format
            )
            filepath = self.config.output_dir / filename
            
            # Save image
            await self._save_image(image, filepath, target_format)
            
            # Get image dimensions
            width, height = image.size
            
            # Calculate checksum
            checksum = hashlib.md5(image_data).hexdigest()
            
            return ThumbnailResult(
                success=True,
                filepath=filepath,
                filename=filename,
                url=url,
                video_id=video_id,
                quality=target_quality,
                format=target_format,
                width=width,
                height=height,
                file_size=filepath.stat().st_size,
                checksum=checksum,
            )
            
        except Exception as e:
            logger.error(f"Thumbnail grab error: {e}")
            return ThumbnailResult(
                success=False,
                url=url,
                error_message=str(e),
            )
    
    async def _download_image(self, url: str) -> Optional[bytes]:
        """Download image from URL with retries."""
        for attempt in range(self.config.retries):
            try:
                async with self._session.get(url) as response:
                    if response.status == 200:
                        return await response.read()
                    elif response.status == 404:
                        # Try fallback quality for YouTube
                        if 'maxresdefault' in url:
                            url = url.replace('maxresdefault', 'hqdefault')
                            continue
            except Exception as e:
                logger.warning(f"Download attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(self.config.timeout * (attempt + 1))
        
        return None
    
    async def _process_image(
        self,
        image_data: bytes,
        target_format: ThumbnailFormat,
    ) -> Optional[Image.Image]:
        """Process image with optional resizing."""
        try:
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'P') and target_format in {
                ThumbnailFormat.JPG, ThumbnailFormat.JPEG
            }:
                # Create white background for transparency
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Resize if configured
            if self.config.resize:
                width, height = self.config.resize
                if self.config.maintain_aspect:
                    image.thumbnail((width, height), Image.Resampling.LANCZOS)
                else:
                    image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            logger.error(f"Image processing error: {e}")
            return None
    
    async def _save_image(
        self,
        image: Image.Image,
        filepath: Path,
        target_format: ThumbnailFormat,
    ) -> None:
        """Save image to file."""
        save_kwargs = {
            'format': target_format.pil_format,
        }
        
        if target_format in {ThumbnailFormat.JPG, ThumbnailFormat.JPEG, ThumbnailFormat.WEBP}:
            save_kwargs['quality'] = self.config.quality_percent
            if self.config.optimize:
                save_kwargs['optimize'] = True
        
        if target_format == ThumbnailFormat.PNG:
            save_kwargs['compress_level'] = 9
        
        image.save(filepath, **save_kwargs)
    
    def _generate_filename(
        self,
        video_id: str,
        quality: ThumbnailQuality,
        format: ThumbnailFormat,
    ) -> str:
        """Generate output filename."""
        template = self.config.filename_template
        filename = template.replace('%(id)s', video_id)
        filename = filename.replace('%(quality)s', quality.name.lower())
        filename = filename.replace('%(ext)s', format.extension)
        return filename
    
    async def grab_from_file(
        self,
        video_path: Path,
        timestamp: float = 0.0,
        output_filename: Optional[str] = None,
    ) -> ThumbnailResult:
        """
        Extract thumbnail from local video file.
        
        Args:
            video_path: Path to video file
            timestamp: Timestamp in seconds
            output_filename: Custom output filename
            
        Returns:
            ThumbnailResult
        """
        ffmpeg = self.config.ffmpeg_path or shutil.which("ffmpeg")
        
        if not ffmpeg:
            return ThumbnailResult(
                success=False,
                url=str(video_path),
                error_message="ffmpeg not found",
            )
        
        try:
            filename = output_filename or f"{video_path.stem}_thumb.jpg"
            output_path = self.config.output_dir / filename
            
            # Build ffmpeg command
            cmd = [
                ffmpeg,
                "-ss", str(timestamp),
                "-i", str(video_path),
                "-vframes", "1",
                "-q:v", "2",
                "-y",
                str(output_path),
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            await process.communicate()
            
            if process.returncode == 0 and output_path.exists():
                # Get image dimensions
                with Image.open(output_path) as img:
                    width, height = img.size
                
                return ThumbnailResult(
                    success=True,
                    filepath=output_path,
                    filename=filename,
                    url=str(video_path),
                    format=self.config.format,
                    width=width,
                    height=height,
                    file_size=output_path.stat().st_size,
                )
            
            return ThumbnailResult(
                success=False,
                url=str(video_path),
                error_message="ffmpeg extraction failed",
            )
            
        except Exception as e:
            logger.error(f"File thumbnail extraction error: {e}")
            return ThumbnailResult(
                success=False,
                url=str(video_path),
                error_message=str(e),
            )
    
    async def grab_multiple(
        self,
        urls: List[str],
        max_concurrent: int = 5,
    ) -> List[ThumbnailResult]:
        """
        Grab thumbnails from multiple URLs.
        
        Args:
            urls: List of video URLs
            max_concurrent: Maximum concurrent downloads
            
        Returns:
            List of results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def grab_with_semaphore(url: str) -> ThumbnailResult:
            async with semaphore:
                return await self.grab(url)
        
        tasks = [grab_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            r if isinstance(r, ThumbnailResult) else ThumbnailResult(
                success=False,
                url=urls[i],
                error_message=str(r),
            )
            for i, r in enumerate(results)
        ]
    
    async def grab_all_qualities(
        self,
        url: str,
        qualities: Optional[List[ThumbnailQuality]] = None,
    ) -> List[ThumbnailResult]:
        """
        Grab thumbnails in all available qualities.
        
        Args:
            url: Video URL
            qualities: Specific qualities to grab
            
        Returns:
            List of results
        """
        qualities = qualities or list(ThumbnailQuality)
        tasks = [self.grab(url, quality=q) for q in qualities]
        return list(await asyncio.gather(*tasks, return_exceptions=True))


# Convenience function
async def grab_thumbnail(
    url: str,
    output_dir: str = "./downloads/thumbnails",
    quality: ThumbnailQuality = ThumbnailQuality.MAXRES,
) -> ThumbnailResult:
    """
    Quick thumbnail grab function.
    
    Args:
        url: Video URL
        output_dir: Output directory
        quality: Target quality
        
    Returns:
        ThumbnailResult
    """
    config = ThumbnailConfig(
        output_dir=Path(output_dir),
        quality=quality,
    )
    
    async with ThumbnailGrabber(config=config) as grabber:
        return await grabber.grab(url)


__all__ = [
    "ThumbnailGrabber",
    "ThumbnailQuality",
    "ThumbnailFormat",
    "ThumbnailResult",
    "ThumbnailConfig",
    "grab_thumbnail",
]

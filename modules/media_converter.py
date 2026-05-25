"""
OMNIPOTENT SOVEREIGN NEXUS - Media Converter Module
Version: v3.0.1 ULTIMATE NEXUS

Advanced media conversion with support for:
- Video format conversion (MP4, WebM, MKV, AVI, etc.)
- Audio format conversion (MP3, AAC, FLAC, WAV, etc.)
- Quality presets and custom settings
- Batch conversion with parallel processing
- Hardware acceleration (NVENC, VAAPI, VTB)
- Audio/video extraction
- Subtitle burning and extraction
- Thumbnail generation from video
- Video trimming and concatenation

Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
"""

import asyncio
import aiofiles
import logging
import re
import json
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
)
from concurrent.futures import ThreadPoolExecutor
import subprocess


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)


class ConversionFormat(Enum):
    """Supported conversion formats."""
    
    # Video formats
    MP4 = "mp4"
    WEBM = "webm"
    MKV = "mkv"
    AVI = "avi"
    MOV = "mov"
    FLV = "flv"
    WMV = "wmv"
    TS = "ts"
    M4V = "m4v"
    OGV = "ogv"
    
    # Audio formats
    MP3 = "mp3"
    AAC = "aac"
    M4A = "m4a"
    FLAC = "flac"
    WAV = "wav"
    OGG = "ogg"
    OPUS = "opus"
    WMA = "wma"
    AIFF = "aiff"
    
    @property
    def is_video(self) -> bool:
        """Check if video format."""
        return self in {
            ConversionFormat.MP4,
            ConversionFormat.WEBM,
            ConversionFormat.MKV,
            ConversionFormat.AVI,
            ConversionFormat.MOV,
            ConversionFormat.FLV,
            ConversionFormat.WMV,
            ConversionFormat.TS,
            ConversionFormat.M4V,
            ConversionFormat.OGV,
        }
    
    @property
    def is_audio(self) -> bool:
        """Check if audio format."""
        return not self.is_video
    
    @property
    def default_codec(self) -> str:
        """Return default codec for format."""
        codecs = {
            ConversionFormat.MP4: "libx264",
            ConversionFormat.WEBM: "libvpx-vp9",
            ConversionFormat.MKV: "libx264",
            ConversionFormat.AVI: "mpeg4",
            ConversionFormat.MOV: "libx264",
            ConversionFormat.FLV: "flv",
            ConversionFormat.MP3: "libmp3lame",
            ConversionFormat.AAC: "aac",
            ConversionFormat.M4A: "aac",
            ConversionFormat.FLAC: "flac",
            ConversionFormat.WAV: "pcm_s16le",
            ConversionFormat.OGG: "libvorbis",
            ConversionFormat.OPUS: "libopus",
        }
        return codecs.get(self, "copy")


class ConversionPreset(Enum):
    """Conversion quality presets."""
    
    ULTRA_FAST = "ultra_fast"
    FAST = "fast"
    BALANCED = "balanced"
    QUALITY = "quality"
    BEST_QUALITY = "best_quality"
    CUSTOM = "custom"
    
    @property
    def ffmpeg_preset(self) -> str:
        """Return ffmpeg preset value."""
        presets = {
            ConversionPreset.ULTRA_FAST: "ultrafast",
            ConversionPreset.FAST: "fast",
            ConversionPreset.BALANCED: "medium",
            ConversionPreset.QUALITY: "slow",
            ConversionPreset.BEST_QUALITY: "veryslow",
        }
        return presets.get(self, "medium")


class HardwareAcceleration(Enum):
    """Hardware acceleration options."""
    
    NONE = "none"
    NVENC = "nvenc"      # NVIDIA
    VAAPI = "vaapi"      # Linux VAAPI
    VTB = "videotoolbox" # macOS
    QSV = "qsv"          # Intel QuickSync
    AMF = "amf"          # AMD
    
    @property
    def ffmpeg_codec(self) -> Optional[str]:
        """Return ffmpeg hardware codec."""
        codecs = {
            HardwareAcceleration.NVENC: "h264_nvenc",
            HardwareAcceleration.VAAPI: "h264_vaapi",
            HardwareAcceleration.VTB: "h264_videotoolbox",
            HardwareAcceleration.QSV: "h264_qsv",
            HardwareAcceleration.AMF: "h264_amf",
        }
        return codecs.get(self)


@dataclass
class ConversionResult:
    """
    Conversion result information.
    
    Attributes:
        success: Whether conversion succeeded
        input_path: Input file path
        output_path: Output file path
        output_format: Output format
        file_size: Output file size
        duration: Processing duration
        original_size: Original file size
        compression_ratio: Compression ratio
        bitrate: Output bitrate
        error_message: Error message if failed
        timestamp: Completion timestamp
    """
    success: bool
    input_path: Optional[Path] = None
    output_path: Optional[Path] = None
    output_format: ConversionFormat = ConversionFormat.MP4
    file_size: int = 0
    duration: float = 0.0
    original_size: int = 0
    compression_ratio: float = 0.0
    bitrate: int = 0
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def saved_bytes(self) -> int:
        """Return bytes saved by conversion."""
        return self.original_size - self.file_size
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "input_path": str(self.input_path) if self.input_path else None,
            "output_path": str(self.output_path) if self.output_path else None,
            "output_format": self.output_format.value,
            "file_size": self.file_size,
            "duration": self.duration,
            "original_size": self.original_size,
            "compression_ratio": self.compression_ratio,
            "saved_bytes": self.saved_bytes,
            "bitrate": self.bitrate,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ConversionProgress:
    """
    Conversion progress information.
    
    Attributes:
        input_file: Input file path
        output_file: Output file path
        percentage: Conversion progress percentage
        current_time: Current processing time
        total_time: Total duration
        speed: Processing speed
        eta: Estimated time remaining
        frame: Current frame number
        fps: Processing FPS
        bitrate: Current bitrate
    """
    input_file: str
    output_file: str
    percentage: float = 0.0
    current_time: float = 0.0
    total_time: float = 0.0
    speed: float = 0.0
    eta: float = 0.0
    frame: int = 0
    fps: float = 0.0
    bitrate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "input_file": self.input_file,
            "output_file": self.output_file,
            "percentage": self.percentage,
            "current_time": self.current_time,
            "total_time": self.total_time,
            "speed": self.speed,
            "eta": self.eta,
            "frame": self.frame,
            "fps": self.fps,
            "bitrate": self.bitrate,
        }


@dataclass
class ConversionConfig:
    """
    Configuration for media conversion.
    
    Attributes:
        output_format: Target format
        output_dir: Output directory
        preset: Quality preset
        video_codec: Video codec override
        audio_codec: Audio codec override
        video_bitrate: Video bitrate (kbps)
        audio_bitrate: Audio bitrate (kbps)
        resolution: Target resolution (width, height)
        fps: Target FPS
        crf: Constant Rate Factor (0-51, lower = better)
        hwaccel: Hardware acceleration
        copy_audio: Copy audio stream without re-encoding
        copy_video: Copy video stream without re-encoding
        remove_audio: Remove audio stream
        remove_video: Remove video stream
        start_time: Start time for trimming (seconds)
        end_time: End time for trimming (seconds)
        subtitle_file: Subtitle file to burn
        subtitle_burn: Burn subtitles into video
        metadata: Metadata to embed
        ffmpeg_path: Path to ffmpeg
        ffprobe_path: Path to ffprobe
        overwrite: Overwrite existing files
        keep_original: Keep original file
    """
    output_format: ConversionFormat = ConversionFormat.MP4
    output_dir: Path = Path("./converted")
    preset: ConversionPreset = ConversionPreset.BALANCED
    video_codec: Optional[str] = None
    audio_codec: Optional[str] = None
    video_bitrate: Optional[int] = None
    audio_bitrate: Optional[int] = None
    resolution: Optional[Tuple[int, int]] = None
    fps: Optional[int] = None
    crf: int = 23
    hwaccel: HardwareAcceleration = HardwareAcceleration.NONE
    copy_audio: bool = False
    copy_video: bool = False
    remove_audio: bool = False
    remove_video: bool = False
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    subtitle_file: Optional[Path] = None
    subtitle_burn: bool = False
    metadata: Dict[str, str] = field(default_factory=dict)
    ffmpeg_path: Optional[str] = None
    ffprobe_path: Optional[str] = None
    overwrite: bool = True
    keep_original: bool = True


class MediaConverter:
    """
    OMNIPOTENT SOVEREIGN NEXUS Media Converter.
    
    Advanced media conversion with comprehensive features:
    - Multiple format support
    - Quality presets
    - Hardware acceleration
    - Batch conversion
    - Trimming and concatenation
    """
    
    def __init__(
        self,
        config: Optional[ConversionConfig] = None,
        progress_callback: Optional[Callable[[ConversionProgress], Awaitable[None]]] = None,
    ) -> None:
        """
        Initialize the media converter.
        
        Args:
            config: Conversion configuration
            progress_callback: Progress update callback
        """
        self.config = config or ConversionConfig()
        self._progress_callback = progress_callback
        self._active_conversions: Dict[str, subprocess.Process] = {}
        
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"MediaConverter initialized v3.0.1 ULTIMATE NEXUS")
    
    def _get_ffmpeg_path(self) -> Optional[str]:
        """Find ffmpeg executable."""
        if self.config.ffmpeg_path:
            return self.config.ffmpeg_path
        
        return shutil.which("ffmpeg")
    
    def _get_ffprobe_path(self) -> Optional[str]:
        """Find ffprobe executable."""
        if self.config.ffprobe_path:
            return self.config.ffprobe_path
        
        return shutil.which("ffprobe")
    
    async def convert(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        output_format: Optional[ConversionFormat] = None,
    ) -> ConversionResult:
        """
        Convert media file to another format.
        
        Args:
            input_path: Input file path
            output_path: Output file path
            output_format: Override output format
            
        Returns:
            ConversionResult
        """
        start_time = datetime.now()
        
        ffmpeg = self._get_ffmpeg_path()
        if not ffmpeg:
            return ConversionResult(
                success=False,
                input_path=input_path,
                error_message="ffmpeg not found",
            )
        
        target_format = output_format or self.config.output_format
        
        # Generate output path if not provided
        if not output_path:
            output_filename = f"{input_path.stem}.{target_format.value}"
            output_path = self.config.output_dir / output_filename
        
        try:
            # Get original file info
            original_size = input_path.stat().st_size
            media_info = await self._get_media_info(input_path)
            
            # Build ffmpeg command
            cmd = self._build_ffmpeg_command(
                input_path=input_path,
                output_path=output_path,
                output_format=target_format,
                media_info=media_info,
            )
            
            # Execute conversion
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            # Monitor progress
            await self._monitor_conversion(process, str(input_path), str(output_path), media_info)
            
            # Wait for completion
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0 and output_path.exists():
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                output_size = output_path.stat().st_size
                
                return ConversionResult(
                    success=True,
                    input_path=input_path,
                    output_path=output_path,
                    output_format=target_format,
                    file_size=output_size,
                    duration=duration,
                    original_size=original_size,
                    compression_ratio=output_size / original_size if original_size > 0 else 0,
                )
            else:
                error_msg = stderr.decode() if stderr else "Unknown error"
                return ConversionResult(
                    success=False,
                    input_path=input_path,
                    output_path=output_path,
                    output_format=target_format,
                    error_message=error_msg[:500],
                )
            
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return ConversionResult(
                success=False,
                input_path=input_path,
                error_message=str(e),
            )
    
    def _build_ffmpeg_command(
        self,
        input_path: Path,
        output_path: Path,
        output_format: ConversionFormat,
        media_info: Dict[str, Any],
    ) -> List[str]:
        """Build ffmpeg conversion command."""
        ffmpeg = self._get_ffmpeg_path()
        cmd = [ffmpeg, "-y"]  # Overwrite output
        
        # Input file
        cmd.extend(["-i", str(input_path)])
        
        # Start time for trimming
        if self.config.start_time is not None:
            cmd.extend(["-ss", str(self.config.start_time)])
        
        # End time for trimming
        if self.config.end_time is not None:
            cmd.extend(["-t", str(self.config.end_time - (self.config.start_time or 0))])
        
        # Subtitle burning
        if self.config.subtitle_file and self.config.subtitle_burn:
            cmd.extend(["-vf", f"subtitles={self.config.subtitle_file}"])
        
        # Video settings
        if output_format.is_video and not self.config.remove_video:
            if self.config.copy_video:
                cmd.extend(["-vcodec", "copy"])
            else:
                # Video codec
                if self.config.video_codec:
                    codec = self.config.video_codec
                elif self.config.hwaccel != HardwareAcceleration.NONE:
                    codec = self.config.hwaccel.ffmpeg_codec or "libx264"
                else:
                    codec = output_format.default_codec
                
                cmd.extend(["-vcodec", codec])
                
                # Preset
                if codec in ["libx264", "libx265", "libvpx-vp9"]:
                    cmd.extend(["-preset", self.config.preset.ffmpeg_preset])
                
                # CRF or bitrate
                if self.config.video_bitrate:
                    cmd.extend(["-b:v", f"{self.config.video_bitrate}k"])
                else:
                    cmd.extend(["-crf", str(self.config.crf)])
                
                # Resolution
                if self.config.resolution:
                    width, height = self.config.resolution
                    cmd.extend(["-vf", f"scale={width}:{height}"])
                
                # FPS
                if self.config.fps:
                    cmd.extend(["-r", str(self.config.fps)])
        
        # Audio settings
        if not self.config.remove_audio:
            if self.config.copy_audio:
                cmd.extend(["-acodec", "copy"])
            else:
                # Audio codec
                if self.config.audio_codec:
                    codec = self.config.audio_codec
                else:
                    codec = "aac" if output_format.is_video else output_format.default_codec
                
                cmd.extend(["-acodec", codec])
                
                # Audio bitrate
                if self.config.audio_bitrate:
                    cmd.extend(["-b:a", f"{self.config.audio_bitrate}k"])
        
        # Remove streams
        if self.config.remove_video:
            cmd.extend(["-vn"])
        if self.config.remove_audio:
            cmd.extend(["-an"])
        
        # Metadata
        for key, value in self.config.metadata.items():
            cmd.extend(["-metadata", f"{key}={value}"])
        
        # Output file
        cmd.append(str(output_path))
        
        return cmd
    
    async def _get_media_info(self, filepath: Path) -> Dict[str, Any]:
        """Get media file information using ffprobe."""
        ffprobe = self._get_ffprobe_path()
        if not ffprobe:
            return {}
        
        try:
            cmd = [
                ffprobe,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                str(filepath),
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, _ = await process.communicate()
            
            if process.returncode == 0:
                return json.loads(stdout.decode())
            
        except Exception as e:
            logger.warning(f"Failed to get media info: {e}")
        
        return {}
    
    async def _monitor_conversion(
        self,
        process: asyncio.subprocess.Process,
        input_file: str,
        output_file: str,
        media_info: Dict[str, Any],
    ) -> None:
        """Monitor conversion progress."""
        total_duration = float(
            media_info.get("format", {}).get("duration", 0)
        )
        
        if self._progress_callback and total_duration > 0:
            progress = ConversionProgress(
                input_file=input_file,
                output_file=output_file,
                total_time=total_duration,
            )
            
            # Read stderr for progress
            while True:
                line = await process.stderr.readline()
                if not line:
                    break
                
                line = line.decode()
                
                # Parse ffmpeg progress
                if "time=" in line:
                    match = re.search(r"time=(\d+):(\d+):(\d+\.?\d*)", line)
                    if match:
                        hours, minutes, seconds = match.groups()
                        current = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                        
                        progress.current_time = current
                        progress.percentage = (current / total_duration) * 100
                        
                        # Parse speed
                        speed_match = re.search(r"speed=(\d+\.?\d*)x", line)
                        if speed_match:
                            progress.speed = float(speed_match.group(1))
                        
                        try:
                            await self._progress_callback(progress)
                        except Exception:
                            pass
    
    async def convert_multiple(
        self,
        input_files: List[Path],
        output_format: Optional[ConversionFormat] = None,
        max_concurrent: int = 1,
    ) -> List[ConversionResult]:
        """
        Convert multiple files.
        
        Args:
            input_files: List of input files
            output_format: Output format
            max_concurrent: Maximum concurrent conversions
            
        Returns:
            List of results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def convert_with_semaphore(filepath: Path) -> ConversionResult:
            async with semaphore:
                return await self.convert(filepath, output_format=output_format)
        
        tasks = [convert_with_semaphore(fp) for fp in input_files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            r if isinstance(r, ConversionResult) else ConversionResult(
                success=False,
                input_path=input_files[i],
                error_message=str(r),
            )
            for i, r in enumerate(results)
        ]
    
    async def extract_audio(
        self,
        video_path: Path,
        audio_format: ConversionFormat = ConversionFormat.MP3,
        audio_bitrate: int = 320,
    ) -> ConversionResult:
        """
        Extract audio from video file.
        
        Args:
            video_path: Video file path
            audio_format: Audio format
            audio_bitrate: Audio bitrate in kbps
            
        Returns:
            ConversionResult
        """
        config = ConversionConfig(
            output_format=audio_format,
            remove_video=True,
            audio_bitrate=audio_bitrate,
            output_dir=self.config.output_dir,
        )
        
        converter = MediaConverter(config=config)
        return await converter.convert(video_path)
    
    async def trim(
        self,
        input_path: Path,
        start_time: float,
        end_time: float,
        output_path: Optional[Path] = None,
    ) -> ConversionResult:
        """
        Trim media file.
        
        Args:
            input_path: Input file path
            start_time: Start time in seconds
            end_time: End time in seconds
            output_path: Output file path
            
        Returns:
            ConversionResult
        """
        config = ConversionConfig(
            output_format=self._get_format_from_path(input_path),
            start_time=start_time,
            end_time=end_time,
            copy_video=True,
            copy_audio=True,
            output_dir=self.config.output_dir,
        )
        
        converter = MediaConverter(config=config)
        return await converter.convert(input_path, output_path)
    
    def _get_format_from_path(self, filepath: Path) -> ConversionFormat:
        """Get conversion format from file extension."""
        ext = filepath.suffix.lstrip('.').lower()
        
        for fmt in ConversionFormat:
            if fmt.value == ext:
                return fmt
        
        return ConversionFormat.MP4
    
    async def concatenate(
        self,
        input_files: List[Path],
        output_path: Path,
    ) -> ConversionResult:
        """
        Concatenate multiple media files.
        
        Args:
            input_files: List of input files
            output_path: Output file path
            
        Returns:
            ConversionResult
        """
        ffmpeg = self._get_ffmpeg_path()
        if not ffmpeg:
            return ConversionResult(
                success=False,
                error_message="ffmpeg not found",
            )
        
        try:
            # Create file list
            list_file = self.config.output_dir / "concat_list.txt"
            
            async with aiofiles.open(list_file, 'w') as f:
                for fp in input_files:
                    await f.write(f"file '{fp.absolute()}'\n")
            
            # Build command
            cmd = [
                ffmpeg, "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(list_file),
                "-c", "copy",
                str(output_path),
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            await process.communicate()
            
            # Clean up
            list_file.unlink()
            
            if process.returncode == 0 and output_path.exists():
                return ConversionResult(
                    success=True,
                    output_path=output_path,
                    output_format=self._get_format_from_path(output_path),
                    file_size=output_path.stat().st_size,
                )
            
            return ConversionResult(
                success=False,
                output_path=output_path,
                error_message="Concatenation failed",
            )
            
        except Exception as e:
            return ConversionResult(
                success=False,
                error_message=str(e),
            )
    
    async def generate_thumbnails(
        self,
        video_path: Path,
        output_dir: Path,
        count: int = 10,
    ) -> List[Path]:
        """
        Generate thumbnails from video.
        
        Args:
            video_path: Video file path
            output_dir: Output directory
            count: Number of thumbnails
            
        Returns:
            List of thumbnail paths
        """
        ffmpeg = self._get_ffmpeg_path()
        if not ffmpeg:
            return []
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Get video duration
            media_info = await self._get_media_info(video_path)
            duration = float(media_info.get("format", {}).get("duration", 0))
            
            if duration == 0:
                return []
            
            # Calculate intervals
            interval = duration / (count + 1)
            
            thumbnails = []
            
            for i in range(1, count + 1):
                timestamp = interval * i
                output_path = output_dir / f"{video_path.stem}_thumb_{i:03d}.jpg"
                
                cmd = [
                    ffmpeg, "-y",
                    "-ss", str(timestamp),
                    "-i", str(video_path),
                    "-vframes", "1",
                    "-q:v", "2",
                    str(output_path),
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                
                await process.communicate()
                
                if process.returncode == 0 and output_path.exists():
                    thumbnails.append(output_path)
            
            return thumbnails
            
        except Exception as e:
            logger.error(f"Thumbnail generation error: {e}")
            return []
    
    async def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get supported input/output formats."""
        return {
            "video_input": ["mp4", "webm", "mkv", "avi", "mov", "flv", "wmv", "ts", "m4v", "ogv"],
            "video_output": ["mp4", "webm", "mkv", "avi", "mov", "flv", "wmv", "ts", "m4v", "ogv"],
            "audio_input": ["mp3", "aac", "m4a", "flac", "wav", "ogg", "opus", "wma", "aiff"],
            "audio_output": ["mp3", "aac", "m4a", "flac", "wav", "ogg", "opus", "wma", "aiff"],
        }


# Convenience functions
async def convert_media(
    input_path: str,
    output_format: ConversionFormat = ConversionFormat.MP4,
    output_dir: str = "./converted",
) -> ConversionResult:
    """
    Quick media conversion function.
    
    Args:
        input_path: Input file path
        output_format: Output format
        output_dir: Output directory
        
    Returns:
        ConversionResult
    """
    config = ConversionConfig(
        output_format=output_format,
        output_dir=Path(output_dir),
    )
    
    converter = MediaConverter(config=config)
    return await converter.convert(Path(input_path))


async def extract_audio(
    video_path: str,
    audio_format: ConversionFormat = ConversionFormat.MP3,
    output_dir: str = "./converted",
) -> ConversionResult:
    """
    Quick audio extraction function.
    
    Args:
        video_path: Video file path
        audio_format: Audio format
        output_dir: Output directory
        
    Returns:
        ConversionResult
    """
    config = ConversionConfig(
        output_format=audio_format,
        remove_video=True,
        output_dir=Path(output_dir),
    )
    
    converter = MediaConverter(config=config)
    return await converter.convert(Path(video_path))


__all__ = [
    "MediaConverter",
    "ConversionFormat",
    "ConversionPreset",
    "HardwareAcceleration",
    "ConversionResult",
    "ConversionProgress",
    "ConversionConfig",
    "convert_media",
    "extract_audio",
]

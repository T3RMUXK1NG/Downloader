"""
OMNIPOTENT SOVEREIGN NEXUS - Video Editor Module
Version: v3.0.1 ULTIMATE NEXUS

Video editing capabilities with support for:
- Trim and cut operations
- Merge and concatenate videos
- Add watermarks and logos
- Apply filters and effects
- Add text and titles
- Speed adjustment
- Audio replacement/mixing
- Crop and resize
- Rotation and flipping
- Transitions and fades

Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
"""

import asyncio
import aiofiles
import logging
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


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)


class TransitionType(Enum):
    """Video transition types."""
    
    NONE = "none"
    FADE = "fade"
    DISSOLVE = "dissolve"
    WIPE_LEFT = "wipe_left"
    WIPE_RIGHT = "wipe_right"
    WIPE_UP = "wipe_up"
    WIPE_DOWN = "wipe_down"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    BLUR = "blur"


class FilterType(Enum):
    """Video filter types."""
    
    NONE = "none"
    GRAYSCALE = "grayscale"
    SEPIA = "sepia"
    NEGATE = "negate"
    VINTAGE = "vintage"
    BRIGHTNESS = "brightness"
    CONTRAST = "contrast"
    SATURATION = "saturation"
    SHARPEN = "sharpen"
    BLUR = "blur"
    SHARPEN = "sharpen"
    NOISE_REDUCE = "noise_reduce"
    STABILIZE = "stabilize"


@dataclass
class TrimPoint:
    """
    Trim point for video editing.
    
    Attributes:
        start_time: Start time in seconds
        end_time: End time in seconds
    """
    start_time: float
    end_time: float
    
    @property
    def duration(self) -> float:
        """Return segment duration."""
        return self.end_time - self.start_time


@dataclass
class WatermarkConfig:
    """
    Watermark configuration.
    
    Attributes:
        image_path: Path to watermark image
        position: Position (x, y) or preset
        opacity: Opacity (0-1)
        scale: Scale factor
    """
    image_path: Path
    position: Tuple[int, int] = (10, 10)
    opacity: float = 0.8
    scale: float = 1.0


@dataclass
class TextOverlay:
    """
    Text overlay configuration.
    
    Attributes:
        text: Text content
        font_size: Font size
        font_color: Font color (RGB)
        position: Position (x, y)
        start_time: Start time in seconds
        end_time: End time in seconds
        background: Background color (optional)
        background_opacity: Background opacity
    """
    text: str
    font_size: int = 24
    font_color: Tuple[int, int, int] = (255, 255, 255)
    position: Tuple[int, int] = (10, 10)
    start_time: float = 0.0
    end_time: float = 0.0
    background: Optional[Tuple[int, int, int]] = None
    background_opacity: float = 0.5


@dataclass
class EditingResult:
    """
    Video editing result.
    
    Attributes:
        success: Whether operation succeeded
        output_file: Path to output file
        operation: Operation performed
        duration: Processing time
        error_message: Error message if failed
        timestamp: Completion timestamp
    """
    success: bool
    output_file: Optional[Path] = None
    operation: str = ""
    duration: float = 0.0
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "output_file": str(self.output_file) if self.output_file else None,
            "operation": self.operation,
            "duration": self.duration,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class VideoEditorConfig:
    """
    Configuration for video editing.
    
    Attributes:
        output_dir: Output directory
        output_format: Output format
        video_codec: Video codec
        audio_codec: Audio codec
        crf: Constant Rate Factor
        preset: Encoding preset
        hwaccel: Hardware acceleration
        threads: Number of threads
        overwrite: Overwrite existing files
        keep_original: Keep original file
    """
    output_dir: Path = Path("./downloads/edited")
    output_format: str = "mp4"
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    crf: int = 23
    preset: str = "medium"
    hwaccel: bool = False
    threads: int = 4
    overwrite: bool = True
    keep_original: bool = True


class VideoEditor:
    """
    OMNIPOTENT SOVEREIGN NEXUS Video Editor.
    
    Comprehensive video editing capabilities using ffmpeg.
    """
    
    def __init__(
        self,
        config: Optional[VideoEditorConfig] = None,
        progress_callback: Optional[Callable[[float], Awaitable[None]]] = None,
    ) -> None:
        """
        Initialize the video editor.
        
        Args:
            config: Editor configuration
            progress_callback: Progress callback
        """
        self.config = config or VideoEditorConfig()
        self._progress_callback = progress_callback
        
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"VideoEditor initialized v3.0.1 ULTIMATE NEXUS")
    
    def _get_ffmpeg_path(self) -> Optional[str]:
        """Find ffmpeg executable."""
        return shutil.which("ffmpeg")
    
    def _get_ffprobe_path(self) -> Optional[str]:
        """Find ffprobe executable."""
        return shutil.which("ffprobe")
    
    async def trim(
        self,
        input_path: Path,
        start_time: float,
        end_time: float,
        output_path: Optional[Path] = None,
    ) -> EditingResult:
        """
        Trim video to specified time range.
        
        Args:
            input_path: Input video path
            start_time: Start time in seconds
            end_time: End time in seconds
            output_path: Output path
            
        Returns:
            EditingResult
        """
        ffmpeg = self._get_ffmpeg_path()
        if not ffmpeg:
            return EditingResult(
                success=False,
                operation="trim",
                error_message="ffmpeg not found",
            )
        
        start = datetime.now()
        
        output = output_path or self.config.output_dir / f"{input_path.stem}_trimmed.mp4"
        
        try:
            cmd = [
                ffmpeg,
                "-y" if self.config.overwrite else "-n",
                "-ss", str(start_time),
                "-i", str(input_path),
                "-t", str(end_time - start_time),
                "-c:v", self.config.video_codec,
                "-c:a", self.config.audio_codec,
                "-crf", str(self.config.crf),
                "-preset", self.config.preset,
                "-threads", str(self.config.threads),
                str(output),
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            await process.communicate()
            
            if process.returncode == 0:
                duration = (datetime.now() - start).total_seconds()
                return EditingResult(
                    success=True,
                    output_file=output,
                    operation="trim",
                    duration=duration,
                )
            
            return EditingResult(
                success=False,
                operation="trim",
                error_message="FFmpeg error",
            )
            
        except Exception as e:
            return EditingResult(
                success=False,
                operation="trim",
                error_message=str(e),
            )
    
    async def concatenate(
        self,
        input_files: List[Path],
        output_path: Optional[Path] = None,
    ) -> EditingResult:
        """
        Concatenate multiple videos.
        
        Args:
            input_files: List of video files
            output_path: Output path
            
        Returns:
            EditingResult
        """
        ffmpeg = self._get_ffmpeg_path()
        if not ffmpeg:
            return EditingResult(
                success=False,
                operation="concatenate",
                error_message="ffmpeg not found",
            )
        
        start = datetime.now()
        
        try:
            # Create file list
            list_file = self.config.output_dir / "concat_list.txt"
            
            async with aiofiles.open(list_file, 'w') as f:
                for fp in input_files:
                    await f.write(f"file '{fp.absolute()}'\n")
            
            output = output_path or self.config.output_dir / "concatenated.mp4"
            
            cmd = [
                ffmpeg,
                "-y" if self.config.overwrite else "-n",
                "-f", "concat",
                "-safe", "0",
                "-i", str(list_file),
                "-c:v", self.config.video_codec,
                "-c:a", self.config.audio_codec,
                "-crf", str(self.config.crf),
                "-preset", self.config.preset,
                str(output),
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            await process.communicate()
            
            # Clean up
            list_file.unlink()
            
            if process.returncode == 0:
                duration = (datetime.now() - start).total_seconds()
                return EditingResult(
                    success=True,
                    output_file=output,
                    operation="concatenate",
                    duration=duration,
                )
            
            return EditingResult(
                success=False,
                operation="concatenate",
                error_message="Concatenation failed",
            )
            
        except Exception as e:
            return EditingResult(
                success=False,
                operation="concatenate",
                error_message=str(e),
            )
    
    async def add_watermark(
        self,
        input_path: Path,
        watermark: WatermarkConfig,
        output_path: Optional[Path] = None,
    ) -> EditingResult:
        """
        Add watermark to video.
        
        Args:
            input_path: Input video path
            watermark: Watermark configuration
            output_path: Output path
            
        Returns:
            EditingResult
        """
        ffmpeg = self._get_ffmpeg_path()
        if not ffmpeg:
            return EditingResult(
                success=False,
                operation="watermark",
                error_message="ffmpeg not found",
            )
        
        start = datetime.now()
        output = output_path or self.config.output_dir / f"{input_path.stem}_watermarked.mp4"
        
        try:
            # Build filter for watermark
            x, y = watermark.position
            opacity = watermark.opacity
            
            filter_complex = (
                f"[1:v]format=rgba,colorchannelmixer=aa={opacity}[wm];"
                f"[0:v][wm]overlay={x}:{y}"
            )
            
            cmd = [
                ffmpeg,
                "-y" if self.config.overwrite else "-n",
                "-i", str(input_path),
                "-i", str(watermark.image_path),
                "-filter_complex", filter_complex,
                "-c:v", self.config.video_codec,
                "-c:a", "copy",
                "-crf", str(self.config.crf),
                str(output),
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            await process.communicate()
            
            if process.returncode == 0:
                duration = (datetime.now() - start).total_seconds()
                return EditingResult(
                    success=True,
                    output_file=output,
                    operation="watermark",
                    duration=duration,
                )
            
            return EditingResult(
                success=False,
                operation="watermark",
                error_message="Watermark failed",
            )
            
        except Exception as e:
            return EditingResult(
                success=False,
                operation="watermark",
                error_message=str(e),
            )
    
    async def add_text(
        self,
        input_path: Path,
        text_overlay: TextOverlay,
        output_path: Optional[Path] = None,
    ) -> EditingResult:
        """
        Add text overlay to video.
        
        Args:
            input_path: Input video path
            text_overlay: Text overlay configuration
            output_path: Output path
            
        Returns:
            EditingResult
        """
        ffmpeg = self._get_ffmpeg_path()
        if not ffmpeg:
            return EditingResult(
                success=False,
                operation="text",
                error_message="ffmpeg not found",
            )
        
        start = datetime.now()
        output = output_path or self.config.output_dir / f"{input_path.stem}_text.mp4"
        
        try:
            x, y = text_overlay.position
            r, g, b = text_overlay.font_color
            fontcolor = f"0x{r:02x}{g:02x}{b:02x}"
            
            filter_str = (
                f"drawtext=text='{text_overlay.text}':"
                f"fontsize={text_overlay.font_size}:"
                f"fontcolor={fontcolor}:"
                f"x={x}:y={y}"
            )
            
            if text_overlay.start_time > 0 or text_overlay.end_time > 0:
                filter_str += f":enable='between(t,{text_overlay.start_time},{text_overlay.end_time or 999999})'"
            
            cmd = [
                ffmpeg,
                "-y" if self.config.overwrite else "-n",
                "-i", str(input_path),
                "-vf", filter_str,
                "-c:v", self.config.video_codec,
                "-c:a", "copy",
                "-crf", str(self.config.crf),
                str(output),
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            await process.communicate()
            
            if process.returncode == 0:
                duration = (datetime.now() - start).total_seconds()
                return EditingResult(
                    success=True,
                    output_file=output,
                    operation="text",
                    duration=duration,
                )
            
            return EditingResult(
                success=False,
                operation="text",
                error_message="Text overlay failed",
            )
            
        except Exception as e:
            return EditingResult(
                success=False,
                operation="text",
                error_message=str(e),
            )
    
    async def apply_filter(
        self,
        input_path: Path,
        filter_type: FilterType,
        intensity: float = 1.0,
        output_path: Optional[Path] = None,
    ) -> EditingResult:
        """
        Apply filter to video.
        
        Args:
            input_path: Input video path
            filter_type: Filter type
            intensity: Filter intensity (0-1)
            output_path: Output path
            
        Returns:
            EditingResult
        """
        ffmpeg = self._get_ffmpeg_path()
        if not ffmpeg:
            return EditingResult(
                success=False,
                operation="filter",
                error_message="ffmpeg not found",
            )
        
        start = datetime.now()
        output = output_path or self.config.output_dir / f"{input_path.stem}_{filter_type.value}.mp4"
        
        # Build filter string
        filter_map = {
            FilterType.GRAYSCALE: "colorchannelmixer=.3:.4:.3:0:.3:.4:.3:0:.3:.4:.3",
            FilterType.SEPIA: "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131",
            FilterType.NEGATE: "negate",
            FilterType.BLUR: f"gblur=sigma={intensity * 10}",
            FilterType.SHARPEN: f"unsharp=5:5:{intensity}:5:5:{intensity}",
        }
        
        filter_str = filter_map.get(filter_type, "")
        
        if not filter_str:
            return EditingResult(
                success=False,
                operation="filter",
                error_message=f"Unsupported filter: {filter_type}",
            )
        
        try:
            cmd = [
                ffmpeg,
                "-y" if self.config.overwrite else "-n",
                "-i", str(input_path),
                "-vf", filter_str,
                "-c:v", self.config.video_codec,
                "-c:a", "copy",
                "-crf", str(self.config.crf),
                str(output),
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            await process.communicate()
            
            if process.returncode == 0:
                duration = (datetime.now() - start).total_seconds()
                return EditingResult(
                    success=True,
                    output_file=output,
                    operation=f"filter_{filter_type.value}",
                    duration=duration,
                )
            
            return EditingResult(
                success=False,
                operation="filter",
                error_message="Filter failed",
            )
            
        except Exception as e:
            return EditingResult(
                success=False,
                operation="filter",
                error_message=str(e),
            )
    
    async def change_speed(
        self,
        input_path: Path,
        speed: float,
        output_path: Optional[Path] = None,
    ) -> EditingResult:
        """
        Change video speed.
        
        Args:
            input_path: Input video path
            speed: Speed factor (0.5 = half speed, 2.0 = double speed)
            output_path: Output path
            
        Returns:
            EditingResult
        """
        ffmpeg = self._get_ffmpeg_path()
        if not ffmpeg:
            return EditingResult(
                success=False,
                operation="speed",
                error_message="ffmpeg not found",
            )
        
        start = datetime.now()
        output = output_path or self.config.output_dir / f"{input_path.stem}_speed{speed}.mp4"
        
        try:
            # Video filter for speed
            video_filter = f"setpts={1/speed}*PTS"
            
            # Audio filter for speed (atempo has limits, so chain if needed)
            audio_filter = f"atempo={speed}" if 0.5 <= speed <= 2.0 else f"atempo=2.0,atempo={speed/2}"
            
            cmd = [
                ffmpeg,
                "-y" if self.config.overwrite else "-n",
                "-i", str(input_path),
                "-filter:v", video_filter,
                "-filter:a", audio_filter,
                "-c:v", self.config.video_codec,
                "-c:a", self.config.audio_codec,
                "-crf", str(self.config.crf),
                str(output),
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            await process.communicate()
            
            if process.returncode == 0:
                duration = (datetime.now() - start).total_seconds()
                return EditingResult(
                    success=True,
                    output_file=output,
                    operation="speed",
                    duration=duration,
                )
            
            return EditingResult(
                success=False,
                operation="speed",
                error_message="Speed change failed",
            )
            
        except Exception as e:
            return EditingResult(
                success=False,
                operation="speed",
                error_message=str(e),
            )
    
    async def resize(
        self,
        input_path: Path,
        width: int,
        height: int,
        maintain_aspect: bool = True,
        output_path: Optional[Path] = None,
    ) -> EditingResult:
        """
        Resize video.
        
        Args:
            input_path: Input video path
            width: Target width
            height: Target height
            maintain_aspect: Maintain aspect ratio
            output_path: Output path
            
        Returns:
            EditingResult
        """
        ffmpeg = self._get_ffmpeg_path()
        if not ffmpeg:
            return EditingResult(
                success=False,
                operation="resize",
                error_message="ffmpeg not found",
            )
        
        start = datetime.now()
        output = output_path or self.config.output_dir / f"{input_path.stem}_{width}x{height}.mp4"
        
        try:
            if maintain_aspect:
                filter_str = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
            else:
                filter_str = f"scale={width}:{height}"
            
            cmd = [
                ffmpeg,
                "-y" if self.config.overwrite else "-n",
                "-i", str(input_path),
                "-vf", filter_str,
                "-c:v", self.config.video_codec,
                "-c:a", "copy",
                "-crf", str(self.config.crf),
                str(output),
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            await process.communicate()
            
            if process.returncode == 0:
                duration = (datetime.now() - start).total_seconds()
                return EditingResult(
                    success=True,
                    output_file=output,
                    operation="resize",
                    duration=duration,
                )
            
            return EditingResult(
                success=False,
                operation="resize",
                error_message="Resize failed",
            )
            
        except Exception as e:
            return EditingResult(
                success=False,
                operation="resize",
                error_message=str(e),
            )
    
    async def rotate(
        self,
        input_path: Path,
        degrees: int,
        output_path: Optional[Path] = None,
    ) -> EditingResult:
        """
        Rotate video.
        
        Args:
            input_path: Input video path
            degrees: Rotation degrees (90, 180, 270)
            output_path: Output path
            
        Returns:
            EditingResult
        """
        ffmpeg = self._get_ffmpeg_path()
        if not ffmpeg:
            return EditingResult(
                success=False,
                operation="rotate",
                error_message="ffmpeg not found",
            )
        
        start = datetime.now()
        output = output_path or self.config.output_dir / f"{input_path.stem}_rotated{degrees}.mp4"
        
        try:
            # Map degrees to transpose value
            transpose_map = {90: 1, 180: "1,transpose=1", 270: 2}
            transpose = transpose_map.get(degrees, 0)
            
            filter_str = f"transpose={transpose}" if degrees != 180 else "transpose=1,transpose=1"
            
            cmd = [
                ffmpeg,
                "-y" if self.config.overwrite else "-n",
                "-i", str(input_path),
                "-vf", filter_str,
                "-c:v", self.config.video_codec,
                "-c:a", "copy",
                "-crf", str(self.config.crf),
                str(output),
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            await process.communicate()
            
            if process.returncode == 0:
                duration = (datetime.now() - start).total_seconds()
                return EditingResult(
                    success=True,
                    output_file=output,
                    operation="rotate",
                    duration=duration,
                )
            
            return EditingResult(
                success=False,
                operation="rotate",
                error_message="Rotation failed",
            )
            
        except Exception as e:
            return EditingResult(
                success=False,
                operation="rotate",
                error_message=str(e),
            )


# Convenience functions
async def trim_video(
    input_path: str,
    start_time: float,
    end_time: float,
    output_dir: str = "./downloads/edited",
) -> EditingResult:
    """Quick trim function."""
    editor = VideoEditor(VideoEditorConfig(output_dir=Path(output_dir)))
    return await editor.trim(Path(input_path), start_time, end_time)


async def concatenate_videos(
    input_files: List[str],
    output_dir: str = "./downloads/edited",
) -> EditingResult:
    """Quick concatenate function."""
    editor = VideoEditor(VideoEditorConfig(output_dir=Path(output_dir)))
    return await editor.concatenate([Path(f) for f in input_files])


__all__ = [
    "VideoEditor",
    "VideoEditorConfig",
    "EditingResult",
    "TransitionType",
    "FilterType",
    "TrimPoint",
    "WatermarkConfig",
    "TextOverlay",
    "trim_video",
    "concatenate_videos",
]

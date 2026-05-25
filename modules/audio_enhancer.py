"""
OMNIPOTENT SOVEREIGN NEXUS - Audio Enhancer Module
Version: v3.0.1 ULTIMATE NEXUS

AI-powered audio enhancement with support for:
- Noise reduction
- Audio normalization
- Bass boost
- Voice enhancement
- Background music separation
- Speech clarity improvement
- Audio repair
- Volume leveling
- Stereo widening
- Dynamic range compression

Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
"""

import asyncio
import aiofiles
import logging
import json
import shutil
import math
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


class EnhancementType(Enum):
    """Audio enhancement types."""
    
    NOISE_REDUCTION = "noise_reduction"
    NORMALIZATION = "normalization"
    BASS_BOOST = "bass_boost"
    VOICE_ENHANCE = "voice_enhance"
    STEREO_WIDE = "stereo_wide"
    COMPRESSION = "compression"
    VOLUME_LEVEL = "volume_level"
    DEESSER = "deesser"
    REVERB = "reverb"
    PITCH_CORRECT = "pitch_correct"


class NoiseProfile(Enum):
    """Noise profile types for noise reduction."""
    
    AUTO = "auto"
    TAPE_HISS = "tape_hiss"
    VINYL = "vinyl"
    ELECTRICAL = "electrical"
    WIND = "wind"
    BREATH = "breath"
    BACKGROUND = "background"
    CUSTOM = "custom"


@dataclass
class AudioAnalysis:
    """
    Audio analysis result.
    
    Attributes:
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        channels: Number of channels
        bit_depth: Bit depth
        bitrate: Bitrate in kbps
        loudness: Integrated loudness (LUFS)
        peak: Peak level (dB)
        noise_level: Estimated noise level
        dc_offset: DC offset
        clipping: Whether audio is clipping
    """
    duration: float = 0.0
    sample_rate: int = 44100
    channels: int = 2
    bit_depth: int = 16
    bitrate: int = 128
    loudness: float = -14.0
    peak: float = -1.0
    noise_level: float = -60.0
    dc_offset: float = 0.0
    clipping: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "duration": self.duration,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "bit_depth": self.bit_depth,
            "bitrate": self.bitrate,
            "loudness": self.loudness,
            "peak": self.peak,
            "noise_level": self.noise_level,
            "dc_offset": self.dc_offset,
            "clipping": self.clipping,
        }


@dataclass
class EnhancementResult:
    """
    Audio enhancement result.
    
    Attributes:
        success: Whether enhancement succeeded
        input_file: Input file path
        output_file: Output file path
        enhancement_type: Type of enhancement
        analysis_before: Analysis before enhancement
        analysis_after: Analysis after enhancement
        processing_time: Processing duration
        error_message: Error message if failed
    """
    success: bool
    input_file: Optional[Path] = None
    output_file: Optional[Path] = None
    enhancement_type: EnhancementType = EnhancementType.NORMALIZATION
    analysis_before: Optional[AudioAnalysis] = None
    analysis_after: Optional[AudioAnalysis] = None
    processing_time: float = 0.0
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "input_file": str(self.input_file) if self.input_file else None,
            "output_file": str(self.output_file) if self.output_file else None,
            "enhancement_type": self.enhancement_type.value,
            "analysis_before": self.analysis_before.to_dict() if self.analysis_before else None,
            "analysis_after": self.analysis_after.to_dict() if self.analysis_after else None,
            "processing_time": self.processing_time,
            "error_message": self.error_message,
        }


@dataclass
class EnhancerConfig:
    """
    Configuration for audio enhancement.
    
    Attributes:
        output_dir: Output directory
        output_format: Output format
        output_bitrate: Output bitrate (kbps)
        output_sample_rate: Output sample rate
        noise_reduction_strength: Noise reduction strength (0-1)
        normalization_target: Target loudness (LUFS)
        bass_boost_db: Bass boost in dB
        voice_enhance_level: Voice enhancement level
        stereo_width: Stereo width (1 = normal)
        compression_ratio: Compression ratio
        keep_original: Keep original file
        use_gpu: Use GPU acceleration
    """
    output_dir: Path = Path("./downloads/enhanced")
    output_format: str = "mp3"
    output_bitrate: int = 320
    output_sample_rate: int = 44100
    noise_reduction_strength: float = 0.5
    normalization_target: float = -14.0
    bass_boost_db: float = 6.0
    voice_enhance_level: float = 0.5
    stereo_width: float = 1.5
    compression_ratio: float = 4.0
    keep_original: bool = True
    use_gpu: bool = False


class AudioEnhancer:
    """
    OMNIPOTENT SOVEREIGN NEXUS Audio Enhancer.
    
    AI-powered audio enhancement using ffmpeg and SoX.
    """
    
    def __init__(
        self,
        config: Optional[EnhancerConfig] = None,
        progress_callback: Optional[Callable[[float], Awaitable[None]]] = None,
    ) -> None:
        """
        Initialize the audio enhancer.
        
        Args:
            config: Enhancer configuration
            progress_callback: Progress callback
        """
        self.config = config or EnhancerConfig()
        self._progress_callback = progress_callback
        
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"AudioEnhancer initialized v3.0.1 ULTIMATE NEXUS")
    
    def _get_ffmpeg_path(self) -> Optional[str]:
        """Find ffmpeg executable."""
        return shutil.which("ffmpeg")
    
    def _get_ffprobe_path(self) -> Optional[str]:
        """Find ffprobe executable."""
        return shutil.which("ffprobe")
    
    def _get_sox_path(self) -> Optional[str]:
        """Find SoX executable."""
        return shutil.which("sox")
    
    async def analyze(self, input_path: Path) -> Optional[AudioAnalysis]:
        """
        Analyze audio file.
        
        Args:
            input_path: Path to audio file
            
        Returns:
            AudioAnalysis or None
        """
        ffprobe = self._get_ffprobe_path()
        if not ffprobe:
            return None
        
        try:
            cmd = [
                ffprobe,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                str(input_path),
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, _ = await process.communicate()
            
            if process.returncode == 0:
                data = json.loads(stdout.decode())
                format_info = data.get("format", {})
                streams = data.get("streams", [])
                
                audio_stream = next(
                    (s for s in streams if s.get("codec_type") == "audio"),
                    {}
                )
                
                return AudioAnalysis(
                    duration=float(format_info.get("duration", 0)),
                    sample_rate=int(audio_stream.get("sample_rate", 44100)),
                    channels=int(audio_stream.get("channels", 2)),
                    bit_depth=int(audio_stream.get("bits_per_sample", 16)),
                    bitrate=int(format_info.get("bit_rate", 0)) // 1000,
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return None
    
    async def enhance(
        self,
        input_path: Path,
        enhancement_type: EnhancementType,
        strength: float = 0.5,
        output_path: Optional[Path] = None,
    ) -> EnhancementResult:
        """
        Apply audio enhancement.
        
        Args:
            input_path: Input audio path
            enhancement_type: Type of enhancement
            strength: Enhancement strength (0-1)
            output_path: Output path
            
        Returns:
            EnhancementResult
        """
        ffmpeg = self._get_ffmpeg_path()
        if not ffmpeg:
            return EnhancementResult(
                success=False,
                input_file=input_path,
                enhancement_type=enhancement_type,
                error_message="ffmpeg not found",
            )
        
        start = datetime.now()
        
        # Analyze before
        analysis_before = await self.analyze(input_path)
        
        output = output_path or self.config.output_dir / f"{input_path.stem}_{enhancement_type.value}.{self.config.output_format}"
        
        try:
            # Build filter based on enhancement type
            filter_str = self._build_filter(enhancement_type, strength)
            
            cmd = [
                ffmpeg,
                "-y",
                "-i", str(input_path),
                "-af", filter_str,
                "-c:a", "libmp3lame" if self.config.output_format == "mp3" else "copy",
            ]
            
            if self.config.output_format == "mp3":
                cmd.extend(["-b:a", f"{self.config.output_bitrate}k"])
            
            cmd.extend(["-ar", str(self.config.output_sample_rate)])
            cmd.append(str(output))
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            await process.communicate()
            
            if process.returncode == 0:
                # Analyze after
                analysis_after = await self.analyze(output)
                
                processing_time = (datetime.now() - start).total_seconds()
                
                return EnhancementResult(
                    success=True,
                    input_file=input_path,
                    output_file=output,
                    enhancement_type=enhancement_type,
                    analysis_before=analysis_before,
                    analysis_after=analysis_after,
                    processing_time=processing_time,
                )
            
            return EnhancementResult(
                success=False,
                input_file=input_path,
                enhancement_type=enhancement_type,
                error_message="Enhancement failed",
            )
            
        except Exception as e:
            return EnhancementResult(
                success=False,
                input_file=input_path,
                enhancement_type=enhancement_type,
                error_message=str(e),
            )
    
    def _build_filter(self, enhancement_type: EnhancementType, strength: float) -> str:
        """Build ffmpeg filter for enhancement."""
        filters = {
            EnhancementType.NOISE_REDUCTION: f"afftdn=nf={strength * 25}",
            EnhancementType.NORMALIZATION: f"loudnorm=I={self.config.normalization_target}:TP=-1:LRA=11",
            EnhancementType.BASS_BOOST: f"bass=g={self.config.bass_boost_db * strength}",
            EnhancementType.VOICE_ENHANCE: f"highpass=f=100,lowpass=f=8000,acompressor=threshold=-20dB:ratio={self.config.compression_ratio}",
            EnhancementType.STEREO_WIDE: f"stereowiden=spread={self.config.stereo_width * strength}",
            EnhancementType.COMPRESSION: f"acompressor=threshold=-20dB:ratio={self.config.compression_ratio}:attack=5:release=50",
            EnhancementType.VOLUME_LEVEL: f"loudnorm=I={self.config.normalization_target}",
            EnhancementType.DEESSER: f"adeclick=window=50:overlap=75,afftdn=nf=10",
            EnhancementType.REVERB: f"aecho=0.8:0.9:1000:0.3",
            EnhancementType.PITCH_CORRECT: "rubberband=pitch=1.0",
        }
        
        return filters.get(enhancement_type, "")
    
    async def reduce_noise(
        self,
        input_path: Path,
        strength: float = 0.5,
        noise_profile: NoiseProfile = NoiseProfile.AUTO,
        output_path: Optional[Path] = None,
    ) -> EnhancementResult:
        """
        Reduce noise in audio.
        
        Args:
            input_path: Input audio path
            strength: Noise reduction strength
            noise_profile: Noise profile
            output_path: Output path
            
        Returns:
            EnhancementResult
        """
        return await self.enhance(
            input_path,
            EnhancementType.NOISE_REDUCTION,
            strength,
            output_path,
        )
    
    async def normalize(
        self,
        input_path: Path,
        target_loudness: float = -14.0,
        output_path: Optional[Path] = None,
    ) -> EnhancementResult:
        """
        Normalize audio loudness.
        
        Args:
            input_path: Input audio path
            target_loudness: Target loudness in LUFS
            output_path: Output path
            
        Returns:
            EnhancementResult
        """
        # Update config temporarily
        original_target = self.config.normalization_target
        self.config.normalization_target = target_loudness
        
        result = await self.enhance(
            input_path,
            EnhancementType.NORMALIZATION,
            output_path=output_path,
        )
        
        self.config.normalization_target = original_target
        return result
    
    async def boost_bass(
        self,
        input_path: Path,
        gain_db: float = 6.0,
        output_path: Optional[Path] = None,
    ) -> EnhancementResult:
        """
        Boost bass frequencies.
        
        Args:
            input_path: Input audio path
            gain_db: Bass gain in dB
            output_path: Output path
            
        Returns:
            EnhancementResult
        """
        original_bass = self.config.bass_boost_db
        self.config.bass_boost_db = gain_db
        
        result = await self.enhance(
            input_path,
            EnhancementType.BASS_BOOST,
            output_path=output_path,
        )
        
        self.config.bass_boost_db = original_bass
        return result
    
    async def enhance_voice(
        self,
        input_path: Path,
        level: float = 0.5,
        output_path: Optional[Path] = None,
    ) -> EnhancementResult:
        """
        Enhance voice clarity.
        
        Args:
            input_path: Input audio path
            level: Enhancement level
            output_path: Output path
            
        Returns:
            EnhancementResult
        """
        return await self.enhance(
            input_path,
            EnhancementType.VOICE_ENHANCE,
            level,
            output_path,
        )
    
    async def apply_multiple(
        self,
        input_path: Path,
        enhancements: List[Tuple[EnhancementType, float]],
        output_path: Optional[Path] = None,
    ) -> EnhancementResult:
        """
        Apply multiple enhancements.
        
        Args:
            input_path: Input audio path
            enhancements: List of (enhancement_type, strength) tuples
            output_path: Output path
            
        Returns:
            EnhancementResult
        """
        ffmpeg = self._get_ffmpeg_path()
        if not ffmpeg:
            return EnhancementResult(
                success=False,
                input_file=input_path,
                error_message="ffmpeg not found",
            )
        
        start = datetime.now()
        analysis_before = await self.analyze(input_path)
        
        output = output_path or self.config.output_dir / f"{input_path.stem}_enhanced.{self.config.output_format}"
        
        try:
            # Build combined filter
            filters = [self._build_filter(e, s) for e, s in enhancements]
            filter_str = ",".join(f for f in filters if f)
            
            cmd = [
                ffmpeg,
                "-y",
                "-i", str(input_path),
                "-af", filter_str,
                "-c:a", "libmp3lame" if self.config.output_format == "mp3" else "copy",
                "-b:a", f"{self.config.output_bitrate}k",
                str(output),
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            await process.communicate()
            
            if process.returncode == 0:
                analysis_after = await self.analyze(output)
                processing_time = (datetime.now() - start).total_seconds()
                
                return EnhancementResult(
                    success=True,
                    input_file=input_path,
                    output_file=output,
                    enhancement_type=enhancements[0][0] if enhancements else EnhancementType.NORMALIZATION,
                    analysis_before=analysis_before,
                    analysis_after=analysis_after,
                    processing_time=processing_time,
                )
            
            return EnhancementResult(
                success=False,
                input_file=input_path,
                error_message="Multi-enhancement failed",
            )
            
        except Exception as e:
            return EnhancementResult(
                success=False,
                input_file=input_path,
                error_message=str(e),
            )


# Convenience functions
async def reduce_audio_noise(
    input_path: str,
    strength: float = 0.5,
    output_dir: str = "./downloads/enhanced",
) -> EnhancementResult:
    """Quick noise reduction function."""
    enhancer = AudioEnhancer(EnhancerConfig(output_dir=Path(output_dir)))
    return await enhancer.reduce_noise(Path(input_path), strength)


async def normalize_audio(
    input_path: str,
    target_loudness: float = -14.0,
    output_dir: str = "./downloads/enhanced",
) -> EnhancementResult:
    """Quick normalization function."""
    enhancer = AudioEnhancer(EnhancerConfig(output_dir=Path(output_dir)))
    return await enhancer.normalize(Path(input_path), target_loudness)


__all__ = [
    "AudioEnhancer",
    "EnhancerConfig",
    "EnhancementResult",
    "EnhancementType",
    "NoiseProfile",
    "AudioAnalysis",
    "reduce_audio_noise",
    "normalize_audio",
]

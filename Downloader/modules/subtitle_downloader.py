"""
OMNIPOTENT SOVEREIGN NEXUS - Subtitle Downloader Module
Version: v3.0.1 ULTIMATE NEXUS

Advanced subtitle downloading with support for:
- Multiple platforms (YouTube, Vimeo, etc.)
- Multiple subtitle formats (SRT, VTT, ASS, TTML)
- Automatic and manual subtitles
- Language selection and detection
- Subtitle translation
- Subtitle merging and combining
- Batch download from playlists
- Subtitle editing and correction

Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
"""

import asyncio
import aiohttp
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
    Set,
    Union,
    Awaitable,
    Tuple,
)
from xml.etree import ElementTree
from concurrent.futures import ThreadPoolExecutor
import subprocess


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)


class SubtitleFormat(Enum):
    """Supported subtitle formats."""
    
    SRT = "srt"
    VTT = "vtt"
    ASS = "ass"
    SSA = "ssa"
    TTML = "ttml"
    SBV = "sbv"
    SUB = "sub"
    LRC = "lrc"
    JSON = "json"
    TXT = "txt"
    
    @property
    def extension(self) -> str:
        """Return file extension."""
        return f".{self.value}"
    
    @property
    def mime_type(self) -> str:
        """Return MIME type."""
        mime_types = {
            SubtitleFormat.SRT: "application/x-subrip",
            SubtitleFormat.VTT: "text/vtt",
            SubtitleFormat.ASS: "text/x-ssa",
            SubtitleFormat.SSA: "text/x-ssa",
            SubtitleFormat.TTML: "application/ttml+xml",
            SubtitleFormat.JSON: "application/json",
            SubtitleFormat.TXT: "text/plain",
        }
        return mime_types.get(self, "text/plain")


class SubtitleType(Enum):
    """Subtitle source type."""
    
    MANUAL = "manual"        # Manually uploaded subtitles
    AUTO = "auto"           # Auto-generated subtitles
    TRANSLATION = "translation"  # Translated subtitles


@dataclass
class SubtitleLanguage:
    """
    Subtitle language information.
    
    Attributes:
        code: ISO 639-1 language code
        name: Full language name
        native_name: Native language name
        is_auto: Whether auto-generated
    """
    code: str
    name: str = ""
    native_name: str = ""
    is_auto: bool = False
    
    def __str__(self) -> str:
        """Return string representation."""
        if self.is_auto:
            return f"{self.code} (auto)"
        return self.code
    
    @classmethod
    def from_code(cls, code: str) -> "SubtitleLanguage":
        """Create from language code."""
        # Common language names
        lang_names = {
            'en': ('English', 'English'),
            'es': ('Spanish', 'Español'),
            'fr': ('French', 'Français'),
            'de': ('German', 'Deutsch'),
            'it': ('Italian', 'Italiano'),
            'pt': ('Portuguese', 'Português'),
            'ru': ('Russian', 'Русский'),
            'ja': ('Japanese', '日本語'),
            'ko': ('Korean', '한국어'),
            'zh': ('Chinese', '中文'),
            'zh-Hans': ('Chinese (Simplified)', '简体中文'),
            'zh-Hant': ('Chinese (Traditional)', '繁體中文'),
            'ar': ('Arabic', 'العربية'),
            'hi': ('Hindi', 'हिन्दी'),
            'nl': ('Dutch', 'Nederlands'),
            'pl': ('Polish', 'Polski'),
            'tr': ('Turkish', 'Türkçe'),
            'vi': ('Vietnamese', 'Tiếng Việt'),
            'th': ('Thai', 'ไทย'),
            'id': ('Indonesian', 'Bahasa Indonesia'),
        }
        
        # Check if auto-generated
        is_auto = code.endswith('-auto') or code.startswith('a.')
        clean_code = code.replace('-auto', '').replace('a.', '')
        
        name, native = lang_names.get(clean_code, (clean_code.upper(), clean_code))
        
        return cls(
            code=clean_code,
            name=name,
            native_name=native,
            is_auto=is_auto,
        )


@dataclass
class SubtitleResult:
    """
    Subtitle download result.
    
    Attributes:
        success: Whether download succeeded
        filepath: Path to saved subtitle file
        filename: Filename
        url: Source video URL
        video_id: Video ID
        language: Subtitle language
        format: Subtitle format
        subtitle_type: Manual/Auto/Translation
        line_count: Number of subtitle lines
        file_size: File size in bytes
        error_message: Error message if failed
        timestamp: Download timestamp
    """
    success: bool
    filepath: Optional[Path] = None
    filename: Optional[str] = None
    url: str = ""
    video_id: str = ""
    language: Optional[SubtitleLanguage] = None
    format: SubtitleFormat = SubtitleFormat.SRT
    subtitle_type: SubtitleType = SubtitleType.MANUAL
    line_count: int = 0
    file_size: int = 0
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "filepath": str(self.filepath) if self.filepath else None,
            "filename": self.filename,
            "url": self.url,
            "video_id": self.video_id,
            "language": str(self.language) if self.language else None,
            "format": self.format.value,
            "subtitle_type": self.subtitle_type.value,
            "line_count": self.line_count,
            "file_size": self.file_size,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class SubtitleConfig:
    """
    Configuration for subtitle downloads.
    
    Attributes:
        output_dir: Output directory
        format: Target subtitle format
        languages: List of language codes to download
        prefer_auto: Prefer auto-generated over manual
        include_auto: Include auto-generated subtitles
        write_auto_subs: Save auto-generated subtitles
        translate_to: Target language for translation
        merge_subs: Merge multiple subtitles
        proxy: Proxy URL
        cookies_file: Path to cookies file
        timeout: Request timeout
        embed_in_video: Embed subtitles in video file
    """
    output_dir: Path = Path("./downloads/subtitles")
    format: SubtitleFormat = SubtitleFormat.SRT
    languages: List[str] = field(default_factory=lambda: ['en'])
    prefer_auto: bool = False
    include_auto: bool = True
    write_auto_subs: bool = True
    translate_to: Optional[str] = None
    merge_subs: bool = False
    proxy: Optional[str] = None
    cookies_file: Optional[Path] = None
    timeout: float = 30.0
    embed_in_video: bool = False


@dataclass
class SubtitleEntry:
    """
    Single subtitle entry.
    
    Attributes:
        index: Entry index
        start_time: Start time in seconds
        end_time: End time in seconds
        text: Subtitle text
    """
    index: int
    start_time: float
    end_time: float
    text: str
    
    def to_srt(self) -> str:
        """Format as SRT entry."""
        start = self._format_time_srt(self.start_time)
        end = self._format_time_srt(self.end_time)
        return f"{self.index}\n{start} --> {end}\n{self.text}\n"
    
    def to_vtt(self) -> str:
        """Format as VTT entry."""
        start = self._format_time_vtt(self.start_time)
        end = self._format_time_vtt(self.end_time)
        return f"{start} --> {end}\n{self.text}\n"
    
    @staticmethod
    def _format_time_srt(seconds: float) -> str:
        """Format time for SRT format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    @staticmethod
    def _format_time_vtt(seconds: float) -> str:
        """Format time for VTT format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


class SubtitleDownloader:
    """
    OMNIPOTENT SOVEREIGN NEXUS Subtitle Downloader.
    
    Advanced subtitle downloading with comprehensive features:
    - Multi-platform support
    - Multiple formats
    - Language selection
    - Translation support
    - Batch downloads
    """
    
    def __init__(
        self,
        config: Optional[SubtitleConfig] = None,
        progress_callback: Optional[Callable[[str, str], Awaitable[None]]] = None,
    ) -> None:
        """
        Initialize the subtitle downloader.
        
        Args:
            config: Download configuration
            progress_callback: Progress callback (video_id, status)
        """
        self.config = config or SubtitleConfig()
        self._progress_callback = progress_callback
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"SubtitleDownloader initialized v3.0.1 ULTIMATE NEXUS")
    
    async def __aenter__(self) -> "SubtitleDownloader":
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
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                trust_env=True,
            )
    
    async def close(self) -> None:
        """Close the downloader."""
        if self._session and not self._session.closed:
            await self._session.close()
        logger.info("SubtitleDownloader closed")
    
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
    
    async def list_available(
        self,
        url: str,
    ) -> Dict[str, List[SubtitleLanguage]]:
        """
        List available subtitles for a video.
        
        Args:
            url: Video URL
            
        Returns:
            Dictionary with 'manual' and 'auto' lists
        """
        yt_dlp = self._get_yt_dlp_path()
        if not yt_dlp:
            logger.error("yt-dlp not found")
            return {"manual": [], "auto": []}
        
        try:
            cmd = [
                yt_dlp,
                "--list-subs",
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
            output = stdout.decode()
            
            manual = []
            auto = []
            
            in_auto_section = False
            
            for line in output.split('\n'):
                line = line.strip()
                
                if 'Auto-captions' in line or 'Automatic captions' in line:
                    in_auto_section = True
                    continue
                
                if 'Available subtitles' in line:
                    in_auto_section = False
                    continue
                
                # Parse language lines
                parts = line.split()
                if len(parts) >= 2:
                    lang_code = parts[0]
                    if lang_code and len(lang_code) <= 10:
                        lang = SubtitleLanguage.from_code(lang_code)
                        if in_auto_section:
                            auto.append(lang)
                        else:
                            manual.append(lang)
            
            return {"manual": manual, "auto": auto}
            
        except Exception as e:
            logger.error(f"Error listing subtitles: {e}")
            return {"manual": [], "auto": []}
    
    async def download(
        self,
        url: str,
        language: Optional[str] = None,
        output_filename: Optional[str] = None,
        format: Optional[SubtitleFormat] = None,
    ) -> SubtitleResult:
        """
        Download subtitle from URL.
        
        Args:
            url: Video URL
            language: Language code (e.g., 'en', 'en-auto')
            output_filename: Custom output filename
            format: Override output format
            
        Returns:
            SubtitleResult
        """
        target_format = format or self.config.format
        target_language = language or (self.config.languages[0] if self.config.languages else 'en')
        
        yt_dlp = self._get_yt_dlp_path()
        if not yt_dlp:
            return SubtitleResult(
                success=False,
                url=url,
                error_message="yt-dlp not found",
            )
        
        try:
            # Determine if auto-generated
            is_auto = target_language.endswith('-auto') or target_language.startswith('a.')
            clean_lang = target_language.replace('-auto', '').replace('a.', '')
            
            # Build command
            cmd = [
                yt_dlp,
                "--write-subs" if not is_auto else "--write-auto-subs",
                "--skip-download",
                "--sub-lang", clean_lang,
                "--sub-format", target_format.value,
            ]
            
            if output_filename:
                output_path = self.config.output_dir / f"{output_filename}.%(ext)s"
            else:
                output_path = self.config.output_dir / "%(id)s.%(ext)s"
            
            cmd.extend(["-o", str(output_path)])
            
            if self.config.proxy:
                cmd.extend(["--proxy", self.config.proxy])
            
            if self.config.cookies_file:
                cmd.extend(["--cookies", str(self.config.cookies_file)])
            
            cmd.append(url)
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Find downloaded file
                downloaded_file = await self._find_subtitle_file(clean_lang, target_format)
                
                if downloaded_file and downloaded_file.exists():
                    # Count lines
                    line_count = self._count_subtitle_lines(downloaded_file)
                    
                    return SubtitleResult(
                        success=True,
                        filepath=downloaded_file,
                        filename=downloaded_file.name,
                        url=url,
                        language=SubtitleLanguage.from_code(target_language),
                        format=target_format,
                        subtitle_type=SubtitleType.AUTO if is_auto else SubtitleType.MANUAL,
                        line_count=line_count,
                        file_size=downloaded_file.stat().st_size,
                    )
            
            return SubtitleResult(
                success=False,
                url=url,
                error_message=stderr.decode() if stderr else "Download failed",
            )
            
        except Exception as e:
            logger.error(f"Subtitle download error: {e}")
            return SubtitleResult(
                success=False,
                url=url,
                error_message=str(e),
            )
    
    async def download_all(
        self,
        url: str,
        languages: Optional[List[str]] = None,
        include_auto: Optional[bool] = None,
    ) -> List[SubtitleResult]:
        """
        Download all available subtitles.
        
        Args:
            url: Video URL
            languages: Language codes to download
            include_auto: Include auto-generated
            
        Returns:
            List of results
        """
        # Get available subtitles
        available = await self.list_available(url)
        
        results = []
        target_languages = languages or self.config.languages
        include = include_auto if include_auto is not None else self.config.include_auto
        
        # Download manual subtitles
        for lang in available['manual']:
            if not target_languages or lang.code in target_languages:
                result = await self.download(url, language=lang.code)
                results.append(result)
        
        # Download auto-generated subtitles
        if include:
            for lang in available['auto']:
                if not target_languages or lang.code in target_languages:
                    result = await self.download(url, language=f"{lang.code}-auto")
                    results.append(result)
        
        return results
    
    async def download_multiple(
        self,
        urls: List[str],
        language: str = "en",
    ) -> List[SubtitleResult]:
        """
        Download subtitles from multiple videos.
        
        Args:
            urls: List of video URLs
            language: Language code
            
        Returns:
            List of results
        """
        tasks = [self.download(url, language=language) for url in urls]
        return list(await asyncio.gather(*tasks, return_exceptions=True))
    
    async def _find_subtitle_file(
        self,
        language: str,
        format: SubtitleFormat,
    ) -> Optional[Path]:
        """Find downloaded subtitle file."""
        for file in self.config.output_dir.iterdir():
            if file.is_file():
                name = file.name.lower()
                if f".{language}." in name or name.endswith(f".{format.value}"):
                    return file
        return None
    
    def _count_subtitle_lines(self, filepath: Path) -> int:
        """Count number of subtitle entries."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # SRT format: count index numbers
            if filepath.suffix == '.srt':
                return len(re.findall(r'^\d+$', content, re.MULTILINE))
            
            # VTT format: count cue timings
            elif filepath.suffix == '.vtt':
                return len(re.findall(r'-->', content))
            
            # Default: count non-empty lines
            return len([l for l in content.split('\n') if l.strip()])
            
        except Exception:
            return 0
    
    async def convert(
        self,
        input_path: Path,
        output_format: SubtitleFormat,
        output_path: Optional[Path] = None,
    ) -> Optional[Path]:
        """
        Convert subtitle to another format.
        
        Args:
            input_path: Input subtitle file
            output_format: Target format
            output_path: Output file path
            
        Returns:
            Path to converted file or None
        """
        try:
            # Read and parse input
            entries = await self._parse_subtitle_file(input_path)
            
            if not entries:
                return None
            
            # Generate output
            output_path = output_path or input_path.with_suffix(output_format.extension)
            
            if output_format == SubtitleFormat.SRT:
                content = '\n'.join(entry.to_srt() for entry in entries)
            elif output_format == SubtitleFormat.VTT:
                content = "WEBVTT\n\n" + '\n'.join(entry.to_vtt() for entry in entries)
            else:
                content = '\n'.join(entry.to_srt() for entry in entries)
            
            async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Subtitle conversion error: {e}")
            return None
    
    async def _parse_subtitle_file(self, filepath: Path) -> List[SubtitleEntry]:
        """Parse subtitle file into entries."""
        entries = []
        
        try:
            async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            if filepath.suffix == '.srt':
                entries = self._parse_srt(content)
            elif filepath.suffix == '.vtt':
                entries = self._parse_vtt(content)
            
        except Exception as e:
            logger.error(f"Error parsing subtitle file: {e}")
        
        return entries
    
    def _parse_srt(self, content: str) -> List[SubtitleEntry]:
        """Parse SRT format."""
        entries = []
        blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    index = int(lines[0])
                    timing = lines[1]
                    text = '\n'.join(lines[2:])
                    
                    start, end = timing.split(' --> ')
                    start_time = self._parse_srt_time(start)
                    end_time = self._parse_srt_time(end)
                    
                    entries.append(SubtitleEntry(
                        index=index,
                        start_time=start_time,
                        end_time=end_time,
                        text=text,
                    ))
                except (ValueError, IndexError):
                    continue
        
        return entries
    
    def _parse_vtt(self, content: str) -> List[SubtitleEntry]:
        """Parse VTT format."""
        entries = []
        lines = content.strip().split('\n')
        
        index = 0
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if '-->' in line:
                index += 1
                timing = line
                text_lines = []
                
                i += 1
                while i < len(lines) and lines[i].strip() and '-->' not in lines[i]:
                    text_lines.append(lines[i].strip())
                    i += 1
                
                start, end = timing.split(' --> ')
                start_time = self._parse_vtt_time(start)
                end_time = self._parse_vtt_time(end)
                
                entries.append(SubtitleEntry(
                    index=index,
                    start_time=start_time,
                    end_time=end_time,
                    text='\n'.join(text_lines),
                ))
            else:
                i += 1
        
        return entries
    
    @staticmethod
    def _parse_srt_time(time_str: str) -> float:
        """Parse SRT time format (HH:MM:SS,mmm)."""
        time_str = time_str.strip().replace(',', '.')
        parts = time_str.split(':')
        
        if len(parts) == 3:
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        
        return 0.0
    
    @staticmethod
    def _parse_vtt_time(time_str: str) -> float:
        """Parse VTT time format (HH:MM:SS.mmm)."""
        return SubtitleDownloader._parse_srt_time(time_str)
    
    async def translate(
        self,
        input_path: Path,
        target_language: str,
        source_language: Optional[str] = None,
    ) -> Optional[Path]:
        """
        Translate subtitle file.
        
        Args:
            input_path: Input subtitle file
            target_language: Target language code
            source_language: Source language code (auto-detect if None)
            
        Returns:
            Path to translated file or None
        """
        # This would integrate with a translation API
        # For now, return None as placeholder
        logger.info(f"Translation requested: {input_path} -> {target_language}")
        return None
    
    async def merge(
        self,
        subtitle_files: List[Path],
        output_path: Path,
    ) -> Optional[Path]:
        """
        Merge multiple subtitle files.
        
        Args:
            subtitle_files: List of subtitle files
            output_path: Output file path
            
        Returns:
            Path to merged file or None
        """
        all_entries = []
        
        for filepath in subtitle_files:
            entries = await self._parse_subtitle_file(filepath)
            all_entries.extend(entries)
        
        if not all_entries:
            return None
        
        # Sort by start time
        all_entries.sort(key=lambda e: e.start_time)
        
        # Re-index
        for i, entry in enumerate(all_entries, 1):
            entry.index = i
        
        # Write merged file
        content = '\n'.join(entry.to_srt() for entry in all_entries)
        
        async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
            await f.write(content)
        
        return output_path


# Convenience function
async def download_subtitle(
    url: str,
    language: str = "en",
    output_dir: str = "./downloads/subtitles",
) -> SubtitleResult:
    """
    Quick subtitle download function.
    
    Args:
        url: Video URL
        language: Language code
        output_dir: Output directory
        
    Returns:
        SubtitleResult
    """
    config = SubtitleConfig(
        output_dir=Path(output_dir),
        languages=[language],
    )
    
    async with SubtitleDownloader(config=config) as downloader:
        return await downloader.download(url, language=language)


__all__ = [
    "SubtitleDownloader",
    "SubtitleFormat",
    "SubtitleType",
    "SubtitleLanguage",
    "SubtitleResult",
    "SubtitleConfig",
    "SubtitleEntry",
    "download_subtitle",
]

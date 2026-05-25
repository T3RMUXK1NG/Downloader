"""
OMNIPOTENT SOVEREIGN NEXUS - Metadata Extractor Module
Version: v3.0.1 ULTIMATE NEXUS

Advanced metadata extraction with support for:
- Multiple platforms (YouTube, Vimeo, SoundCloud, etc.)
- Comprehensive video/audio metadata
- ID3 tag extraction and embedding
- EXIF data handling
- JSON/XML export
- Batch extraction
- Custom metadata fields
- Chapters and segments extraction

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
    Set,
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


class MetadataFormat(Enum):
    """Output format for metadata."""
    
    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    CSV = "csv"
    TXT = "txt"
    NFO = "nfo"  # Kodi/XBMC format


@dataclass
class Chapter:
    """
    Video chapter/segment information.
    
    Attributes:
        index: Chapter index
        title: Chapter title
        start_time: Start time in seconds
        end_time: End time in seconds
    """
    index: int
    title: str
    start_time: float
    end_time: float
    
    @property
    def duration(self) -> float:
        """Return chapter duration."""
        return self.end_time - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "index": self.index,
            "title": self.title,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
        }


@dataclass
class Comment:
    """
    Video comment information.
    
    Attributes:
        id: Comment ID
        author: Author name
        author_id: Author ID
        text: Comment text
        likes: Number of likes
        timestamp: Comment timestamp
        replies: Number of replies
        is_reply: Whether this is a reply
        parent_id: Parent comment ID if reply
    """
    id: str
    author: str
    author_id: str = ""
    text: str = ""
    likes: int = 0
    timestamp: Optional[str] = None
    replies: int = 0
    is_reply: bool = False
    parent_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "author": self.author,
            "author_id": self.author_id,
            "text": self.text,
            "likes": self.likes,
            "timestamp": self.timestamp,
            "replies": self.replies,
            "is_reply": self.is_reply,
            "parent_id": self.parent_id,
        }


@dataclass
class VideoMetadata:
    """
    Comprehensive video metadata.
    
    Attributes:
        id: Video ID
        title: Video title
        description: Full description
        duration: Duration in seconds
        view_count: View count
        like_count: Like count
        dislike_count: Dislike count
        comment_count: Comment count
        uploader: Uploader name
        uploader_id: Uploader ID
        uploader_url: Uploader profile URL
        channel: Channel name
        channel_id: Channel ID
        channel_url: Channel URL
        upload_date: Upload date (YYYYMMDD)
        release_date: Release date if different
        timestamp: Unix timestamp
        thumbnail: Thumbnail URL
        thumbnails: List of available thumbnails
        tags: Video tags
        categories: Video categories
        license: Video license
        availability: Availability status
        is_live: Whether video is live
        was_live: Whether video was a livestream
        live_status: Current live status
        chapters: Video chapters
        automatic_captions: Available auto captions
        subtitles: Available subtitles
        width: Video width
        height: Video height
        fps: Frames per second
        aspect_ratio: Aspect ratio
        vcodec: Video codec
        acodec: Audio codec
        bitrate: Total bitrate
        abr: Average bitrate
        vbr: Video bitrate
        filesize: Expected file size
        player_url: Player URL
        age_limit: Age restriction
        webpage_url: Source webpage URL
        original_url: Original URL
        extractor: Extractor name
        extractor_key: Extractor key
        url: Direct video URL
        format: Format ID
        format_id: Format identifier
        ext: File extension
        protocol: Protocol used
        http_headers: HTTP headers
        formats: Available formats list
    """
    id: str = ""
    title: str = ""
    description: Optional[str] = None
    duration: int = 0
    view_count: int = 0
    like_count: int = 0
    dislike_count: int = 0
    comment_count: int = 0
    uploader: Optional[str] = None
    uploader_id: Optional[str] = None
    uploader_url: Optional[str] = None
    channel: Optional[str] = None
    channel_id: Optional[str] = None
    channel_url: Optional[str] = None
    upload_date: Optional[str] = None
    release_date: Optional[str] = None
    timestamp: Optional[int] = None
    thumbnail: Optional[str] = None
    thumbnails: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    license: Optional[str] = None
    availability: str = "public"
    is_live: bool = False
    was_live: bool = False
    live_status: Optional[str] = None
    chapters: List[Chapter] = field(default_factory=list)
    automatic_captions: Dict[str, List[Dict]] = field(default_factory=dict)
    subtitles: Dict[str, List[Dict]] = field(default_factory=dict)
    width: int = 0
    height: int = 0
    fps: Optional[float] = None
    aspect_ratio: Optional[float] = None
    vcodec: Optional[str] = None
    acodec: Optional[str] = None
    bitrate: Optional[int] = None
    abr: Optional[int] = None
    vbr: Optional[int] = None
    filesize: Optional[int] = None
    player_url: Optional[str] = None
    age_limit: int = 0
    webpage_url: Optional[str] = None
    original_url: Optional[str] = None
    extractor: Optional[str] = None
    extractor_key: Optional[str] = None
    url: Optional[str] = None
    format: Optional[str] = None
    format_id: Optional[str] = None
    ext: Optional[str] = None
    protocol: Optional[str] = None
    http_headers: Dict[str, str] = field(default_factory=dict)
    formats: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def duration_formatted(self) -> str:
        """Return formatted duration."""
        if self.duration == 0:
            return "0:00"
        
        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"
    
    @property
    def resolution(self) -> str:
        """Return video resolution string."""
        if self.width and self.height:
            return f"{self.width}x{self.height}"
        return "Unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "duration": self.duration,
            "duration_formatted": self.duration_formatted,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "dislike_count": self.dislike_count,
            "comment_count": self.comment_count,
            "uploader": self.uploader,
            "uploader_id": self.uploader_id,
            "uploader_url": self.uploader_url,
            "channel": self.channel,
            "channel_id": self.channel_id,
            "channel_url": self.channel_url,
            "upload_date": self.upload_date,
            "release_date": self.release_date,
            "timestamp": self.timestamp,
            "thumbnail": self.thumbnail,
            "thumbnails": self.thumbnails,
            "tags": self.tags,
            "categories": self.categories,
            "license": self.license,
            "availability": self.availability,
            "is_live": self.is_live,
            "was_live": self.was_live,
            "live_status": self.live_status,
            "chapters": [c.to_dict() for c in self.chapters],
            "width": self.width,
            "height": self.height,
            "resolution": self.resolution,
            "fps": self.fps,
            "aspect_ratio": self.aspect_ratio,
            "vcodec": self.vcodec,
            "acodec": self.acodec,
            "bitrate": self.bitrate,
            "filesize": self.filesize,
            "age_limit": self.age_limit,
            "webpage_url": self.webpage_url,
            "extractor": self.extractor,
        }


@dataclass
class AudioMetadata:
    """
    Audio-specific metadata.
    
    Attributes:
        title: Track title
        artist: Artist name
        album: Album name
        album_artist: Album artist
        track_number: Track number
        track_total: Total tracks
        disc_number: Disc number
        disc_total: Total discs
        year: Release year
        genre: Music genre
        composer: Composer
        performer: Performer
        copyright: Copyright info
        publisher: Publisher
        lyrics: Song lyrics
        comment: Comment
        duration: Duration in seconds
        bitrate: Bitrate in kbps
        sample_rate: Sample rate in Hz
        channels: Number of channels
        bits_per_sample: Bits per sample
        codec: Audio codec
        format: Audio format
        isrc: ISRC code
        mb_track_id: MusicBrainz track ID
        mb_album_id: MusicBrainz album ID
        mb_artist_id: MusicBrainz artist ID
        cover_art: Cover art URL or path
    """
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    album_artist: Optional[str] = None
    track_number: Optional[int] = None
    track_total: Optional[int] = None
    disc_number: Optional[int] = None
    disc_total: Optional[int] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    composer: Optional[str] = None
    performer: Optional[str] = None
    copyright: Optional[str] = None
    publisher: Optional[str] = None
    lyrics: Optional[str] = None
    comment: Optional[str] = None
    duration: int = 0
    bitrate: int = 0
    sample_rate: int = 0
    channels: int = 2
    bits_per_sample: Optional[int] = None
    codec: Optional[str] = None
    format: Optional[str] = None
    isrc: Optional[str] = None
    mb_track_id: Optional[str] = None
    mb_album_id: Optional[str] = None
    mb_artist_id: Optional[str] = None
    cover_art: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "album_artist": self.album_artist,
            "track_number": self.track_number,
            "track_total": self.track_total,
            "disc_number": self.disc_number,
            "disc_total": self.disc_total,
            "year": self.year,
            "genre": self.genre,
            "composer": self.composer,
            "performer": self.performer,
            "copyright": self.copyright,
            "publisher": self.publisher,
            "lyrics": self.lyrics,
            "comment": self.comment,
            "duration": self.duration,
            "bitrate": self.bitrate,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "bits_per_sample": self.bits_per_sample,
            "codec": self.codec,
            "format": self.format,
            "isrc": self.isrc,
            "mb_track_id": self.mb_track_id,
            "mb_album_id": self.mb_album_id,
            "mb_artist_id": self.mb_artist_id,
            "cover_art": self.cover_art,
        }


@dataclass
class MediaMetadata:
    """
    Combined media metadata container.
    
    Attributes:
        video: Video metadata
        audio: Audio metadata
        custom: Custom metadata fields
        raw: Raw metadata from source
    """
    video: Optional[VideoMetadata] = None
    audio: Optional[AudioMetadata] = None
    custom: Dict[str, Any] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "video": self.video.to_dict() if self.video else None,
            "audio": self.audio.to_dict() if self.audio else None,
            "custom": self.custom,
            "raw": self.raw,
        }


@dataclass
class MetadataExtractorConfig:
    """
    Configuration for metadata extraction.
    
    Attributes:
        include_comments: Extract comments
        comment_limit: Maximum comments to extract
        include_chapters: Extract chapters
        include_subtitles: Include subtitle info
        include_formats: Include available formats
        include_thumbnails: Include thumbnail info
        write_json: Save metadata as JSON
        write_nfo: Save NFO file for Kodi
        output_dir: Output directory for saved files
        proxy: Proxy URL
        cookies_file: Path to cookies file
        timeout: Request timeout
        user_agent: Custom user agent
    """
    include_comments: bool = False
    comment_limit: int = 100
    include_chapters: bool = True
    include_subtitles: bool = True
    include_formats: bool = True
    include_thumbnails: bool = True
    write_json: bool = False
    write_nfo: bool = False
    output_dir: Path = Path("./downloads/metadata")
    proxy: Optional[str] = None
    cookies_file: Optional[Path] = None
    timeout: float = 30.0
    user_agent: Optional[str] = None


class MetadataExtractor:
    """
    OMNIPOTENT SOVEREIGN NEXUS Metadata Extractor.
    
    Advanced metadata extraction with comprehensive features:
    - Multi-platform support
    - Video and audio metadata
    - Chapters and segments
    - Comments extraction
    - Multiple export formats
    """
    
    def __init__(
        self,
        config: Optional[MetadataExtractorConfig] = None,
    ) -> None:
        """
        Initialize the metadata extractor.
        
        Args:
            config: Extraction configuration
        """
        self.config = config or MetadataExtractorConfig()
        
        # Ensure output directory exists
        if self.config.write_json or self.config.write_nfo:
            self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"MetadataExtractor initialized v3.0.1 ULTIMATE NEXUS")
    
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
    
    async def extract(
        self,
        url: str,
        include_comments: Optional[bool] = None,
    ) -> Optional[MediaMetadata]:
        """
        Extract metadata from URL.
        
        Args:
            url: Video/audio URL
            include_comments: Override comment extraction
            
        Returns:
            MediaMetadata or None
        """
        yt_dlp = self._get_yt_dlp_path()
        if not yt_dlp:
            logger.error("yt-dlp not found")
            return None
        
        try:
            cmd = [
                yt_dlp,
                "--dump-json",
                "--no-download",
                "--no-playlist",
            ]
            
            # Include comments if requested
            if (include_comments or self.config.include_comments) and self.config.comment_limit > 0:
                cmd.extend([
                    "--get-comments",
                    "--extractor-args", f"youtube:max_comments={self.config.comment_limit}",
                ])
            
            if self.config.proxy:
                cmd.extend(["--proxy", self.config.proxy])
            
            if self.config.cookies_file:
                cmd.extend(["--cookies", str(self.config.cookies_file)])
            
            if self.config.user_agent:
                cmd.extend(["--user-agent", self.config.user_agent])
            
            cmd.append(url)
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                data = json.loads(stdout.decode())
                media_metadata = self._parse_metadata(data)
                
                # Save if configured
                if self.config.write_json:
                    await self._save_json(media_metadata, data.get('id', 'metadata'))
                
                if self.config.write_nfo:
                    await self._save_nfo(media_metadata, data.get('id', 'metadata'))
                
                return media_metadata
            
            logger.error(f"Failed to extract metadata: {stderr.decode()}")
            return None
            
        except Exception as e:
            logger.error(f"Metadata extraction error: {e}")
            return None
    
    def _parse_metadata(self, data: Dict[str, Any]) -> MediaMetadata:
        """Parse yt-dlp JSON output to MediaMetadata."""
        # Parse chapters
        chapters = []
        if self.config.include_chapters and 'chapters' in data:
            for i, ch in enumerate(data['chapters']):
                chapters.append(Chapter(
                    index=i,
                    title=ch.get('title', f'Chapter {i+1}'),
                    start_time=ch.get('start_time', 0),
                    end_time=ch.get('end_time', 0),
                ))
        
        # Parse video metadata
        video = VideoMetadata(
            id=data.get('id', ''),
            title=data.get('title', ''),
            description=data.get('description'),
            duration=data.get('duration', 0),
            view_count=data.get('view_count', 0),
            like_count=data.get('like_count', 0),
            dislike_count=data.get('dislike_count', 0),
            comment_count=data.get('comment_count', 0),
            uploader=data.get('uploader'),
            uploader_id=data.get('uploader_id'),
            uploader_url=data.get('uploader_url'),
            channel=data.get('channel'),
            channel_id=data.get('channel_id'),
            channel_url=data.get('channel_url'),
            upload_date=data.get('upload_date'),
            release_date=data.get('release_date'),
            timestamp=data.get('timestamp'),
            thumbnail=data.get('thumbnail'),
            thumbnails=data.get('thumbnails', []),
            tags=data.get('tags', []),
            categories=data.get('categories', []),
            license=data.get('license'),
            availability=data.get('availability', 'public'),
            is_live=data.get('is_live', False),
            was_live=data.get('was_live', False),
            live_status=data.get('live_status'),
            chapters=chapters,
            automatic_captions=data.get('automatic_captions', {}),
            subtitles=data.get('subtitles', {}),
            width=data.get('width', 0),
            height=data.get('height', 0),
            fps=data.get('fps'),
            aspect_ratio=data.get('aspect_ratio'),
            vcodec=data.get('vcodec'),
            acodec=data.get('acodec'),
            bitrate=data.get('bitrate'),
            abr=data.get('abr'),
            vbr=data.get('vbr'),
            filesize=data.get('filesize'),
            age_limit=data.get('age_limit', 0),
            webpage_url=data.get('webpage_url'),
            original_url=data.get('original_url'),
            extractor=data.get('extractor'),
            extractor_key=data.get('extractor_key'),
            formats=data.get('formats', []) if self.config.include_formats else [],
        )
        
        # Parse audio metadata if applicable
        audio = None
        if data.get('acodec') or data.get('vcodec') == 'none':
            audio = AudioMetadata(
                title=data.get('title'),
                artist=data.get('artist') or data.get('uploader'),
                album=data.get('album'),
                duration=data.get('duration', 0),
                bitrate=data.get('abr', 0),
                sample_rate=data.get('asr', 0),
                channels=data.get('audio_channels', 2),
                codec=data.get('acodec'),
            )
        
        return MediaMetadata(
            video=video,
            audio=audio,
            raw=data,
        )
    
    async def _save_json(
        self,
        metadata: MediaMetadata,
        filename: str,
    ) -> None:
        """Save metadata as JSON file."""
        filepath = self.config.output_dir / f"{filename}.info.json"
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(metadata.to_dict(), indent=2, ensure_ascii=False))
    
    async def _save_nfo(
        self,
        metadata: MediaMetadata,
        filename: str,
    ) -> None:
        """Save metadata as NFO file for Kodi/XBMC."""
        video = metadata.video
        if not video:
            return
        
        nfo_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<musicvideo>
    <title>{video.title}</title>
    <artist>{video.uploader or ''}</artist>
    <album>{video.channel or ''}</album>
    <genre>{', '.join(video.tags[:5]) if video.tags else ''}</genre>
    <year>{video.upload_date[:4] if video.upload_date else ''}</year>
    <track></track>
    <duration>{video.duration}</duration>
    <plot>{video.description or ''}</plot>
    <thumb>{video.thumbnail or ''}</thumb>
</musicvideo>
"""
        
        filepath = self.config.output_dir / f"{filename}.nfo"
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(nfo_content)
    
    async def extract_multiple(
        self,
        urls: List[str],
    ) -> List[Optional[MediaMetadata]]:
        """
        Extract metadata from multiple URLs.
        
        Args:
            urls: List of URLs
            
        Returns:
            List of MediaMetadata or None
        """
        tasks = [self.extract(url) for url in urls]
        return list(await asyncio.gather(*tasks, return_exceptions=True))
    
    async def extract_from_file(
        self,
        filepath: Path,
    ) -> Optional[MediaMetadata]:
        """
        Extract metadata from local media file.
        
        Args:
            filepath: Path to media file
            
        Returns:
            MediaMetadata or None
        """
        ffprobe = shutil.which("ffprobe")
        if not ffprobe:
            logger.error("ffprobe not found")
            return None
        
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
                data = json.loads(stdout.decode())
                return self._parse_ffprobe_data(filepath, data)
            
            return None
            
        except Exception as e:
            logger.error(f"File metadata extraction error: {e}")
            return None
    
    def _parse_ffprobe_data(
        self,
        filepath: Path,
        data: Dict[str, Any],
    ) -> MediaMetadata:
        """Parse ffprobe output to MediaMetadata."""
        format_info = data.get('format', {})
        streams = data.get('streams', [])
        
        video_stream = next((s for s in streams if s.get('codec_type') == 'video'), None)
        audio_stream = next((s for s in streams if s.get('codec_type') == 'audio'), None)
        
        tags = format_info.get('tags', {})
        
        video = VideoMetadata(
            id=filepath.stem,
            title=tags.get('title', filepath.stem),
            duration=int(float(format_info.get('duration', 0))),
            width=video_stream.get('width', 0) if video_stream else 0,
            height=video_stream.get('height', 0) if video_stream else 0,
            fps=eval(video_stream.get('r_frame_rate', '0/1')) if video_stream else 0,
            vcodec=video_stream.get('codec_name') if video_stream else None,
            acodec=audio_stream.get('codec_name') if audio_stream else None,
            bitrate=int(format_info.get('bit_rate', 0)),
            filesize=int(format_info.get('size', 0)),
            ext=filepath.suffix.lstrip('.'),
        )
        
        audio = None
        if audio_stream:
            audio = AudioMetadata(
                title=tags.get('title'),
                artist=tags.get('artist'),
                album=tags.get('album'),
                year=int(tags.get('year', 0)) if tags.get('year') else None,
                genre=tags.get('genre'),
                duration=int(float(format_info.get('duration', 0))),
                bitrate=int(audio_stream.get('bit_rate', 0)) // 1000,
                sample_rate=int(audio_stream.get('sample_rate', 0)),
                channels=int(audio_stream.get('channels', 2)),
                codec=audio_stream.get('codec_name'),
            )
        
        return MediaMetadata(
            video=video,
            audio=audio,
            raw=data,
        )
    
    async def export(
        self,
        metadata: MediaMetadata,
        output_path: Path,
        format: MetadataFormat = MetadataFormat.JSON,
    ) -> bool:
        """
        Export metadata to file.
        
        Args:
            metadata: Metadata to export
            output_path: Output file path
            format: Output format
            
        Returns:
            Success boolean
        """
        try:
            if format == MetadataFormat.JSON:
                async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(metadata.to_dict(), indent=2, ensure_ascii=False))
            
            elif format == MetadataFormat.TXT:
                lines = self._format_as_txt(metadata)
                async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
                    await f.write('\n'.join(lines))
            
            elif format == MetadataFormat.NFO:
                await self._save_nfo(metadata, output_path.stem)
            
            return True
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            return False
    
    def _format_as_txt(self, metadata: MediaMetadata) -> List[str]:
        """Format metadata as plain text."""
        lines = []
        video = metadata.video
        
        if video:
            lines.extend([
                f"Title: {video.title}",
                f"ID: {video.id}",
                f"Duration: {video.duration_formatted}",
                f"Views: {video.view_count:,}",
                f"Likes: {video.like_count:,}",
                f"Uploader: {video.uploader or 'Unknown'}",
                f"Upload Date: {video.upload_date or 'Unknown'}",
                "",
                "Description:",
                video.description or "No description",
            ])
        
        return lines


# Convenience function
async def extract_metadata(
    url: str,
    include_comments: bool = False,
) -> Optional[MediaMetadata]:
    """
    Quick metadata extraction function.
    
    Args:
        url: Video/audio URL
        include_comments: Whether to include comments
        
    Returns:
        MediaMetadata or None
    """
    config = MetadataExtractorConfig(include_comments=include_comments)
    extractor = MetadataExtractor(config=config)
    return await extractor.extract(url)


__all__ = [
    "MetadataExtractor",
    "MetadataFormat",
    "MediaMetadata",
    "VideoMetadata",
    "AudioMetadata",
    "Chapter",
    "Comment",
    "MetadataExtractorConfig",
    "extract_metadata",
]

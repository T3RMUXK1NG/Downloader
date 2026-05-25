"""
OMNIPOTENT SOVEREIGN NEXUS - Metadata Enricher Module
Version: v3.0.1 ULTIMATE NEXUS

Metadata enrichment with support for:
- MusicBrainz integration for audio
- IMDb/TMDB for movies/series
- Game databases for gaming content
- Automatic tag correction
- Cover art fetching
- Lyrics integration
- Rating aggregation
- Genre classification
- Release date verification

Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
"""

import asyncio
import aiohttp
import aiofiles
import logging
import json
import re
import hashlib
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


class EnrichmentSource(Enum):
    """Sources for metadata enrichment."""
    
    MUSICBRAINZ = "musicbrainz"
    LASTFM = "lastfm"
    SPOTIFY = "spotify"
    DISCOGS = "discogs"
    IMDB = "imdb"
    TMDB = "tmdb"
    TVDB = "tvdb"
    IGDB = "igdb"
    OPENAI = "openai"
    AUTO = "auto"


class ContentType(Enum):
    """Content types for enrichment."""
    
    MUSIC = "music"
    VIDEO = "video"
    MOVIE = "movie"
    SERIES = "series"
    PODCAST = "podcast"
    AUDIOBOOK = "audiobook"
    GAME = "game"
    UNKNOWN = "unknown"


@dataclass
class EnrichedMetadata:
    """
    Enriched metadata result.
    
    Attributes:
        title: Content title
        artist: Artist/Creator
        album: Album/Series
        year: Release year
        genre: Genres
        description: Description
        cover_url: Cover art URL
        cover_path: Local cover path
        rating: Rating (0-10)
        tags: Tags
        lyrics: Lyrics (for music)
        credits: Credits dictionary
        external_ids: External database IDs
        sources: Sources used
        confidence: Confidence score (0-1)
    """
    title: str = ""
    artist: Optional[str] = None
    album: Optional[str] = None
    year: Optional[int] = None
    genre: List[str] = field(default_factory=list)
    description: str = ""
    cover_url: Optional[str] = None
    cover_path: Optional[Path] = None
    rating: float = 0.0
    tags: List[str] = field(default_factory=list)
    lyrics: Optional[str] = None
    credits: Dict[str, List[str]] = field(default_factory=dict)
    external_ids: Dict[str, str] = field(default_factory=dict)
    sources: List[str] = field(default_factory=list)
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "year": self.year,
            "genre": self.genre,
            "description": self.description,
            "cover_url": self.cover_url,
            "cover_path": str(self.cover_path) if self.cover_path else None,
            "rating": self.rating,
            "tags": self.tags,
            "lyrics": self.lyrics,
            "credits": self.credit,
            "external_ids": self.external_ids,
            "sources": self.sources,
            "confidence": self.confidence,
        }


@dataclass
class EnrichmentResult:
    """
    Metadata enrichment result.
    
    Attributes:
        success: Whether enrichment succeeded
        content_type: Detected content type
        original_metadata: Original metadata
        enriched_metadata: Enriched metadata
        sources_used: Sources that were queried
        processing_time: Processing duration
        error_message: Error message if failed
    """
    success: bool
    content_type: ContentType = ContentType.UNKNOWN
    original_metadata: Dict[str, Any] = field(default_factory=dict)
    enriched_metadata: Optional[EnrichedMetadata] = None
    sources_used: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "content_type": self.content_type.value,
            "original_metadata": self.original_metadata,
            "enriched_metadata": self.enriched_metadata.to_dict() if self.enriched_metadata else None,
            "sources_used": self.sources_used,
            "processing_time": self.processing_time,
            "error_message": self.error_message,
        }


@dataclass
class EnricherConfig:
    """
    Configuration for metadata enrichment.
    
    Attributes:
        sources: Preferred enrichment sources
        musicbrainz_user: MusicBrainz username
        lastfm_api_key: Last.fm API key
        spotify_client_id: Spotify client ID
        spotify_client_secret: Spotify client secret
        tmdb_api_key: TMDB API key
        openai_api_key: OpenAI API key
        fetch_covers: Fetch cover art
        fetch_lyrics: Fetch lyrics
        cover_dir: Directory for cover art
        auto_apply: Auto-apply to files
        confidence_threshold: Minimum confidence to use data
        timeout: Request timeout
    """
    sources: List[EnrichmentSource] = field(default_factory=lambda: [EnrichmentSource.AUTO])
    musicbrainz_user: Optional[str] = None
    lastfm_api_key: Optional[str] = None
    spotify_client_id: Optional[str] = None
    spotify_client_secret: Optional[str] = None
    tmdb_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    fetch_covers: bool = True
    fetch_lyrics: bool = False
    cover_dir: Path = Path("./downloads/covers")
    auto_apply: bool = False
    confidence_threshold: float = 0.5
    timeout: float = 30.0


class MetadataEnricher:
    """
    OMNIPOTENT SOVEREIGN NEXUS Metadata Enricher.
    
    Automatic metadata enrichment from multiple sources.
    """
    
    # Genre mapping for classification
    GENRE_PATTERNS = {
        'rock': ['rock', 'alternative', 'indie', 'punk', 'metal'],
        'pop': ['pop', 'dance', 'electronic', 'synth'],
        'hiphop': ['hip hop', 'rap', 'trap', 'r&b'],
        'classical': ['classical', 'orchestral', 'symphony'],
        'jazz': ['jazz', 'blues', 'swing'],
        'country': ['country', 'folk', 'americana'],
    }
    
    def __init__(
        self,
        config: Optional[EnricherConfig] = None,
        progress_callback: Optional[Callable[[str, float], Awaitable[None]]] = None,
    ) -> None:
        """
        Initialize the metadata enricher.
        
        Args:
            config: Enricher configuration
            progress_callback: Progress callback
        """
        self.config = config or EnricherConfig()
        self._progress_callback = progress_callback
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Ensure cover directory exists
        self.config.cover_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"MetadataEnricher initialized v3.0.1 ULTIMATE NEXUS")
    
    async def __aenter__(self) -> "MetadataEnricher":
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
                headers={"User-Agent": "RS-Toolkit/3.0.1 (Metadata Enricher)"},
            )
    
    async def close(self) -> None:
        """Close the enricher."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def enrich(
        self,
        title: Optional[str] = None,
        artist: Optional[str] = None,
        album: Optional[str] = None,
        existing_metadata: Optional[Dict[str, Any]] = None,
        content_type: Optional[ContentType] = None,
    ) -> EnrichmentResult:
        """
        Enrich metadata from available information.
        
        Args:
            title: Content title
            artist: Artist/Creator name
            album: Album/Series name
            existing_metadata: Existing metadata to enhance
            content_type: Content type override
            
        Returns:
            EnrichmentResult
        """
        start = datetime.now()
        
        await self._create_session()
        
        original = existing_metadata or {}
        if title:
            original["title"] = title
        if artist:
            original["artist"] = artist
        if album:
            original["album"] = album
        
        # Detect content type if not provided
        detected_type = content_type or self._detect_content_type(original)
        
        sources_used = []
        
        try:
            enriched = EnrichedMetadata()
            
            if detected_type == ContentType.MUSIC:
                result = await self._enrich_music(original)
            elif detected_type == ContentType.MOVIE:
                result = await self._enrich_movie(original)
            elif detected_type == ContentType.SERIES:
                result = await self._enrich_series(original)
            else:
                result = await self._enrich_generic(original)
            
            if result:
                enriched = result
                sources_used = result.sources
            
            processing_time = (datetime.now() - start).total_seconds()
            
            return EnrichmentResult(
                success=True,
                content_type=detected_type,
                original_metadata=original,
                enriched_metadata=enriched,
                sources_used=sources_used,
                processing_time=processing_time,
            )
            
        except Exception as e:
            logger.error(f"Enrichment error: {e}")
            return EnrichmentResult(
                success=False,
                content_type=detected_type,
                original_metadata=original,
                error_message=str(e),
            )
    
    def _detect_content_type(self, metadata: Dict[str, Any]) -> ContentType:
        """Detect content type from metadata."""
        # Check for music indicators
        if any(k in metadata for k in ["artist", "album", "track", "disc"]):
            return ContentType.MUSIC
        
        # Check for video/movie indicators
        if any(k in metadata for k in ["director", "imdb", "tmdb"]):
            if "season" in metadata or "episode" in metadata:
                return ContentType.SERIES
            return ContentType.MOVIE
        
        return ContentType.UNKNOWN
    
    async def _enrich_music(self, metadata: Dict[str, Any]) -> Optional[EnrichedMetadata]:
        """Enrich music metadata."""
        enriched = EnrichedMetadata()
        
        title = metadata.get("title", "")
        artist = metadata.get("artist", "")
        album = metadata.get("album", "")
        
        enriched.title = title
        enriched.artist = artist
        enriched.album = album
        
        # Try MusicBrainz
        mb_data = await self._query_musicbrainz(title, artist, album)
        if mb_data:
            enriched.sources.append("musicbrainz")
            if mb_data.get("year"):
                enriched.year = mb_data["year"]
            if mb_data.get("genre"):
                enriched.genre = mb_data["genre"]
            if mb_data.get("cover_url"):
                enriched.cover_url = mb_data["cover_url"]
            enriched.external_ids["musicbrainz"] = mb_data.get("mbid", "")
            enriched.confidence = 0.8
        
        # Try Last.fm
        if self.config.lastfm_api_key:
            lastfm_data = await self._query_lastfm(title, artist)
            if lastfm_data:
                enriched.sources.append("lastfm")
                if not enriched.tags and lastfm_data.get("tags"):
                    enriched.tags = lastfm_data["tags"]
                if not enriched.description and lastfm_data.get("wiki"):
                    enriched.description = lastfm_data["wiki"]
        
        # Fetch cover art
        if enriched.cover_url and self.config.fetch_covers:
            cover_path = await self._download_cover(enriched.cover_url, enriched.title)
            if cover_path:
                enriched.cover_path = cover_path
        
        return enriched
    
    async def _query_musicbrainz(
        self,
        title: str,
        artist: str,
        album: str,
    ) -> Optional[Dict[str, Any]]:
        """Query MusicBrainz API."""
        if not self._session:
            return None
        
        try:
            # Search for recording
            query = f'recording:"{title}"'
            if artist:
                query += f' AND artist:"{artist}"'
            if album:
                query += f' AND release:"{album}"'
            
            url = f"https://musicbrainz.org/ws/2/recording/?query={query}&fmt=json&limit=1"
            
            async with self._session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    recordings = data.get("recordings", [])
                    
                    if recordings:
                        rec = recordings[0]
                        result = {
                            "mbid": rec.get("id"),
                            "title": rec.get("title"),
                        }
                        
                        # Get artist
                        if rec.get("artist-credit"):
                            result["artist"] = rec["artist-credit"][0].get("name", "")
                        
                        # Get release info
                        if rec.get("releases"):
                            release = rec["releases"][0]
                            result["album"] = release.get("title")
                            if release.get("date"):
                                try:
                                    result["year"] = int(release["date"][:4])
                                except (ValueError, TypeError):
                                    pass
                        
                        return result
            
            return None
            
        except Exception as e:
            logger.warning(f"MusicBrainz query error: {e}")
            return None
    
    async def _query_lastfm(
        self,
        title: str,
        artist: str,
    ) -> Optional[Dict[str, Any]]:
        """Query Last.fm API."""
        if not self._session or not self.config.lastfm_api_key:
            return None
        
        try:
            url = f"http://ws.audioscrobbler.com/2.0/?method=track.getinfo"
            params = {
                "api_key": self.config.lastfm_api_key,
                "artist": artist,
                "track": title,
                "format": "json",
            }
            
            async with self._session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    track = data.get("track", {})
                    
                    result = {}
                    
                    # Get tags
                    if track.get("toptags"):
                        result["tags"] = [t["name"] for t in track["toptags"].get("tag", [])]
                    
                    # Get wiki
                    if track.get("wiki"):
                        result["wiki"] = track["wiki"].get("summary", "")
                    
                    return result
            
            return None
            
        except Exception as e:
            logger.warning(f"Last.fm query error: {e}")
            return None
    
    async def _enrich_movie(self, metadata: Dict[str, Any]) -> Optional[EnrichedMetadata]:
        """Enrich movie metadata."""
        enriched = EnrichedMetadata()
        title = metadata.get("title", "")
        year = metadata.get("year")
        
        enriched.title = title
        if year:
            enriched.year = year
        
        # Try TMDB
        if self.config.tmdb_api_key:
            tmdb_data = await self._query_tmdb(title, year, "movie")
            if tmdb_data:
                enriched.sources.append("tmdb")
                enriched.description = tmdb_data.get("overview", "")
                enriched.rating = tmdb_data.get("vote_average", 0)
                enriched.genre = tmdb_data.get("genres", [])
                enriched.cover_url = tmdb_data.get("poster_path")
                enriched.external_ids["tmdb"] = str(tmdb_data.get("id", ""))
                enriched.confidence = 0.85
        
        return enriched
    
    async def _query_tmdb(
        self,
        title: str,
        year: Optional[int],
        media_type: str,
    ) -> Optional[Dict[str, Any]]:
        """Query TMDB API."""
        if not self._session or not self.config.tmdb_api_key:
            return None
        
        try:
            url = f"https://api.themoviedb.org/3/search/{media_type}"
            params = {
                "api_key": self.config.tmdb_api_key,
                "query": title,
            }
            
            if year:
                params["year"] = year
            
            async with self._session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get("results", [])
                    
                    if results:
                        movie = results[0]
                        return {
                            "id": movie.get("id"),
                            "title": movie.get("title") or movie.get("name"),
                            "overview": movie.get("overview"),
                            "vote_average": movie.get("vote_average", 0),
                            "genres": [],  # Would need additional API call
                            "poster_path": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None,
                            "release_date": movie.get("release_date"),
                        }
            
            return None
            
        except Exception as e:
            logger.warning(f"TMDB query error: {e}")
            return None
    
    async def _enrich_series(self, metadata: Dict[str, Any]) -> Optional[EnrichedMetadata]:
        """Enrich TV series metadata."""
        enriched = EnrichedMetadata()
        title = metadata.get("title", "")
        
        enriched.title = title
        
        # Try TMDB for TV
        if self.config.tmdb_api_key:
            tmdb_data = await self._query_tmdb(title, None, "tv")
            if tmdb_data:
                enriched.sources.append("tmdb")
                enriched.description = tmdb_data.get("overview", "")
                enriched.rating = tmdb_data.get("vote_average", 0)
                enriched.cover_url = tmdb_data.get("poster_path")
                enriched.confidence = 0.8
        
        return enriched
    
    async def _enrich_generic(self, metadata: Dict[str, Any]) -> Optional[EnrichedMetadata]:
        """Enrich generic content metadata."""
        enriched = EnrichedMetadata()
        enriched.title = metadata.get("title", "")
        enriched.artist = metadata.get("artist")
        enriched.album = metadata.get("album")
        enriched.year = metadata.get("year")
        enriched.confidence = 0.5
        enriched.sources.append("local")
        return enriched
    
    async def _download_cover(
        self,
        url: str,
        title: str,
    ) -> Optional[Path]:
        """Download cover art."""
        if not self._session:
            return None
        
        try:
            # Generate filename
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
            filename = f"{safe_title}_cover.jpg"
            filepath = self.config.cover_dir / filename
            
            async with self._session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    async with aiofiles.open(filepath, 'wb') as f:
                        await f.write(content)
                    
                    return filepath
            
            return None
            
        except Exception as e:
            logger.warning(f"Cover download error: {e}")
            return None
    
    async def enrich_file(
        self,
        file_path: Path,
    ) -> EnrichmentResult:
        """
        Enrich metadata from file.
        
        Args:
            file_path: Path to media file
            
        Returns:
            EnrichmentResult
        """
        # Extract basic metadata from file
        metadata = await self._extract_file_metadata(file_path)
        
        return await self.enrich(
            title=metadata.get("title"),
            artist=metadata.get("artist"),
            album=metadata.get("album"),
            existing_metadata=metadata,
        )
    
    async def _extract_file_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from file using ffprobe."""
        ffprobe = shutil.which("ffprobe")
        if not ffprobe:
            return {"title": file_path.stem}
        
        try:
            cmd = [
                ffprobe,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                str(file_path),
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, _ = await process.communicate()
            
            if process.returncode == 0:
                data = json.loads(stdout.decode())
                tags = data.get("format", {}).get("tags", {})
                
                return {
                    "title": tags.get("title", file_path.stem),
                    "artist": tags.get("artist"),
                    "album": tags.get("album"),
                    "year": int(tags.get("year", 0)) if tags.get("year") else None,
                }
            
            return {"title": file_path.stem}
            
        except Exception as e:
            logger.warning(f"File metadata extraction error: {e}")
            return {"title": file_path.stem}


# Convenience function
async def enrich_metadata(
    title: str,
    artist: Optional[str] = None,
    album: Optional[str] = None,
    content_type: ContentType = ContentType.MUSIC,
) -> EnrichmentResult:
    """Quick metadata enrichment function."""
    config = EnricherConfig()
    async with MetadataEnricher(config=config) as enricher:
        return await enricher.enrich(
            title=title,
            artist=artist,
            album=album,
            content_type=content_type,
        )


__all__ = [
    "MetadataEnricher",
    "EnricherConfig",
    "EnrichmentResult",
    "EnrichedMetadata",
    "EnrichmentSource",
    "ContentType",
    "enrich_metadata",
]

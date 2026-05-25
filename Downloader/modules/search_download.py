"""
OMNIPOTENT SOVEREIGN NEXUS - Search and Download Module
Version: v3.0.1 ULTIMATE NEXUS

Advanced search and download with support for:
- Multiple search engines (YouTube, SoundCloud, Vimeo, etc.)
- Advanced search filters (date, duration, quality)
- Auto-download from search results
- Search suggestions and autocomplete
- History and favorites management
- Download queue from search
- Metadata preview
- Bulk download from search

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


class SearchEngine(Enum):
    """Available search engines."""
    
    YOUTUBE = "youtube"
    YOUTUBE_MUSIC = "youtube_music"
    SOUNDCLOUD = "soundcloud"
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    SPOTIFY = "spotify"
    BANDCAMP = "bandcamp"
    DEEZER = "deezer"
    APPLE_MUSIC = "apple_music"
    ALL = "all"  # Search all platforms


class SortOrder(Enum):
    """Search result sort order."""
    
    RELEVANCE = "relevance"
    DATE = "date"
    VIEWS = "view_count"
    RATING = "rating"
    DURATION = "duration"
    TITLE = "title"


class UploadDateFilter(Enum):
    """Upload date filter options."""
    
    ANY = "any"
    HOUR = "hour"
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class DurationFilter(Enum):
    """Duration filter options."""
    
    ANY = "any"
    SHORT = "short"      # Under 4 minutes
    MEDIUM = "medium"    # 4-20 minutes
    LONG = "long"        # Over 20 minutes


@dataclass
class SearchResult:
    """
    Individual search result.
    
    Attributes:
        id: Video/audio ID
        title: Result title
        url: Result URL
        thumbnail: Thumbnail URL
        duration: Duration in seconds
        view_count: View count
        uploader: Uploader name
        uploader_url: Uploader URL
        upload_date: Upload date
        description: Short description
        platform: Source platform
        is_live: Whether currently live
        is_premium: Premium content flag
        score: Relevance score
        selected: Whether selected for download
    """
    id: str
    title: str
    url: str
    thumbnail: Optional[str] = None
    duration: int = 0
    view_count: int = 0
    uploader: Optional[str] = None
    uploader_url: Optional[str] = None
    upload_date: Optional[str] = None
    description: Optional[str] = None
    platform: SearchEngine = SearchEngine.YOUTUBE
    is_live: bool = False
    is_premium: bool = False
    score: float = 0.0
    selected: bool = False
    
    @property
    def duration_formatted(self) -> str:
        """Return formatted duration."""
        if self.duration == 0:
            return "Unknown"
        
        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "thumbnail": self.thumbnail,
            "duration": self.duration,
            "duration_formatted": self.duration_formatted,
            "view_count": self.view_count,
            "uploader": self.uploader,
            "uploader_url": self.uploader_url,
            "upload_date": self.upload_date,
            "description": self.description,
            "platform": self.platform.value,
            "is_live": self.is_live,
            "is_premium": self.is_premium,
            "score": self.score,
            "selected": self.selected,
        }


@dataclass
class SearchConfig:
    """
    Configuration for search operations.
    
    Attributes:
        engine: Search engine to use
        max_results: Maximum results to return
        sort: Sort order
        upload_date: Upload date filter
        duration: Duration filter
        min_views: Minimum view count
        min_duration: Minimum duration in seconds
        max_duration: Maximum duration in seconds
        exclude_words: Words to exclude
        exact_match: Require exact phrase match
        safe_search: Enable safe search
        proxy: Proxy URL
        cookies_file: Path to cookies file
        timeout: Request timeout
    """
    engine: SearchEngine = SearchEngine.YOUTUBE
    max_results: int = 20
    sort: SortOrder = SortOrder.RELEVANCE
    upload_date: UploadDateFilter = UploadDateFilter.ANY
    duration: DurationFilter = DurationFilter.ANY
    min_views: int = 0
    min_duration: int = 0
    max_duration: int = 0
    exclude_words: List[str] = field(default_factory=list)
    exact_match: bool = False
    safe_search: bool = True
    proxy: Optional[str] = None
    cookies_file: Optional[Path] = None
    timeout: float = 30.0


@dataclass
class SearchResponse:
    """
    Complete search response.
    
    Attributes:
        query: Original search query
        results: List of search results
        total_results: Total available results
        page: Current page number
        has_more: Whether more results available
        search_time: Search duration in seconds
        suggestions: Search suggestions
        corrected_query: Auto-corrected query
    """
    query: str
    results: List[SearchResult] = field(default_factory=list)
    total_results: int = 0
    page: int = 1
    has_more: bool = False
    search_time: float = 0.0
    suggestions: List[str] = field(default_factory=list)
    corrected_query: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "results": [r.to_dict() for r in self.results],
            "total_results": self.total_results,
            "page": self.page,
            "has_more": self.has_more,
            "search_time": self.search_time,
            "suggestions": self.suggestions,
            "corrected_query": self.corrected_query,
        }


class SearchDownloader:
    """
    OMNIPOTENT SOVEREIGN NEXUS Search and Download.
    
    Advanced search with download capabilities:
    - Multiple search engines
    - Advanced filtering
    - Auto-download from results
    - Search suggestions
    """
    
    def __init__(
        self,
        config: Optional[SearchConfig] = None,
        result_callback: Optional[Callable[[SearchResult], Awaitable[None]]] = None,
    ) -> None:
        """
        Initialize the search downloader.
        
        Args:
            config: Search configuration
            result_callback: Callback for each result found
        """
        self.config = config or SearchConfig()
        self._result_callback = result_callback
        self._history: List[str] = []
        self._favorites: List[str] = []
        self._cache: Dict[str, SearchResponse] = {}
        
        logger.info(f"SearchDownloader initialized v3.0.1 ULTIMATE NEXUS")
    
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
    
    async def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        engine: Optional[SearchEngine] = None,
    ) -> SearchResponse:
        """
        Search for content.
        
        Args:
            query: Search query
            max_results: Override max results
            engine: Override search engine
            
        Returns:
            SearchResponse with results
        """
        start_time = datetime.now()
        
        # Check cache
        cache_key = f"{query}_{max_results or self.config.max_results}_{engine or self.config.engine}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        max_res = max_results or self.config.max_results
        search_engine = engine or self.config.engine
        
        # Build search URL
        if search_engine == SearchEngine.ALL:
            results = await self._search_all(query, max_res)
        else:
            results = await self._search_single(query, max_res, search_engine)
        
        # Calculate search time
        search_time = (datetime.now() - start_time).total_seconds()
        
        # Build response
        response = SearchResponse(
            query=query,
            results=results[:max_res],
            total_results=len(results),
            has_more=len(results) > max_res,
            search_time=search_time,
        )
        
        # Add to history
        self._add_to_history(query)
        
        # Cache result
        self._cache[cache_key] = response
        
        return response
    
    async def _search_single(
        self,
        query: str,
        max_results: int,
        engine: SearchEngine,
    ) -> List[SearchResult]:
        """Search single platform."""
        yt_dlp = self._get_yt_dlp_path()
        if not yt_dlp:
            logger.error("yt-dlp not found")
            return []
        
        try:
            # Build search URL for yt-dlp
            search_prefix = self._get_search_prefix(engine)
            search_url = f"{search_prefix}{max_results}:{query}"
            
            cmd = [
                yt_dlp,
                "--flat-playlist",
                "--dump-json",
                "--no-download",
                search_url,
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
                results = []
                
                for line in stdout.decode().strip().split('\n'):
                    if line:
                        try:
                            data = json.loads(line)
                            result = SearchResult(
                                id=data.get('id', ''),
                                title=data.get('title', ''),
                                url=data.get('url', ''),
                                thumbnail=data.get('thumbnail'),
                                duration=data.get('duration', 0),
                                view_count=data.get('view_count', 0),
                                uploader=data.get('uploader'),
                                upload_date=data.get('upload_date'),
                                platform=engine,
                            )
                            results.append(result)
                            
                            # Callback
                            if self._result_callback:
                                await self._result_callback(result)
                                
                        except json.JSONDecodeError:
                            continue
                
                return results
            
            return []
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    async def _search_all(
        self,
        query: str,
        max_results: int,
    ) -> List[SearchResult]:
        """Search all platforms."""
        # Split results across platforms
        per_platform = max_results // 4
        
        tasks = [
            self._search_single(query, per_platform, SearchEngine.YOUTUBE),
            self._search_single(query, per_platform, SearchEngine.SOUNDCLOUD),
            self._search_single(query, per_platform, SearchEngine.VIMEO),
            self._search_single(query, per_platform, SearchEngine.DAILYMOTION),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_results = []
        for r in results:
            if isinstance(r, list):
                all_results.extend(r)
        
        # Sort by relevance (title match)
        query_lower = query.lower()
        all_results.sort(
            key=lambda x: x.score if x.score > 0 else 
                (1.0 if query_lower in x.title.lower() else 0.5),
            reverse=True,
        )
        
        return all_results
    
    def _get_search_prefix(self, engine: SearchEngine) -> str:
        """Get yt-dlp search prefix for engine."""
        prefixes = {
            SearchEngine.YOUTUBE: "ytsearch",
            SearchEngine.YOUTUBE_MUSIC: "ytmsearch",
            SearchEngine.SOUNDCLOUD: "scsearch",
            SearchEngine.VIMEO: "vimeosearch",
            SearchEngine.DAILYMOTION: "dmsearch",
            SearchEngine.SPOTIFY: "spotifysearch",
            SearchEngine.BANDCAMP: "bcsearch",
            SearchEngine.DEEZER: "dzsearch",
        }
        return prefixes.get(engine, "ytsearch")
    
    async def search_and_download(
        self,
        query: str,
        max_results: int = 1,
        output_dir: Path = Path("./downloads"),
        auto_download: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Search and optionally auto-download results.
        
        Args:
            query: Search query
            max_results: Number of results to download
            output_dir: Output directory
            auto_download: Automatically download results
            
        Returns:
            List of download results
        """
        # Search
        response = await self.search(query, max_results=max_results)
        
        if not auto_download:
            return [r.to_dict() for r in response.results]
        
        # Download results
        results = []
        yt_dlp = self._get_yt_dlp_path()
        
        if not yt_dlp:
            return results
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for result in response.results:
            try:
                cmd = [
                    yt_dlp,
                    "-f", "bestvideo+bestaudio/best",
                    "--merge-output-format", "mp4",
                    "-o", str(output_dir / "%(title)s.%(ext)s"),
                    result.url,
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                
                await process.communicate()
                
                results.append({
                    "result": result.to_dict(),
                    "download_success": process.returncode == 0,
                })
                
            except Exception as e:
                results.append({
                    "result": result.to_dict(),
                    "download_success": False,
                    "error": str(e),
                })
        
        return results
    
    async def get_suggestions(self, query: str) -> List[str]:
        """
        Get search suggestions for partial query.
        
        Args:
            query: Partial search query
            
        Returns:
            List of suggestions
        """
        # YouTube suggestions API
        try:
            async with aiohttp.ClientSession() as session:
                url = f"http://suggestqueries.google.com/complete/search?client=firefox&q={query}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if len(data) > 1:
                            return data[1]
        except Exception as e:
            logger.debug(f"Failed to get suggestions: {e}")
        
        return []
    
    def _add_to_history(self, query: str) -> None:
        """Add query to search history."""
        if query in self._history:
            self._history.remove(query)
        self._history.insert(0, query)
        
        # Keep last 100 searches
        if len(self._history) > 100:
            self._history = self._history[:100]
    
    def get_history(self, limit: int = 20) -> List[str]:
        """Get search history."""
        return self._history[:limit]
    
    def clear_history(self) -> None:
        """Clear search history."""
        self._history.clear()
    
    def add_favorite(self, url: str) -> None:
        """Add URL to favorites."""
        if url not in self._favorites:
            self._favorites.append(url)
    
    def remove_favorite(self, url: str) -> None:
        """Remove URL from favorites."""
        if url in self._favorites:
            self._favorites.remove(url)
    
    def get_favorites(self) -> List[str]:
        """Get favorite URLs."""
        return self._favorites.copy()
    
    def clear_cache(self) -> None:
        """Clear search cache."""
        self._cache.clear()
    
    async def download_from_favorites(
        self,
        output_dir: Path = Path("./downloads"),
    ) -> List[Dict[str, Any]]:
        """
        Download all favorites.
        
        Args:
            output_dir: Output directory
            
        Returns:
            List of download results
        """
        results = []
        
        for url in self._favorites:
            yt_dlp = self._get_yt_dlp_path()
            
            if not yt_dlp:
                continue
            
            try:
                cmd = [
                    yt_dlp,
                    "-f", "bestvideo+bestaudio/best",
                    "--merge-output-format", "mp4",
                    "-o", str(output_dir / "%(title)s.%(ext)s"),
                    url,
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                
                await process.communicate()
                
                results.append({
                    "url": url,
                    "success": process.returncode == 0,
                })
                
            except Exception as e:
                results.append({
                    "url": url,
                    "success": False,
                    "error": str(e),
                })
        
        return results


# Convenience functions
async def search_videos(
    query: str,
    max_results: int = 20,
    engine: SearchEngine = SearchEngine.YOUTUBE,
) -> SearchResponse:
    """
    Quick search function.
    
    Args:
        query: Search query
        max_results: Maximum results
        engine: Search engine
        
    Returns:
        SearchResponse
    """
    config = SearchConfig(
        engine=engine,
        max_results=max_results,
    )
    
    searcher = SearchDownloader(config=config)
    return await searcher.search(query)


async def search_and_download(
    query: str,
    output_dir: str = "./downloads",
    max_results: int = 1,
) -> List[Dict[str, Any]]:
    """
    Quick search and download function.
    
    Args:
        query: Search query
        output_dir: Output directory
        max_results: Number of results to download
        
    Returns:
        List of results
    """
    searcher = SearchDownloader()
    return await searcher.search_and_download(
        query,
        max_results=max_results,
        output_dir=Path(output_dir),
    )


__all__ = [
    "SearchDownloader",
    "SearchEngine",
    "SortOrder",
    "UploadDateFilter",
    "DurationFilter",
    "SearchResult",
    "SearchConfig",
    "SearchResponse",
    "search_videos",
    "search_and_download",
]

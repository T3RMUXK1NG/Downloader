"""
OMNIPOTENT SOVEREIGN NEXUS - Downloader Modules Package
Version: v3.0.1 ULTIMATE NEXUS

Comprehensive media downloading and processing toolkit with:
- Multi-platform video/audio downloading
- Playlist processing with parallel downloads
- Thumbnail extraction and metadata management
- Subtitle downloading with translation support (100+ languages)
- Batch processing with ML-powered smart scheduling
- Media format conversion
- AI-powered video summarization
- Cloud storage integration (Google Drive, Dropbox, Mega)
- Live stream recording
- Video editing capabilities
- Audio enhancement with AI
- Advanced thumbnail generation
- Metadata enrichment

Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
"""

__version__ = "3.0.1"
__author__ = "RAJSARASWATI JATAV (RS)"
__codename__ = "ULTIMATE NEXUS"

# Core downloader modules
from .video_downloader import (
    VideoDownloader,
    VideoQuality,
    VideoFormat,
    DownloadResult,
    DownloadProgress,
)
from .audio_downloader import (
    AudioDownloader,
    AudioQuality,
    AudioFormat,
    AudioDownloadResult,
)
from .playlist_downloader import (
    PlaylistDownloader,
    PlaylistInfo,
    PlaylistItem,
    PlaylistProgress,
)
from .thumbnail_grabber import (
    ThumbnailGrabber,
    ThumbnailFormat,
    ThumbnailQuality,
    ThumbnailResult,
)
from .metadata_extractor import (
    MetadataExtractor,
    MediaMetadata,
    VideoMetadata,
    AudioMetadata,
)
from .subtitle_downloader import (
    SubtitleDownloader,
    SubtitleFormat,
    SubtitleLanguage,
    SubtitleResult,
)
from .batch_downloader import (
    BatchDownloader,
    BatchConfig,
    BatchProgress,
    BatchResult,
)
from .search_download import (
    SearchDownloader,
    SearchEngine,
    SearchResult,
    SearchConfig,
)
from .media_converter import (
    MediaConverter,
    ConversionFormat,
    ConversionPreset,
    ConversionResult,
)

# New advanced modules - ULTIMATE NEXUS v3.0.1
from .live_stream import (
    LiveStreamRecorder,
    StreamPlatform,
    StreamQuality,
    StreamStatus,
    StreamInfo,
    RecordingProgress,
    RecordingResult,
    RecordingConfig,
    StreamDetector,
    record_stream,
)
from .ai_tools import (
    AITools,
    AIProvider,
    AIConfig,
    Language,
    SummaryLength,
    SentimentType,
    SummarizationResult,
    TranslationResult,
    SentimentResult,
    KeywordExtractionResult,
    ContentAnalysisResult,
    summarize_text,
    translate_text,
    analyze_text,
)
from .cloud_sync import (
    CloudSync,
    CloudProvider,
    CloudConfig,
    CloudFile,
    SyncDirection,
    ConflictResolution,
    TransferStatus,
    TransferProgress,
    TransferResult,
    SyncResult,
    upload_to_cloud,
    download_from_cloud,
)
from .video_editor import (
    VideoEditor,
    VideoCodec,
    AudioCodec,
    VideoFilter,
    TransitionType,
    VideoInfo,
    TrimConfig,
    MergeConfig,
    EffectConfig,
    WatermarkConfig,
    EditProgress,
    EditResult,
    trim_video,
    merge_videos,
)
from .audio_enhancer import (
    AudioEnhancer,
    AudioFormat,
    EnhancementType,
    NoiseProfile,
    EnhanceStatus,
    AudioInfo,
    EnhancementConfig,
    EnhancementProgress,
    EnhancementResult,
    AudioAnalysis,
    reduce_audio_noise,
    normalize_audio,
)
from .subtitle_ai import (
    SubtitleAI,
    SubtitleFormat,
    SubtitleLanguage,
    SubtitleStatus,
    SubtitleEntry,
    SubtitleConfig,
    SubtitleProgress,
    SubtitleResult,
    generate_subtitles,
)
from .proxy_manager import (
    ProxyManager,
    ProxyType,
    ProxyStatus,
    RotationStrategy,
    ProxyInfo,
    ProxyPoolConfig,
    ProxyTestResult,
    create_proxy_manager,
)
from .scheduler import (
    DownloadScheduler,
    ScheduleType,
    TaskStatus,
    TaskPriority,
    ScheduledTask,
    ScheduleConfig,
    TaskResult,
    SchedulerStats,
)
from .analytics import (
    Analytics,
    TimePeriod,
    DownloadStatus,
    ReportFormat,
    DownloadRecord,
    PlatformStats,
    TimeBasedStats,
    AnalyticsSummary,
    ReportConfig,
    create_analytics,
)
from .security import (
    SecurityTools,
    HashAlgorithm,
    EncryptionAlgorithm,
    SecurityLevel,
    ThreatLevel,
    HashResult,
    VerificationResult,
    EncryptionResult,
    URLValidationResult,
    FileIntegrityReport,
    hash_file,
    verify_file_hash,
)

# Common utilities and types
from typing import Dict, List, Optional, Union, Callable, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
from pathlib import Path


@dataclass
class DownloaderConfig:
    """
    Global configuration for all downloader modules.
    
    Attributes:
        output_dir: Default output directory for downloads
        max_concurrent: Maximum concurrent downloads
        retry_count: Number of retry attempts for failed downloads
        retry_delay: Base delay between retries (exponential backoff)
        timeout: Request timeout in seconds
        proxy: Proxy URL (HTTP/HTTPS/SOCKS5)
        cookies_file: Path to cookies file for authentication
        rate_limit: Maximum download speed in bytes/sec (0 = unlimited)
        user_agent: Custom user agent string
        verify_ssl: Whether to verify SSL certificates
    """
    output_dir: Path = Path("./downloads")
    max_concurrent: int = 4
    retry_count: int = 3
    retry_delay: float = 1.0
    timeout: float = 300.0
    proxy: Optional[str] = None
    cookies_file: Optional[Path] = None
    rate_limit: int = 0
    user_agent: Optional[str] = None
    verify_ssl: bool = True


class DownloaderRegistry:
    """
    Central registry for all downloader instances.
    Manages shared configuration and resources.
    """
    
    _instance: Optional["DownloaderRegistry"] = None
    _downloaders: Dict[str, Any] = {}
    _config: DownloaderConfig = DownloaderConfig()
    
    def __new__(cls) -> "DownloaderRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def register(cls, name: str, downloader: Any) -> None:
        """Register a downloader instance."""
        cls._downloaders[name] = downloader
    
    @classmethod
    def get(cls, name: str) -> Optional[Any]:
        """Get a registered downloader by name."""
        return cls._downloaders.get(name)
    
    @classmethod
    def get_config(cls) -> DownloaderConfig:
        """Get the global configuration."""
        return cls._config
    
    @classmethod
    def set_config(cls, config: DownloaderConfig) -> None:
        """Set the global configuration."""
        cls._config = config
    
    @classmethod
    def list_downloaders(cls) -> List[str]:
        """List all registered downloader names."""
        return list(cls._downloaders.keys())


def get_version() -> str:
    """Return the package version."""
    return __version__


def create_default_config(output_dir: str = "./downloads") -> DownloaderConfig:
    """
    Create a default configuration with specified output directory.
    
    Args:
        output_dir: Path to the output directory
        
    Returns:
        Configured DownloaderConfig instance
    """
    return DownloaderConfig(output_dir=Path(output_dir))


__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__codename__",
    "get_version",
    
    # Configuration
    "DownloaderConfig",
    "DownloaderRegistry",
    "create_default_config",
    
    # Video Downloader
    "VideoDownloader",
    "VideoQuality",
    "VideoFormat",
    "DownloadResult",
    "DownloadProgress",
    
    # Audio Downloader
    "AudioDownloader",
    "AudioQuality",
    "AudioFormat",
    "AudioDownloadResult",
    
    # Playlist Downloader
    "PlaylistDownloader",
    "PlaylistInfo",
    "PlaylistItem",
    "PlaylistProgress",
    
    # Thumbnail Grabber
    "ThumbnailGrabber",
    "ThumbnailFormat",
    "ThumbnailQuality",
    "ThumbnailResult",
    
    # Metadata Extractor
    "MetadataExtractor",
    "MediaMetadata",
    "VideoMetadata",
    "AudioMetadata",
    
    # Subtitle Downloader
    "SubtitleDownloader",
    "SubtitleFormat",
    "SubtitleLanguage",
    "SubtitleResult",
    
    # Batch Downloader
    "BatchDownloader",
    "BatchConfig",
    "BatchProgress",
    "BatchResult",
    
    # Search Download
    "SearchDownloader",
    "SearchEngine",
    "SearchResult",
    "SearchConfig",
    
    # Media Converter
    "MediaConverter",
    "ConversionFormat",
    "ConversionPreset",
    "ConversionResult",
    
    # Live Stream Recording (NEW v3.0.1)
    "LiveStreamRecorder",
    "StreamPlatform",
    "StreamQuality",
    "StreamStatus",
    "StreamInfo",
    "RecordingProgress",
    "RecordingResult",
    "RecordingConfig",
    "StreamDetector",
    "record_stream",
    
    # AI Tools (NEW v3.0.1)
    "AITools",
    "AIProvider",
    "AIConfig",
    "Language",
    "SummaryLength",
    "SentimentType",
    "SummarizationResult",
    "TranslationResult",
    "SentimentResult",
    "KeywordExtractionResult",
    "ContentAnalysisResult",
    "summarize_text",
    "translate_text",
    "analyze_text",
    
    # Cloud Sync (NEW v3.0.1)
    "CloudSync",
    "CloudProvider",
    "CloudConfig",
    "CloudFile",
    "SyncDirection",
    "ConflictResolution",
    "TransferStatus",
    "TransferProgress",
    "TransferResult",
    "SyncResult",
    "upload_to_cloud",
    "download_from_cloud",
    
    # Video Editor (NEW v3.0.1)
    "VideoEditor",
    "VideoCodec",
    "AudioCodec",
    "VideoFilter",
    "TransitionType",
    "VideoInfo",
    "TrimConfig",
    "MergeConfig",
    "EffectConfig",
    "WatermarkConfig",
    "EditProgress",
    "EditResult",
    "trim_video",
    "merge_videos",
    
    # Audio Enhancer (NEW v3.0.1)
    "AudioEnhancer",
    "AudioFormat",
    "EnhancementType",
    "NoiseProfile",
    "EnhanceStatus",
    "AudioInfo",
    "EnhancementConfig",
    "EnhancementProgress",
    "EnhancementResult",
    "AudioAnalysis",
    "reduce_audio_noise",
    "normalize_audio",
    
    # Subtitle AI (NEW v3.0.1)
    "SubtitleAI",
    "SubtitleFormat",
    "SubtitleLanguage",
    "SubtitleStatus",
    "SubtitleEntry",
    "SubtitleConfig",
    "SubtitleProgress",
    "SubtitleResult",
    "generate_subtitles",
    
    # Proxy Manager (NEW v3.0.1)
    "ProxyManager",
    "ProxyType",
    "ProxyStatus",
    "RotationStrategy",
    "ProxyInfo",
    "ProxyPoolConfig",
    "ProxyTestResult",
    "create_proxy_manager",
    
    # Scheduler (NEW v3.0.1)
    "DownloadScheduler",
    "ScheduleType",
    "TaskStatus",
    "TaskPriority",
    "ScheduledTask",
    "ScheduleConfig",
    "TaskResult",
    "SchedulerStats",
    
    # Analytics (NEW v3.0.1)
    "Analytics",
    "TimePeriod",
    "DownloadStatus",
    "ReportFormat",
    "DownloadRecord",
    "PlatformStats",
    "TimeBasedStats",
    "AnalyticsSummary",
    "ReportConfig",
    "create_analytics",
    
    # Security (NEW v3.0.1)
    "SecurityTools",
    "HashAlgorithm",
    "EncryptionAlgorithm",
    "SecurityLevel",
    "ThreatLevel",
    "HashResult",
    "VerificationResult",
    "EncryptionResult",
    "URLValidationResult",
    "FileIntegrityReport",
    "hash_file",
    "verify_file_hash",
]

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - Modules Package                             ║
║  Author: RS (T3rmuxk1ng)                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from .video_downloader import VideoDownloader
from .audio_downloader import AudioDownloader
from .playlist_downloader import PlaylistDownloader
from .thumbnail_grabber import ThumbnailGrabber
from .metadata_extractor import MetadataExtractor
from .subtitle_downloader import SubtitleDownloader
from .batch_downloader import BatchDownloader
from .search_download import SearchDownload
from .media_converter import MediaConverter

__all__ = [
    'VideoDownloader',
    'AudioDownloader',
    'PlaylistDownloader',
    'ThumbnailGrabber',
    'MetadataExtractor',
    'SubtitleDownloader',
    'BatchDownloader',
    'SearchDownload',
    'MediaConverter',
]

# Module info
MODULES = {
    '1': ('Video Downloader', VideoDownloader),
    '2': ('Audio Downloader', AudioDownloader),
    '3': ('Playlist Downloader', PlaylistDownloader),
    '4': ('Thumbnail Grabber', ThumbnailGrabber),
    '5': ('Metadata Extractor', MetadataExtractor),
    '6': ('Subtitle Downloader', SubtitleDownloader),
    '7': ('Batch Downloader', BatchDownloader),
    '8': ('Search & Download', SearchDownload),
    '9': ('Media Converter', MediaConverter),
}

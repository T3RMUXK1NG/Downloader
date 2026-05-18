#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - URL Validator                               ║
║  Author: RS (T3rmuxk1ng)                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import re
from typing import Tuple, Optional, List
from urllib.parse import urlparse, parse_qs


class URLValidator:
    """
    URL validation and parsing for YouTube and other platforms
    - YouTube videos, shorts, playlists, live streams
    - Channel URLs
    - General URL validation
    """
    
    # YouTube URL patterns
    YOUTUBE_PATTERNS = {
        'video': [
            r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
        ],
        'shorts': [
            r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
        ],
        'live': [
            r'youtube\.com/live/([a-zA-Z0-9_-]{11})',
        ],
        'playlist': [
            r'youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)',
            r'youtube\.com/watch\?.*list=([a-zA-Z0-9_-]+)',
        ],
        'channel': [
            r'youtube\.com/channel/([a-zA-Z0-9_-]+)',
            r'youtube\.com/@([a-zA-Z0-9_-]+)',
            r'youtube\.com/c/([a-zA-Z0-9_-]+)',
            r'youtube\.com/user/([a-zA-Z0-9_-]+)',
        ],
    }
    
    # Supported platforms
    SUPPORTED_PLATFORMS = [
        'youtube.com',
        'youtu.be',
        'www.youtube.com',
        'm.youtube.com',
    ]
    
    @classmethod
    def validate_url(cls, url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate any URL
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url:
            return False, "URL is empty"
        
        url = url.strip()
        
        # Check if URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            parsed = urlparse(url)
            
            if not parsed.netloc:
                return False, "Invalid URL format"
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    @classmethod
    def is_youtube_url(cls, url: str) -> bool:
        """Check if URL is from YouTube"""
        try:
            parsed = urlparse(url if '://' in url else 'https://' + url)
            domain = parsed.netloc.lower().replace('www.', '')
            return domain in cls.SUPPORTED_PLATFORMS
        except:
            return False
    
    @classmethod
    def get_youtube_video_id(cls, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        for pattern in cls.YOUTUBE_PATTERNS['video']:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # Also check shorts and live
        for patterns in [cls.YOUTUBE_PATTERNS['shorts'], cls.YOUTUBE_PATTERNS['live']]:
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
        
        return None
    
    @classmethod
    def get_youtube_playlist_id(cls, url: str) -> Optional[str]:
        """Extract YouTube playlist ID from URL"""
        for pattern in cls.YOUTUBE_PATTERNS['playlist']:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    @classmethod
    def get_youtube_channel_id(cls, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract YouTube channel identifier
        
        Returns:
            Tuple of (identifier, type) where type is 'id', 'handle', or 'custom'
        """
        # Channel ID
        for pattern in cls.YOUTUBE_PATTERNS['channel'][:1]:
            match = re.search(pattern, url)
            if match:
                return match.group(1), 'id'
        
        # Handle (@username)
        for pattern in cls.YOUTUBE_PATTERNS['channel'][1:2]:
            match = re.search(pattern, url)
            if match:
                return match.group(1), 'handle'
        
        # Custom URL
        for pattern in cls.YOUTUBE_PATTERNS['channel'][2:]:
            match = re.search(pattern, url)
            if match:
                return match.group(1), 'custom'
        
        return None, None
    
    @classmethod
    def get_url_type(cls, url: str) -> str:
        """
        Determine URL type
        
        Returns:
            'video', 'playlist', 'channel', 'shorts', 'live', or 'unknown'
        """
        if not cls.is_youtube_url(url):
            return 'unknown'
        
        # Check for playlist
        if cls.get_youtube_playlist_id(url):
            return 'playlist'
        
        # Check for channel
        channel_id, _ = cls.get_youtube_channel_id(url)
        if channel_id:
            return 'channel'
        
        # Check for shorts
        for pattern in cls.YOUTUBE_PATTERNS['shorts']:
            if re.search(pattern, url):
                return 'shorts'
        
        # Check for live
        for pattern in cls.YOUTUBE_PATTERNS['live']:
            if re.search(pattern, url):
                return 'live'
        
        # Check for video
        if cls.get_youtube_video_id(url):
            return 'video'
        
        return 'unknown'
    
    @classmethod
    def normalize_youtube_url(cls, url: str) -> str:
        """Normalize YouTube URL to standard format"""
        video_id = cls.get_youtube_video_id(url)
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"
        return url
    
    @classmethod
    def get_thumbnail_url(cls, video_id: str, quality: str = 'maxres') -> str:
        """
        Get thumbnail URL for a video
        
        Quality options: maxres, hq, mq, sd, default
        """
        return f"https://img.youtube.com/vi/{video_id}/{quality}default.jpg"
    
    @classmethod
    def extract_urls_from_text(cls, text: str) -> List[str]:
        """Extract all URLs from text"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, text)
    
    @classmethod
    def extract_youtube_urls_from_text(cls, text: str) -> List[str]:
        """Extract only YouTube URLs from text"""
        urls = cls.extract_urls_from_text(text)
        return [url for url in urls if cls.is_youtube_url(url)]
    
    @classmethod
    def build_youtube_url(cls, video_id: str) -> str:
        """Build YouTube URL from video ID"""
        return f"https://www.youtube.com/watch?v={video_id}"
    
    @classmethod
    def build_youtube_playlist_url(cls, playlist_id: str) -> str:
        """Build YouTube playlist URL from playlist ID"""
        return f"https://www.youtube.com/playlist?list={playlist_id}"
    
    @classmethod
    def validate_video_id(cls, video_id: str) -> bool:
        """Validate YouTube video ID format"""
        return bool(re.match(r'^[a-zA-Z0-9_-]{11}$', video_id))
    
    @classmethod
    def validate_playlist_id(cls, playlist_id: str) -> bool:
        """Validate YouTube playlist ID format"""
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', playlist_id))


# Convenience functions
def validate_youtube_url(url: str) -> Tuple[bool, Optional[str]]:
    """Validate YouTube URL"""
    return URLValidator.validate_url(url)


def get_video_id(url: str) -> Optional[str]:
    """Get video ID from URL"""
    return URLValidator.get_youtube_video_id(url)


def get_playlist_id(url: str) -> Optional[str]:
    """Get playlist ID from URL"""
    return URLValidator.get_youtube_playlist_id(url)


def get_url_type(url: str) -> str:
    """Get URL type"""
    return URLValidator.get_url_type(url)

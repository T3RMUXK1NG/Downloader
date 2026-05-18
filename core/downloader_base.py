#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - Downloader Base Class                       ║
║  Author: RS (T3rmuxk1ng)                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import re
import sys
import json
import time
import shutil
import subprocess
from typing import Dict, List, Optional, Tuple, Any
from abc import ABC, abstractmethod


class DownloaderBase(ABC):
    """
    Base class for all download modules
    Contains common methods and utilities
    """
    
    # YouTube URL patterns
    YOUTUBE_PATTERNS = [
        r'(youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',  # Standard
        r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',  # Shorts
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',  # Embed
        r'youtube\.com/v/([a-zA-Z0-9_-]{11})',  # Old embed
        r'youtube\.com/live/([a-zA-Z0-9_-]{11})',  # Live
    ]
    
    # Quality mapping
    QUALITY_MAP = {
        '4k': {'height': 2160, 'label': '4K Ultra HD'},
        '2160p': {'height': 2160, 'label': '4K Ultra HD'},
        '1440p': {'height': 1440, 'label': '2K QHD'},
        '1080p': {'height': 1080, 'label': 'Full HD'},
        '720p': {'height': 720, 'label': 'HD'},
        '480p': {'height': 480, 'label': 'SD'},
        '360p': {'height': 360, 'label': 'Low'},
        '240p': {'height': 240, 'label': 'Very Low'},
        '144p': {'height': 144, 'label': 'Minimum'},
    }
    
    # Format mapping
    FORMAT_MAP = {
        'mp4': {'vcodec': 'h264', 'acodec': 'aac', 'container': 'mp4'},
        'webm': {'vcodec': 'vp9', 'acodec': 'opus', 'container': 'webm'},
        'mkv': {'vcodec': 'h264', 'acodec': 'aac', 'container': 'mkv'},
        'mp3': {'vcodec': None, 'acodec': 'mp3', 'container': 'mp3'},
        'm4a': {'vcodec': None, 'acodec': 'aac', 'container': 'm4a'},
        'opus': {'vcodec': None, 'acodec': 'opus', 'container': 'opus'},
    }
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.output_dir = self._get_default_output_dir()
        self.ffmpeg_path = self._find_ffmpeg()
        self.config = self._load_config()
        self.logger = self._get_logger()
    
    def _get_default_output_dir(self) -> str:
        """Get default output directory based on OS"""
        if os.name == 'nt':  # Windows
            base = os.path.expanduser('~/Downloads')
        elif 'TERMUX_VERSION' in os.environ:  # Termux
            base = os.path.expanduser('~/storage/downloads')
        else:  # Linux/Mac
            base = os.path.expanduser('~/Downloads')
        
        return os.path.join(base, 'RS_Downloader')
    
    def _load_config(self) -> Dict:
        """Load configuration"""
        try:
            from core.config import config
            return config
        except:
            return {}
    
    def _get_logger(self):
        """Get logger instance"""
        try:
            from core.logger import logger
            return logger
        except:
            return None
    
    def _find_ffmpeg(self) -> Optional[str]:
        """Find FFmpeg binary"""
        # Check common locations
        common_paths = [
            'ffmpeg',  # In PATH
            '/usr/bin/ffmpeg',
            '/usr/local/bin/ffmpeg',
            '/opt/homebrew/bin/ffmpeg',  # Mac Homebrew
            os.path.expanduser('~/bin/ffmpeg'),
        ]
        
        # Termux path
        if 'TERMUX_VERSION' in os.environ:
            common_paths.insert(0, '/data/data/com.termux/files/usr/bin/ffmpeg')
        
        for path in common_paths:
            try:
                result = subprocess.run(
                    [path, '-version'],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return path
            except:
                continue
        
        return None
    
    def is_ffmpeg_available(self) -> bool:
        """Check if FFmpeg is available"""
        return self.ffmpeg_path is not None
    
    def validate_youtube_url(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate YouTube URL and extract video ID
        
        Returns:
            Tuple of (is_valid, video_id)
        """
        for pattern in self.YOUTUBE_PATTERNS:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(2) if len(match.groups()) > 1 else match.group(1)
                return True, video_id
        return False, None
    
    def get_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from URL"""
        is_valid, video_id = self.validate_youtube_url(url)
        return video_id if is_valid else None
    
    def is_playlist_url(self, url: str) -> bool:
        """Check if URL is a playlist"""
        return 'playlist?list=' in url or '&list=' in url
    
    def get_playlist_id(self, url: str) -> Optional[str]:
        """Extract playlist ID from URL"""
        match = re.search(r'[?&]list=([a-zA-Z0-9_-]+)', url)
        return match.group(1) if match else None
    
    def sanitize_filename(self, filename: str, max_length: int = 200) -> str:
        """Sanitize filename for safe file operations"""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove control characters
        filename = ''.join(char for char in filename if ord(char) >= 32)
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        
        # Truncate if too long
        if len(filename) > max_length:
            filename = filename[:max_length].rstrip()
        
        return filename or 'download'
    
    def format_filesize(self, bytes: int) -> str:
        """Format bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024
        return f"{bytes:.2f} PB"
    
    def format_duration(self, seconds: int) -> str:
        """Format seconds to HH:MM:SS"""
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
    
    def format_number(self, num: int) -> str:
        """Format number with commas"""
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        return str(num)
    
    def create_output_dir(self, subfolder: str = None) -> str:
        """Create output directory and return path"""
        path = self.output_dir
        if subfolder:
            path = os.path.join(path, subfolder)
        
        os.makedirs(path, exist_ok=True)
        return path
    
    def get_unique_filename(self, filepath: str) -> str:
        """Get unique filename if file exists"""
        if not os.path.exists(filepath):
            return filepath
        
        base, ext = os.path.splitext(filepath)
        counter = 1
        
        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1
        
        return f"{base}_{counter}{ext}"
    
    def merge_video_audio(self, video_path: str, audio_path: str, output_path: str) -> bool:
        """Merge video and audio using FFmpeg"""
        if not self.is_ffmpeg_available():
            return False
        
        try:
            cmd = [
                self.ffmpeg_path, '-y',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-strict', 'experimental',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=300)
            return result.returncode == 0
        except:
            return False
    
    def convert_media(self, input_path: str, output_path: str, 
                      output_format: str = None, bitrate: str = None) -> bool:
        """Convert media using FFmpeg"""
        if not self.is_ffmpeg_available():
            return False
        
        try:
            cmd = [self.ffmpeg_path, '-y', '-i', input_path]
            
            # Add format-specific options
            if output_format == 'mp3':
                cmd.extend(['-vn', '-acodec', 'libmp3lame'])
                if bitrate:
                    cmd.extend(['-b:a', bitrate])
            elif output_format == 'm4a':
                cmd.extend(['-vn', '-acodec', 'aac'])
                if bitrate:
                    cmd.extend(['-b:a', bitrate])
            elif output_format == 'mp4':
                cmd.extend(['-c:v', 'libx264', '-c:a', 'aac'])
            
            cmd.append(output_path)
            
            result = subprocess.run(cmd, capture_output=True, timeout=600)
            return result.returncode == 0
        except:
            return False
    
    def print_header(self, title: str):
        """Print styled header"""
        width = shutil.get_terminal_size().columns - 10
        print(f"\n{'═' * width}")
        print(f"  {title.center(width - 4)}")
        print(f"{'═' * width}\n")
    
    def print_status(self, message: str, status: str = 'info'):
        """Print status message"""
        colors = {
            'info': '\033[92m',      # Green
            'warning': '\033[93m',   # Yellow
            'error': '\033[91m',     # Red
            'progress': '\033[96m',  # Cyan
        }
        reset = '\033[0m'
        color = colors.get(status, colors['info'])
        
        icons = {
            'info': '✓',
            'warning': '⚠',
            'error': '✗',
            'progress': '→',
        }
        icon = icons.get(status, '•')
        
        print(f"{color}[{icon}] {message}{reset}")
    
    @abstractmethod
    def run(self):
        """Run the module - must be implemented by subclass"""
        pass
    
    def get_module_info(self) -> Dict:
        """Get module information"""
        return {
            'name': self.name,
            'output_dir': self.output_dir,
            'ffmpeg_available': self.is_ffmpeg_available(),
        }

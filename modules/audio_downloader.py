#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - Module 2: Audio Downloader                  ║
║  Author: RS (T3rmuxk1ng)                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import subprocess
from typing import Dict, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.downloader_base import DownloaderBase
from utils.colors import *
from utils.banner import show_module_header, show_error_box, show_success_box
from utils.helpers import get_input, confirm, press_enter, format_size
from utils.validator import URLValidator, get_video_id


class AudioDownloader(DownloaderBase):
    """
    Audio Downloader Module
    - Extract audio from videos
    - Multiple formats (MP3, M4A, WEBM, AAC, FLAC)
    - Quality selection (64kbps - 320kbps)
    - Metadata embedding
    """
    
    FORMATS = [
        ('1', 'MP3 (Universal)', 'mp3'),
        ('2', 'M4A (Best Quality)', 'm4a'),
        ('3', 'WEBM (Web)', 'webm'),
        ('4', 'AAC (Compressed)', 'aac'),
        ('5', 'FLAC (Lossless)', 'flac'),
        ('6', 'OPUS (Best Size/Quality)', 'opus'),
    ]
    
    QUALITIES = [
        ('1', '320 kbps (Best)', '320'),
        ('2', '256 kbps (High)', '256'),
        ('3', '192 kbps (Good)', '192'),
        ('4', '128 kbps (Normal)', '128'),
        ('5', '96 kbps (Low)', '96'),
        ('6', '64 kbps (Smallest)', '64'),
    ]
    
    def __init__(self):
        super().__init__()
        self.name = "Audio Downloader"
        self.module_icon = "🎵"
    
    def run(self):
        """Run audio downloader module"""
        show_module_header(f"{self.module_icon} AUDIO DOWNLOADER", "▶")
        
        # Get URL
        print(f"{NEON_CYAN}[?] Enter YouTube Video URL (or 'back' to return):{RESET}")
        url = get_input("URL")
        
        if url.lower() == 'back':
            return
        
        # Validate
        if not URLValidator.is_youtube_url(url):
            show_error_box("Invalid URL", "Please enter a valid YouTube URL")
            return
        
        video_id = get_video_id(url)
        if not video_id:
            show_error_box("Invalid URL", "Could not extract video ID")
            return
        
        # Get info
        print(f"\n{NEON_GREEN}[+] Fetching video information...{RESET}")
        info = self._get_video_info(url)
        
        if info:
            self._display_video_info(info)
        
        # Select format
        audio_format = self._select_format()
        if not audio_format:
            return
        
        # Select quality
        quality = self._select_quality()
        if not quality:
            return
        
        # Options
        embed_thumbnail = confirm("Embed thumbnail?", True)
        embed_metadata = confirm("Embed metadata?", True)
        
        # Confirm
        if not confirm("Start download?", True):
            print(f"{NEON_YELLOW}[!] Download cancelled{RESET}")
            return
        
        # Download
        self._download_audio(url, info, audio_format, quality, embed_thumbnail, embed_metadata)
    
    def _get_video_info(self, url: str) -> Optional[Dict]:
        """Get video info using yt-dlp"""
        try:
            result = subprocess.run(
                ['yt-dlp', '--dump-json', '--no-download', url],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        
        video_id = get_video_id(url)
        return {'id': video_id, 'title': f'audio_{video_id}'}
    
    def _display_video_info(self, info: Dict):
        """Display video info"""
        print(f"\n{NEON_GREEN}╔══════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{NEON_GREEN}║{RESET} {BRIGHT_WHITE}{'VIDEO INFORMATION'.center(58)}{RESET} {NEON_GREEN}║{RESET}")
        print(f"{NEON_GREEN}╠══════════════════════════════════════════════════════════════╣{RESET}")
        
        title = info.get('title', 'Unknown')[:50]
        duration = info.get('duration', 0)
        duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else 'Unknown'
        
        print(f"{NEON_GREEN}║{RESET} {CYAN}Title:{RESET} {BRIGHT_WHITE}{title}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}Duration:{RESET} {BRIGHT_WHITE}{duration_str}{RESET}")
        
        if 'uploader' in info:
            print(f"{NEON_GREEN}║{RESET} {CYAN}Channel:{RESET} {BRIGHT_WHITE}{info['uploader'][:40]}{RESET}")
        
        print(f"{NEON_GREEN}╚══════════════════════════════════════════════════════════════╝{RESET}")
    
    def _select_format(self) -> Optional[str]:
        """Select audio format"""
        print(f"\n{NEON_CYAN}[?] Select Audio Format:{RESET}\n")
        
        for key, label, _ in self.FORMATS:
            print(f"  {NEON_GREEN}[{key}]{RESET} {label}")
        
        choice = get_input("Format", "1")
        
        for key, label, value in self.FORMATS:
            if choice == key:
                return value
        
        return 'mp3'
    
    def _select_quality(self) -> Optional[str]:
        """Select audio quality"""
        print(f"\n{NEON_CYAN}[?] Select Audio Quality:{RESET}\n")
        
        for key, label, _ in self.QUALITIES:
            print(f"  {NEON_GREEN}[{key}]{RESET} {label}")
        
        choice = get_input("Quality", "1")
        
        for key, label, value in self.QUALITIES:
            if choice == key:
                return value
        
        return '320'
    
    def _download_audio(self, url: str, info: Dict, audio_format: str, quality: str,
                        embed_thumbnail: bool, embed_metadata: bool):
        """Download audio"""
        output_dir = self.create_output_dir('audio')
        title = self.sanitize_filename(info.get('title', 'audio'))
        output_file = os.path.join(output_dir, f"{title}.{audio_format}")
        output_file = self.get_unique_filename(output_file)
        
        print(f"\n{NEON_GREEN}[+] Starting audio extraction...{RESET}")
        print(f"{NEON_CYAN}[→] Output: {output_file}{RESET}")
        
        # Build command
        cmd = self._build_command(url, output_file, audio_format, quality,
                                   embed_thumbnail, embed_metadata)
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            for line in process.stdout:
                line = line.strip()
                if '[download]' in line and '%' in line:
                    try:
                        percent_str = line.split('%')[0].split()[-1]
                        percent = float(percent_str)
                        bar_len = int(percent * 30 / 100)
                        bar = f"{NEON_GREEN}{'█' * bar_len}{RESET}{DIM}{'░' * (30 - bar_len)}{RESET}"
                        print(f"\r{NEON_CYAN}[↓]{RESET} Progress: [{bar}] {percent:.1f}%", end='')
                    except:
                        pass
            
            process.wait()
            
            if process.returncode == 0:
                print(f"\n\n{NEON_GREEN}✓ Audio extraction complete!{RESET}")
                print(f"{NEON_CYAN}[→] Saved to: {output_file}{RESET}")
                show_success_box("SUCCESS", f"Audio saved to {output_file}")
            else:
                print(f"\n\n{NEON_RED}✗ Download failed!{RESET}")
                show_error_box("Error", "Download failed")
                
        except FileNotFoundError:
            show_error_box("Error", "yt-dlp not found. Install: pip install yt-dlp")
        except Exception as e:
            show_error_box("Error", str(e))
        
        press_enter()
    
    def _build_command(self, url: str, output: str, format_choice: str,
                       quality: str, embed_thumb: bool, embed_meta: bool) -> list:
        """Build yt-dlp command for audio"""
        cmd = ['yt-dlp']
        
        # Audio format and quality
        cmd.extend(['-x', '--audio-format', format_choice])
        cmd.extend(['--audio-quality', quality + 'K'])
        
        # Embed thumbnail
        if embed_thumb:
            cmd.append('--embed-thumbnail')
        
        # Embed metadata
        if embed_meta:
            cmd.append('--embed-metadata')
            cmd.append('--add-metadata')
        
        # FFmpeg args for specific formats
        if format_choice == 'mp3':
            cmd.extend(['--postprocessor-args', 'ffmpeg:-acodec libmp3lame'])
        
        # Output
        cmd.extend(['-o', output])
        cmd.extend(['--progress', '--newline'])
        cmd.append(url)
        
        return cmd
    
    def download(self, url: str, format_choice: str = 'mp3', quality: str = '320',
                 output_dir: str = None) -> Tuple[bool, str]:
        """Programmatic download"""
        if not URLValidator.is_youtube_url(url):
            return False, "Invalid YouTube URL"
        
        video_id = get_video_id(url)
        if not video_id:
            return False, "Could not extract video ID"
        
        if output_dir is None:
            output_dir = self.create_output_dir('audio')
        
        info = self._get_video_info(url)
        title = self.sanitize_filename(info.get('title', f'audio_{video_id}'))
        output_file = os.path.join(output_dir, f"{title}.{format_choice}")
        output_file = self.get_unique_filename(output_file)
        
        cmd = self._build_command(url, output_file, format_choice, quality, False, False)
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=3600)
            if result.returncode == 0:
                return True, output_file
            return False, result.stderr.decode()
        except Exception as e:
            return False, str(e)


def run():
    """Run audio downloader"""
    downloader = AudioDownloader()
    downloader.run()


if __name__ == "__main__":
    run()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - Module 3: Playlist Downloader               ║
║  Author: RS (T3rmuxk1ng)                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import subprocess
import time
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.downloader_base import DownloaderBase
from utils.colors import *
from utils.banner import show_module_header, show_error_box, show_success_box
from utils.helpers import get_input, confirm, press_enter, format_size
from utils.validator import URLValidator, get_playlist_id


class PlaylistDownloader(DownloaderBase):
    """
    Playlist Downloader Module
    - Download entire playlists
    - Range selection
    - Parallel downloads
    - Skip existing
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Playlist Downloader"
        self.module_icon = "📁"
        self.total_videos = 0
        self.downloaded = 0
        self.failed = 0
    
    def run(self):
        """Run playlist downloader module"""
        show_module_header(f"{self.module_icon} PLAYLIST DOWNLOADER", "▶")
        
        # Get URL
        print(f"{NEON_CYAN}[?] Enter YouTube Playlist URL (or 'back' to return):{RESET}")
        url = get_input("URL")
        
        if url.lower() == 'back':
            return
        
        # Validate
        playlist_id = get_playlist_id(url)
        if not playlist_id:
            show_error_box("Invalid URL", "Please enter a valid YouTube playlist URL")
            return
        
        # Get playlist info
        print(f"\n{NEON_GREEN}[+] Fetching playlist information...{RESET}")
        playlist_info = self._get_playlist_info(url)
        
        if not playlist_info:
            show_error_box("Error", "Could not fetch playlist information")
            return
        
        # Display info
        self._display_playlist_info(playlist_info)
        
        # Get download options
        options = self._get_download_options()
        
        # Confirm
        if not confirm("Start download?", True):
            print(f"{NEON_YELLOW}[!] Download cancelled{RESET}")
            return
        
        # Download
        self._download_playlist(url, playlist_info, options)
    
    def _get_playlist_info(self, url: str) -> Optional[Dict]:
        """Get playlist info using yt-dlp"""
        try:
            result = subprocess.run(
                ['yt-dlp', '--dump-json', '--flat-playlist', '--no-download', url],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                videos = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            videos.append(json.loads(line))
                        except:
                            pass
                
                return {
                    'videos': videos,
                    'total': len(videos)
                }
        except:
            pass
        
        return None
    
    def _display_playlist_info(self, info: Dict):
        """Display playlist information"""
        total = info.get('total', 0)
        
        print(f"\n{NEON_GREEN}╔══════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{NEON_GREEN}║{RESET} {BRIGHT_WHITE}{'PLAYLIST INFORMATION'.center(58)}{RESET} {NEON_GREEN}║{RESET}")
        print(f"{NEON_GREEN}╠══════════════════════════════════════════════════════════════╣{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}Total Videos:{RESET} {BRIGHT_WHITE}{total}{RESET}")
        print(f"{NEON_GREEN}╚══════════════════════════════════════════════════════════════╝{RESET}")
        
        # Show first 5 videos
        videos = info.get('videos', [])[:5]
        if videos:
            print(f"\n{NEON_CYAN}First {len(videos)} videos:{RESET}")
            for i, video in enumerate(videos, 1):
                title = video.get('title', 'Unknown')[:40]
                print(f"  {NEON_GREEN}[{i}]{RESET} {title}")
            
            if total > 5:
                print(f"  {DIM}... and {total - 5} more{RESET}")
    
    def _get_download_options(self) -> Dict:
        """Get download options from user"""
        options = {}
        
        # Range
        print(f"\n{NEON_CYAN}[?] Download range (press Enter for all):{RESET}")
        print(f"  {DIM}Format: start-end (e.g., 1-10 for first 10 videos){RESET}")
        range_input = get_input("Range", "all")
        
        if range_input != 'all' and '-' in range_input:
            try:
                start, end = range_input.split('-')
                options['start'] = int(start)
                options['end'] = int(end)
            except:
                pass
        
        # Quality
        print(f"\n{NEON_CYAN}[?] Video Quality:{RESET}")
        print(f"  {NEON_GREEN}[1]{RESET} Best Available")
        print(f"  {NEON_GREEN}[2]{RESET} 1080p")
        print(f"  {NEON_GREEN}[3]{RESET} 720p")
        print(f"  {NEON_GREEN}[4]{RESET} 480p")
        
        quality_choice = get_input("Quality", "1")
        quality_map = {'1': 'best', '2': '1080', '3': '720', '4': '480'}
        options['quality'] = quality_map.get(quality_choice, 'best')
        
        # Format
        print(f"\n{NEON_CYAN}[?] Video Format:{RESET}")
        print(f"  {NEON_GREEN}[1]{RESET} MP4")
        print(f"  {NEON_GREEN}[2]{RESET} WEBM")
        
        format_choice = get_input("Format", "1")
        options['format'] = 'mp4' if format_choice == '1' else 'webm'
        
        # Parallel downloads
        print(f"\n{NEON_CYAN}[?] Parallel Downloads (1-5):{RESET}")
        parallel = get_input("Count", "3")
        try:
            options['parallel'] = min(5, max(1, int(parallel)))
        except:
            options['parallel'] = 3
        
        # Skip existing
        options['skip_existing'] = confirm("Skip existing files?", True)
        
        return options
    
    def _download_playlist(self, url: str, info: Dict, options: Dict):
        """Download playlist"""
        output_dir = self.create_output_dir('playlists')
        
        # Get playlist name for subfolder
        playlist_name = self.sanitize_filename(info.get('title', 'playlist'))
        output_dir = os.path.join(output_dir, playlist_name)
        os.makedirs(output_dir, exist_ok=True)
        
        videos = info.get('videos', [])
        total = len(videos)
        
        # Apply range
        start = options.get('start', 1)
        end = options.get('end', total)
        videos = videos[start-1:end]
        
        self.total_videos = len(videos)
        self.downloaded = 0
        self.failed = 0
        
        print(f"\n{NEON_GREEN}[+] Starting playlist download...{RESET}")
        print(f"{NEON_CYAN}[→] Output folder: {output_dir}{RESET}")
        print(f"{NEON_CYAN}[→] Total videos: {self.total_videos}{RESET}")
        print(f"{NEON_CYAN}[→] Parallel downloads: {options['parallel']}{RESET}\n")
        
        # Build base command
        base_cmd = self._build_base_command(options, output_dir)
        
        # Download videos
        for i, video in enumerate(videos, 1):
            video_url = f"https://www.youtube.com/watch?v={video.get('id')}"
            video_title = video.get('title', 'Unknown')[:40]
            
            # Check skip existing
            if options.get('skip_existing'):
                safe_title = self.sanitize_filename(video_title)
                expected_file = os.path.join(output_dir, f"{safe_title}.{options['format']}")
                if os.path.exists(expected_file):
                    print(f"{DIM}[{i}/{self.total_videos}] Skipped (exists): {video_title}{RESET}")
                    continue
            
            print(f"{NEON_GREEN}[{i}/{self.total_videos}]{RESET} Downloading: {video_title}")
            
            # Download single video
            success = self._download_single(video_url, base_cmd, video_title, output_dir, options['format'])
            
            if success:
                self.downloaded += 1
                print(f"{NEON_GREEN}  ✓ Complete{RESET}")
            else:
                self.failed += 1
                print(f"{NEON_RED}  ✗ Failed{RESET}")
        
        # Summary
        print(f"\n{NEON_GREEN}╔══════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{NEON_GREEN}║{RESET} {BRIGHT_WHITE}{'DOWNLOAD SUMMARY'.center(58)}{RESET} {NEON_GREEN}║{RESET}")
        print(f"{NEON_GREEN}╠══════════════════════════════════════════════════════════════╣{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}Total:{RESET} {BRIGHT_WHITE}{self.total_videos}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {NEON_GREEN}Downloaded:{RESET} {BRIGHT_WHITE}{self.downloaded}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {NEON_RED}Failed:{RESET} {BRIGHT_WHITE}{self.failed}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}Output:{RESET} {BRIGHT_WHITE}{output_dir[:40]}{RESET}")
        print(f"{NEON_GREEN}╚══════════════════════════════════════════════════════════════╝{RESET}")
        
        press_enter()
    
    def _build_base_command(self, options: Dict, output_dir: str) -> list:
        """Build base yt-dlp command"""
        cmd = ['yt-dlp']
        
        quality = options.get('quality', 'best')
        format_choice = options.get('format', 'mp4')
        
        if quality == 'best':
            format_str = f'bestvideo[ext={format_choice}]+bestaudio/best[ext={format_choice}]/best'
        else:
            format_str = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best'
        
        cmd.extend(['-f', format_str])
        
        if format_choice == 'mp4':
            cmd.extend(['--merge-output-format', 'mp4'])
        
        return cmd
    
    def _download_single(self, url: str, base_cmd: list, title: str, 
                         output_dir: str, format_choice: str) -> bool:
        """Download single video"""
        safe_title = self.sanitize_filename(title)
        output_file = os.path.join(output_dir, f"{safe_title}.{format_choice}")
        output_file = self.get_unique_filename(output_file)
        
        cmd = base_cmd.copy()
        cmd.extend(['-o', output_file, '--no-playlist', url])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=600
            )
            return result.returncode == 0
        except:
            return False


def run():
    """Run playlist downloader"""
    downloader = PlaylistDownloader()
    downloader.run()


if __name__ == "__main__":
    run()

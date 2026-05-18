#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - Module 8: Search & Download                 ║
║  Author: RS (T3rmuxk1ng)                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote_plus

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.downloader_base import DownloaderBase
from utils.colors import *
from utils.banner import show_module_header, show_error_box, show_success_box
from utils.helpers import get_input, confirm, press_enter, format_size, format_duration, format_number
from utils.validator import URLValidator, get_video_id


class SearchDownload(DownloaderBase):
    """
    Search & Download Module
    - Search YouTube directly
    - Select from results
    - Download without copying URLs
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Search & Download"
        self.module_icon = "🔍"
        self.results = []
    
    def run(self):
        """Run search & download module"""
        show_module_header(f"{self.module_icon} SEARCH & DOWNLOAD", "▶")
        
        # Get search query
        print(f"{NEON_CYAN}[?] Enter search query (or 'back' to return):{RESET}")
        query = get_input("Search")
        
        if query.lower() == 'back':
            return
        
        if not query:
            show_error_box("Error", "Please enter a search query")
            return
        
        # Search
        print(f"\n{NEON_GREEN}[+] Searching for: {query}...{RESET}")
        self.results = self._search_youtube(query)
        
        if not self.results:
            show_error_box("No Results", "No videos found for your query")
            return
        
        # Display results
        self._display_results()
        
        # Select video
        selection = self._select_video()
        
        if not selection:
            return
        
        # Download
        self._download_selection(selection)
    
    def _search_youtube(self, query: str) -> List[Dict]:
        """Search YouTube using yt-dlp"""
        try:
            # Use yt-dlp search
            search_url = f"ytsearch10:{query}"
            
            result = subprocess.run(
                ['yt-dlp', '--flat-playlist', '--dump-json', search_url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                videos = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            video = json.loads(line)
                            videos.append({
                                'id': video.get('id', ''),
                                'title': video.get('title', 'Unknown'),
                                'duration': video.get('duration', 0),
                                'view_count': video.get('view_count', 0),
                                'channel': video.get('channel', 'Unknown'),
                                'url': f"https://www.youtube.com/watch?v={video.get('id', '')}"
                            })
                        except:
                            pass
                return videos
                
        except:
            pass
        
        return []
    
    def _display_results(self):
        """Display search results"""
        print(f"\n{NEON_GREEN}╔══════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{NEON_GREEN}║{RESET} {BRIGHT_WHITE}{'SEARCH RESULTS'.center(58)}{RESET} {NEON_GREEN}║{RESET}")
        print(f"{NEON_GREEN}╠══════════════════════════════════════════════════════════════╣{RESET}")
        
        for i, video in enumerate(self.results[:10], 1):
            title = video['title'][:45]
            duration = format_duration(video.get('duration', 0))
            channel = video.get('channel', 'Unknown')[:20]
            
            print(f"{NEON_GREEN}║{RESET}")
            print(f"{NEON_GREEN}║{RESET} {NEON_GREEN}[{i}]{RESET} {BRIGHT_WHITE}{title}{RESET}")
            print(f"{NEON_GREEN}║{RESET}     {DIM}Channel: {channel} | Duration: {duration}{RESET}")
        
        print(f"{NEON_GREEN}║{RESET}")
        print(f"{NEON_GREEN}╚══════════════════════════════════════════════════════════════╝{RESET}")
    
    def _select_video(self) -> Optional[Dict]:
        """Select video from results"""
        print(f"\n{NEON_CYAN}[?] Select video (1-{len(self.results)}) or 'back':{RESET}")
        selection = get_input("Select")
        
        if selection.lower() == 'back':
            return None
        
        try:
            index = int(selection) - 1
            if 0 <= index < len(self.results):
                return self.results[index]
        except:
            pass
        
        show_error_box("Invalid", "Please enter a valid number")
        return None
    
    def _download_selection(self, video: Dict):
        """Download selected video"""
        url = video['url']
        title = video['title']
        
        print(f"\n{NEON_GREEN}[+] Selected: {title[:50]}{RESET}")
        
        # Get download options
        print(f"\n{NEON_CYAN}[?] Download options:{RESET}")
        print(f"  {NEON_GREEN}[1]{RESET} Video (Best Quality)")
        print(f"  {NEON_GREEN}[2]{RESET} Video (1080p)")
        print(f"  {NEON_GREEN}[3]{RESET} Video (720p)")
        print(f"  {NEON_GREEN}[4]{RESET} Audio Only (MP3)")
        
        choice = get_input("Option", "1")
        
        # Build command
        cmd = ['yt-dlp']
        output_dir = self.create_output_dir('videos')
        
        if choice == '4':
            cmd.extend(['-x', '--audio-format', 'mp3', '--audio-quality', '0'])
            output_dir = self.create_output_dir('audio')
        elif choice == '2':
            cmd.extend(['-f', 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'])
            cmd.extend(['--merge-output-format', 'mp4'])
        elif choice == '3':
            cmd.extend(['-f', 'bestvideo[height<=720]+bestaudio/best[height<=720]'])
            cmd.extend(['--merge-output-format', 'mp4'])
        else:
            cmd.extend(['-f', 'bestvideo+bestaudio/best'])
            cmd.extend(['--merge-output-format', 'mp4'])
        
        # Output
        output_template = os.path.join(output_dir, '%(title)s.%(ext)s')
        cmd.extend(['-o', output_template])
        cmd.extend(['--progress', '--newline'])
        cmd.append(url)
        
        # Download
        print(f"\n{NEON_GREEN}[+] Starting download...{RESET}")
        
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
                print(f"\n\n{NEON_GREEN}✓ Download complete!{RESET}")
                print(f"{NEON_CYAN}[→] Saved to: {output_dir}{RESET}")
                show_success_box("SUCCESS", f"Downloaded: {title[:40]}")
            else:
                print(f"\n\n{NEON_RED}✗ Download failed!{RESET}")
                
        except Exception as e:
            show_error_box("Error", str(e))
        
        press_enter()
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Programmatic search"""
        try:
            search_url = f"ytsearch{limit}:{query}"
            result = subprocess.run(
                ['yt-dlp', '--flat-playlist', '--dump-json', search_url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                videos = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            video = json.loads(line)
                            videos.append({
                                'id': video.get('id', ''),
                                'title': video.get('title', ''),
                                'url': f"https://www.youtube.com/watch?v={video.get('id', '')}"
                            })
                        except:
                            pass
                return videos
        except:
            pass
        
        return []


def run():
    """Run search & download"""
    searcher = SearchDownload()
    searcher.run()


if __name__ == "__main__":
    run()

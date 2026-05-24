#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - Module 1: Video Downloader                  ║
║  Author: RS (T3rmuxk1ng)                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import json
import subprocess
from typing import Dict, List, Optional, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.downloader_base import DownloaderBase
from utils.colors import *
from utils.banner import show_module_header, show_error_box, show_success_box
from utils.helpers import get_input, confirm, select_option, press_enter, format_size
from utils.progress import DownloadProgress
from utils.validator import URLValidator, get_video_id


class VideoDownloader(DownloaderBase):
    """
    Video Downloader Module
    - Download videos in any quality (4K, 1080p, 720p, etc.)
    - Multiple format support (MP4, WEBM, MKV)
    - FFmpeg integration for merging
    - Progress tracking
    """

    QUALITIES = [
        ('1', '4K (2160p)', '2160p'),
        ('2', '2K (1440p)', '1440p'),
        ('3', 'Full HD (1080p)', '1080p'),
        ('4', 'HD (720p)', '720p'),
        ('5', 'SD (480p)', '480p'),
        ('6', 'Low (360p)', '360p'),
        ('7', 'Very Low (240p)', '240p'),
        ('8', 'Best Available', 'best'),
    ]

    FORMATS = [
        ('1', 'MP4 (Recommended)', 'mp4'),
        ('2', 'WEBM', 'webm'),
        ('3', 'MKV', 'mkv'),
    ]

    def __init__(self):
        super().__init__()
        self.name = "Video Downloader"
        self.module_icon = "🎬"

    def run(self):
        """Run video downloader module"""
        show_module_header(f"{self.module_icon} VIDEO DOWNLOADER", "▶")

        # Get URL from user
        print(f"{NEON_CYAN}[?] Enter YouTube Video URL (or 'back' to return):{RESET}")
        url = get_input("URL")

        if url.lower() == 'back':
            return

        # Validate URL
        if not URLValidator.is_youtube_url(url):
            show_error_box("Invalid URL", "Please enter a valid YouTube URL")
            return

        video_id = get_video_id(url)
        if not video_id:
            show_error_box("Invalid URL", "Could not extract video ID")
            return

        # Get video info
        print(f"\n{NEON_GREEN}[+] Fetching video information...{RESET}")
        video_info = self._get_video_info(url)

        if not video_info:
            show_error_box("Error", "Could not fetch video information")
            return

        # Display video info
        self._display_video_info(video_info)

        # Select quality
        quality = self._select_quality()
        if not quality:
            return

        # Select format
        format_choice = self._select_format()
        if not format_choice:
            return

        # Confirm download
        if not confirm("Start download?", True):
            print(f"{NEON_YELLOW}[!] Download cancelled{RESET}")
            return

        # Download
        self._download_video(url, video_info, quality, format_choice)

    def _get_video_info(self, url: str) -> Optional[Dict]:
        """Get video information using yt-dlp"""
        try:
            # Try using yt-dlp if available
            result = subprocess.run(
                ['yt-dlp', '--dump-json', '--no-download', url],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception:
            pass

        # Fallback: Extract basic info from URL
        video_id = get_video_id(url)
        return {
            'id': video_id,
            'title': f'video_{video_id}',
            'url': url,
        }

    def _display_video_info(self, info: Dict):
        """Display video information"""
        print(f"\n{NEON_GREEN}╔══════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{NEON_GREEN}║{RESET} {BRIGHT_WHITE}{'VIDEO INFORMATION'.center(58)}{RESET} {NEON_GREEN}║{RESET}")
        print(f"{NEON_GREEN}╠══════════════════════════════════════════════════════════════╣{RESET}")

        title = info.get('title', 'Unknown')[:50]
        duration = info.get('duration', 0)
        duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else 'Unknown'

        print(f"{NEON_GREEN}║{RESET} {CYAN}Title:{RESET} {BRIGHT_WHITE}{title}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}Duration:{RESET} {BRIGHT_WHITE}{duration_str}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}Video ID:{RESET} {BRIGHT_WHITE}{info.get('id', 'Unknown')}{RESET}")

        if 'view_count' in info:
            views = info['view_count']
            print(f"{NEON_GREEN}║{RESET} {CYAN}Views:{RESET} {BRIGHT_WHITE}{views:,}{RESET}")

        if 'uploader' in info:
            print(f"{NEON_GREEN}║{RESET} {CYAN}Channel:{RESET} {BRIGHT_WHITE}{info['uploader'][:40]}{RESET}")

        print(f"{NEON_GREEN}╚══════════════════════════════════════════════════════════════╝{RESET}")

    def _select_quality(self) -> Optional[str]:
        """Select video quality"""
        print(f"\n{NEON_CYAN}[?] Select Video Quality:{RESET}\n")

        for key, label, _ in self.QUALITIES:
            print(f"  {NEON_GREEN}[{key}]{RESET} {label}")

        choice = get_input("Quality", "3")  # Default to 1080p

        for key, label, value in self.QUALITIES:
            if choice == key:
                return value

        # If invalid, return best
        return 'best'

    def _select_format(self) -> Optional[str]:
        """Select video format"""
        print(f"\n{NEON_CYAN}[?] Select Video Format:{RESET}\n")

        for key, label, _ in self.FORMATS:
            print(f"  {NEON_GREEN}[{key}]{RESET} {label}")

        choice = get_input("Format", "1")  # Default to MP4

        for key, label, value in self.FORMATS:
            if choice == key:
                return value

        return 'mp4'

    def _download_video(self, url: str, info: Dict, quality: str, format_choice: str):
        """Download the video"""
        output_dir = self.create_output_dir('videos')
        title = self.sanitize_filename(info.get('title', 'video'))
        output_file = os.path.join(output_dir, f"{title}.{format_choice}")

        # Check for existing file
        output_file = self.get_unique_filename(output_file)

        print(f"\n{NEON_GREEN}[+] Starting download...{RESET}")
        print(f"{NEON_CYAN}[→] Output: {output_file}{RESET}")

        # Build yt-dlp command
        cmd = self._build_ytdlp_command(url, output_file, quality, format_choice)

        # Execute download
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            # Monitor progress
            for line in process.stdout:
                line = line.strip()
                if '[download]' in line and '%' in line:
                    # Extract percentage
                    try:
                        percent_str = line.split('%')[0].split()[-1]
                        percent = float(percent_str)
                        bar_len = int(percent * 30 / 100)
                        bar = f"{NEON_GREEN}{'█' * bar_len}{RESET}{DIM}{'░' * (30 - bar_len)}{RESET}"
                        print(f"\r{NEON_CYAN}[↓]{RESET} Progress: [{bar}] {percent:.1f}%", end='')
                    except Exception:
                        pass

            process.wait()

            if process.returncode == 0:
                print(f"\n\n{NEON_GREEN}✓ Download complete!{RESET}")
                print(f"{NEON_CYAN}[→] Saved to: {output_file}{RESET}")
                show_success_box("SUCCESS", f"Video saved to {output_file}")
            else:
                print(f"\n\n{NEON_RED}✗ Download failed!{RESET}")
                show_error_box("Error", "Download failed. Check the URL and try again.")

        except FileNotFoundError:
            show_error_box("Error", "yt-dlp not found. Please install it first.\nRun: pip install yt-dlp")
        except Exception as e:
            show_error_box("Error", str(e))

        press_enter()

    def _build_ytdlp_command(self, url: str, output: str, quality: str, format_choice: str) -> list:
        """Build yt-dlp command with options"""
        cmd = ['yt-dlp']

        # Format selection
        if quality == 'best':
            format_str = f'bestvideo[ext={format_choice}]+bestaudio/best[ext={format_choice}]/best'
        else:
            height = quality.replace('p', '')
            format_str = f'bestvideo[height<={height}][ext={format_choice}]+bestaudio/best[height<={height}]/best'

        cmd.extend(['-f', format_str])

        # Merge format
        if format_choice == 'mp4':
            cmd.extend(['--merge-output-format', 'mp4'])

        # Output
        cmd.extend(['-o', output])

        # Progress
        cmd.extend(['--progress', '--newline'])

        # Add URL
        cmd.append(url)

        return cmd

    def download(self, url: str, quality: str = 'best', format_choice: str = 'mp4',
                 output_dir: str = None) -> Tuple[bool, str]:
        """
        Programmatic download method

        Returns:
            Tuple of (success, output_path or error_message)
        """
        if not URLValidator.is_youtube_url(url):
            return False, "Invalid YouTube URL"

        video_id = get_video_id(url)
        if not video_id:
            return False, "Could not extract video ID"

        # Set output directory
        if output_dir is None:
            output_dir = self.create_output_dir('videos')

        # Get video info for filename
        info = self._get_video_info(url)
        title = self.sanitize_filename(info.get('title', f'video_{video_id}'))
        output_file = os.path.join(output_dir, f"{title}.{format_choice}")
        output_file = self.get_unique_filename(output_file)

        # Build and execute command
        cmd = self._build_ytdlp_command(url, output_file, quality, format_choice)

        try:
            result = subprocess.run(cmd, capture_output=True, timeout=3600)

            if result.returncode == 0:
                return True, output_file
            else:
                return False, result.stderr.decode()

        except Exception as e:
            return False, str(e)


# Module entry point
def run():
    """Run the video downloader module"""
    downloader = VideoDownloader()
    downloader.run()


if __name__ == "__main__":
    run()

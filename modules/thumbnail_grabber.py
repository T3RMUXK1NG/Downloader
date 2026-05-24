#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - Module 4: Thumbnail Grabber                 ║
║  Author: RS (T3rmuxk1ng)                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import subprocess
import urllib.request
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.downloader_base import DownloaderBase
from utils.colors import *
from utils.banner import show_module_header, show_error_box, show_success_box
from utils.helpers import get_input, confirm, press_enter, format_size
from utils.validator import URLValidator, get_video_id


class ThumbnailGrabber(DownloaderBase):
    """
    Thumbnail Grabber Module
    - Download video thumbnails
    - Multiple quality options
    - JPG/PNG/WEBP formats
    - Bulk thumbnail download
    """

    QUALITIES = [
        ('1', 'Maximum Resolution (Recommended)', 'maxres'),
        ('2', 'High Quality', 'hq'),
        ('3', 'Medium Quality', 'mq'),
        ('4', 'Standard', 'sd'),
        ('5', 'Default', 'default'),
        ('6', 'All Available', 'all'),
    ]

    FORMATS = [
        ('1', 'JPG', 'jpg'),
        ('2', 'PNG', 'png'),
        ('3', 'WEBP', 'webp'),
    ]

    THUMBNAIL_URLS = {
        'maxres': 'https://img.youtube.com/vi/{id}/maxresdefault.jpg',
        'hq': 'https://img.youtube.com/vi/{id}/hqdefault.jpg',
        'mq': 'https://img.youtube.com/vi/{id}/mqdefault.jpg',
        'sd': 'https://img.youtube.com/vi/{id}/sddefault.jpg',
        'default': 'https://img.youtube.com/vi/{id}/default.jpg',
    }

    def __init__(self):
        super().__init__()
        self.name = "Thumbnail Grabber"
        self.module_icon = "🖼️"

    def run(self):
        """Run thumbnail grabber module"""
        show_module_header(f"{self.module_icon} THUMBNAIL GRABBER", "▶")

        # Get URL
        print(f"{NEON_CYAN}[?] Enter YouTube Video URL (or 'back' to return):{RESET}")
        url = get_input("URL")

        if url.lower() == 'back':
            return

        # Validate
        video_id = get_video_id(url)
        if not video_id:
            show_error_box("Invalid URL", "Please enter a valid YouTube URL")
            return

        # Get video info for filename
        print(f"\n{NEON_GREEN}[+] Fetching video information...{RESET}")
        info = self._get_video_info(url)

        if info:
            self._display_video_info(info)

        # Select quality
        quality = self._select_quality()
        if not quality:
            return

        # Select format
        format_choice = self._select_format()
        if not format_choice:
            return

        # Download
        self._download_thumbnails(video_id, info, quality, format_choice)

    def _get_video_info(self, url: str) -> Optional[Dict]:
        """Get video info"""
        try:
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

        video_id = get_video_id(url)
        return {'id': video_id, 'title': f'video_{video_id}'}

    def _display_video_info(self, info: Dict):
        """Display video info"""
        print(f"\n{NEON_GREEN}╔══════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{NEON_GREEN}║{RESET} {BRIGHT_WHITE}{'VIDEO INFORMATION'.center(58)}{RESET} {NEON_GREEN}║{RESET}")
        print(f"{NEON_GREEN}╠══════════════════════════════════════════════════════════════╣{RESET}")

        title = info.get('title', 'Unknown')[:50]
        print(f"{NEON_GREEN}║{RESET} {CYAN}Title:{RESET} {BRIGHT_WHITE}{title}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}Video ID:{RESET} {BRIGHT_WHITE}{info.get('id', 'Unknown')}{RESET}")

        if 'uploader' in info:
            print(f"{NEON_GREEN}║{RESET} {CYAN}Channel:{RESET} {BRIGHT_WHITE}{info['uploader'][:40]}{RESET}")

        print(f"{NEON_GREEN}╚══════════════════════════════════════════════════════════════╝{RESET}")

    def _select_quality(self) -> Optional[str]:
        """Select thumbnail quality"""
        print(f"\n{NEON_CYAN}[?] Select Thumbnail Quality:{RESET}\n")

        for key, label, _ in self.QUALITIES:
            print(f"  {NEON_GREEN}[{key}]{RESET} {label}")

        choice = get_input("Quality", "1")

        for key, label, value in self.QUALITIES:
            if choice == key:
                return value

        return 'maxres'

    def _select_format(self) -> Optional[str]:
        """Select output format"""
        print(f"\n{NEON_CYAN}[?] Select Output Format:{RESET}\n")

        for key, label, _ in self.FORMATS:
            print(f"  {NEON_GREEN}[{key}]{RESET} {label}")

        choice = get_input("Format", "1")

        for key, label, value in self.FORMATS:
            if choice == key:
                return value

        return 'jpg'

    def _download_thumbnails(self, video_id: str, info: Dict, quality: str, format_choice: str):
        """Download thumbnails"""
        output_dir = self.create_output_dir('thumbnails')
        title = self.sanitize_filename(info.get('title', f'thumbnail_{video_id}'))

        if quality == 'all':
            # Download all available qualities
            downloaded = 0

            print(f"\n{NEON_GREEN}[+] Downloading all available thumbnails...{RESET}\n")

            for q_name, url_template in self.THUMBNAIL_URLS.items():
                output_file = os.path.join(output_dir, f"{title}_{q_name}.{format_choice}")

                if self._download_single_thumbnail(video_id, output_file, q_name):
                    print(f"  {NEON_GREEN}✓{RESET} Downloaded: {q_name}")
                    downloaded += 1
                else:
                    print(f"  {NEON_RED}✗{RESET} Not available: {q_name}")

            print(f"\n{NEON_GREEN}[+] Downloaded {downloaded} thumbnails{RESET}")
            print(f"{NEON_CYAN}[→] Output folder: {output_dir}{RESET}")

        else:
            # Download single quality
            output_file = os.path.join(output_dir, f"{title}.{format_choice}")
            output_file = self.get_unique_filename(output_file)

            print(f"\n{NEON_GREEN}[+] Downloading thumbnail...{RESET}")

            if self._download_single_thumbnail(video_id, output_file, quality):
                show_success_box("SUCCESS", f"Thumbnail saved to:\n{output_file}")
            else:
                show_error_box("Error", "Could not download thumbnail. The quality might not be available.")

        press_enter()

    def _download_single_thumbnail(self, video_id: str, output_path: str, quality: str) -> bool:
        """Download a single thumbnail"""
        url = self.THUMBNAIL_URLS.get(quality, self.THUMBNAIL_URLS['hq'])
        url = url.format(id=video_id)

        try:
            # Create request with user agent
            request = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )

            response = urllib.request.urlopen(request, timeout=10)

            if response.status == 200:
                data = response.read()

                # Save thumbnail
                with open(output_path, 'wb') as f:
                    f.write(data)

                return True

        except Exception:
            pass

        return False

    def download(self, url: str, quality: str = 'maxres', format_choice: str = 'jpg',
                 output_dir: str = None) -> Tuple[bool, str]:
        """Programmatic download"""
        video_id = get_video_id(url)
        if not video_id:
            return False, "Invalid YouTube URL"

        if output_dir is None:
            output_dir = self.create_output_dir('thumbnails')

        # Get title from video info
        info = self._get_video_info(url)
        title = self.sanitize_filename(info.get('title', f'thumbnail_{video_id}'))
        output_file = os.path.join(output_dir, f"{title}.{format_choice}")

        if self._download_single_thumbnail(video_id, output_file, quality):
            return True, output_file

        return False, "Could not download thumbnail"


def run():
    """Run thumbnail grabber"""
    grabber = ThumbnailGrabber()
    grabber.run()


if __name__ == "__main__":
    run()

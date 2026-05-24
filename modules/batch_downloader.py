#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - Module 7: Batch Downloader                  ║
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
from utils.helpers import get_input, confirm, press_enter, format_size, sanitize_filename
from utils.validator import URLValidator, get_video_id, get_playlist_id


class BatchDownloader(DownloaderBase):
    """
    Batch Downloader Module
    - Download multiple videos at once
    - File input support
    - Parallel downloads
    - Progress tracking
    """

    def __init__(self):
        super().__init__()
        self.name = "Batch Downloader"
        self.module_icon = "📦"
        self.total = 0
        self.downloaded = 0
        self.failed = 0
        self.results = []

    def run(self):
        """Run batch downloader module"""
        show_module_header(f"{self.module_icon} BATCH DOWNLOADER", "▶")

        # Get input method
        print(f"{NEON_CYAN}[?] Select Input Method:{RESET}\n")
        print(f"  {NEON_GREEN}[1]{RESET} Enter URLs manually")
        print(f"  {NEON_GREEN}[2]{RESET} Load URLs from file")
        print(f"  {NEON_GREEN}[3]{RESET} From download history")

        choice = get_input("Method", "1")

        urls = []

        if choice == '1':
            urls = self._get_manual_urls()
        elif choice == '2':
            urls = self._get_urls_from_file()
        elif choice == '3':
            urls = self._get_urls_from_history()
        else:
            show_error_box("Invalid", "Invalid choice")
            return

        if not urls:
            show_error_box("No URLs", "No valid URLs provided")
            return

        # Display URLs
        self._display_urls(urls)

        # Get options
        options = self._get_options()

        # Confirm
        if not confirm(f"Download {len(urls)} videos?", True):
            print(f"{NEON_YELLOW}[!] Download cancelled{RESET}")
            return

        # Start batch download
        self._start_batch_download(urls, options)

    def _get_manual_urls(self) -> List[str]:
        """Get URLs manually from user"""
        print(f"\n{NEON_CYAN}[?] Enter YouTube URLs (one per line, empty line to finish):{RESET}\n")

        urls = []
        while True:
            url = input(f"  {NEON_GREEN}[URL]>{RESET} ").strip()

            if not url:
                break

            if URLValidator.is_youtube_url(url):
                urls.append(url)
            else:
                print(f"  {NEON_RED}✗ Invalid URL skipped{RESET}")

        return urls

    def _get_urls_from_file(self) -> List[str]:
        """Load URLs from file"""
        print(f"\n{NEON_CYAN}[?] Enter file path (or press Enter for default 'urls.txt'):{RESET}")
        filepath = get_input("File", "urls.txt")

        if not os.path.exists(filepath):
            show_error_box("File Not Found", f"File not found: {filepath}")
            return []

        urls = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and URLValidator.is_youtube_url(line):
                    urls.append(line)

        return urls

    def _get_urls_from_history(self) -> List[str]:
        """Get URLs from download history"""
        # Try to load from config
        try:
            from core.config import config
            history = config.get_history(20)

            if not history:
                show_error_box("No History", "No download history found")
                return []

            print(f"\n{NEON_CYAN}[?] Select from history:{RESET}\n")

            for i, entry in enumerate(history[:10], 1):
                url = entry.get('url', 'Unknown')
                print(f"  {NEON_GREEN}[{i}]{RESET} {url[:50]}")

            selection = get_input("Select (comma-separated)", "1")

            indices = [int(x.strip()) - 1 for x in selection.split(',') if x.strip().isdigit()]
            urls = [history[i]['url'] for i in indices if 0 <= i < len(history)]

            return urls

        except Exception:
            show_error_box("Error", "Could not load history")
            return []

    def _display_urls(self, urls: List[str]):
        """Display URLs to download"""
        print(f"\n{NEON_GREEN}╔══════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{NEON_GREEN}║{RESET} {BRIGHT_WHITE}{'URLS TO DOWNLOAD'.center(58)}{RESET} {NEON_GREEN}║{RESET}")
        print(f"{NEON_GREEN}╠══════════════════════════════════════════════════════════════╣{RESET}")

        for i, url in enumerate(urls[:10], 1):
            print(f"{NEON_GREEN}║{RESET} {NEON_GREEN}[{i}]{RESET} {url[:50]}")

        if len(urls) > 10:
            print(f"{NEON_GREEN}║{RESET} {DIM}... and {len(urls) - 10} more{RESET}")

        print(f"{NEON_GREEN}╚══════════════════════════════════════════════════════════════╝{RESET}")

    def _get_options(self) -> Dict:
        """Get download options"""
        options = {}

        # Quality
        print(f"\n{NEON_CYAN}[?] Video Quality:{RESET}")
        print(f"  {NEON_GREEN}[1]{RESET} Best")
        print(f"  {NEON_GREEN}[2]{RESET} 1080p")
        print(f"  {NEON_GREEN}[3]{RESET} 720p")

        quality = get_input("Quality", "1")
        options['quality'] = {'1': 'best', '2': '1080', '3': '720'}.get(quality, 'best')

        # Format
        print(f"\n{NEON_CYAN}[?] Format:{RESET}")
        print(f"  {NEON_GREEN}[1]{RESET} Video (MP4)")
        print(f"  {NEON_GREEN}[2]{RESET} Audio (MP3)")

        format_choice = get_input("Format", "1")

        if format_choice == '2':
            options['audio_only'] = True
            options['format'] = 'mp3'
        else:
            options['audio_only'] = False
            options['format'] = 'mp4'

        # Parallel
        print(f"\n{NEON_CYAN}[?] Parallel downloads (1-5):{RESET}")
        parallel = get_input("Count", "3")
        try:
            options['parallel'] = min(5, max(1, int(parallel)))
        except Exception:
            options['parallel'] = 3

        # Skip existing
        options['skip_existing'] = confirm("Skip existing?", True)

        return options

    def _start_batch_download(self, urls: List[str], options: Dict):
        """Start batch download process"""
        self.total = len(urls)
        self.downloaded = 0
        self.failed = 0
        self.results = []

        # Create output directory
        subfolder = 'audio' if options.get('audio_only') else 'videos'
        output_dir = self.create_output_dir(f'batch_{subfolder}')

        print(f"\n{NEON_GREEN}[+] Starting batch download...{RESET}")
        print(f"{NEON_CYAN}[→] Total: {self.total} URLs{RESET}")
        print(f"{NEON_CYAN}[→] Parallel: {options['parallel']}{RESET}")
        print(f"{NEON_CYAN}[→] Output: {output_dir}{RESET}\n")

        # Process URLs
        for i, url in enumerate(urls, 1):
            print(f"\n{NEON_GREEN}[{i}/{self.total}]{RESET} Processing: {url[:50]}")

            success, message = self._download_single(url, output_dir, options)

            if success:
                self.downloaded += 1
                print(f"  {NEON_GREEN}✓ Success{RESET}")
            else:
                self.failed += 1
                print(f"  {NEON_RED}✗ Failed: {message[:40]}{RESET}")

            self.results.append({
                'url': url,
                'success': success,
                'message': message
            })

        # Show summary
        self._show_summary(output_dir)

    def _download_single(self, url: str, output_dir: str, options: Dict) -> Tuple[bool, str]:
        """Download single URL"""
        try:
            cmd = ['yt-dlp']

            # Format selection
            if options.get('audio_only'):
                cmd.extend(['-x', '--audio-format', 'mp3', '--audio-quality', '0'])
            else:
                quality = options.get('quality', 'best')
                if quality == 'best':
                    format_str = 'bestvideo[ext=mp4]+bestaudio/best[ext=mp4]/best'
                else:
                    format_str = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best'
                cmd.extend(['-f', format_str, '--merge-output-format', 'mp4'])

            # Output
            output_template = os.path.join(output_dir, '%(title)s.%(ext)s')
            cmd.extend(['-o', output_template])

            # Skip if exists
            if options.get('skip_existing'):
                pass  # yt-dlp auto-handles

            cmd.append(url)

            result = subprocess.run(cmd, capture_output=True, timeout=600)

            if result.returncode == 0:
                return True, "Downloaded"
            else:
                return False, result.stderr.decode()[:100]

        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)[:50]

    def _show_summary(self, output_dir: str):
        """Show download summary"""
        print(f"\n{NEON_GREEN}╔══════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{NEON_GREEN}║{RESET} {BRIGHT_WHITE}{'BATCH DOWNLOAD SUMMARY'.center(58)}{RESET} {NEON_GREEN}║{RESET}")
        print(f"{NEON_GREEN}╠══════════════════════════════════════════════════════════════╣{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}Total:{RESET} {BRIGHT_WHITE}{self.total}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {NEON_GREEN}Downloaded:{RESET} {BRIGHT_WHITE}{self.downloaded}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {NEON_RED}Failed:{RESET} {BRIGHT_WHITE}{self.failed}{RESET}")
        print(f"{NEON_GREEN}║{RESET} {CYAN}Output:{RESET} {BRIGHT_WHITE}{output_dir[:40]}{RESET}")
        print(f"{NEON_GREEN}╚══════════════════════════════════════════════════════════════╝{RESET}")

        # Save report
        report_file = os.path.join(output_dir, 'batch_report.json')
        try:
            with open(report_file, 'w') as f:
                json.dump({
                    'total': self.total,
                    'downloaded': self.downloaded,
                    'failed': self.failed,
                    'results': self.results
                }, f, indent=2)
            print(f"\n{NEON_CYAN}[→] Report saved: {report_file}{RESET}")
        except Exception:
            pass

        press_enter()


def run():
    """Run batch downloader"""
    downloader = BatchDownloader()
    downloader.run()


if __name__ == "__main__":
    run()

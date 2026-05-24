#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - Progress Bars & Animations                  ║
║  Author: RS (T3rmuxk1ng)                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys
import time
import shutil
from typing import Optional
from .colors import *


class ProgressBar:
    """
    Animated progress bar for downloads
    - Visual progress indication
    - Speed calculation
    - ETA estimation
    - Termux compatible
    """

    def __init__(self, total: int = 100, prefix: str = "", suffix: str = "",
                 length: int = 40, fill: str = "█", empty: str = "░"):
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.length = length
        self.fill = fill
        self.empty = empty
        self.current = 0
        self.start_time = time.time()
        self.last_update = 0
        self.update_interval = 0.1  # Update every 100ms

    def update(self, current: int, suffix: str = None):
        """Update progress bar"""
        self.current = current

        # Limit update frequency
        now = time.time()
        if now - self.last_update < self.update_interval and current < self.total:
            return
        self.last_update = now

        if suffix:
            self.suffix = suffix

        # Calculate progress
        percent = 100 * (self.current / self.total) if self.total > 0 else 0
        filled = int(self.length * self.current // self.total) if self.total > 0 else 0
        bar = f"{NEON_GREEN}{self.fill * filled}{RESET}{DIM}{self.empty * (self.length - filled)}{RESET}"

        # Calculate speed and ETA
        elapsed = time.time() - self.start_time
        speed = self.current / elapsed if elapsed > 0 else 0
        eta = (self.total - self.current) / speed if speed > 0 else 0

        # Format output
        speed_str = self._format_size(speed) + "/s"
        eta_str = self._format_time(eta)

        # Print progress
        line = f"\r{self.prefix} |{bar}| {percent:5.1f}% {speed_str:>10} ETA: {eta_str} {self.suffix}"
        sys.stdout.write(line)
        sys.stdout.flush()

    def finish(self, message: str = "Complete!"):
        """Finish progress bar"""
        self.update(self.total, message)
        print()

    def _format_size(self, bytes: float) -> str:
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024:
                return f"{bytes:.1f}{unit}"
            bytes /= 1024
        return f"{bytes:.1f}TB"

    def _format_time(self, seconds: float) -> str:
        """Format seconds to readable time"""
        if seconds < 0:
            return "--:--"
        elif seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m{int(seconds % 60)}s"
        else:
            return f"{int(seconds // 3600)}h{int((seconds % 3600) // 60)}m"


class DownloadProgress:
    """
    Progress tracker for downloads with detailed info
    """

    def __init__(self, filename: str = "", total_size: int = 0):
        self.filename = filename
        self.total_size = total_size
        self.downloaded = 0
        self.start_time = time.time()
        self.last_bytes = 0
        self.last_time = time.time()
        self.speed = 0

    def update(self, bytes_received: int):
        """Update download progress"""
        now = time.time()
        self.downloaded = bytes_received

        # Calculate speed
        time_diff = now - self.last_time
        if time_diff >= 0.5:  # Update speed every 0.5s
            bytes_diff = self.downloaded - self.last_bytes
            self.speed = bytes_diff / time_diff
            self.last_bytes = self.downloaded
            self.last_time = now

    def get_progress(self) -> dict:
        """Get progress info"""
        elapsed = time.time() - self.start_time
        percent = (self.downloaded / self.total_size * 100) if self.total_size > 0 else 0
        eta = (self.total_size - self.downloaded) / self.speed if self.speed > 0 else 0

        return {
            'downloaded': self.downloaded,
            'total': self.total_size,
            'percent': percent,
            'speed': self.speed,
            'elapsed': elapsed,
            'eta': eta
        }

    def print_progress(self):
        """Print progress line"""
        info = self.get_progress()

        # Format values
        downloaded_str = self._format_size(info['downloaded'])
        total_str = self._format_size(info['total'])
        speed_str = self._format_size(info['speed']) + "/s"
        eta_str = self._format_time(info['eta'])

        # Create progress bar
        bar_length = 30
        filled = int(bar_length * info['percent'] / 100)
        bar = f"{NEON_GREEN}{'█' * filled}{RESET}{DIM}{'░' * (bar_length - filled)}{RESET}"

        # Print line
        line = (f"\r{NEON_CYAN}[↓]{RESET} {self.filename[:30]:<30} "
                f"[{bar}] {info['percent']:5.1f}% "
                f"{downloaded_str}/{total_str} {speed_str:>12} ETA: {eta_str}")

        sys.stdout.write(line)
        sys.stdout.flush()

    def finish(self, success: bool = True):
        """Finish download"""
        self.print_progress()
        if success:
            print(f"\n{NEON_GREEN}✓ Download complete!{RESET}")
        else:
            print(f"\n{NEON_RED}✗ Download failed!{RESET}")

    def _format_size(self, bytes: int) -> str:
        """Format bytes"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024:
                return f"{bytes:.1f}{unit}"
            bytes /= 1024
        return f"{bytes:.1f}TB"

    def _format_time(self, seconds: float) -> str:
        """Format time"""
        if seconds < 0:
            return "--:--"
        elif seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m{int(seconds % 60)}s"
        else:
            return f"{int(seconds // 3600)}h{int((seconds % 3600) // 60)}m"


class MultiProgressBar:
    """
    Multiple progress bars for parallel downloads
    """

    def __init__(self, num_bars: int = 3, length: int = 30):
        self.num_bars = num_bars
        self.length = length
        self.bars = [ProgressBar(length=length) for _ in range(num_bars)]

    def update(self, bar_index: int, current: int, total: int, label: str = ""):
        """Update specific bar"""
        if 0 <= bar_index < self.num_bars:
            bar = self.bars[bar_index]
            bar.total = total
            bar.prefix = label[:15].ljust(15)
            bar.update(current)

    def render(self):
        """Render all bars"""
        # Move cursor up for redraw
        for i in range(self.num_bars):
            sys.stdout.write("[F")  # Move up one line

        for bar in self.bars:
            bar.print_progress()


def show_download_progress(downloaded: int, total: int, speed: float = 0,
                           filename: str = "", prefix: str = ""):
    """
    Simple function to show download progress

    Args:
        downloaded: Bytes downloaded
        total: Total bytes
        speed: Download speed in bytes/sec
        filename: File being downloaded
        prefix: Prefix text
    """
    # Calculate percentage
    percent = (downloaded / total * 100) if total > 0 else 0

    # Create progress bar
    bar_length = 30
    filled = int(bar_length * percent / 100)
    bar = f"{NEON_GREEN}{'█' * filled}{RESET}{DIM}{'░' * (bar_length - filled)}{RESET}"

    # Format sizes
    def format_size(b):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if b < 1024:
                return f"{b:.1f}{unit}"
            b /= 1024
        return f"{b:.1f}TB"

    downloaded_str = format_size(downloaded)
    total_str = format_size(total)
    speed_str = format_size(speed) + "/s" if speed > 0 else "-- MB/s"

    # Print progress line
    line = (f"\r{NEON_CYAN}{prefix}{RESET} {filename[:25]:<25} "
            f"[{bar}] {percent:5.1f}% {downloaded_str}/{total_str} {speed_str:>12}")

    sys.stdout.write(line)
    sys.stdout.flush()


def show_upload_progress(uploaded: int, total: int, speed: float = 0,
                         filename: str = ""):
    """Show upload progress"""
    show_download_progress(uploaded, total, speed, filename, "↑")


def print_progress_bar(iteration: int, total: int, prefix: str = '',
                       suffix: str = '', length: int = 50, fill: str = '█'):
    """
    Simple progress bar for any iteration

    Args:
        iteration: Current iteration
        total: Total iterations
        prefix: Prefix string
        suffix: Suffix string
        length: Bar length
        fill: Fill character
    """
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled = int(length * iteration // total)
    bar = f"{NEON_GREEN}{fill * filled}{RESET}{DIM}{'░' * (length - filled)}{RESET}"

    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')

    if iteration == total:
        print()

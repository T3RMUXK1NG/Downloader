#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - Helper Utilities                            ║
║  Author: RS (T3rmuxk1ng)                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import shutil
import threading
import platform
from typing import Optional, Callable
from .colors import *


def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_terminal_width() -> int:
    """Get terminal width"""
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 80


def center_text(text: str, width: int = None) -> str:
    """Center text in terminal"""
    if width is None:
        width = get_terminal_width()
    return text.center(width)


def animate_text(text: str, delay: float = 0.02, color: str = NEON_GREEN):
    """Animate text character by character"""
    for char in text:
        sys.stdout.write(f"{color}{char}{RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    print()


def type_text(text: str, delay: float = 0.03):
    """Type text like typing effect"""
    animate_text(text, delay, NEON_CYAN)


def format_size(bytes: int) -> str:
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} PB"


def format_time(seconds: int) -> str:
    """Format seconds to human readable time"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        mins, secs = divmod(seconds, 60)
        return f"{mins}m {secs}s"
    else:
        hrs, mins = divmod(seconds // 60, 60)
        return f"{hrs}h {mins}m"


def format_duration(seconds: int) -> str:
    """Format duration to HH:MM:SS or MM:SS"""
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_number(num: int) -> str:
    """Format number with K/M/B suffixes"""
    if num >= 1000000000:
        return f"{num/1000000000:.1f}B"
    elif num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)


def create_directory(path: str) -> bool:
    """Create directory if not exists"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception:
        return False


def sanitize_filename(filename: str, max_length: int = 200) -> str:
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


def get_unique_filename(filepath: str) -> str:
    """Get unique filename if file exists"""
    if not os.path.exists(filepath):
        return filepath

    base, ext = os.path.splitext(filepath)
    counter = 1

    while os.path.exists(f"{base}_{counter}{ext}"):
        counter += 1

    return f"{base}_{counter}{ext}"


def is_termux() -> bool:
    """Check if running in Termux"""
    return 'TERMUX_VERSION' in os.environ or 'com.termux' in os.environ.get('PREFIX', '')


def get_downloads_folder() -> str:
    """Get default downloads folder based on OS"""
    if os.name == 'nt':  # Windows
        return os.path.join(os.environ.get('USERPROFILE', '~'), 'Downloads')
    elif is_termux():  # Termux
        return os.path.expanduser('~/storage/downloads')
    else:  # Linux/Mac
        return os.path.join(os.environ.get('HOME', '~'), 'Downloads')


def get_app_data_folder() -> str:
    """Get application data folder"""
    if os.name == 'nt':  # Windows
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
    elif is_termux():  # Termux
        base = os.path.expanduser('~')
    else:  # Linux/Mac
        base = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))

    app_folder = os.path.join(base, 'rs_downloader')
    create_directory(app_folder)
    return app_folder


def print_table(headers: list, rows: list, padding: int = 2):
    """Print formatted table"""
    # Calculate column widths
    widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    # Add padding
    widths = [w + padding for w in widths]

    # Print header
    header_line = '│'.join(str(h).center(w) for h, w in zip(headers, widths))
    separator = '┼'.join('─' * w for w in widths)

    print(f"{NEON_GREEN}┌{'┬'.join('─' * w for w in widths)}┐{RESET}")
    print(f"{NEON_GREEN}│{RESET}{header_line}{NEON_GREEN}│{RESET}")
    print(f"{NEON_GREEN}├{separator}┤{RESET}")

    # Print rows
    for row in rows:
        row_line = '│'.join(str(cell).center(w) for cell, w in zip(row, widths))
        print(f"{NEON_GREEN}│{RESET}{row_line}{NEON_GREEN}│{RESET}")

    print(f"{NEON_GREEN}└{'┴'.join('─' * w for w in widths)}┘{RESET}")


def print_box(title: str, content: list = None, style: str = "double"):
    """Print content in a styled box"""
    if content is None:
        content = []

    max_len = max(len(title), max(len(str(line)) for line in content) if content else 0)
    width = max_len + 4

    if style == "double":
        tl, tr, bl, br, h, v = "╔", "╗", "╚", "╝", "═", "║"
    else:
        tl, tr, bl, br, h, v = "┌", "┐", "└", "┘", "─", "│"

    print(f"{NEON_GREEN}{tl}{h * width}{tr}{RESET}")
    print(f"{NEON_GREEN}{v}{RESET} {BRIGHT_WHITE}{title.center(max_len)}{RESET} {NEON_GREEN}{v}{RESET}")

    if content:
        print(f"{NEON_GREEN}{tl}{h * width}{tr}{RESET}")
        for line in content:
            print(f"{NEON_GREEN}{v}{RESET} {BRIGHT_WHITE}{str(line).ljust(max_len)}{RESET} {NEON_GREEN}{v}{RESET}")

    print(f"{NEON_GREEN}{bl}{h * width}{br}{RESET}")


def get_input(prompt: str, default: str = None, color: str = NEON_CYAN) -> str:
    """Get user input with styling"""
    if default:
        prompt_text = f"{color}[?] {prompt} [{default}]: {RESET}"
    else:
        prompt_text = f"{color}[?] {prompt}: {RESET}"

    try:
        result = input(prompt_text).strip()
        return result if result else default
    except KeyboardInterrupt:
        print(f"\n{NEON_YELLOW}[!] Input cancelled{RESET}")
        return default


def confirm(prompt: str, default: bool = False) -> bool:
    """Get yes/no confirmation"""
    default_str = "Y/n" if default else "y/N"
    response = get_input(f"{prompt} ({default_str})")

    if response is None or response == '':
        return default

    return response.lower() in ['y', 'yes', 'true', '1']


def select_option(prompt: str, options: list) -> int:
    """Select from numbered options"""
    print(f"\n{NEON_CYAN}[?] {prompt}{RESET}\n")

    for i, option in enumerate(options, 1):
        print(f"  {NEON_GREEN}[{i}]{RESET} {option}")

    while True:
        try:
            choice = input(f"\n{NEON_CYAN}[RS]>{RESET} Select: {RESET}")
            index = int(choice)
            if 1 <= index <= len(options):
                return index - 1
            print(f"{NEON_RED}[!] Invalid option{RESET}")
        except ValueError:
            print(f"{NEON_RED}[!] Enter a number{RESET}")


def press_enter(prompt: str = "Press Enter to continue..."):
    """Wait for Enter key"""
    input(f"\n{DIM}{prompt}{RESET}")


def show_spinner(message: str, duration: float = 2.0):
    """Show animated spinner"""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration

    i = 0
    while time.time() < end_time:
        frame = frames[i % len(frames)]
        sys.stdout.write(f"\r{NEON_CYAN}{frame}{RESET} {message}...")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1

    sys.stdout.write(f"\r{NEON_GREEN}✓{RESET} {message} complete!   \n")


class Spinner:
    """Context manager for spinner animation"""

    def __init__(self, message: str = "Processing"):
        self.message = message
        self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.running = False
        self.thread = None

    def _spin(self):
        i = 0
        while self.running:
            frame = self.frames[i % len(self.frames)]
            sys.stdout.write(f"\r{NEON_CYAN}{frame}{RESET} {self.message}...")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()

    def stop(self, success: bool = True):
        self.running = False
        if self.thread:
            self.thread.join()
        status = f"{NEON_GREEN}✓{RESET}" if success else f"{NEON_RED}✗{RESET}"
        sys.stdout.write(f"\r{status} {self.message}{' ' * 20}\n")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop(exc_type is None)


def get_system_info() -> dict:
    """Get system information"""
    return {
        'os': platform.system(),
        'os_version': platform.version(),
        'python': platform.python_version(),
        'architecture': platform.machine(),
        'termux': is_termux(),
        'downloads_folder': get_downloads_folder(),
    }

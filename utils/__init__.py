#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - Utils Module                                ║
║  Author: RS (T3rmuxk1ng)                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from .colors import *
from .banner import *
from .helpers import *
from .progress import *
from .validator import *

__all__ = [
    # Colors
    'RESET', 'BOLD', 'DIM', 'UNDERLINE', 'BLINK',
    'BLACK', 'RED', 'GREEN', 'YELLOW', 'BLUE', 'MAGENTA', 'CYAN', 'WHITE',
    'BRIGHT_BLACK', 'BRIGHT_RED', 'BRIGHT_GREEN', 'BRIGHT_YELLOW',
    'BRIGHT_BLUE', 'BRIGHT_MAGENTA', 'BRIGHT_CYAN', 'BRIGHT_WHITE',
    'NEON_GREEN', 'NEON_CYAN', 'NEON_RED', 'NEON_YELLOW', 'NEON_PURPLE',
    'color_text', 'success', 'error', 'warning', 'info', 'highlight',

    # Banner
    'show_banner', 'show_mini_banner', 'show_about', 'show_module_header',
    'show_menu_box', 'show_error_box', 'show_success_box', 'show_loading',

    # Helpers
    'clear_screen', 'get_terminal_width', 'center_text', 'animate_text',
    'type_text', 'format_size', 'format_time', 'format_duration', 'format_number',
    'create_directory', 'sanitize_filename', 'get_unique_filename',
    'is_termux', 'get_downloads_folder', 'get_app_data_folder',
    'print_table', 'print_box', 'get_input', 'confirm', 'select_option',
    'press_enter', 'show_spinner', 'Spinner', 'get_system_info',

    # Progress
    'ProgressBar', 'DownloadProgress', 'MultiProgressBar',
    'show_download_progress', 'show_upload_progress', 'print_progress_bar',

    # Validator
    'URLValidator', 'validate_youtube_url', 'get_video_id', 'get_playlist_id',
    'get_url_type',
]

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - Color Definitions                           ║
║  Author: RS (T3rmuxk1ng)                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys

# Disable colors if NO_COLOR is set or not a TTY
_NO_COLOR = os.environ.get('NO_COLOR', '') or not hasattr(sys, 'stdout') or not os.isatty(1)

# ANSI Color Codes - Hacker Terminal Style
RESET = '' if _NO_COLOR else '\033[0m'
BOLD = '' if _NO_COLOR else '\033[1m'
DIM = '' if _NO_COLOR else '\033[2m'
UNDERLINE = '' if _NO_COLOR else '\033[4m'
BLINK = '' if _NO_COLOR else '\033[5m'
REVERSE = '' if _NO_COLOR else '\033[7m'

# Standard Colors
BLACK = '' if _NO_COLOR else '\033[30m'
RED = '' if _NO_COLOR else '\033[31m'
GREEN = '' if _NO_COLOR else '\033[32m'
YELLOW = '' if _NO_COLOR else '\033[33m'
BLUE = '' if _NO_COLOR else '\033[34m'
MAGENTA = '' if _NO_COLOR else '\033[35m'
CYAN = '' if _NO_COLOR else '\033[36m'
WHITE = '' if _NO_COLOR else '\033[37m'

# Bright Colors
BRIGHT_BLACK = '' if _NO_COLOR else '\033[90m'
BRIGHT_RED = '' if _NO_COLOR else '\033[91m'
BRIGHT_GREEN = '' if _NO_COLOR else '\033[92m'
BRIGHT_YELLOW = '' if _NO_COLOR else '\033[93m'
BRIGHT_BLUE = '' if _NO_COLOR else '\033[94m'
BRIGHT_MAGENTA = '' if _NO_COLOR else '\033[95m'
BRIGHT_CYAN = '' if _NO_COLOR else '\033[96m'
BRIGHT_WHITE = '' if _NO_COLOR else '\033[97m'

# Hacker Style Colors
NEON_GREEN = '' if _NO_COLOR else '\033[92m'
NEON_CYAN = '' if _NO_COLOR else '\033[96m'
NEON_RED = '' if _NO_COLOR else '\033[91m'
NEON_YELLOW = '' if _NO_COLOR else '\033[93m'
NEON_PURPLE = '' if _NO_COLOR else '\033[95m'
NEON_BLUE = '' if _NO_COLOR else '\033[94m'
MATRIX_GREEN = '' if _NO_COLOR else '\033[32m'

# Background Colors
BG_BLACK = '' if _NO_COLOR else '\033[40m'
BG_RED = '' if _NO_COLOR else '\033[41m'
BG_GREEN = '' if _NO_COLOR else '\033[42m'
BG_YELLOW = '' if _NO_COLOR else '\033[43m'
BG_BLUE = '' if _NO_COLOR else '\033[44m'
BG_MAGENTA = '' if _NO_COLOR else '\033[45m'
BG_CYAN = '' if _NO_COLOR else '\033[46m'
BG_WHITE = '' if _NO_COLOR else '\033[47m'

# Progress Bar Colors
PROGRESS_DONE = NEON_GREEN
PROGRESS_LEFT = DIM + WHITE
PROGRESS_CURRENT = NEON_CYAN

# RS Branding Colors
RS_PRIMARY = NEON_GREEN
RS_SECONDARY = NEON_CYAN
RS_ACCENT = NEON_YELLOW
RS_ERROR = NEON_RED


def color_text(text: str, color: str) -> str:
    """Apply color to text"""
    return f"{color}{text}{RESET}"


def success(text: str) -> str:
    """Green success text"""
    return f"{NEON_GREEN}✓ {text}{RESET}"


def error(text: str) -> str:
    """Red error text"""
    return f"{NEON_RED}✗ {text}{RESET}"


def warning(text: str) -> str:
    """Yellow warning text"""
    return f"{NEON_YELLOW}⚠ {text}{RESET}"


def info(text: str) -> str:
    """Cyan info text"""
    return f"{NEON_CYAN}ℹ {text}{RESET}"


def highlight(text: str) -> str:
    """Highlight important text"""
    return f"{BOLD}{NEON_YELLOW}{text}{RESET}"


def dim_text(text: str) -> str:
    """Dim less important text"""
    return f"{DIM}{text}{RESET}"


def rainbow(text: str) -> str:
    """Rainbow colored text"""
    colors = [RED, YELLOW, GREEN, CYAN, BLUE, MAGENTA]
    result = ""
    for i, char in enumerate(text):
        result += f"{colors[i % len(colors)]}{char}"
    return result + RESET

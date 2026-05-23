#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - Color Definitions                           ║
║  Author: RS (T3rmuxk1ng)                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ANSI Color Codes - Hacker Terminal Style
RESET = '[0m'
BOLD = '[1m'
DIM = '[2m'
UNDERLINE = '[4m'
BLINK = '[5m'
REVERSE = '[7m'

# Standard Colors
BLACK = '[30m'
RED = '[31m'
GREEN = '[32m'
YELLOW = '[33m'
BLUE = '[34m'
MAGENTA = '[35m'
CYAN = '[36m'
WHITE = '[37m'

# Bright Colors
BRIGHT_BLACK = '[90m'
BRIGHT_RED = '[91m'
BRIGHT_GREEN = '[92m'
BRIGHT_YELLOW = '[93m'
BRIGHT_BLUE = '[94m'
BRIGHT_MAGENTA = '[95m'
BRIGHT_CYAN = '[96m'
BRIGHT_WHITE = '[97m'

# Hacker Style Colors
NEON_GREEN = '[92m[1m'
NEON_CYAN = '[96m[1m'
NEON_RED = '[91m[1m'
NEON_YELLOW = '[93m[1m'
NEON_PURPLE = '[95m[1m'
NEON_BLUE = '[94m[1m'
MATRIX_GREEN = '[32m[5m'

# Background Colors
BG_BLACK = '[40m'
BG_RED = '[41m'
BG_GREEN = '[42m'
BG_YELLOW = '[43m'
BG_BLUE = '[44m'
BG_MAGENTA = '[45m'
BG_CYAN = '[46m'
BG_WHITE = '[47m'

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

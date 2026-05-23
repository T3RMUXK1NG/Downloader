#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - Color Definitions (v2.0 GOD MODE NEXUS)     ║
║  Author: RS (T3rmuxk1ng)                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ANSI Color Codes - Hacker Terminal Style
RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'
UNDERLINE = '\033[4m'
BLINK = '\033[5m'
REVERSE = '\033[7m'

# Standard Colors
BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'

# Bright Colors
BRIGHT_BLACK = '\033[90m'
BRIGHT_RED = '\033[91m'
BRIGHT_GREEN = '\033[92m'
BRIGHT_YELLOW = '\033[93m'
BRIGHT_BLUE = '\033[94m'
BRIGHT_MAGENTA = '\033[95m'
BRIGHT_CYAN = '\033[96m'
BRIGHT_WHITE = '\033[97m'

# Hacker Style Colors - GOD MODE NEXUS Theme
NEON_GREEN = '\033[92m\033[1m'
NEON_CYAN = '\033[96m\033[1m'
NEON_RED = '\033[91m\033[1m'
NEON_YELLOW = '\033[93m\033[1m'
NEON_PURPLE = '\033[95m\033[1m'
NEON_BLUE = '\033[94m\033[1m'
MATRIX_GREEN = '\033[32m\033[2m'

# Background Colors
BG_BLACK = '\033[40m'
BG_RED = '\033[41m'
BG_GREEN = '\033[42m'
BG_YELLOW = '\033[43m'
BG_BLUE = '\033[44m'
BG_MAGENTA = '\033[45m'
BG_CYAN = '\033[46m'
BG_WHITE = '\033[47m'

# Progress Bar Colors
PROGRESS_DONE = NEON_GREEN
PROGRESS_LEFT = DIM + WHITE
PROGRESS_CURRENT = NEON_CYAN

# RS Branding Colors
RS_PRIMARY = NEON_GREEN
RS_SECONDARY = NEON_CYAN
RS_ACCENT = NEON_YELLOW
RS_ERROR = NEON_RED

# GOD MODE NEXUS Special Colors
NEXUS_GOLD = '\033[38;5;220m\033[1m'
NEXUS_PURPLE = '\033[38;5;129m\033[1m'
NEXUS_BLUE = '\033[38;5;39m\033[1m'
NEXUS_PINK = '\033[38;5;199m\033[1m'


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


def nexus_text(text: str) -> str:
    """GOD MODE NEXUS styled text"""
    return f"{NEXUS_PURPLE}{BOLD}{text}{RESET}"


def god_mode_text(text: str) -> str:
    """GOD MODE special text"""
    return f"{NEXUS_GOLD}{BOLD}🔱 {text} 🔱{RESET}"

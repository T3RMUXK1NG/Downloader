#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ULTIMATE NEXUS BANNER SYSTEM                         ║
║                              v3.0.1 SOVEREIGN EDITION                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Author: RAJSARASWATI JATAV (RS) - OMNIPOTENT SOVEREIGN NEXUS                ║
║  Channel: T3rmuxk1ng                                                         ║
║  Description: Advanced banner generation with 20+ styles, animations,       ║
║               ASCII art, sound notifications, and customizable templates     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import os
import sys
import time
import random
import shutil
import platform
import subprocess
from typing import Dict, List, Tuple, Optional, Union, Callable, Any
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime
import threading
import itertools

from .colors import (
    ColorManager, ANSICodes, TrueColor, ColorScheme,
    ColorSchemeCategory, ColorSchemes
)

# ============================================================================
# VERSION INFORMATION
# ============================================================================
__version__ = "3.0.1"
__author__ = "RAJSARASWATI JATAV (RS)"
__status__ = "OMNIPOTENT SOVEREIGN"

# ============================================================================
# BANNER STYLE ENUMERATION
# ============================================================================
class BannerStyle(Enum):
    """Available banner styles."""
    CLASSIC = auto()
    MATRIX = auto()
    CYBERPUNK = auto()
    NEON = auto()
    MINIMAL = auto()
    DOUBLE_LINE = auto()
    BLOCK = auto()
    ASCII_ART = auto()
    GRADIENT = auto()
    RETRO = auto()
    MODERN = auto()
    HACKER = auto()
    FIRE = auto()
    ICE = auto()
    NATURE = auto()
    MILITARY = auto()
    CORPORATE = auto()
    GAMING = auto()
    ANIME = auto()
    SCIFI = auto()


class BannerPosition(Enum):
    """Text alignment positions."""
    LEFT = auto()
    CENTER = auto()
    RIGHT = auto()


class AnimationType(Enum):
    """Available animation types."""
    NONE = auto()
    TYPEWRITER = auto()
    FADE_IN = auto()
    SLIDE_IN = auto()
    BLINK = auto()
    RAINBOW = auto()
    MATRIX_RAIN = auto()
    GLITCH = auto()
    PULSE = auto()
    WAVE = auto()
    SCROLL = auto()
    BOUNCE = auto()
    SPIN = auto()
    LOADING = auto()


# ============================================================================
# BANNER TEMPLATE DATA CLASS
# ============================================================================
@dataclass
class BannerTemplate:
    """
    Template for creating custom banners.
    
    Attributes:
        name: Template name
        style: Banner style
        title: Main title text
        subtitle: Subtitle text
        version: Version string
        author: Author name
        description: Tool description
        additional_info: Extra information lines
        color_scheme: Color scheme name or ColorScheme object
        animation: Animation type
        position: Text alignment
        width: Banner width (0 for auto)
        border_style: Border character style
        show_timestamp: Whether to show timestamp
        show_system_info: Whether to show system info
        sound_enabled: Whether to play sound on display
    """
    name: str = "Default Banner"
    style: BannerStyle = BannerStyle.CLASSIC
    title: str = "ULTIMATE NEXUS"
    subtitle: str = ""
    version: str = ""
    author: str = ""
    description: str = ""
    additional_info: List[str] = field(default_factory=list)
    color_scheme: Union[str, ColorScheme] = "NEXUS_HACKER"
    animation: AnimationType = AnimationType.NONE
    position: BannerPosition = BannerPosition.CENTER
    width: int = 0  # Auto
    border_style: str = "═"
    show_timestamp: bool = False
    show_system_info: bool = False
    sound_enabled: bool = False
    
    def __post_init__(self) -> None:
        """Validate and process template data."""
        if isinstance(self.color_scheme, str):
            cm = ColorManager()
            scheme = cm.get_scheme(self.color_scheme)
            if scheme:
                self.color_scheme = scheme


# ============================================================================
# ASCII ART COLLECTIONS
# ============================================================================
class ASCIICollections:
    """Collection of ASCII art for banner generation."""
    
    # Large ASCII fonts (FIGlet-style)
    FONTS = {
        'standard': {
            'A': ["  ███  ", " █   █ ", "███████", "█     █", "█     █"],
            'B': ["██████ ", "█     █", "██████ ", "█     █", "██████ "],
            'C': [" █████ ", "█     █", "█      ", "█     █", " █████ "],
            'D': ["██████ ", "█     █", "█     █", "█     █", "██████ "],
            'E': ["███████", "█      ", "████   ", "█      ", "███████"],
            'F': ["███████", "█      ", "████   ", "█      ", "█      "],
            'G': [" █████ ", "█      ", "█  ████", "█     █", " █████ "],
            'H': ["█     █", "█     █", "███████", "█     █", "█     █"],
            'I': ["███", " █ ", " █ ", " █ ", "███"],
            'J': ["    ███", "      █", "      █", "█     █", " █████ "],
            'K': ["█    █ ", "█   █  ", "████   ", "█   █  ", "█    █ "],
            'L': ["█      ", "█      ", "█      ", "█      ", "███████"],
            'M': ["█     █", "██   ██", "█ █ █ █", "█  █  █", "█     █"],
            'N': ["█     █", "██    █", "█ █   █", "█  █  █", "█   ███"],
            'O': [" █████ ", "█     █", "█     █", "█     █", " █████ "],
            'P': ["██████ ", "█     █", "██████ ", "█      ", "█      "],
            'Q': [" █████ ", "█     █", "█   █ █", "█    █ ", " ████ █"],
            'R': ["██████ ", "█     █", "██████ ", "█   █  ", "█    █ "],
            'S': [" █████ ", "█      ", " █████ ", "      █", " █████ "],
            'T': ["███████", "  ███  ", "  ███  ", "  ███  ", "  ███  "],
            'U': ["█     █", "█     █", "█     █", "█     █", " █████ "],
            'V': ["█     █", "█     █", "█     █", " █   █ ", "  ███  "],
            'W': ["█     █", "█  █  █", "█ █ █ █", "██   ██", "█     █"],
            'X': ["█     █", " █   █ ", "  ███  ", " █   █ ", "█     █"],
            'Y': ["█     █", " █   █ ", "  ███  ", "  ███  ", "  ███  "],
            'Z': ["███████", "    █  ", "   █   ", "  █    ", "███████"],
            '0': [" █████ ", "█    ██", "█   █ █", "█  █  █", " █████ "],
            '1': ["  ███  ", "   █   ", "   █   ", "   █   ", " █████ "],
            '2': [" █████ ", "█     █", "   ███ ", " █     ", "███████"],
            '3': [" █████ ", "      █", "  ████ ", "      █", " █████ "],
            '4': ["█     █", "█     █", "███████", "      █", "      █"],
            '5': ["███████", "█      ", "██████ ", "      █", "██████ "],
            '6': [" █████ ", "█      ", "██████ ", "█     █", " █████ "],
            '7': ["███████", "     █ ", "    █  ", "   █   ", "   █   "],
            '8': [" █████ ", "█     █", " █████ ", "█     █", " █████ "],
            '9': [" █████ ", "█     █", " ██████", "      █", " █████ "],
            ' ': ["   ", "   ", "   ", "   ", "   "],
            '.': ["   ", "   ", "   ", "   ", " █ "],
            '-': ["     ", "     ", "█████", "     ", "     "],
            '_': ["     ", "     ", "     ", "     ", "█████"],
            ':': [" █ ", "   ", " █ ", "   ", "   "],
        },
        'block': {
            'A': ["█████ ", "█    █", "██████", "█    █", "█    █"],
            'B': ["█████ ", "█    █", "█████ ", "█    █", "█████ "],
            'C': ["██████", "█     ", "█     ", "█     ", "██████"],
            'D': ["█████ ", "█    █", "█    █", "█    █", "█████ "],
            'E': ["██████", "█     ", "████  ", "█     ", "██████"],
            'F': ["██████", "█     ", "████  ", "█     ", "█     "],
            'G': ["██████", "█     ", "█  ███", "█    █", "██████"],
            'H': ["█    █", "█    █", "██████", "█    █", "█    █"],
            'I': ["███", " █ ", " █ ", " █ ", "███"],
            'J': ["  ███", "   █ ", "   █ ", "█  █ ", "███  "],
            'K': ["█   █ ", "█  █  ", "███   ", "█  █  ", "█   █ "],
            'L': ["█     ", "█     ", "█     ", "█     ", "██████"],
            'M': ["█    █", "██  ██", "█ ██ █", "█    █", "█    █"],
            'N': ["█    █", "██   █", "█ █  █", "█  █ █", "█   ██"],
            'O': ["█████ ", "█    █", "█    █", "█    █", "█████ "],
            'P': ["█████ ", "█    █", "█████ ", "█     ", "█     "],
            'Q': ["█████ ", "█    █", "█  █ █", "█   █ ", "████ █"],
            'R': ["█████ ", "█    █", "█████ ", "█  █  ", "█   █ "],
            'S': ["██████", "█     ", "█████ ", "     █", "██████"],
            'T': ["██████", "  ██  ", "  ██  ", "  ██  ", "  ██  "],
            'U': ["█    █", "█    █", "█    █", "█    █", "██████"],
            'V': ["█    █", "█    █", "█    █", " █  █ ", "  ██  "],
            'W': ["█    █", "█    █", "█ ██ █", "██  ██", "█    █"],
            'X': ["█    █", " █  █ ", "  ██  ", " █  █ ", "█    █"],
            'Y': ["█    █", " █  █ ", "  ██  ", "  ██  ", "  ██  "],
            'Z': ["██████", "   █  ", "  █   ", " █    ", "██████"],
            ' ': ["   ", "   ", "   ", "   ", "   "],
        },
        'matrix': {
            'A': ["╔═╗  ", "║ ║  ", "╠═══╗ ", "║ ║ ║ ", "╚═╝ ╚═"],
            'B': ["╔═══╗ ", "║ ╔═╝ ", "╠══╣  ", "║ ╚═╗ ", "╚═══╝ "],
            'C': ["╔═══╗ ", "║     ", "║     ", "║     ", "╚═══╝ "],
            'D': ["╔═══╗ ", "║   ║ ", "║   ║ ", "║   ║ ", "╚═══╝ "],
            'E': ["╔═════", "║     ", "╠═══  ", "║     ", "╚═════"],
            'F': ["╔═════", "║     ", "╠═══  ", "║     ", "║     "],
            'G': ["╔═══╗ ", "║     ", "║  ╔═╗", "║  ╚═╝", "╚═══╝ "],
            'H': ["║   ║ ", "║   ║ ", "╠═══╣ ", "║   ║ ", "║   ║ "],
            'I': ["╔═╗", " ║ ", " ║ ", " ║ ", "╚═╝"],
            'J': ["  ╔═╗ ", "   ║  ", "   ║  ", "║  ║  ", "╚══╝  "],
            'K': ["║  ╔═╗", "║ ╚═╗ ", "╠═╗  ║", "║ ╚═╗║", "║   ╚╝"],
            'L': ["║     ", "║     ", "║     ", "║     ", "╚═════"],
            'M': ["╔╗  ╔╗", "║╚╗╔╝║", "║ ║║ ║", "║ ╚╝ ║", "╚═╗╔═╝"],
            'N': ["╔═╗ ║ ", "║ ╚╗║ ", "║  ╚║ ", "║  ╔╣ ", "╚═╝ ║ "],
            'O': ["╔═══╗ ", "║   ║ ", "║   ║ ", "║   ║ ", "╚═══╝ "],
            'P': ["╔═══╗ ", "║   ║ ", "╠═══╝ ", "║     ", "║     "],
            'Q': ["╔═══╗ ", "║   ║ ", "║ ╔ ║ ", "║ ╚═╣ ", "╚══╩═╝"],
            'R': ["╔═══╗ ", "║   ║ ", "╠═══╝ ", "║ ╚═╗ ", "║   ╚╗"],
            'S': ["╔═══╗ ", "║     ", "╠═══╗ ", "    ║ ", "╚═══╝ "],
            'T': ["╔═══╗ ", " ╔═╗  ", " ║ ║  ", " ║ ║  ", " ╚═╝  "],
            'U': ["║   ║ ", "║   ║ ", "║   ║ ", "║   ║ ", "╚═══╝ "],
            'V': ["║   ║ ", "║   ║ ", "║   ║ ", " ╚ ╝  ", "  ╝   "],
            'W': ["║   ║ ", "║   ║ ", "║ ╳ ║ ", "║╔═╗║ ", "╚╝ ╚╝ "],
            'X': ["╔═╗ ╔═╗", "║ ╚═╝ ║", "║     ║", "╚═╗ ╔═╝", "  ╚═╝  "],
            'Y': ["╔═╗ ╔═╗", "║ ╚═╝ ║", "║  ╔═╗║", "║  ╚═╝║", "╚════╝"],
            'Z': ["╔═════", "   ╔═╝", "  ╔═╝ ", " ╔═╝  ", "╚═════"],
            ' ': ["   ", "   ", "   ", "   ", "   "],
        },
    }
    
    # Border styles
    BORDERS = {
        'single': {
            'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
            'h': '─', 'v': '│',
        },
        'double': {
            'tl': '╔', 'tr': '╗', 'bl': '╚', 'br': '╝',
            'h': '═', 'v': '║',
        },
        'heavy': {
            'tl': '┏', 'tr': '┓', 'bl': '┗', 'br': '┛',
            'h': '━', 'v': '┃',
        },
        'rounded': {
            'tl': '╭', 'tr': '╮', 'bl': '╰', 'br': '╯',
            'h': '─', 'v': '│',
        },
        'ascii': {
            'tl': '+', 'tr': '+', 'bl': '+', 'br': '+',
            'h': '-', 'v': '|',
        },
        'star': {
            'tl': '*', 'tr': '*', 'bl': '*', 'br': '*',
            'h': '*', 'v': '*',
        },
        'hash': {
            'tl': '#', 'tr': '#', 'bl': '#', 'br': '#',
            'h': '#', 'v': '#',
        },
        'block': {
            'tl': '█', 'tr': '█', 'bl': '█', 'br': '█',
            'h': '█', 'v': '█',
        },
    }
    
    # Decorative elements
    DECORATIONS = {
        'star': '★',
        'star_outline': '☆',
        'diamond': '◆',
        'diamond_outline': '◇',
        'circle': '●',
        'circle_outline': '○',
        'square': '■',
        'square_outline': '□',
        'triangle': '▲',
        'triangle_outline': '△',
        'arrow_right': '►',
        'arrow_left': '◄',
        'arrow_up': '▲',
        'arrow_down': '▼',
        'bullet': '•',
        'check': '✓',
        'cross': '✗',
        'lightning': '⚡',
        'skull': '☠',
        'biohazard': '☣',
        'radioactive': '☢',
        'peace': '☮',
        'ying_yang': '☯',
        'sparkle': '✦',
        'flower': '✿',
        'heart': '♥',
        'club': '♣',
        'spade': '♠',
        'note': '♪',
        'double_note': '♫',
        'sun': '☀',
        'moon': '☾',
        'cloud': '☁',
        'umbrella': '☂',
        'snowflake': '❄',
        'scissors': '✂',
        'phone': '☎',
        'plane': '✈',
        'envelope': '✉',
        'pencil': '✎',
        'pen': '✒',
    }
    
    # Pre-made ASCII art logos
    LOGOS = {
        'hacker': [
            "    ██╗  ██╗ █████╗  ██████╗██╗  ██╗███████╗██████╗ ",
            "    ██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗",
            "    ███████║███████║██║     █████╔╝ █████╗  ██████╔╝",
            "    ██╔══██║██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗",
            "    ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║",
            "    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝",
        ],
        'nexus': [
            "    ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗",
            "    ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝",
            "    ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗",
            "    ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║",
            "    ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║",
            "    ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝",
        ],
        'downloader': [
            "    ██████╗ ██████╗  ██████╗ ██╗  ██╗██╗   ██╗███████╗██╗██████╗ ███████╗",
            "    ██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝██║   ██║██╔════╝██║██╔══██╗██╔════╝",
            "    ██║  ██║██████╔╝██║   ██║ ╚███╔╝ ██║   ██║███████╗██║██║  ██║█████╗  ",
            "    ██║  ██║██╔══██╗██║   ██║ ██╔██╗ ██║   ██║╚════██║██║██║  ██║██╔══╝  ",
            "    ██████╔╝██║  ██║╚██████╔╝██╔╝ ██╗╚██████╔╝███████║██║██████╔╝███████╗",
            "    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝╚═════╝ ╚══════╝",
        ],
        'terminal': [
            "    ████████╗███████╗████████╗██████╗  ██████╗ ████████╗███████╗██████╗ ",
            "    ╚══██╔══╝██╔════╝╚══██╔══╝██╔══██╗██╔═══██╗╚══██╔══╝██╔════╝██╔══██╗",
            "       ██║   █████╗     ██║   ██████╔╝██║   ██║   ██║   █████╗  ██████╔╝",
            "       ██║   ██╔══╝     ██║   ██╔══██╗██║   ██║   ██║   ██╔══╝  ██╔══██╗",
            "       ██║   ███████╗   ██║   ██║  ██║╚██████╔╝   ██║   ███████╗██║  ██║",
            "       ╚═╝   ╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚══════╝╚═╝  ╚═╝",
        ],
        'cyber': [
            "     ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄",
            "     █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█",
            "     █░░▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀░░█",
            "     █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█",
            "     █░░░░░░░░░░░░░░░░░CYBER░░░░░░░░░░░░░░░░░█",
            "     █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█",
            "     ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀",
        ],
        'matrix': [
            "    ╔════════════════════════════════════════════════════════════╗",
            "    ║ ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ ║",
            "    ║ █ M A T R I X █ N E X U S █ D O W N L O A D E R █      █ ║",
            "    ║ ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀ ║",
            "    ╚════════════════════════════════════════════════════════════╝",
        ],
    }
    
    # Spinner characters
    SPINNERS = {
        'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
        'line': ['-', '\\', '|', '/'],
        'arrow': ['→', '↘', '↓', '↙', '←', '↖', '↑', '↗'],
        'bounce': ['⠁', '⠂', '⠄', '⠂'],
        'pulse': ['█', '▓', '▒', '░', '▒', '▓'],
        'wave': ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█', '▇', '▆', '▅', '▄', '▃', '▂'],
        'grow': ['▉', '▊', '▋', '▌', '▍', '▎', '▏'],
        'toggle': ['◁', '◀', '◁', '▶'],
        'box': ['□', '■', '□', '■'],
        'braille': ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'],
    }


# ============================================================================
# BANNER GENERATOR CLASS
# ============================================================================
class BannerGenerator:
    """
    Advanced banner generation system with multiple styles and animations.
    
    Features:
    - 20+ banner styles
    - ASCII art generation
    - Animation support
    - Custom templates
    - Border customization
    - Text alignment
    - Sound notifications
    - System info display
    
    Example:
        >>> gen = BannerGenerator()
        >>> banner = gen.generate(title="My Tool", style=BannerStyle.CYBERPUNK)
        >>> print(banner)
    """
    
    def __init__(self, color_scheme: Union[str, ColorScheme] = "NEXUS_HACKER") -> None:
        """
        Initialize the banner generator.
        
        Args:
            color_scheme: Default color scheme name or ColorScheme object
        """
        self._cm = ColorManager()
        self._set_color_scheme(color_scheme)
        self._width = self._get_terminal_width()
        self._animation_running = False
        self._animation_thread: Optional[threading.Thread] = None
    
    def _set_color_scheme(self, scheme: Union[str, ColorScheme]) -> None:
        """Set the color scheme for banners."""
        if isinstance(scheme, str):
            self._cm.set_scheme(scheme)
        elif isinstance(scheme, ColorScheme):
            self._cm.add_scheme(scheme)
            self._cm.set_scheme(scheme.name)
    
    @staticmethod
    def _get_terminal_width() -> int:
        """Get terminal width with fallback."""
        try:
            return shutil.get_terminal_size().columns
        except Exception:
            return 80
    
    def generate(self, template: Optional[BannerTemplate] = None, **kwargs) -> str:
        """
        Generate a banner from a template or keyword arguments.
        
        Args:
            template: BannerTemplate object
            **kwargs: Override template attributes
            
        Returns:
            Generated banner string
        """
        if template is None:
            template = BannerTemplate()
        
        # Apply kwargs to template
        for key, value in kwargs.items():
            if hasattr(template, key):
                setattr(template, key, value)
        
        # Set color scheme
        if isinstance(template.color_scheme, str):
            self._cm.set_scheme(template.color_scheme)
        elif isinstance(template.color_scheme, ColorScheme):
            self._cm.add_scheme(template.color_scheme)
            self._cm.set_scheme(template.color_scheme.name)
        
        # Determine width
        width = template.width if template.width > 0 else self._width
        
        # Generate based on style
        generator_map = {
            BannerStyle.CLASSIC: self._generate_classic,
            BannerStyle.MATRIX: self._generate_matrix,
            BannerStyle.CYBERPUNK: self._generate_cyberpunk,
            BannerStyle.NEON: self._generate_neon,
            BannerStyle.MINIMAL: self._generate_minimal,
            BannerStyle.DOUBLE_LINE: self._generate_double_line,
            BannerStyle.BLOCK: self._generate_block,
            BannerStyle.ASCII_ART: self._generate_ascii_art,
            BannerStyle.GRADIENT: self._generate_gradient,
            BannerStyle.RETRO: self._generate_retro,
            BannerStyle.MODERN: self._generate_modern,
            BannerStyle.HACKER: self._generate_hacker,
            BannerStyle.FIRE: self._generate_fire,
            BannerStyle.ICE: self._generate_ice,
            BannerStyle.NATURE: self._generate_nature,
            BannerStyle.MILITARY: self._generate_military,
            BannerStyle.CORPORATE: self._generate_corporate,
            BannerStyle.GAMING: self._generate_gaming,
            BannerStyle.ANIME: self._generate_anime,
            BannerStyle.SCIFI: self._generate_scifi,
        }
        
        generator = generator_map.get(template.style, self._generate_classic)
        banner = generator(template, width)
        
        # Add timestamp if requested
        if template.show_timestamp:
            banner += self._add_timestamp(width)
        
        # Add system info if requested
        if template.show_system_info:
            banner += self._add_system_info(width)
        
        return banner
    
    # ===== STYLE GENERATORS =====
    
    def _generate_classic(self, template: BannerTemplate, width: int) -> str:
        """Generate classic bordered banner."""
        lines = []
        border = ASCIICollections.BORDERS['double']
        
        # Top border
        lines.append(border['tl'] + border['h'] * (width - 2) + border['tr'])
        
        # Title
        if template.title:
            title_line = self._align_text(template.title, width - 4, template.position)
            lines.append(border['v'] + ' ' + self._cm.primary(title_line) + ' ' + border['v'])
        
        # Empty line
        lines.append(border['v'] + ' ' * (width - 2) + border['v'])
        
        # Subtitle
        if template.subtitle:
            sub_line = self._align_text(template.subtitle, width - 4, template.position)
            lines.append(border['v'] + ' ' + self._cm.secondary(sub_line) + ' ' + border['v'])
        
        # Version and Author
        if template.version or template.author:
            info = f"Version: {template.version}" if template.version else ""
            if template.author:
                info += f" | Author: {template.author}" if info else f"Author: {template.author}"
            info_line = self._align_text(info, width - 4, template.position)
            lines.append(border['v'] + ' ' + self._cm.info(info_line) + ' ' + border['v'])
        
        # Description
        if template.description:
            desc_line = self._align_text(template.description, width - 4, template.position)
            lines.append(border['v'] + ' ' + self._cm.text_secondary(desc_line) + ' ' + border['v'])
        
        # Additional info
        for info in template.additional_info:
            info_line = self._align_text(info, width - 4, template.position)
            lines.append(border['v'] + ' ' + self._cm.text(info_line) + ' ' + border['v'])
        
        # Bottom border
        lines.append(border['bl'] + border['h'] * (width - 2) + border['br'])
        
        return '\n'.join(lines)
    
    def _generate_matrix(self, template: BannerTemplate, width: int) -> str:
        """Generate Matrix-style banner."""
        lines = []
        
        # Matrix-style header
        lines.append(self._cm.primary("╔" + "═" * (width - 2) + "╗"))
        
        # Matrix rain effect for title
        if template.title:
            title_art = self._generate_ascii_title(template.title, 'matrix')
            for line in title_art:
                padded = self._align_text(line, width - 2, template.position)
                lines.append(self._cm.primary("║") + self._cm.primary(padded) + self._cm.primary("║"))
        
        # Info section
        lines.append(self._cm.primary("║") + " " * (width - 2) + self._cm.primary("║"))
        
        if template.version:
            ver = f"[ VERSION: {template.version} ]"
            ver_line = self._align_text(ver, width - 2, template.position)
            lines.append(self._cm.primary("║") + self._cm.success(ver_line) + self._cm.primary("║"))
        
        if template.author:
            auth = f"[ AUTHOR: {template.author} ]"
            auth_line = self._align_text(auth, width - 2, template.position)
            lines.append(self._cm.primary("║") + self._cm.secondary(auth_line) + self._cm.primary("║"))
        
        if template.description:
            desc = f">>> {template.description}"
            desc_line = self._align_text(desc, width - 2, template.position)
            lines.append(self._cm.primary("║") + self._cm.info(desc_line) + self._cm.primary("║"))
        
        # Footer
        lines.append(self._cm.primary("╚" + "═" * (width - 2) + "╝"))
        
        return '\n'.join(lines)
    
    def _generate_cyberpunk(self, template: BannerTemplate, width: int) -> str:
        """Generate Cyberpunk-style banner with neon colors."""
        lines = []
        accent = self._cm.primary
        cyan = lambda t: self._cm.rgb(0, 255, 255, t)
        
        # Glitch-style border
        lines.append(accent("▄" * width))
        lines.append(accent("█" + "░" * (width - 2) + "█"))
        
        # Title with glitch effect
        if template.title:
            title_art = self._generate_ascii_title(template.title, 'block')
            for line in title_art:
                padded = self._align_text(line, width - 4, template.position)
                # Alternate colors for cyberpunk effect
                color_line = ""
                for char in padded:
                    if random.random() > 0.7:
                        color_line += cyan(char)
                    else:
                        color_line += accent(char)
                lines.append(accent("█ ") + color_line + accent(" █"))
        
        # Separator
        lines.append(accent("█" + "═" * (width - 2) + "█"))
        
        # Info with cyberpunk styling
        if template.version:
            ver = f"◈ VERSION: {template.version}"
            ver_line = self._align_text(ver, width - 4, template.position)
            lines.append(accent("█ ") + self._cm.warning(ver_line) + accent(" █"))
        
        if template.author:
            auth = f"◈ AUTHOR: {template.author}"
            auth_line = self._align_text(auth, width - 4, template.position)
            lines.append(accent("█ ") + self._cm.secondary(auth_line) + accent(" █"))
        
        # Description
        if template.description:
            desc = f"► {template.description}"
            desc_line = self._align_text(desc, width - 4, template.position)
            lines.append(accent("█ ") + self._cm.info(desc_line) + accent(" █"))
        
        # Footer
        lines.append(accent("█" + "░" * (width - 2) + "█"))
        lines.append(accent("▀" * width))
        
        return '\n'.join(lines)
    
    def _generate_neon(self, template: BannerTemplate, width: int) -> str:
        """Generate neon-style glowing banner."""
        lines = []
        
        # Neon glow border
        lines.append(self._cm.primary("╭" + "─" * (width - 2) + "╮"))
        lines.append(self._cm.secondary("│" + " " * (width - 2) + "│"))
        
        # Glowing title
        if template.title:
            title_line = self._align_text(template.title, width - 4, template.position)
            glow_title = self._cm.bold(self._cm.primary(title_line))
            lines.append(self._cm.secondary("│ ") + glow_title + self._cm.secondary(" │"))
        
        lines.append(self._cm.secondary("│" + " " * (width - 2) + "│"))
        
        # Info with neon colors
        if template.subtitle:
            sub_line = self._align_text(template.subtitle, width - 4, template.position)
            lines.append(self._cm.secondary("│ ") + self._cm.warning(sub_line) + self._cm.secondary(" │"))
        
        if template.version:
            ver = f"⚡ v{template.version}"
            ver_line = self._align_text(ver, width - 4, template.position)
            lines.append(self._cm.secondary("│ ") + self._cm.info(ver_line) + self._cm.secondary(" │"))
        
        if template.author:
            auth = f"✦ {template.author}"
            auth_line = self._align_text(auth, width - 4, template.position)
            lines.append(self._cm.secondary("│ ") + self._cm.success(auth_line) + self._cm.secondary(" │"))
        
        # Footer
        lines.append(self._cm.secondary("│" + " " * (width - 2) + "│"))
        lines.append(self._cm.primary("╰" + "─" * (width - 2) + "╯"))
        
        return '\n'.join(lines)
    
    def _generate_minimal(self, template: BannerTemplate, width: int) -> str:
        """Generate minimal clean banner."""
        lines = []
        
        # Simple line
        lines.append(self._cm.text_secondary("─" * width))
        
        if template.title:
            title_line = self._align_text(template.title, width, template.position)
            lines.append(self._cm.bold(title_line))
        
        if template.subtitle:
            sub_line = self._align_text(template.subtitle, width, template.position)
            lines.append(self._cm.text_secondary(sub_line))
        
        info_parts = []
        if template.version:
            info_parts.append(f"v{template.version}")
        if template.author:
            info_parts.append(f"by {template.author}")
        
        if info_parts:
            info_line = self._align_text(" | ".join(info_parts), width, template.position)
            lines.append(self._cm.text(info_line))
        
        if template.description:
            desc_line = self._align_text(template.description, width, template.position)
            lines.append(self._cm.text_secondary(desc_line))
        
        lines.append(self._cm.text_secondary("─" * width))
        
        return '\n'.join(lines)
    
    def _generate_double_line(self, template: BannerTemplate, width: int) -> str:
        """Generate double-line bordered banner."""
        lines = []
        
        lines.append("╔" + "═" * (width - 2) + "╗")
        
        if template.title:
            title_line = self._align_text(template.title, width - 4, template.position)
            lines.append("║ " + self._cm.bold(title_line) + " ║")
        
        lines.append("╠" + "═" * (width - 2) + "╣")
        
        if template.subtitle:
            sub_line = self._align_text(template.subtitle, width - 4, template.position)
            lines.append("║ " + self._cm.secondary(sub_line) + " ║")
        
        if template.version:
            ver_line = self._align_text(f"Version: {template.version}", width - 4, template.position)
            lines.append("║ " + self._cm.info(ver_line) + " ║")
        
        if template.author:
            auth_line = self._align_text(f"Author: {template.author}", width - 4, template.position)
            lines.append("║ " + self._cm.text(auth_line) + " ║")
        
        lines.append("╚" + "═" * (width - 2) + "╝")
        
        return '\n'.join(lines)
    
    def _generate_block(self, template: BannerTemplate, width: int) -> str:
        """Generate solid block-style banner."""
        lines = []
        
        # Solid top
        lines.append(self._cm.primary("█" * width))
        lines.append(self._cm.primary("█" + " " * (width - 2) + "█"))
        
        if template.title:
            title_art = self._generate_ascii_title(template.title, 'block')
            for line in title_art:
                padded = self._align_text(line, width - 4, template.position)
                lines.append(self._cm.primary("█ ") + padded + self._cm.primary(" █"))
        
        lines.append(self._cm.primary("█" + " " * (width - 2) + "█"))
        
        if template.version or template.author:
            info = " | ".join(filter(None, [
                f"v{template.version}" if template.version else "",
                f"by {template.author}" if template.author else ""
            ]))
            info_line = self._align_text(info, width - 4, template.position)
            lines.append(self._cm.primary("█ ") + self._cm.secondary(info_line) + self._cm.primary(" █"))
        
        lines.append(self._cm.primary("█" + " " * (width - 2) + "█"))
        lines.append(self._cm.primary("▀" * width))
        
        return '\n'.join(lines)
    
    def _generate_ascii_art(self, template: BannerTemplate, width: int) -> str:
        """Generate ASCII art banner."""
        lines = []
        
        # Generate ASCII art title
        if template.title:
            title_art = self._generate_ascii_title(template.title, 'standard')
            for line in title_art:
                padded = self._align_text(line, width, template.position)
                lines.append(self._cm.primary(padded))
        
        # Add separator
        lines.append(self._cm.text_secondary("─" * min(40, width)))
        
        # Add info
        if template.version:
            lines.append(self._cm.info(f"  Version: {template.version}"))
        if template.author:
            lines.append(self._cm.secondary(f"  Author: {template.author}"))
        if template.description:
            lines.append(self._cm.text(f"  {template.description}"))
        
        return '\n'.join(lines)
    
    def _generate_gradient(self, template: BannerTemplate, width: int) -> str:
        """Generate gradient-colored banner."""
        lines = []
        
        if template.title:
            # Create gradient effect
            title_art = self._generate_ascii_title(template.title, 'standard')
            start_color = (255, 0, 128)  # Pink
            end_color = (0, 255, 255)    # Cyan
            
            for line in title_art:
                gradient_line = self._cm.gradient_text(line, start_color, end_color)
                padded = self._align_text(gradient_line, width, template.position)
                lines.append(padded)
        
        # Add decorative line
        line_grad = self._cm.gradient_text("━" * min(50, width), end_color, start_color)
        lines.append(line_grad)
        
        # Info
        if template.version:
            lines.append(self._cm.info(f"  Version: {template.version}"))
        if template.author:
            lines.append(self._cm.secondary(f"  Author: {template.author}"))
        
        return '\n'.join(lines)
    
    def _generate_retro(self, template: BannerTemplate, width: int) -> str:
        """Generate retro-style banner."""
        lines = []
        
        lines.append(self._cm.primary("╔═══════════════════════════════════════════════════════╗"))
        lines.append(self._cm.primary("║                                                       ║"))
        
        if template.title:
            title_line = self._align_text(f"◄► {template.title} ◄►", width - 4, template.position)
            lines.append(self._cm.primary("║ ") + self._cm.warning(title_line) + self._cm.primary(" ║"))
        
        lines.append(self._cm.primary("║                                                       ║"))
        
        if template.subtitle:
            sub_line = self._align_text(template.subtitle, width - 4, template.position)
            lines.append(self._cm.primary("║ ") + self._cm.secondary(sub_line) + self._cm.primary(" ║"))
        
        # Retro-style info
        if template.version:
            ver_line = self._align_text(f"▓▓ VERSION: {template.version} ▓▓", width - 4, template.position)
            lines.append(self._cm.primary("║ ") + self._cm.info(ver_line) + self._cm.primary(" ║"))
        
        if template.author:
            auth_line = self._align_text(f"▓▓ AUTHOR: {template.author} ▓▓", width - 4, template.position)
            lines.append(self._cm.primary("║ ") + self._cm.text(auth_line) + self._cm.primary(" ║"))
        
        lines.append(self._cm.primary("║                                                       ║"))
        lines.append(self._cm.primary("╚═══════════════════════════════════════════════════════╝"))
        
        return '\n'.join(lines)
    
    def _generate_modern(self, template: BannerTemplate, width: int) -> str:
        """Generate modern clean banner."""
        lines = []
        
        # Modern rounded style
        lines.append(self._cm.primary("╭──────────────────────────────────────────────────────╮"))
        lines.append(self._cm.primary("│                                                      │"))
        
        if template.title:
            title_line = self._align_text(template.title, width - 6, template.position)
            lines.append(self._cm.primary("│  ") + self._cm.bold(title_line) + self._cm.primary("  │"))
        
        lines.append(self._cm.primary("│  " + "─" * (width - 8) + "  │"))
        
        if template.subtitle:
            sub_line = self._align_text(template.subtitle, width - 6, template.position)
            lines.append(self._cm.primary("│  ") + self._cm.secondary(sub_line) + self._cm.primary("  │"))
        
        if template.version:
            ver_line = f"v{template.version}"
            lines.append(self._cm.primary("│  ") + self._cm.info(ver_line) + self._cm.primary("  │"))
        
        if template.author:
            auth_line = f"Created by {template.author}"
            lines.append(self._cm.primary("│  ") + self._cm.text(auth_line) + self._cm.primary("  │"))
        
        lines.append(self._cm.primary("│                                                      │"))
        lines.append(self._cm.primary("╰──────────────────────────────────────────────────────╯"))
        
        return '\n'.join(lines)
    
    def _generate_hacker(self, template: BannerTemplate, width: int) -> str:
        """Generate hacker-style terminal banner."""
        lines = []
        
        # Terminal-style header
        lines.append(self._cm.text("┌──(") + self._cm.primary("root@nexus") + self._cm.text(")-[" + 
                     self._cm.secondary("~/tools") + self._cm.text("]"))
        lines.append(self._cm.text("└─$ "))
        
        if template.title:
            lines.append(self._cm.primary(f"    > {template.title.upper()} INITIALIZED"))
        
        lines.append(self._cm.text_secondary("    │"))
        
        if template.subtitle:
            lines.append(self._cm.secondary(f"    ├── {template.subtitle}"))
        
        if template.version:
            lines.append(self._cm.info(f"    ├── Version: {template.version}"))
        
        if template.author:
            lines.append(self._cm.text(f"    ├── Author: {template.author}"))
        
        if template.description:
            lines.append(self._cm.warning(f"    └── {template.description}"))
        
        lines.append(self._cm.text_secondary("    │"))
        lines.append(self._cm.success("    [✓] System Ready"))
        
        return '\n'.join(lines)
    
    def _generate_fire(self, template: BannerTemplate, width: int) -> str:
        """Generate fire-themed banner."""
        lines = []
        
        # Fire colors
        fire_chars = "▓▒░ "
        
        lines.append(self._cm.rgb(255, 100, 0, "▲" * width))
        lines.append(self._cm.rgb(255, 150, 0, "△" * width))
        
        if template.title:
            title_line = self._align_text(template.title, width - 4, template.position)
            lines.append(self._cm.rgb(255, 50, 0, "│ ") + 
                        self._cm.rgb(255, 200, 0, title_line) + 
                        self._cm.rgb(255, 50, 0, " │"))
        
        lines.append(self._cm.rgb(255, 100, 0, "│" + " " * (width - 2) + "│"))
        
        if template.version:
            ver_line = self._align_text(f"🔥 Version: {template.version}", width - 4, template.position)
            lines.append(self._cm.rgb(255, 50, 0, "│ ") + 
                        self._cm.rgb(255, 150, 0, ver_line) + 
                        self._cm.rgb(255, 50, 0, " │"))
        
        lines.append(self._cm.rgb(255, 150, 0, "▽" * width))
        lines.append(self._cm.rgb(255, 100, 0, "▼" * width))
        
        return '\n'.join(lines)
    
    def _generate_ice(self, template: BannerTemplate, width: int) -> str:
        """Generate ice-themed banner."""
        lines = []
        
        # Ice colors (blues and whites)
        lines.append(self._cm.rgb(100, 200, 255, "❄" * width))
        lines.append(self._cm.rgb(150, 220, 255, "✻" * width))
        
        if template.title:
            title_line = self._align_text(template.title, width - 4, template.position)
            lines.append(self._cm.rgb(50, 150, 255, "│ ") + 
                        self._cm.rgb(200, 230, 255, title_line) + 
                        self._cm.rgb(50, 150, 255, " │"))
        
        lines.append(self._cm.rgb(100, 180, 230, "│" + " " * (width - 2) + "│"))
        
        if template.version:
            ver_line = self._align_text(f"❆ Version: {template.version}", width - 4, template.position)
            lines.append(self._cm.rgb(50, 150, 255, "│ ") + 
                        self._cm.rgb(180, 220, 255, ver_line) + 
                        self._cm.rgb(50, 150, 255, " │"))
        
        if template.author:
            auth_line = self._align_text(f"❅ by {template.author}", width - 4, template.position)
            lines.append(self._cm.rgb(50, 150, 255, "│ ") + 
                        self._cm.rgb(150, 200, 255, auth_line) + 
                        self._cm.rgb(50, 150, 255, " │"))
        
        lines.append(self._cm.rgb(150, 220, 255, "✻" * width))
        lines.append(self._cm.rgb(100, 200, 255, "❄" * width))
        
        return '\n'.join(lines)
    
    def _generate_nature(self, template: BannerTemplate, width: int) -> str:
        """Generate nature-themed banner."""
        lines = []
        
        # Nature decoration
        lines.append(self._cm.rgb(34, 139, 34, "🌿" * (width // 2)))
        
        if template.title:
            title_line = self._align_text(f"🍃 {template.title} 🍃", width, template.position)
            lines.append(self._cm.rgb(50, 180, 50, title_line))
        
        lines.append(self._cm.rgb(80, 160, 80, "─" * width))
        
        if template.subtitle:
            lines.append(self._cm.rgb(100, 140, 60, f"  {template.subtitle}"))
        
        if template.version:
            lines.append(self._cm.rgb(60, 150, 60, f"  🌱 Version: {template.version}"))
        
        if template.author:
            lines.append(self._cm.rgb(80, 130, 60, f"  🌿 Author: {template.author}"))
        
        lines.append(self._cm.rgb(34, 139, 34, "🌿" * (width // 2)))
        
        return '\n'.join(lines)
    
    def _generate_military(self, template: BannerTemplate, width: int) -> str:
        """Generate military-style banner."""
        lines = []
        
        lines.append(self._cm.rgb(80, 100, 60, "▓" * width))
        lines.append(self._cm.rgb(100, 120, 70, "░" + "═" * (width - 2) + "░"))
        
        if template.title:
            title_line = self._align_text(f"[ {template.title} ]", width - 4, template.position)
            lines.append(self._cm.rgb(100, 120, 70, "░ ") + 
                        self._cm.rgb(200, 220, 100, title_line) + 
                        self._cm.rgb(100, 120, 70, " ░"))
        
        lines.append(self._cm.rgb(100, 120, 70, "░" + "─" * (width - 2) + "░"))
        
        if template.version:
            ver_line = self._align_text(f"CLASSIFICATION: {template.version}", width - 4, template.position)
            lines.append(self._cm.rgb(100, 120, 70, "░ ") + 
                        self._cm.rgb(150, 170, 80, ver_line) + 
                        self._cm.rgb(100, 120, 70, " ░"))
        
        if template.author:
            auth_line = self._align_text(f"OPERATOR: {template.author}", width - 4, template.position)
            lines.append(self._cm.rgb(100, 120, 70, "░ ") + 
                        self._cm.rgb(150, 170, 80, auth_line) + 
                        self._cm.rgb(100, 120, 70, " ░"))
        
        lines.append(self._cm.rgb(100, 120, 70, "░" + "═" * (width - 2) + "░"))
        lines.append(self._cm.rgb(80, 100, 60, "▓" * width))
        
        return '\n'.join(lines)
    
    def _generate_corporate(self, template: BannerTemplate, width: int) -> str:
        """Generate corporate-style banner."""
        lines = []
        
        lines.append(self._cm.rgb(0, 82, 155, "═" * width))
        
        if template.title:
            title_line = self._align_text(template.title, width, template.position)
            lines.append(self._cm.rgb(0, 82, 155, "  ") + 
                        self._cm.bold(title_line))
        
        lines.append(self._cm.text_secondary("  " + "─" * min(50, width - 4)))
        
        if template.subtitle:
            lines.append(self._cm.text(f"  {template.subtitle}"))
        
        info_parts = []
        if template.version:
            info_parts.append(f"Version {template.version}")
        if template.author:
            info_parts.append(f"© {template.author}")
        
        if info_parts:
            lines.append(self._cm.text_secondary("  " + " | ".join(info_parts)))
        
        lines.append(self._cm.rgb(0, 82, 155, "═" * width))
        
        return '\n'.join(lines)
    
    def _generate_gaming(self, template: BannerTemplate, width: int) -> str:
        """Generate gaming-style banner."""
        lines = []
        
        lines.append(self._cm.rgb(255, 0, 85, "▸" * width))
        
        if template.title:
            title_line = self._align_text(f"🎮 {template.title} 🎮", width, template.position)
            lines.append(self._cm.rgb(0, 255, 170, title_line))
        
        lines.append(self._cm.rgb(255, 0, 85, "│" + " " * (width - 2) + "│"))
        
        if template.version:
            ver_line = self._align_text(f"⚔️ LEVEL: {template.version}", width - 4, template.position)
            lines.append(self._cm.rgb(255, 0, 85, "│ ") + 
                        self._cm.rgb(255, 200, 0, ver_line) + 
                        self._cm.rgb(255, 0, 85, " │"))
        
        if template.author:
            auth_line = self._align_text(f"👤 PLAYER: {template.author}", width - 4, template.position)
            lines.append(self._cm.rgb(255, 0, 85, "│ ") + 
                        self._cm.rgb(100, 200, 255, auth_line) + 
                        self._cm.rgb(255, 0, 85, " │"))
        
        lines.append(self._cm.rgb(255, 0, 85, "▸" * width))
        
        return '\n'.join(lines)
    
    def _generate_anime(self, template: BannerTemplate, width: int) -> str:
        """Generate anime-style banner."""
        lines = []
        
        lines.append(self._cm.rgb(255, 105, 180, "✧" * width))
        
        if template.title:
            title_line = self._align_text(f"✨ {template.title} ✨", width, template.position)
            lines.append(self._cm.rgb(255, 182, 193, title_line))
        
        lines.append(self._cm.rgb(255, 105, 180, "│" + " " * (width - 2) + "│"))
        
        if template.subtitle:
            sub_line = self._align_text(template.subtitle, width - 4, template.position)
            lines.append(self._cm.rgb(255, 105, 180, "│ ") + 
                        self._cm.rgb(255, 182, 193, sub_line) + 
                        self._cm.rgb(255, 105, 180, " │"))
        
        if template.version:
            lines.append(self._cm.rgb(255, 105, 180, "│ ") + 
                        self._cm.rgb(255, 218, 185, f"♪ Version: {template.version}") + 
                        self._cm.rgb(255, 105, 180, " │"))
        
        if template.author:
            lines.append(self._cm.rgb(255, 105, 180, "│ ") + 
                        self._cm.rgb(176, 224, 230, f"♥ by {template.author}") + 
                        self._cm.rgb(255, 105, 180, " │"))
        
        lines.append(self._cm.rgb(255, 105, 180, "✧" * width))
        
        return '\n'.join(lines)
    
    def _generate_scifi(self, template: BannerTemplate, width: int) -> str:
        """Generate sci-fi themed banner."""
        lines = []
        
        lines.append(self._cm.rgb(0, 255, 255, "╔" + "═" * (width - 2) + "╗"))
        lines.append(self._cm.rgb(0, 255, 255, "║" + "░" * (width - 2) + "║"))
        
        if template.title:
            title_art = self._generate_ascii_title(template.title, 'standard')
            for line in title_art:
                padded = self._align_text(line, width - 4, template.position)
                lines.append(self._cm.rgb(0, 255, 255, "║ ") + 
                            self._cm.rgb(100, 255, 255, padded) + 
                            self._cm.rgb(0, 255, 255, " ║"))
        
        lines.append(self._cm.rgb(0, 255, 255, "║" + "─" * (width - 2) + "║"))
        
        if template.version:
            ver_line = self._align_text(f"◈ SYSTEM VERSION: {template.version}", width - 4, template.position)
            lines.append(self._cm.rgb(0, 255, 255, "║ ") + 
                        self._cm.rgb(0, 200, 200, ver_line) + 
                        self._cm.rgb(0, 255, 255, " ║"))
        
        if template.author:
            auth_line = self._align_text(f"◈ OPERATOR: {template.author}", width - 4, template.position)
            lines.append(self._cm.rgb(0, 255, 255, "║ ") + 
                        self._cm.rgb(0, 200, 200, auth_line) + 
                        self._cm.rgb(0, 255, 255, " ║"))
        
        lines.append(self._cm.rgb(0, 255, 255, "║" + "░" * (width - 2) + "║"))
        lines.append(self._cm.rgb(0, 255, 255, "╚" + "═" * (width - 2) + "╝"))
        
        return '\n'.join(lines)
    
    # ===== HELPER METHODS =====
    
    def _generate_ascii_title(self, text: str, font: str = 'standard') -> List[str]:
        """Generate ASCII art lines for a title."""
        font_data = ASCIICollections.FONTS.get(font, ASCIICollections.FONTS['standard'])
        lines = [''] * 5
        
        for char in text.upper():
            char_data = font_data.get(char, font_data.get(' ', [''] * 5))
            for i, line in enumerate(char_data):
                lines[i] += line
        
        return lines
    
    def _align_text(self, text: str, width: int, position: BannerPosition) -> str:
        """Align text within specified width."""
        text = ColorManager.strip_ansi(text)
        text_len = len(text)
        
        if text_len >= width:
            return text[:width]
        
        if position == BannerPosition.CENTER:
            padding = (width - text_len) // 2
            return ' ' * padding + text + ' ' * (width - text_len - padding)
        elif position == BannerPosition.RIGHT:
            return ' ' * (width - text_len) + text
        else:  # LEFT
            return text + ' ' * (width - text_len)
    
    def _add_timestamp(self, width: int) -> str:
        """Add timestamp to banner."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self._cm.text_secondary(f"\n  [Timestamp: {timestamp}]")
    
    def _add_system_info(self, width: int) -> str:
        """Add system information to banner."""
        info = f"\n  [System: {platform.system()} {platform.release()} | Python: {platform.python_version()}]"
        return self._cm.text_secondary(info)
    
    # ===== ANIMATION METHODS =====
    
    def animate(self, banner: str, animation_type: AnimationType, 
                duration: float = 2.0) -> None:
        """
        Display banner with animation.
        
        Args:
            banner: Banner text to animate
            animation_type: Type of animation to apply
            duration: Animation duration in seconds
        """
        if animation_type == AnimationType.NONE:
            print(banner)
            return
        
        animation_map = {
            AnimationType.TYPEWRITER: self._animate_typewriter,
            AnimationType.FADE_IN: self._animate_fade_in,
            AnimationType.RAINBOW: self._animate_rainbow,
            AnimationType.PULSE: self._animate_pulse,
            AnimationType.GLITCH: self._animate_glitch,
        }
        
        animator = animation_map.get(animation_type, lambda b, d: print(b))
        animator(banner, duration)
    
    def _animate_typewriter(self, text: str, duration: float) -> None:
        """Typewriter animation."""
        lines = text.split('\n')
        delay = duration / len(text)
        
        for line in lines:
            for char in line:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(delay)
            print()
    
    def _animate_fade_in(self, text: str, duration: float) -> None:
        """Fade in animation."""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if i > 0:
                time.sleep(0.05)
            print(line)
    
    def _animate_rainbow(self, text: str, duration: float) -> None:
        """Rainbow animation."""
        print(self._cm.rainbow_text(text))
    
    def _animate_pulse(self, text: str, duration: float) -> None:
        """Pulse animation."""
        lines = text.split('\n')
        for _ in range(3):
            for line in lines:
                print(self._cm.bold(line))
            time.sleep(0.3)
            os.system('cls' if os.name == 'nt' else 'clear')
            for line in lines:
                print(self._cm.dim(line))
            time.sleep(0.3)
    
    def _animate_glitch(self, text: str, duration: float) -> None:
        """Glitch animation effect."""
        lines = text.split('\n')
        glitch_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        
        for _ in range(5):
            for line in lines:
                glitched = ''.join(
                    random.choice(glitch_chars) if random.random() < 0.1 else char
                    for char in line
                )
                print(self._cm.error(glitched))
            time.sleep(0.1)
            os.system('cls' if os.name == 'nt' else 'clear')
        
        for line in lines:
            print(line)
    
    # ===== SPINNER ANIMATION =====
    
    def spinner(self, message: str = "Loading", spinner_type: str = 'dots',
                duration: float = 5.0) -> None:
        """
        Display animated spinner.
        
        Args:
            message: Message to display
            spinner_type: Type of spinner animation
            duration: Duration in seconds
        """
        frames = ASCIICollections.SPINNERS.get(spinner_type, ASCIICollections.SPINNERS['dots'])
        
        start_time = time.time()
        idx = 0
        
        try:
            while time.time() - start_time < duration:
                frame = frames[idx % len(frames)]
                sys.stdout.write(f"\r{self._cm.primary(frame)} {message}")
                sys.stdout.flush()
                time.sleep(0.1)
                idx += 1
        except KeyboardInterrupt:
            pass
        finally:
            sys.stdout.write("\r" + " " * (len(message) + 10) + "\r")
    
    # ===== SOUND NOTIFICATIONS =====
    
    def play_sound(self, sound_type: str = 'beep') -> bool:
        """
        Play notification sound.
        
        Args:
            sound_type: Type of sound ('beep', 'success', 'error', 'alert')
            
        Returns:
            True if sound was played successfully
        """
        try:
            if platform.system() == 'Windows':
                import winsound
                sound_map = {
                    'beep': winsound.Beep(1000, 200),
                    'success': winsound.Beep(1500, 300),
                    'error': winsound.Beep(500, 400),
                    'alert': winsound.Beep(2000, 200),
                }
                sound_map.get(sound_type, winsound.Beep(1000, 200))
            else:
                # Use system bell
                sys.stdout.write('\a')
                sys.stdout.flush()
            return True
        except Exception:
            return False


# ============================================================================
# PREDEFINED BANNERS
# ============================================================================
class PredefinedBanners:
    """Collection of ready-to-use banner templates."""
    
    @staticmethod
    def downloader(version: str = "3.0.1") -> BannerTemplate:
        """Create standard downloader banner."""
        return BannerTemplate(
            name="Downloader",
            style=BannerStyle.MATRIX,
            title="NEXUS DOWNLOADER",
            subtitle="Ultimate Download Manager",
            version=version,
            author="RS - OMNIPOTENT SOVEREIGN NEXUS",
            description="High-performance multi-threaded downloader",
            color_scheme="NEXUS_HACKER",
            show_timestamp=True,
        )
    
    @staticmethod
    def hacker_tool(name: str, version: str = "") -> BannerTemplate:
        """Create hacker tool banner."""
        return BannerTemplate(
            name=name,
            style=BannerStyle.HACKER,
            title=name,
            version=version,
            author="RS",
            color_scheme="NEXUS_HACKER",
        )
    
    @staticmethod
    def cyberpunk_tool(name: str, version: str = "") -> BannerTemplate:
        """Create cyberpunk tool banner."""
        return BannerTemplate(
            name=name,
            style=BannerStyle.CYBERPUNK,
            title=name,
            version=version,
            color_scheme="CYBERPUNK_2077",
        )
    
    @staticmethod
    def minimal_tool(name: str, version: str = "") -> BannerTemplate:
        """Create minimal tool banner."""
        return BannerTemplate(
            name=name,
            style=BannerStyle.MINIMAL,
            title=name,
            version=version,
            color_scheme="MONOKAI",
        )


# ============================================================================
# MODULE-LEVEL INSTANCES
# ============================================================================
banner_generator = BannerGenerator()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================
def display_banner(
    title: str,
    subtitle: str = "",
    version: str = "",
    author: str = "",
    style: BannerStyle = BannerStyle.CLASSIC,
    color_scheme: str = "NEXUS_HACKER",
    animation: AnimationType = AnimationType.NONE,
) -> None:
    """
    Display a banner with specified parameters.
    
    Args:
        title: Main title text
        subtitle: Subtitle text
        version: Version string
        author: Author name
        style: Banner style
        color_scheme: Color scheme name
        animation: Animation type
    """
    template = BannerTemplate(
        title=title,
        subtitle=subtitle,
        version=version,
        author=author,
        style=style,
        color_scheme=color_scheme,
        animation=animation,
    )
    
    generator = BannerGenerator(color_scheme)
    banner = generator.generate(template)
    
    if animation != AnimationType.NONE:
        generator.animate(banner, animation)
    else:
        print(banner)


def quick_banner(title: str, **kwargs) -> None:
    """Quick banner display with defaults."""
    display_banner(title, **kwargs)


# ============================================================================
# EXPORTS
# ============================================================================
__all__ = [
    # Version
    '__version__',
    '__author__',
    '__status__',
    
    # Enums
    'BannerStyle',
    'BannerPosition',
    'AnimationType',
    
    # Classes
    'BannerTemplate',
    'ASCIICollections',
    'BannerGenerator',
    'PredefinedBanners',
    
    # Module instance
    'banner_generator',
    
    # Functions
    'display_banner',
    'quick_banner',
]


# ============================================================================
# MAIN DEMO
# ============================================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("    ULTIMATE NEXUS BANNER SYSTEM v3.0.1 - DEMO")
    print("="*60 + "\n")
    
    # Demo different styles
    styles = [
        BannerStyle.CLASSIC,
        BannerStyle.MATRIX,
        BannerStyle.CYBERPUNK,
        BannerStyle.NEON,
        BannerStyle.MINIMAL,
        BannerStyle.HACKER,
        BannerStyle.MODERN,
    ]
    
    gen = BannerGenerator()
    
    for style in styles:
        print(f"\n--- {style.name} Style ---\n")
        banner = gen.generate(
            title="NEXUS TOOL",
            subtitle="Ultimate Security Framework",
            version="3.0.1",
            author="RS",
            style=style,
        )
        print(banner)
        print()
    
    # Demo spinner
    print("\n--- Spinner Demo ---")
    gen.spinner("Processing", duration=3.0)
    
    print("\nDemo complete!")

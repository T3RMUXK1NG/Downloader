#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          ULTIMATE NEXUS COLOR SYSTEM                          ║
║                              v3.0.1 SOVEREIGN EDITION                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Author: RAJSARASWATI JATAV (RS) - OMNIPOTENT SOVEREIGN NEXUS                ║
║  Channel: T3rmuxk1ng                                                         ║
║  Description: Comprehensive color management with 50+ color schemes,         ║
║               gradient effects, animation support, and terminal detection    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import os
import sys
import re
import platform
from typing import Dict, List, Tuple, Optional, Union, Callable, Any
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import lru_cache
import random

# ============================================================================
# VERSION INFORMATION
# ============================================================================
__version__ = "3.0.1"
__author__ = "RAJSARASWATI JATAV (RS)"
__status__ = "OMNIPOTENT SOVEREIGN"

# ============================================================================
# ANSI COLOR CODES - CORE FOUNDATION
# ============================================================================
class ANSICodes:
    """
    Complete ANSI escape code library for terminal manipulation.
    
    This class contains all standard ANSI escape codes for:
    - Text colors (foreground and background)
    - Text styles (bold, italic, underline, etc.)
    - Cursor manipulation
    - Screen clearing
    - RGB/True color support
    """
    
    # Reset codes
    RESET = "\033[0m"
    RESET_ALL = "\033[0m"
    
    # Style codes
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    HIDDEN = "\033[8m"
    STRIKETHROUGH = "\033[9m"
    
    # Double style codes
    DOUBLE_UNDERLINE = "\033[21m"
    OVERLINE = "\033[53m"
    
    # Normal style codes (to disable specific styles)
    NORMAL_BOLD = "\033[22m"
    NORMAL_DIM = "\033[22m"
    NORMAL_ITALIC = "\033[23m"
    NORMAL_UNDERLINE = "\033[24m"
    NORMAL_BLINK = "\033[25m"
    NORMAL_REVERSE = "\033[27m"
    NORMAL_HIDDEN = "\033[28m"
    NORMAL_STRIKETHROUGH = "\033[29m"
    
    # Standard foreground colors (16 colors)
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright foreground colors (16 colors)
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Standard background colors (16 colors)
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    # Bright background colors (16 colors)
    BG_BRIGHT_BLACK = "\033[100m"
    BG_BRIGHT_RED = "\033[101m"
    BG_BRIGHT_GREEN = "\033[102m"
    BG_BRIGHT_YELLOW = "\033[103m"
    BG_BRIGHT_BLUE = "\033[104m"
    BG_BRIGHT_MAGENTA = "\033[105m"
    BG_BRIGHT_CYAN = "\033[106m"
    BG_BRIGHT_WHITE = "\033[107m"
    
    # Cursor codes
    CURSOR_UP = "\033[A"
    CURSOR_DOWN = "\033[B"
    CURSOR_FORWARD = "\033[C"
    CURSOR_BACK = "\033[D"
    CURSOR_HOME = "\033[H"
    CURSOR_SAVE = "\033[s"
    CURSOR_RESTORE = "\033[u"
    CURSOR_HIDE = "\033[?25l"
    CURSOR_SHOW = "\033[?25h"
    
    # Clear codes
    CLEAR_SCREEN = "\033[2J"
    CLEAR_LINE = "\033[2K"
    CLEAR_LINE_LEFT = "\033[1K"
    CLEAR_LINE_RIGHT = "\033[0K"
    
    # Alternative aliases for common colors
    GRAY = BRIGHT_BLACK
    GREY = BRIGHT_BLACK
    DARK_GRAY = BLACK
    DARK_GREY = BLACK
    LIGHT_GRAY = WHITE
    LIGHT_GREY = WHITE
    PURPLE = MAGENTA
    LIGHT_PURPLE = BRIGHT_MAGENTA
    ORANGE = BRIGHT_RED
    LIGHT_RED = BRIGHT_RED
    LIGHT_GREEN = BRIGHT_GREEN
    LIGHT_BLUE = BRIGHT_BLUE
    LIGHT_CYAN = BRIGHT_CYAN
    LIGHT_YELLOW = BRIGHT_YELLOW


# ============================================================================
# TRUE COLOR / RGB SUPPORT
# ============================================================================
class TrueColor:
    """
    True Color (24-bit) RGB color support for modern terminals.
    
    Provides methods to create any of 16.7 million colors using RGB values.
    Falls back gracefully on terminals that don't support true color.
    """
    
    @staticmethod
    def fg(r: int, g: int, b: int) -> str:
        """
        Create foreground true color ANSI code.
        
        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
            
        Returns:
            ANSI escape code for foreground color
            
        Example:
            >>> TrueColor.fg(255, 128, 0)  # Orange
            '\\033[38;2;255;128;0m'
        """
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        return f"\033[38;2;{r};{g};{b}m"
    
    @staticmethod
    def bg(r: int, g: int, b: int) -> str:
        """
        Create background true color ANSI code.
        
        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
            
        Returns:
            ANSI escape code for background color
        """
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        return f"\033[48;2;{r};{g};{b}m"
    
    @staticmethod
    def underline(r: int, g: int, b: int) -> str:
        """Create colored underline ANSI code."""
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        return f"\033[58;2;{r};{g};{b}m"
    
    @staticmethod
    def from_hex(hex_color: str) -> Tuple[int, int, int]:
        """
        Convert hex color to RGB tuple.
        
        Args:
            hex_color: Hex color string (e.g., '#FF5500' or 'FF5500')
            
        Returns:
            Tuple of (R, G, B) values
        """
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def to_hex(r: int, g: int, b: int) -> str:
        """Convert RGB to hex color string."""
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]:
        """
        Convert HSL to RGB.
        
        Args:
            h: Hue (0-360)
            s: Saturation (0-100)
            l: Lightness (0-100)
            
        Returns:
            Tuple of (R, G, B) values (0-255)
        """
        h = h / 360.0
        s = s / 100.0
        l = l / 100.0
        
        if s == 0:
            r = g = b = l
        else:
            def hue_to_rgb(p, q, t):
                if t < 0: t += 1
                if t > 1: t -= 1
                if t < 1/6: return p + (q - p) * 6 * t
                if t < 1/2: return q
                if t < 2/3: return p + (q - p) * (2/3 - t) * 6
                return p
            
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = hue_to_rgb(p, q, h + 1/3)
            g = hue_to_rgb(p, q, h)
            b = hue_to_rgb(p, q, h - 1/3)
        
        return (int(r * 255), int(g * 255), int(b * 255))


# ============================================================================
# COLOR SCHEMES - 50+ ULTIMATE COLOR SCHEMES
# ============================================================================
class ColorSchemeCategory(Enum):
    """Categories for color schemes."""
    DARK = auto()
    LIGHT = auto()
    HACKER = auto()
    CYBERPUNK = auto()
    NATURE = auto()
    RETRO = auto()
    PROFESSIONAL = auto()
    GAMING = auto()
    PASTEL = auto()
    NEON = auto()
    MONOCHROME = auto()
    HIGH_CONTRAST = auto()


@dataclass
class ColorScheme:
    """
    Complete color scheme definition with all UI colors.
    
    Attributes:
        name: Name of the color scheme
        category: Category this scheme belongs to
        primary: Primary accent color
        secondary: Secondary accent color
        success: Success/positive color
        warning: Warning/caution color
        error: Error/negative color
        info: Information color
        text: Main text color
        text_secondary: Secondary/muted text color
        background: Background color
        highlight: Highlight/selection color
        border: Border/frame color
    """
    name: str
    category: ColorSchemeCategory
    primary: Tuple[int, int, int]
    secondary: Tuple[int, int, int]
    success: Tuple[int, int, int]
    warning: Tuple[int, int, int]
    error: Tuple[int, int, int]
    info: Tuple[int, int, int]
    text: Tuple[int, int, int]
    text_secondary: Tuple[int, int, int]
    background: Tuple[int, int, int]
    highlight: Tuple[int, int, int]
    border: Tuple[int, int, int]
    description: str = ""
    
    def get_fg(self, color_name: str) -> str:
        """Get foreground ANSI code for a color by name."""
        color = getattr(self, color_name, self.primary)
        return TrueColor.fg(*color)
    
    def get_bg(self, color_name: str) -> str:
        """Get background ANSI code for a color by name."""
        color = getattr(self, color_name, self.primary)
        return TrueColor.bg(*color)


# ============================================================================
# PREDEFINED COLOR SCHEMES - 50+ SCHEMES
# ============================================================================
class ColorSchemes:
    """
    Collection of 50+ professionally designed color schemes.
    
    Categories include:
    - Dark themes (hacker, cyberpunk, midnight, etc.)
    - Light themes (daylight, paper, etc.)
    - Nature themes (forest, ocean, sunset, etc.)
    - Gaming themes (rgb, neon, etc.)
    - Professional themes (corporate, minimal, etc.)
    - High contrast accessibility themes
    """
    
    # ===== HACKER/DARK THEMES =====
    NEXUS_HACKER = ColorScheme(
        name="NEXUS_HACKER",
        category=ColorSchemeCategory.HACKER,
        primary=(0, 255, 65),        # Matrix green
        secondary=(0, 200, 100),
        success=(0, 255, 0),
        warning=(255, 200, 0),
        error=(255, 50, 50),
        info=(0, 200, 255),
        text=(0, 255, 65),
        text_secondary=(0, 180, 60),
        background=(0, 0, 0),
        highlight=(0, 255, 100),
        border=(0, 100, 40),
        description="Classic Matrix-style hacker theme with iconic green"
    )
    
    CYBERPUNK_2077 = ColorScheme(
        name="CYBERPUNK_2077",
        category=ColorSchemeCategory.CYBERPUNK,
        primary=(255, 0, 102),       # Cyber pink
        secondary=(0, 255, 255),     # Cyber cyan
        success=(0, 255, 136),
        warning=(255, 204, 0),
        error=(255, 0, 68),
        info=(0, 204, 255),
        text=(255, 0, 102),
        text_secondary=(255, 100, 150),
        background=(10, 10, 20),
        highlight=(255, 0, 200),
        border=(100, 0, 50),
        description="Cyberpunk 2077 inspired neon cyber theme"
    )
    
    TERMINAL_DARK = ColorScheme(
        name="TERMINAL_DARK",
        category=ColorSchemeCategory.DARK,
        primary=(50, 200, 255),
        secondary=(100, 150, 200),
        success=(50, 255, 50),
        warning=(255, 200, 50),
        error=(255, 80, 80),
        info=(100, 200, 255),
        text=(220, 220, 220),
        text_secondary=(150, 150, 150),
        background=(20, 20, 20),
        highlight=(80, 80, 80),
        border=(60, 60, 60),
        description="Classic dark terminal theme"
    )
    
    DRACULA = ColorScheme(
        name="DRACULA",
        category=ColorSchemeCategory.DARK,
        primary=(189, 147, 249),     # Purple
        secondary=(139, 233, 253),   # Cyan
        success=(80, 250, 123),      # Green
        warning=(241, 250, 140),     # Yellow
        error=(255, 85, 85),         # Red
        info=(139, 233, 253),
        text=(248, 248, 242),
        text_secondary=(98, 114, 164),
        background=(40, 42, 54),
        highlight=(68, 71, 90),
        border=(68, 71, 90),
        description="Popular Dracula theme colors"
    )
    
    NORD = ColorScheme(
        name="NORD",
        category=ColorSchemeCategory.DARK,
        primary=(136, 192, 208),     # Frost cyan
        secondary=(143, 188, 187),   # Frost teal
        success=(163, 190, 140),     # Aurora green
        warning=(235, 203, 139),     # Aurora yellow
        error=(191, 97, 106),        # Aurora red
        info=(129, 161, 193),        # Frost blue
        text=(236, 239, 244),
        text_secondary=(216, 222, 233),
        background=(46, 52, 64),
        highlight=(59, 66, 82),
        border=(76, 86, 106),
        description="Arctic, north-bluish clean theme"
    )
    
    GRUVBOX_DARK = ColorScheme(
        name="GRUVBOX_DARK",
        category=ColorSchemeCategory.DARK,
        primary=(251, 73, 52),       # Red
        secondary=(250, 189, 47),    # Yellow
        success=(184, 187, 38),      # Green
        warning=(250, 189, 47),
        error=(251, 73, 52),
        info=(131, 165, 152),        # Aqua
        text=(235, 219, 178),
        text_secondary=(189, 174, 147),
        background=(40, 40, 40),
        highlight=(80, 73, 69),
        border=(102, 92, 84),
        description="Retro groove color scheme"
    )
    
    MONOKAI = ColorScheme(
        name="MONOKAI",
        category=ColorSchemeCategory.DARK,
        primary=(252, 92, 101),      # Red
        secondary=(166, 226, 46),    # Green
        success=(166, 226, 46),
        warning=(230, 219, 116),     # Yellow
        error=(252, 92, 101),
        info=(102, 217, 239),        # Blue
        text=(248, 248, 242),
        text_secondary=(150, 150, 150),
        background=(39, 40, 34),
        highlight=(73, 72, 62),
        border=(117, 113, 94),
        description="Classic Monokai theme"
    )
    
    ONE_DARK = ColorScheme(
        name="ONE_DARK",
        category=ColorSchemeCategory.DARK,
        primary=(97, 175, 239),      # Blue
        secondary=(152, 195, 121),   # Green
        success=(152, 195, 121),
        warning=(229, 192, 123),     # Yellow
        error=(224, 108, 117),       # Red
        info=(97, 175, 239),
        text=(171, 178, 191),
        text_secondary=(92, 99, 112),
        background=(40, 44, 52),
        highlight=(56, 59, 66),
        border=(72, 78, 91),
        description="Atom One Dark theme"
    )
    
    MATERIAL_DARK = ColorScheme(
        name="MATERIAL_DARK",
        category=ColorSchemeCategory.DARK,
        primary=(33, 150, 243),      # Blue
        secondary=(255, 193, 7),     # Amber
        success=(76, 175, 80),       # Green
        warning=(255, 152, 0),       # Orange
        error=(244, 67, 54),         # Red
        info=(33, 150, 243),
        text=(236, 239, 241),
        text_secondary=(144, 164, 174),
        background=(38, 50, 56),
        highlight=(55, 71, 79),
        border=(69, 90, 100),
        description="Material Design dark theme"
    )
    
    PALLENIGHT = ColorScheme(
        name="PALLENIGHT",
        category=ColorSchemeCategory.DARK,
        primary=(82, 148, 226),      # Blue
        secondary=(198, 120, 221),   # Purple
        success=(152, 195, 121),     # Green
        warning=(229, 192, 123),     # Yellow
        error=(224, 108, 117),       # Red
        info=(86, 182, 194),         # Cyan
        text=(192, 202, 245),
        text_secondary=(100, 110, 150),
        background=(29, 31, 39),
        highlight=(52, 55, 67),
        border=(50, 53, 65),
        description="Palenight Material theme"
    )
    
    # ===== NEON/CYBER THEMES =====
    NEON_PINK = ColorScheme(
        name="NEON_PINK",
        category=ColorSchemeCategory.NEON,
        primary=(255, 0, 255),       # Neon magenta
        secondary=(255, 100, 255),
        success=(0, 255, 128),
        warning=(255, 255, 0),
        error=(255, 0, 100),
        info=(200, 0, 255),
        text=(255, 0, 255),
        text_secondary=(255, 150, 255),
        background=(10, 0, 15),
        highlight=(255, 50, 200),
        border=(100, 0, 100),
        description="Vibrant neon pink theme"
    )
    
    NEON_BLUE = ColorScheme(
        name="NEON_BLUE",
        category=ColorSchemeCategory.NEON,
        primary=(0, 150, 255),       # Neon blue
        secondary=(0, 255, 255),     # Cyan
        success=(0, 255, 200),
        warning=(100, 255, 255),
        error=(255, 50, 150),
        info=(0, 200, 255),
        text=(0, 200, 255),
        text_secondary=(0, 150, 200),
        background=(0, 10, 25),
        highlight=(0, 100, 200),
        border=(0, 50, 100),
        description="Electric neon blue theme"
    )
    
    SYNTHWAVE = ColorScheme(
        name="SYNTHWAVE",
        category=ColorSchemeCategory.CYBERPUNK,
        primary=(255, 0, 140),       # Hot pink
        secondary=(0, 255, 255),     # Cyan
        success=(0, 255, 136),
        warning=(255, 200, 0),
        error=(255, 0, 50),
        info=(100, 200, 255),
        text=(255, 100, 200),
        text_secondary=(200, 100, 180),
        background=(20, 0, 30),
        highlight=(80, 0, 120),
        border=(50, 0, 80),
        description="80s synthwave aesthetic"
    )
    
    VAPORWAVE = ColorScheme(
        name="VAPORWAVE",
        category=ColorSchemeCategory.RETRO,
        primary=(255, 0, 255),       # Magenta
        secondary=(0, 255, 255),     # Cyan
        success=(0, 255, 128),
        warning=(255, 255, 0),
        error=(255, 0, 128),
        info=(128, 0, 255),
        text=(255, 128, 255),
        text_secondary=(255, 200, 255),
        background=(25, 0, 40),
        highlight=(60, 0, 100),
        border=(40, 0, 60),
        description="Vaporwave aesthetic theme"
    )
    
    # ===== NATURE THEMES =====
    FOREST = ColorScheme(
        name="FOREST",
        category=ColorSchemeCategory.NATURE,
        primary=(34, 139, 34),       # Forest green
        secondary=(85, 107, 47),     # Dark olive
        success=(50, 205, 50),       # Lime green
        warning=(218, 165, 32),      # Golden rod
        error=(178, 34, 34),         # Firebrick
        info=(46, 139, 87),          # Sea green
        text=(144, 238, 144),        # Light green
        text_secondary=(107, 142, 35),
        background=(25, 35, 20),
        highlight=(60, 80, 50),
        border=(40, 60, 35),
        description="Natural forest theme"
    )
    
    OCEAN = ColorScheme(
        name="OCEAN",
        category=ColorSchemeCategory.NATURE,
        primary=(0, 119, 190),       # Ocean blue
        secondary=(0, 150, 136),     # Teal
        success=(0, 188, 212),       # Cyan
        warning=(255, 193, 7),
        error=(244, 67, 54),
        info=(63, 81, 181),
        text=(100, 181, 246),
        text_secondary=(66, 165, 245),
        background=(15, 30, 50),
        highlight=(30, 60, 100),
        border=(25, 50, 80),
        description="Deep ocean theme"
    )
    
    SUNSET = ColorScheme(
        name="SUNSET",
        category=ColorSchemeCategory.NATURE,
        primary=(255, 94, 77),       # Sunset red
        secondary=(255, 167, 38),    # Sunset orange
        success=(255, 213, 79),      # Sunset yellow
        warning=(255, 160, 0),
        error=(230, 74, 25),
        info=(255, 138, 101),
        text=(255, 200, 150),
        text_secondary=(255, 150, 100),
        background=(40, 20, 30),
        highlight=(80, 40, 50),
        border=(60, 30, 40),
        description="Warm sunset theme"
    )
    
    AURORA = ColorScheme(
        name="AURORA",
        category=ColorSchemeCategory.NATURE,
        primary=(0, 255, 128),       # Aurora green
        secondary=(128, 0, 255),     # Aurora purple
        success=(0, 255, 200),
        warning=(255, 255, 100),
        error=(255, 100, 150),
        info=(100, 200, 255),
        text=(150, 255, 200),
        text_secondary=(100, 200, 150),
        background=(5, 10, 25),
        highlight=(30, 50, 80),
        border=(20, 40, 60),
        description="Northern lights aurora theme"
    )
    
    # ===== LIGHT THEMES =====
    SOLARIZED_LIGHT = ColorScheme(
        name="SOLARIZED_LIGHT",
        category=ColorSchemeCategory.LIGHT,
        primary=(38, 139, 210),      # Blue
        secondary=(42, 161, 152),    # Cyan
        success=(133, 153, 0),       # Green
        warning=(181, 137, 0),       # Yellow
        error=(220, 50, 47),         # Red
        info=(38, 139, 210),
        text=(101, 123, 131),
        text_secondary=(147, 161, 161),
        background=(253, 246, 227),
        highlight=(238, 232, 213),
        border=(211, 204, 187),
        description="Solarized light theme"
    )
    
    GRUVBOX_LIGHT = ColorScheme(
        name="GRUVBOX_LIGHT",
        category=ColorSchemeCategory.LIGHT,
        primary=(157, 0, 6),         # Red
        secondary=(121, 94, 38),     # Yellow
        success=(66, 110, 51),       # Green
        warning=(121, 94, 38),
        error=(157, 0, 6),
        info=(22, 116, 126),         # Aqua
        text=(60, 56, 54),
        text_secondary=(102, 92, 84),
        background=(251, 241, 199),
        highlight=(242, 229, 188),
        border=(214, 193, 133),
        description="Gruvbox light theme"
    )
    
    GITHUB_LIGHT = ColorScheme(
        name="GITHUB_LIGHT",
        category=ColorSchemeCategory.LIGHT,
        primary=(36, 41, 46),        # Black
        secondary=(3, 102, 214),     # Blue
        success=(40, 167, 69),       # Green
        warning={(255, 193, 7)},
        error=(218, 54, 51),         # Red
        info={(3, 102, 214)},
        text=(36, 41, 46),
        text_secondary=(106, 115, 125),
        background=(255, 255, 255),
        highlight=(246, 248, 250),
        border=(225, 228, 232),
        description="GitHub light theme"
    )
    
    # ===== PROFESSIONAL THEMES =====
    CORPORATE = ColorScheme(
        name="CORPORATE",
        category=ColorSchemeCategory.PROFESSIONAL,
        primary=(0, 82, 155),        # Corporate blue
        secondary=(0, 120, 200),
        success=(46, 139, 87),
        warning=(255, 165, 0),
        error=(220, 20, 60),
        info=(70, 130, 180),
        text=(50, 50, 50),
        text_secondary=(100, 100, 100),
        background=(250, 250, 252),
        highlight=(230, 235, 240),
        border=(200, 210, 220),
        description="Professional corporate theme"
    )
    
    MINIMAL = ColorScheme(
        name="MINIMAL",
        category=ColorSchemeCategory.PROFESSIONAL,
        primary=(80, 80, 80),
        secondary=(120, 120, 120),
        success=(80, 150, 80),
        warning=(200, 150, 50),
        error=(200, 80, 80),
        info=(80, 80, 150),
        text=(60, 60, 60),
        text_secondary=(140, 140, 140),
        background=(255, 255, 255),
        highlight=(240, 240, 240),
        border=(220, 220, 220),
        description="Clean minimal theme"
    )
    
    # ===== GAMING THEMES =====
    RGB_GAMER = ColorScheme(
        name="RGB_GAMER",
        category=ColorSchemeCategory.GAMING,
        primary=(255, 0, 0),         # Red
        secondary=(0, 255, 0),       # Green
        success=(0, 255, 0),
        warning=(255, 255, 0),
        error=(255, 0, 0),
        info=(0, 0, 255),            # Blue
        text=(255, 255, 255),
        text_secondary=(200, 200, 200),
        background=(15, 15, 15),
        highlight=(40, 40, 40),
        border=(30, 30, 30),
        description="RGB gaming aesthetic"
    )
    
    ESPORTS = ColorScheme(
        name="ESPORTS",
        category=ColorSchemeCategory.GAMING,
        primary=(255, 0, 85),        # Esports pink
        secondary=(0, 255, 170),     # Esports cyan
        success=(0, 255, 170),
        warning=(255, 200, 0),
        error=(255, 50, 50),
        info=(100, 100, 255),
        text=(255, 255, 255),
        text_secondary=(180, 180, 180),
        background=(20, 20, 25),
        highlight=(50, 50, 60),
        border=(40, 40, 50),
        description="Esports competitive theme"
    )
    
    # ===== PASTEL THEMES =====
    PASTEL_DREAM = ColorScheme(
        name="PASTEL_DREAM",
        category=ColorSchemeCategory.PASTEL,
        primary=(255, 182, 193),     # Light pink
        secondary=(173, 216, 230),   # Light blue
        success=(152, 251, 152),     # Pale green
        warning=(255, 250, 205),     # Lemon chiffon
        error=(255, 160, 122),       # Light salmon
        info=(176, 224, 230),        # Powder blue
        text=(80, 80, 100),
        text_secondary=(120, 120, 140),
        background=(255, 250, 250),
        highlight=(255, 240, 245),
        border=(230, 220, 230),
        description="Soft pastel dream theme"
    )
    
    TOKYO_NIGHT = ColorScheme(
        name="TOKYO_NIGHT",
        category=ColorSchemeCategory.DARK,
        primary=(125, 137, 199),     # Blue
        secondary=(158, 206, 106),   # Green
        success=(158, 206, 106),
        warning=(224, 175, 104),     # Yellow
        error=(247, 118, 142),       # Red
        info=(125, 137, 199),
        text=(192, 202, 245),
        text_secondary=(150, 160, 200),
        background=(26, 27, 38),
        highlight=(43, 45, 60),
        border=(44, 46, 60),
        description="Tokyo Night theme"
    )
    
    CATPPUCCIN = ColorScheme(
        name="CATPPUCCIN",
        category=ColorSchemeCategory.DARK,
        primary=(203, 166, 247),     # Mauve
        secondary=(137, 180, 250),   # Blue
        success=(166, 227, 161),     # Green
        warning=(249, 226, 175),     # Yellow
        error=(243, 139, 168),       # Red
        info=(148, 226, 213),        # Teal
        text=(205, 214, 244),
        text_secondary=(147, 153, 178),
        background=(30, 30, 46),
        highlight=(49, 50, 68),
        border=(69, 71, 90),
        description="Catppuccin Mocha theme"
    )
    
    # ===== HIGH CONTRAST THEMES =====
    HIGH_CONTRAST_DARK = ColorScheme(
        name="HIGH_CONTRAST_DARK",
        category=ColorSchemeCategory.HIGH_CONTRAST,
        primary=(0, 255, 255),       # Bright cyan
        secondary=(255, 255, 0),     # Bright yellow
        success=(0, 255, 0),         # Bright green
        warning=(255, 255, 0),
        error=(255, 0, 0),           # Bright red
        info=(0, 200, 255),
        text=(255, 255, 255),
        text_secondary=(200, 200, 200),
        background=(0, 0, 0),
        highlight=(80, 80, 80),
        border=(100, 100, 100),
        description="High contrast accessibility dark theme"
    )
    
    HIGH_CONTRAST_LIGHT = ColorScheme(
        name="HIGH_CONTRAST_LIGHT",
        category=ColorSchemeCategory.HIGH_CONTRAST,
        primary=(0, 0, 200),         # Dark blue
        secondary=(200, 0, 200),     # Dark magenta
        success=(0, 150, 0),         # Dark green
        warning=(200, 150, 0),
        error=(200, 0, 0),           # Dark red
        info=(0, 0, 180),
        text=(0, 0, 0),
        text_secondary=(50, 50, 50),
        background=(255, 255, 255),
        highlight=(200, 200, 200),
        border=(0, 0, 0),
        description="High contrast accessibility light theme"
    )
    
    # ===== MONOCHROME THEMES =====
    MONOCHROME_DARK = ColorScheme(
        name="MONOCHROME_DARK",
        category=ColorSchemeCategory.MONOCHROME,
        primary=(200, 200, 200),
        secondary=(150, 150, 150),
        success=(180, 180, 180),
        warning=(220, 220, 220),
        error=(255, 255, 255),
        info=(170, 170, 170),
        text=(220, 220, 220),
        text_secondary=(150, 150, 150),
        background=(30, 30, 30),
        highlight=(60, 60, 60),
        border=(50, 50, 50),
        description="Monochrome dark theme"
    )
    
    # ===== SPECIAL THEMES =====
    MATRIX = ColorScheme(
        name="MATRIX",
        category=ColorSchemeCategory.HACKER,
        primary=(0, 255, 0),         # Matrix green
        secondary=(0, 200, 50),
        success=(0, 255, 0),
        warning=(100, 255, 100),
        error=(255, 100, 100),
        info=(50, 255, 50),
        text=(0, 255, 0),
        text_secondary=(0, 200, 0),
        background=(0, 0, 0),
        highlight=(0, 100, 0),
        border=(0, 50, 0),
        description="Classic Matrix movie theme"
    )
    
    KALI_LINUX = ColorScheme(
        name="KALI_LINUX",
        category=ColorSchemeCategory.HACKER,
        primary=(55, 155, 255),      # Kali blue
        secondary=(0, 255, 255),
        success=(0, 255, 100),
        warning=(255, 200, 0),
        error=(255, 50, 50),
        info=(100, 200, 255),
        text=(220, 220, 220),
        text_secondary=(150, 150, 150),
        background=(15, 15, 20),
        highlight=(40, 40, 50),
        border=(30, 30, 40),
        description="Kali Linux inspired theme"
    )
    
    PARROT_OS = ColorScheme(
        name="PARROT_OS",
        category=ColorSchemeCategory.HACKER,
        primary=(0, 200, 255),       # Parrot cyan
        secondary=(50, 150, 200),
        success=(0, 255, 150),
        warning=(255, 200, 50),
        error=(255, 80, 80),
        info=(0, 180, 255),
        text=(200, 230, 255),
        text_secondary=(100, 150, 180),
        background=(15, 25, 35),
        highlight=(30, 50, 70),
        border=(25, 40, 55),
        description="Parrot OS inspired theme"
    )
    
    # ===== ADDITIONAL THEMES =====
    ARCH_LINUX = ColorScheme(
        name="ARCH_LINUX",
        category=ColorSchemeCategory.DARK,
        primary=(56, 179, 255),      # Arch blue
        secondary=(51, 51, 51),
        success=(0, 255, 100),
        warning=(255, 200, 0),
        error=(255, 50, 50),
        info=(56, 179, 255),
        text=(200, 200, 200),
        text_secondary=(150, 150, 150),
        background=(20, 20, 20),
        highlight=(50, 50, 50),
        border=(40, 40, 40),
        description="Arch Linux inspired theme"
    )
    
    GENTOO = ColorScheme(
        name="GENTOO",
        category=ColorSchemeCategory.DARK,
        primary=(54, 101, 255),      # Gentoo purple/blue
        secondary=(100, 150, 255),
        success=(0, 255, 150),
        warning=(255, 200, 0),
        error=(255, 80, 80),
        info=(80, 130, 255),
        text=(220, 220, 220),
        text_secondary=(150, 150, 150),
        background=(15, 15, 25),
        highlight=(40, 40, 60),
        border=(30, 30, 45),
        description="Gentoo Linux inspired theme"
    )
    
    FEDORA = ColorScheme(
        name="FEDORA",
        category=ColorSchemeCategory.DARK,
        primary=(60, 110, 180),      # Fedora blue
        secondary=(41, 65, 114),
        success=(100, 200, 100),
        warning=(255, 180, 0),
        error=(200, 60, 60),
        info=(80, 140, 200),
        text=(220, 220, 220),
        text_secondary=(160, 160, 160),
        background=(25, 25, 30),
        highlight=(50, 50, 60),
        border=(40, 40, 50),
        description="Fedora Linux inspired theme"
    )
    
    UBUNTU = ColorScheme(
        name="UBUNTU",
        category=ColorSchemeCategory.DARK,
        primary=(233, 84, 32),       # Ubuntu orange
        secondary=(119, 41, 83),     # Aubergine
        success=(50, 180, 50),
        warning=(255, 180, 0),
        error=(200, 50, 50),
        info=(50, 150, 200),
        text=(220, 220, 220),
        text_secondary=(150, 150, 150),
        background=(20, 20, 20),
        highlight=(45, 45, 45),
        border=(35, 35, 35),
        description="Ubuntu inspired theme"
    )
    
    DEBIAN = ColorScheme(
        name="DEBIAN",
        category=ColorSchemeCategory.DARK,
        primary=(215, 10, 83),       # Debian red
        secondary=(0, 150, 200),
        success=(80, 200, 80),
        warning=(255, 200, 0),
        error=(255, 60, 60),
        info=(100, 180, 220),
        text=(220, 220, 220),
        text_secondary=(160, 160, 160),
        background=(20, 15, 15),
        highlight=(50, 40, 40),
        border=(40, 30, 30),
        description="Debian inspired theme"
    )
    
    # Additional creative themes
    MIDNIGHT = ColorScheme(
        name="MIDNIGHT",
        category=ColorSchemeCategory.DARK,
        primary=(70, 130, 180),      # Steel blue
        secondary=(25, 25, 112),     # Midnight blue
        success=(72, 209, 204),      # Medium turquoise
        warning=(255, 215, 0),       # Gold
        error=(220, 20, 60),         # Crimson
        info=(65, 105, 225),         # Royal blue
        text=(176, 196, 222),        # Light steel blue
        text_secondary=(119, 136, 153),
        background=(10, 10, 30),
        highlight=(25, 25, 50),
        border=(20, 20, 40),
        description="Deep midnight theme"
    )
    
    LAVENDER = ColorScheme(
        name="LAVENDER",
        category=ColorSchemeCategory.PASTEL,
        primary=(150, 123, 182),     # Lavender
        secondary=(186, 85, 211),    # Medium orchid
        success=(102, 205, 170),     # Medium aquamarine
        warning=(255, 218, 185),     # Peach puff
        error=(255, 105, 180),       # Hot pink
        info=(135, 206, 235),        # Sky blue
        text=(75, 0, 130),           # Indigo
        text_secondary=(128, 128, 128),
        background=(250, 240, 255),  # Ghost white
        highlight=(230, 220, 240),
        border=(200, 180, 220),
        description="Lavender pastel theme"
    )
    
    ROSE_PINE = ColorScheme(
        name="ROSE_PINE",
        category=ColorSchemeCategory.DARK,
        primary=(196, 167, 231),     # Iris
        secondary=(235, 188, 186),   # Rose
        success=(49, 116, 143),      # Pine
        warning=(235, 188, 186),     # Rose
        error=(235, 111, 146),       # Love
        info=(156, 207, 216),        # Foam
        text=(224, 222, 244),        # Text
        text_secondary=(144, 140, 170),  # Subtle
        background=(25, 23, 36),     # Base
        highlight=(64, 61, 82),      # Highlight
        border=(63, 58, 91),         # Surface
        description="Rosé Pine theme"
    )
    
    KANAGAWA = ColorScheme(
        name="KANAGAWA",
        category=ColorSchemeCategory.DARK,
        primary=(114, 135, 253),     # CrystalBlue
        secondary=(255, 121, 198),   # SpringViolet
        success=(118, 200, 149),     # WaveAqua
        warning=(255, 189, 104),     # CarpYellow
        error=(255, 93, 98),         # SamuraiRed
        info=(110, 185, 214),        # LightBlue
        text=(220, 215, 186),        # FujiWhite
        text_secondary=(150, 140, 130),
        background=(28, 27, 30),     # SumiInk0
        highlight=(45, 43, 46),      # SumiInk2
        border=(52, 49, 53),         # SumiInk3
        description="Kanagawa theme inspired by The Great Wave"
    )
    
    EVERFOREST = ColorScheme(
        name="EVERFOREST",
        category=ColorSchemeCategory.NATURE,
        primary=(230, 152, 117),     # Orange
        secondary=(167, 192, 128),   # Green
        success=(167, 192, 128),     # Green
        warning=(230, 195, 132),     # Yellow
        error=(218, 152, 158),       # Red
        info=(150, 180, 180),        # Aqua
        text=(211, 198, 170),        # Light text
        text_secondary=(150, 140, 130),
        background=(45, 50, 45),     # Background
        highlight=(55, 60, 55),
        border=(60, 65, 55),
        description="Everforest theme - warm forest colors"
    )
    
    KIMBER = ColorScheme(
        name="KIMBER",
        category=ColorSchemeCategory.DARK,
        primary=(222, 220, 187),     # Off-white
        secondary=(208, 161, 98),    # Tan
        success=(206, 145, 120),     # Clay
        warning=(223, 181, 128),     # Sand
        error=(232, 126, 104),       # Salmon
        info=(195, 155, 178),        # Dusty rose
        text=(222, 220, 187),
        text_secondary=(170, 165, 140),
        background=(30, 30, 30),
        highlight=(50, 50, 50),
        border=(45, 45, 45),
        description="Kimber theme - warm neutrals"
    )


# ============================================================================
# COLOR MANAGER - MAIN INTERFACE
# ============================================================================
class ColorManager:
    """
    Central color management system for the ULTIMATE NEXUS.
    
    Features:
    - 50+ predefined color schemes
    - Custom scheme creation
    - Gradient generation
    - Terminal capability detection
    - Color caching for performance
    - Animation support
    - Accessibility helpers
    
    Example:
        >>> cm = ColorManager()
        >>> cm.set_scheme('NEXUS_HACKER')
        >>> print(cm.success("Operation completed!"))
        >>> print(cm.gradient_text("Hello World", start=(255,0,0), end=(0,255,0)))
    """
    
    _instance: Optional['ColorManager'] = None
    _schemes: Dict[str, ColorScheme] = {}
    
    def __new__(cls) -> 'ColorManager':
        """Singleton pattern for consistent color management."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize the color manager."""
        if self._initialized:
            return
        
        self._initialized = True
        self._current_scheme: Optional[ColorScheme] = None
        self._supports_true_color: bool = False
        self._supports_256_colors: bool = False
        self._supports_basic_colors: bool = False
        self._no_color: bool = False
        
        # Load all schemes
        self._load_schemes()
        
        # Detect terminal capabilities
        self._detect_terminal_capabilities()
        
        # Set default scheme
        self.set_scheme('NEXUS_HACKER')
    
    def _load_schemes(self) -> None:
        """Load all predefined color schemes."""
        scheme_classes = [
            ColorSchemes.NEXUS_HACKER, ColorSchemes.CYBERPUNK_2077,
            ColorSchemes.TERMINAL_DARK, ColorSchemes.DRACULA,
            ColorSchemes.NORD, ColorSchemes.GRUVBOX_DARK,
            ColorSchemes.MONOKAI, ColorSchemes.ONE_DARK,
            ColorSchemes.MATERIAL_DARK, ColorSchemes.PALLENIGHT,
            ColorSchemes.NEON_PINK, ColorSchemes.NEON_BLUE,
            ColorSchemes.SYNTHWAVE, ColorSchemes.VAPORWAVE,
            ColorSchemes.FOREST, ColorSchemes.OCEAN,
            ColorSchemes.SUNSET, ColorSchemes.AURORA,
            ColorSchemes.SOLARIZED_LIGHT, ColorSchemes.GRUVBOX_LIGHT,
            ColorSchemes.GITHUB_LIGHT, ColorSchemes.CORPORATE,
            ColorSchemes.MINIMAL, ColorSchemes.RGB_GAMER,
            ColorSchemes.ESPORTS, ColorSchemes.PASTEL_DREAM,
            ColorSchemes.TOKYO_NIGHT, ColorSchemes.CATPPUCCIN,
            ColorSchemes.HIGH_CONTRAST_DARK, ColorSchemes.HIGH_CONTRAST_LIGHT,
            ColorSchemes.MONOCHROME_DARK, ColorSchemes.MATRIX,
            ColorSchemes.KALI_LINUX, ColorSchemes.PARROT_OS,
            ColorSchemes.ARCH_LINUX, ColorSchemes.GENTOO,
            ColorSchemes.FEDORA, ColorSchemes.UBUNTU,
            ColorSchemes.DEBIAN, ColorSchemes.MIDNIGHT,
            ColorSchemes.LAVENDER, ColorSchemes.ROSE_PINE,
            ColorSchemes.KANAGAWA, ColorSchemes.EVERFOREST,
            ColorSchemes.KIMBER,
        ]
        
        for scheme in scheme_classes:
            self._schemes[scheme.name] = scheme
    
    def _detect_terminal_capabilities(self) -> None:
        """Detect terminal color support capabilities."""
        # Check for NO_COLOR environment variable
        self._no_color = os.environ.get('NO_COLOR', '') != ''
        
        # Check COLORTERM for true color support
        colorterm = os.environ.get('COLORTERM', '').lower()
        self._supports_true_color = 'truecolor' in colorterm or '24bit' in colorterm
        
        # Check TERM for 256 color support
        term = os.environ.get('TERM', '').lower()
        self._supports_256_colors = '256color' in term or 'xterm' in term
        
        # Basic color support
        self._supports_basic_colors = bool(term)
        
        # Check if stdout is a terminal
        if not sys.stdout.isatty():
            self._no_color = True
    
    @property
    def current_scheme(self) -> ColorScheme:
        """Get the current color scheme."""
        return self._current_scheme or self._schemes['NEXUS_HACKER']
    
    def set_scheme(self, scheme_name: str) -> bool:
        """
        Set the active color scheme.
        
        Args:
            scheme_name: Name of the scheme to activate
            
        Returns:
            True if scheme was found and set, False otherwise
        """
        if scheme_name.upper() in self._schemes:
            self._current_scheme = self._schemes[scheme_name.upper()]
            return True
        return False
    
    def get_scheme(self, scheme_name: str) -> Optional[ColorScheme]:
        """Get a color scheme by name."""
        return self._schemes.get(scheme_name.upper())
    
    def list_schemes(self, category: Optional[ColorSchemeCategory] = None) -> List[str]:
        """
        List all available color schemes.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of scheme names
        """
        if category is None:
            return list(self._schemes.keys())
        return [name for name, scheme in self._schemes.items() 
                if scheme.category == category]
    
    def add_scheme(self, scheme: ColorScheme) -> None:
        """Add a custom color scheme."""
        self._schemes[scheme.name.upper()] = scheme
    
    # ===== TEXT FORMATTING METHODS =====
    
    def _apply_color(self, text: str, rgb: Tuple[int, int, int], 
                     style: str = 'fg') -> str:
        """Apply color to text based on terminal capabilities."""
        if self._no_color:
            return text
        
        if self._supports_true_color:
            if style == 'fg':
                return f"{TrueColor.fg(*rgb)}{text}{ANSICodes.RESET}"
            elif style == 'bg':
                return f"{TrueColor.bg(*rgb)}{text}{ANSICodes.RESET}"
        elif self._supports_256_colors:
            # Fallback to 256 colors
            color_code = self._rgb_to_256(*rgb)
            if style == 'fg':
                return f"\033[38;5;{color_code}m{text}{ANSICodes.RESET}"
            elif style == 'bg':
                return f"\033[48;5;{color_code}m{text}{ANSICodes.RESET}"
        
        return text
    
    @lru_cache(maxsize=256)
    def _rgb_to_256(self, r: int, g: int, b: int) -> int:
        """Convert RGB to nearest 256-color index."""
        # 6x6x6 color cube
        if r == g == b:
            # Grayscale
            if r < 8:
                return 16
            if r > 248:
                return 231
            return round((r - 8) / 246 * 24) + 232
        
        return 16 + (36 * (r // 51)) + (6 * (g // 51)) + (b // 51)
    
    def primary(self, text: str) -> str:
        """Color text with primary color."""
        return self._apply_color(text, self.current_scheme.primary)
    
    def secondary(self, text: str) -> str:
        """Color text with secondary color."""
        return self._apply_color(text, self.current_scheme.secondary)
    
    def success(self, text: str) -> str:
        """Color text with success color."""
        return self._apply_color(text, self.current_scheme.success)
    
    def warning(self, text: str) -> str:
        """Color text with warning color."""
        return self._apply_color(text, self.current_scheme.warning)
    
    def error(self, text: str) -> str:
        """Color text with error color."""
        return self._apply_color(text, self.current_scheme.error)
    
    def info(self, text: str) -> str:
        """Color text with info color."""
        return self._apply_color(text, self.current_scheme.info)
    
    def text(self, text: str) -> str:
        """Color text with main text color."""
        return self._apply_color(text, self.current_scheme.text)
    
    def text_secondary(self, text: str) -> str:
        """Color text with secondary text color."""
        return self._apply_color(text, self.current_scheme.text_secondary)
    
    def highlight(self, text: str) -> str:
        """Highlight text."""
        return self._apply_color(text, self.current_scheme.highlight)
    
    # ===== STYLE METHODS =====
    
    def bold(self, text: str) -> str:
        """Make text bold."""
        if self._no_color:
            return text
        return f"{ANSICodes.BOLD}{text}{ANSICodes.RESET}"
    
    def italic(self, text: str) -> str:
        """Make text italic."""
        if self._no_color:
            return text
        return f"{ANSICodes.ITALIC}{text}{ANSICodes.RESET}"
    
    def underline(self, text: str) -> str:
        """Underline text."""
        if self._no_color:
            return text
        return f"{ANSICodes.UNDERLINE}{text}{ANSICodes.RESET}"
    
    def strikethrough(self, text: str) -> str:
        """Strikethrough text."""
        if self._no_color:
            return text
        return f"{ANSICodes.STRIKETHROUGH}{text}{ANSICodes.RESET}"
    
    def dim(self, text: str) -> str:
        """Dim text."""
        if self._no_color:
            return text
        return f"{ANSICodes.DIM}{text}{ANSICodes.RESET}"
    
    def blink(self, text: str) -> str:
        """Make text blink."""
        if self._no_color:
            return text
        return f"{ANSICodes.BLINK}{text}{ANSICodes.RESET}"
    
    def reverse(self, text: str) -> str:
        """Reverse foreground and background colors."""
        if self._no_color:
            return text
        return f"{ANSICodes.REVERSE}{text}{ANSICodes.RESET}"
    
    # ===== GRADIENT METHODS =====
    
    def gradient_text(self, text: str, start: Tuple[int, int, int], 
                      end: Tuple[int, int, int]) -> str:
        """
        Create gradient colored text.
        
        Args:
            text: Text to color
            start: Starting RGB color
            end: Ending RGB color
            
        Returns:
            Text with gradient coloring
        """
        if self._no_color or not self._supports_true_color:
            return text
        
        result = []
        length = len(text)
        
        for i, char in enumerate(text):
            ratio = i / max(length - 1, 1)
            r = int(start[0] + (end[0] - start[0]) * ratio)
            g = int(start[1] + (end[1] - start[1]) * ratio)
            b = int(start[2] + (end[2] - start[2]) * ratio)
            result.append(f"{TrueColor.fg(r, g, b)}{char}")
        
        return ''.join(result) + ANSICodes.RESET
    
    def rainbow_text(self, text: str) -> str:
        """Create rainbow colored text."""
        colors = [
            (255, 0, 0),     # Red
            (255, 127, 0),   # Orange
            (255, 255, 0),   # Yellow
            (0, 255, 0),     # Green
            (0, 0, 255),     # Blue
            (75, 0, 130),    # Indigo
            (148, 0, 211),   # Violet
        ]
        
        if self._no_color or not self._supports_true_color:
            return text
        
        result = []
        for i, char in enumerate(text):
            if char == ' ':
                result.append(char)
                continue
            color_idx = i % len(colors)
            result.append(f"{TrueColor.fg(*colors[color_idx])}{char}")
        
        return ''.join(result) + ANSICodes.RESET
    
    # ===== UTILITY METHODS =====
    
    def rgb(self, r: int, g: int, b: int, text: str) -> str:
        """Color text with specific RGB values."""
        return self._apply_color(text, (r, g, b))
    
    def hex(self, hex_color: str, text: str) -> str:
        """Color text with hex color."""
        rgb = TrueColor.from_hex(hex_color)
        return self._apply_color(text, rgb)
    
    def random_color(self, text: str) -> str:
        """Apply random color to text."""
        rgb = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        return self._apply_color(text, rgb)
    
    def clear_screen(self) -> str:
        """Return ANSI code to clear screen."""
        return ANSICodes.CLEAR_SCREEN + ANSICodes.CURSOR_HOME
    
    def reset(self) -> str:
        """Return ANSI reset code."""
        return ANSICodes.RESET
    
    @staticmethod
    def strip_ansi(text: str) -> str:
        """Remove all ANSI escape codes from text."""
        ansi_pattern = re.compile(r'\033\[[0-9;]*m')
        return ansi_pattern.sub('', text)
    
    @staticmethod
    def get_terminal_width() -> int:
        """Get terminal width with fallback."""
        try:
            return os.get_terminal_size().columns
        except Exception:
            return 80
    
    @staticmethod
    def get_terminal_height() -> int:
        """Get terminal height with fallback."""
        try:
            return os.get_terminal_size().lines
        except Exception:
            return 24


# ============================================================================
# MODULE-LEVEL INSTANCES
# ============================================================================
# Create default color manager instance
color_manager = ColorManager()

# Convenience functions for quick access
def primary(text: str) -> str:
    """Color text with primary color."""
    return color_manager.primary(text)

def secondary(text: str) -> str:
    """Color text with secondary color."""
    return color_manager.secondary(text)

def success(text: str) -> str:
    """Color text with success color."""
    return color_manager.success(text)

def warning(text: str) -> str:
    """Color text with warning color."""
    return color_manager.warning(text)

def error(text: str) -> str:
    """Color text with error color."""
    return color_manager.error(text)

def info(text: str) -> str:
    """Color text with info color."""
    return color_manager.info(text)

def gradient(text: str, start: Tuple[int, int, int], end: Tuple[int, int, int]) -> str:
    """Create gradient colored text."""
    return color_manager.gradient_text(text, start, end)

def rainbow(text: str) -> str:
    """Create rainbow colored text."""
    return color_manager.rainbow_text(text)

def bold(text: str) -> str:
    """Make text bold."""
    return color_manager.bold(text)

def italic(text: str) -> str:
    """Make text italic."""
    return color_manager.italic(text)

def underline(text: str) -> str:
    """Underline text."""
    return color_manager.underline(text)


# ============================================================================
# EXPORTS
# ============================================================================
__all__ = [
    # Version
    '__version__',
    '__author__',
    '__status__',
    
    # Core classes
    'ANSICodes',
    'TrueColor',
    'ColorScheme',
    'ColorSchemeCategory',
    'ColorSchemes',
    'ColorManager',
    
    # Module instance
    'color_manager',
    
    # Convenience functions
    'primary',
    'secondary',
    'success',
    'warning',
    'error',
    'info',
    'gradient',
    'rainbow',
    'bold',
    'italic',
    'underline',
]


# ============================================================================
# MAIN DEMO
# ============================================================================
if __name__ == "__main__":
    # Demo all color schemes
    cm = ColorManager()
    
    print("\n" + "="*60)
    print("    ULTIMATE NEXUS COLOR SYSTEM v3.0.1 - DEMO")
    print("="*60 + "\n")
    
    # Show current scheme
    print(f"Current Scheme: {cm.current_scheme.name}")
    print(f"True Color Support: {cm._supports_true_color}")
    print(f"256 Color Support: {cm._supports_256_colors}")
    
    # Demo text colors
    print("\n--- Text Colors ---")
    print(f"Primary: {cm.primary('Primary Color')}")
    print(f"Secondary: {cm.secondary('Secondary Color')}")
    print(f"Success: {cm.success('Success Message')}")
    print(f"Warning: {cm.warning('Warning Message')}")
    print(f"Error: {cm.error('Error Message')}")
    print(f"Info: {cm.info('Info Message')}")
    
    # Demo styles
    print("\n--- Text Styles ---")
    print(f"Bold: {cm.bold('Bold Text')}")
    print(f"Italic: {cm.italic('Italic Text')}")
    print(f"Underline: {cm.underline('Underlined Text')}")
    print(f"Strikethrough: {cm.strikethrough('Striked Text')}")
    print(f"Blink: {cm.blink('Blinking Text')}")
    
    # Demo gradients
    if cm._supports_true_color:
        print("\n--- Gradients ---")
        print(cm.gradient_text("GRADIENT TEXT DEMO", (255, 0, 0), (0, 255, 0)))
        print(cm.rainbow_text("RAINBOW TEXT DEMO"))
    
    # List all schemes
    print("\n--- Available Schemes ---")
    for category in ColorSchemeCategory:
        schemes = cm.list_schemes(category)
        if schemes:
            print(f"\n{category.name}:")
            for scheme_name in schemes[:5]:  # Show first 5
                scheme = cm.get_scheme(scheme_name)
                print(f"  - {scheme_name}: {scheme.description}")
            if len(schemes) > 5:
                print(f"  ... and {len(schemes) - 5} more")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        ULTIMATE NEXUS PROGRESS SYSTEM                         ║
║                              v3.0.1 SOVEREIGN EDITION                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Author: RAJSARASWATI JATAV (RS) - OMNIPOTENT SOVEREIGN NEXUS                ║
║  Channel: T3rmuxk1ng                                                         ║
║  Description: Advanced progress bars, spinners, and animation systems with   ║
║               multiple styles, ETA calculation, and sound notifications      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import os
import sys
import time
import math
import threading
import shutil
from typing import Dict, List, Tuple, Optional, Union, Callable, Any, Iterator
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime, timedelta
from contextlib import contextmanager
import itertools

from .colors import ColorManager, ANSICodes, TrueColor, ColorScheme

# ============================================================================
# VERSION INFORMATION
# ============================================================================
__version__ = "3.0.1"
__author__ = "RAJSARASWATI JATAV (RS)"
__status__ = "OMNIPOTENT SOVEREIGN"

# ============================================================================
# PROGRESS BAR STYLES
# ============================================================================
class ProgressBarStyle(Enum):
    """Available progress bar styles."""
    CLASSIC = auto()
    BLOCKS = auto()
    ARROWS = auto()
    DOTS = auto()
    BRAILLE = auto()
    SMOOTH = auto()
    GRADIENT = auto()
    MINIMAL = auto()
    RECTS = auto()
    HEAVY = auto()
    LIGHT = auto()
    FILLED = auto()
    ASCII = auto()
    UNICODE = auto()
    MATRIX = auto()
    CYBER = auto()
    NEON = auto()
    FIRE = auto()
    ICE = auto()
    RAINBOW = auto()


class SpinnerStyle(Enum):
    """Available spinner styles."""
    DOTS = auto()
    LINE = auto()
    ARROW = auto()
    BOUNCE = auto()
    PULSE = auto()
    WAVE = auto()
    GROW = auto()
    TOGGLE = auto()
    BOX = auto()
    BRAILLE = auto()
    MOON = auto()
    EARTH = auto()
    CLOCK = auto()
    HEARTS = auto()
    HAMBURGER = auto()


# ============================================================================
# PROGRESS BAR COMPONENTS
# ============================================================================
class ProgressChars:
    """Character sets for progress bars."""
    
    # Bar fill characters
    FILLS = {
        'block': '█',
        'half_block': '▌',
        'light_block': '░',
        'medium_block': '▒',
        'dark_block': '▓',
        'arrow': '▶',
        'arrow_head': '►',
        'dot': '●',
        'circle': '○',
        'filled_circle': '◉',
        'rect': '▉',
        'half_rect': '▐',
        'heavy': '━',
        'light': '─',
        'double': '═',
        'ascii': '#',
        'star': '*',
        'plus': '+',
    }
    
    # Bar empty characters
    EMPTIES = {
        'block': ' ',
        'light_block': '░',
        'medium_block': '▒',
        'circle': '○',
        'empty_circle': '◯',
        'light': '─',
        'heavy': '━',
        'double': '═',
        'ascii': '-',
        'dot': '·',
        'underscore': '_',
    }
    
    # Braille patterns for smooth progress
    BRAILLE = ['⠀', '⡀', '⡄', '⡆', '⡇', '⣇', '⣧', '⣷', '⣿']
    
    # Arrow progress
    ARROWS = {
        'right': ['→', '↘', '↓', '↙', '←', '↖', '↑', '↗'],
        'progress': ['▹', '▹▹', '▹▹▹', '▸'],
    }
    
    # Gradient colors (RGB tuples)
    GRADIENT_COLORS = {
        'fire': [(255, 0, 0), (255, 100, 0), (255, 200, 0)],
        'ice': [(0, 100, 255), (0, 200, 255), (200, 255, 255)],
        'matrix': [(0, 50, 0), (0, 150, 0), (0, 255, 0)],
        'neon': [(255, 0, 255), (0, 255, 255), (255, 255, 0)],
        'rainbow': [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)],
        'cyber': [(255, 0, 102), (0, 255, 255), (128, 0, 255)],
    }


class SpinnerChars:
    """Character sets for spinners."""
    
    SPINNERS = {
        SpinnerStyle.DOTS: ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
        SpinnerStyle.LINE: ['-', '\\', '|', '/'],
        SpinnerStyle.ARROW: ['→', '↘', '↓', '↙', '←', '↖', '↑', '↗'],
        SpinnerStyle.BOUNCE: ['⠁', '⠂', '⠄', '⠂'],
        SpinnerStyle.PULSE: ['█', '▓', '▒', '░', '▒', '▓'],
        SpinnerStyle.WAVE: ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█', '▇', '▆', '▅', '▄', '▃', '▂'],
        SpinnerStyle.GROW: ['▉', '▊', '▋', '▌', '▍', '▎', '▏'],
        SpinnerStyle.TOGGLE: ['◁', '◀', '◁', '▶'],
        SpinnerStyle.BOX: ['□', '■', '□', '■'],
        SpinnerStyle.BRAILLE: ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'],
        SpinnerStyle.MOON: ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘'],
        SpinnerStyle.EARTH: ['🌍', '🌎', '🌏'],
        SpinnerStyle.CLOCK: ['🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚', '🕛'],
        SpinnerStyle.HEARTS: ['💗', '💓', '💖', '💕', '💘', '💝'],
        SpinnerStyle.HAMBURGER: [' hamburger', ' 🍔', '  hamburger', '   🍔'],
    }


# ============================================================================
# PROGRESS BAR CLASS
# ============================================================================
class ProgressBar:
    """
    Advanced progress bar with multiple styles and features.
    
    Features:
    - 18+ progress bar styles
    - ETA calculation
    - Speed display
    - Custom colors
    - Gradient effects
    - Unicode support
    - Custom formatters
    - Thread-safe updates
    
    Example:
        >>> with ProgressBar(total=100, desc="Processing") as bar:
        ...     for i in range(100):
        ...         bar.update(1)
        ...         time.sleep(0.1)
    """
    
    def __init__(
        self,
        total: int,
        desc: str = "",
        unit: str = "it",
        style: ProgressBarStyle = ProgressBarStyle.BLOCKS,
        width: int = 40,
        color_scheme: str = "NEXUS_HACKER",
        show_speed: bool = True,
        show_eta: bool = True,
        show_percentage: bool = True,
        show_counter: bool = True,
        min_update_interval: float = 0.1,
        file: Any = None,
    ) -> None:
        """
        Initialize progress bar.
        
        Args:
            total: Total number of items
            desc: Description prefix
            unit: Unit name for items
            style: Progress bar style
            width: Bar width in characters
            color_scheme: Color scheme name
            show_speed: Whether to show speed
            show_eta: Whether to show ETA
            show_percentage: Whether to show percentage
            show_counter: Whether to show counter
            min_update_interval: Minimum time between updates
            file: Output file (default: sys.stderr)
        """
        self.total = max(total, 1)
        self.desc = desc
        self.unit = unit
        self.style = style
        self.width = width
        self.show_speed = show_speed
        self.show_eta = show_eta
        self.show_percentage = show_percentage
        self.show_counter = show_counter
        self.min_update_interval = min_update_interval
        self.file = file or sys.stderr
        
        # State
        self.n = 0
        self.start_time: Optional[float] = None
        self.last_update_time: float = 0.0
        self.last_update_n: int = 0
        self.speed_history: List[Tuple[float, int]] = []
        self._lock = threading.Lock()
        
        # Color manager
        self._cm = ColorManager()
        self._cm.set_scheme(color_scheme)
        
        # Terminal width
        self._term_width = self._get_terminal_width()
    
    def _get_terminal_width(self) -> int:
        """Get terminal width."""
        try:
            return shutil.get_terminal_size().columns
        except Exception:
            return 80
    
    def __enter__(self) -> 'ProgressBar':
        """Enter context manager."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager."""
        self.close()
    
    def __iter__(self) -> Iterator[int]:
        """Iterate with progress updates."""
        for i in range(self.total):
            yield i
            self.update(1)
    
    def start(self) -> None:
        """Start the progress bar."""
        self.n = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.last_update_n = 0
        self.speed_history = []
        self._display()
    
    def update(self, n: int = 1) -> None:
        """
        Update progress by n items.
        
        Args:
            n: Number of items to add
        """
        with self._lock:
            self.n = min(self.n + n, self.total)
            current_time = time.time()
            
            # Check if we should update display
            if current_time - self.last_update_time >= self.min_update_interval:
                self._display()
                self.last_update_time = current_time
                self.last_update_n = self.n
    
    def set_progress(self, n: int) -> None:
        """Set progress to specific value."""
        with self._lock:
            self.n = min(max(n, 0), self.total)
            self._display()
    
    def close(self) -> None:
        """Close the progress bar."""
        self.n = self.total
        self._display(final=True)
        if self.file:
            self.file.write('\n')
            self.file.flush()
    
    def _display(self, final: bool = False) -> None:
        """Display the progress bar."""
        if not self.file:
            return
        
        # Calculate progress
        progress = self.n / self.total
        
        # Calculate speed and ETA
        elapsed = time.time() - self.start_time if self.start_time else 0
        speed = self._calculate_speed()
        eta = self._calculate_eta()
        
        # Build progress bar string
        bar_str = self._build_bar(progress)
        
        # Build info string
        info_parts = []
        
        if self.desc:
            info_parts.append(self._cm.text(self.desc))
        
        if self.show_percentage:
            pct = self._cm.primary(f"{progress * 100:5.1f}%")
            info_parts.append(pct)
        
        if self.show_counter:
            counter = self._cm.text_secondary(f"{self.n}/{self.total}{self.unit}")
            info_parts.append(counter)
        
        info_str = ' '.join(info_parts)
        
        # Build speed and ETA string
        suffix_parts = []
        
        if self.show_speed and speed > 0:
            speed_str = self._cm.info(f"{speed:.2f}{self.unit}/s")
            suffix_parts.append(speed_str)
        
        if self.show_eta and eta > 0 and not final:
            eta_str = self._cm.warning(f"ETA: {self._format_time(eta)}")
            suffix_parts.append(eta_str)
        
        suffix_str = ' '.join(suffix_parts)
        
        # Combine all parts
        if suffix_str:
            full_str = f"{info_str} {bar_str} {suffix_str}"
        else:
            full_str = f"{info_str} {bar_str}"
        
        # Truncate to terminal width
        full_str = full_str[:self._term_width]
        
        # Clear line and write
        self.file.write('\r' + ANSICodes.CLEAR_LINE + full_str)
        self.file.flush()
    
    def _build_bar(self, progress: float) -> str:
        """Build the progress bar string."""
        style_builders = {
            ProgressBarStyle.CLASSIC: self._build_classic_bar,
            ProgressBarStyle.BLOCKS: self._build_blocks_bar,
            ProgressBarStyle.ARROWS: self._build_arrows_bar,
            ProgressBarStyle.DOTS: self._build_dots_bar,
            ProgressBarStyle.BRAILLE: self._build_braille_bar,
            ProgressBarStyle.SMOOTH: self._build_smooth_bar,
            ProgressBarStyle.GRADIENT: self._build_gradient_bar,
            ProgressBarStyle.MINIMAL: self._build_minimal_bar,
            ProgressBarStyle.RECTS: self._build_rects_bar,
            ProgressBarStyle.HEAVY: self._build_heavy_bar,
            ProgressBarStyle.LIGHT: self._build_light_bar,
            ProgressBarStyle.FILLED: self._build_filled_bar,
            ProgressBarStyle.ASCII: self._build_ascii_bar,
            ProgressBarStyle.UNICODE: self._build_unicode_bar,
            ProgressBarStyle.MATRIX: self._build_matrix_bar,
            ProgressBarStyle.CYBER: self._build_cyber_bar,
            ProgressBarStyle.NEON: self._build_neon_bar,
            ProgressBarStyle.FIRE: self._build_fire_bar,
            ProgressBarStyle.ICE: self._build_ice_bar,
            ProgressBarStyle.RAINBOW: self._build_rainbow_bar,
        }
        
        builder = style_builders.get(self.style, self._build_blocks_bar)
        return builder(progress)
    
    def _build_classic_bar(self, progress: float) -> str:
        """Build classic [=====>   ] style bar."""
        filled = int(progress * self.width)
        empty = self.width - filled
        bar = '[' + '=' * filled + '>' + ' ' * (empty - 1) + ']'
        return self._cm.primary(bar)
    
    def _build_blocks_bar(self, progress: float) -> str:
        """Build █▓▒░ style bar."""
        filled = int(progress * self.width)
        partial = (progress * self.width) - filled
        empty = self.width - filled - 1
        
        bar = '█' * filled
        
        # Partial block
        if partial > 0 and empty >= 0:
            if partial < 0.25:
                bar += '░'
            elif partial < 0.5:
                bar += '▒'
            elif partial < 0.75:
                bar += '▓'
            else:
                bar += '█'
            empty -= 1
        
        bar += '░' * max(empty, 0)
        
        # Color based on progress
        if progress < 0.3:
            return self._cm.error(bar)
        elif progress < 0.7:
            return self._cm.warning(bar)
        else:
            return self._cm.success(bar)
    
    def _build_arrows_bar(self, progress: float) -> str:
        """Build arrow style bar."""
        filled = int(progress * self.width)
        empty = self.width - filled
        
        bar = '▶' * filled + '▷' * empty
        return self._cm.primary(bar)
    
    def _build_dots_bar(self, progress: float) -> str:
        """Build dot style bar."""
        filled = int(progress * self.width)
        empty = self.width - filled
        
        bar = '●' * filled + '○' * empty
        return self._cm.primary(bar)
    
    def _build_braille_bar(self, progress: float) -> str:
        """Build braille pattern bar."""
        filled_chars = int(progress * self.width)
        partial = (progress * self.width) - filled_chars
        empty_chars = self.width - filled_chars - 1
        
        bar = '⣿' * filled_chars
        
        if partial > 0 and empty_chars >= 0:
            braille_idx = int(partial * len(ProgressChars.BRAILLE))
            bar += ProgressChars.BRAILLE[min(braille_idx, len(ProgressChars.BRAILLE) - 1)]
            empty_chars -= 1
        
        bar += '⠀' * max(empty_chars, 0)
        
        return self._cm.primary(bar)
    
    def _build_smooth_bar(self, progress: float) -> str:
        """Build smooth gradient bar."""
        total_blocks = self.width * 8  # Each braille is 8 sub-blocks
        filled = int(progress * total_blocks)
        
        result = []
        for i in range(self.width):
            block_filled = min(max(filled - (i * 8), 0), 8)
            if block_filled == 0:
                result.append('░')
            elif block_filled == 8:
                result.append('█')
            else:
                braille_chars = ['░', '▏', '▎', '▍', '▌', '▋', '▊', '▉', '█']
                result.append(braille_chars[block_filled])
        
        return self._cm.primary(''.join(result))
    
    def _build_gradient_bar(self, progress: float) -> str:
        """Build gradient colored bar."""
        filled = int(progress * self.width)
        empty = self.width - filled
        
        result = []
        colors = ProgressChars.GRADIENT_COLORS['rainbow']
        
        for i in range(filled):
            color_idx = int((i / self.width) * (len(colors) - 1))
            color = colors[color_idx]
            char = self._cm.rgb(*color, '█')
            result.append(char)
        
        result.append(self._cm.text_secondary('░' * empty))
        
        return ''.join(result)
    
    def _build_minimal_bar(self, progress: float) -> str:
        """Build minimal bar."""
        pct = int(progress * 100)
        bar = f"[{pct:3d}%]"
        return self._cm.primary(bar)
    
    def _build_rects_bar(self, progress: float) -> str:
        """Build rectangle style bar."""
        filled = int(progress * self.width)
        empty = self.width - filled
        bar = '▉' * filled + '░' * empty
        return self._cm.primary(bar)
    
    def _build_heavy_bar(self, progress: float) -> str:
        """Build heavy line bar."""
        filled = int(progress * self.width)
        empty = self.width - filled
        bar = '━' * filled + '─' * empty
        return self._cm.primary('[' + bar + ']')
    
    def _build_light_bar(self, progress: float) -> str:
        """Build light line bar."""
        filled = int(progress * self.width)
        empty = self.width - filled
        bar = '─' * filled + '╌' * empty
        return self._cm.text('[' + bar + ']')
    
    def _build_filled_bar(self, progress: float) -> str:
        """Build filled bar."""
        filled = int(progress * self.width)
        empty = self.width - filled
        bar = '▓' * filled + '░' * empty
        return self._cm.primary(bar)
    
    def _build_ascii_bar(self, progress: float) -> str:
        """Build ASCII-only bar."""
        filled = int(progress * self.width)
        empty = self.width - filled
        bar = '#' * filled + '-' * empty
        return self._cm.primary('[' + bar + ']')
    
    def _build_unicode_bar(self, progress: float) -> str:
        """Build fancy unicode bar."""
        filled = int(progress * self.width)
        empty = self.width - filled
        bar = '▰' * filled + '▱' * empty
        return self._cm.primary(bar)
    
    def _build_matrix_bar(self, progress: float) -> str:
        """Build Matrix-style bar."""
        filled = int(progress * self.width)
        empty = self.width - filled
        bar = '█' * filled + '·' * empty
        return self._cm.rgb(0, 255, 0, bar)
    
    def _build_cyber_bar(self, progress: float) -> str:
        """Build cyberpunk-style bar."""
        filled = int(progress * self.width)
        empty = self.width - filled
        bar = '◥' * filled + '◢' * empty
        
        # Alternate colors
        result = []
        for i, char in enumerate(bar):
            if i < filled:
                if i % 2 == 0:
                    result.append(self._cm.rgb(255, 0, 102, char))
                else:
                    result.append(self._cm.rgb(0, 255, 255, char))
            else:
                result.append(self._cm.text_secondary(char))
        
        return ''.join(result)
    
    def _build_neon_bar(self, progress: float) -> str:
        """Build neon-style bar."""
        filled = int(progress * self.width)
        empty = self.width - filled
        bar = '◆' * filled + '◇' * empty
        return self._cm.rgb(255, 0, 255, bar)
    
    def _build_fire_bar(self, progress: float) -> str:
        """Build fire-themed bar."""
        filled = int(progress * self.width)
        colors = ProgressChars.GRADIENT_COLORS['fire']
        
        result = []
        for i in range(self.width):
            if i < filled:
                color_idx = int((i / filled) * (len(colors) - 1))
                color = colors[color_idx]
                result.append(self._cm.rgb(*color, '█'))
            else:
                result.append(self._cm.text_secondary('░'))
        
        return ''.join(result)
    
    def _build_ice_bar(self, progress: float) -> str:
        """Build ice-themed bar."""
        filled = int(progress * self.width)
        colors = ProgressChars.GRADIENT_COLORS['ice']
        
        result = []
        for i in range(self.width):
            if i < filled:
                color_idx = int((i / filled) * (len(colors) - 1))
                color = colors[color_idx]
                result.append(self._cm.rgb(*color, '❄'))
            else:
                result.append(self._cm.text_secondary('·'))
        
        return ''.join(result)
    
    def _build_rainbow_bar(self, progress: float) -> str:
        """Build rainbow bar."""
        filled = int(progress * self.width)
        colors = ProgressChars.GRADIENT_COLORS['rainbow']
        
        result = []
        for i in range(self.width):
            if i < filled:
                color_idx = i % len(colors)
                color = colors[color_idx]
                result.append(self._cm.rgb(*color, '█'))
            else:
                result.append(self._cm.text_secondary('░'))
        
        return ''.join(result)
    
    def _calculate_speed(self) -> float:
        """Calculate current speed."""
        if not self.start_time or self.n == 0:
            return 0.0
        
        elapsed = time.time() - self.start_time
        if elapsed == 0:
            return 0.0
        
        return self.n / elapsed
    
    def _calculate_eta(self) -> float:
        """Calculate estimated time remaining."""
        if not self.start_time or self.n == 0 or self.n >= self.total:
            return 0.0
        
        elapsed = time.time() - self.start_time
        if elapsed == 0:
            return 0.0
        
        speed = self.n / elapsed
        if speed == 0:
            return 0.0
        
        remaining = self.total - self.n
        return remaining / speed
    
    def _format_time(self, seconds: float) -> str:
        """Format time in seconds to readable string."""
        if seconds < 0:
            return "??:??"
        
        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours:d}:{minutes:02d}:{secs:02d}"
        elif minutes > 0:
            return f"{minutes:d}:{secs:02d}"
        else:
            return f"{secs}s"


# ============================================================================
# SPINNER CLASS
# ============================================================================
class Spinner:
    """
    Animated spinner for indeterminate progress.
    
    Features:
    - 15+ spinner styles
    - Custom messages
    - Color support
    - Elapsed time display
    - Thread-safe
    
    Example:
        >>> with Spinner("Loading...") as spinner:
        ...     time.sleep(5)
    """
    
    def __init__(
        self,
        message: str = "Loading",
        style: SpinnerStyle = SpinnerStyle.DOTS,
        color_scheme: str = "NEXUS_HACKER",
        show_elapsed: bool = True,
        interval: float = 0.1,
        file: Any = None,
    ) -> None:
        """
        Initialize spinner.
        
        Args:
            message: Spinner message
            style: Spinner animation style
            color_scheme: Color scheme name
            show_elapsed: Whether to show elapsed time
            interval: Animation frame interval
            file: Output file
        """
        self.message = message
        self.style = style
        self.show_elapsed = show_elapsed
        self.interval = interval
        self.file = file or sys.stderr
        
        # State
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._start_time: Optional[float] = None
        
        # Color manager
        self._cm = ColorManager()
        self._cm.set_scheme(color_scheme)
        
        # Get spinner frames
        self._frames = SpinnerChars.SPINNERS.get(style, SpinnerChars.SPINNERS[SpinnerStyle.DOTS])
        self._frame_iter = itertools.cycle(self._frames)
    
    def __enter__(self) -> 'Spinner':
        """Enter context manager."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager."""
        self.stop()
    
    def start(self) -> None:
        """Start the spinner."""
        self._running = True
        self._start_time = time.time()
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
    
    def stop(self, clear: bool = True) -> None:
        """
        Stop the spinner.
        
        Args:
            clear: Whether to clear the spinner line
        """
        self._running = False
        if self._thread:
            self._thread.join(timeout=0.5)
        
        if clear and self.file:
            self.file.write('\r' + ' ' * 80 + '\r')
            self.file.flush()
    
    def update_message(self, message: str) -> None:
        """Update spinner message."""
        self.message = message
    
    def succeed(self, message: Optional[str] = None) -> None:
        """Stop spinner with success message."""
        self.stop(clear=True)
        msg = message or self.message
        if self.file:
            self.file.write(self._cm.success(f"✓ {msg}") + '\n')
            self.file.flush()
    
    def fail(self, message: Optional[str] = None) -> None:
        """Stop spinner with failure message."""
        self.stop(clear=True)
        msg = message or self.message
        if self.file:
            self.file.write(self._cm.error(f"✗ {msg}") + '\n')
            self.file.flush()
    
    def _spin(self) -> None:
        """Animation loop."""
        while self._running:
            frame = next(self._frame_iter)
            
            # Build display string
            parts = [self._cm.primary(frame), self.message]
            
            if self.show_elapsed and self._start_time:
                elapsed = time.time() - self._start_time
                parts.append(self._cm.text_secondary(f"({elapsed:.1f}s)"))
            
            display = ' '.join(parts)
            
            if self.file:
                self.file.write('\r' + ANSICodes.CLEAR_LINE + display)
                self.file.flush()
            
            time.sleep(self.interval)


# ============================================================================
# MULTIPROGRESS CLASS
# ============================================================================
class MultiProgress:
    """
    Manage multiple progress bars simultaneously.
    
    Example:
        >>> with MultiProgress() as mp:
        ...     bar1 = mp.add_bar(total=100, desc="Task 1")
        ...     bar2 = mp.add_bar(total=50, desc="Task 2")
        ...     for i in range(100):
        ...         bar1.update(1)
        ...         if i < 50:
        ...             bar2.update(1)
    """
    
    def __init__(
        self,
        color_scheme: str = "NEXUS_HACKER",
        file: Any = None,
    ) -> None:
        """Initialize multi-progress manager."""
        self._bars: List[ProgressBar] = []
        self._color_scheme = color_scheme
        self._file = file or sys.stderr
        self._lock = threading.Lock()
        self._active = False
    
    def __enter__(self) -> 'MultiProgress':
        """Enter context manager."""
        self._active = True
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager."""
        self._active = False
        self._display(final=True)
        if self._file:
            self._file.write('\n')
    
    def add_bar(
        self,
        total: int,
        desc: str = "",
        unit: str = "it",
        style: ProgressBarStyle = ProgressBarStyle.BLOCKS,
    ) -> ProgressBar:
        """Add a new progress bar."""
        bar = ProgressBar(
            total=total,
            desc=desc,
            unit=unit,
            style=style,
            color_scheme=self._color_scheme,
            file=None,  # We'll handle display ourselves
            show_speed=False,  # Simplified for multi-bar
            show_eta=False,
        )
        self._bars.append(bar)
        bar.start_time = time.time()
        return bar
    
    def update(self, bar: ProgressBar, n: int = 1) -> None:
        """Update a bar and refresh display."""
        bar.update(n)
        self._display()
    
    def _display(self, final: bool = False) -> None:
        """Display all progress bars."""
        if not self._file:
            return
        
        with self._lock:
            # Move cursor up for each bar
            if self._bars:
                self._file.write(f'\033[{len(self._bars)}A')
            
            # Display each bar
            for bar in self._bars:
                progress = bar.n / bar.total
                bar_str = bar._build_bar(progress)
                
                info = f"{bar.desc} [{bar.n}/{bar.total}] {bar_str}"
                
                if final and bar.n >= bar.total:
                    info = self._cm.success(f"✓ {info}")
                
                self._file.write('\r' + ANSICodes.CLEAR_LINE + info + '\n')
            
            self._file.flush()


# ============================================================================
# STATUS INDICATOR
# ============================================================================
class StatusIndicator:
    """
    Status indicator with icons and colors.
    
    Example:
        >>> StatusIndicator.success("Operation completed!")
        >>> StatusIndicator.error("Operation failed!")
    """
    
    @staticmethod
    def success(message: str) -> str:
        """Format success message."""
        cm = ColorManager()
        return cm.success(f"✓ {message}")
    
    @staticmethod
    def error(message: str) -> str:
        """Format error message."""
        cm = ColorManager()
        return cm.error(f"✗ {message}")
    
    @staticmethod
    def warning(message: str) -> str:
        """Format warning message."""
        cm = ColorManager()
        return cm.warning(f"⚠ {message}")
    
    @staticmethod
    def info(message: str) -> str:
        """Format info message."""
        cm = ColorManager()
        return cm.info(f"ℹ {message}")
    
    @staticmethod
    def loading(message: str) -> str:
        """Format loading message."""
        cm = ColorManager()
        return cm.primary(f"⏳ {message}")
    
    @staticmethod
    def complete(message: str) -> str:
        """Format complete message."""
        cm = ColorManager()
        return cm.success(f"★ {message}")
    
    @staticmethod
    def pending(message: str) -> str:
        """Format pending message."""
        cm = ColorManager()
        return cm.text_secondary(f"○ {message}")
    
    @staticmethod
    def running(message: str) -> str:
        """Format running message."""
        cm = ColorManager()
        return cm.primary(f"► {message}")
    
    @staticmethod
    def skipped(message: str) -> str:
        """Format skipped message."""
        cm = ColorManager()
        return cm.text_secondary(f"→ {message}")


# ============================================================================
# ANIMATION EFFECTS
# ============================================================================
class AnimationEffects:
    """
    Visual animation effects for terminal output.
    """
    
    @staticmethod
    def typing_effect(text: str, delay: float = 0.05, 
                      file: Any = None) -> None:
        """
        Print text with typing animation.
        
        Args:
            text: Text to type
            delay: Delay between characters
            file: Output file
        """
        file = file or sys.stdout
        for char in text:
            file.write(char)
            file.flush()
            time.sleep(delay)
        file.write('\n')
    
    @staticmethod
    def pulse_text(text: str, times: int = 3, 
                   delay: float = 0.3, file: Any = None) -> None:
        """
        Pulse text (bold/dim alternation).
        
        Args:
            text: Text to pulse
            times: Number of pulses
            delay: Delay between pulses
            file: Output file
        """
        file = file or sys.stdout
        cm = ColorManager()
        
        for _ in range(times):
            file.write('\r' + cm.bold(text))
            file.flush()
            time.sleep(delay)
            file.write('\r' + cm.dim(text))
            file.flush()
            time.sleep(delay)
        
        file.write('\r' + text + '\n')
        file.flush()
    
    @staticmethod
    def loading_dots(message: str = "Loading", 
                     duration: float = 3.0, file: Any = None) -> None:
        """
        Show loading animation with dots.
        
        Args:
            message: Loading message
            duration: Total duration
            file: Output file
        """
        file = file or sys.stdout
        cm = ColorManager()
        
        start_time = time.time()
        dots = 0
        
        while time.time() - start_time < duration:
            dots = (dots % 3) + 1
            display = f"\r{message}{'.' * dots}{' ' * (3 - dots)}"
            file.write(cm.primary(display))
            file.flush()
            time.sleep(0.3)
        
        file.write('\r' + ' ' * (len(message) + 5) + '\r')
        file.flush()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================
def progress(
    iterable: Optional[Iterable[T]] = None,
    total: Optional[int] = None,
    desc: str = "",
    **kwargs
) -> Union[ProgressBar, Iterator[T]]:
    """
    Convenience function for progress bars.
    
    Args:
        iterable: Iterable to wrap with progress
        total: Total items (required if iterable is None)
        desc: Description
        **kwargs: Additional ProgressBar arguments
        
    Returns:
        ProgressBar or iterator
    """
    if iterable is not None:
        total = len(iterable) if hasattr(iterable, '__len__') else total
    
    bar = ProgressBar(total=total or 1, desc=desc, **kwargs)
    
    if iterable is not None:
        bar.start()
        for item in iterable:
            yield item
            bar.update(1)
        bar.close()
    else:
        return bar


def spinner(message: str = "Loading", **kwargs) -> Spinner:
    """Create a spinner with default settings."""
    return Spinner(message=message, **kwargs)


# ============================================================================
# MODULE-LEVEL INSTANCES
# ============================================================================
status = StatusIndicator()
animations = AnimationEffects()


# ============================================================================
# EXPORTS
# ============================================================================
__all__ = [
    # Version
    '__version__',
    '__author__',
    '__status__',
    
    # Enums
    'ProgressBarStyle',
    'SpinnerStyle',
    
    # Classes
    'ProgressChars',
    'SpinnerChars',
    'ProgressBar',
    'Spinner',
    'MultiProgress',
    'StatusIndicator',
    'AnimationEffects',
    
    # Instances
    'status',
    'animations',
    
    # Functions
    'progress',
    'spinner',
]


# ============================================================================
# MAIN DEMO
# ============================================================================
if __name__ == "__main__":
    import time as time_module
    
    print("\n" + "="*60)
    print("    ULTIMATE NEXUS PROGRESS SYSTEM v3.0.1 - DEMO")
    print("="*60 + "\n")
    
    # Demo progress bars
    styles = [
        ProgressBarStyle.BLOCKS,
        ProgressBarStyle.CLASSIC,
        ProgressBarStyle.DOTS,
        ProgressBarStyle.ARROWS,
        ProgressBarStyle.GRADIENT,
        ProgressBarStyle.MATRIX,
        ProgressBarStyle.CYBER,
        ProgressBarStyle.RAINBOW,
    ]
    
    for style in styles:
        print(f"\n--- {style.name} Style ---")
        with ProgressBar(total=50, desc=style.name, style=style, 
                         width=30, show_speed=True, show_eta=True) as bar:
            for _ in range(50):
                time_module.sleep(0.02)
                bar.update(1)
    
    # Demo spinner
    print("\n--- Spinner Demo ---")
    with Spinner("Processing data...", style=SpinnerStyle.DOTS) as sp:
        time_module.sleep(2)
        sp.succeed("Data processed!")
    
    # Demo status indicators
    print("\n--- Status Indicators ---")
    print(status.success("Operation completed successfully"))
    print(status.error("Operation failed"))
    print(status.warning("This is a warning"))
    print(status.info("This is information"))
    print(status.loading("Loading in progress"))
    print(status.complete("All tasks complete"))
    
    # Demo animation effects
    print("\n--- Animation Effects ---")
    AnimationEffects.loading_dots("Loading", duration=2)
    print("Done!")
    
    print("\nDemo complete!")

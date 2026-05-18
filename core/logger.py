#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - Logger System                               ║
║  Author: RS (T3rmuxk1ng)                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import logging
from datetime import datetime
from typing import Optional


class Logger:
    """
    Comprehensive logging system for RS Toolkit
    - Console output with colors
    - File logging
    - Termux compatible
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, log_dir: str = None, log_level: int = logging.DEBUG):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self._initialized = True
        
        # Setup log directory
        if log_dir is None:
            if os.name == 'nt':  # Windows
                base_dir = os.path.expanduser('~')
            elif 'TERMUX_VERSION' in os.environ:  # Termux
                base_dir = os.path.expanduser('~/storage/downloads')
            else:  # Linux/Mac
                base_dir = os.path.expanduser('~')
            
            log_dir = os.path.join(base_dir, '.rs_downloader', 'logs')
        
        os.makedirs(log_dir, exist_ok=True)
        
        # Log file path
        self.log_file = os.path.join(log_dir, f'toolkit_{datetime.now().strftime("%Y%m%d")}.log')
        
        # Create logger
        self.logger = logging.getLogger('RS_Toolkit')
        self.logger.setLevel(log_level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Color codes
        self.colors = {
            'DEBUG': '\033[36m',     # Cyan
            'INFO': '\033[92m',      # Green
            'WARNING': '\033[93m',   # Yellow
            'ERROR': '\033[91m',     # Red
            'CRITICAL': '\033[95m',  # Magenta
            'RESET': '\033[0m'
        }
    
    def _format_console(self, level: str, message: str) -> str:
        """Format console message with colors"""
        color = self.colors.get(level, self.colors['RESET'])
        reset = self.colors['RESET']
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        icons = {
            'DEBUG': '🔍',
            'INFO': '✓',
            'WARNING': '⚠',
            'ERROR': '✗',
            'CRITICAL': '💀'
        }
        icon = icons.get(level, '•')
        
        return f"{color}[{icon}] [{timestamp}] {message}{reset}"
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(self._format_console('DEBUG', message))
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(self._format_console('INFO', message))
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(self._format_console('WARNING', message))
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(self._format_console('ERROR', message))
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(self._format_console('CRITICAL', message))
    
    def success(self, message: str):
        """Log success message (green with checkmark)"""
        self.info(message)
    
    def download_progress(self, filename: str, downloaded: int, total: int, speed: str = None):
        """Log download progress"""
        percent = (downloaded / total * 100) if total > 0 else 0
        msg = f"Downloading: {filename} - {percent:.1f}%"
        if speed:
            msg += f" - {speed}"
        self.debug(msg)
    
    def get_log_file(self) -> str:
        """Get log file path"""
        return self.log_file
    
    def clear_old_logs(self, days: int = 30):
        """Clear logs older than specified days"""
        import glob
        import time
        
        cutoff = time.time() - (days * 86400)
        
        for log_file in glob.glob(os.path.join(os.path.dirname(self.log_file), 'toolkit_*.log')):
            if os.path.getmtime(log_file) < cutoff:
                try:
                    os.remove(log_file)
                except:
                    pass


# Global logger instance
logger = Logger()

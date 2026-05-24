#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - Configuration Manager                       ║
║  Author: RS (T3rmuxk1ng)                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import json
from typing import Any, Dict, Optional
from pathlib import Path


class ConfigManager:
    """
    Configuration Manager for RS Toolkit
    - Save/Load user preferences
    - Default configurations
    - Termux compatible paths
    """

    _instance = None
    DEFAULT_CONFIG = {
        "version": "2.0.0",
        "author": "RS (T3rmuxk1ng)",
        "output_paths": {
            "videos": "output/videos",
            "audio": "output/audio",
            "thumbnails": "output/thumbnails",
            "subtitles": "output/subtitles",
            "metadata": "output/metadata"
        },
        "video": {
            "default_quality": "1080p",
            "default_format": "mp4",
            "preferred_codec": "h264"
        },
        "audio": {
            "default_quality": "320",
            "default_format": "mp3",
            "embed_thumbnail": True,
            "embed_metadata": True
        },
        "playlist": {
            "parallel_downloads": 3,
            "skip_existing": True,
            "create_subfolder": True
        },
        "subtitle": {
            "languages": ["en", "hi"],
            "include_auto_generated": True,
            "format": "srt"
        },
        "network": {
            "proxy_enabled": False,
            "proxy_type": "http",
            "proxy_host": "127.0.0.1",
            "proxy_port": 8080,
            "timeout": 30,
            "retry_count": 3,
            "rate_limit": 0
        },
        "ui": {
            "theme": "hacker_green",
            "show_progress": True,
            "sound_notification": False,
            "animation_speed": "normal"
        },
        "history": [],
        "favorites": []
    }

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_dir: str = None):
        if hasattr(self, '_initialized') and self._initialized:
            return

        self._initialized = True

        # Determine config directory
        if config_dir is None:
            if os.name == 'nt':  # Windows
                base_dir = os.path.expanduser('~')
            elif 'TERMUX_VERSION' in os.environ:  # Termux
                base_dir = os.path.expanduser('~/storage/downloads')
            else:  # Linux/Mac
                base_dir = os.path.expanduser('~')

            config_dir = os.path.join(base_dir, '.rs_downloader')

        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, 'config.json')

        # Create config directory
        os.makedirs(config_dir, exist_ok=True)

        # Load or create config
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load config from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Merge with defaults for missing keys
                return self._merge_with_defaults(config)
            except (json.JSONDecodeError, IOError):
                pass

        # Create default config
        self._save_config(self.DEFAULT_CONFIG)
        return self.DEFAULT_CONFIG.copy()

    def _merge_with_defaults(self, config: Dict) -> Dict:
        """Merge loaded config with defaults"""
        merged = self.DEFAULT_CONFIG.copy()

        def deep_merge(base: dict, update: dict):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value

        deep_merge(merged, config)
        return merged

    def _save_config(self, config: Dict = None):
        """Save config to file"""
        if config is None:
            config = self.config

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by key (supports dot notation)"""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any, save: bool = True):
        """Set config value by key (supports dot notation)"""
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

        if save:
            self._save_config()

    def get_output_path(self, path_type: str = "videos") -> str:
        """Get output path for specific type"""
        relative_path = self.get(f"output_paths.{path_type}", f"output/{path_type}")

        # Convert to absolute path
        if not os.path.isabs(relative_path):
            relative_path = os.path.join(self.config_dir, '..', relative_path)

        # Create directory if not exists
        os.makedirs(relative_path, exist_ok=True)

        return os.path.abspath(relative_path)

    def add_to_history(self, entry: Dict):
        """Add entry to download history"""
        history = self.get('history', [])

        # Add timestamp
        entry['timestamp'] = str(int(os.times().elapsed * 1000)) if hasattr(os.times(), 'elapsed') else ''

        # Keep last 100 entries
        history.insert(0, entry)
        history = history[:100]

        self.set('history', history)

    def get_history(self, limit: int = 10) -> list:
        """Get download history"""
        return self.get('history', [])[:limit]

    def clear_history(self):
        """Clear download history"""
        self.set('history', [])

    def add_favorite(self, url: str, name: str = ""):
        """Add URL to favorites"""
        favorites = self.get('favorites', [])
        favorites.append({'url': url, 'name': name or url})
        self.set('favorites', favorites)

    def get_favorites(self) -> list:
        """Get favorite URLs"""
        return self.get('favorites', [])

    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.config = self.DEFAULT_CONFIG.copy()
        self._save_config()

    def export_config(self, export_path: str):
        """Export config to file"""
        import shutil
        shutil.copy(self.config_file, export_path)

    def import_config(self, import_path: str):
        """Import config from file"""
        with open(import_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.config = self._merge_with_defaults(config)
        self._save_config()


# Global config instance
config = ConfigManager()

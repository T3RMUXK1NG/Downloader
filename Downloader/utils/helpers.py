#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        ULTIMATE NEXUS HELPER FUNCTIONS                        ║
║                              v3.0.1 SOVEREIGN EDITION                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Author: RAJSARASWATI JATAV (RS) - OMNIPOTENT SOVEREIGN NEXUS                ║
║  Channel: T3rmuxk1ng                                                         ║
║  Description: Comprehensive helper functions for file operations, network,   ║
║               string manipulation, system utilities, and more                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import os
import sys
import re
import json
import csv
import math
import time
import random
import string
import hashlib
import secrets
import base64
import pickle
import shutil
import tempfile
import platform
import subprocess
import threading
import multiprocessing
import urllib.parse
import urllib.request
import zipfile
import gzip
import tarfile
from datetime import datetime, timedelta
from typing import (
    Dict, List, Tuple, Optional, Union, Callable, Any, 
    Iterator, Generator, TypeVar, Generic, Set, FrozenSet,
    Sequence, Mapping, MutableMapping, Iterable, Container,
    Hashable, Reversible, SupportsInt, SupportsFloat,
)
from dataclasses import dataclass, field
from functools import wraps, lru_cache, reduce
from collections import defaultdict, Counter, OrderedDict
from contextlib import contextmanager, suppress
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

# ============================================================================
# VERSION INFORMATION
# ============================================================================
__version__ = "3.0.1"
__author__ = "RAJSARASWATI JATAV (RS)"
__status__ = "OMNIPOTENT SOVEREIGN"

# ============================================================================
# TYPE VARIABLES
# ============================================================================
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')
R = TypeVar('R')

# ============================================================================
# FILE OPERATIONS
# ============================================================================
class FileHelpers:
    """
    Comprehensive file operation utilities.
    
    Features:
    - Safe file operations with error handling
    - Atomic file writes
    - File locking
    - Compression support
    - Batch operations
    - File monitoring
    """
    
    @staticmethod
    def read_file(filepath: Union[str, Path], encoding: str = 'utf-8', 
                  default: str = "") -> str:
        """
        Safely read file contents.
        
        Args:
            filepath: Path to the file
            encoding: File encoding
            default: Default value if file doesn't exist
            
        Returns:
            File contents or default value
        """
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except (FileNotFoundError, UnicodeDecodeError, IOError):
            return default
    
    @staticmethod
    def write_file(filepath: Union[str, Path], content: str, 
                   encoding: str = 'utf-8', mode: str = 'w') -> bool:
        """
        Safely write content to file.
        
        Args:
            filepath: Path to the file
            content: Content to write
            encoding: File encoding
            mode: Write mode ('w' for write, 'a' for append)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, mode, encoding=encoding) as f:
                f.write(content)
            return True
        except (IOError, OSError):
            return False
    
    @staticmethod
    def read_json(filepath: Union[str, Path], default: Any = None) -> Any:
        """
        Read JSON file safely.
        
        Args:
            filepath: Path to the JSON file
            default: Default value if reading fails
            
        Returns:
            Parsed JSON data or default value
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, IOError):
            return default if default is not None else {}
    
    @staticmethod
    def write_json(filepath: Union[str, Path], data: Any, 
                   indent: int = 2, sort_keys: bool = True) -> bool:
        """
        Write JSON file safely.
        
        Args:
            filepath: Path to the JSON file
            data: Data to write
            indent: JSON indentation
            sort_keys: Whether to sort keys
            
        Returns:
            True if successful, False otherwise
        """
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, sort_keys=sort_keys, 
                         ensure_ascii=False)
            return True
        except (IOError, TypeError, ValueError):
            return False
    
    @staticmethod
    def read_lines(filepath: Union[str, Path], strip: bool = True,
                   skip_empty: bool = True) -> List[str]:
        """
        Read file as list of lines.
        
        Args:
            filepath: Path to the file
            strip: Whether to strip whitespace
            skip_empty: Whether to skip empty lines
            
        Returns:
            List of lines
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if strip:
                lines = [line.strip() for line in lines]
            if skip_empty:
                lines = [line for line in lines if line]
            return lines
        except FileNotFoundError:
            return []
    
    @staticmethod
    def append_line(filepath: Union[str, Path], line: str) -> bool:
        """Append a line to file."""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(line + '\n')
            return True
        except IOError:
            return False
    
    @staticmethod
    def read_csv(filepath: Union[str, Path], delimiter: str = ',',
                 has_header: bool = True) -> List[Dict[str, str]]:
        """
        Read CSV file as list of dictionaries.
        
        Args:
            filepath: Path to the CSV file
            delimiter: CSV delimiter
            has_header: Whether CSV has header row
            
        Returns:
            List of row dictionaries
        """
        try:
            with open(filepath, 'r', encoding='utf-8', newline='') as f:
                if has_header:
                    reader = csv.DictReader(f, delimiter=delimiter)
                    return list(reader)
                else:
                    reader = csv.reader(f, delimiter=delimiter)
                    return [{'col_' + str(i): v for i, v in enumerate(row)} 
                           for row in reader]
        except (FileNotFoundError, csv.Error):
            return []
    
    @staticmethod
    def write_csv(filepath: Union[str, Path], data: List[Dict], 
                  fieldnames: Optional[List[str]] = None) -> bool:
        """
        Write list of dictionaries to CSV file.
        
        Args:
            filepath: Path to the CSV file
            data: List of row dictionaries
            fieldnames: Column names (auto-detected if None)
            
        Returns:
            True if successful, False otherwise
        """
        if not data:
            return False
        
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            if fieldnames is None:
                fieldnames = list(data[0].keys())
            
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True
        except (IOError, csv.Error):
            return False
    
    @staticmethod
    def get_file_size(filepath: Union[str, Path]) -> int:
        """Get file size in bytes."""
        try:
            return os.path.getsize(filepath)
        except OSError:
            return 0
    
    @staticmethod
    def get_file_size_formatted(filepath: Union[str, Path]) -> str:
        """Get file size as formatted string."""
        size = FileHelpers.get_file_size(filepath)
        return format_size(size)
    
    @staticmethod
    def get_file_hash(filepath: Union[str, Path], algorithm: str = 'sha256') -> str:
        """
        Calculate file hash.
        
        Args:
            filepath: Path to the file
            algorithm: Hash algorithm ('md5', 'sha1', 'sha256', 'sha512')
            
        Returns:
            Hexadecimal hash string
        """
        hash_func = getattr(hashlib, algorithm, hashlib.sha256)()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except OSError:
            return ""
    
    @staticmethod
    def copy_file(src: Union[str, Path], dst: Union[str, Path], 
                  overwrite: bool = False) -> bool:
        """
        Copy file safely.
        
        Args:
            src: Source file path
            dst: Destination file path
            overwrite: Whether to overwrite existing file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not overwrite and Path(dst).exists():
                return False
            Path(dst).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            return True
        except (OSError, shutil.Error):
            return False
    
    @staticmethod
    def move_file(src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """Move file safely."""
        try:
            Path(dst).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            return True
        except (OSError, shutil.Error):
            return False
    
    @staticmethod
    def delete_file(filepath: Union[str, Path], missing_ok: bool = True) -> bool:
        """Delete file safely."""
        try:
            Path(filepath).unlink(missing_ok=missing_ok)
            return True
        except OSError:
            return False
    
    @staticmethod
    def ensure_directory(dirpath: Union[str, Path]) -> bool:
        """Ensure directory exists, create if necessary."""
        try:
            Path(dirpath).mkdir(parents=True, exist_ok=True)
            return True
        except OSError:
            return False
    
    @staticmethod
    def list_files(directory: Union[str, Path], pattern: str = '*',
                   recursive: bool = False) -> List[Path]:
        """
        List files in directory.
        
        Args:
            directory: Directory path
            pattern: File pattern (glob)
            recursive: Whether to search recursively
            
        Returns:
            List of file paths
        """
        try:
            dirpath = Path(directory)
            if recursive:
                return list(dirpath.rglob(pattern))
            else:
                return [f for f in dirpath.glob(pattern) if f.is_file()]
        except OSError:
            return []
    
    @staticmethod
    def list_directories(directory: Union[str, Path], 
                         recursive: bool = False) -> List[Path]:
        """List subdirectories."""
        try:
            dirpath = Path(directory)
            if recursive:
                return [d for d in dirpath.rglob('*') if d.is_dir()]
            else:
                return [d for d in dirpath.iterdir() if d.is_dir()]
        except OSError:
            return []
    
    @staticmethod
    def compress_files(files: List[Union[str, Path]], output: Union[str, Path],
                       compression: str = 'zip') -> bool:
        """
        Compress files into archive.
        
        Args:
            files: List of file paths to compress
            output: Output archive path
            compression: Compression type ('zip', 'tar', 'gztar')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if compression == 'zip':
                with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for file in files:
                        file = Path(file)
                        zf.write(file, file.name)
            else:
                mode = 'w:gz' if compression == 'gztar' else 'w'
                with tarfile.open(output, mode) as tf:
                    for file in files:
                        tf.add(file, arcname=Path(file).name)
            return True
        except (OSError, zipfile.BadZipFile, tarfile.TarError):
            return False
    
    @staticmethod
    def extract_archive(archive: Union[str, Path], destination: Union[str, Path]) -> bool:
        """Extract archive to destination."""
        try:
            Path(destination).mkdir(parents=True, exist_ok=True)
            archive = Path(archive)
            
            if archive.suffix == '.zip':
                with zipfile.ZipFile(archive, 'r') as zf:
                    zf.extractall(destination)
            elif archive.suffix in ('.tar', '.gz', '.tgz'):
                with tarfile.open(archive, 'r:*') as tf:
                    tf.extractall(destination)
            else:
                return False
            return True
        except (OSError, zipfile.BadZipFile, tarfile.TarError):
            return False
    
    @staticmethod
    def get_file_info(filepath: Union[str, Path]) -> Dict[str, Any]:
        """Get comprehensive file information."""
        try:
            path = Path(filepath)
            stat = path.stat()
            return {
                'path': str(path.absolute()),
                'name': path.name,
                'stem': path.stem,
                'extension': path.suffix,
                'size_bytes': stat.st_size,
                'size_formatted': format_size(stat.st_size),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
                'is_file': path.is_file(),
                'is_directory': path.is_dir(),
                'is_symlink': path.is_symlink(),
                'exists': path.exists(),
            }
        except OSError:
            return {}
    
    @staticmethod
    def watch_file(filepath: Union[str, Path], callback: Callable[[str], None],
                   interval: float = 1.0) -> None:
        """
        Watch file for changes.
        
        Args:
            filepath: Path to watch
            callback: Function to call when file changes
            interval: Check interval in seconds
        """
        last_modified = 0
        while True:
            try:
                current_modified = Path(filepath).stat().st_mtime
                if current_modified != last_modified:
                    last_modified = current_modified
                    callback(str(filepath))
            except OSError:
                pass
            time.sleep(interval)


# ============================================================================
# STRING OPERATIONS
# ============================================================================
class StringHelpers:
    """
    Comprehensive string manipulation utilities.
    
    Features:
    - Text transformations
    - Pattern matching
    - Encoding/decoding
    - String generation
    - Text cleaning
    """
    
    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = '...') -> str:
        """Truncate text to max length with suffix."""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def truncate_middle(text: str, max_length: int, 
                        separator: str = '...') -> str:
        """Truncate text from the middle."""
        if len(text) <= max_length:
            return text
        half = (max_length - len(separator)) // 2
        return text[:half] + separator + text[-half:]
    
    @staticmethod
    def pad_center(text: str, width: int, fillchar: str = ' ') -> str:
        """Center pad text."""
        return text.center(width, fillchar)
    
    @staticmethod
    def pad_left(text: str, width: int, fillchar: str = ' ') -> str:
        """Left pad text (right align)."""
        return text.rjust(width, fillchar)
    
    @staticmethod
    def pad_right(text: str, width: int, fillchar: str = ' ') -> str:
        """Right pad text (left align)."""
        return text.ljust(width, fillchar)
    
    @staticmethod
    def strip_ansi(text: str) -> str:
        """Remove ANSI escape codes from text."""
        ansi_pattern = re.compile(r'\033\[[0-9;]*[mGKH]')
        return ansi_pattern.sub('', text)
    
    @staticmethod
    def strip_html(text: str) -> str:
        """Remove HTML tags from text."""
        clean = re.compile(r'<[^>]+>')
        return clean.sub('', text)
    
    @staticmethod
    def slugify(text: str, separator: str = '-') -> str:
        """
        Convert text to URL-safe slug.
        
        Args:
            text: Text to convert
            separator: Word separator
            
        Returns:
            URL-safe slug string
        """
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_-]+', separator, text)
        return text.strip(separator)
    
    @staticmethod
    def camel_to_snake(text: str) -> str:
        """Convert camelCase to snake_case."""
        text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', text)
        text = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', text)
        return text.lower()
    
    @staticmethod
    def snake_to_camel(text: str, capitalize_first: bool = False) -> str:
        """Convert snake_case to camelCase."""
        components = text.split('_')
        if capitalize_first:
            return ''.join(x.title() for x in components)
        return components[0] + ''.join(x.title() for x in components[1:])
    
    @staticmethod
    def title_case(text: str) -> str:
        """Convert to title case (handles special words)."""
        minor_words = {'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 
                      'in', 'nor', 'of', 'on', 'or', 'so', 'the', 'to', 'up', 'yet'}
        words = text.lower().split()
        result = []
        for i, word in enumerate(words):
            if i == 0 or word not in minor_words:
                result.append(word.capitalize())
            else:
                result.append(word)
        return ' '.join(result)
    
    @staticmethod
    def reverse_words(text: str) -> str:
        """Reverse word order in text."""
        return ' '.join(text.split()[::-1])
    
    @staticmethod
    def reverse_chars(text: str) -> str:
        """Reverse character order in text."""
        return text[::-1]
    
    @staticmethod
    def word_wrap(text: str, width: int = 80) -> str:
        """Wrap text at specified width."""
        lines = []
        for paragraph in text.split('\n'):
            if len(paragraph) <= width:
                lines.append(paragraph)
            else:
                words = paragraph.split()
                current_line = []
                current_length = 0
                for word in words:
                    if current_length + len(word) + 1 <= width:
                        current_line.append(word)
                        current_length += len(word) + 1
                    else:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                        current_length = len(word)
                if current_line:
                    lines.append(' '.join(current_line))
        return '\n'.join(lines)
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text."""
        return len(text.split())
    
    @staticmethod
    def count_chars(text: str, include_spaces: bool = True) -> int:
        """Count characters in text."""
        if include_spaces:
            return len(text)
        return len(text.replace(' ', ''))
    
    @staticmethod
    def count_lines(text: str) -> int:
        """Count lines in text."""
        return len(text.splitlines())
    
    @staticmethod
    def generate_random_string(length: int = 16, 
                               chars: str = string.ascii_letters + string.digits) -> str:
        """Generate random string."""
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    @staticmethod
    def generate_password(length: int = 16, 
                          include_special: bool = True) -> str:
        """Generate secure password."""
        chars = string.ascii_letters + string.digits
        if include_special:
            chars += '!@#$%^&*()_+-=[]{}|;:,.<>?'
        
        # Ensure at least one of each type
        password = [
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.digits),
        ]
        if include_special:
            password.append(secrets.choice('!@#$%^&*'))
        
        # Fill rest
        password.extend(secrets.choice(chars) for _ in range(length - len(password)))
        
        # Shuffle
        result = list(password)
        secrets.SystemRandom().shuffle(result)
        return ''.join(result)
    
    @staticmethod
    def generate_uuid() -> str:
        """Generate UUID string."""
        import uuid
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_short_id(length: int = 8) -> str:
        """Generate short unique ID."""
        import uuid
        return uuid.uuid4().hex[:length]
    
    @staticmethod
    def generate_hex(length: int = 16) -> str:
        """Generate random hex string."""
        return secrets.token_hex(length // 2 + 1)[:length]
    
    @staticmethod
    def base64_encode(data: str) -> str:
        """Base64 encode string."""
        return base64.b64encode(data.encode()).decode()
    
    @staticmethod
    def base64_decode(data: str) -> str:
        """Base64 decode string."""
        return base64.b64decode(data.encode()).decode()
    
    @staticmethod
    def rot13(text: str) -> str:
        """Apply ROT13 transformation."""
        result = []
        for char in text:
            if 'a' <= char <= 'z':
                result.append(chr((ord(char) - ord('a') + 13) % 26 + ord('a')))
            elif 'A' <= char <= 'Z':
                result.append(chr((ord(char) - ord('A') + 13) % 26 + ord('A')))
            else:
                result.append(char)
        return ''.join(result)
    
    @staticmethod
    def remove_duplicates(text: str, char: str = ' ') -> str:
        """Remove duplicate characters/words."""
        return re.sub(f'{re.escape(char)}+', char, text)
    
    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return StringHelpers.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    @staticmethod
    def similarity(s1: str, s2: str) -> float:
        """Calculate string similarity ratio (0.0 to 1.0)."""
        if not s1 or not s2:
            return 0.0
        distance = StringHelpers.levenshtein_distance(s1, s2)
        max_len = max(len(s1), len(s2))
        return 1.0 - (distance / max_len)
    
    @staticmethod
    def highlight_matches(text: str, pattern: str, 
                          highlight_start: str = '**', 
                          highlight_end: str = '**') -> str:
        """Highlight pattern matches in text."""
        return re.sub(f'({re.escape(pattern)})', 
                     f'{highlight_start}\\1{highlight_end}', 
                     text, flags=re.IGNORECASE)
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract URLs from text."""
        url_pattern = re.compile(
            r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
        )
        return url_pattern.findall(text)
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """Extract email addresses from text."""
        email_pattern = re.compile(
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        )
        return email_pattern.findall(text)
    
    @staticmethod
    def extract_phone_numbers(text: str) -> List[str]:
        """Extract phone numbers from text."""
        phone_pattern = re.compile(
            r'(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})'
        )
        return phone_pattern.findall(text)
    
    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """Extract hashtags from text."""
        hashtag_pattern = re.compile(r'#(\w+)')
        return hashtag_pattern.findall(text)
    
    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """Extract mentions from text."""
        mention_pattern = re.compile(r'@(\w+)')
        return mention_pattern.findall(text)
    
    @staticmethod
    def mask_sensitive(text: str, visible_chars: int = 4, 
                       mask_char: str = '*') -> str:
        """Mask sensitive data (e.g., passwords, API keys)."""
        if len(text) <= visible_chars:
            return mask_char * len(text)
        return text[:visible_chars] + mask_char * (len(text) - visible_chars)


# ============================================================================
# NETWORK OPERATIONS
# ============================================================================
class NetworkHelpers:
    """
    Network and URL utilities.
    
    Features:
    - URL parsing and manipulation
    - HTTP requests
    - IP address utilities
    - Network calculations
    """
    
    @staticmethod
    def parse_url(url: str) -> Dict[str, str]:
        """
        Parse URL into components.
        
        Args:
            url: URL string
            
        Returns:
            Dictionary with URL components
        """
        parsed = urllib.parse.urlparse(url)
        return {
            'scheme': parsed.scheme,
            'netloc': parsed.netloc,
            'path': parsed.path,
            'params': parsed.params,
            'query': parsed.query,
            'fragment': parsed.fragment,
            'username': parsed.username,
            'password': parsed.password,
            'hostname': parsed.hostname,
            'port': parsed.port,
        }
    
    @staticmethod
    def build_url(base: str, path: str = '', params: Dict[str, str] = None,
                  fragment: str = '') -> str:
        """Build URL from components."""
        url = urllib.parse.urljoin(base, path)
        if params:
            url += '?' + urllib.parse.urlencode(params)
        if fragment:
            url += '#' + fragment
        return url
    
    @staticmethod
    def encode_url(url: str) -> str:
        """URL encode string."""
        return urllib.parse.quote(url, safe='')
    
    @staticmethod
    def decode_url(url: str) -> str:
        """URL decode string."""
        return urllib.parse.unquote(url)
    
    @staticmethod
    def get_domain(url: str) -> str:
        """Extract domain from URL."""
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc
    
    @staticmethod
    def get_file_extension_from_url(url: str) -> str:
        """Get file extension from URL."""
        parsed = urllib.parse.urlparse(url)
        path = parsed.path
        if '.' in path:
            return path.rsplit('.', 1)[-1].lower()
        return ''
    
    @staticmethod
    def get_filename_from_url(url: str) -> str:
        """Get filename from URL."""
        parsed = urllib.parse.urlparse(url)
        path = parsed.path
        if '/' in path:
            return path.rsplit('/', 1)[-1]
        return path
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid."""
        try:
            result = urllib.parse.urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def fetch_url(url: str, timeout: int = 30, 
                  headers: Dict[str, str] = None) -> Optional[str]:
        """
        Fetch URL content.
        
        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            headers: Request headers
            
        Returns:
            Response content or None if failed
        """
        try:
            request = urllib.request.Request(url)
            if headers:
                for key, value in headers.items():
                    request.add_header(key, value)
            
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read().decode('utf-8', errors='ignore')
        except Exception:
            return None
    
    @staticmethod
    def download_file(url: str, destination: Union[str, Path],
                      timeout: int = 300, chunk_size: int = 8192,
                      callback: Callable[[int, int], None] = None) -> bool:
        """
        Download file from URL.
        
        Args:
            url: URL to download
            destination: Local file path
            timeout: Download timeout
            chunk_size: Download chunk size
            callback: Progress callback(downloaded, total)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            Path(destination).parent.mkdir(parents=True, exist_ok=True)
            
            with urllib.request.urlopen(url, timeout=timeout) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                
                with open(destination, 'wb') as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if callback:
                            callback(downloaded, total_size)
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_headers(url: str, timeout: int = 10) -> Dict[str, str]:
        """Get HTTP headers for URL."""
        try:
            request = urllib.request.Request(url, method='HEAD')
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return dict(response.headers)
        except Exception:
            return {}
    
    @staticmethod
    def is_ipv4(ip: str) -> bool:
        """Check if string is valid IPv4 address."""
        try:
            parts = ip.split('.')
            return len(parts) == 4 and all(
                0 <= int(part) <= 255 for part in parts
            )
        except (ValueError, AttributeError):
            return False
    
    @staticmethod
    def is_ipv6(ip: str) -> bool:
        """Check if string is valid IPv6 address."""
        try:
            import ipaddress
            ipaddress.IPv6Address(ip)
            return True
        except (ValueError, ipaddress.AddressValueError):
            return False
    
    @staticmethod
    def is_private_ip(ip: str) -> bool:
        """Check if IP is private/local."""
        try:
            import ipaddress
            return ipaddress.ip_address(ip).is_private
        except ValueError:
            return False
    
    @staticmethod
    def ipv4_to_int(ip: str) -> int:
        """Convert IPv4 to integer."""
        parts = [int(x) for x in ip.split('.')]
        return (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]
    
    @staticmethod
    def int_to_ipv4(num: int) -> str:
        """Convert integer to IPv4."""
        return f"{(num >> 24) & 0xFF}.{(num >> 16) & 0xFF}.{(num >> 8) & 0xFF}.{num & 0xFF}"
    
    @staticmethod
    def cidr_to_range(cidr: str) -> Tuple[str, str]:
        """Convert CIDR to IP range."""
        import ipaddress
        network = ipaddress.ip_network(cidr, strict=False)
        return str(network.network_address), str(network.broadcast_address)
    
    @staticmethod
    def expand_port_range(ports: str) -> List[int]:
        """
        Expand port range string to list.
        
        Args:
            ports: Port range (e.g., "80,443,8000-9000")
            
        Returns:
            List of port numbers
        """
        result = []
        for part in ports.split(','):
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                result.extend(range(int(start), int(end) + 1))
            else:
                result.append(int(part))
        return sorted(set(result))


# ============================================================================
# SYSTEM OPERATIONS
# ============================================================================
class SystemHelpers:
    """
    System and platform utilities.
    
    Features:
    - Platform detection
    - Process management
    - Environment variables
    - Resource monitoring
    """
    
    @staticmethod
    def get_platform() -> Dict[str, str]:
        """Get platform information."""
        return {
            'system': platform.system(),
            'node': platform.node(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'python_implementation': platform.python_implementation(),
        }
    
    @staticmethod
    def is_windows() -> bool:
        """Check if running on Windows."""
        return platform.system() == 'Windows'
    
    @staticmethod
    def is_linux() -> bool:
        """Check if running on Linux."""
        return platform.system() == 'Linux'
    
    @staticmethod
    def is_macos() -> bool:
        """Check if running on macOS."""
        return platform.system() == 'Darwin'
    
    @staticmethod
    def is_root() -> bool:
        """Check if running as root/admin."""
        try:
            return os.geteuid() == 0
        except AttributeError:
            # Windows
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
    
    @staticmethod
    def get_env(key: str, default: str = '') -> str:
        """Get environment variable."""
        return os.environ.get(key, default)
    
    @staticmethod
    def set_env(key: str, value: str) -> None:
        """Set environment variable."""
        os.environ[key] = value
    
    @staticmethod
    def get_home() -> Path:
        """Get home directory path."""
        return Path.home()
    
    @staticmethod
    def get_cwd() -> Path:
        """Get current working directory."""
        return Path.cwd()
    
    @staticmethod
    def get_temp_dir() -> Path:
        """Get temp directory path."""
        return Path(tempfile.gettempdir())
    
    @staticmethod
    def get_cpu_count() -> int:
        """Get CPU core count."""
        return multiprocessing.cpu_count()
    
    @staticmethod
    def get_memory_info() -> Dict[str, int]:
        """Get memory information."""
        try:
            import psutil
            mem = psutil.virtual_memory()
            return {
                'total': mem.total,
                'available': mem.available,
                'used': mem.used,
                'free': mem.free,
                'percent': mem.percent,
            }
        except ImportError:
            return {'total': 0, 'available': 0, 'used': 0, 'free': 0, 'percent': 0}
    
    @staticmethod
    def get_disk_usage(path: str = '/') -> Dict[str, int]:
        """Get disk usage information."""
        try:
            usage = shutil.disk_usage(path)
            return {
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
            }
        except OSError:
            return {'total': 0, 'used': 0, 'free': 0}
    
    @staticmethod
    def run_command(command: Union[str, List[str]], 
                    timeout: Optional[int] = None,
                    cwd: Optional[str] = None,
                    env: Optional[Dict[str, str]] = None,
                    capture_output: bool = True) -> Dict[str, Any]:
        """
        Run shell command.
        
        Args:
            command: Command to run
            timeout: Command timeout
            cwd: Working directory
            env: Environment variables
            capture_output: Whether to capture output
            
        Returns:
            Dictionary with command results
        """
        try:
            result = subprocess.run(
                command,
                shell=isinstance(command, str),
                timeout=timeout,
                cwd=cwd,
                env=env,
                capture_output=capture_output,
                text=True,
            )
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout if capture_output else '',
                'stderr': result.stderr if capture_output else '',
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': 'Command timed out',
            }
        except Exception as e:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
            }
    
    @staticmethod
    def kill_process(pid: int) -> bool:
        """Kill process by PID."""
        try:
            os.kill(pid, 9)
            return True
        except (OSError, ProcessLookupError):
            return False
    
    @staticmethod
    def is_process_running(pid: int) -> bool:
        """Check if process is running."""
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False
    
    @staticmethod
    def get_pid() -> int:
        """Get current process ID."""
        return os.getpid()
    
    @staticmethod
    def clear_screen() -> None:
        """Clear terminal screen."""
        os.system('cls' if SystemHelpers.is_windows() else 'clear')
    
    @staticmethod
    def beep() -> None:
        """Play system beep."""
        print('\a', end='', flush=True)
    
    @staticmethod
    def sleep(seconds: float) -> None:
        """Sleep for specified seconds."""
        time.sleep(seconds)
    
    @staticmethod
    def get_uptime() -> float:
        """Get system uptime in seconds."""
        try:
            import psutil
            return time.time() - psutil.boot_time()
        except ImportError:
            return 0.0


# ============================================================================
# DATA STRUCTURE OPERATIONS
# ============================================================================
class DataHelpers:
    """
    Data structure manipulation utilities.
    
    Features:
    - Dictionary operations
    - List operations
    - Set operations
    - Data transformations
    """
    
    @staticmethod
    def deep_get(dictionary: Dict, keys: str, default: Any = None,
                 separator: str = '.') -> Any:
        """
        Get nested dictionary value.
        
        Args:
            dictionary: Source dictionary
            keys: Dot-separated key path
            default: Default value if not found
            separator: Key separator
            
        Returns:
            Value at key path or default
        """
        keys_list = keys.split(separator)
        value = dictionary
        try:
            for key in keys_list:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    @staticmethod
    def deep_set(dictionary: Dict, keys: str, value: Any,
                 separator: str = '.') -> Dict:
        """Set nested dictionary value."""
        keys_list = keys.split(separator)
        d = dictionary
        for key in keys_list[:-1]:
            if key not in d:
                d[key] = {}
            d = d[key]
        d[keys_list[-1]] = value
        return dictionary
    
    @staticmethod
    def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = dict1.copy()
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = DataHelpers.deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    @staticmethod
    def flatten_dict(dictionary: Dict, separator: str = '.', 
                     prefix: str = '') -> Dict:
        """Flatten nested dictionary."""
        items = []
        for key, value in dictionary.items():
            new_key = f"{prefix}{separator}{key}" if prefix else key
            if isinstance(value, dict):
                items.extend(DataHelpers.flatten_dict(value, separator, new_key).items())
            else:
                items.append((new_key, value))
        return dict(items)
    
    @staticmethod
    def unflatten_dict(dictionary: Dict, separator: str = '.') -> Dict:
        """Unflatten dictionary with dot-separated keys."""
        result = {}
        for key, value in dictionary.items():
            DataHelpers.deep_set(result, key, value, separator)
        return result
    
    @staticmethod
    def invert_dict(dictionary: Dict) -> Dict:
        """Invert dictionary (swap keys and values)."""
        return {v: k for k, v in dictionary.items()}
    
    @staticmethod
    def chunk_list(lst: List[T], chunk_size: int) -> Generator[List[T], None, None]:
        """Split list into chunks."""
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i + chunk_size]
    
    @staticmethod
    def flatten_list(nested_list: List[List[T]]) -> List[T]:
        """Flatten nested list."""
        return [item for sublist in nested_list for item in sublist]
    
    @staticmethod
    def unique_list(lst: List[T]) -> List[T]:
        """Get unique items preserving order."""
        seen = set()
        result = []
        for item in lst:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result
    
    @staticmethod
    def group_by(lst: List[T], key_func: Callable[[T], K]) -> Dict[K, List[T]]:
        """Group list items by key function."""
        result = defaultdict(list)
        for item in lst:
            result[key_func(item)].append(item)
        return dict(result)
    
    @staticmethod
    def partition(lst: List[T], predicate: Callable[[T], bool]) -> Tuple[List[T], List[T]]:
        """Partition list by predicate."""
        true_list, false_list = [], []
        for item in lst:
            (true_list if predicate(item) else false_list).append(item)
        return true_list, false_list
    
    @staticmethod
    def find_duplicates(lst: List[T]) -> List[T]:
        """Find duplicate items in list."""
        seen = set()
        duplicates = set()
        for item in lst:
            if item in seen:
                duplicates.add(item)
            else:
                seen.add(item)
        return list(duplicates)
    
    @staticmethod
    def rotate_list(lst: List[T], n: int) -> List[T]:
        """Rotate list by n positions."""
        if not lst:
            return lst
        n = n % len(lst)
        return lst[n:] + lst[:n]
    
    @staticmethod
    def take(lst: List[T], n: int) -> List[T]:
        """Take first n elements from list."""
        return lst[:n]
    
    @staticmethod
    def drop(lst: List[T], n: int) -> List[T]:
        """Drop first n elements from list."""
        return lst[n:]
    
    @staticmethod
    def first(lst: List[T], default: Any = None) -> Any:
        """Get first element or default."""
        return lst[0] if lst else default
    
    @staticmethod
    def last(lst: List[T], default: Any = None) -> Any:
        """Get last element or default."""
        return lst[-1] if lst else default


# ============================================================================
# DATE/TIME OPERATIONS
# ============================================================================
class DateTimeHelpers:
    """
    Date and time utilities.
    
    Features:
    - Date formatting and parsing
    - Time calculations
    - Timezone handling
    - Duration formatting
    """
    
    @staticmethod
    def now() -> datetime:
        """Get current datetime."""
        return datetime.now()
    
    @staticmethod
    def now_iso() -> str:
        """Get current datetime in ISO format."""
        return datetime.now().isoformat()
    
    @staticmethod
    def now_formatted(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Get current datetime formatted."""
        return datetime.now().strftime(fmt)
    
    @staticmethod
    def today() -> str:
        """Get today's date string."""
        return datetime.now().strftime("%Y-%m-%d")
    
    @staticmethod
    def timestamp() -> int:
        """Get current Unix timestamp."""
        return int(time.time())
    
    @staticmethod
    def timestamp_ms() -> int:
        """Get current Unix timestamp in milliseconds."""
        return int(time.time() * 1000)
    
    @staticmethod
    def from_timestamp(ts: int) -> datetime:
        """Convert timestamp to datetime."""
        return datetime.fromtimestamp(ts)
    
    @staticmethod
    def parse_date(date_string: str, fmt: str = "%Y-%m-%d") -> Optional[datetime]:
        """Parse date string."""
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            return None
    
    @staticmethod
    def format_date(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format datetime."""
        return dt.strftime(fmt)
    
    @staticmethod
    def add_days(dt: datetime, days: int) -> datetime:
        """Add days to datetime."""
        return dt + timedelta(days=days)
    
    @staticmethod
    def add_hours(dt: datetime, hours: int) -> datetime:
        """Add hours to datetime."""
        return dt + timedelta(hours=hours)
    
    @staticmethod
    def add_minutes(dt: datetime, minutes: int) -> datetime:
        """Add minutes to datetime."""
        return dt + timedelta(minutes=minutes)
    
    @staticmethod
    def days_between(dt1: datetime, dt2: datetime) -> int:
        """Calculate days between two dates."""
        return abs((dt2 - dt1).days)
    
    @staticmethod
    def seconds_between(dt1: datetime, dt2: datetime) -> float:
        """Calculate seconds between two datetimes."""
        return abs((dt2 - dt1).total_seconds())
    
    @staticmethod
    def format_duration(seconds: float, show_ms: bool = False) -> str:
        """
        Format duration in human-readable format.
        
        Args:
            seconds: Duration in seconds
            show_ms: Whether to show milliseconds
            
        Returns:
            Formatted duration string
        """
        if seconds < 0:
            return "0s"
        
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        
        parts = []
        if hours >= 1:
            parts.append(f"{int(hours)}h")
        if minutes >= 1:
            parts.append(f"{int(minutes)}m")
        if secs >= 1 or not parts:
            if show_ms:
                parts.append(f"{secs:.2f}s")
            else:
                parts.append(f"{int(secs)}s")
        
        return ' '.join(parts)
    
    @staticmethod
    def format_relative(dt: datetime) -> str:
        """
        Format datetime as relative time (e.g., "2 hours ago").
        
        Args:
            dt: Datetime to format
            
        Returns:
            Relative time string
        """
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "just now"
    
    @staticmethod
    def is_weekend(dt: datetime) -> bool:
        """Check if date is weekend."""
        return dt.weekday() >= 5
    
    @staticmethod
    def is_today(dt: datetime) -> bool:
        """Check if date is today."""
        return dt.date() == datetime.now().date()


# ============================================================================
# MATH OPERATIONS
# ============================================================================
class MathHelpers:
    """
    Mathematical utilities.
    
    Features:
    - Advanced math operations
    - Statistical functions
    - Number formatting
    - Unit conversions
    """
    
    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        """Clamp value between min and max."""
        return max(min_val, min(max_val, value))
    
    @staticmethod
    def lerp(start: float, end: float, t: float) -> float:
        """Linear interpolation between start and end."""
        return start + (end - start) * t
    
    @staticmethod
    def map_range(value: float, in_min: float, in_max: float,
                  out_min: float, out_max: float) -> float:
        """Map value from one range to another."""
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    
    @staticmethod
    def percentage(part: float, total: float) -> float:
        """Calculate percentage."""
        if total == 0:
            return 0.0
        return (part / total) * 100
    
    @staticmethod
    def average(values: List[float]) -> float:
        """Calculate average of values."""
        if not values:
            return 0.0
        return sum(values) / len(values)
    
    @staticmethod
    def median(values: List[float]) -> float:
        """Calculate median of values."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        n = len(sorted_values)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_values[mid - 1] + sorted_values[mid]) / 2
        return sorted_values[mid]
    
    @staticmethod
    def mode(values: List[Any]) -> Any:
        """Find most common value."""
        if not values:
            return None
        counter = Counter(values)
        return counter.most_common(1)[0][0]
    
    @staticmethod
    def std_dev(values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        mean = MathHelpers.average(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)
    
    @staticmethod
    def round_to(value: float, decimals: int = 2) -> float:
        """Round to specified decimal places."""
        return round(value, decimals)
    
    @staticmethod
    def floor(value: float) -> int:
        """Round down to nearest integer."""
        return math.floor(value)
    
    @staticmethod
    def ceil(value: float) -> int:
        """Round up to nearest integer."""
        return math.ceil(value)
    
    @staticmethod
    def is_even(n: int) -> bool:
        """Check if number is even."""
        return n % 2 == 0
    
    @staticmethod
    def is_odd(n: int) -> bool:
        """Check if number is odd."""
        return n % 2 != 0
    
    @staticmethod
    def is_prime(n: int) -> bool:
        """Check if number is prime."""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    @staticmethod
    def gcd(a: int, b: int) -> int:
        """Calculate greatest common divisor."""
        while b:
            a, b = b, a % b
        return a
    
    @staticmethod
    def lcm(a: int, b: int) -> int:
        """Calculate least common multiple."""
        return abs(a * b) // MathHelpers.gcd(a, b)
    
    @staticmethod
    def factorial(n: int) -> int:
        """Calculate factorial."""
        if n < 0:
            raise ValueError("Factorial not defined for negative numbers")
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result
    
    @staticmethod
    def fibonacci(n: int) -> List[int]:
        """Generate Fibonacci sequence."""
        if n <= 0:
            return []
        if n == 1:
            return [0]
        fib = [0, 1]
        while len(fib) < n:
            fib.append(fib[-1] + fib[-2])
        return fib
    
    @staticmethod
    def bytes_to_human(size_bytes: int) -> str:
        """Convert bytes to human-readable format."""
        return format_size(size_bytes)
    
    @staticmethod
    def human_to_bytes(size_str: str) -> int:
        """Convert human-readable size to bytes."""
        size_str = size_str.strip().upper()
        units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3,
                 'TB': 1024**4, 'PB': 1024**5}
        
        for unit, multiplier in units.items():
            if size_str.endswith(unit):
                number = float(size_str[:-len(unit)])
                return int(number * multiplier)
        
        return int(size_str)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def format_size(size_bytes: int) -> str:
    """
    Format bytes to human-readable size.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 GB")
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
    i = int(math.floor(math.log(size_bytes, 1024)))
    i = min(i, len(units) - 1)
    size = size_bytes / (1024 ** i)
    return f"{size:.2f} {units[i]}"


def format_number(number: Union[int, float], 
                  decimal_places: int = 2) -> str:
    """Format number with thousands separator."""
    if isinstance(number, int):
        return f"{number:,}"
    return f"{number:,.{decimal_places}f}"


def format_speed(bytes_per_second: float) -> str:
    """Format download speed."""
    return f"{format_size(int(bytes_per_second))}/s"


def format_time(seconds: float) -> str:
    """Format time in seconds to readable format."""
    return DateTimeHelpers.format_duration(seconds)


def retry(func: Callable[..., T], max_attempts: int = 3,
          delay: float = 1.0, exceptions: Tuple = (Exception,),
          on_retry: Optional[Callable[[int, Exception], None]] = None) -> T:
    """
    Retry function with exponential backoff.
    
    Args:
        func: Function to retry
        max_attempts: Maximum retry attempts
        delay: Initial delay between retries
        exceptions: Exceptions to catch
        on_retry: Callback on each retry
        
    Returns:
        Function result
    """
    last_exception = None
    for attempt in range(max_attempts):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            if on_retry:
                on_retry(attempt + 1, e)
            if attempt < max_attempts - 1:
                time.sleep(delay * (2 ** attempt))
    raise last_exception


def timeout(func: Callable[..., T], seconds: float) -> T:
    """Execute function with timeout."""
    result = [None]
    exception = [None]
    
    def wrapper():
        try:
            result[0] = func()
        except Exception as e:
            exception[0] = e
    
    thread = threading.Thread(target=wrapper)
    thread.daemon = True
    thread.start()
    thread.join(seconds)
    
    if thread.is_alive():
        raise TimeoutError(f"Function timed out after {seconds} seconds")
    
    if exception[0]:
        raise exception[0]
    
    return result[0]


@contextmanager
def timer(name: str = "Operation") -> Generator[None, None, None]:
    """Context manager to time operations."""
    start = time.time()
    yield
    elapsed = time.time() - start
    print(f"{name} took {elapsed:.4f} seconds")


@contextmanager
def suppress_output() -> Generator[None, None, None]:
    """Context manager to suppress stdout and stderr."""
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr


def debounce(wait: float) -> Callable:
    """Decorator to debounce function calls."""
    def decorator(func: Callable) -> Callable:
        last_called = [0.0]
        scheduled = [None]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            def call():
                func(*args, **kwargs)
                scheduled[0] = None
            
            if scheduled[0]:
                scheduled[0].cancel()
            
            elapsed = time.time() - last_called[0]
            if elapsed >= wait:
                last_called[0] = time.time()
                func(*args, **kwargs)
            else:
                scheduled[0] = threading.Timer(wait - elapsed, call)
                scheduled[0].start()
        
        return wrapper
    return decorator


def throttle(wait: float) -> Callable:
    """Decorator to throttle function calls."""
    def decorator(func: Callable) -> Callable:
        last_called = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed >= wait:
                last_called[0] = time.time()
                return func(*args, **kwargs)
            return None
        
        return wrapper
    return decorator


# ============================================================================
# MODULE-LEVEL INSTANCES
# ============================================================================
file_helpers = FileHelpers()
string_helpers = StringHelpers()
network_helpers = NetworkHelpers()
system_helpers = SystemHelpers()
data_helpers = DataHelpers()
datetime_helpers = DateTimeHelpers()
math_helpers = MathHelpers()


# ============================================================================
# EXPORTS
# ============================================================================
__all__ = [
    # Version
    '__version__',
    '__author__',
    '__status__',
    
    # Classes
    'FileHelpers',
    'StringHelpers',
    'NetworkHelpers',
    'SystemHelpers',
    'DataHelpers',
    'DateTimeHelpers',
    'MathHelpers',
    
    # Instances
    'file_helpers',
    'string_helpers',
    'network_helpers',
    'system_helpers',
    'data_helpers',
    'datetime_helpers',
    'math_helpers',
    
    # Utility functions
    'format_size',
    'format_number',
    'format_speed',
    'format_time',
    'retry',
    'timeout',
    'timer',
    'suppress_output',
    'debounce',
    'throttle',
]


# ============================================================================
# MAIN DEMO
# ============================================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("    ULTIMATE NEXUS HELPER FUNCTIONS v3.0.1 - DEMO")
    print("="*60 + "\n")
    
    # String helpers demo
    print("--- String Helpers ---")
    print(f"Slugify: {string_helpers.slugify('Hello World! This is a Test.')}")
    print(f"Random string: {string_helpers.generate_random_string(16)}")
    print(f"Password: {string_helpers.generate_password()}")
    print(f"UUID: {string_helpers.generate_uuid()}")
    
    # Math helpers demo
    print("\n--- Math Helpers ---")
    print(f"Format size: {math_helpers.bytes_to_human(1536000000)}")
    print(f"Average: {math_helpers.average([1, 2, 3, 4, 5])}")
    print(f"Is prime (17): {math_helpers.is_prime(17)}")
    print(f"Fibonacci (10): {math_helpers.fibonacci(10)}")
    
    # DateTime helpers demo
    print("\n--- DateTime Helpers ---")
    print(f"Now: {datetime_helpers.now_formatted()}")
    print(f"Timestamp: {datetime_helpers.timestamp()}")
    print(f"Duration: {datetime_helpers.format_duration(3725)}")
    
    # System helpers demo
    print("\n--- System Helpers ---")
    print(f"Platform: {system_helpers.get_platform()['system']}")
    print(f"CPU count: {system_helpers.get_cpu_count()}")
    print(f"Home: {system_helpers.get_home()}")
    
    print("\nDemo complete!")

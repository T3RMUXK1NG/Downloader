#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RS YouTube Downloader Toolkit - Network Handler                             ║
║  Author: RS (T3rmuxk1ng)                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import socket
import random
import urllib.request
import urllib.error
import http.client
from typing import Dict, Optional, Tuple, Any
from urllib.parse import urlparse, parse_qs, urlencode


class NetworkHandler:
    """
    Network Handler for RS Toolkit
    - HTTP/HTTPS requests
    - Proxy support (HTTP, SOCKS4, SOCKS5)
    - Rate limiting
    - Retry logic
    - User-Agent rotation
    - Termux compatible (uses stdlib only)
    """
    
    # User agents for rotation
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36',
    ]
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # Network settings
        self.timeout = self.config.get('timeout', 30)
        self.retry_count = self.config.get('retry_count', 3)
        self.retry_delay = self.config.get('retry_delay', 2)
        self.rate_limit = self.config.get('rate_limit', 0)  # requests per second, 0 = unlimited
        
        # Proxy settings
        self.proxy_enabled = self.config.get('proxy_enabled', False)
        self.proxy_type = self.config.get('proxy_type', 'http')
        self.proxy_host = self.config.get('proxy_host', '127.0.0.1')
        self.proxy_port = self.config.get('proxy_port', 8080)
        
        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = 1.0 / self.rate_limit if self.rate_limit > 0 else 0
        
        # Cookie jar for session management
        self.cookies = {}
    
    def _get_random_user_agent(self) -> str:
        """Get random user agent"""
        return random.choice(self.USER_AGENTS)
    
    def _apply_rate_limit(self):
        """Apply rate limiting"""
        if self._min_request_interval > 0:
            elapsed = time.time() - self._last_request_time
            if elapsed < self._min_request_interval:
                time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()
    
    def _setup_proxy(self, handler: urllib.request.OpenerDirector) -> urllib.request.OpenerDirector:
        """Setup proxy for request"""
        if not self.proxy_enabled:
            return handler
        
        proxy_url = f"{self.proxy_type}://{self.proxy_host}:{self.proxy_port}"
        
        if self.proxy_type in ['http', 'https']:
            proxy_handler = urllib.request.ProxyHandler({
                'http': proxy_url,
                'https': proxy_url
            })
        elif self.proxy_type == 'socks5':
            # For SOCKS5, we need to handle differently
            # Basic SOCKS5 support through HTTP proxy tunnel
            proxy_handler = urllib.request.ProxyHandler({
                'http': proxy_url,
                'https': proxy_url
            })
        else:
            return handler
        
        return urllib.request.build_opener(proxy_handler)
    
    def request(self, url: str, method: str = 'GET', data: bytes = None,
                headers: Dict = None, return_headers: bool = False) -> Tuple[int, Any]:
        """
        Make HTTP request with retry logic
        
        Returns:
            Tuple of (status_code, content_or_headers)
        """
        self._apply_rate_limit()
        
        # Prepare headers
        request_headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'identity',  # Disable compression for simplicity
            'Connection': 'keep-alive',
        }
        
        if headers:
            request_headers.update(headers)
        
        # Add cookies
        if self.cookies:
            cookie_str = '; '.join(f"{k}={v}" for k, v in self.cookies.items())
            request_headers['Cookie'] = cookie_str
        
        # Create request
        req = urllib.request.Request(url, data=data, headers=request_headers, method=method)
        
        # Setup opener with proxy if enabled
        opener = self._setup_proxy(urllib.request.build_opener())
        
        # Retry logic
        last_error = None
        for attempt in range(self.retry_count):
            try:
                response = opener.open(req, timeout=self.timeout)
                
                # Save cookies from response
                if 'Set-Cookie' in response.headers:
                    for cookie in response.headers.get_all('Set-Cookie'):
                        parts = cookie.split(';')[0].split('=', 1)
                        if len(parts) == 2:
                            self.cookies[parts[0]] = parts[1]
                
                if return_headers:
                    return response.status, dict(response.headers)
                
                content = response.read()
                return response.status, content
                
            except urllib.error.HTTPError as e:
                last_error = e
                if e.code == 404:
                    return e.code, None  # Don't retry 404
                if e.code == 403:
                    # Try with different user agent
                    request_headers['User-Agent'] = self._get_random_user_agent()
                    
            except urllib.error.URLError as e:
                last_error = e
                
            except socket.timeout:
                last_error = "Connection timeout"
                
            except Exception as e:
                last_error = e
            
            # Wait before retry
            if attempt < self.retry_count - 1:
                time.sleep(self.retry_delay * (attempt + 1))
        
        # All retries failed
        return 0, str(last_error)
    
    def get(self, url: str, headers: Dict = None) -> Tuple[int, bytes]:
        """GET request"""
        return self.request(url, 'GET', headers=headers)
    
    def post(self, url: str, data: Dict = None, headers: Dict = None) -> Tuple[int, bytes]:
        """POST request"""
        post_data = urlencode(data).encode() if data else None
        return self.request(url, 'POST', data=post_data, headers=headers)
    
    def head(self, url: str, headers: Dict = None) -> Tuple[int, Dict]:
        """HEAD request - returns headers only"""
        return self.request(url, 'HEAD', headers=headers, return_headers=True)
    
    def download_file(self, url: str, output_path: str, chunk_size: int = 8192,
                      progress_callback=None) -> bool:
        """
        Download file with progress callback
        
        Args:
            url: URL to download
            output_path: Local file path
            chunk_size: Download chunk size
            progress_callback: Function(downloaded, total, speed)
        
        Returns:
            True if successful, False otherwise
        """
        self._apply_rate_limit()
        
        # Get file info first
        status, headers = self.head(url)
        if status != 200:
            return False
        
        total_size = int(headers.get('Content-Length', 0))
        
        # Setup request
        request_headers = {
            'User-Agent': self._get_random_user_agent(),
        }
        req = urllib.request.Request(url, headers=request_headers)
        opener = self._setup_proxy(urllib.request.build_opener())
        
        try:
            response = opener.open(req, timeout=self.timeout)
            
            # Create output directory
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            
            # Download with progress
            downloaded = 0
            start_time = time.time()
            
            with open(output_path, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Calculate speed
                    elapsed = time.time() - start_time
                    speed = downloaded / elapsed if elapsed > 0 else 0
                    
                    # Callback
                    if progress_callback:
                        progress_callback(downloaded, total_size, speed)
            
            return True
            
        except Exception as e:
            # Clean up partial file
            if os.path.exists(output_path):
                os.remove(output_path)
            return False
    
    def get_json(self, url: str, headers: Dict = None) -> Tuple[int, Dict]:
        """GET request expecting JSON response"""
        import json
        status, content = self.get(url, headers)
        
        if status == 200 and content:
            try:
                return status, json.loads(content.decode('utf-8'))
            except json.JSONDecodeError:
                return status, None
        
        return status, None
    
    def check_connection(self, test_url: str = "https://www.youtube.com") -> bool:
        """Check if internet connection is working"""
        try:
            status, _ = self.head(test_url)
            return status == 200
        except:
            return False
    
    def get_file_size(self, url: str) -> int:
        """Get file size without downloading"""
        status, headers = self.head(url)
        if status == 200:
            return int(headers.get('Content-Length', 0))
        return 0
    
    def set_cookies(self, cookies: Dict):
        """Set cookies for session"""
        self.cookies.update(cookies)
    
    def clear_cookies(self):
        """Clear session cookies"""
        self.cookies = {}


# Global network instance
network = NetworkHandler()

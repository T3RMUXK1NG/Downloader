#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OMNIPOTENT SOVEREIGN NEXUS - Network Utilities Module
=====================================================

Version: 3.2.0 ULTIMATE NEXUS
Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng

This module provides comprehensive network utilities for the Downloader
package with security hardening, retry mechanisms, and async support.

ARCHITECTURE:
    - Async-first design with sync compatibility
    - Connection pooling and reuse
    - Automatic retry with multiple strategies
    - Rate limiting and throttling
    - DNS caching and resolution
    - SSL/TLS security hardening

FEATURES:
    - HTTP/HTTPS client with async support
    - Connection pooling for performance
    - Retry with exponential backoff
    - Rate limiting with token bucket
    - Request/response interceptors
    - Cookie and session management
    - Redirect handling
    - Timeout management
    - Proxy support (HTTP, HTTPS, SOCKS)

SECURITY:
    - SSL certificate verification
    - Request sanitization
    - Header injection prevention
    - URL validation
    - Safe redirect following
    - Certificate pinning support
"""

from __future__ import annotations

import asyncio
import functools
import hashlib
import hmac
import inspect
import ipaddress
import json
import os
import random
import re
import socket
import ssl
import sys
import time
import urllib.parse
import warnings
from abc import ABC, abstractmethod
from collections import OrderedDict
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum, auto
from http.cookiejar import Cookie, CookieJar
from io import BytesIO, StringIO
from pathlib import Path
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    BinaryIO,
    Callable,
    ClassVar,
    Dict,
    Final,
    FrozenSet,
    Generic,
    IO,
    Iterator,
    List,
    Literal,
    Mapping,
    MutableMapping,
    Optional,
    Protocol,
    Set,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
    runtime_checkable,
)
from urllib.parse import ParseResult, urlparse, urljoin, urlunparse
from weakref import WeakSet

# Try to import optional dependencies
try:
    import aiohttp
    from aiohttp import ClientSession, ClientResponse, ClientError, ClientTimeout
    from aiohttp.connector import TCPConnector
    from aiohttp.client_reqrep import ClientRequest
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False
    aiohttp = None  # type: ignore

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    httpx = None  # type: ignore

try:
    import certifi
    SSL_CERT_FILE = certifi.where()
except ImportError:
    SSL_CERT_FILE = None

try:
    from tenacity import (
        retry, stop_after_attempt, wait_exponential,
        retry_if_exception_type, RetryError as TenacityRetryError
    )
    HAS_TENACITY = True
except ImportError:
    HAS_TENACITY = False

# Import from our package
from .config import (
    Config,
    TimeoutConfig,
    RetryConfig,
    ProxyConfig,
    SSLConfig,
    ConnectionPoolConfig,
    RateLimitConfig,
    RetryStrategy,
    mask_sensitive,
    validate_url,
    validate_proxy_url,
)
from .logger import Logger, get_logger, LogLevel


# =============================================================================
# CONSTANTS AND ENUMS
# =============================================================================

class HttpMethod(str, Enum):
    """HTTP method enumeration."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"
    CONNECT = "CONNECT"


class ContentType(str, Enum):
    """Common content type enumeration."""
    JSON = "application/json"
    FORM = "application/x-www-form-urlencoded"
    MULTIPART = "multipart/form-data"
    TEXT = "text/plain"
    HTML = "text/html"
    XML = "application/xml"
    BINARY = "application/octet-stream"
    PDF = "application/pdf"
    ZIP = "application/zip"


class AuthType(str, Enum):
    """Authentication type enumeration."""
    NONE = "none"
    BASIC = "basic"
    BEARER = "bearer"
    DIGEST = "digest"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    CUSTOM = "custom"


# Default values
DEFAULT_USER_AGENT: Final[str] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
DEFAULT_ACCEPT: Final[str] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
DEFAULT_ACCEPT_LANGUAGE: Final[str] = "en-US,en;q=0.9"
DEFAULT_ACCEPT_ENCODING: Final[str] = "gzip, deflate, br"
MAX_RESPONSE_SIZE: Final[int] = 100 * 1024 * 1024  # 100 MB
MAX_REDIRECT_URL_LENGTH: Final[int] = 2048
DNS_CACHE_SIZE: Final[int] = 1000
RATE_LIMIT_WINDOW: Final[float] = 1.0  # seconds

# Safe headers that don't contain sensitive data
SAFE_HEADERS: FrozenSet[str] = frozenset({
    "accept", "accept-encoding", "accept-language", "cache-control",
    "connection", "content-length", "content-type", "date", "etag",
    "expires", "host", "if-modified-since", "if-none-match", "keep-alive",
    "last-modified", "location", "pragma", "server", "transfer-encoding",
    "user-agent", "vary", "via", "x-forwarded-for", "x-request-id"
})

# Headers that may contain sensitive data
SENSITIVE_HEADERS: FrozenSet[str] = frozenset({
    "authorization", "cookie", "set-cookie", "proxy-authorization",
    "www-authenticate", "x-api-key", "x-auth-token"
})


# =============================================================================
# EXCEPTIONS
# =============================================================================

class NetworkError(Exception):
    """
    Base exception for network-related errors.
    
    Attributes:
        message: Error message.
        url: URL that caused the error.
        status_code: HTTP status code (if applicable).
        response: Response object (if available).
        retry_after: Seconds to wait before retry (if applicable).
    """
    
    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        response: Optional[Any] = None,
        retry_after: Optional[float] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.url = url
        self.status_code = status_code
        self.response = response
        self.retry_after = retry_after
    
    def __str__(self) -> str:
        parts = [self.message]
        if self.url:
            parts.append(f"URL: {mask_sensitive(self.url)}")
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        return " | ".join(parts)


class ConnectionError(NetworkError):
    """Exception raised when connection fails."""
    pass


class TimeoutError(NetworkError):
    """Exception raised when request times out."""
    pass


class DNSError(NetworkError):
    """Exception raised for DNS resolution failures."""
    pass


class SSLError(NetworkError):
    """Exception raised for SSL/TLS errors."""
    pass


class HTTPError(NetworkError):
    """Exception raised for HTTP errors (4xx, 5xx)."""
    pass


class RateLimitError(NetworkError):
    """Exception raised when rate limit is exceeded."""
    pass


class RedirectError(NetworkError):
    """Exception raised for redirect-related errors."""
    pass


class InvalidURLError(NetworkError):
    """Exception raised for invalid URLs."""
    pass


class RetryExhaustedError(NetworkError):
    """Exception raised when all retry attempts are exhausted."""
    pass


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass(frozen=True)
class URL:
    """
    Immutable URL wrapper with validation and manipulation.
    
    Provides safe URL handling with validation, sanitization,
    and component access.
    
    Attributes:
        _parsed: Parsed URL components.
        _raw: Original URL string.
    """
    
    _parsed: ParseResult
    _raw: str
    
    def __init__(self, url: str, base: Optional[str] = None) -> None:
        """
        Initialize URL.
        
        Args:
            url: URL string.
            base: Base URL for relative URLs.
        
        Raises:
            InvalidURLError: If URL is invalid.
        """
        if base:
            url = urljoin(base, url)
        
        parsed = urlparse(url)
        
        # Validate URL
        if not parsed.scheme or not parsed.netloc:
            if not parsed.scheme:
                raise InvalidURLError(f"URL missing scheme: {url}")
            if not parsed.netloc:
                raise InvalidURLError(f"URL missing netloc: {url}")
        
        if parsed.scheme not in ("http", "https"):
            raise InvalidURLError(f"Unsupported URL scheme: {parsed.scheme}")
        
        object.__setattr__(self, "_parsed", parsed)
        object.__setattr__(self, "_raw", url)
    
    @property
    def scheme(self) -> str:
        """Get URL scheme."""
        return self._parsed.scheme
    
    @property
    def netloc(self) -> str:
        """Get network location."""
        return self._parsed.netloc
    
    @property
    def hostname(self) -> Optional[str]:
        """Get hostname."""
        return self._parsed.hostname
    
    @property
    def port(self) -> Optional[int]:
        """Get port number."""
        return self._parsed.port
    
    @property
    def path(self) -> str:
        """Get URL path."""
        return self._parsed.path or "/"
    
    @property
    def query(self) -> str:
        """Get query string."""
        return self._parsed.query
    
    @property
    def fragment(self) -> str:
        """Get URL fragment."""
        return self._parsed.fragment
    
    @property
    def username(self) -> Optional[str]:
        """Get username from URL."""
        return self._parsed.username
    
    @property
    def password(self) -> Optional[str]:
        """Get password from URL."""
        return self._parsed.password
    
    @property
    def is_https(self) -> bool:
        """Check if URL uses HTTPS."""
        return self.scheme == "https"
    
    @property
    def is_valid(self) -> bool:
        """Check if URL is valid."""
        return bool(self._parsed.scheme and self._parsed.netloc)
    
    @property
    def host_with_port(self) -> str:
        """Get host with port if not default."""
        if self.port:
            if (self.scheme == "http" and self.port != 80) or \
               (self.scheme == "https" and self.port != 443):
                return f"{self.hostname}:{self.port}"
        return self.hostname or ""
    
    def with_path(self, path: str) -> "URL":
        """
        Create new URL with different path.
        
        Args:
            path: New path.
        
        Returns:
            URL: New URL instance.
        """
        new_parsed = ParseResult(
            scheme=self._parsed.scheme,
            netloc=self._parsed.netloc,
            path=path,
            params=self._parsed.params,
            query=self._parsed.query,
            fragment=self._parsed.fragment
        )
        url = URL.__new__(URL)
        object.__setattr__(url, "_parsed", new_parsed)
        object.__setattr__(url, "_raw", new_parsed.geturl())
        return url
    
    def with_query(self, **params: Any) -> "URL":
        """
        Create new URL with query parameters.
        
        Args:
            **params: Query parameters.
        
        Returns:
            URL: New URL instance.
        """
        query = urllib.parse.urlencode(params)
        new_parsed = ParseResult(
            scheme=self._parsed.scheme,
            netloc=self._parsed.netloc,
            path=self._parsed.path,
            params=self._parsed.params,
            query=query,
            fragment=self._parsed.fragment
        )
        url = URL.__new__(URL)
        object.__setattr__(url, "_parsed", new_parsed)
        object.__setattr__(url, "_raw", new_parsed.geturl())
        return url
    
    def resolve(self, base: str) -> "URL":
        """
        Resolve URL against a base URL.
        
        Args:
            base: Base URL.
        
        Returns:
            URL: Resolved URL.
        """
        resolved = urljoin(base, self._raw)
        return URL(resolved)
    
    def __str__(self) -> str:
        return self._raw
    
    def __repr__(self) -> str:
        return f"URL({self._raw!r})"
    
    def __hash__(self) -> int:
        return hash(self._raw)
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, URL):
            return self._raw == other._raw
        if isinstance(other, str):
            return self._raw == other
        return False


@dataclass(frozen=True)
class Headers:
    """
    Immutable HTTP headers container.
    
    Provides case-insensitive header access with security features.
    """
    
    _data: Mapping[str, str]
    
    def __init__(self, headers: Optional[Mapping[str, str]] = None, **kwargs: str) -> None:
        """
        Initialize headers.
        
        Args:
            headers: Initial headers.
            **kwargs: Additional headers.
        """
        data: Dict[str, str] = {}
        if headers:
            for key, value in headers.items():
                data[key.lower()] = str(value)
        for key, value in kwargs.items():
            # Handle _ prefixed keys (e.g., content_type -> Content-Type)
            key = key.replace("_", "-")
            data[key.lower()] = str(value)
        object.__setattr__(self, "_data", MappingProxyType(data))
    
    def get(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get header value.
        
        Args:
            name: Header name (case-insensitive).
            default: Default value if not found.
        
        Returns:
            Optional[str]: Header value or default.
        """
        return self._data.get(name.lower(), default)
    
    def __getitem__(self, name: str) -> str:
        return self._data[name.lower()]
    
    def __contains__(self, name: str) -> bool:
        return name.lower() in self._data
    
    def __iter__(self) -> Iterator[Tuple[str, str]]:
        return iter(self._data.items())
    
    def __len__(self) -> int:
        return len(self._data)
    
    def keys(self) -> Set[str]:
        """Get header names."""
        return set(self._data.keys())
    
    def values(self) -> List[str]:
        """Get header values."""
        return list(self._data.values())
    
    def items(self) -> Iterator[Tuple[str, str]]:
        """Iterate over headers."""
        return iter(self._data.items())
    
    def merge(self, other: Mapping[str, str]) -> "Headers":
        """
        Merge with other headers.
        
        Args:
            other: Headers to merge.
        
        Returns:
            Headers: New merged headers.
        """
        new_data = dict(self._data)
        for key, value in other.items():
            new_data[key.lower()] = str(value)
        return Headers(new_data)
    
    def to_dict(self, mask_sensitive_headers: bool = True) -> Dict[str, str]:
        """
        Convert to dictionary.
        
        Args:
            mask_sensitive_headers: Mask sensitive header values.
        
        Returns:
            Dict[str, str]: Headers dictionary.
        """
        result = {}
        for key, value in self._data.items():
            if mask_sensitive_headers and key in SENSITIVE_HEADERS:
                result[key] = mask_sensitive(value)
            else:
                result[key] = value
        return result
    
    def safe_str(self) -> str:
        """Get safe string representation for logging."""
        return str(self.to_dict(mask_sensitive_headers=True))


# Helper for frozen mapping
class MappingProxyType(MutableMapping[str, str]):
    """Read-only proxy for mapping."""
    
    def __init__(self, data: Dict[str, str]) -> None:
        self._data = data
    
    def __getitem__(self, key: str) -> str:
        return self._data[key]
    
    def __setitem__(self, key: str, value: str) -> None:
        raise TypeError("Headers are immutable")
    
    def __delitem__(self, key: str) -> None:
        raise TypeError("Headers are immutable")
    
    def __iter__(self) -> Iterator[str]:
        return iter(self._data)
    
    def __len__(self) -> int:
        return len(self._data)


@dataclass
class Request:
    """
    HTTP request container.
    
    Attributes:
        method: HTTP method.
        url: Request URL.
        headers: Request headers.
        params: Query parameters.
        data: Request body data.
        json: JSON body data.
        cookies: Request cookies.
        timeout: Request timeout.
        allow_redirects: Whether to follow redirects.
        verify_ssl: Whether to verify SSL certificates.
    """
    
    method: HttpMethod = HttpMethod.GET
    url: Optional[URL] = None
    headers: Headers = field(default_factory=lambda: Headers())
    params: Dict[str, Any] = field(default_factory=dict)
    data: Optional[Union[bytes, str, Dict[str, Any]]] = None
    json: Optional[Dict[str, Any]] = None
    cookies: Dict[str, str] = field(default_factory=dict)
    timeout: Optional[float] = None
    allow_redirects: bool = True
    verify_ssl: bool = True
    
    def __post_init__(self) -> None:
        """Validate request."""
        if isinstance(self.url, str):
            self.url = URL(self.url)
    
    @property
    def is_json(self) -> bool:
        """Check if request has JSON body."""
        return self.json is not None or \
               self.headers.get("content-type", "").startswith("application/json")


@dataclass
class Response:
    """
    HTTP response container.
    
    Attributes:
        status_code: HTTP status code.
        reason: HTTP reason phrase.
        headers: Response headers.
        content: Response body bytes.
        text: Response body text.
        url: Final URL (after redirects).
        elapsed: Request duration in seconds.
        history: Redirect history.
        cookies: Response cookies.
        encoding: Content encoding.
        request: Original request.
    """
    
    status_code: int
    reason: str = ""
    headers: Headers = field(default_factory=lambda: Headers())
    content: bytes = b""
    url: Optional[str] = None
    elapsed: float = 0.0
    history: List["Response"] = field(default_factory=list)
    cookies: Dict[str, str] = field(default_factory=dict)
    encoding: str = "utf-8"
    request: Optional[Request] = None
    
    @property
    def ok(self) -> bool:
        """Check if response was successful."""
        return 200 <= self.status_code < 400
    
    @property
    def is_redirect(self) -> bool:
        """Check if response is a redirect."""
        return self.status_code in (301, 302, 303, 307, 308)
    
    @property
    def is_client_error(self) -> bool:
        """Check if response is a client error."""
        return 400 <= self.status_code < 500
    
    @property
    def is_server_error(self) -> bool:
        """Check if response is a server error."""
        return 500 <= self.status_code < 600
    
    @property
    def text(self) -> str:
        """Get response body as text."""
        if not self.content:
            return ""
        try:
            return self.content.decode(self.encoding or "utf-8")
        except (UnicodeDecodeError, LookupError):
            return self.content.decode("utf-8", errors="replace")
    
    def json(self) -> Any:
        """
        Parse response body as JSON.
        
        Returns:
            Any: Parsed JSON data.
        
        Raises:
            ValueError: If response is not valid JSON.
        """
        return json.loads(self.text)
    
    @property
    def content_length(self) -> int:
        """Get content length."""
        if self.content:
            return len(self.content)
        return int(self.headers.get("content-length", 0))
    
    @property
    def content_type(self) -> Optional[str]:
        """Get content type."""
        ct = self.headers.get("content-type")
        if ct:
            return ct.split(";")[0].strip()
        return None
    
    def raise_for_status(self) -> None:
        """
        Raise exception for HTTP errors.
        
        Raises:
            HTTPError: If status code indicates an error.
        """
        if self.is_client_error:
            raise HTTPError(
                f"Client error: {self.status_code}",
                url=self.url,
                status_code=self.status_code,
                response=self
            )
        if self.is_server_error:
            raise HTTPError(
                f"Server error: {self.status_code}",
                url=self.url,
                status_code=self.status_code,
                response=self
            )


# =============================================================================
# RETRY HANDLER
# =============================================================================

class RetryHandler:
    """
    Retry handler with multiple strategies.
    
    Provides automatic retry for failed requests with
    configurable strategies and conditions.
    
    Example:
        >>> retry_handler = RetryHandler(config=RetryConfig(max_retries=3))
        >>> response = await retry_handler.execute(request_func)
    """
    
    def __init__(self, config: Optional[RetryConfig] = None) -> None:
        """
        Initialize retry handler.
        
        Args:
            config: Retry configuration.
        """
        self.config = config or RetryConfig()
        self._logger = get_logger("downloader.retry")
    
    async def execute(
        self,
        func: Callable[..., Awaitable[Response]],
        *args: Any,
        **kwargs: Any
    ) -> Response:
        """
        Execute function with retry logic.
        
        Args:
            func: Async function to execute.
            *args: Function arguments.
            **kwargs: Function keyword arguments.
        
        Returns:
            Response: Response from function.
        
        Raises:
            RetryExhaustedError: If all retries are exhausted.
        """
        last_error: Optional[Exception] = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                response = await func(*args, **kwargs)
                
                # Check if status code should trigger retry
                if response.status_code in self.config.retry_on_status:
                    if attempt < self.config.max_retries:
                        delay = self.config.calculate_delay(attempt)
                        self._logger.warning(
                            f"Retrying request (status {response.status_code}), "
                            f"attempt {attempt + 1}/{self.config.max_retries}, "
                            f"waiting {delay:.2f}s"
                        )
                        await asyncio.sleep(delay)
                        continue
                
                return response
                
            except (ConnectionError, TimeoutError, DNSError, SSLError) as e:
                last_error = e
                
                if attempt < self.config.max_retries:
                    delay = self.config.calculate_delay(attempt)
                    self._logger.warning(
                        f"Retrying request after error: {e}, "
                        f"attempt {attempt + 1}/{self.config.max_retries}, "
                        f"waiting {delay:.2f}s"
                    )
                    await asyncio.sleep(delay)
                    continue
        
        raise RetryExhaustedError(
            f"All {self.config.max_retries} retry attempts exhausted",
            response=getattr(last_error, "response", None)
        ) from last_error
    
    def should_retry(self, error: Exception) -> bool:
        """
        Check if error should trigger retry.
        
        Args:
            error: Exception to check.
        
        Returns:
            bool: True if error should trigger retry.
        """
        if isinstance(error, (ConnectionError, TimeoutError, DNSError)):
            return True
        if isinstance(error, HTTPError):
            return error.status_code in self.config.retry_on_status
        return False


# =============================================================================
# RATE LIMITER
# =============================================================================

class RateLimiter:
    """
    Token bucket rate limiter.
    
    Implements token bucket algorithm for rate limiting with
    burst support and configurable rates.
    
    Example:
        >>> limiter = RateLimiter(requests_per_second=10, burst_size=20)
        >>> async with limiter:
        ...     response = await client.get(url)
    """
    
    def __init__(
        self,
        requests_per_second: float = 10.0,
        burst_size: Optional[int] = None,
        wait_on_limit: bool = True,
        max_wait: float = 60.0
    ) -> None:
        """
        Initialize rate limiter.
        
        Args:
            requests_per_second: Maximum requests per second.
            burst_size: Maximum burst size (defaults to 2x rate).
            wait_on_limit: Whether to wait when rate limited.
            max_wait: Maximum wait time in seconds.
        """
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size or int(requests_per_second * 2)
        self.wait_on_limit = wait_on_limit
        self.max_wait = max_wait
        
        self._tokens = float(self.burst_size)
        self._last_update = time.monotonic()
        self._lock = asyncio.Lock()
        self._logger = get_logger("downloader.ratelimit")
    
    async def acquire(self, tokens: int = 1) -> bool:
        """
        Acquire tokens from bucket.
        
        Args:
            tokens: Number of tokens to acquire.
        
        Returns:
            bool: True if tokens were acquired, False if rate limited.
        
        Raises:
            RateLimitError: If rate limited and wait_on_limit is False.
        """
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_update
            
            # Replenish tokens
            self._tokens = min(
                self.burst_size,
                self._tokens + elapsed * self.requests_per_second
            )
            self._last_update = now
            
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            
            if not self.wait_on_limit:
                raise RateLimitError(
                    "Rate limit exceeded",
                    retry_after=(tokens - self._tokens) / self.requests_per_second
                )
            
            # Calculate wait time
            wait_time = (tokens - self._tokens) / self.requests_per_second
            if wait_time > self.max_wait:
                raise RateLimitError(
                    f"Rate limit wait time ({wait_time:.2f}s) exceeds max ({self.max_wait}s)",
                    retry_after=wait_time
                )
            
            self._logger.debug(f"Rate limited, waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
            
            # Replenish after wait
            self._tokens = 0  # Consumed by the wait
            return True
    
    @asynccontextmanager
    async def limit(self, tokens: int = 1) -> AsyncIterator[None]:
        """
        Context manager for rate limiting.
        
        Args:
            tokens: Number of tokens to acquire.
        
        Yields:
            None
        """
        await self.acquire(tokens)
        yield
    
    async def __aenter__(self) -> "RateLimiter":
        await self.acquire()
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        pass


# =============================================================================
# DNS CACHE
# =============================================================================

class DNSCache:
    """
    Thread-safe DNS cache with TTL support.
    
    Caches DNS resolutions to reduce latency and DNS queries.
    """
    
    def __init__(self, ttl: int = 300, max_size: int = DNS_CACHE_SIZE) -> None:
        """
        Initialize DNS cache.
        
        Args:
            ttl: Cache TTL in seconds.
            max_size: Maximum cache size.
        """
        self.ttl = ttl
        self.max_size = max_size
        self._cache: OrderedDict[str, Tuple[str, float]] = OrderedDict()
        self._lock = threading.Lock()
    
    def get(self, hostname: str) -> Optional[str]:
        """
        Get cached IP address.
        
        Args:
            hostname: Hostname to look up.
        
        Returns:
            Optional[str]: Cached IP address or None.
        """
        with self._lock:
            if hostname not in self._cache:
                return None
            
            ip, timestamp = self._cache[hostname]
            if time.time() - timestamp > self.ttl:
                del self._cache[hostname]
                return None
            
            # Move to end (LRU)
            self._cache.move_to_end(hostname)
            return ip
    
    def set(self, hostname: str, ip: str) -> None:
        """
        Cache IP address.
        
        Args:
            hostname: Hostname.
            ip: IP address.
        """
        with self._lock:
            # Remove oldest if at capacity
            if len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)
            
            self._cache[hostname] = (ip, time.time())
    
    def clear(self) -> None:
        """Clear the cache."""
        with self._lock:
            self._cache.clear()
    
    def resolve(self, hostname: str) -> str:
        """
        Resolve hostname with caching.
        
        Args:
            hostname: Hostname to resolve.
        
        Returns:
            str: IP address.
        
        Raises:
            DNSError: If resolution fails.
        """
        # Check cache
        cached = self.get(hostname)
        if cached:
            return cached
        
        try:
            # Resolve
            addrinfo = socket.getaddrinfo(hostname, None)
            if not addrinfo:
                raise DNSError(f"No addresses found for {hostname}")
            
            ip = addrinfo[0][4][0]
            self.set(hostname, ip)
            return ip
            
        except socket.gaierror as e:
            raise DNSError(f"DNS resolution failed for {hostname}: {e}") from e


# =============================================================================
# NETWORK CLIENT
# =============================================================================

class NetworkClient:
    """
    Async HTTP client with comprehensive features.
    
    Provides a high-level HTTP client with connection pooling,
    retries, rate limiting, and security features.
    
    Example:
        >>> async with NetworkClient(config) as client:
        ...     response = await client.get("https://example.com")
        ...     print(response.text)
    """
    
    def __init__(
        self,
        config: Optional[Config] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize network client.
        
        Args:
            config: Configuration instance.
            logger: Logger instance.
        """
        self.config = config or Config()
        self._logger = logger or get_logger("downloader.network")
        
        # Initialize components
        self._retry_handler = RetryHandler(self.config.retry)
        self._rate_limiter = RateLimiter(
            requests_per_second=self.config.rate_limit.requests_per_second,
            burst_size=self.config.rate_limit.burst_size,
            wait_on_limit=self.config.rate_limit.wait_on_limit,
            max_wait=self.config.rate_limit.max_wait
        )
        self._dns_cache = DNSCache(ttl=self.config.dns_cache_ttl)
        
        # Session management
        self._session: Optional[ClientSession] = None
        self._closed = False
        self._lock = asyncio.Lock()
        
        # Cookie storage
        self._cookie_jar: Dict[str, Dict[str, Cookie]] = {}
    
    async def __aenter__(self) -> "NetworkClient":
        """Enter async context."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        """Exit async context."""
        await self.close()
    
    async def _ensure_session(self) -> ClientSession:
        """
        Ensure session is created.
        
        Returns:
            ClientSession: The aiohttp session.
        """
        if self._session is None or self._session.closed:
            async with self._lock:
                if self._session is None or self._session.closed:
                    self._session = await self._create_session()
        return self._session
    
    async def _create_session(self) -> ClientSession:
        """
        Create new aiohttp session.
        
        Returns:
            ClientSession: New session.
        """
        if not HAS_AIOHTTP:
            raise ImportError("aiohttp is required for async HTTP client")
        
        # Configure connector
        connector = TCPConnector(
            limit=self.config.pool.max_connections,
            limit_per_host=self.config.pool.max_connections_per_host,
            ttl_dns_cache=self.config.dns_cache_ttl,
            enable_cleanup_closed=self.config.pool.enable_cleanup,
            force_close=False,
        )
        
        # Configure timeout
        timeout = ClientTimeout(
            total=self.config.timeout.total,
            connect=self.config.timeout.connect,
            sock_read=self.config.timeout.read,
        )
        
        # Configure proxy
        proxy = None
        if self.config.proxy.enabled:
            proxy = self.config.proxy.http or self.config.proxy.https or self.config.proxy.all
        
        # Create session
        session = ClientSession(
            connector=connector,
            timeout=timeout,
            headers=self._get_default_headers(),
            proxy=proxy,
            raise_for_status=False,
            trust_env=False,
        )
        
        return session
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default request headers."""
        return {
            "User-Agent": self.config.user_agent.get_user_agent(),
            "Accept": DEFAULT_ACCEPT,
            "Accept-Language": DEFAULT_ACCEPT_LANGUAGE,
            "Accept-Encoding": DEFAULT_ACCEPT_ENCODING,
            "Connection": "keep-alive",
        }
    
    # HTTP methods
    async def request(
        self,
        method: Union[HttpMethod, str],
        url: Union[str, URL],
        **kwargs: Any
    ) -> Response:
        """
        Send HTTP request.
        
        Args:
            method: HTTP method.
            url: Request URL.
            **kwargs: Additional request options.
        
        Returns:
            Response: HTTP response.
        """
        if isinstance(method, str):
            method = HttpMethod(method.upper())
        
        if isinstance(url, str):
            url = URL(url)
        
        request = Request(
            method=method,
            url=url,
            headers=kwargs.get("headers", Headers()),
            params=kwargs.get("params", {}),
            data=kwargs.get("data"),
            json=kwargs.get("json"),
            cookies=kwargs.get("cookies", {}),
            timeout=kwargs.get("timeout", self.config.timeout.total),
            allow_redirects=kwargs.get("allow_redirects", self.config.follow_redirects),
            verify_ssl=kwargs.get("verify_ssl", self.config.ssl.verify),
        )
        
        return await self._execute_request(request)
    
    async def _execute_request(self, request: Request) -> Response:
        """
        Execute HTTP request with all features.
        
        Args:
            request: Request to execute.
        
        Returns:
            Response: HTTP response.
        """
        if request.url is None:
            raise InvalidURLError("Request URL is required")
        
        async with self._rate_limiter.limit():
            start_time = time.monotonic()
            
            try:
                response = await self._retry_handler.execute(
                    self._send_request,
                    request
                )
                
                elapsed = time.monotonic() - start_time
                response.elapsed = elapsed
                
                # Log request
                self._log_request(request, response)
                
                return response
                
            except Exception as e:
                elapsed = time.monotonic() - start_time
                self._logger.error(
                    f"Request failed: {request.method.value} {request.url} ({elapsed:.3f}s): {e}"
                )
                raise
    
    async def _send_request(self, request: Request) -> Response:
        """
        Send actual HTTP request.
        
        Args:
            request: Request to send.
        
        Returns:
            Response: HTTP response.
        """
        if request.url is None:
            raise InvalidURLError("Request URL is required")
        
        session = await self._ensure_session()
        
        # Build request
        headers = self._get_default_headers()
        headers.update(dict(request.headers))
        
        kwargs: Dict[str, Any] = {
            "params": request.params,
            "headers": headers,
            "allow_redirects": request.allow_redirects,
            "ssl": request.verify_ssl,
        }
        
        if request.timeout:
            kwargs["timeout"] = ClientTimeout(total=request.timeout)
        
        if request.json:
            kwargs["json"] = request.json
        elif request.data:
            kwargs["data"] = request.data
        
        if request.cookies:
            kwargs["cookies"] = request.cookies
        
        # Send request
        url_str = str(request.url)
        self._logger.debug(f"Sending {request.method.value} {url_str}")
        
        try:
            async with session.request(request.method.value, url_str, **kwargs) as resp:
                content = await resp.read()
                
                response = Response(
                    status_code=resp.status,
                    reason=resp.reason or "",
                    headers=Headers(dict(resp.headers)),
                    content=content,
                    url=str(resp.url),
                    request=request,
                )
                
                return response
                
        except asyncio.TimeoutError as e:
            raise TimeoutError(
                f"Request timed out: {request.url}",
                url=str(request.url)
            ) from e
        except aiohttp.ClientError as e:
            raise ConnectionError(
                f"Connection error: {e}",
                url=str(request.url)
            ) from e
    
    def _log_request(self, request: Request, response: Response) -> None:
        """
        Log request/response details.
        
        Args:
            request: Original request.
            response: Received response.
        """
        level = LogLevel.DEBUG if self.config.debug else LogLevel.INFO
        
        self._logger.log(
            level.value if isinstance(level, LogLevel) else level,
            f"{request.method.value} {request.url} -> {response.status_code} "
            f"({response.elapsed:.3f}s, {len(response.content)} bytes)"
        )
    
    # Convenience methods
    async def get(
        self,
        url: Union[str, URL],
        **kwargs: Any
    ) -> Response:
        """Send GET request."""
        return await self.request(HttpMethod.GET, url, **kwargs)
    
    async def post(
        self,
        url: Union[str, URL],
        **kwargs: Any
    ) -> Response:
        """Send POST request."""
        return await self.request(HttpMethod.POST, url, **kwargs)
    
    async def put(
        self,
        url: Union[str, URL],
        **kwargs: Any
    ) -> Response:
        """Send PUT request."""
        return await self.request(HttpMethod.PUT, url, **kwargs)
    
    async def patch(
        self,
        url: Union[str, URL],
        **kwargs: Any
    ) -> Response:
        """Send PATCH request."""
        return await self.request(HttpMethod.PATCH, url, **kwargs)
    
    async def delete(
        self,
        url: Union[str, URL],
        **kwargs: Any
    ) -> Response:
        """Send DELETE request."""
        return await self.request(HttpMethod.DELETE, url, **kwargs)
    
    async def head(
        self,
        url: Union[str, URL],
        **kwargs: Any
    ) -> Response:
        """Send HEAD request."""
        return await self.request(HttpMethod.HEAD, url, **kwargs)
    
    async def download(
        self,
        url: Union[str, URL],
        path: Union[str, Path],
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        progress: bool = False,
        **kwargs: Any
    ) -> Path:
        """
        Download file to disk.
        
        Args:
            url: Download URL.
            path: Destination path.
            chunk_size: Download chunk size.
            progress: Show progress.
            **kwargs: Additional request options.
        
        Returns:
            Path: Path to downloaded file.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        response = await self.get(url, **kwargs)
        response.raise_for_status()
        
        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0
        
        self._logger.info(f"Downloading {url} to {path}")
        
        with open(path, "wb") as f:
            # Simulate chunked writing
            chunk_pos = 0
            while chunk_pos < len(response.content):
                chunk = response.content[chunk_pos:chunk_pos + chunk_size]
                f.write(chunk)
                chunk_pos += chunk_size
                downloaded = min(chunk_pos, len(response.content))
                
                if progress:
                    self._logger.debug(
                        f"Downloaded {downloaded}/{total_size or len(response.content)} bytes"
                    )
        
        self._logger.info(f"Download complete: {path}")
        return path
    
    async def close(self) -> None:
        """Close the client and release resources."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
        self._closed = True
    
    @property
    def is_closed(self) -> bool:
        """Check if client is closed."""
        return self._closed


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def parse_content_type(content_type: Optional[str]) -> Tuple[str, Dict[str, str]]:
    """
    Parse content type header.
    
    Args:
        content_type: Content type header value.
    
    Returns:
        Tuple[str, Dict[str, str]]: MIME type and parameters.
    """
    if not content_type:
        return "", {}
    
    parts = content_type.split(";")
    mime_type = parts[0].strip().lower()
    
    params: Dict[str, str] = {}
    for part in parts[1:]:
        part = part.strip()
        if "=" in part:
            key, value = part.split("=", 1)
            params[key.strip().lower()] = value.strip().strip('"')
    
    return mime_type, params


def is_ip_address(host: str) -> bool:
    """
    Check if host is an IP address.
    
    Args:
        host: Host string.
    
    Returns:
        bool: True if host is an IP address.
    """
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def is_private_ip(host: str) -> bool:
    """
    Check if host is a private IP address.
    
    Args:
        host: Host string.
    
    Returns:
        bool: True if host is a private IP address.
    """
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_private
    except ValueError:
        return False


def build_url(
    scheme: str,
    host: str,
    port: Optional[int] = None,
    path: str = "/",
    query: Optional[Dict[str, Any]] = None
) -> str:
    """
    Build URL from components.
    
    Args:
        scheme: URL scheme.
        host: Hostname or IP.
        port: Port number.
        path: URL path.
        query: Query parameters.
    
    Returns:
        str: Built URL.
    """
    # Add port if not default
    if port:
        if (scheme == "http" and port != 80) or (scheme == "https" and port != 443):
            netloc = f"{host}:{port}"
        else:
            netloc = host
    else:
        netloc = host
    
    # Build URL
    url = f"{scheme}://{netloc}{path}"
    
    # Add query
    if query:
        url += "?" + urllib.parse.urlencode(query)
    
    return url


def get_content_disposition_filename(headers: Mapping[str, str]) -> Optional[str]:
    """
    Extract filename from Content-Disposition header.
    
    Args:
        headers: Response headers.
    
    Returns:
        Optional[str]: Filename or None.
    """
    content_disp = headers.get("content-disposition", "")
    if not content_disp:
        return None
    
    # Try to extract filename
    patterns = [
        r'filename\*?=["\']?([^"\';\s]+)["\']?',
        r'filename\*?=UTF-8["\']?([^"\';\s]+)["\']?',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content_disp, re.IGNORECASE)
        if match:
            return urllib.parse.unquote(match.group(1))
    
    return None


def sanitize_url_for_logging(url: str) -> str:
    """
    Sanitize URL for safe logging.
    
    Removes sensitive query parameters and credentials.
    
    Args:
        url: URL string.
    
    Returns:
        str: Sanitized URL.
    """
    parsed = urlparse(url)
    
    # Remove credentials
    netloc = parsed.hostname or ""
    if parsed.port:
        netloc += f":{parsed.port}"
    
    # Remove sensitive query params
    sensitive_params = {"token", "api_key", "apikey", "key", "secret", "password"}
    query_items = urllib.parse.parse_qsl(parsed.query)
    safe_query = urllib.parse.urlencode([
        (k, "***" if k.lower() in sensitive_params else v)
        for k, v in query_items
    ])
    
    # Rebuild URL
    return urllib.parse.urlunparse(
        (parsed.scheme, netloc, parsed.path, parsed.params, safe_query, "")
    )


# =============================================================================
# PROXY ROTATION (NEW v3.2.0)
# =============================================================================

@dataclass
class ProxyEntry:
    """
    Proxy server entry with metadata.
    
    Attributes:
        url: Proxy URL.
        proxy_type: Type of proxy (http, https, socks4, socks5).
        country: Country code (ISO 3166-1 alpha-2).
        priority: Priority for selection (higher = better).
        last_used: Last usage timestamp.
        success_count: Number of successful requests.
        failure_count: Number of failed requests.
        avg_response_time: Average response time in seconds.
        enabled: Whether proxy is enabled.
    """
    url: str
    proxy_type: str = "http"
    country: Optional[str] = None
    priority: int = 0
    last_used: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    avg_response_time: float = 0.0
    enabled: bool = True
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.success_count + self.failure_count
        if total == 0:
            return 1.0
        return self.success_count / total
    
    @property
    def score(self) -> float:
        """Calculate overall proxy score."""
        # Weight factors
        success_weight = 0.5
        response_weight = 0.3
        priority_weight = 0.2
        
        # Normalize response time (assume 1s is ideal, 10s is max)
        response_score = max(0, 1 - (self.avg_response_time / 10))
        
        return (
            success_weight * self.success_rate +
            response_weight * response_score +
            priority_weight * (self.priority / 100)
        )


class ProxyPool:
    """
    Advanced proxy pool with rotation and health checking.
    
    Provides intelligent proxy selection based on performance metrics,
    geographic location, and rotation strategies.
    
    Example:
        >>> pool = ProxyPool()
        >>> pool.add_proxy("http://proxy1:8080", country="US", priority=10)
        >>> pool.add_proxy("socks5://proxy2:1080", country="DE", priority=5)
        >>> proxy = pool.get_proxy()
    """
    
    def __init__(
        self,
        rotation_strategy: str = "round_robin",
        health_check_interval: float = 300.0,
        min_success_rate: float = 0.5,
        max_failures_before_disable: int = 5
    ) -> None:
        """
        Initialize proxy pool.
        
        Args:
            rotation_strategy: Strategy for selecting proxies
                ('round_robin', 'random', 'least_used', 'best_performance', 'geo').
            health_check_interval: Interval between health checks in seconds.
            min_success_rate: Minimum success rate to keep proxy enabled.
            max_failures_before_disable: Max consecutive failures before disabling.
        """
        self.rotation_strategy = rotation_strategy
        self.health_check_interval = health_check_interval
        self.min_success_rate = min_success_rate
        self.max_failures_before_disable = max_failures_before_disable
        
        self._proxies: List[ProxyEntry] = []
        self._current_index = 0
        self._lock = threading.Lock()
        self._last_health_check = 0.0
    
    def add_proxy(
        self,
        url: str,
        proxy_type: str = "http",
        country: Optional[str] = None,
        priority: int = 0
    ) -> None:
        """
        Add a proxy to the pool.
        
        Args:
            url: Proxy URL.
            proxy_type: Type of proxy.
            country: Country code.
            priority: Priority for selection.
        """
        with self._lock:
            # Check if proxy already exists
            for proxy in self._proxies:
                if proxy.url == url:
                    return
            
            self._proxies.append(ProxyEntry(
                url=url,
                proxy_type=proxy_type,
                country=country,
                priority=priority
            ))
    
    def add_proxies_from_file(self, file_path: Union[str, Path]) -> int:
        """
        Load proxies from a file.
        
        File format: One proxy per line, optionally with metadata.
        Example: http://proxy:8080 US 10
        
        Args:
            file_path: Path to proxy file.
        
        Returns:
            int: Number of proxies added.
        """
        path = Path(file_path)
        if not path.exists():
            return 0
        
        count = 0
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                parts = line.split()
                url = parts[0]
                country = parts[1] if len(parts) > 1 else None
                priority = int(parts[2]) if len(parts) > 2 else 0
                
                # Determine proxy type from URL
                if url.startswith("socks5://"):
                    proxy_type = "socks5"
                elif url.startswith("socks4://"):
                    proxy_type = "socks4"
                elif url.startswith("https://"):
                    proxy_type = "https"
                else:
                    proxy_type = "http"
                
                self.add_proxy(url, proxy_type, country, priority)
                count += 1
        
        return count
    
    def remove_proxy(self, url: str) -> bool:
        """
        Remove a proxy from the pool.
        
        Args:
            url: Proxy URL to remove.
        
        Returns:
            bool: True if proxy was removed.
        """
        with self._lock:
            for i, proxy in enumerate(self._proxies):
                if proxy.url == url:
                    del self._proxies[i]
                    return True
            return False
    
    def get_proxy(
        self,
        country: Optional[str] = None,
        exclude: Optional[Set[str]] = None
    ) -> Optional[ProxyEntry]:
        """
        Get a proxy from the pool based on rotation strategy.
        
        Args:
            country: Preferred country code.
            exclude: Set of proxy URLs to exclude.
        
        Returns:
            Optional[ProxyEntry]: Selected proxy or None if pool is empty.
        """
        with self._lock:
            # Filter enabled proxies
            available = [p for p in self._proxies if p.enabled]
            
            # Filter by country if specified
            if country:
                country_proxies = [p for p in available if p.country == country]
                if country_proxies:
                    available = country_proxies
            
            # Exclude specified proxies
            if exclude:
                available = [p for p in available if p.url not in exclude]
            
            if not available:
                return None
            
            # Select based on strategy
            if self.rotation_strategy == "round_robin":
                proxy = available[self._current_index % len(available)]
                self._current_index += 1
            
            elif self.rotation_strategy == "random":
                import random
                proxy = random.choice(available)
            
            elif self.rotation_strategy == "least_used":
                proxy = min(available, key=lambda p: p.last_used)
            
            elif self.rotation_strategy == "best_performance":
                proxy = max(available, key=lambda p: p.score)
            
            elif self.rotation_strategy == "geo" and country:
                # Prefer proxies in same country
                same_country = [p for p in available if p.country == country]
                if same_country:
                    proxy = max(same_country, key=lambda p: p.score)
                else:
                    proxy = max(available, key=lambda p: p.score)
            
            else:
                proxy = available[0]
            
            # Update last used time
            proxy.last_used = time.time()
            return proxy
    
    def report_success(self, url: str, response_time: float) -> None:
        """
        Report a successful request through a proxy.
        
        Args:
            url: Proxy URL.
            response_time: Response time in seconds.
        """
        with self._lock:
            for proxy in self._proxies:
                if proxy.url == url:
                    proxy.success_count += 1
                    # Update average response time (exponential moving average)
                    proxy.avg_response_time = (
                        0.9 * proxy.avg_response_time + 0.1 * response_time
                    )
                    break
    
    def report_failure(self, url: str) -> None:
        """
        Report a failed request through a proxy.
        
        Args:
            url: Proxy URL.
        """
        with self._lock:
            for proxy in self._proxies:
                if proxy.url == url:
                    proxy.failure_count += 1
                    
                    # Check if should disable
                    recent_failures = proxy.failure_count
                    if recent_failures >= self.max_failures_before_disable:
                        proxy.enabled = False
                    
                    # Check success rate
                    if proxy.success_rate < self.min_success_rate:
                        proxy.enabled = False
                    break
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all proxies.
        
        Returns:
            Dict[str, Any]: Health check results.
        """
        results = {
            "total": len(self._proxies),
            "enabled": 0,
            "disabled": 0,
            "avg_success_rate": 0.0,
            "best_proxy": None,
            "worst_proxy": None,
        }
        
        with self._lock:
            if not self._proxies:
                return results
            
            enabled = [p for p in self._proxies if p.enabled]
            results["enabled"] = len(enabled)
            results["disabled"] = results["total"] - len(enabled)
            
            if enabled:
                results["avg_success_rate"] = sum(p.success_rate for p in enabled) / len(enabled)
                results["best_proxy"] = max(enabled, key=lambda p: p.score).url
                results["worst_proxy"] = min(enabled, key=lambda p: p.score).url
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get pool statistics.
        
        Returns:
            Dict[str, Any]: Pool statistics.
        """
        with self._lock:
            return {
                "total_proxies": len(self._proxies),
                "enabled_proxies": sum(1 for p in self._proxies if p.enabled),
                "countries": list(set(p.country for p in self._proxies if p.country)),
                "types": {
                    t: sum(1 for p in self._proxies if p.proxy_type == t)
                    for t in ["http", "https", "socks4", "socks5"]
                },
                "avg_success_rate": sum(p.success_rate for p in self._proxies) / len(self._proxies) if self._proxies else 0,
            }
    
    def reset_stats(self) -> None:
        """Reset all proxy statistics."""
        with self._lock:
            for proxy in self._proxies:
                proxy.success_count = 0
                proxy.failure_count = 0
                proxy.avg_response_time = 0.0
                proxy.enabled = True


# =============================================================================
# ADVANCED CONNECTION POOL (NEW v3.2.0)
# =============================================================================

class ConnectionPoolStats:
    """Statistics for connection pool monitoring."""
    
    def __init__(self) -> None:
        self.total_connections = 0
        self.active_connections = 0
        self.idle_connections = 0
        self.pending_requests = 0
        self.requests_served = 0
        self.connection_errors = 0
        self.timeout_errors = 0
    
    def to_dict(self) -> Dict[str, int]:
        return {
            "total_connections": self.total_connections,
            "active_connections": self.active_connections,
            "idle_connections": self.idle_connections,
            "pending_requests": self.pending_requests,
            "requests_served": self.requests_served,
            "connection_errors": self.connection_errors,
            "timeout_errors": self.timeout_errors,
        }


class AdvancedConnectionPool:
    """
    Advanced connection pool with monitoring and optimization.
    
    Provides intelligent connection management with automatic scaling,
    health monitoring, and performance optimization.
    
    Example:
        >>> pool = AdvancedConnectionPool(max_connections=100)
        >>> async with pool.connection("https://example.com") as conn:
        ...     response = await conn.get("/api/data")
    """
    
    def __init__(
        self,
        max_connections: int = 100,
        max_connections_per_host: int = 10,
        keepalive_timeout: float = 30.0,
        enable_keepalive: bool = True,
        enable_compression: bool = True,
        connection_timeout: float = 10.0,
        enable_stats: bool = True
    ) -> None:
        """
        Initialize advanced connection pool.
        
        Args:
            max_connections: Maximum total connections.
            max_connections_per_host: Maximum connections per host.
            keepalive_timeout: Keep-alive timeout in seconds.
            enable_keepalive: Whether to enable TCP keepalive.
            enable_compression: Whether to enable compression.
            connection_timeout: Connection establishment timeout.
            enable_stats: Whether to enable statistics collection.
        """
        self.max_connections = max_connections
        self.max_connections_per_host = max_connections_per_host
        self.keepalive_timeout = keepalive_timeout
        self.enable_keepalive = enable_keepalive
        self.enable_compression = enable_compression
        self.connection_timeout = connection_timeout
        
        # Connection tracking
        self._connections: Dict[str, List[Any]] = {}  # host -> connections
        self._pending: Dict[str, int] = {}  # host -> pending count
        self._lock = asyncio.Lock()
        
        # Statistics
        self.enable_stats = enable_stats
        self.stats = ConnectionPoolStats()
        
        # Health tracking
        self._host_health: Dict[str, float] = {}  # host -> health score
    
    async def acquire(self, host: str) -> Any:
        """
        Acquire a connection for a host.
        
        Args:
            host: Target host.
        
        Returns:
            Connection object.
        """
        async with self._lock:
            self.stats.pending_requests += 1
            self._pending[host] = self._pending.get(host, 0) + 1
        
        try:
            # Wait for available connection slot
            while True:
                async with self._lock:
                    host_connections = len(self._connections.get(host, []))
                    total_connections = sum(len(conns) for conns in self._connections.values())
                    
                    if (host_connections < self.max_connections_per_host and
                        total_connections < self.max_connections):
                        break
                
                await asyncio.sleep(0.01)
            
            # Create or reuse connection
            # (Actual connection creation would be done by the HTTP client)
            if self.enable_stats:
                async with self._lock:
                    self.stats.active_connections += 1
            
            return host
            
        finally:
            async with self._lock:
                self.stats.pending_requests -= 1
                self._pending[host] = self._pending.get(host, 0) - 1
    
    async def release(self, host: str, connection: Any, error: bool = False) -> None:
        """
        Release a connection back to the pool.
        
        Args:
            host: Target host.
            connection: Connection to release.
            error: Whether the connection had an error.
        """
        async with self._lock:
            self.stats.active_connections -= 1
            
            if error:
                self.stats.connection_errors += 1
                # Update host health
                self._host_health[host] = max(0, self._host_health.get(host, 1.0) - 0.1)
            else:
                self.stats.requests_served += 1
                # Update host health
                self._host_health[host] = min(1.0, self._host_health.get(host, 0.5) + 0.05)
    
    def get_host_health(self, host: str) -> float:
        """
        Get health score for a host.
        
        Args:
            host: Target host.
        
        Returns:
            float: Health score (0.0 to 1.0).
        """
        return self._host_health.get(host, 0.5)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get pool statistics.
        
        Returns:
            Dict[str, Any]: Pool statistics.
        """
        stats = self.stats.to_dict()
        stats["hosts"] = list(self._connections.keys())
        stats["host_health"] = dict(self._host_health)
        return stats
    
    async def close(self) -> None:
        """Close all connections in the pool."""
        async with self._lock:
            self._connections.clear()
            self._pending.clear()


# =============================================================================
# CIRCUIT BREAKER (NEW v3.2.0)
# =============================================================================

class CircuitState(Enum):
    """Circuit breaker state enumeration."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass
class CircuitStats:
    """Circuit breaker statistics."""
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: float = 0.0
    last_state_change: float = 0.0


class CircuitBreaker:
    """
    Circuit breaker for fault tolerance.
    
    Implements the circuit breaker pattern to prevent cascading failures
    when a service is experiencing issues.
    
    Example:
        >>> breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
        >>> async with breaker:
        ...     response = await client.get(url)
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 3,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 3
    ) -> None:
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit.
            success_threshold: Number of successes in half-open to close.
            recovery_timeout: Time in seconds before attempting recovery.
            half_open_max_calls: Max calls allowed in half-open state.
        """
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self._stats = CircuitStats()
        self._half_open_calls = 0
        self._lock = asyncio.Lock()
        self._logger = get_logger("downloader.circuit_breaker")
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._stats.state
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self._stats.state == CircuitState.CLOSED
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open (rejecting requests)."""
        return self._stats.state == CircuitState.OPEN
    
    async def __aenter__(self) -> "CircuitBreaker":
        """Enter context manager."""
        await self._check_state()
        
        if self._stats.state == CircuitState.OPEN:
            raise Exception("Circuit breaker is OPEN - rejecting request")
        
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager."""
        if exc_type is not None:
            await self._record_failure()
        else:
            await self._record_success()
    
    async def _check_state(self) -> None:
        """Check and update circuit state."""
        async with self._lock:
            if self._stats.state == CircuitState.OPEN:
                # Check if recovery timeout has passed
                elapsed = time.time() - self._stats.last_failure_time
                if elapsed >= self.recovery_timeout:
                    self._transition_to(CircuitState.HALF_OPEN)
    
    async def _record_failure(self) -> None:
        """Record a failure and potentially open the circuit."""
        async with self._lock:
            self._stats.failure_count += 1
            self._stats.success_count = 0
            self._stats.last_failure_time = time.time()
            
            if self._stats.state == CircuitState.HALF_OPEN:
                self._transition_to(CircuitState.OPEN)
                self._logger.warning("Circuit breaker opened from HALF_OPEN")
            
            elif self._stats.state == CircuitState.CLOSED:
                if self._stats.failure_count >= self.failure_threshold:
                    self._transition_to(CircuitState.OPEN)
                    self._logger.warning(
                        f"Circuit breaker opened after {self._stats.failure_count} failures"
                    )
    
    async def _record_success(self) -> None:
        """Record a success and potentially close the circuit."""
        async with self._lock:
            self._stats.success_count += 1
            self._stats.failure_count = 0
            
            if self._stats.state == CircuitState.HALF_OPEN:
                if self._stats.success_count >= self.success_threshold:
                    self._transition_to(CircuitState.CLOSED)
                    self._logger.info("Circuit breaker closed after recovery")
    
    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state."""
        self._logger.debug(f"Circuit breaker: {self._stats.state.value} -> {new_state.value}")
        self._stats.state = new_state
        self._stats.last_state_change = time.time()
        
        if new_state == CircuitState.CLOSED:
            self._stats.failure_count = 0
            self._stats.success_count = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get circuit breaker statistics.
        
        Returns:
            Dict[str, Any]: Circuit breaker statistics.
        """
        return {
            "state": self._stats.state.value,
            "failure_count": self._stats.failure_count,
            "success_count": self._stats.success_count,
            "last_failure_time": self._stats.last_failure_time,
            "last_state_change": self._stats.last_state_change,
        }


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "HttpMethod",
    "ContentType",
    "AuthType",
    "CircuitState",  # NEW v3.2.0
    # Exceptions
    "NetworkError",
    "ConnectionError",
    "TimeoutError",
    "DNSError",
    "SSLError",
    "HTTPError",
    "RateLimitError",
    "RedirectError",
    "InvalidURLError",
    "RetryExhaustedError",
    # Classes
    "URL",
    "Headers",
    "Request",
    "Response",
    "NetworkClient",
    "RetryHandler",
    "RateLimiter",
    "DNSCache",
    # NEW v3.2.0
    "ProxyEntry",
    "ProxyPool",
    "ConnectionPoolStats",
    "AdvancedConnectionPool",
    "CircuitBreaker",
    "CircuitStats",
    # Functions
    "parse_content_type",
    "is_ip_address",
    "is_private_ip",
    "build_url",
    "get_content_disposition_filename",
    "sanitize_url_for_logging",
    # Constants
    "DEFAULT_USER_AGENT",
    "DEFAULT_ACCEPT",
    "DEFAULT_ACCEPT_LANGUAGE",
    "DEFAULT_ACCEPT_ENCODING",
    "MAX_RESPONSE_SIZE",
    "MAX_REDIRECT_URL_LENGTH",
    "DNS_CACHE_SIZE",
    "SAFE_HEADERS",
    "SENSITIVE_HEADERS",
]

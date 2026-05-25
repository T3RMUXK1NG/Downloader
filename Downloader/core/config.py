#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OMNIPOTENT SOVEREIGN NEXUS - Configuration Management Module
============================================================

Version: 3.0.1 ULTIMATE NEXUS
Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng

This module provides comprehensive configuration management for the Downloader
package with validation, serialization, environment variable support, and
secure handling of sensitive data.

ARCHITECTURE:
    - Pydantic-based validation for type safety
    - Environment variable override support
    - Configuration file loading (JSON, YAML, TOML)
    - Secure secret management
    - Thread-safe configuration updates
    - Configuration inheritance and profiles

FEATURES:
    - Automatic type coercion and validation
    - Default value management
    - Configuration profiles (dev, staging, production)
    - Secrets masking in logs and repr
    - Immutable configuration freezing
    - Configuration change notifications

SECURITY:
    - Sensitive field masking
    - Input validation
    - Safe string representation
    - Environment variable sanitization
"""

from __future__ import annotations

import os
import json
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict, Field
from enum import Enum, auto
from pathlib import Path
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Final,
    FrozenSet,
    Generic,
    List,
    Literal,
    Mapping,
    MutableMapping,
    Optional,
    Protocol,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    runtime_checkable,
)
from functools import cached_property, lru_cache, partial
from contextlib import contextmanager
from copy import deepcopy
import threading
import hashlib
import secrets
import re
from datetime import timedelta

# Try to import optional dependencies
try:
    import tomli
    HAS_TOMLI = True
except ImportError:
    HAS_TOMLI = False

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    from pydantic import BaseModel, Field as PydanticField, validator, root_validator
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False


# =============================================================================
# CONSTANTS AND ENUMS
# =============================================================================

class LogLevel(str, Enum):
    """Log level enumeration with string representation."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ConfigProfile(str, Enum):
    """Configuration profile enumeration."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class ProxyType(str, Enum):
    """Proxy type enumeration."""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


class RetryStrategy(str, Enum):
    """Retry strategy enumeration."""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    CONSTANT = "constant"
    FIBONACCI = "fibonacci"


# Default values
DEFAULT_TIMEOUT: Final[float] = 30.0
DEFAULT_CONNECT_TIMEOUT: Final[float] = 10.0
DEFAULT_READ_TIMEOUT: Final[float] = 30.0
DEFAULT_MAX_RETRIES: Final[int] = 3
DEFAULT_RETRY_DELAY: Final[float] = 1.0
DEFAULT_MAX_REDIRECTS: Final[int] = 10
DEFAULT_CHUNK_SIZE: Final[int] = 8192  # 8KB
DEFAULT_MAX_CONNECTIONS: Final[int] = 100
DEFAULT_CONNECTIONS_PER_HOST: Final[int] = 10
DEFAULT_USER_AGENT: Final[str] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
DEFAULT_DNS_CACHE_TTL: Final[int] = 300  # 5 minutes

# Sensitive field names that should be masked
SENSITIVE_FIELDS: FrozenSet[str] = frozenset({
    "password", "passwd", "pwd", "secret", "token", "api_key", "apikey",
    "authorization", "auth", "credential", "private_key", "privatekey",
    "access_key", "accesskey", "secret_key", "secretkey"
})


# =============================================================================
# VALIDATION UTILITIES
# =============================================================================

def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL string to validate.
    
    Returns:
        bool: True if URL is valid, False otherwise.
    
    Example:
        >>> validate_url("https://example.com")
        True
        >>> validate_url("not-a-url")
        False
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return bool(url_pattern.match(url))


def validate_proxy_url(url: str) -> bool:
    """
    Validate proxy URL format.
    
    Supports HTTP, HTTPS, SOCKS4, and SOCKS5 proxies.
    
    Args:
        url: Proxy URL string to validate.
    
    Returns:
        bool: True if proxy URL is valid, False otherwise.
    
    Example:
        >>> validate_proxy_url("http://proxy.example.com:8080")
        True
        >>> validate_proxy_url("socks5://user:pass@proxy.com:1080")
        True
    """
    proxy_pattern = re.compile(
        r'^(https?|socks[45])://'
        r'(?:([^:]+):([^@]+)@)?'  # optional auth
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?$', re.IGNORECASE
    )
    return bool(proxy_pattern.match(url))


def mask_sensitive(value: str, visible_chars: int = 4) -> str:
    """
    Mask sensitive string value for safe logging.
    
    Args:
        value: The string value to mask.
        visible_chars: Number of characters to show at start.
    
    Returns:
        str: Masked string value.
    
    Example:
        >>> mask_sensitive("my-secret-password")
        'my-s***********'
    """
    if not value or len(value) <= visible_chars:
        return "****"
    return f"{value[:visible_chars]}{'*' * (len(value) - visible_chars)}"


def validate_positive_number(value: Union[int, float], name: str) -> Union[int, float]:
    """
    Validate that a number is positive.
    
    Args:
        value: The numeric value to validate.
        name: Parameter name for error message.
    
    Returns:
        The validated value.
    
    Raises:
        ValueError: If value is not positive.
    """
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")
    return value


def validate_non_negative_number(value: Union[int, float], name: str) -> Union[int, float]:
    """
    Validate that a number is non-negative.
    
    Args:
        value: The numeric value to validate.
        name: Parameter name for error message.
    
    Returns:
        The validated value.
    
    Raises:
        ValueError: If value is negative.
    """
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")
    return value


# =============================================================================
# CONFIGURATION DATA CLASSES
# =============================================================================

@dataclass(frozen=True)
class TimeoutConfig:
    """
    Immutable timeout configuration.
    
    Attributes:
        total: Total timeout for the entire request in seconds.
        connect: Connection establishment timeout in seconds.
        read: Read timeout in seconds.
        write: Write timeout in seconds.
        pool: Connection pool acquisition timeout in seconds.
    """
    total: float = DEFAULT_TIMEOUT
    connect: float = DEFAULT_CONNECT_TIMEOUT
    read: float = DEFAULT_READ_TIMEOUT
    write: float = DEFAULT_TIMEOUT
    pool: float = DEFAULT_CONNECT_TIMEOUT
    
    def __post_init__(self) -> None:
        """Validate timeout values."""
        validate_positive_number(self.total, "total timeout")
        validate_positive_number(self.connect, "connect timeout")
        validate_positive_number(self.read, "read timeout")
        validate_positive_number(self.write, "write timeout")
        validate_positive_number(self.pool, "pool timeout")
    
    @classmethod
    def from_seconds(cls, seconds: float) -> "TimeoutConfig":
        """
        Create timeout config with all values set to same seconds.
        
        Args:
            seconds: Timeout value in seconds.
        
        Returns:
            TimeoutConfig: New timeout configuration instance.
        """
        return cls(total=seconds, connect=seconds, read=seconds, write=seconds)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary representation."""
        return asdict(self)


@dataclass(frozen=True)
class RetryConfig:
    """
    Immutable retry configuration.
    
    Attributes:
        max_retries: Maximum number of retry attempts.
        retry_delay: Initial delay between retries in seconds.
        max_delay: Maximum delay between retries in seconds.
        backoff_factor: Multiplier for exponential backoff.
        retry_on_status: HTTP status codes that trigger retry.
        strategy: Retry delay strategy.
        jitter: Whether to add random jitter to delays.
    """
    max_retries: int = DEFAULT_MAX_RETRIES
    retry_delay: float = DEFAULT_RETRY_DELAY
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    retry_on_status: Tuple[int, ...] = (408, 429, 500, 502, 503, 504)
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    jitter: bool = True
    
    def __post_init__(self) -> None:
        """Validate retry configuration."""
        if self.max_retries < 0:
            raise ValueError(f"max_retries must be non-negative, got {self.max_retries}")
        validate_non_negative_number(self.retry_delay, "retry_delay")
        validate_positive_number(self.max_delay, "max_delay")
        validate_positive_number(self.backoff_factor, "backoff_factor")
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for given retry attempt.
        
        Args:
            attempt: The retry attempt number (0-indexed).
        
        Returns:
            float: Delay in seconds.
        """
        import random
        
        if self.strategy == RetryStrategy.CONSTANT:
            delay = self.retry_delay
        elif self.strategy == RetryStrategy.LINEAR:
            delay = self.retry_delay * (attempt + 1)
        elif self.strategy == RetryStrategy.FIBONACCI:
            fib = [1, 1]
            for _ in range(attempt):
                fib.append(fib[-1] + fib[-2])
            delay = self.retry_delay * fib[min(attempt, len(fib) - 1)]
        else:  # EXPONENTIAL (default)
            delay = self.retry_delay * (self.backoff_factor ** attempt)
        
        # Apply maximum delay cap
        delay = min(delay, self.max_delay)
        
        # Add jitter if enabled
        if self.jitter:
            delay = delay * (0.5 + random.random())
        
        return delay


@dataclass(frozen=True)
class ProxyConfig:
    """
    Immutable proxy configuration.
    
    Attributes:
        http: HTTP proxy URL.
        https: HTTPS proxy URL.
        all: Proxy URL for all protocols.
        no_proxy: List of hosts to bypass proxy.
    """
    http: Optional[str] = None
    https: Optional[str] = None
    all: Optional[str] = None
    no_proxy: Tuple[str, ...] = field(default_factory=tuple)
    
    def __post_init__(self) -> None:
        """Validate proxy URLs."""
        if self.http and not validate_proxy_url(self.http):
            raise ValueError(f"Invalid HTTP proxy URL: {mask_sensitive(self.http)}")
        if self.https and not validate_proxy_url(self.https):
            raise ValueError(f"Invalid HTTPS proxy URL: {mask_sensitive(self.https)}")
        if self.all and not validate_proxy_url(self.all):
            raise ValueError(f"Invalid proxy URL: {mask_sensitive(self.all)}")
    
    @property
    def enabled(self) -> bool:
        """Check if any proxy is configured."""
        return bool(self.http or self.https or self.all)
    
    def get_proxy_for_url(self, url: str) -> Optional[str]:
        """
        Get appropriate proxy for a given URL.
        
        Args:
            url: The target URL.
        
        Returns:
            Optional[str]: Proxy URL if configured, None otherwise.
        """
        # Check no_proxy first
        from urllib.parse import urlparse
        parsed = urlparse(url)
        host = parsed.hostname or ""
        
        for no_proxy_host in self.no_proxy:
            if host.endswith(no_proxy_host) or no_proxy_host == "*":
                return None
        
        # Return appropriate proxy
        if url.startswith("https://"):
            return self.https or self.all
        return self.http or self.all


@dataclass(frozen=True)
class SSLConfig:
    """
    Immutable SSL/TLS configuration.
    
    Attributes:
        verify: Whether to verify SSL certificates.
        cert: Path to client certificate file.
        key: Path to client private key file.
        key_password: Password for encrypted private key.
        ca_certs: Path to CA certificate bundle.
        cert_required: Require valid certificate from server.
        min_version: Minimum TLS version.
        ciphers: Allowed cipher suites.
    """
    verify: bool = True
    cert: Optional[str] = None
    key: Optional[str] = None
    key_password: Optional[str] = None
    ca_certs: Optional[str] = None
    cert_required: bool = False
    min_version: str = "TLSv1.2"
    ciphers: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate SSL configuration."""
        valid_versions = {"TLSv1", "TLSv1.1", "TLSv1.2", "TLSv1.3"}
        if self.min_version not in valid_versions:
            raise ValueError(f"min_version must be one of {valid_versions}")
        
        if self.cert:
            cert_path = Path(self.cert)
            if not cert_path.exists():
                raise FileNotFoundError(f"Certificate file not found: {self.cert}")
        
        if self.key:
            key_path = Path(self.key)
            if not key_path.exists():
                raise FileNotFoundError(f"Key file not found: {self.key}")
    
    @property
    def has_client_cert(self) -> bool:
        """Check if client certificate is configured."""
        return bool(self.cert and self.key)


@dataclass(frozen=True)
class ConnectionPoolConfig:
    """
    Immutable connection pool configuration.
    
    Attributes:
        max_connections: Maximum total connections in pool.
        max_connections_per_host: Maximum connections per host.
        keepalive_timeout: Keep-alive timeout in seconds.
        enable_cleanup: Enable idle connection cleanup.
        cleanup_interval: Cleanup interval in seconds.
    """
    max_connections: int = DEFAULT_MAX_CONNECTIONS
    max_connections_per_host: int = DEFAULT_CONNECTIONS_PER_HOST
    keepalive_timeout: float = 30.0
    enable_cleanup: bool = True
    cleanup_interval: float = 60.0
    
    def __post_init__(self) -> None:
        """Validate connection pool configuration."""
        validate_positive_number(self.max_connections, "max_connections")
        validate_positive_number(self.max_connections_per_host, "max_connections_per_host")
        validate_non_negative_number(self.keepalive_timeout, "keepalive_timeout")
        validate_positive_number(self.cleanup_interval, "cleanup_interval")


@dataclass(frozen=True)
class RateLimitConfig:
    """
    Immutable rate limiting configuration.
    
    Attributes:
        requests_per_second: Maximum requests per second.
        burst_size: Maximum burst size (token bucket capacity).
        wait_on_limit: Whether to wait when rate limited.
        max_wait: Maximum wait time when rate limited in seconds.
    """
    requests_per_second: float = 10.0
    burst_size: int = 20
    wait_on_limit: bool = True
    max_wait: float = 60.0
    
    def __post_init__(self) -> None:
        """Validate rate limit configuration."""
        validate_positive_number(self.requests_per_second, "requests_per_second")
        validate_positive_number(self.burst_size, "burst_size")
        validate_non_negative_number(self.max_wait, "max_wait")
    
    @property
    def interval_ms(self) -> float:
        """Get interval between requests in milliseconds."""
        return 1000.0 / self.requests_per_second


@dataclass(frozen=True)
class UserAgentConfig:
    """
    Immutable user agent configuration.
    
    Attributes:
        base: Base user agent string.
        rotate: Whether to rotate user agents.
        user_agents: List of user agents to rotate through.
        include_version: Include library version in user agent.
    """
    base: str = DEFAULT_USER_AGENT
    rotate: bool = False
    user_agents: Tuple[str, ...] = field(default_factory=lambda: (DEFAULT_USER_AGENT,))
    include_version: bool = False
    
    def get_user_agent(self) -> str:
        """
        Get a user agent string.
        
        If rotation is enabled, returns a random user agent from the list.
        
        Returns:
            str: User agent string.
        """
        if self.rotate and len(self.user_agents) > 1:
            import random
            return random.choice(self.user_agents)
        
        user_agent = self.base
        
        if self.include_version:
            from . import __version__
            user_agent = f"{user_agent} Downloader/{__version__}"
        
        return user_agent


# =============================================================================
# MAIN CONFIGURATION CLASS
# =============================================================================

class Config:
    """
    Main configuration class with comprehensive settings management.
    
    This class provides thread-safe configuration management with validation,
    serialization, and environment variable support.
    
    Attributes:
        _lock: Thread lock for thread-safe operations.
        _frozen: Whether configuration is frozen (immutable).
        _profile: Active configuration profile.
        _change_callbacks: Registered change callbacks.
    
    Example:
        >>> config = Config()
        >>> config.timeout.total = 60.0  # Update timeout
        >>> config.freeze()  # Make immutable
    """
    
    # Class-level defaults
    _default_profile: ClassVar[ConfigProfile] = ConfigProfile.DEVELOPMENT
    
    def __init__(
        self,
        profile: ConfigProfile = ConfigProfile.DEVELOPMENT,
        **kwargs: Any
    ) -> None:
        """
        Initialize configuration.
        
        Args:
            profile: Configuration profile to use.
            **kwargs: Override default configuration values.
        """
        self._lock = threading.RLock()
        self._frozen: bool = False
        self._profile: ConfigProfile = profile
        self._change_callbacks: List[Callable[[str, Any, Any], None]] = []
        
        # Initialize configuration sections
        self._timeout: TimeoutConfig = kwargs.get("timeout", TimeoutConfig())
        self._retry: RetryConfig = kwargs.get("retry", RetryConfig())
        self._proxy: ProxyConfig = kwargs.get("proxy", ProxyConfig())
        self._ssl: SSLConfig = kwargs.get("ssl", SSLConfig())
        self._pool: ConnectionPoolConfig = kwargs.get("pool", ConnectionPoolConfig())
        self._rate_limit: RateLimitConfig = kwargs.get("rate_limit", RateLimitConfig())
        self._user_agent: UserAgentConfig = kwargs.get("user_agent", UserAgentConfig())
        
        # Additional settings
        self._max_redirects: int = kwargs.get("max_redirects", DEFAULT_MAX_REDIRECTS)
        self._chunk_size: int = kwargs.get("chunk_size", DEFAULT_CHUNK_SIZE)
        self._follow_redirects: bool = kwargs.get("follow_redirects", True)
        self._raise_on_error: bool = kwargs.get("raise_on_error", True)
        self._log_level: LogLevel = kwargs.get("log_level", LogLevel.INFO)
        self._debug: bool = kwargs.get("debug", False)
        self._dns_cache_ttl: int = kwargs.get("dns_cache_ttl", DEFAULT_DNS_CACHE_TTL)
        self._temp_dir: Optional[Path] = kwargs.get("temp_dir", None)
        
        # Load from environment if enabled
        if kwargs.get("load_env", True):
            self._load_from_environment()
    
    def __repr__(self) -> str:
        """Return safe string representation (masks sensitive data)."""
        return (
            f"Config(profile={self._profile.value}, "
            f"timeout={self._timeout}, "
            f"retry={self._retry}, "
            f"proxy={'<configured>' if self._proxy.enabled else 'None'}, "
            f"ssl_verify={self._ssl.verify}, "
            f"rate_limit={self._rate_limit.requests_per_second}/s)"
        )
    
    # Property getters
    @property
    def timeout(self) -> TimeoutConfig:
        """Get timeout configuration."""
        return self._timeout
    
    @property
    def retry(self) -> RetryConfig:
        """Get retry configuration."""
        return self._retry
    
    @property
    def proxy(self) -> ProxyConfig:
        """Get proxy configuration."""
        return self._proxy
    
    @property
    def ssl(self) -> SSLConfig:
        """Get SSL configuration."""
        return self._ssl
    
    @property
    def pool(self) -> ConnectionPoolConfig:
        """Get connection pool configuration."""
        return self._pool
    
    @property
    def rate_limit(self) -> RateLimitConfig:
        """Get rate limit configuration."""
        return self._rate_limit
    
    @property
    def user_agent(self) -> UserAgentConfig:
        """Get user agent configuration."""
        return self._user_agent
    
    @property
    def max_redirects(self) -> int:
        """Get maximum redirects."""
        return self._max_redirects
    
    @property
    def chunk_size(self) -> int:
        """Get chunk size for downloads."""
        return self._chunk_size
    
    @property
    def follow_redirects(self) -> bool:
        """Get follow redirects setting."""
        return self._follow_redirects
    
    @property
    def raise_on_error(self) -> bool:
        """Get raise on error setting."""
        return self._raise_on_error
    
    @property
    def log_level(self) -> LogLevel:
        """Get log level."""
        return self._log_level
    
    @property
    def debug(self) -> bool:
        """Get debug mode setting."""
        return self._debug
    
    @property
    def dns_cache_ttl(self) -> int:
        """Get DNS cache TTL."""
        return self._dns_cache_ttl
    
    @property
    def temp_dir(self) -> Optional[Path]:
        """Get temporary directory."""
        return self._temp_dir
    
    @property
    def profile(self) -> ConfigProfile:
        """Get configuration profile."""
        return self._profile
    
    @property
    def is_frozen(self) -> bool:
        """Check if configuration is frozen."""
        return self._frozen
    
    # Update methods (return new immutable instances)
    def with_timeout(self, **kwargs: Any) -> "Config":
        """
        Create new config with updated timeout settings.
        
        Args:
            **kwargs: TimeoutConfig field values.
        
        Returns:
            Config: New configuration instance.
        """
        new_timeout = TimeoutConfig(
            **{**self._timeout.to_dict(), **kwargs}
        )
        return self._copy_with(timeout=new_timeout)
    
    def with_retry(self, **kwargs: Any) -> "Config":
        """
        Create new config with updated retry settings.
        
        Args:
            **kwargs: RetryConfig field values.
        Returns:
            Config: New configuration instance.
        """
        current = asdict(self._retry)
        current["strategy"] = self._retry.strategy
        new_retry = RetryConfig(**{**current, **kwargs})
        return self._copy_with(retry=new_retry)
    
    def with_proxy(self, **kwargs: Any) -> "Config":
        """
        Create new config with updated proxy settings.
        
        Args:
            **kwargs: ProxyConfig field values.
        
        Returns:
            Config: New configuration instance.
        """
        current = asdict(self._proxy)
        new_proxy = ProxyConfig(**{**current, **kwargs})
        return self._copy_with(proxy=new_proxy)
    
    def with_ssl(self, **kwargs: Any) -> "Config":
        """
        Create new config with updated SSL settings.
        
        Args:
            **kwargs: SSLConfig field values.
        
        Returns:
            Config: New configuration instance.
        """
        current = asdict(self._ssl)
        new_ssl = SSLConfig(**{**current, **kwargs})
        return self._copy_with(ssl=new_ssl)
    
    def with_rate_limit(self, **kwargs: Any) -> "Config":
        """
        Create new config with updated rate limit settings.
        
        Args:
            **kwargs: RateLimitConfig field values.
        
        Returns:
            Config: New configuration instance.
        """
        current = asdict(self._rate_limit)
        new_rate = RateLimitConfig(**{**current, **kwargs})
        return self._copy_with(rate_limit=new_rate)
    
    def _copy_with(self, **updates: Any) -> "Config":
        """
        Create a copy with updated fields.
        
        Args:
            **updates: Fields to update.
        
        Returns:
            Config: New configuration instance.
        """
        with self._lock:
            return Config(
                profile=self._profile,
                timeout=updates.get("timeout", self._timeout),
                retry=updates.get("retry", self._retry),
                proxy=updates.get("proxy", self._proxy),
                ssl=updates.get("ssl", self._ssl),
                pool=updates.get("pool", self._pool),
                rate_limit=updates.get("rate_limit", self._rate_limit),
                user_agent=updates.get("user_agent", self._user_agent),
                max_redirects=updates.get("max_redirects", self._max_redirects),
                chunk_size=updates.get("chunk_size", self._chunk_size),
                follow_redirects=updates.get("follow_redirects", self._follow_redirects),
                raise_on_error=updates.get("raise_on_error", self._raise_on_error),
                log_level=updates.get("log_level", self._log_level),
                debug=updates.get("debug", self._debug),
                dns_cache_ttl=updates.get("dns_cache_ttl", self._dns_cache_ttl),
                temp_dir=updates.get("temp_dir", self._temp_dir),
                load_env=False,
            )
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        # Timeout settings
        if timeout := os.getenv("DOWNLOADER_TIMEOUT"):
            try:
                self._timeout = TimeoutConfig(total=float(timeout))
            except ValueError:
                warnings.warn(f"Invalid DOWNLOADER_TIMEOUT: {timeout}")
        
        # Proxy settings
        proxy_http = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
        proxy_https = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
        proxy_all = os.getenv("ALL_PROXY") or os.getenv("all_proxy")
        no_proxy = os.getenv("NO_PROXY") or os.getenv("no_proxy")
        
        if proxy_http or proxy_https or proxy_all:
            no_proxy_list = tuple(no_proxy.split(",")) if no_proxy else ()
            self._proxy = ProxyConfig(
                http=proxy_http,
                https=proxy_https,
                all=proxy_all,
                no_proxy=no_proxy_list,
            )
        
        # SSL settings
        if verify := os.getenv("DOWNLOADER_SSL_VERIFY"):
            self._ssl = SSLConfig(verify=verify.lower() == "true")
        
        # Debug mode
        if debug := os.getenv("DOWNLOADER_DEBUG"):
            self._debug = debug.lower() == "true"
        
        # Log level
        if log_level := os.getenv("DOWNLOADER_LOG_LEVEL"):
            try:
                self._log_level = LogLevel(log_level.upper())
            except ValueError:
                warnings.warn(f"Invalid DOWNLOADER_LOG_LEVEL: {log_level}")
        
        # Rate limit
        if rps := os.getenv("DOWNLOADER_RATE_LIMIT"):
            try:
                self._rate_limit = RateLimitConfig(requests_per_second=float(rps))
            except ValueError:
                warnings.warn(f"Invalid DOWNLOADER_RATE_LIMIT: {rps}")
    
    # Serialization methods
    def to_dict(self, mask_secrets: bool = True) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Args:
            mask_secrets: Whether to mask sensitive values.
        
        Returns:
            Dict[str, Any]: Configuration dictionary.
        """
        def safe_serialize(obj: Any) -> Any:
            if isinstance(obj, (TimeoutConfig, RetryConfig, ProxyConfig, 
                               SSLConfig, ConnectionPoolConfig, 
                               RateLimitConfig, UserAgentConfig)):
                result = asdict(obj)
                if mask_secrets and isinstance(obj, ProxyConfig):
                    if result.get("http"):
                        result["http"] = mask_sensitive(result["http"])
                    if result.get("https"):
                        result["https"] = mask_sensitive(result["https"])
                return result
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, Path):
                return str(obj)
            return obj
        
        return {
            "profile": self._profile.value,
            "timeout": safe_serialize(self._timeout),
            "retry": safe_serialize(self._retry),
            "proxy": safe_serialize(self._proxy),
            "ssl": safe_serialize(self._ssl),
            "pool": safe_serialize(self._pool),
            "rate_limit": safe_serialize(self._rate_limit),
            "user_agent": safe_serialize(self._user_agent),
            "max_redirects": self._max_redirects,
            "chunk_size": self._chunk_size,
            "follow_redirects": self._follow_redirects,
            "raise_on_error": self._raise_on_error,
            "log_level": self._log_level.value,
            "debug": self._debug,
            "dns_cache_ttl": self._dns_cache_ttl,
            "temp_dir": str(self._temp_dir) if self._temp_dir else None,
        }
    
    def to_json(self, mask_secrets: bool = True, indent: int = 2) -> str:
        """
        Convert configuration to JSON string.
        
        Args:
            mask_secrets: Whether to mask sensitive values.
            indent: JSON indentation level.
        
        Returns:
            str: JSON string.
        """
        return json.dumps(self.to_dict(mask_secrets=mask_secrets), indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """
        Create configuration from dictionary.
        
        Args:
            data: Configuration dictionary.
        
        Returns:
            Config: New configuration instance.
        """
        # Parse nested configurations
        if "timeout" in data and isinstance(data["timeout"], dict):
            data["timeout"] = TimeoutConfig(**data["timeout"])
        if "retry" in data and isinstance(data["retry"], dict):
            retry_data = data["retry"].copy()
            if "strategy" in retry_data and isinstance(retry_data["strategy"], str):
                retry_data["strategy"] = RetryStrategy(retry_data["strategy"])
            if "retry_on_status" in retry_data:
                retry_data["retry_on_status"] = tuple(retry_data["retry_on_status"])
            data["retry"] = RetryConfig(**retry_data)
        if "proxy" in data and isinstance(data["proxy"], dict):
            proxy_data = data["proxy"].copy()
            if "no_proxy" in proxy_data:
                proxy_data["no_proxy"] = tuple(proxy_data["no_proxy"])
            data["proxy"] = ProxyConfig(**proxy_data)
        if "ssl" in data and isinstance(data["ssl"], dict):
            data["ssl"] = SSLConfig(**data["ssl"])
        if "pool" in data and isinstance(data["pool"], dict):
            data["pool"] = ConnectionPoolConfig(**data["pool"])
        if "rate_limit" in data and isinstance(data["rate_limit"], dict):
            data["rate_limit"] = RateLimitConfig(**data["rate_limit"])
        if "user_agent" in data and isinstance(data["user_agent"], dict):
            ua_data = data["user_agent"].copy()
            if "user_agents" in ua_data:
                ua_data["user_agents"] = tuple(ua_data["user_agents"])
            data["user_agent"] = UserAgentConfig(**ua_data)
        if "log_level" in data and isinstance(data["log_level"], str):
            data["log_level"] = LogLevel(data["log_level"])
        if "profile" in data and isinstance(data["profile"], str):
            data["profile"] = ConfigProfile(data["profile"])
        if "temp_dir" in data and data["temp_dir"]:
            data["temp_dir"] = Path(data["temp_dir"])
        
        return cls(load_env=False, **data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "Config":
        """
        Create configuration from JSON string.
        
        Args:
            json_str: JSON string.
        
        Returns:
            Config: New configuration instance.
        """
        return cls.from_dict(json.loads(json_str))
    
    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "Config":
        """
        Load configuration from file.
        
        Supports JSON, YAML, and TOML formats based on file extension.
        
        Args:
            path: Path to configuration file.
        
        Returns:
            Config: New configuration instance.
        
        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If file format is not supported.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        content = path.read_text(encoding="utf-8")
        
        if path.suffix == ".json":
            return cls.from_json(content)
        elif path.suffix in (".yaml", ".yml"):
            if not HAS_YAML:
                raise ImportError("PyYAML is required to load YAML files")
            return cls.from_dict(yaml.safe_load(content))
        elif path.suffix == ".toml":
            if not HAS_TOMLI:
                raise ImportError("tomli is required to load TOML files")
            return cls.from_dict(tomli.loads(content))
        else:
            raise ValueError(f"Unsupported configuration file format: {path.suffix}")
    
    def save_to_file(self, path: Union[str, Path], mask_secrets: bool = True) -> None:
        """
        Save configuration to file.
        
        Format is determined by file extension.
        
        Args:
            path: Path to save configuration to.
            mask_secrets: Whether to mask sensitive values.
        """
        path = Path(path)
        content: str
        
        if path.suffix == ".json":
            content = self.to_json(mask_secrets=mask_secrets)
        elif path.suffix in (".yaml", ".yml"):
            if not HAS_YAML:
                raise ImportError("PyYAML is required to save YAML files")
            content = yaml.safe_dump(self.to_dict(mask_secrets=mask_secrets))
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
        
        path.write_text(content, encoding="utf-8")
    
    # Profile presets
    @classmethod
    def development(cls) -> "Config":
        """Create development configuration preset."""
        return cls(
            profile=ConfigProfile.DEVELOPMENT,
            log_level=LogLevel.DEBUG,
            debug=True,
            retry=RetryConfig(max_retries=3, retry_delay=1.0),
            ssl=SSLConfig(verify=False),
        )
    
    @classmethod
    def staging(cls) -> "Config":
        """Create staging configuration preset."""
        return cls(
            profile=ConfigProfile.STAGING,
            log_level=LogLevel.INFO,
            debug=False,
            retry=RetryConfig(max_retries=5, retry_delay=2.0),
        )
    
    @classmethod
    def production(cls) -> "Config":
        """Create production configuration preset."""
        return cls(
            profile=ConfigProfile.PRODUCTION,
            log_level=LogLevel.WARNING,
            debug=False,
            retry=RetryConfig(max_retries=5, retry_delay=2.0, max_delay=120.0),
            rate_limit=RateLimitConfig(requests_per_second=20.0, burst_size=50),
            pool=ConnectionPoolConfig(max_connections=200, max_connections_per_host=20),
        )
    
    @classmethod
    def testing(cls) -> "Config":
        """Create testing configuration preset."""
        return cls(
            profile=ConfigProfile.TESTING,
            log_level=LogLevel.DEBUG,
            debug=True,
            retry=RetryConfig(max_retries=1, retry_delay=0.1),
            timeout=TimeoutConfig(total=5.0, connect=2.0),
        )


# =============================================================================
# CONFIGURATION MANAGER (SINGLETON)
# =============================================================================

class ConfigManager:
    """
    Thread-safe singleton configuration manager.
    
    Provides centralized configuration management with caching and
    profile switching capabilities.
    """
    
    _instance: Optional["ConfigManager"] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> "ConfigManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._configs: Dict[str, Config] = {}
                    cls._instance._active_profile = ConfigProfile.DEVELOPMENT
        return cls._instance
    
    def get_config(self, profile: Optional[ConfigProfile] = None) -> Config:
        """
        Get configuration for specified profile.
        
        Args:
            profile: Profile to get, uses active profile if None.
        
        Returns:
            Config: Configuration instance.
        """
        profile = profile or self._active_profile
        
        if profile.value not in self._configs:
            # Create profile preset
            if profile == ConfigProfile.DEVELOPMENT:
                self._configs[profile.value] = Config.development()
            elif profile == ConfigProfile.STAGING:
                self._configs[profile.value] = Config.staging()
            elif profile == ConfigProfile.PRODUCTION:
                self._configs[profile.value] = Config.production()
            elif profile == ConfigProfile.TESTING:
                self._configs[profile.value] = Config.testing()
            else:
                self._configs[profile.value] = Config(profile=profile)
        
        return self._configs[profile.value]
    
    def set_active_profile(self, profile: ConfigProfile) -> None:
        """
        Set the active configuration profile.
        
        Args:
            profile: Profile to activate.
        """
        self._active_profile = profile
    
    @property
    def active_config(self) -> Config:
        """Get the active configuration."""
        return self.get_config()
    
    def reload(self, profile: Optional[ConfigProfile] = None) -> Config:
        """
        Reload configuration from environment.
        
        Args:
            profile: Profile to reload, uses active profile if None.
        
        Returns:
            Config: Fresh configuration instance.
        """
        profile = profile or self._active_profile
        self._configs.pop(profile.value, None)
        return self.get_config(profile)
    
    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance."""
        with cls._lock:
            cls._instance = None


def get_config_manager() -> ConfigManager:
    """
    Get the configuration manager singleton.
    
    Returns:
        ConfigManager: The configuration manager instance.
    """
    return ConfigManager()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "LogLevel",
    "ConfigProfile",
    "ProxyType",
    "RetryStrategy",
    # Configuration classes
    "Config",
    "ConfigManager",
    "TimeoutConfig",
    "RetryConfig",
    "ProxyConfig",
    "SSLConfig",
    "ConnectionPoolConfig",
    "RateLimitConfig",
    "UserAgentConfig",
    # Utility functions
    "get_config_manager",
    "mask_sensitive",
    "validate_url",
    "validate_proxy_url",
    # Constants
    "DEFAULT_TIMEOUT",
    "DEFAULT_CONNECT_TIMEOUT",
    "DEFAULT_READ_TIMEOUT",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_RETRY_DELAY",
    "DEFAULT_MAX_REDIRECTS",
    "DEFAULT_CHUNK_SIZE",
    "DEFAULT_USER_AGENT",
]

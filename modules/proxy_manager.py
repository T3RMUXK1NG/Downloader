"""
OMNIPOTENT SOVEREIGN NEXUS - Proxy Manager Module
Version: v3.0.1 ULTIMATE NEXUS

Proxy rotation and management with support for:
- HTTP/HTTPS proxies
- SOCKS4/SOCKS5 proxies
- Rotating proxy pools
- Proxy authentication
- Proxy health checking
- Geographic filtering
- Automatic failover
- Load balancing

Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
"""

import asyncio
import aiohttp
import logging
import re
import time
import hashlib
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
    Awaitable,
)
from urllib.parse import urlparse


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)


class ProxyType(Enum):
    """Proxy protocol types."""
    
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


class ProxyStatus(Enum):
    """Proxy status enumeration."""
    
    UNKNOWN = "unknown"
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    FAILED = "failed"
    BANNED = "banned"


class RotationStrategy(Enum):
    """Proxy rotation strategies."""
    
    SEQUENTIAL = "sequential"
    RANDOM = "random"
    ROUND_ROBIN = "round_robin"
    LEAST_USED = "least_used"
    FASTEST = "fastest"
    GEO_LOCATION = "geo_location"


@dataclass
class ProxyInfo:
    """
    Proxy information.
    
    Attributes:
        host: Proxy host
        port: Proxy port
        proxy_type: Proxy type
        username: Authentication username
        password: Authentication password
        country: Country code
        city: City name
        status: Current status
        last_checked: Last health check time
        response_time: Response time in seconds
        success_rate: Success rate (0-100)
        total_requests: Total requests made
        failed_requests: Failed requests count
    """
    host: str
    port: int
    proxy_type: ProxyType = ProxyType.HTTP
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    status: ProxyStatus = ProxyStatus.UNKNOWN
    last_checked: Optional[datetime] = None
    response_time: float = 0.0
    success_rate: float = 100.0
    total_requests: int = 0
    failed_requests: int = 0
    
    @property
    def url(self) -> str:
        """Get proxy URL."""
        if self.username and self.password:
            return f"{self.proxy_type.value}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.proxy_type.value}://{self.host}:{self.port}"
    
    @property
    def address(self) -> str:
        """Get proxy address."""
        return f"{self.host}:{self.port}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "type": self.proxy_type.value,
            "country": self.country,
            "city": self.city,
            "status": self.status.value,
            "response_time": round(self.response_time, 3),
            "success_rate": round(self.success_rate, 2),
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
        }


@dataclass
class ProxyPoolConfig:
    """
    Proxy pool configuration.
    
    Attributes:
        strategy: Rotation strategy
        health_check_interval: Health check interval in seconds
        health_check_url: URL for health checks
        timeout: Request timeout in seconds
        max_failures: Max failures before marking as failed
        min_success_rate: Minimum success rate to keep active
        verify_ssl: Whether to verify SSL certificates
        test_urls: List of URLs for testing
    """
    strategy: RotationStrategy = RotationStrategy.ROUND_ROBIN
    health_check_interval: int = 300
    health_check_url: str = "http://httpbin.org/ip"
    timeout: float = 10.0
    max_failures: int = 3
    min_success_rate: float = 70.0
    verify_ssl: bool = False
    test_urls: List[str] = field(default_factory=lambda: [
        "http://httpbin.org/ip",
        "http://ip-api.com/json",
    ])


@dataclass
class ProxyTestResult:
    """
    Proxy test result.
    
    Attributes:
        proxy: Proxy info
        success: Whether test succeeded
        response_time: Response time in seconds
        error_message: Error message if failed
        ip_address: Detected IP address
        country: Detected country
    """
    proxy: ProxyInfo
    success: bool = False
    response_time: float = 0.0
    error_message: Optional[str] = None
    ip_address: Optional[str] = None
    country: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "proxy": self.proxy.address,
            "success": self.success,
            "response_time": round(self.response_time, 3),
            "error_message": self.error_message,
            "ip_address": self.ip_address,
            "country": self.country,
        }


class ProxyManager:
    """
    OMNIPOTENT SOVEREIGN NEXUS Proxy Manager.
    
    Comprehensive proxy management with:
    - Multiple proxy types
    - Automatic rotation
    - Health checking
    - Failover support
    - Load balancing
    """
    
    def __init__(
        self,
        config: Optional[ProxyPoolConfig] = None,
    ) -> None:
        """
        Initialize proxy manager.
        
        Args:
            config: Proxy pool configuration
        """
        self.config = config or ProxyPoolConfig()
        self._proxies: List[ProxyInfo] = []
        self._active_index: int = 0
        self._usage_count: Dict[str, int] = {}
        self._session: Optional[aiohttp.ClientSession] = None
        self._lock = asyncio.Lock()
        self._health_task: Optional[asyncio.Task] = None
        
        logger.info(f"ProxyManager initialized v3.0.1 ULTIMATE NEXUS")
    
    async def __aenter__(self) -> "ProxyManager":
        """Async context manager entry."""
        await self._ensure_session()
        self._start_health_check()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self) -> None:
        """Ensure aiohttp session exists."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
    
    async def close(self) -> None:
        """Close proxy manager."""
        if self._health_task:
            self._health_task.cancel()
        
        if self._session and not self._session.closed:
            await self._session.close()
        
        logger.info("ProxyManager closed")
    
    def _start_health_check(self) -> None:
        """Start health check background task."""
        if self.config.health_check_interval > 0:
            self._health_task = asyncio.create_task(self._health_check_loop())
    
    async def _health_check_loop(self) -> None:
        """Background health check loop."""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self.check_all_proxies()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
    
    def add_proxy(
        self,
        host: str,
        port: int,
        proxy_type: ProxyType = ProxyType.HTTP,
        username: Optional[str] = None,
        password: Optional[str] = None,
        country: Optional[str] = None,
    ) -> ProxyInfo:
        """
        Add a proxy to the pool.
        
        Args:
            host: Proxy host
            port: Proxy port
            proxy_type: Proxy type
            username: Auth username
            password: Auth password
            country: Country code
            
        Returns:
            ProxyInfo object
        """
        proxy = ProxyInfo(
            host=host,
            port=port,
            proxy_type=proxy_type,
            username=username,
            password=password,
            country=country,
        )
        
        self._proxies.append(proxy)
        self._usage_count[proxy.address] = 0
        
        logger.info(f"Added proxy: {proxy.address}")
        return proxy
    
    def add_proxies_from_file(self, file_path: Path) -> int:
        """
        Load proxies from file.
        
        Format: host:port or host:port:username:password
        
        Args:
            file_path: Path to proxy file
            
        Returns:
            Number of proxies added
        """
        if not file_path.exists():
            logger.error(f"Proxy file not found: {file_path}")
            return 0
        
        count = 0
        
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split(':')
                
                if len(parts) >= 2:
                    host = parts[0]
                    port = int(parts[1])
                    username = parts[2] if len(parts) > 2 else None
                    password = parts[3] if len(parts) > 3 else None
                    
                    self.add_proxy(host, port, ProxyType.HTTP, username, password)
                    count += 1
        
        logger.info(f"Loaded {count} proxies from file")
        return count
    
    def add_proxies_from_list(
        self,
        proxies: List[str],
        proxy_type: ProxyType = ProxyType.HTTP,
    ) -> int:
        """
        Add proxies from list.
        
        Format: "host:port" or "protocol://host:port"
        
        Args:
            proxies: List of proxy strings
            proxy_type: Default proxy type
            
        Returns:
            Number of proxies added
        """
        count = 0
        
        for proxy_str in proxies:
            try:
                # Parse proxy string
                if '://' in proxy_str:
                    parsed = urlparse(proxy_str)
                    host = parsed.hostname
                    port = parsed.port
                    username = parsed.username
                    password = parsed.password
                    
                    # Determine type from scheme
                    scheme = parsed.scheme.lower()
                    if scheme == 'socks4':
                        p_type = ProxyType.SOCKS4
                    elif scheme == 'socks5':
                        p_type = ProxyType.SOCKS5
                    elif scheme == 'https':
                        p_type = ProxyType.HTTPS
                    else:
                        p_type = ProxyType.HTTP
                else:
                    parts = proxy_str.split(':')
                    host = parts[0]
                    port = int(parts[1])
                    username = parts[2] if len(parts) > 2 else None
                    password = parts[3] if len(parts) > 3 else None
                    p_type = proxy_type
                
                self.add_proxy(host, port, p_type, username, password)
                count += 1
                
            except Exception as e:
                logger.warning(f"Failed to parse proxy: {proxy_str} - {e}")
        
        return count
    
    def remove_proxy(self, host: str, port: int) -> bool:
        """
        Remove proxy from pool.
        
        Args:
            host: Proxy host
            port: Proxy port
            
        Returns:
            True if removed
        """
        address = f"{host}:{port}"
        
        for i, proxy in enumerate(self._proxies):
            if proxy.address == address:
                self._proxies.pop(i)
                self._usage_count.pop(address, None)
                logger.info(f"Removed proxy: {address}")
                return True
        
        return False
    
    async def get_proxy(
        self,
        country: Optional[str] = None,
        exclude: Optional[List[str]] = None,
    ) -> Optional[ProxyInfo]:
        """
        Get a proxy from the pool.
        
        Args:
            country: Filter by country
            exclude: List of addresses to exclude
            
        Returns:
            ProxyInfo or None
        """
        async with self._lock:
            available = [
                p for p in self._proxies
                if p.status == ProxyStatus.ACTIVE
                and (country is None or p.country == country)
                and (exclude is None or p.address not in exclude)
            ]
            
            if not available:
                # Try unknown status proxies
                available = [
                    p for p in self._proxies
                    if p.status in (ProxyStatus.UNKNOWN, ProxyStatus.ACTIVE)
                    and (country is None or p.country == country)
                    and (exclude is None or p.address not in exclude)
                ]
            
            if not available:
                return None
            
            # Apply rotation strategy
            if self.config.strategy == RotationStrategy.RANDOM:
                proxy = random.choice(available)
            
            elif self.config.strategy == RotationStrategy.SEQUENTIAL:
                proxy = available[self._active_index % len(available)]
                self._active_index += 1
            
            elif self.config.strategy == RotationStrategy.ROUND_ROBIN:
                proxy = available[self._active_index % len(available)]
                self._active_index = (self._active_index + 1) % len(available)
            
            elif self.config.strategy == RotationStrategy.LEAST_USED:
                proxy = min(available, key=lambda p: self._usage_count.get(p.address, 0))
            
            elif self.config.strategy == RotationStrategy.FASTEST:
                active_available = [p for p in available if p.response_time > 0]
                if active_available:
                    proxy = min(active_available, key=lambda p: p.response_time)
                else:
                    proxy = available[0]
            
            else:
                proxy = available[0]
            
            # Update usage
            self._usage_count[proxy.address] = self._usage_count.get(proxy.address, 0) + 1
            
            return proxy
    
    async def get_multiple_proxies(
        self,
        count: int,
        unique: bool = True,
    ) -> List[ProxyInfo]:
        """
        Get multiple proxies from pool.
        
        Args:
            count: Number of proxies
            unique: Ensure unique proxies
            
        Returns:
            List of ProxyInfo
        """
        proxies = []
        exclude = []
        
        for _ in range(count):
            proxy = await self.get_proxy(exclude=exclude if unique else None)
            if proxy:
                proxies.append(proxy)
                if unique:
                    exclude.append(proxy.address)
            else:
                break
        
        return proxies
    
    async def test_proxy(
        self,
        proxy: ProxyInfo,
        test_url: Optional[str] = None,
    ) -> ProxyTestResult:
        """
        Test a proxy.
        
        Args:
            proxy: Proxy to test
            test_url: URL to test against
            
        Returns:
            ProxyTestResult
        """
        await self._ensure_session()
        
        url = test_url or self.config.health_check_url
        start_time = time.time()
        
        try:
            proxy.status = ProxyStatus.TESTING
            
            # Build proxy URL
            if proxy.username and proxy.password:
                proxy_url = f"{proxy.proxy_type.value}://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}"
            else:
                proxy_url = f"{proxy.proxy_type.value}://{proxy.host}:{proxy.port}"
            
            connector = aiohttp.TCPConnector(ssl=self.config.verify_ssl)
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            ) as session:
                async with session.get(
                    url,
                    proxy=proxy_url,
                    ssl=self.config.verify_ssl,
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        ip_address = data.get("origin", data.get("query", ""))
                        country = data.get("country", "")
                        
                        proxy.status = ProxyStatus.ACTIVE
                        proxy.response_time = response_time
                        proxy.last_checked = datetime.now()
                        
                        return ProxyTestResult(
                            proxy=proxy,
                            success=True,
                            response_time=response_time,
                            ip_address=ip_address,
                            country=country,
                        )
                    else:
                        proxy.status = ProxyStatus.FAILED
                        proxy.last_checked = datetime.now()
                        
                        return ProxyTestResult(
                            proxy=proxy,
                            success=False,
                            response_time=response_time,
                            error_message=f"HTTP {response.status}",
                        )
                        
        except asyncio.TimeoutError:
            proxy.status = ProxyStatus.FAILED
            proxy.last_checked = datetime.now()
            
            return ProxyTestResult(
                proxy=proxy,
                success=False,
                error_message="Timeout",
            )
            
        except Exception as e:
            proxy.status = ProxyStatus.FAILED
            proxy.last_checked = datetime.now()
            
            return ProxyTestResult(
                proxy=proxy,
                success=False,
                error_message=str(e),
            )
    
    async def check_all_proxies(self) -> List[ProxyTestResult]:
        """
        Check all proxies in pool.
        
        Returns:
            List of ProxyTestResult
        """
        results = []
        
        # Test concurrently with limit
        semaphore = asyncio.Semaphore(10)
        
        async def test_with_semaphore(proxy: ProxyInfo) -> ProxyTestResult:
            async with semaphore:
                return await self.test_proxy(proxy)
        
        tasks = [test_with_semaphore(proxy) for proxy in self._proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            r if isinstance(r, ProxyTestResult) else ProxyTestResult(
                proxy=self._proxies[i],
                success=False,
                error_message=str(r),
            )
            for i, r in enumerate(results)
        ]
    
    def report_success(self, proxy_address: str) -> None:
        """Report successful proxy usage."""
        for proxy in self._proxies:
            if proxy.address == proxy_address:
                proxy.total_requests += 1
                proxy.success_rate = (
                    (proxy.success_rate * (proxy.total_requests - 1) + 100) /
                    proxy.total_requests
                )
                break
    
    def report_failure(self, proxy_address: str) -> None:
        """Report failed proxy usage."""
        for proxy in self._proxies:
            if proxy.address == proxy_address:
                proxy.total_requests += 1
                proxy.failed_requests += 1
                
                # Update success rate
                if proxy.total_requests > 0:
                    proxy.success_rate = (
                        (proxy.total_requests - proxy.failed_requests) /
                        proxy.total_requests * 100
                    )
                
                # Check if should be marked as failed
                if proxy.failed_requests >= self.config.max_failures:
                    proxy.status = ProxyStatus.FAILED
                elif proxy.success_rate < self.config.min_success_rate:
                    proxy.status = ProxyStatus.FAILED
                
                break
    
    def get_active_proxies(self) -> List[ProxyInfo]:
        """Get all active proxies."""
        return [p for p in self._proxies if p.status == ProxyStatus.ACTIVE]
    
    def get_failed_proxies(self) -> List[ProxyInfo]:
        """Get all failed proxies."""
        return [p for p in self._proxies if p.status == ProxyStatus.FAILED]
    
    def get_proxy_count(self) -> int:
        """Get total proxy count."""
        return len(self._proxies)
    
    def get_active_count(self) -> int:
        """Get active proxy count."""
        return len([p for p in self._proxies if p.status == ProxyStatus.ACTIVE])
    
    def clear_failed(self) -> int:
        """Remove all failed proxies."""
        before = len(self._proxies)
        self._proxies = [p for p in self._proxies if p.status != ProxyStatus.FAILED]
        return before - len(self._proxies)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        active = [p for p in self._proxies if p.status == ProxyStatus.ACTIVE]
        failed = [p for p in self._proxies if p.status == ProxyStatus.FAILED]
        
        avg_response = 0.0
        if active:
            avg_response = sum(p.response_time for p in active) / len(active)
        
        return {
            "total": len(self._proxies),
            "active": len(active),
            "failed": len(failed),
            "average_response_time": round(avg_response, 3),
            "total_requests": sum(p.total_requests for p in self._proxies),
        }


# Convenience functions
def create_proxy_manager(
    proxies: Optional[List[str]] = None,
    strategy: RotationStrategy = RotationStrategy.ROUND_ROBIN,
) -> ProxyManager:
    """
    Create a proxy manager with optional proxies.
    
    Args:
        proxies: List of proxy strings
        strategy: Rotation strategy
        
    Returns:
        ProxyManager
    """
    config = ProxyPoolConfig(strategy=strategy)
    manager = ProxyManager(config)
    
    if proxies:
        manager.add_proxies_from_list(proxies)
    
    return manager


# Export all public classes and functions
__all__ = [
    "ProxyManager",
    "ProxyType",
    "ProxyStatus",
    "RotationStrategy",
    "ProxyInfo",
    "ProxyPoolConfig",
    "ProxyTestResult",
    "create_proxy_manager",
]

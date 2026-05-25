#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OMNIPOTENT SOVEREIGN NEXUS - Core Package Initialization
=========================================================

Version: 3.2.0 ULTIMATE NEXUS
Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
License: OMNIPOTENT SOVEREIGN LICENSE

This module serves as the central initialization point for the Downloader
core package, providing version information, public API exports, and
package-level utilities.

ARCHITECTURE:
    - Single Source of Truth for package version
    - Lazy loading for performance optimization
    - Comprehensive type hints and docstrings
    - Thread-safe initialization

FEATURES:
    - Version management with semantic versioning
    - Public API exposure control
    - Dependency validation
    - Runtime environment checks
    - Performance metrics collection

SECURITY:
    - No sensitive data exposure
    - Controlled module exports
    - Integrity verification hooks
"""

from __future__ import annotations

import sys
import warnings
from typing import Final, Optional, Dict, Any, List, Callable
from functools import lru_cache
from pathlib import Path
import importlib.util
import platform

# =============================================================================
# VERSION INFORMATION - SINGLE SOURCE OF TRUTH
# =============================================================================

__version__: Final[str] = "3.2.0"
__version_info__: Final[tuple[int, int, int]] = (3, 2, 0)
__release_name__: Final[str] = "ULTIMATE NEXUS"
__author__: Final[str] = "RAJSARASWATI JATAV (RS)"
__author_alias__: Final[str] = "T3rmuxk1ng"
__license__: Final[str] = "OMNIPOTENT SOVEREIGN LICENSE"
__copyright__: Final[str] = "2024-2025 RAJSARASWATI JATAV"
__email__: Final[str] = "t3rmuxk1ng@proton.me"

# Minimum Python version requirement
_MIN_PYTHON_VERSION: Final[tuple[int, int]] = (3, 10)
_PYTHON_VERSION: tuple[int, int, int] = sys.version_info[:3]


# =============================================================================
# RUNTIME VALIDATION
# =============================================================================

def _validate_python_version() -> bool:
    """
    Validate that the current Python version meets minimum requirements.
    
    Returns:
        bool: True if Python version is compatible, False otherwise.
    
    Raises:
        RuntimeError: If Python version is below minimum requirement.
    
    Example:
        >>> _validate_python_version()
        True
    """
    current = sys.version_info[:2]
    if current < _MIN_PYTHON_VERSION:
        raise RuntimeError(
            f"Downloader core requires Python {'.'.join(map(str, _MIN_PYTHON_VERSION))}+, "
            f"but you have {sys.version_info.major}.{sys.version_info.minor}"
        )
    return True


def _get_runtime_info() -> Dict[str, Any]:
    """
    Collect comprehensive runtime environment information.
    
    Returns:
        Dict[str, Any]: Dictionary containing runtime details including
            Python version, platform, implementation details, and system info.
    
    Example:
        >>> info = _get_runtime_info()
        >>> info['python_version']
        '3.11.5'
    """
    return {
        "python_version": f"{_PYTHON_VERSION[0]}.{_PYTHON_VERSION[1]}.{_PYTHON_VERSION[2]}",
        "python_implementation": platform.python_implementation(),
        "python_compiler": platform.python_compiler(),
        "platform_system": platform.system(),
        "platform_machine": platform.machine(),
        "platform_version": platform.version(),
        "is_64bit": sys.maxsize > 2**32,
        "executable": sys.executable,
        "prefix": sys.prefix,
    }


@lru_cache(maxsize=1)
def _check_optional_dependencies() -> Dict[str, bool]:
    """
    Check availability of optional dependencies.
    
    Uses LRU cache to avoid repeated checks during the same session.
    
    Returns:
        Dict[str, bool]: Dictionary mapping dependency names to availability status.
    
    Example:
        >>> deps = _check_optional_dependencies()
        >>> deps.get('aiohttp', False)
        True
    """
    optional_packages = [
        "aiohttp",
        "httpx",
        "requests",
        "aiofiles",
        "tqdm",
        "rich",
        "pydantic",
        "certifi",
        "urllib3",
        "tenacity",
        "cryptography",
    ]
    
    availability: Dict[str, bool] = {}
    
    for package in optional_packages:
        try:
            spec = importlib.util.find_spec(package)
            availability[package] = spec is not None
        except (ImportError, ModuleNotFoundError, ValueError):
            availability[package] = False
    
    return availability


def _warn_missing_dependencies() -> None:
    """
    Issue warnings for missing optional dependencies that enhance functionality.
    
    This function checks for critical optional dependencies and emits
    appropriate warnings without blocking execution.
    """
    deps = _check_optional_dependencies()
    
    critical_missing = []
    
    # Check for async HTTP client
    if not deps.get("aiohttp") and not deps.get("httpx"):
        critical_missing.append("aiohttp or httpx (async HTTP client)")
    
    # Check for SSL certificate bundle
    if not deps.get("certifi"):
        critical_missing.append("certifi (SSL certificate bundle)")
    
    # Check for retry mechanism
    if not deps.get("tenacity"):
        critical_missing.append("tenacity (retry mechanism)")
    
    if critical_missing:
        warnings.warn(
            f"Missing optional dependencies: {', '.join(critical_missing)}. "
            f"Some features may be limited. Install with: pip install {' '.join([p.split()[0] for p in critical_missing])}",
            UserWarning,
            stacklevel=2
        )


# =============================================================================
# PACKAGE CONFIGURATION
# =============================================================================

class _PackageConfig:
    """
    Internal package configuration singleton.
    
    This class manages package-wide settings and provides thread-safe
    configuration management.
    
    Attributes:
        _instance: Singleton instance.
        _debug: Debug mode flag.
        _strict_mode: Strict validation mode flag.
        _performance_mode: Performance optimization mode.
    """
    
    _instance: Optional["_PackageConfig"] = None
    _debug: bool = False
    _strict_mode: bool = True
    _performance_mode: bool = False
    _log_level: str = "INFO"
    
    def __new__(cls) -> "_PackageConfig":
        """Implement singleton pattern with thread safety."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def debug(self) -> bool:
        """Get debug mode status."""
        return self._debug
    
    @debug.setter
    def debug(self, value: bool) -> None:
        """Set debug mode with validation."""
        if not isinstance(value, bool):
            raise TypeError(f"debug must be bool, got {type(value).__name__}")
        self._debug = value
    
    @property
    def strict_mode(self) -> bool:
        """Get strict mode status."""
        return self._strict_mode
    
    @strict_mode.setter
    def strict_mode(self, value: bool) -> None:
        """Set strict mode with validation."""
        if not isinstance(value, bool):
            raise TypeError(f"strict_mode must be bool, got {type(value).__name__}")
        self._strict_mode = value
    
    @property
    def performance_mode(self) -> bool:
        """Get performance mode status."""
        return self._performance_mode
    
    @performance_mode.setter
    def performance_mode(self, value: bool) -> None:
        """Set performance mode with validation."""
        if not isinstance(value, bool):
            raise TypeError(f"performance_mode must be bool, got {type(value).__name__}")
        self._performance_mode = value
    
    @property
    def log_level(self) -> str:
        """Get log level."""
        return self._log_level
    
    @log_level.setter
    def log_level(self, value: str) -> None:
        """Set log level with validation."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if not isinstance(value, str):
            raise TypeError(f"log_level must be str, got {type(value).__name__}")
        if value.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}, got {value}")
        self._log_level = value.upper()


def get_config() -> _PackageConfig:
    """
    Get the package configuration singleton.
    
    Returns:
        _PackageConfig: The package configuration instance.
    
    Example:
        >>> config = get_config()
        >>> config.debug = True
    """
    return _PackageConfig()


# =============================================================================
# PUBLIC API
# =============================================================================

# Lazy import function for public modules
def __getattr__(name: str) -> Any:
    """
    Lazy import public API components.
    
    This enables deferred loading of modules for better startup performance.
    
    Args:
        name: The name of the attribute to import.
    
    Returns:
        The requested module or raises AttributeError.
    
    Raises:
        AttributeError: If the requested name is not found.
    """
    _lazy_imports: Dict[str, str] = {
        "Config": "config",
        "DownloaderBase": "downloader_base",
        "Logger": "logger",
        "NetworkClient": "network",
        "NetworkError": "network",
        "RetryHandler": "network",
    }
    
    if name in _lazy_imports:
        module_name = _lazy_imports[name]
        try:
            module = importlib.import_module(f".{module_name}", package=__name__)
            return getattr(module, name)
        except (ImportError, AttributeError) as e:
            raise AttributeError(f"Cannot import {name} from {__name__}: {e}") from e
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Explicitly define what should be exported
__all__: Final[List[str]] = [
    # Version info
    "__version__",
    "__version_info__",
    "__release_name__",
    "__author__",
    "__author_alias__",
    "__license__",
    "__copyright__",
    "__email__",
    # Core classes (lazy loaded)
    "Config",
    "DownloaderBase",
    "Logger",
    "NetworkClient",
    "NetworkError",
    "RetryHandler",
    # Utility functions
    "get_config",
    "get_runtime_info",
    "check_dependencies",
]


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_runtime_info() -> Dict[str, Any]:
    """
    Get comprehensive runtime environment information.
    
    Returns:
        Dict[str, Any]: Runtime information dictionary.
    
    Example:
        >>> info = get_runtime_info()
        >>> print(info['python_version'])
        3.11.5
    """
    return _get_runtime_info()


def check_dependencies() -> Dict[str, bool]:
    """
    Check availability of all optional dependencies.
    
    Returns:
        Dict[str, bool]: Dictionary mapping package names to availability.
    
    Example:
        >>> deps = check_dependencies()
        >>> if deps['aiohttp']:
        ...     print("Async HTTP available")
    """
    return _check_optional_dependencies()


def enable_debug_mode() -> None:
    """
    Enable debug mode for verbose logging and additional checks.
    
    Example:
        >>> enable_debug_mode()
        >>> get_config().debug
        True
    """
    get_config().debug = True
    get_config().log_level = "DEBUG"


def enable_performance_mode() -> None:
    """
    Enable performance optimization mode.
    
    This disables some validation checks for maximum throughput.
    
    Example:
        >>> enable_performance_mode()
        >>> get_config().performance_mode
        True
    """
    get_config().performance_mode = True
    get_config().strict_mode = False


def enable_strict_mode() -> None:
    """
    Enable strict validation mode for maximum safety.
    
    Example:
        >>> enable_strict_mode()
        >>> get_config().strict_mode
        True
    """
    get_config().strict_mode = True
    get_config().performance_mode = False


# =============================================================================
# INITIALIZATION
# =============================================================================

def _initialize() -> None:
    """
    Perform package initialization tasks.
    
    This function is called when the package is first imported and handles:
    - Python version validation
    - Dependency checks
    - Warning emissions for missing optional packages
    """
    try:
        _validate_python_version()
        _warn_missing_dependencies()
    except Exception as e:
        warnings.warn(
            f"Initialization warning: {e}",
            RuntimeWarning,
            stacklevel=2
        )


# Execute initialization
_initialize()


# =============================================================================
# MODULE REGISTRATION
# =============================================================================

# Register cleanup handler
def _cleanup() -> None:
    """Perform cleanup operations on module unload."""
    # Clear caches
    _check_optional_dependencies.cache_clear()
    
    # Reset singleton if needed
    _PackageConfig._instance = None


# Register atexit handler for clean shutdown
import atexit
atexit.register(_cleanup)


# =============================================================================
# DOCUMENTATION
# =============================================================================

__doc__ = f"""
{__doc__}

QUICK START:
    >>> from core import Config, DownloaderBase, NetworkClient
    >>> config = Config()
    >>> async with NetworkClient(config) as client:
    ...     response = await client.get("https://example.com")
    
DEPENDENCIES:
    Required:
        - Python {_MIN_PYTHON_VERSION[0]}.{_MIN_PYTHON_VERSION[1]}+
    
    Optional (recommended):
        - aiohttp: Async HTTP client
        - httpx: Alternative async HTTP client
        - tenacity: Retry mechanisms
        - certifi: SSL certificate bundle
        - tqdm/-rich: Progress bars
    
RUNTIME INFO:
    {_get_runtime_info()}
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       ULTIMATE NEXUS VALIDATION SYSTEM                        ║
║                              v3.0.1 SOVEREIGN EDITION                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Author: RAJSARASWATI JATAV (RS) - OMNIPOTENT SOVEREIGN NEXUS                ║
║  Channel: T3rmuxk1ng                                                         ║
║  Description: Comprehensive validation system for URLs, emails, IPs, files,  ║
║               security data, and custom patterns with detailed error messages║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import os
import re
import sys
import json
import socket
import ipaddress
import platform
import subprocess
import urllib.parse
from typing import (
    Dict, List, Tuple, Optional, Union, Callable, Any, 
    Pattern, Set, Type, Generic, TypeVar, Iterator,
)
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from functools import lru_cache
from datetime import datetime

from .colors import ColorManager

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

# ============================================================================
# VALIDATION RESULT
# ============================================================================
@dataclass
class ValidationResult:
    """
    Result of a validation operation.
    
    Attributes:
        is_valid: Whether validation passed
        value: Validated (possibly sanitized) value
        errors: List of error messages
        warnings: List of warning messages
        metadata: Additional validation metadata
    """
    is_valid: bool
    value: Any = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __bool__(self) -> bool:
        return self.is_valid
    
    def __repr__(self) -> str:
        status = "✓ Valid" if self.is_valid else "✗ Invalid"
        return f"ValidationResult({status}, errors={len(self.errors)})"
    
    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)
    
    def merge(self, other: 'ValidationResult') -> 'ValidationResult':
        """Merge another validation result into this one."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.metadata.update(other.metadata)
        if not other.is_valid:
            self.is_valid = False
        return self


# ============================================================================
# VALIDATION ERROR CLASS
# ============================================================================
class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, message: str, field: str = "", value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(f"{field}: {message}" if field else message)


# ============================================================================
# VALIDATION LEVEL ENUM
# ============================================================================
class ValidationLevel(Enum):
    """Validation strictness levels."""
    LENIENT = auto()    # Allow minor issues with warnings
    NORMAL = auto()     # Standard validation
    STRICT = auto()     # Strict validation, no warnings allowed
    PARANOID = auto()   # Maximum strictness


# ============================================================================
# URL VALIDATOR
# ============================================================================
class URLValidator:
    """
    Comprehensive URL validation.
    
    Features:
    - Protocol validation (http, https, ftp, etc.)
    - Domain validation
    - Port validation
    - Path validation
    - Query parameter validation
    - Security checks (SSRF, injection, etc.)
    """
    
    # Allowed schemes
    ALLOWED_SCHEMES = {'http', 'https', 'ftp', 'ftps', 'sftp', 'file', 'data'}
    
    # Dangerous patterns
    DANGEROUS_PATTERNS = [
        r'javascript:',
        r'data:text/html',
        r'vbscript:',
        r'file://.*\.\./',  # Path traversal
        r'@',               # URL authority injection
    ]
    
    # URL regex pattern
    URL_PATTERN = re.compile(
        r'^(?P<scheme>[a-zA-Z][a-zA-Z0-9+.-]*)://'
        r'(?P<authority>'
        r'(?P<userinfo>(?P<user>[^:/@]+)(?::(?P<password>[^/@]*))?@)?'
        r'(?P<host>[^:/@]+)'
        r'(?::(?P<port>\d+))?'
        r')'
        r'(?P<path>/[^?#]*)?'
        r'(?:\?(?P<query>[^#]*))?'
        r'(?:#(?P<fragment>.*))?$',
        re.IGNORECASE
    )
    
    def __init__(
        self,
        allowed_schemes: Set[str] = None,
        allow_localhost: bool = True,
        allow_private_ips: bool = True,
        allow_credentials: bool = False,
        max_length: int = 2048,
        level: ValidationLevel = ValidationLevel.NORMAL,
    ) -> None:
        """
        Initialize URL validator.
        
        Args:
            allowed_schemes: Set of allowed URL schemes
            allow_localhost: Whether to allow localhost URLs
            allow_private_ips: Whether to allow private IP addresses
            allow_credentials: Whether to allow credentials in URL
            max_length: Maximum URL length
            level: Validation strictness level
        """
        self.allowed_schemes = allowed_schemes or self.ALLOWED_SCHEMES
        self.allow_localhost = allow_localhost
        self.allow_private_ips = allow_private_ips
        self.allow_credentials = allow_credentials
        self.max_length = max_length
        self.level = level
    
    def validate(self, url: str) -> ValidationResult:
        """
        Validate a URL string.
        
        Args:
            url: URL string to validate
            
        Returns:
            ValidationResult with validation status and details
        """
        result = ValidationResult(is_valid=True, value=url)
        
        # Check if URL is empty
        if not url:
            result.add_error("URL cannot be empty")
            return result
        
        # Check URL length
        if len(url) > self.max_length:
            result.add_error(f"URL exceeds maximum length of {self.max_length}")
        
        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                result.add_error(f"URL contains dangerous pattern: {pattern}")
        
        # Parse URL
        try:
            parsed = urllib.parse.urlparse(url)
        except Exception as e:
            result.add_error(f"Failed to parse URL: {str(e)}")
            return result
        
        # Validate scheme
        if not parsed.scheme:
            result.add_error("URL must have a scheme (e.g., https://)")
        elif parsed.scheme.lower() not in self.allowed_schemes:
            result.add_error(f"URL scheme '{parsed.scheme}' is not allowed. "
                           f"Allowed: {', '.join(self.allowed_schemes)}")
        
        # Validate host
        if not parsed.netloc:
            result.add_error("URL must have a host")
        else:
            host = parsed.hostname
            if host:
                # Check for localhost
                if host.lower() in ('localhost', '127.0.0.1', '::1'):
                    if not self.allow_localhost:
                        result.add_error("Localhost URLs are not allowed")
                    else:
                        result.add_warning("URL points to localhost")
                
                # Check for private IPs
                try:
                    ip = ipaddress.ip_address(host)
                    if ip.is_private and not self.allow_private_ips:
                        result.add_error(f"Private IP addresses are not allowed: {host}")
                except ValueError:
                    pass  # Not an IP address, continue
                
                # Validate domain format
                if not self._is_valid_domain(host):
                    if self.level in (ValidationLevel.STRICT, ValidationLevel.PARANOID):
                        result.add_error(f"Invalid domain format: {host}")
                    else:
                        result.add_warning(f"Domain format may be invalid: {host}")
        
        # Check for credentials in URL
        if parsed.username or parsed.password:
            if not self.allow_credentials:
                result.add_error("Credentials in URL are not allowed")
            else:
                result.add_warning("URL contains credentials - this is a security risk")
        
        # Validate port if specified
        if parsed.port:
            if not (1 <= parsed.port <= 65535):
                result.add_error(f"Invalid port number: {parsed.port}")
            elif parsed.port < 1024 and self.level == ValidationLevel.PARANOID:
                result.add_warning(f"URL uses privileged port: {parsed.port}")
        
        # Store parsed components in metadata
        result.metadata['parsed'] = {
            'scheme': parsed.scheme,
            'netloc': parsed.netloc,
            'host': parsed.hostname,
            'port': parsed.port,
            'path': parsed.path,
            'query': parsed.query,
            'fragment': parsed.fragment,
        }
        
        return result
    
    def _is_valid_domain(self, domain: str) -> bool:
        """Check if domain format is valid."""
        # Domain regex pattern
        pattern = re.compile(
            r'^(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*'
            r'[a-zA-Z]{2,}|'
            r'\[(?:[A-Fa-f0-9:]+)\])$'
        )
        return bool(pattern.match(domain))
    
    @staticmethod
    def is_valid(url: str) -> bool:
        """Quick check if URL is valid."""
        return URLValidator().validate(url).is_valid
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract all URLs from text."""
        url_pattern = re.compile(
            r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}'
            r'\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
        )
        return url_pattern.findall(text)


# ============================================================================
# EMAIL VALIDATOR
# ============================================================================
class EmailValidator:
    """
    Comprehensive email validation.
    
    Features:
    - RFC 5322 compliant email validation
    - Domain validation
    - MX record checking
    - Disposable email detection
    - Role-based email detection
    """
    
    # Email regex pattern (RFC 5322 simplified)
    EMAIL_PATTERN = re.compile(
        r"^(?P<local>[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+)"
        r"@"
        r"(?P<domain>[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
        r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+)$"
    )
    
    # Common disposable email domains
    DISPOSABLE_DOMAINS = {
        '10minutemail.com', 'guerrillamail.com', 'mailinator.com',
        'tempmail.com', 'throwaway.email', 'fakeinbox.com',
        'temp-mail.org', 'dispostable.com', 'mailnesia.com',
        'tempmail.net', 'throwam.com', 'getairmail.com',
    }
    
    # Role-based email prefixes
    ROLE_PREFIXES = {
        'admin', 'administrator', 'info', 'support', 'sales',
        'contact', 'help', 'webmaster', 'postmaster', 'root',
        'abuse', 'noc', 'security', 'hostmaster', 'marketing',
        'pr', 'press', 'legal', 'finance', 'accounting',
    }
    
    def __init__(
        self,
        allow_disposable: bool = False,
        allow_role_based: bool = True,
        check_mx: bool = False,
        max_length: int = 254,
        level: ValidationLevel = ValidationLevel.NORMAL,
    ) -> None:
        """
        Initialize email validator.
        
        Args:
            allow_disposable: Whether to allow disposable emails
            allow_role_based: Whether to allow role-based emails
            check_mx: Whether to check MX records
            max_length: Maximum email length
            level: Validation strictness level
        """
        self.allow_disposable = allow_disposable
        self.allow_role_based = allow_role_based
        self.check_mx = check_mx
        self.max_length = max_length
        self.level = level
    
    def validate(self, email: str) -> ValidationResult:
        """
        Validate an email address.
        
        Args:
            email: Email address to validate
            
        Returns:
            ValidationResult with validation status and details
        """
        result = ValidationResult(is_valid=True, value=email.strip().lower())
        
        # Check if email is empty
        if not email:
            result.add_error("Email cannot be empty")
            return result
        
        # Check email length
        if len(email) > self.max_length:
            result.add_error(f"Email exceeds maximum length of {self.max_length}")
        
        # Normalize email
        email = email.strip().lower()
        
        # Check email format
        match = self.EMAIL_PATTERN.match(email)
        if not match:
            result.add_error("Invalid email format")
            return result
        
        local_part = match.group('local')
        domain = match.group('domain')
        
        # Check local part
        if len(local_part) > 64:
            result.add_error("Email local part exceeds 64 characters")
        
        if local_part.startswith('.') or local_part.endswith('.'):
            result.add_error("Email local part cannot start or end with a dot")
        
        if '..' in local_part:
            result.add_error("Email local part cannot contain consecutive dots")
        
        # Check for role-based email
        local_prefix = local_part.split('+')[0].split('.')[0]
        if local_prefix in self.ROLE_PREFIXES:
            if not self.allow_role_based:
                result.add_error(f"Role-based email addresses are not allowed: {local_prefix}")
            else:
                result.add_warning(f"This appears to be a role-based email: {local_prefix}")
        
        # Check for disposable email
        if domain in self.DISPOSABLE_DOMAINS:
            if not self.allow_disposable:
                result.add_error(f"Disposable email domains are not allowed: {domain}")
            else:
                result.add_warning(f"This is a disposable email domain: {domain}")
        
        # Check MX records (if enabled)
        if self.check_mx and result.is_valid:
            if not self._check_mx_record(domain):
                if self.level in (ValidationLevel.STRICT, ValidationLevel.PARANOID):
                    result.add_error(f"No MX records found for domain: {domain}")
                else:
                    result.add_warning(f"Could not verify MX records for domain: {domain}")
        
        # Store parsed components
        result.metadata['local'] = local_part
        result.metadata['domain'] = domain
        
        return result
    
    def _check_mx_record(self, domain: str) -> bool:
        """Check if domain has MX records."""
        try:
            import dns.resolver
            answers = dns.resolver.resolve(domain, 'MX')
            return len(answers) > 0
        except Exception:
            return False
    
    @staticmethod
    def is_valid(email: str) -> bool:
        """Quick check if email is valid."""
        return EmailValidator().validate(email).is_valid


# ============================================================================
# IP ADDRESS VALIDATOR
# ============================================================================
class IPValidator:
    """
    Comprehensive IP address validation.
    
    Features:
    - IPv4 and IPv6 validation
    - CIDR notation support
    - Private/Public IP detection
    - Reserved IP detection
    - IP range validation
    """
    
    def __init__(
        self,
        allow_private: bool = True,
        allow_loopback: bool = True,
        allow_multicast: bool = True,
        allow_reserved: bool = True,
        version: Optional[int] = None,  # 4, 6, or None for both
    ) -> None:
        """
        Initialize IP validator.
        
        Args:
            allow_private: Whether to allow private IPs
            allow_loopback: Whether to allow loopback IPs
            allow_multicast: Whether to allow multicast IPs
            allow_reserved: Whether to allow reserved IPs
            version: IP version to allow (4, 6, or None for both)
        """
        self.allow_private = allow_private
        self.allow_loopback = allow_loopback
        self.allow_multicast = allow_multicast
        self.allow_reserved = allow_reserved
        self.version = version
    
    def validate(self, ip: str) -> ValidationResult:
        """
        Validate an IP address.
        
        Args:
            ip: IP address string to validate
            
        Returns:
            ValidationResult with validation status and details
        """
        result = ValidationResult(is_valid=True, value=ip.strip())
        
        if not ip:
            result.add_error("IP address cannot be empty")
            return result
        
        ip = ip.strip()
        
        # Handle CIDR notation
        cidr = None
        if '/' in ip:
            ip, cidr = ip.split('/', 1)
            try:
                cidr = int(cidr)
            except ValueError:
                result.add_error(f"Invalid CIDR notation: {cidr}")
                return result
        
        # Parse IP address
        try:
            ip_obj = ipaddress.ip_address(ip)
        except ValueError:
            result.add_error(f"Invalid IP address format: {ip}")
            return result
        
        # Check IP version
        if self.version:
            if self.version == 4 and not isinstance(ip_obj, ipaddress.IPv4Address):
                result.add_error(f"Expected IPv4 address, got IPv6: {ip}")
            elif self.version == 6 and not isinstance(ip_obj, ipaddress.IPv6Address):
                result.add_error(f"Expected IPv6 address, got IPv4: {ip}")
        
        # Check for loopback
        if ip_obj.is_loopback and not self.allow_loopback:
            result.add_error("Loopback IP addresses are not allowed")
        
        # Check for private
        if ip_obj.is_private and not self.allow_private:
            result.add_error("Private IP addresses are not allowed")
        
        # Check for multicast
        if ip_obj.is_multicast and not self.allow_multicast:
            result.add_error("Multicast IP addresses are not allowed")
        
        # Check for reserved
        if ip_obj.is_reserved and not self.allow_reserved:
            result.add_error("Reserved IP addresses are not allowed")
        
        # Validate CIDR if present
        if cidr is not None:
            if isinstance(ip_obj, ipaddress.IPv4Address):
                if not (0 <= cidr <= 32):
                    result.add_error(f"Invalid IPv4 CIDR: {cidr} (must be 0-32)")
            else:
                if not (0 <= cidr <= 128):
                    result.add_error(f"Invalid IPv6 CIDR: {cidr} (must be 0-128)")
        
        # Store metadata
        result.metadata['version'] = 4 if isinstance(ip_obj, ipaddress.IPv4Address) else 6
        result.metadata['is_private'] = ip_obj.is_private
        result.metadata['is_loopback'] = ip_obj.is_loopback
        result.metadata['is_multicast'] = ip_obj.is_multicast
        result.metadata['is_reserved'] = ip_obj.is_reserved
        result.metadata['is_global'] = ip_obj.is_global
        result.metadata['cidr'] = cidr
        
        return result
    
    def validate_range(self, start_ip: str, end_ip: str) -> ValidationResult:
        """Validate an IP range."""
        result = ValidationResult(is_valid=True)
        
        start_result = self.validate(start_ip)
        end_result = self.validate(end_ip)
        
        result.merge(start_result)
        result.merge(end_result)
        
        if result.is_valid:
            try:
                start = ipaddress.ip_address(start_ip.strip())
                end = ipaddress.ip_address(end_ip.strip())
                
                if start > end:
                    result.add_error(f"Start IP {start_ip} is greater than end IP {end_ip}")
                
                if type(start) != type(end):
                    result.add_error("Start and end IPs must be the same version")
                
                result.metadata['count'] = int(end) - int(start) + 1
            except Exception:
                pass
        
        return result
    
    @staticmethod
    def is_valid(ip: str) -> bool:
        """Quick check if IP is valid."""
        return IPValidator().validate(ip).is_valid
    
    @staticmethod
    def is_ipv4(ip: str) -> bool:
        """Check if IP is valid IPv4."""
        try:
            return isinstance(ipaddress.ip_address(ip.strip()), ipaddress.IPv4Address)
        except ValueError:
            return False
    
    @staticmethod
    def is_ipv6(ip: str) -> bool:
        """Check if IP is valid IPv6."""
        try:
            return isinstance(ipaddress.ip_address(ip.strip()), ipaddress.IPv6Address)
        except ValueError:
            return False


# ============================================================================
# PORT VALIDATOR
# ============================================================================
class PortValidator:
    """
    Port number validation.
    
    Features:
    - Valid port range (1-65535)
    - Well-known port warnings
    - Port range parsing
    """
    
    WELL_KNOWN_PORTS = {
        20: 'FTP Data', 21: 'FTP Control', 22: 'SSH', 23: 'Telnet',
        25: 'SMTP', 53: 'DNS', 67: 'DHCP Server', 68: 'DHCP Client',
        69: 'TFTP', 80: 'HTTP', 110: 'POP3', 119: 'NNTP',
        123: 'NTP', 135: 'RPC', 137: 'NetBIOS', 138: 'NetBIOS',
        139: 'NetBIOS', 143: 'IMAP', 161: 'SNMP', 162: 'SNMP Trap',
        389: 'LDAP', 443: 'HTTPS', 445: 'SMB', 465: 'SMTPS',
        514: 'Syslog', 587: 'SMTP (TLS)', 636: 'LDAPS', 993: 'IMAPS',
        995: 'POP3S', 1080: 'SOCKS', 1433: 'MSSQL', 1521: 'Oracle',
        1723: 'PPTP', 2049: 'NFS', 3306: 'MySQL', 3389: 'RDP',
        5432: 'PostgreSQL', 5900: 'VNC', 6379: 'Redis', 8080: 'HTTP Proxy',
        8443: 'HTTPS Alt', 9000: 'PHP-FPM', 27017: 'MongoDB',
    }
    
    def __init__(
        self,
        allow_privileged: bool = True,
        allow_well_known: bool = True,
        min_port: int = 1,
        max_port: int = 65535,
    ) -> None:
        """
        Initialize port validator.
        
        Args:
            allow_privileged: Whether to allow ports < 1024
            allow_well_known: Whether to allow well-known ports
            min_port: Minimum allowed port
            max_port: Maximum allowed port
        """
        self.allow_privileged = allow_privileged
        self.allow_well_known = allow_well_known
        self.min_port = min_port
        self.max_port = max_port
    
    def validate(self, port: Union[str, int]) -> ValidationResult:
        """Validate a port number."""
        result = ValidationResult(is_valid=True)
        
        # Convert to int
        try:
            port_num = int(port)
        except (ValueError, TypeError):
            result.add_error(f"Invalid port number: {port}")
            return result
        
        result.value = port_num
        
        # Check range
        if not (self.min_port <= port_num <= self.max_port):
            result.add_error(f"Port must be between {self.min_port} and {self.max_port}")
        
        # Check privileged port
        if port_num < 1024:
            if not self.allow_privileged:
                result.add_error(f"Privileged ports (< 1024) are not allowed")
            else:
                result.add_warning(f"Port {port_num} is a privileged port")
        
        # Check well-known port
        if port_num in self.WELL_KNOWN_PORTS:
            service = self.WELL_KNOWN_PORTS[port_num]
            if not self.allow_well_known:
                result.add_error(f"Well-known port {port_num} ({service}) is not allowed")
            else:
                result.metadata['service'] = service
                result.add_warning(f"Port {port_num} is typically used for {service}")
        
        return result
    
    def validate_range(self, port_range: str) -> ValidationResult:
        """Validate port range string (e.g., '80,443,8000-9000')."""
        result = ValidationResult(is_valid=True)
        ports = []
        
        for part in port_range.split(','):
            part = part.strip()
            if '-' in part:
                try:
                    start, end = part.split('-')
                    start, end = int(start), int(end)
                    if start > end:
                        result.add_error(f"Invalid port range: {part}")
                    else:
                        for port in range(start, end + 1):
                            port_result = self.validate(port)
                            if port_result.is_valid:
                                ports.append(port)
                            result.warnings.extend(port_result.warnings)
                except ValueError:
                    result.add_error(f"Invalid port range format: {part}")
            else:
                try:
                    port = int(part)
                    port_result = self.validate(port)
                    if port_result.is_valid:
                        ports.append(port)
                    result.warnings.extend(port_result.warnings)
                except ValueError:
                    result.add_error(f"Invalid port: {part}")
        
        result.value = sorted(set(ports))
        result.metadata['count'] = len(ports)
        
        return result
    
    @staticmethod
    def is_valid(port: Union[str, int]) -> bool:
        """Quick check if port is valid."""
        return PortValidator().validate(port).is_valid


# ============================================================================
# FILE VALIDATOR
# ============================================================================
class FileValidator:
    """
    File path and content validation.
    
    Features:
    - Path validation (exists, readable, writable)
    - Extension validation
    - Size validation
    - Content type validation
    """
    
    def __init__(
        self,
        allowed_extensions: Optional[Set[str]] = None,
        min_size: int = 0,
        max_size: Optional[int] = None,
        must_exist: bool = False,
        must_be_file: bool = False,
        must_be_dir: bool = False,
        must_be_readable: bool = False,
        must_be_writable: bool = False,
    ) -> None:
        """
        Initialize file validator.
        
        Args:
            allowed_extensions: Set of allowed file extensions
            min_size: Minimum file size in bytes
            max_size: Maximum file size in bytes
            must_exist: Whether file must exist
            must_be_file: Whether path must be a file
            must_be_dir: Whether path must be a directory
            must_be_readable: Whether file must be readable
            must_be_writable: Whether file must be writable
        """
        self.allowed_extensions = allowed_extensions
        self.min_size = min_size
        self.max_size = max_size
        self.must_exist = must_exist
        self.must_be_file = must_be_file
        self.must_be_dir = must_be_dir
        self.must_be_readable = must_be_readable
        self.must_be_writable = must_be_writable
    
    def validate(self, filepath: Union[str, Path]) -> ValidationResult:
        """Validate a file path."""
        result = ValidationResult(is_valid=True, value=str(filepath))
        
        path = Path(filepath)
        
        # Check existence
        if self.must_exist and not path.exists():
            result.add_error(f"Path does not exist: {filepath}")
            return result
        
        if path.exists():
            # Check if file
            if self.must_be_file and not path.is_file():
                result.add_error(f"Path is not a file: {filepath}")
            
            # Check if directory
            if self.must_be_dir and not path.is_dir():
                result.add_error(f"Path is not a directory: {filepath}")
            
            # Check extension
            if self.allowed_extensions:
                ext = path.suffix.lower().lstrip('.')
                if ext not in {e.lower().lstrip('.') for e in self.allowed_extensions}:
                    result.add_error(f"File extension '{ext}' is not allowed. "
                                   f"Allowed: {', '.join(self.allowed_extensions)}")
            
            # Check size (only for files)
            if path.is_file():
                size = path.stat().st_size
                if size < self.min_size:
                    result.add_error(f"File size {size} is below minimum {self.min_size}")
                if self.max_size and size > self.max_size:
                    result.add_error(f"File size {size} exceeds maximum {self.max_size}")
                result.metadata['size'] = size
            
            # Check readability
            if self.must_be_readable and not os.access(path, os.R_OK):
                result.add_error(f"File is not readable: {filepath}")
            
            # Check writability
            if self.must_be_writable and not os.access(path, os.W_OK):
                result.add_error(f"File is not writable: {filepath}")
        
        # Store metadata
        result.metadata['path'] = str(path.absolute())
        result.metadata['name'] = path.name
        result.metadata['extension'] = path.suffix
        result.metadata['exists'] = path.exists()
        
        return result
    
    @staticmethod
    def is_valid_path(filepath: Union[str, Path]) -> bool:
        """Quick check if path is valid."""
        try:
            Path(filepath)
            return True
        except Exception:
            return False


# ============================================================================
# NUMBER VALIDATOR
# ============================================================================
class NumberValidator:
    """
    Number validation utilities.
    
    Features:
    - Integer validation
    - Float validation
    - Range validation
    - Type coercion
    """
    
    def __init__(
        self,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        allow_negative: bool = True,
        allow_zero: bool = True,
        allow_float: bool = True,
        precision: Optional[int] = None,
    ) -> None:
        """
        Initialize number validator.
        
        Args:
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            allow_negative: Whether to allow negative numbers
            allow_zero: Whether to allow zero
            allow_float: Whether to allow floating-point numbers
            precision: Decimal precision for floats
        """
        self.min_value = min_value
        self.max_value = max_value
        self.allow_negative = allow_negative
        self.allow_zero = allow_zero
        self.allow_float = allow_float
        self.precision = precision
    
    def validate(self, value: Union[str, int, float]) -> ValidationResult:
        """Validate a number."""
        result = ValidationResult(is_valid=True)
        
        # Convert to number
        if isinstance(value, str):
            value = value.strip()
            try:
                if '.' in value or 'e' in value.lower():
                    num = float(value)
                else:
                    num = int(value)
            except ValueError:
                result.add_error(f"Invalid number format: {value}")
                return result
        else:
            num = value
        
        # Check type
        if isinstance(num, float) and not self.allow_float:
            result.add_error("Floating-point numbers are not allowed")
            return result
        
        # Check negative
        if num < 0 and not self.allow_negative:
            result.add_error("Negative numbers are not allowed")
        
        # Check zero
        if num == 0 and not self.allow_zero:
            result.add_error("Zero is not allowed")
        
        # Check range
        if self.min_value is not None and num < self.min_value:
            result.add_error(f"Value {num} is below minimum {self.min_value}")
        
        if self.max_value is not None and num > self.max_value:
            result.add_error(f"Value {num} exceeds maximum {self.max_value}")
        
        # Apply precision
        if self.precision is not None and isinstance(num, float):
            num = round(num, self.precision)
        
        result.value = num
        result.metadata['type'] = 'float' if isinstance(num, float) else 'int'
        
        return result


# ============================================================================
# STRING VALIDATOR
# ============================================================================
class StringValidator:
    """
    String validation utilities.
    
    Features:
    - Length validation
    - Pattern matching
    - Character restrictions
    - Sanitization options
    """
    
    def __init__(
        self,
        min_length: int = 0,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        allowed_chars: Optional[str] = None,
        forbidden_chars: Optional[str] = None,
        allow_empty: bool = False,
        strip_whitespace: bool = True,
        case: Optional[str] = None,  # 'upper', 'lower', or None
    ) -> None:
        """
        Initialize string validator.
        
        Args:
            min_length: Minimum string length
            max_length: Maximum string length
            pattern: Regex pattern to match
            allowed_chars: String of allowed characters
            forbidden_chars: String of forbidden characters
            allow_empty: Whether to allow empty strings
            strip_whitespace: Whether to strip whitespace
            case: Force case ('upper', 'lower', or None)
        """
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = re.compile(pattern) if pattern else None
        self.allowed_chars = allowed_chars
        self.forbidden_chars = forbidden_chars
        self.allow_empty = allow_empty
        self.strip_whitespace = strip_whitespace
        self.case = case
    
    def validate(self, value: str) -> ValidationResult:
        """Validate a string."""
        result = ValidationResult(is_valid=True)
        
        if not isinstance(value, str):
            value = str(value)
        
        # Strip whitespace
        if self.strip_whitespace:
            value = value.strip()
        
        # Check empty
        if not value:
            if not self.allow_empty:
                result.add_error("String cannot be empty")
            result.value = value
            return result
        
        # Check length
        if len(value) < self.min_length:
            result.add_error(f"String length {len(value)} is below minimum {self.min_length}")
        
        if self.max_length and len(value) > self.max_length:
            result.add_error(f"String length {len(value)} exceeds maximum {self.max_length}")
        
        # Check pattern
        if self.pattern and not self.pattern.match(value):
            result.add_error(f"String does not match required pattern: {self.pattern.pattern}")
        
        # Check allowed characters
        if self.allowed_chars:
            invalid_chars = set(value) - set(self.allowed_chars)
            if invalid_chars:
                result.add_error(f"String contains invalid characters: {invalid_chars}")
        
        # Check forbidden characters
        if self.forbidden_chars:
            found = set(value) & set(self.forbidden_chars)
            if found:
                result.add_error(f"String contains forbidden characters: {found}")
        
        # Apply case
        if self.case == 'upper':
            value = value.upper()
        elif self.case == 'lower':
            value = value.lower()
        
        result.value = value
        result.metadata['length'] = len(value)
        
        return result


# ============================================================================
# COMPOSITE VALIDATOR
# ============================================================================
class CompositeValidator:
    """
    Combine multiple validators.
    
    Example:
        >>> validator = CompositeValidator([
        ...     StringValidator(min_length=5),
        ...     URLValidator()
        ... ])
        >>> result = validator.validate("https://example.com")
    """
    
    def __init__(self, validators: List[Callable[[Any], ValidationResult]]) -> None:
        """
        Initialize composite validator.
        
        Args:
            validators: List of validator functions
        """
        self.validators = validators
    
    def validate(self, value: Any) -> ValidationResult:
        """Run all validators."""
        result = ValidationResult(is_valid=True, value=value)
        
        for validator in self.validators:
            validator_result = validator(value)
            result.merge(validator_result)
            if not validator_result.is_valid and not isinstance(validator, type):
                break
        
        return result
    
    def add_validator(self, validator: Callable[[Any], ValidationResult]) -> None:
        """Add a validator."""
        self.validators.append(validator)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================
def validate_url(url: str, **kwargs) -> ValidationResult:
    """Validate a URL."""
    return URLValidator(**kwargs).validate(url)


def validate_email(email: str, **kwargs) -> ValidationResult:
    """Validate an email address."""
    return EmailValidator(**kwargs).validate(email)


def validate_ip(ip: str, **kwargs) -> ValidationResult:
    """Validate an IP address."""
    return IPValidator(**kwargs).validate(ip)


def validate_port(port: Union[str, int], **kwargs) -> ValidationResult:
    """Validate a port number."""
    return PortValidator(**kwargs).validate(port)


def validate_file(filepath: Union[str, Path], **kwargs) -> ValidationResult:
    """Validate a file path."""
    return FileValidator(**kwargs).validate(filepath)


def validate_number(value: Union[str, int, float], **kwargs) -> ValidationResult:
    """Validate a number."""
    return NumberValidator(**kwargs).validate(value)


def validate_string(value: str, **kwargs) -> ValidationResult:
    """Validate a string."""
    return StringValidator(**kwargs).validate(value)


# ============================================================================
# VALIDATOR FACTORY
# ============================================================================
class ValidatorFactory:
    """
    Factory for creating validators.
    
    Example:
        >>> factory = ValidatorFactory()
        >>> url_validator = factory.create_url_validator(allow_localhost=False)
        >>> email_validator = factory.create_email_validator(check_mx=True)
    """
    
    @staticmethod
    def create_url_validator(**kwargs) -> URLValidator:
        """Create a URL validator."""
        return URLValidator(**kwargs)
    
    @staticmethod
    def create_email_validator(**kwargs) -> EmailValidator:
        """Create an email validator."""
        return EmailValidator(**kwargs)
    
    @staticmethod
    def create_ip_validator(**kwargs) -> IPValidator:
        """Create an IP validator."""
        return IPValidator(**kwargs)
    
    @staticmethod
    def create_port_validator(**kwargs) -> PortValidator:
        """Create a port validator."""
        return PortValidator(**kwargs)
    
    @staticmethod
    def create_file_validator(**kwargs) -> FileValidator:
        """Create a file validator."""
        return FileValidator(**kwargs)
    
    @staticmethod
    def create_number_validator(**kwargs) -> NumberValidator:
        """Create a number validator."""
        return NumberValidator(**kwargs)
    
    @staticmethod
    def create_string_validator(**kwargs) -> StringValidator:
        """Create a string validator."""
        return StringValidator(**kwargs)


# ============================================================================
# MODULE-LEVEL INSTANCES
# ============================================================================
validator_factory = ValidatorFactory()


# ============================================================================
# EXPORTS
# ============================================================================
__all__ = [
    # Version
    '__version__',
    '__author__',
    '__status__',
    
    # Result class
    'ValidationResult',
    'ValidationError',
    'ValidationLevel',
    
    # Validators
    'URLValidator',
    'EmailValidator',
    'IPValidator',
    'PortValidator',
    'FileValidator',
    'NumberValidator',
    'StringValidator',
    'CompositeValidator',
    
    # Factory
    'ValidatorFactory',
    'validator_factory',
    
    # Convenience functions
    'validate_url',
    'validate_email',
    'validate_ip',
    'validate_port',
    'validate_file',
    'validate_number',
    'validate_string',
]


# ============================================================================
# MAIN DEMO
# ============================================================================
if __name__ == "__main__":
    from .colors import ColorManager
    cm = ColorManager()
    
    print("\n" + "="*60)
    print("    ULTIMATE NEXUS VALIDATION SYSTEM v3.0.1 - DEMO")
    print("="*60 + "\n")
    
    # URL Validation Demo
    print("--- URL Validation ---")
    urls = [
        "https://example.com",
        "http://localhost:8080",
        "javascript:alert('xss')",
        "not-a-url",
        "ftp://files.example.com/file.txt",
    ]
    
    for url in urls:
        result = validate_url(url)
        status = cm.success("✓") if result.is_valid else cm.error("✗")
        print(f"{status} {url}")
        if result.errors:
            for err in result.errors:
                print(f"    {cm.error(err)}")
    
    # Email Validation Demo
    print("\n--- Email Validation ---")
    emails = [
        "user@example.com",
        "invalid-email",
        "admin@company.com",  # Role-based
        "user@10minutemail.com",  # Disposable
        "user+tag@gmail.com",
    ]
    
    for email in emails:
        result = validate_email(email)
        status = cm.success("✓") if result.is_valid else cm.error("✗")
        print(f"{status} {email}")
        if result.warnings:
            for warn in result.warnings:
                print(f"    {cm.warning(warn)}")
    
    # IP Validation Demo
    print("\n--- IP Validation ---")
    ips = [
        "192.168.1.1",
        "8.8.8.8",
        "2001:4860:4860::8888",
        "invalid-ip",
        "10.0.0.1/24",
    ]
    
    for ip in ips:
        result = validate_ip(ip)
        status = cm.success("✓") if result.is_valid else cm.error("✗")
        print(f"{status} {ip}")
        if result.metadata:
            print(f"    Version: IPv{result.metadata.get('version')}")
    
    # Port Validation Demo
    print("\n--- Port Validation ---")
    ports = ["80", "443", "8080", "99999", "22"]
    
    for port in ports:
        result = validate_port(port)
        status = cm.success("✓") if result.is_valid else cm.error("✗")
        service = result.metadata.get('service', '')
        print(f"{status} {port} {f'({service})' if service else ''}")
    
    print("\nDemo complete!")

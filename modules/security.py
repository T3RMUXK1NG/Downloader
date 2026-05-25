"""
OMNIPOTENT SOVEREIGN NEXUS - Security Tools Module
Version: v3.0.1 ULTIMATE NEXUS

Security tools with support for:
- File integrity verification
- Hash calculation and verification
- Encryption/Decryption
- Secure file deletion
- URL validation
- Malware scanning integration
- Certificate validation
- Safe filename handling

Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
"""

import asyncio
import aiofiles
import logging
import hashlib
import hmac
import secrets
import base64
import os
import re
import json
import ssl
import socket
import subprocess
import shutil
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
import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, ciphers
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)


class HashAlgorithm(Enum):
    """Hash algorithm options."""
    
    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"
    BLAKE2B = "blake2b"
    BLAKE2S = "blake2s"


class EncryptionAlgorithm(Enum):
    """Encryption algorithm options."""
    
    AES_128 = "aes_128"
    AES_256 = "aes_256"
    FERNET = "fernet"
    CHACHA20 = "chacha20"


class SecurityLevel(Enum):
    """Security level presets."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PARANOID = "paranoid"


class ThreatLevel(Enum):
    """Threat level assessment."""
    
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class HashResult:
    """
    Hash calculation result.
    
    Attributes:
        algorithm: Hash algorithm used
        hash_value: Hash value in hex
        file_path: File path (if file hash)
        data_size: Data size in bytes
        calculation_time: Time taken in seconds
    """
    algorithm: HashAlgorithm
    hash_value: str
    file_path: Optional[Path] = None
    data_size: int = 0
    calculation_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "algorithm": self.algorithm.value,
            "hash_value": self.hash_value,
            "file_path": str(self.file_path) if self.file_path else None,
            "data_size": self.data_size,
            "calculation_time": round(self.calculation_time, 3),
        }


@dataclass
class VerificationResult:
    """
    Hash verification result.
    
    Attributes:
        success: Whether verification passed
        expected_hash: Expected hash value
        actual_hash: Actual hash value
        algorithm: Algorithm used
        file_path: File path
        error_message: Error if failed
    """
    success: bool
    expected_hash: str
    actual_hash: str
    algorithm: HashAlgorithm
    file_path: Optional[Path] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "expected_hash": self.expected_hash,
            "actual_hash": self.actual_hash,
            "algorithm": self.algorithm.value,
            "file_path": str(self.file_path) if self.file_path else None,
            "error_message": self.error_message,
        }


@dataclass
class EncryptionResult:
    """
    Encryption operation result.
    
    Attributes:
        success: Whether encryption succeeded
        encrypted_data: Encrypted data (bytes or path)
        iv: Initialization vector
        algorithm: Algorithm used
        error_message: Error if failed
    """
    success: bool
    encrypted_data: Optional[bytes] = None
    output_path: Optional[Path] = None
    iv: Optional[bytes] = None
    algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "output_path": str(self.output_path) if self.output_path else None,
            "algorithm": self.algorithm.value,
            "error_message": self.error_message,
        }


@dataclass
class URLValidationResult:
    """
    URL validation result.
    
    Attributes:
        url: Original URL
        is_valid: Whether URL is valid
        is_safe: Whether URL is considered safe
        domain: Extracted domain
        threat_level: Assessed threat level
        warnings: List of warnings
        redirect_url: Final URL after redirects
        ssl_valid: Whether SSL certificate is valid
    """
    url: str
    is_valid: bool
    is_safe: bool = True
    domain: Optional[str] = None
    threat_level: ThreatLevel = ThreatLevel.SAFE
    warnings: List[str] = field(default_factory=list)
    redirect_url: Optional[str] = None
    ssl_valid: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "is_valid": self.is_valid,
            "is_safe": self.is_safe,
            "domain": self.domain,
            "threat_level": self.threat_level.value,
            "warnings": self.warnings,
            "redirect_url": self.redirect_url,
            "ssl_valid": self.ssl_valid,
        }


@dataclass
class FileIntegrityReport:
    """
    File integrity report.
    
    Attributes:
        file_path: File path
        exists: Whether file exists
        size: File size
        hashes: Calculated hashes
        last_modified: Last modification time
        permissions: File permissions
        is_readable: Whether file is readable
        is_writable: Whether file is writable
    """
    file_path: Path
    exists: bool = False
    size: int = 0
    hashes: Dict[str, str] = field(default_factory=dict)
    last_modified: Optional[datetime] = None
    permissions: Optional[str] = None
    is_readable: bool = False
    is_writable: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": str(self.file_path),
            "exists": self.exists,
            "size": self.size,
            "hashes": self.hashes,
            "last_modified": self.last_modified.isoformat() if self.last_modified else None,
            "permissions": self.permissions,
            "is_readable": self.is_readable,
            "is_writable": self.is_writable,
        }


class SecurityTools:
    """
    OMNIPOTENT SOVEREIGN NEXUS Security Tools.
    
    Comprehensive security utilities with:
    - Hash calculation and verification
    - Encryption/Decryption
    - URL validation
    - File integrity
    - Secure deletion
    """
    
    # Known malicious domains (placeholder - would be from threat intel)
    MALICIOUS_DOMAINS = {
        "malware-domain.com",
        "phishing-site.net",
        "suspicious-url.org",
    }
    
    # Suspicious URL patterns
    SUSPICIOUS_PATTERNS = [
        r'\.exe$',
        r'\.scr$',
        r'\.bat$',
        r'\.cmd$',
        r'\.ps1$',
        r'\.vbs$',
        r'\.jar$',
        r'password',
        r'login',
        r'account',
        r'verify',
        r'secure',
        r'update',
    ]
    
    def __init__(
        self,
        security_level: SecurityLevel = SecurityLevel.MEDIUM,
    ) -> None:
        """
        Initialize security tools.
        
        Args:
            security_level: Security level preset
        """
        self.security_level = security_level
        self._fernet_key: Optional[bytes] = None
        
        logger.info(f"SecurityTools initialized v3.0.1 ULTIMATE NEXUS")
    
    async def calculate_hash(
        self,
        data: Union[bytes, str, Path],
        algorithm: HashAlgorithm = HashAlgorithm.SHA256,
        chunk_size: int = 65536,
    ) -> HashResult:
        """
        Calculate hash of data or file.
        
        Args:
            data: Data bytes, string, or file path
            algorithm: Hash algorithm
            chunk_size: Chunk size for file hashing
            
        Returns:
            HashResult
        """
        start_time = datetime.now()
        
        try:
            hasher = hashlib.new(algorithm.value)
            file_path = None
            data_size = 0
            
            if isinstance(data, Path):
                file_path = data
                
                if not data.exists():
                    raise FileNotFoundError(f"File not found: {data}")
                
                async with aiofiles.open(data, 'rb') as f:
                    while chunk := await f.read(chunk_size):
                        hasher.update(chunk)
                        data_size += len(chunk)
            
            elif isinstance(data, str):
                data_bytes = data.encode('utf-8')
                hasher.update(data_bytes)
                data_size = len(data_bytes)
            
            else:  # bytes
                hasher.update(data)
                data_size = len(data)
            
            hash_value = hasher.hexdigest()
            calculation_time = (datetime.now() - start_time).total_seconds()
            
            return HashResult(
                algorithm=algorithm,
                hash_value=hash_value,
                file_path=file_path,
                data_size=data_size,
                calculation_time=calculation_time,
            )
            
        except Exception as e:
            logger.error(f"Hash calculation error: {e}")
            return HashResult(
                algorithm=algorithm,
                hash_value="",
            )
    
    async def verify_hash(
        self,
        data: Union[bytes, str, Path],
        expected_hash: str,
        algorithm: HashAlgorithm = HashAlgorithm.SHA256,
    ) -> VerificationResult:
        """
        Verify data against expected hash.
        
        Args:
            data: Data to verify
            expected_hash: Expected hash value
            algorithm: Hash algorithm
            
        Returns:
            VerificationResult
        """
        try:
            result = await self.calculate_hash(data, algorithm)
            
            success = result.hash_value.lower() == expected_hash.lower()
            
            return VerificationResult(
                success=success,
                expected_hash=expected_hash,
                actual_hash=result.hash_value,
                algorithm=algorithm,
                file_path=result.file_path,
                error_message=None if success else "Hash mismatch",
            )
            
        except Exception as e:
            return VerificationResult(
                success=False,
                expected_hash=expected_hash,
                actual_hash="",
                algorithm=algorithm,
                error_message=str(e),
            )
    
    async def calculate_multiple_hashes(
        self,
        file_path: Path,
        algorithms: Optional[List[HashAlgorithm]] = None,
    ) -> Dict[str, str]:
        """
        Calculate multiple hashes for a file.
        
        Args:
            file_path: File path
            algorithms: List of algorithms (default: MD5, SHA1, SHA256)
            
        Returns:
            Dictionary of algorithm -> hash
        """
        algorithms = algorithms or [
            HashAlgorithm.MD5,
            HashAlgorithm.SHA1,
            HashAlgorithm.SHA256,
        ]
        
        results = {}
        
        for algorithm in algorithms:
            result = await self.calculate_hash(file_path, algorithm)
            results[algorithm.value] = result.hash_value
        
        return results
    
    def generate_encryption_key(
        self,
        password: Optional[str] = None,
        salt: Optional[bytes] = None,
    ) -> bytes:
        """
        Generate encryption key.
        
        Args:
            password: Password for key derivation
            salt: Salt for key derivation
            
        Returns:
            Encryption key
        """
        if password:
            salt = salt or os.urandom(16)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend(),
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        else:
            key = Fernet.generate_key()
        
        return key
    
    async def encrypt_data(
        self,
        data: Union[bytes, str],
        key: Optional[bytes] = None,
        algorithm: EncryptionAlgorithm = EncryptionAlgorithm.FERNET,
    ) -> EncryptionResult:
        """
        Encrypt data.
        
        Args:
            data: Data to encrypt
            key: Encryption key (generates if None)
            algorithm: Encryption algorithm
            
        Returns:
            EncryptionResult
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            if algorithm == EncryptionAlgorithm.FERNET:
                key = key or Fernet.generate_key()
                fernet = Fernet(key)
                encrypted = fernet.encrypt(data)
                
                return EncryptionResult(
                    success=True,
                    encrypted_data=encrypted,
                    algorithm=algorithm,
                )
            
            else:
                # AES encryption
                from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
                
                key = key or secrets.token_bytes(32 if algorithm == EncryptionAlgorithm.AES_256 else 16)
                iv = secrets.token_bytes(16)
                
                cipher = Cipher(
                    algorithms.AES(key[:32] if algorithm == EncryptionAlgorithm.AES_256 else key[:16]),
                    modes.CBC(iv),
                    backend=default_backend(),
                )
                
                # Pad data
                block_size = 16
                padding_length = block_size - (len(data) % block_size)
                padded_data = data + bytes([padding_length] * padding_length)
                
                encryptor = cipher.encryptor()
                encrypted = encryptor.update(padded_data) + encryptor.finalize()
                
                return EncryptionResult(
                    success=True,
                    encrypted_data=encrypted,
                    iv=iv,
                    algorithm=algorithm,
                )
                
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return EncryptionResult(
                success=False,
                algorithm=algorithm,
                error_message=str(e),
            )
    
    async def decrypt_data(
        self,
        encrypted_data: bytes,
        key: bytes,
        iv: Optional[bytes] = None,
        algorithm: EncryptionAlgorithm = EncryptionAlgorithm.FERNET,
    ) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Encrypted data
            key: Decryption key
            iv: Initialization vector (for AES)
            algorithm: Encryption algorithm
            
        Returns:
            Tuple of (success, decrypted_data, error_message)
        """
        try:
            if algorithm == EncryptionAlgorithm.FERNET:
                fernet = Fernet(key)
                decrypted = fernet.decrypt(encrypted_data)
                return True, decrypted, None
            
            else:
                if not iv:
                    return False, None, "IV required for AES decryption"
                
                from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
                
                cipher = Cipher(
                    algorithms.AES(key[:32] if algorithm == EncryptionAlgorithm.AES_256 else key[:16]),
                    modes.CBC(iv),
                    backend=default_backend(),
                )
                
                decryptor = cipher.decryptor()
                padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
                
                # Remove padding
                padding_length = padded_data[-1]
                decrypted = padded_data[:-padding_length]
                
                return True, decrypted, None
                
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return False, None, str(e)
    
    async def encrypt_file(
        self,
        file_path: Path,
        output_path: Optional[Path] = None,
        key: Optional[bytes] = None,
        algorithm: EncryptionAlgorithm = EncryptionAlgorithm.FERNET,
    ) -> EncryptionResult:
        """
        Encrypt a file.
        
        Args:
            file_path: Input file path
            output_path: Output file path
            key: Encryption key
            algorithm: Encryption algorithm
            
        Returns:
            EncryptionResult
        """
        try:
            if not file_path.exists():
                return EncryptionResult(
                    success=False,
                    algorithm=algorithm,
                    error_message="File not found",
                )
            
            output_path = output_path or file_path.with_suffix(file_path.suffix + ".encrypted")
            key = key or Fernet.generate_key()
            
            async with aiofiles.open(file_path, 'rb') as f:
                data = await f.read()
            
            result = await self.encrypt_data(data, key, algorithm)
            
            if result.success and result.encrypted_data:
                async with aiofiles.open(output_path, 'wb') as f:
                    await f.write(result.encrypted_data)
                
                result.output_path = output_path
            
            return result
            
        except Exception as e:
            return EncryptionResult(
                success=False,
                algorithm=algorithm,
                error_message=str(e),
            )
    
    async def secure_delete(
        self,
        file_path: Path,
        passes: int = 3,
    ) -> bool:
        """
        Securely delete a file.
        
        Args:
            file_path: File to delete
            passes: Number of overwrite passes
            
        Returns:
            True if successful
        """
        try:
            if not file_path.exists():
                return False
            
            file_size = file_path.stat().st_size
            
            # Overwrite with random data
            for _ in range(passes):
                random_data = secrets.token_bytes(file_size)
                
                async with aiofiles.open(file_path, 'wb') as f:
                    await f.write(random_data)
                
                # Sync to disk
                if hasattr(os, 'fsync'):
                    with open(file_path, 'rb') as sf:
                        os.fsync(sf.fileno())
            
            # Delete file
            file_path.unlink()
            
            logger.info(f"Securely deleted: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Secure delete error: {e}")
            return False
    
    def validate_url(
        self,
        url: str,
        check_ssl: bool = True,
        follow_redirects: bool = True,
    ) -> URLValidationResult:
        """
        Validate and assess URL safety.
        
        Args:
            url: URL to validate
            check_ssl: Whether to check SSL
            follow_redirects: Whether to follow redirects
            
        Returns:
            URLValidationResult
        """
        result = URLValidationResult(url=url, is_valid=False)
        
        try:
            # Parse URL
            parsed = urlparse(url)
            
            if not parsed.scheme or not parsed.netloc:
                result.warnings.append("Invalid URL format")
                return result
            
            result.domain = parsed.netloc.lower()
            result.is_valid = True
            
            # Check for malicious domain
            if result.domain in self.MALICIOUS_DOMAINS:
                result.is_safe = False
                result.threat_level = ThreatLevel.HIGH
                result.warnings.append("Domain flagged as malicious")
            
            # Check for suspicious patterns
            for pattern in self.SUSPICIOUS_PATTERNS:
                if re.search(pattern, url, re.IGNORECASE):
                    result.warnings.append(f"Suspicious pattern detected: {pattern}")
                    
                    if result.threat_level == ThreatLevel.SAFE:
                        result.threat_level = ThreatLevel.LOW
            
            # Check SSL
            if check_ssl and parsed.scheme == 'https':
                try:
                    context = ssl.create_default_context()
                    with socket.create_connection((parsed.netloc, 443), timeout=5) as sock:
                        with context.wrap_socket(sock, server_hostname=parsed.netloc) as ssock:
                            result.ssl_valid = True
                except Exception:
                    result.ssl_valid = False
                    result.warnings.append("SSL certificate validation failed")
            
            # Assess threat level
            if len(result.warnings) >= 3:
                result.threat_level = ThreatLevel.HIGH
                result.is_safe = False
            elif len(result.warnings) >= 1:
                result.threat_level = ThreatLevel.MEDIUM
            
        except Exception as e:
            result.warnings.append(f"Validation error: {e}")
        
        return result
    
    def sanitize_filename(
        self,
        filename: str,
        max_length: int = 255,
        replacement: str = "_",
    ) -> str:
        """
        Sanitize filename for safe filesystem use.
        
        Args:
            filename: Original filename
            max_length: Maximum length
            replacement: Replacement character
            
        Returns:
            Sanitized filename
        """
        if not filename:
            return "unnamed"
        
        # Remove null bytes
        filename = filename.replace('\x00', '')
        
        # Remove or replace invalid characters
        invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
        filename = re.sub(invalid_chars, replacement, filename)
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        
        # Handle reserved names (Windows)
        reserved = {
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
        }
        
        name_without_ext = filename.rsplit('.', 1)[0].upper()
        if name_without_ext in reserved:
            filename = f"_{filename}"
        
        # Truncate if too long
        if len(filename) > max_length:
            name, ext = os.path.splitext(filename)
            max_name = max_length - len(ext)
            filename = name[:max_name] + ext
        
        return filename or "unnamed"
    
    async def check_file_integrity(
        self,
        file_path: Path,
        algorithms: Optional[List[HashAlgorithm]] = None,
    ) -> FileIntegrityReport:
        """
        Check file integrity.
        
        Args:
            file_path: File path
            algorithms: Hash algorithms to use
            
        Returns:
            FileIntegrityReport
        """
        report = FileIntegrityReport(file_path=file_path)
        
        try:
            if not file_path.exists():
                return report
            
            stat = file_path.stat()
            
            report.exists = True
            report.size = stat.st_size
            report.last_modified = datetime.fromtimestamp(stat.st_mtime)
            report.permissions = oct(stat.st_mode)[-3:]
            report.is_readable = os.access(file_path, os.R_OK)
            report.is_writable = os.access(file_path, os.W_OK)
            
            # Calculate hashes
            algorithms = algorithms or [HashAlgorithm.MD5, HashAlgorithm.SHA256]
            
            for algorithm in algorithms:
                result = await self.calculate_hash(file_path, algorithm)
                report.hashes[algorithm.value] = result.hash_value
            
        except Exception as e:
            logger.error(f"File integrity check error: {e}")
        
        return report
    
    def generate_secure_token(
        self,
        length: int = 32,
    ) -> str:
        """
        Generate secure random token.
        
        Args:
            length: Token length in bytes
            
        Returns:
            Secure token string
        """
        return secrets.token_hex(length)
    
    def generate_password(
        self,
        length: int = 16,
        include_special: bool = True,
    ) -> str:
        """
        Generate secure password.
        
        Args:
            length: Password length
            include_special: Include special characters
            
        Returns:
            Generated password
        """
        import string
        
        characters = string.ascii_letters + string.digits
        if include_special:
            characters += "!@#$%^&*()-_=+"
        
        password = ''.join(secrets.choice(characters) for _ in range(length))
        
        return password
    
    def secure_compare(
        self,
        a: str,
        b: str,
    ) -> bool:
        """
        Timing-attack safe string comparison.
        
        Args:
            a: First string
            b: Second string
            
        Returns:
            True if equal
        """
        return hmac.compare_digest(a.encode(), b.encode())


# Convenience functions
async def hash_file(
    file_path: str,
    algorithm: HashAlgorithm = HashAlgorithm.SHA256,
) -> str:
    """
    Quick file hash function.
    
    Args:
        file_path: File path
        algorithm: Hash algorithm
        
    Returns:
        Hash value
    """
    security = SecurityTools()
    result = await security.calculate_hash(Path(file_path), algorithm)
    return result.hash_value


async def verify_file_hash(
    file_path: str,
    expected_hash: str,
    algorithm: HashAlgorithm = HashAlgorithm.SHA256,
) -> bool:
    """
    Quick hash verification function.
    
    Args:
        file_path: File path
        expected_hash: Expected hash
        algorithm: Hash algorithm
        
    Returns:
        True if verified
    """
    security = SecurityTools()
    result = await security.verify_hash(Path(file_path), expected_hash, algorithm)
    return result.success


# Export all public classes and functions
__all__ = [
    "SecurityTools",
    "HashAlgorithm",
    "EncryptionAlgorithm",
    "SecurityLevel",
    "ThreatLevel",
    "HashResult",
    "VerificationResult",
    "EncryptionResult",
    "URLValidationResult",
    "FileIntegrityReport",
    "hash_file",
    "verify_file_hash",
]

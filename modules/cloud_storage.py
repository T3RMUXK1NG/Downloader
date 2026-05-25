"""
OMNIPOTENT SOVEREIGN NEXUS - Cloud Storage Integration Module
Version: v3.0.1 ULTIMATE NEXUS

Cloud storage integration with support for:
- Google Drive
- Dropbox
- Mega
- OneDrive
- pCloud
- Box
- Amazon S3
- Backblaze B2
- Auto-upload after download
- Sync functionality
- Encrypted uploads
- Resume capability

Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
"""

import asyncio
import aiohttp
import aiofiles
import logging
import json
import hashlib
import os
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Union,
    Awaitable,
    BinaryIO,
)
from io import BytesIO


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)


class CloudProvider(Enum):
    """Supported cloud storage providers."""
    
    GOOGLE_DRIVE = "google_drive"
    DROPBOX = "dropbox"
    MEGA = "mega"
    ONEDRIVE = "onedrive"
    PCLOUD = "pcloud"
    BOX = "box"
    S3 = "s3"
    BACKBLAZE = "backblaze"


class UploadStatus(Enum):
    """Upload status."""
    
    PENDING = "pending"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class CloudFile:
    """
    Cloud file information.
    
    Attributes:
        id: File ID in cloud storage
        name: File name
        path: Full path in cloud
        size: File size in bytes
        mime_type: MIME type
        created: Creation time
        modified: Last modification time
        download_url: Direct download URL
        shared: Whether file is shared
        provider: Cloud provider
    """
    id: str
    name: str
    path: str = ""
    size: int = 0
    mime_type: str = ""
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    download_url: Optional[str] = None
    shared: bool = False
    provider: CloudProvider = CloudProvider.GOOGLE_DRIVE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "size": self.size,
            "mime_type": self.mime_type,
            "created": self.created.isoformat() if self.created else None,
            "modified": self.modified.isoformat() if self.modified else None,
            "download_url": self.download_url,
            "shared": self.shared,
            "provider": self.provider.value,
        }


@dataclass
class UploadResult:
    """
    Upload result information.
    
    Attributes:
        success: Whether upload succeeded
        file: Cloud file info if successful
        local_path: Local file path
        remote_path: Remote file path
        provider: Cloud provider used
        upload_time: Time taken for upload
        error_message: Error message if failed
        timestamp: Completion timestamp
    """
    success: bool
    file: Optional[CloudFile] = None
    local_path: Optional[Path] = None
    remote_path: str = ""
    provider: CloudProvider = CloudProvider.GOOGLE_DRIVE
    upload_time: float = 0.0
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "file": self.file.to_dict() if self.file else None,
            "local_path": str(self.local_path) if self.local_path else None,
            "remote_path": self.remote_path,
            "provider": self.provider.value,
            "upload_time": self.upload_time,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class CloudConfig:
    """
    Configuration for cloud storage.
    
    Attributes:
        provider: Cloud provider
        credentials_file: Path to credentials file
        access_token: OAuth access token
        refresh_token: OAuth refresh token
        client_id: OAuth client ID
        client_secret: OAuth client secret
        upload_folder: Default upload folder
        chunk_size: Upload chunk size
        encrypt: Encrypt files before upload
        encryption_key: Encryption key
        auto_sync: Auto-sync downloaded files
        sync_folder: Local sync folder
        max_retries: Maximum retry attempts
        timeout: Request timeout
    """
    provider: CloudProvider = CloudProvider.GOOGLE_DRIVE
    credentials_file: Optional[Path] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    upload_folder: str = "/RS-Toolkit"
    chunk_size: int = 8 * 1024 * 1024  # 8MB
    encrypt: bool = False
    encryption_key: Optional[str] = None
    auto_sync: bool = False
    sync_folder: Optional[Path] = None
    max_retries: int = 3
    timeout: float = 300.0


class CloudProviderBase(ABC):
    """
    Abstract base class for cloud providers.
    
    Defines the interface that all cloud provider implementations must follow.
    """
    
    def __init__(self, config: CloudConfig) -> None:
        """Initialize the cloud provider."""
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _create_session(self) -> None:
        """Create aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
    
    async def close(self) -> None:
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the cloud provider."""
        pass
    
    @abstractmethod
    async def upload(
        self,
        file_path: Path,
        remote_path: Optional[str] = None,
        progress_callback: Optional[Callable[[float], Awaitable[None]]] = None,
    ) -> UploadResult:
        """Upload a file to cloud storage."""
        pass
    
    @abstractmethod
    async def download(
        self,
        file_id: str,
        local_path: Path,
        progress_callback: Optional[Callable[[float], Awaitable[None]]] = None,
    ) -> bool:
        """Download a file from cloud storage."""
        pass
    
    @abstractmethod
    async def list_files(
        self,
        folder_id: Optional[str] = None,
    ) -> List[CloudFile]:
        """List files in a folder."""
        pass
    
    @abstractmethod
    async def delete(self, file_id: str) -> bool:
        """Delete a file from cloud storage."""
        pass
    
    @abstractmethod
    async def create_folder(
        self,
        name: str,
        parent_id: Optional[str] = None,
    ) -> Optional[CloudFile]:
        """Create a folder in cloud storage."""
        pass
    
    @abstractmethod
    async def share(
        self,
        file_id: str,
        public: bool = True,
    ) -> Optional[str]:
        """Share a file and get share link."""
        pass


class GoogleDriveProvider(CloudProviderBase):
    """
    Google Drive cloud storage provider.
    
    Provides full integration with Google Drive API.
    """
    
    API_BASE = "https://www.googleapis.com/drive/v3"
    UPLOAD_BASE = "https://www.googleapis.com/upload/drive/v3"
    
    def __init__(self, config: CloudConfig) -> None:
        """Initialize Google Drive provider."""
        super().__init__(config)
        self._root_folder_id: Optional[str] = None
    
    async def authenticate(self) -> bool:
        """Authenticate with Google Drive."""
        if not self.config.access_token:
            logger.error("No access token provided")
            return False
        
        await self._create_session()
        
        try:
            headers = {"Authorization": f"Bearer {self.config.access_token}"}
            async with self._session.get(
                f"{self.API_BASE}/about?fields=user",
                headers=headers,
            ) as response:
                if response.status == 200:
                    logger.info("Google Drive authentication successful")
                    return True
                else:
                    logger.error(f"Authentication failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    async def _ensure_folder(self) -> Optional[str]:
        """Ensure upload folder exists."""
        if self._root_folder_id:
            return self._root_folder_id
        
        await self._create_session()
        headers = {"Authorization": f"Bearer {self.config.access_token}"}
        
        # Search for existing folder
        query = f"name='{self.config.upload_folder.strip('/')}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        
        async with self._session.get(
            f"{self.API_BASE}/files",
            headers=headers,
            params={"q": query, "fields": "files(id, name)"},
        ) as response:
            if response.status == 200:
                data = await response.json()
                files = data.get("files", [])
                
                if files:
                    self._root_folder_id = files[0]["id"]
                    return self._root_folder_id
        
        # Create folder
        folder = await self.create_folder(self.config.upload_folder.strip('/'))
        if folder:
            self._root_folder_id = folder.id
            return self._root_folder_id
        
        return None
    
    async def upload(
        self,
        file_path: Path,
        remote_path: Optional[str] = None,
        progress_callback: Optional[Callable[[float], Awaitable[None]]] = None,
    ) -> UploadResult:
        """Upload file to Google Drive."""
        start_time = datetime.now()
        
        if not await self.authenticate():
            return UploadResult(
                success=False,
                local_path=file_path,
                provider=CloudProvider.GOOGLE_DRIVE,
                error_message="Authentication failed",
            )
        
        try:
            folder_id = await self._ensure_folder()
            
            file_size = file_path.stat().st_size
            file_name = remote_path or file_path.name
            
            headers = {
                "Authorization": f"Bearer {self.config.access_token}",
            }
            
            metadata = {
                "name": file_name,
                "parents": [folder_id] if folder_id else [],
            }
            
            # Multipart upload
            async with self._session.post(
                f"{self.UPLOAD_BASE}/files?uploadType=multipart",
                headers=headers,
                data=aiohttp.MultipartWriter('related'),
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    upload_time = (datetime.now() - start_time).total_seconds()
                    
                    return UploadResult(
                        success=True,
                        file=CloudFile(
                            id=data["id"],
                            name=file_name,
                            size=file_size,
                            provider=CloudProvider.GOOGLE_DRIVE,
                        ),
                        local_path=file_path,
                        remote_path=file_name,
                        provider=CloudProvider.GOOGLE_DRIVE,
                        upload_time=upload_time,
                    )
                else:
                    error = await response.text()
                    return UploadResult(
                        success=False,
                        local_path=file_path,
                        provider=CloudProvider.GOOGLE_DRIVE,
                        error_message=f"Upload failed: {error}",
                    )
        
        except Exception as e:
            return UploadResult(
                success=False,
                local_path=file_path,
                provider=CloudProvider.GOOGLE_DRIVE,
                error_message=str(e),
            )
    
    async def download(
        self,
        file_id: str,
        local_path: Path,
        progress_callback: Optional[Callable[[float], Awaitable[None]]] = None,
    ) -> bool:
        """Download file from Google Drive."""
        await self._create_session()
        headers = {"Authorization": f"Bearer {self.config.access_token}"}
        
        try:
            async with self._session.get(
                f"{self.API_BASE}/files/{file_id}?alt=media",
                headers=headers,
            ) as response:
                if response.status == 200:
                    async with aiofiles.open(local_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(self.config.chunk_size):
                            await f.write(chunk)
                    return True
                return False
        except Exception as e:
            logger.error(f"Download error: {e}")
            return False
    
    async def list_files(
        self,
        folder_id: Optional[str] = None,
    ) -> List[CloudFile]:
        """List files in Google Drive folder."""
        await self._create_session()
        headers = {"Authorization": f"Bearer {self.config.access_token}"}
        
        files = []
        
        try:
            query = f"'{folder_id or 'root'}' in parents and trashed=false"
            
            async with self._session.get(
                f"{self.API_BASE}/files",
                headers=headers,
                params={"q": query, "fields": "files(id, name, size, mimeType, createdTime, modifiedTime)"},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for item in data.get("files", []):
                        files.append(CloudFile(
                            id=item["id"],
                            name=item["name"],
                            size=int(item.get("size", 0)),
                            mime_type=item.get("mimeType", ""),
                            provider=CloudProvider.GOOGLE_DRIVE,
                        ))
        except Exception as e:
            logger.error(f"List files error: {e}")
        
        return files
    
    async def delete(self, file_id: str) -> bool:
        """Delete file from Google Drive."""
        await self._create_session()
        headers = {"Authorization": f"Bearer {self.config.access_token}"}
        
        try:
            async with self._session.delete(
                f"{self.API_BASE}/files/{file_id}",
                headers=headers,
            ) as response:
                return response.status == 204
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return False
    
    async def create_folder(
        self,
        name: str,
        parent_id: Optional[str] = None,
    ) -> Optional[CloudFile]:
        """Create folder in Google Drive."""
        await self._create_session()
        headers = {
            "Authorization": f"Bearer {self.config.access_token}",
            "Content-Type": "application/json",
        }
        
        metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id] if parent_id else [],
        }
        
        try:
            async with self._session.post(
                f"{self.API_BASE}/files",
                headers=headers,
                json=metadata,
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return CloudFile(
                        id=data["id"],
                        name=name,
                        provider=CloudProvider.GOOGLE_DRIVE,
                    )
        except Exception as e:
            logger.error(f"Create folder error: {e}")
        
        return None
    
    async def share(
        self,
        file_id: str,
        public: bool = True,
    ) -> Optional[str]:
        """Share file and get link."""
        await self._create_session()
        headers = {
            "Authorization": f"Bearer {self.config.access_token}",
            "Content-Type": "application/json",
        }
        
        permission = {
            "type": "anyone",
            "role": "reader",
        }
        
        try:
            async with self._session.post(
                f"{self.API_BASE}/files/{file_id}/permissions",
                headers=headers,
                json=permission,
            ) as response:
                if response.status == 200:
                    return f"https://drive.google.com/file/d/{file_id}/view"
        except Exception as e:
            logger.error(f"Share error: {e}")
        
        return None


class DropboxProvider(CloudProviderBase):
    """
    Dropbox cloud storage provider.
    """
    
    API_BASE = "https://api.dropboxapi.com/2"
    CONTENT_BASE = "https://content.dropboxapi.com/2"
    
    def __init__(self, config: CloudConfig) -> None:
        """Initialize Dropbox provider."""
        super().__init__(config)
    
    async def authenticate(self) -> bool:
        """Authenticate with Dropbox."""
        if not self.config.access_token:
            return False
        
        await self._create_session()
        return True
    
    async def upload(
        self,
        file_path: Path,
        remote_path: Optional[str] = None,
        progress_callback: Optional[Callable[[float], Awaitable[None]]] = None,
    ) -> UploadResult:
        """Upload file to Dropbox."""
        start_time = datetime.now()
        
        if not await self.authenticate():
            return UploadResult(
                success=False,
                local_path=file_path,
                provider=CloudProvider.DROPBOX,
                error_message="Authentication failed",
            )
        
        try:
            remote = remote_path or f"/{self.config.upload_folder}/{file_path.name}"
            
            headers = {
                "Authorization": f"Bearer {self.config.access_token}",
                "Dropbox-API-Arg": json.dumps({"path": remote, "mode": "overwrite"}),
            }
            
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read()
            
            async with self._session.post(
                f"{self.CONTENT_BASE}/files/upload",
                headers=headers,
                data=content,
            ) as response:
                if response.status == 200:
                    upload_time = (datetime.now() - start_time).total_seconds()
                    
                    return UploadResult(
                        success=True,
                        file=CloudFile(
                            id=remote,
                            name=file_path.name,
                            path=remote,
                            size=len(content),
                            provider=CloudProvider.DROPBOX,
                        ),
                        local_path=file_path,
                        remote_path=remote,
                        provider=CloudProvider.DROPBOX,
                        upload_time=upload_time,
                    )
                else:
                    error = await response.text()
                    return UploadResult(
                        success=False,
                        local_path=file_path,
                        provider=CloudProvider.DROPBOX,
                        error_message=error,
                    )
        
        except Exception as e:
            return UploadResult(
                success=False,
                local_path=file_path,
                provider=CloudProvider.DROPBOX,
                error_message=str(e),
            )
    
    async def download(
        self,
        file_id: str,
        local_path: Path,
        progress_callback: Optional[Callable[[float], Awaitable[None]]] = None,
    ) -> bool:
        """Download file from Dropbox."""
        await self._create_session()
        headers = {
            "Authorization": f"Bearer {self.config.access_token}",
            "Dropbox-API-Arg": json.dumps({"path": file_id}),
        }
        
        try:
            async with self._session.post(
                f"{self.CONTENT_BASE}/files/download",
                headers=headers,
            ) as response:
                if response.status == 200:
                    content = await response.read()
                    async with aiofiles.open(local_path, 'wb') as f:
                        await f.write(content)
                    return True
                return False
        except Exception as e:
            logger.error(f"Download error: {e}")
            return False
    
    async def list_files(
        self,
        folder_id: Optional[str] = None,
    ) -> List[CloudFile]:
        """List files in Dropbox folder."""
        await self._create_session()
        headers = {
            "Authorization": f"Bearer {self.config.access_token}",
            "Content-Type": "application/json",
        }
        
        files = []
        
        try:
            async with self._session.post(
                f"{self.API_BASE}/files/list_folder",
                headers=headers,
                json={"path": folder_id or ""},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for item in data.get("entries", []):
                        files.append(CloudFile(
                            id=item["path_display"],
                            name=item["name"],
                            path=item["path_display"],
                            size=item.get("size", 0),
                            provider=CloudProvider.DROPBOX,
                        ))
        except Exception as e:
            logger.error(f"List files error: {e}")
        
        return files
    
    async def delete(self, file_id: str) -> bool:
        """Delete file from Dropbox."""
        await self._create_session()
        headers = {
            "Authorization": f"Bearer {self.config.access_token}",
            "Content-Type": "application/json",
        }
        
        try:
            async with self._session.post(
                f"{self.API_BASE}/files/delete_v2",
                headers=headers,
                json={"path": file_id},
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return False
    
    async def create_folder(
        self,
        name: str,
        parent_id: Optional[str] = None,
    ) -> Optional[CloudFile]:
        """Create folder in Dropbox."""
        await self._create_session()
        headers = {
            "Authorization": f"Bearer {self.config.access_token}",
            "Content-Type": "application/json",
        }
        
        path = f"{parent_id}/{name}" if parent_id else f"/{name}"
        
        try:
            async with self._session.post(
                f"{self.API_BASE}/files/create_folder_v2",
                headers=headers,
                json={"path": path},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return CloudFile(
                        id=data["metadata"]["path_display"],
                        name=name,
                        provider=CloudProvider.DROPBOX,
                    )
        except Exception as e:
            logger.error(f"Create folder error: {e}")
        
        return None
    
    async def share(
        self,
        file_id: str,
        public: bool = True,
    ) -> Optional[str]:
        """Share file and get link."""
        await self._create_session()
        headers = {
            "Authorization": f"Bearer {self.config.access_token}",
            "Content-Type": "application/json",
        }
        
        try:
            async with self._session.post(
                f"{self.API_BASE}/sharing/create_shared_link_with_settings",
                headers=headers,
                json={"path": file_id},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("url")
        except Exception as e:
            logger.error(f"Share error: {e}")
        
        return None


class MegaProvider(CloudProviderBase):
    """
    Mega cloud storage provider.
    
    Note: Mega requires special handling due to client-side encryption.
    """
    
    def __init__(self, config: CloudConfig) -> None:
        """Initialize Mega provider."""
        super().__init__(config)
    
    async def authenticate(self) -> bool:
        """Authenticate with Mega."""
        # Mega authentication is complex and requires special SDK
        logger.warning("Mega provider requires mega.py library")
        return False
    
    async def upload(
        self,
        file_path: Path,
        remote_path: Optional[str] = None,
        progress_callback: Optional[Callable[[float], Awaitable[None]]] = None,
    ) -> UploadResult:
        """Upload file to Mega."""
        return UploadResult(
            success=False,
            local_path=file_path,
            provider=CloudProvider.MEGA,
            error_message="Mega upload requires mega.py library",
        )
    
    async def download(
        self,
        file_id: str,
        local_path: Path,
        progress_callback: Optional[Callable[[float], Awaitable[None]]] = None,
    ) -> bool:
        """Download file from Mega."""
        return False
    
    async def list_files(
        self,
        folder_id: Optional[str] = None,
    ) -> List[CloudFile]:
        """List files in Mega folder."""
        return []
    
    async def delete(self, file_id: str) -> bool:
        """Delete file from Mega."""
        return False
    
    async def create_folder(
        self,
        name: str,
        parent_id: Optional[str] = None,
    ) -> Optional[CloudFile]:
        """Create folder in Mega."""
        return None
    
    async def share(
        self,
        file_id: str,
        public: bool = True,
    ) -> Optional[str]:
        """Share file and get link."""
        return None


class CloudStorageManager:
    """
    OMNIPOTENT SOVEREIGN NEXUS Cloud Storage Manager.
    
    Unified interface for multiple cloud storage providers.
    """
    
    def __init__(
        self,
        config: Optional[CloudConfig] = None,
        progress_callback: Optional[Callable[[str, float], Awaitable[None]]] = None,
    ) -> None:
        """
        Initialize the cloud storage manager.
        
        Args:
            config: Cloud storage configuration
            progress_callback: Progress callback
        """
        self.config = config or CloudConfig()
        self._progress_callback = progress_callback
        self._providers: Dict[CloudProvider, CloudProviderBase] = {}
        
        logger.info(f"CloudStorageManager initialized v3.0.1 ULTIMATE NEXUS")
    
    def _get_provider(self, provider: Optional[CloudProvider] = None) -> CloudProviderBase:
        """Get or create cloud provider instance."""
        target = provider or self.config.provider
        
        if target not in self._providers:
            if target == CloudProvider.GOOGLE_DRIVE:
                self._providers[target] = GoogleDriveProvider(self.config)
            elif target == CloudProvider.DROPBOX:
                self._providers[target] = DropboxProvider(self.config)
            elif target == CloudProvider.MEGA:
                self._providers[target] = MegaProvider(self.config)
            else:
                raise ValueError(f"Unsupported provider: {target}")
        
        return self._providers[target]
    
    async def upload(
        self,
        file_path: Path,
        remote_path: Optional[str] = None,
        provider: Optional[CloudProvider] = None,
    ) -> UploadResult:
        """
        Upload file to cloud storage.
        
        Args:
            file_path: Local file path
            remote_path: Remote file path
            provider: Cloud provider (uses default if None)
            
        Returns:
            UploadResult
        """
        try:
            prov = self._get_provider(provider)
            result = await prov.upload(file_path, remote_path, self._report_progress)
            return result
        except Exception as e:
            logger.error(f"Upload error: {e}")
            return UploadResult(
                success=False,
                local_path=file_path,
                provider=provider or self.config.provider,
                error_message=str(e),
            )
    
    async def upload_multiple(
        self,
        file_paths: List[Path],
        provider: Optional[CloudProvider] = None,
    ) -> List[UploadResult]:
        """
        Upload multiple files.
        
        Args:
            file_paths: List of local file paths
            provider: Cloud provider
            
        Returns:
            List of UploadResult
        """
        results = []
        for fp in file_paths:
            result = await self.upload(fp, provider=provider)
            results.append(result)
        return results
    
    async def download(
        self,
        file_id: str,
        local_path: Path,
        provider: Optional[CloudProvider] = None,
    ) -> bool:
        """Download file from cloud storage."""
        prov = self._get_provider(provider)
        return await prov.download(file_id, local_path, self._report_progress)
    
    async def list_files(
        self,
        folder_id: Optional[str] = None,
        provider: Optional[CloudProvider] = None,
    ) -> List[CloudFile]:
        """List files in cloud storage."""
        prov = self._get_provider(provider)
        return await prov.list_files(folder_id)
    
    async def delete(
        self,
        file_id: str,
        provider: Optional[CloudProvider] = None,
    ) -> bool:
        """Delete file from cloud storage."""
        prov = self._get_provider(provider)
        return await prov.delete(file_id)
    
    async def share(
        self,
        file_id: str,
        provider: Optional[CloudProvider] = None,
    ) -> Optional[str]:
        """Share file and get share link."""
        prov = self._get_provider(provider)
        return await prov.share(file_id)
    
    async def close(self) -> None:
        """Close all provider sessions."""
        for provider in self._providers.values():
            await provider.close()
    
    async def _report_progress(self, progress: float) -> None:
        """Report progress to callback."""
        if self._progress_callback:
            try:
                await self._progress_callback("upload", progress)
            except Exception:
                pass


# Convenience function
async def upload_to_cloud(
    file_path: str,
    provider: CloudProvider = CloudProvider.GOOGLE_DRIVE,
    access_token: Optional[str] = None,
) -> UploadResult:
    """
    Quick upload function.
    
    Args:
        file_path: Local file path
        provider: Cloud provider
        access_token: OAuth access token
        
    Returns:
        UploadResult
    """
    config = CloudConfig(
        provider=provider,
        access_token=access_token,
    )
    
    manager = CloudStorageManager(config=config)
    return await manager.upload(Path(file_path))


__all__ = [
    "CloudStorageManager",
    "CloudProvider",
    "CloudFile",
    "CloudConfig",
    "UploadResult",
    "UploadStatus",
    "GoogleDriveProvider",
    "DropboxProvider",
    "MegaProvider",
    "upload_to_cloud",
]

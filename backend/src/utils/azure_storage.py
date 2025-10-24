"""Azure Blob Storage operations."""
from azure.storage.blob import BlobServiceClient
from pathlib import Path
from typing import BinaryIO
from ..config import settings


class AzureStorageService:
    """Azure Blob Storage service for PDF storage."""
    
    def __init__(self):
        """Initialize Azure Blob Storage client."""
        if settings.use_azure_storage and settings.azure_storage_connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                settings.azure_storage_connection_string
            )
            self.container_name = settings.azure_storage_container_name
        else:
            self.blob_service_client = None
            self.local_storage_path = Path(settings.local_storage_path)
            self.local_storage_path.mkdir(parents=True, exist_ok=True)
    
    def upload(self, file_content: bytes, blob_path: str) -> str:
        """
        Upload file to Azure Blob Storage or local storage.
        
        Args:
            file_content: File content as bytes
            blob_path: Path within container/storage
            
        Returns:
            Storage URL or local path
        """
        if settings.use_azure_storage:
            return self._upload_to_azure(file_content, blob_path)
        else:
            return self._upload_to_local(file_content, blob_path)
    
    def _upload_to_azure(self, file_content: bytes, blob_path: str) -> str:
        """Upload to Azure Blob Storage."""
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=blob_path
        )
        
        blob_client.upload_blob(file_content, overwrite=True)
        
        return blob_client.url
    
    def _upload_to_local(self, file_content: bytes, blob_path: str) -> str:
        """Upload to local file system."""
        local_path = self.local_storage_path / blob_path
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(local_path, 'wb') as f:
            f.write(file_content)
        
        return str(local_path)
    
    def download(self, blob_path: str) -> bytes:
        """
        Download file from storage.
        
        Args:
            blob_path: Path within container/storage
            
        Returns:
            File content as bytes
        """
        if settings.use_azure_storage:
            return self._download_from_azure(blob_path)
        else:
            return self._download_from_local(blob_path)
    
    def _download_from_azure(self, blob_path: str) -> bytes:
        """Download from Azure Blob Storage."""
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=blob_path
        )
        
        return blob_client.download_blob().readall()
    
    def _download_from_local(self, blob_path: str) -> bytes:
        """Download from local file system."""
        local_path = self.local_storage_path / blob_path
        
        with open(local_path, 'rb') as f:
            return f.read()
    
    def delete(self, blob_path: str) -> None:
        """
        Delete file from storage.
        
        Args:
            blob_path: Path within container/storage
        """
        if settings.use_azure_storage:
            self._delete_from_azure(blob_path)
        else:
            self._delete_from_local(blob_path)
    
    def _delete_from_azure(self, blob_path: str) -> None:
        """Delete from Azure Blob Storage."""
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=blob_path
        )
        
        blob_client.delete_blob()
    
    def _delete_from_local(self, blob_path: str) -> None:
        """Delete from local file system."""
        local_path = self.local_storage_path / blob_path
        
        if local_path.exists():
            local_path.unlink()


# Global storage service instance
storage_service = AzureStorageService()

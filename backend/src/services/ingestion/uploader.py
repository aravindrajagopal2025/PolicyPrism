"""PDF upload service with validation and storage."""
from pathlib import Path
from typing import Dict, BinaryIO
import hashlib
from datetime import datetime


class PDFUploader:
    """Handle PDF document upload, validation, and storage."""
    
    def __init__(self, storage_service):
        """
        Initialize uploader with storage service.
        
        Args:
            storage_service: Storage service (Azure Blob or local)
        """
        self.storage_service = storage_service
    
    def upload_pdf(
        self,
        file: BinaryIO,
        filename: str,
        payer_id: str,
        user_id: str | None = None
    ) -> Dict[str, any]:
        """
        Upload and store a PDF file.
        
        Args:
            file: File object
            filename: Original filename
            payer_id: Payer UUID
            user_id: User UUID who uploaded (optional)
            
        Returns:
            Dictionary with upload metadata
        """
        # Read file content
        file_content = file.read()
        file_size = len(file_content)
        
        # Generate unique storage path
        file_hash = self._calculate_hash(file_content)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        storage_path = f"policies/{payer_id}/{timestamp}_{file_hash[:8]}_{filename}"
        
        # Upload to storage
        storage_url = self.storage_service.upload(
            file_content,
            storage_path
        )
        
        return {
            "storage_path": storage_path,
            "storage_url": storage_url,
            "file_size_bytes": file_size,
            "original_filename": filename,
            "file_hash": file_hash,
            "uploaded_by": user_id,
            "uploaded_at": datetime.utcnow()
        }
    
    def _calculate_hash(self, content: bytes) -> str:
        """Calculate SHA-256 hash of file content."""
        return hashlib.sha256(content).hexdigest()
    
    def validate_pdf(self, file: BinaryIO, max_size_mb: int = 100) -> Dict[str, any]:
        """
        Validate PDF file before upload.
        
        Args:
            file: File object
            max_size_mb: Maximum file size in MB
            
        Returns:
            Validation result dictionary
        """
        errors = []
        warnings = []
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            errors.append(f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds maximum ({max_size_mb}MB)")
        
        if file_size == 0:
            errors.append("File is empty")
        
        # Check PDF magic number
        header = file.read(5)
        file.seek(0)
        
        if not header.startswith(b'%PDF-'):
            errors.append("File is not a valid PDF (invalid header)")
        
        # Check for password protection (basic check)
        content = file.read(1024)  # Read first 1KB
        file.seek(0)
        
        if b'/Encrypt' in content:
            errors.append("PDF appears to be password-protected or encrypted")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "file_size_bytes": file_size
        }

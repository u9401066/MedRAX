"""
Image Storage - In-memory image storage service

Implements ImageStorageProtocol from domain layer.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from medrax.mcp.domain.entities import ImageEntity, ImageFormat


class InMemoryImageStorage:
    """
    In-memory image storage for development/testing.
    
    Implements ImageStorageProtocol for managing image references.
    
    Note: In production, consider using a persistent storage
    like Redis, PostgreSQL, or cloud storage.
    """
    
    def __init__(self):
        """Initialize the storage."""
        self._storage: Dict[str, ImageEntity] = {}
    
    def _detect_format(self, path: Path) -> ImageFormat:
        """Detect image format from file extension."""
        suffix = path.suffix.lower()
        format_map = {
            ".png": ImageFormat.PNG,
            ".jpg": ImageFormat.JPEG,
            ".jpeg": ImageFormat.JPEG,
            ".dcm": ImageFormat.DICOM,
            ".dicom": ImageFormat.DICOM,
        }
        return format_map.get(suffix, ImageFormat.UNKNOWN)
    
    def store(self, image_path: Path) -> ImageEntity:
        """
        Store an image and return its entity.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            ImageEntity with generated ID
        """
        image_id = f"img_{uuid.uuid4().hex[:12]}"
        
        entity = ImageEntity(
            id=image_id,
            path=Path(image_path),
            format=self._detect_format(Path(image_path)),
            created_at=datetime.now(),
        )
        
        self._storage[image_id] = entity
        return entity
    
    def get(self, image_id: str) -> Optional[ImageEntity]:
        """
        Retrieve an image entity by ID.
        
        Args:
            image_id: The image identifier
            
        Returns:
            ImageEntity if found, None otherwise
        """
        return self._storage.get(image_id)
    
    def get_path(self, image_id: str) -> Optional[Path]:
        """
        Get file path for an image ID.
        
        Args:
            image_id: The image identifier
            
        Returns:
            Path if found, None otherwise
        """
        entity = self._storage.get(image_id)
        return entity.path if entity else None
    
    def delete(self, image_id: str) -> bool:
        """
        Delete an image by ID.
        
        Args:
            image_id: The image identifier
            
        Returns:
            True if deleted, False if not found
        """
        if image_id in self._storage:
            del self._storage[image_id]
            return True
        return False
    
    def list_all(self) -> list:
        """List all stored image IDs."""
        return list(self._storage.keys())
    
    def clear(self) -> int:
        """Clear all stored images. Returns count of deleted items."""
        count = len(self._storage)
        self._storage.clear()
        return count

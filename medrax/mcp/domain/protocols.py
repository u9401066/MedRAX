"""
Domain Protocols - Interface definitions for tool implementations

These protocols define the contracts that infrastructure layer must implement.
Using Protocol (structural subtyping) for flexibility.
"""

from abc import abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from medrax.mcp.domain.entities import (
    ClassificationResult,
    DicomMetadata,
    GroundingResult,
    ImageEntity,
    ReportGenerationResult,
    SegmentationResult,
    VQAResult,
)


@runtime_checkable
class ClassifierProtocol(Protocol):
    """Protocol for chest X-ray classification implementations."""
    
    @abstractmethod
    def classify(
        self,
        image_path: Path,
        pathologies: Optional[List[str]] = None,
        threshold: float = 0.5,
    ) -> ClassificationResult:
        """
        Classify chest X-ray for pathologies.
        
        Args:
            image_path: Path to the chest X-ray image
            pathologies: Optional list of specific pathologies to check
            threshold: Confidence threshold for positive findings
            
        Returns:
            ClassificationResult with pathology probabilities
        """
        ...
    
    @property
    @abstractmethod
    def supported_pathologies(self) -> List[str]:
        """List of pathologies this classifier supports."""
        ...


@runtime_checkable
class VQAProtocol(Protocol):
    """Protocol for Visual Question Answering implementations."""
    
    @abstractmethod
    def answer(
        self,
        image_paths: List[Path],
        question: str,
        max_tokens: int = 512,
    ) -> VQAResult:
        """
        Answer questions about chest X-ray images.
        
        Args:
            image_paths: List of image paths to analyze
            question: Natural language question
            max_tokens: Maximum response length
            
        Returns:
            VQAResult with answer text
        """
        ...
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the VQA model."""
        ...


@runtime_checkable
class SegmentationProtocol(Protocol):
    """Protocol for anatomical segmentation implementations."""
    
    @abstractmethod
    def segment(
        self,
        image_path: Path,
        organs: Optional[List[str]] = None,
    ) -> SegmentationResult:
        """
        Segment anatomical structures in chest X-ray.
        
        Args:
            image_path: Path to the chest X-ray image
            organs: Optional list of specific organs to segment
            
        Returns:
            SegmentationResult with organ masks and metrics
        """
        ...
    
    @property
    @abstractmethod
    def supported_organs(self) -> List[str]:
        """List of organs this segmenter supports."""
        ...


@runtime_checkable
class DicomProcessorProtocol(Protocol):
    """Protocol for DICOM file processing implementations."""
    
    @abstractmethod
    def process(
        self,
        dicom_path: Path,
        window_center: Optional[float] = None,
        window_width: Optional[float] = None,
    ) -> tuple[Path, DicomMetadata]:
        """
        Process DICOM file and convert to standard image format.
        
        Args:
            dicom_path: Path to DICOM file
            window_center: Optional window center for display
            window_width: Optional window width for display
            
        Returns:
            Tuple of (output image path, DICOM metadata)
        """
        ...
    
    @abstractmethod
    def extract_metadata(self, dicom_path: Path) -> DicomMetadata:
        """Extract metadata from DICOM file without conversion."""
        ...


@runtime_checkable
class GroundingProtocol(Protocol):
    """Protocol for phrase grounding (finding localization) implementations."""
    
    @abstractmethod
    def ground(
        self,
        image_path: Path,
        phrase: str,
    ) -> GroundingResult:
        """
        Locate findings described by phrase in the image.
        
        Args:
            image_path: Path to the chest X-ray image
            phrase: Description of finding to locate
            
        Returns:
            GroundingResult with bounding boxes
        """
        ...


@runtime_checkable
class ReportGeneratorProtocol(Protocol):
    """Protocol for radiology report generation implementations."""
    
    @abstractmethod
    def generate(
        self,
        image_path: Path,
        indication: Optional[str] = None,
    ) -> ReportGenerationResult:
        """
        Generate radiology report for chest X-ray.
        
        Args:
            image_path: Path to the chest X-ray image
            indication: Optional clinical indication
            
        Returns:
            ReportGenerationResult with generated report
        """
        ...


@runtime_checkable
class ImageStorageProtocol(Protocol):
    """Protocol for image storage/retrieval service."""
    
    @abstractmethod
    def store(self, image_path: Path) -> ImageEntity:
        """Store an image and return its entity."""
        ...
    
    @abstractmethod
    def get(self, image_id: str) -> Optional[ImageEntity]:
        """Retrieve an image entity by ID."""
        ...
    
    @abstractmethod
    def get_path(self, image_id: str) -> Optional[Path]:
        """Get file path for an image ID."""
        ...
    
    @abstractmethod
    def delete(self, image_id: str) -> bool:
        """Delete an image by ID."""
        ...

"""
Application Services - Use case implementations

Services orchestrate infrastructure wrappers and implement business logic.
They handle image ID resolution, validation, and result formatting.
"""

import base64
from pathlib import Path
from typing import Any, Dict, List, Optional

from medrax.mcp.domain.entities import (
    AnalysisStatus,
    ClassificationResult,
    DicomMetadata,
    SegmentationResult,
    VQAResult,
)
from medrax.mcp.domain.exceptions import (
    ImageNotFoundError,
    ValidationError,
    ServiceUnavailableError,
)
from medrax.mcp.infrastructure.classifier import ClassifierWrapper
from medrax.mcp.infrastructure.vqa import VQAWrapper
from medrax.mcp.infrastructure.segmentation import SegmentationWrapper
from medrax.mcp.infrastructure.dicom import DicomWrapper
from medrax.mcp.infrastructure.image_storage import InMemoryImageStorage


class ClassificationService:
    """
    Service for chest X-ray classification.
    
    Orchestrates classifier wrapper with image storage and validation.
    """
    
    def __init__(
        self,
        classifier: ClassifierWrapper,
        image_storage: InMemoryImageStorage,
    ):
        self._classifier = classifier
        self._storage = image_storage
    
    def classify(
        self,
        image_id: str,
        pathologies: Optional[List[str]] = None,
        threshold: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Classify chest X-ray by image ID.
        
        Args:
            image_id: ID of the uploaded image
            pathologies: Optional filter for specific pathologies
            threshold: Confidence threshold for positive findings
            
        Returns:
            Dictionary with classification results
        """
        # Resolve image path
        image_path = self._storage.get_path(image_id)
        if image_path is None:
            raise ImageNotFoundError(image_id=image_id)
        
        # Validate pathologies if specified
        if pathologies:
            supported = set(self._classifier.supported_pathologies)
            invalid = [p for p in pathologies if p not in supported]
            if invalid:
                raise ValidationError(
                    field="pathologies",
                    message=f"Unsupported pathologies: {invalid}. "
                            f"Supported: {list(supported)}",
                    value=invalid,
                )
        
        # Run classification
        result = self._classifier.classify(
            image_path=image_path,
            pathologies=pathologies,
            threshold=threshold,
        )
        
        return result.to_dict()
    
    @property
    def supported_pathologies(self) -> List[str]:
        """List of supported pathologies."""
        return self._classifier.supported_pathologies


class VQAService:
    """
    Service for Visual Question Answering.
    
    Orchestrates VQA wrapper with image storage and validation.
    """
    
    def __init__(
        self,
        vqa: VQAWrapper,
        image_storage: InMemoryImageStorage,
    ):
        self._vqa = vqa
        self._storage = image_storage
    
    def answer(
        self,
        image_ids: List[str],
        question: str,
        max_tokens: int = 512,
    ) -> Dict[str, Any]:
        """
        Answer questions about chest X-ray images.
        
        Args:
            image_ids: List of image IDs to analyze
            question: Natural language question
            max_tokens: Maximum response length
            
        Returns:
            Dictionary with VQA results
        """
        if not image_ids:
            raise ValidationError(
                field="image_ids",
                message="At least one image ID is required",
            )
        
        if not question or not question.strip():
            raise ValidationError(
                field="question",
                message="Question cannot be empty",
            )
        
        # Resolve all image paths
        image_paths = []
        for img_id in image_ids:
            path = self._storage.get_path(img_id)
            if path is None:
                raise ImageNotFoundError(image_id=img_id)
            image_paths.append(path)
        
        # Run VQA
        result = self._vqa.answer(
            image_paths=image_paths,
            question=question.strip(),
            max_tokens=max_tokens,
        )
        
        return result.to_dict()


class SegmentationService:
    """
    Service for anatomical segmentation.
    
    Orchestrates segmentation wrapper with image storage and validation.
    """
    
    def __init__(
        self,
        segmenter: SegmentationWrapper,
        image_storage: InMemoryImageStorage,
    ):
        self._segmenter = segmenter
        self._storage = image_storage
    
    def segment(
        self,
        image_id: str,
        organs: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Segment anatomical structures in chest X-ray.
        
        Args:
            image_id: ID of the uploaded image
            organs: Optional filter for specific organs
            
        Returns:
            Dictionary with segmentation results
        """
        # Resolve image path
        image_path = self._storage.get_path(image_id)
        if image_path is None:
            raise ImageNotFoundError(image_id=image_id)
        
        # Validate organs if specified
        if organs:
            supported = set(self._segmenter.supported_organs)
            invalid = [o for o in organs if o not in supported]
            if invalid:
                raise ValidationError(
                    field="organs",
                    message=f"Unsupported organs: {invalid}. "
                            f"Supported: {list(supported)}",
                    value=invalid,
                )
        
        # Run segmentation
        result = self._segmenter.segment(
            image_path=image_path,
            organs=organs,
        )
        
        return result.to_dict()
    
    @property
    def supported_organs(self) -> List[str]:
        """List of supported organs."""
        return self._segmenter.supported_organs


class DicomService:
    """
    Service for DICOM file processing.
    
    Orchestrates DICOM wrapper with image storage.
    """
    
    def __init__(
        self,
        dicom_processor: DicomWrapper,
        image_storage: InMemoryImageStorage,
    ):
        self._processor = dicom_processor
        self._storage = image_storage
    
    def process(
        self,
        dicom_path: str,
        window_center: Optional[float] = None,
        window_width: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Process DICOM file and convert to standard format.
        
        Args:
            dicom_path: Path to the DICOM file
            window_center: Optional window center for display
            window_width: Optional window width for display
            
        Returns:
            Dictionary with image ID and DICOM metadata
        """
        path = Path(dicom_path)
        if not path.exists():
            raise ImageNotFoundError(image_path=dicom_path)
        
        # Process DICOM
        output_path, metadata = self._processor.process(
            dicom_path=path,
            window_center=window_center,
            window_width=window_width,
        )
        
        # Store the processed image
        entity = self._storage.store(output_path)
        
        # Read and encode image for return
        with open(output_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode("utf-8")
        
        return {
            "image_id": entity.id,
            "image_base64": image_base64,
            "metadata": metadata.to_dict(),
            "original_path": dicom_path,
            "processed_path": str(output_path),
        }
    
    def get_metadata(self, dicom_path: str) -> Dict[str, Any]:
        """
        Extract metadata from DICOM file without conversion.
        
        Args:
            dicom_path: Path to the DICOM file
            
        Returns:
            Dictionary with DICOM metadata
        """
        path = Path(dicom_path)
        if not path.exists():
            raise ImageNotFoundError(image_path=dicom_path)
        
        metadata = self._processor.extract_metadata(path)
        return metadata.to_dict()


class MedRAXServiceContainer:
    """
    Service container for dependency injection.
    
    Creates and manages all MedRAX services with shared dependencies.
    """
    
    def __init__(
        self,
        device: Optional[str] = None,
        temp_dir: Optional[Path] = None,
        lazy_load: bool = True,
    ):
        """
        Initialize the service container.
        
        Args:
            device: Device for model inference (cuda/cpu/mps)
            temp_dir: Directory for temporary files
            lazy_load: If True, models are loaded on first use
        """
        self._device = device
        self._temp_dir = temp_dir or Path("temp")
        self._temp_dir.mkdir(exist_ok=True)
        self._lazy_load = lazy_load
        
        # Shared dependencies
        self._image_storage = InMemoryImageStorage()
        
        # Service instances (lazy loaded if lazy_load=True)
        self._classification_service: Optional[ClassificationService] = None
        self._vqa_service: Optional[VQAService] = None
        self._segmentation_service: Optional[SegmentationService] = None
        self._dicom_service: Optional[DicomService] = None
        
        if not lazy_load:
            self._initialize_all()
    
    def _initialize_all(self) -> None:
        """Initialize all services eagerly."""
        _ = self.classification
        _ = self.vqa
        _ = self.segmentation
        _ = self.dicom
    
    @property
    def image_storage(self) -> InMemoryImageStorage:
        """Get the image storage instance."""
        return self._image_storage
    
    @property
    def classification(self) -> ClassificationService:
        """Get the classification service (lazy loaded)."""
        if self._classification_service is None:
            wrapper = ClassifierWrapper(device=self._device)
            self._classification_service = ClassificationService(
                classifier=wrapper,
                image_storage=self._image_storage,
            )
        return self._classification_service
    
    @property
    def vqa(self) -> VQAService:
        """Get the VQA service (lazy loaded)."""
        if self._vqa_service is None:
            wrapper = VQAWrapper(device=self._device)
            self._vqa_service = VQAService(
                vqa=wrapper,
                image_storage=self._image_storage,
            )
        return self._vqa_service
    
    @property
    def segmentation(self) -> SegmentationService:
        """Get the segmentation service (lazy loaded)."""
        if self._segmentation_service is None:
            wrapper = SegmentationWrapper(
                device=self._device,
                temp_dir=self._temp_dir,
            )
            self._segmentation_service = SegmentationService(
                segmenter=wrapper,
                image_storage=self._image_storage,
            )
        return self._segmentation_service
    
    @property
    def dicom(self) -> DicomService:
        """Get the DICOM service."""
        if self._dicom_service is None:
            wrapper = DicomWrapper(temp_dir=self._temp_dir)
            self._dicom_service = DicomService(
                dicom_processor=wrapper,
                image_storage=self._image_storage,
            )
        return self._dicom_service
    
    def register_image(self, image_path: str) -> str:
        """
        Register an image file and return its ID.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Generated image ID
        """
        entity = self._image_storage.store(Path(image_path))
        return entity.id

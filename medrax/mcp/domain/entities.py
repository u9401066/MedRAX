"""
Domain Entities - Core data structures for MedRAX MCP

These entities are pure data classes with no business logic dependencies.
They represent the core concepts in the medical imaging domain.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ImageFormat(Enum):
    """Supported image formats."""
    PNG = "png"
    JPEG = "jpeg"
    DICOM = "dicom"
    UNKNOWN = "unknown"


class AnalysisStatus(Enum):
    """Status of an analysis operation."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ImageEntity:
    """
    Represents a medical image in the system.
    
    Attributes:
        id: Unique identifier for the image
        path: File system path to the image
        format: Image format (PNG, JPEG, DICOM)
        created_at: Timestamp when the image was registered
        metadata: Additional image metadata
    """
    id: str
    path: Path
    format: ImageFormat = ImageFormat.UNKNOWN
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def exists(self) -> bool:
        """Check if the image file exists."""
        return self.path.exists()
    
    @property
    def is_dicom(self) -> bool:
        """Check if the image is DICOM format."""
        return self.format == ImageFormat.DICOM


@dataclass
class DicomMetadata:
    """
    DICOM-specific metadata extracted from medical images.
    
    Attributes:
        patient_id: Patient identifier
        study_date: Date of the study
        modality: Imaging modality (e.g., CR, DX)
        pixel_spacing: Physical size of pixels in mm
        window_center: Window center for display
        window_width: Window width for display
        bits_stored: Bit depth of stored values
        manufacturer: Equipment manufacturer
    """
    patient_id: Optional[str] = None
    study_date: Optional[str] = None
    modality: Optional[str] = None
    pixel_spacing: Optional[Tuple[float, float]] = None
    window_center: Optional[float] = None
    window_width: Optional[float] = None
    bits_stored: Optional[int] = None
    manufacturer: Optional[str] = None
    image_orientation: Optional[List[float]] = None
    image_position: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "patient_id": self.patient_id,
            "study_date": self.study_date,
            "modality": self.modality,
            "pixel_spacing": self.pixel_spacing,
            "window_center": self.window_center,
            "window_width": self.window_width,
            "bits_stored": self.bits_stored,
            "manufacturer": self.manufacturer,
        }


@dataclass
class AnalysisResult:
    """
    Base class for analysis results.
    
    Attributes:
        status: Current status of the analysis
        timestamp: When the analysis was performed
        error: Error message if analysis failed
        processing_time_ms: Time taken in milliseconds
    """
    status: AnalysisStatus = AnalysisStatus.PENDING
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None
    processing_time_ms: Optional[float] = None
    
    @property
    def is_success(self) -> bool:
        """Check if analysis completed successfully."""
        return self.status == AnalysisStatus.COMPLETED


@dataclass
class ClassificationResult(AnalysisResult):
    """
    Result from chest X-ray classification.
    
    Attributes:
        pathologies: Dict mapping pathology name to probability (0-1)
        model_name: Name of the model used
        threshold: Confidence threshold applied
        image_path: Path to the analyzed image
    """
    pathologies: Dict[str, float] = field(default_factory=dict)
    model_name: str = "densenet121-res224-all"
    threshold: float = 0.5
    image_path: Optional[str] = None
    
    # Standard 18 pathologies from TorchXRayVision
    SUPPORTED_PATHOLOGIES: tuple = (
        "Atelectasis", "Cardiomegaly", "Consolidation", "Edema",
        "Effusion", "Emphysema", "Enlarged Cardiomediastinum", "Fibrosis",
        "Fracture", "Hernia", "Infiltration", "Lung Lesion",
        "Lung Opacity", "Mass", "Nodule", "Pleural Thickening",
        "Pneumonia", "Pneumothorax"
    )
    
    def get_positive_findings(self) -> Dict[str, float]:
        """Get pathologies above threshold."""
        return {
            name: prob for name, prob in self.pathologies.items()
            if prob >= self.threshold
        }
    
    def get_top_findings(self, n: int = 5) -> List[Tuple[str, float]]:
        """Get top N pathologies by probability."""
        sorted_items = sorted(
            self.pathologies.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_items[:n]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MCP response."""
        return {
            "status": self.status.value,
            "classifications": self.pathologies,
            "positive_findings": self.get_positive_findings(),
            "top_findings": [
                {"pathology": p, "probability": round(prob, 4)}
                for p, prob in self.get_top_findings()
            ],
            "model": self.model_name,
            "threshold": self.threshold,
            "processing_time_ms": self.processing_time_ms,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class SegmentationResult(AnalysisResult):
    """
    Result from anatomical segmentation.
    
    Attributes:
        organs: Dict mapping organ name to its metrics
        visualization_path: Path to segmentation overlay image
        organs_segmented: List of successfully segmented organs
    """
    organs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    visualization_path: Optional[str] = None
    visualization_base64: Optional[str] = None
    organs_segmented: List[str] = field(default_factory=list)
    
    # Standard 14 organs from PSPNet
    SUPPORTED_ORGANS: tuple = (
        "Left Clavicle", "Right Clavicle",
        "Left Scapula", "Right Scapula",
        "Left Lung", "Right Lung",
        "Left Hilus Pulmonis", "Right Hilus Pulmonis",
        "Heart", "Aorta",
        "Facies Diaphragmatica", "Mediastinum",
        "Weasand", "Spine"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MCP response."""
        return {
            "status": self.status.value,
            "organs_segmented": self.organs_segmented,
            "organ_metrics": self.organs,
            "visualization": self.visualization_base64,
            "processing_time_ms": self.processing_time_ms,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class VQAResult(AnalysisResult):
    """
    Result from Visual Question Answering.
    
    Attributes:
        question: The input question
        answer: Model's response
        images_analyzed: Number of images processed
        model_name: Name of the VQA model used
    """
    question: str = ""
    answer: str = ""
    images_analyzed: int = 0
    model_name: str = "CheXagent-2-3b"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MCP response."""
        return {
            "status": self.status.value,
            "question": self.question,
            "answer": self.answer,
            "images_analyzed": self.images_analyzed,
            "model": self.model_name,
            "processing_time_ms": self.processing_time_ms,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class GroundingResult(AnalysisResult):
    """
    Result from phrase grounding (finding localization).
    
    Attributes:
        phrase: The phrase being grounded
        boxes: List of bounding boxes (x, y, w, h, confidence)
        visualization_base64: Annotated image in base64
    """
    phrase: str = ""
    boxes: List[Dict[str, Any]] = field(default_factory=list)
    visualization_base64: Optional[str] = None
    model_name: str = "Maira-2"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MCP response."""
        return {
            "status": self.status.value,
            "phrase": self.phrase,
            "boxes": self.boxes,
            "visualization": self.visualization_base64,
            "model": self.model_name,
            "processing_time_ms": self.processing_time_ms,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ReportGenerationResult(AnalysisResult):
    """
    Result from radiology report generation.
    
    Attributes:
        findings: Generated findings section
        impression: Generated impression section
        full_report: Complete generated report
    """
    findings: str = ""
    impression: str = ""
    full_report: str = ""
    model_name: str = "SwinV2-CheXpert"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MCP response."""
        return {
            "status": self.status.value,
            "findings": self.findings,
            "impression": self.impression,
            "full_report": self.full_report,
            "model": self.model_name,
            "processing_time_ms": self.processing_time_ms,
            "timestamp": self.timestamp.isoformat(),
        }

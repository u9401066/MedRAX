"""
Domain Layer - Core Entities and Protocols

This layer contains:
- Entity definitions (ImageEntity, AnalysisResult, etc.)
- Protocol/Interface definitions
- Value objects
- Domain exceptions

No external dependencies except standard library and typing.
"""

from medrax.mcp.domain.entities import (
    ImageEntity,
    AnalysisResult,
    ClassificationResult,
    SegmentationResult,
    VQAResult,
    DicomMetadata,
)
from medrax.mcp.domain.protocols import (
    ClassifierProtocol,
    VQAProtocol,
    SegmentationProtocol,
    DicomProcessorProtocol,
)
from medrax.mcp.domain.exceptions import (
    MedRAXError,
    ImageNotFoundError,
    ModelError,
    ValidationError,
)

__all__ = [
    # Entities
    "ImageEntity",
    "AnalysisResult",
    "ClassificationResult",
    "SegmentationResult",
    "VQAResult",
    "DicomMetadata",
    # Protocols
    "ClassifierProtocol",
    "VQAProtocol",
    "SegmentationProtocol",
    "DicomProcessorProtocol",
    # Exceptions
    "MedRAXError",
    "ImageNotFoundError",
    "ModelError",
    "ValidationError",
]

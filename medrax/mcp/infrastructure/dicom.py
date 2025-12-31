"""
DICOM Wrapper - Wraps DICOM processing functionality

Implements DicomProcessorProtocol from domain layer.
"""

import time
import uuid
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pydicom
from PIL import Image

from medrax.mcp.domain.entities import DicomMetadata
from medrax.mcp.domain.exceptions import ImageNotFoundError, UnsupportedFormatError


class DicomWrapper:
    """
    Wrapper for DICOM file processing.
    
    Implements DicomProcessorProtocol for use in MCP tools.
    
    Attributes:
        temp_dir: Directory for temporary output files
    """
    
    def __init__(self, temp_dir: Optional[Path] = None):
        """
        Initialize the DICOM wrapper.
        
        Args:
            temp_dir: Directory for temporary output files
        """
        self._temp_dir = temp_dir or Path("temp")
        self._temp_dir.mkdir(exist_ok=True)
    
    def _apply_windowing(
        self,
        img: np.ndarray,
        center: float,
        width: float,
    ) -> np.ndarray:
        """Apply window/level adjustment to the image."""
        img_min = center - width // 2
        img_max = center + width // 2
        img = np.clip(img, img_min, img_max)
        img = ((img - img_min) / width * 255).astype(np.uint8)
        return img
    
    def extract_metadata(self, dicom_path: Path) -> DicomMetadata:
        """
        Extract metadata from DICOM file without conversion.
        
        Args:
            dicom_path: Path to DICOM file
            
        Returns:
            DicomMetadata with extracted information
        """
        if not dicom_path.exists():
            raise ImageNotFoundError(image_path=str(dicom_path))
        
        try:
            dcm = pydicom.dcmread(str(dicom_path))
        except Exception as e:
            raise UnsupportedFormatError(
                format="unknown",
                supported_formats=["DICOM"],
            )
        
        # Extract window parameters
        window_center = getattr(dcm, "WindowCenter", None)
        if isinstance(window_center, list):
            window_center = window_center[0]
        
        window_width = getattr(dcm, "WindowWidth", None)
        if isinstance(window_width, list):
            window_width = window_width[0]
        
        # Extract pixel spacing
        pixel_spacing = getattr(dcm, "PixelSpacing", None)
        if pixel_spacing is not None:
            pixel_spacing = tuple(float(x) for x in pixel_spacing)
        
        return DicomMetadata(
            patient_id=getattr(dcm, "PatientID", None),
            study_date=getattr(dcm, "StudyDate", None),
            modality=getattr(dcm, "Modality", None),
            pixel_spacing=pixel_spacing,
            window_center=float(window_center) if window_center is not None else None,
            window_width=float(window_width) if window_width is not None else None,
            bits_stored=getattr(dcm, "BitsStored", None),
            manufacturer=getattr(dcm, "Manufacturer", None),
            image_orientation=getattr(dcm, "ImageOrientationPatient", None),
            image_position=getattr(dcm, "ImagePositionPatient", None),
        )
    
    def process(
        self,
        dicom_path: Path,
        window_center: Optional[float] = None,
        window_width: Optional[float] = None,
    ) -> Tuple[Path, DicomMetadata]:
        """
        Process DICOM file and convert to standard image format.
        
        Args:
            dicom_path: Path to DICOM file
            window_center: Optional window center for display
            window_width: Optional window width for display
            
        Returns:
            Tuple of (output image path, DICOM metadata)
        """
        if not dicom_path.exists():
            raise ImageNotFoundError(image_path=str(dicom_path))
        
        try:
            dcm = pydicom.dcmread(str(dicom_path))
            img = dcm.pixel_array.astype(float)
        except Exception as e:
            raise UnsupportedFormatError(
                format="unknown",
                supported_formats=["DICOM"],
            )
        
        # Get default window parameters from DICOM if not specified
        if window_center is None and hasattr(dcm, "WindowCenter"):
            window_center = dcm.WindowCenter
            if isinstance(window_center, list):
                window_center = window_center[0]
        
        if window_width is None and hasattr(dcm, "WindowWidth"):
            window_width = dcm.WindowWidth
            if isinstance(window_width, list):
                window_width = window_width[0]
        
        # Apply rescale slope/intercept if available
        if hasattr(dcm, "RescaleSlope") and hasattr(dcm, "RescaleIntercept"):
            img = img * dcm.RescaleSlope + dcm.RescaleIntercept
        
        # Apply windowing if parameters are available
        if window_center is not None and window_width is not None:
            img = self._apply_windowing(img, window_center, window_width)
        else:
            # Normalize to 0-255
            img = ((img - img.min()) / (img.max() - img.min()) * 255).astype(np.uint8)
        
        # Save as PNG
        output_path = self._temp_dir / f"dicom_{uuid.uuid4().hex[:8]}.png"
        Image.fromarray(img).save(output_path)
        
        # Extract metadata
        metadata = self.extract_metadata(dicom_path)
        
        return output_path, metadata

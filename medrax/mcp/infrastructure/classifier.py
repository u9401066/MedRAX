"""
Classifier Wrapper - Wraps DenseNet-121 chest X-ray classifier

Implements ClassifierProtocol from domain layer.
"""

import time
from pathlib import Path
from typing import List, Optional

import torch
import torchvision
import skimage.io
import torchxrayvision as xrv

from medrax.mcp.domain.entities import AnalysisStatus, ClassificationResult
from medrax.mcp.domain.exceptions import ImageNotFoundError, ModelError


class ClassifierWrapper:
    """
    Wrapper for TorchXRayVision DenseNet classifier.
    
    Implements ClassifierProtocol for use in MCP tools.
    
    Attributes:
        model: The DenseNet model instance
        device: Device to run inference on
        transform: Image preprocessing transforms
    """
    
    # 18 pathologies from TorchXRayVision
    SUPPORTED_PATHOLOGIES = [
        "Atelectasis", "Cardiomegaly", "Consolidation", "Edema",
        "Effusion", "Emphysema", "Enlarged Cardiomediastinum", "Fibrosis",
        "Fracture", "Hernia", "Infiltration", "Lung Lesion",
        "Lung Opacity", "Mass", "Nodule", "Pleural Thickening",
        "Pneumonia", "Pneumothorax"
    ]
    
    def __init__(
        self,
        model_name: str = "densenet121-res224-all",
        device: Optional[str] = None,
    ):
        """
        Initialize the classifier wrapper.
        
        Args:
            model_name: Model weights to load
            device: Device to run on (cuda/cpu/mps)
        """
        self._model_name = model_name
        self._device = self._get_device(device)
        self._model = None
        self._transform = None
        self._initialized = False
    
    def _get_device(self, device: Optional[str]) -> torch.device:
        """Determine the best available device."""
        if device:
            return torch.device(device)
        if torch.cuda.is_available():
            return torch.device("cuda")
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")
    
    def _ensure_initialized(self) -> None:
        """Lazy initialization of model and transforms."""
        if self._initialized:
            return
        
        try:
            self._model = xrv.models.DenseNet(weights=self._model_name)
            self._model.eval()
            self._model = self._model.to(self._device)
            self._transform = torchvision.transforms.Compose([
                xrv.datasets.XRayCenterCrop()
            ])
            self._initialized = True
        except Exception as e:
            raise ModelError(
                model_name=self._model_name,
                message=f"Failed to initialize classifier: {e}",
                original_error=e,
            )
    
    @property
    def supported_pathologies(self) -> List[str]:
        """List of pathologies this classifier supports."""
        return self.SUPPORTED_PATHOLOGIES.copy()
    
    @property
    def model_name(self) -> str:
        """Name of the model."""
        return self._model_name
    
    def _process_image(self, image_path: Path) -> torch.Tensor:
        """
        Load and preprocess image for inference.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Preprocessed tensor ready for model
        """
        img = skimage.io.imread(str(image_path))
        img = xrv.datasets.normalize(img, 255)
        
        # Convert to grayscale if needed
        if len(img.shape) > 2:
            img = img[:, :, 0]
        
        # Add channel dimension
        img = img[None, :, :]
        
        # Apply transforms
        img = self._transform(img)
        
        # Convert to tensor and add batch dimension
        img = torch.from_numpy(img).unsqueeze(0)
        img = img.to(self._device)
        
        return img
    
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
        start_time = time.perf_counter()
        
        # Validate input
        if not image_path.exists():
            raise ImageNotFoundError(image_path=str(image_path))
        
        # Initialize model if needed
        self._ensure_initialized()
        
        try:
            # Preprocess and run inference
            img = self._process_image(image_path)
            
            with torch.inference_mode():
                preds = self._model(img).cpu()[0]
            
            # Build results dictionary
            all_pathologies = dict(zip(
                xrv.datasets.default_pathologies,
                preds.numpy().tolist()
            ))
            
            # Filter to requested pathologies if specified
            if pathologies:
                all_pathologies = {
                    k: v for k, v in all_pathologies.items()
                    if k in pathologies
                }
            
            processing_time = (time.perf_counter() - start_time) * 1000
            
            return ClassificationResult(
                status=AnalysisStatus.COMPLETED,
                pathologies=all_pathologies,
                model_name=self._model_name,
                threshold=threshold,
                image_path=str(image_path),
                processing_time_ms=processing_time,
            )
            
        except ImageNotFoundError:
            raise
        except Exception as e:
            return ClassificationResult(
                status=AnalysisStatus.FAILED,
                error=str(e),
                image_path=str(image_path),
            )
    
    def __del__(self):
        """Cleanup model resources."""
        if self._model is not None:
            del self._model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

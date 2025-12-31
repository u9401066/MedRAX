"""
Segmentation Wrapper - Wraps PSPNet for anatomical segmentation

Implements SegmentationProtocol from domain layer.
"""

import base64
import io
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import torch
import torchvision
import skimage.io
import skimage.measure
import skimage.transform
import matplotlib.pyplot as plt
import torchxrayvision as xrv

from medrax.mcp.domain.entities import AnalysisStatus, SegmentationResult
from medrax.mcp.domain.exceptions import ImageNotFoundError, ModelError


class SegmentationWrapper:
    """
    Wrapper for TorchXRayVision PSPNet segmentation model.
    
    Implements SegmentationProtocol for use in MCP tools.
    
    Attributes:
        model: The PSPNet model instance
        device: Device to run inference on
    """
    
    # 14 organs from TorchXRayVision PSPNet
    SUPPORTED_ORGANS = [
        "Left Clavicle", "Right Clavicle",
        "Left Scapula", "Right Scapula",
        "Left Lung", "Right Lung",
        "Left Hilus Pulmonis", "Right Hilus Pulmonis",
        "Heart", "Aorta",
        "Facies Diaphragmatica", "Mediastinum",
        "Weasand", "Spine"
    ]
    
    ORGAN_MAP = {
        "Left Clavicle": 0, "Right Clavicle": 1,
        "Left Scapula": 2, "Right Scapula": 3,
        "Left Lung": 4, "Right Lung": 5,
        "Left Hilus Pulmonis": 6, "Right Hilus Pulmonis": 7,
        "Heart": 8, "Aorta": 9,
        "Facies Diaphragmatica": 10, "Mediastinum": 11,
        "Weasand": 12, "Spine": 13,
    }
    
    def __init__(
        self,
        device: Optional[str] = None,
        temp_dir: Optional[Path] = None,
        pixel_spacing_mm: float = 0.2,
    ):
        """
        Initialize the segmentation wrapper.
        
        Args:
            device: Device to run on (cuda/cpu/mps)
            temp_dir: Directory for temporary files
            pixel_spacing_mm: Pixel spacing for area calculations
        """
        self._device = self._get_device(device)
        self._temp_dir = temp_dir or Path("temp")
        self._temp_dir.mkdir(exist_ok=True)
        self._pixel_spacing_mm = pixel_spacing_mm
        self._model = None
        self._transform = None
        self._initialized = False
    
    def _get_device(self, device: Optional[str]) -> torch.device:
        """Determine the best available device."""
        if device:
            return torch.device(device)
        if torch.cuda.is_available():
            return torch.device("cuda")
        return torch.device("cpu")
    
    def _ensure_initialized(self) -> None:
        """Lazy initialization of model and transforms."""
        if self._initialized:
            return
        
        try:
            self._model = xrv.baseline_models.chestx_det.PSPNet()
            self._model = self._model.to(self._device)
            self._model.eval()
            
            self._transform = torchvision.transforms.Compose([
                xrv.datasets.XRayCenterCrop(),
                xrv.datasets.XRayResizer(512)
            ])
            
            self._initialized = True
        except Exception as e:
            raise ModelError(
                model_name="PSPNet",
                message=f"Failed to initialize segmentation model: {e}",
                original_error=e,
            )
    
    @property
    def supported_organs(self) -> List[str]:
        """List of organs this segmenter supports."""
        return self.SUPPORTED_ORGANS.copy()
    
    def _align_mask_to_original(
        self,
        mask: np.ndarray,
        original_shape: tuple,
    ) -> np.ndarray:
        """Align mask from transformed space back to original image."""
        orig_h, orig_w = original_shape
        crop_size = min(orig_h, orig_w)
        crop_top = (orig_h - crop_size) // 2
        crop_left = (orig_w - crop_size) // 2
        
        resized_mask = skimage.transform.resize(
            mask, (crop_size, crop_size),
            order=0, preserve_range=True, anti_aliasing=False
        )
        
        full_mask = np.zeros(original_shape)
        full_mask[crop_top:crop_top + crop_size, crop_left:crop_left + crop_size] = resized_mask
        
        return full_mask
    
    def _compute_organ_metrics(
        self,
        mask: np.ndarray,
        original_img: np.ndarray,
        confidence: float,
    ) -> Optional[Dict[str, Any]]:
        """Compute comprehensive metrics for a single organ mask."""
        if mask.shape != original_img.shape:
            mask = self._align_mask_to_original(mask, original_img.shape)
        
        props = skimage.measure.regionprops(mask.astype(int))
        if not props:
            return None
        
        props = props[0]
        area_cm2 = mask.sum() * (self._pixel_spacing_mm / 10) ** 2
        
        img_height, img_width = mask.shape
        cy, cx = props.centroid
        
        organ_pixels = original_img[mask > 0]
        mean_intensity = organ_pixels.mean() if len(organ_pixels) > 0 else 0
        std_intensity = organ_pixels.std() if len(organ_pixels) > 0 else 0
        
        return {
            "area_pixels": int(mask.sum()),
            "area_cm2": float(area_cm2),
            "centroid": [float(cy), float(cx)],
            "bbox": list(map(int, props.bbox)),
            "width": int(props.bbox[3] - props.bbox[1]),
            "height": int(props.bbox[2] - props.bbox[0]),
            "aspect_ratio": float(
                (props.bbox[2] - props.bbox[0]) / max(1, props.bbox[3] - props.bbox[1])
            ),
            "relative_position": {
                "top": cy / img_height,
                "left": cx / img_width,
            },
            "mean_intensity": float(mean_intensity),
            "std_intensity": float(std_intensity),
            "confidence_score": float(confidence),
        }
    
    def _create_visualization(
        self,
        original_img: np.ndarray,
        pred_masks: torch.Tensor,
        organ_indices: List[int],
        organ_names: List[str],
    ) -> str:
        """Create visualization and return as base64."""
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.imshow(
            original_img, cmap="gray",
            extent=[0, original_img.shape[1], original_img.shape[0], 0]
        )
        
        colors = plt.cm.rainbow(np.linspace(0, 1, len(organ_indices)))
        
        for idx, (organ_idx, color, name) in enumerate(zip(organ_indices, colors, organ_names)):
            mask = pred_masks[0, organ_idx].cpu().numpy()
            if mask.sum() > 0:
                if mask.shape != original_img.shape:
                    mask = self._align_mask_to_original(mask, original_img.shape)
                
                rgba_color = list(color[:3]) + [0.3]
                overlay = np.zeros((*original_img.shape, 4))
                overlay[mask > 0] = rgba_color
                ax.imshow(
                    overlay,
                    extent=[0, original_img.shape[1], original_img.shape[0], 0]
                )
                
                # Add label
                props = skimage.measure.regionprops(mask.astype(int))
                if props:
                    cy, cx = props[0].centroid
                    ax.annotate(
                        name, (cx, cy),
                        color=color, fontsize=8, ha='center',
                        bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.7)
                    )
        
        ax.axis("off")
        ax.set_title("Anatomical Segmentation")
        
        # Convert to base64
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
        buf.seek(0)
        plt.close(fig)
        
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    
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
        start_time = time.perf_counter()
        
        if not image_path.exists():
            raise ImageNotFoundError(image_path=str(image_path))
        
        self._ensure_initialized()
        
        try:
            # Load image
            original_img = skimage.io.imread(str(image_path))
            if len(original_img.shape) > 2:
                original_img = original_img[:, :, 0]
            
            # Preprocess
            img = xrv.datasets.normalize(original_img, 255)
            img = img[None, :, :]
            img = self._transform(img)
            img = torch.from_numpy(img).unsqueeze(0).to(self._device)
            
            # Run inference
            with torch.inference_mode():
                pred = self._model(img)
            
            # Determine organs to process
            if organs:
                organ_indices = [self.ORGAN_MAP[o] for o in organs if o in self.ORGAN_MAP]
                organ_names = [o for o in organs if o in self.ORGAN_MAP]
            else:
                organ_indices = list(range(14))
                organ_names = self.SUPPORTED_ORGANS
            
            # Compute metrics for each organ
            organ_metrics = {}
            organs_segmented = []
            
            for organ_idx, organ_name in zip(organ_indices, organ_names):
                mask = pred[0, organ_idx].cpu().numpy()
                confidence = float(mask.max())
                
                if mask.sum() > 0:
                    metrics = self._compute_organ_metrics(mask, original_img, confidence)
                    if metrics:
                        organ_metrics[organ_name] = metrics
                        organs_segmented.append(organ_name)
            
            # Create visualization
            visualization_base64 = self._create_visualization(
                original_img, pred, organ_indices, organ_names
            )
            
            processing_time = (time.perf_counter() - start_time) * 1000
            
            return SegmentationResult(
                status=AnalysisStatus.COMPLETED,
                organs=organ_metrics,
                organs_segmented=organs_segmented,
                visualization_base64=visualization_base64,
                processing_time_ms=processing_time,
            )
            
        except ImageNotFoundError:
            raise
        except Exception as e:
            return SegmentationResult(
                status=AnalysisStatus.FAILED,
                error=str(e),
            )
    
    def __del__(self):
        """Cleanup model resources."""
        if self._model is not None:
            del self._model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

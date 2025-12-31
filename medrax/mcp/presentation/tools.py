"""
MCP Tools - FastMCP tool definitions

These tools are exposed via MCP protocol and orchestrate application services.
"""

from typing import Any, Dict, List, Optional

from medrax.mcp.application.services import MedRAXServiceContainer
from medrax.mcp.domain.exceptions import MedRAXError


def register_tools(app, services: MedRAXServiceContainer) -> None:
    """
    Register all MCP tools with the FastMCP app.
    
    Args:
        app: FastMCP application instance
        services: Service container with initialized services
    """
    
    @app.tool()
    async def register_image(image_path: str) -> Dict[str, Any]:
        """
        Register a local image file for analysis.
        
        This must be called first to get an image_id that can be used
        with other analysis tools.
        
        Args:
            image_path: Absolute path to the image file (PNG, JPEG)
            
        Returns:
            Dictionary with:
            - image_id: Unique identifier for the registered image
            - format: Detected image format
            - message: Success message
        """
        try:
            image_id = services.register_image(image_path)
            entity = services.image_storage.get(image_id)
            
            return {
                "image_id": image_id,
                "format": entity.format.value if entity else "unknown",
                "message": f"Image registered successfully. Use image_id '{image_id}' for analysis.",
            }
        except MedRAXError as e:
            return {"error": e.message, "details": e.details}
        except Exception as e:
            return {"error": str(e)}
    
    @app.tool()
    async def classify_cxr(
        image_id: str,
        pathologies: Optional[List[str]] = None,
        threshold: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Classify chest X-ray for 18 different pathologies.
        
        Uses a DenseNet-121 model trained on multiple chest X-ray datasets.
        
        Supported pathologies:
        - Atelectasis, Cardiomegaly, Consolidation, Edema
        - Effusion, Emphysema, Enlarged Cardiomediastinum, Fibrosis
        - Fracture, Hernia, Infiltration, Lung Lesion
        - Lung Opacity, Mass, Nodule, Pleural Thickening
        - Pneumonia, Pneumothorax
        
        Args:
            image_id: ID of a registered chest X-ray image
            pathologies: Optional list to filter specific pathologies
            threshold: Confidence threshold (0-1) for positive findings
            
        Returns:
            Dictionary with:
            - classifications: All pathology probabilities
            - positive_findings: Pathologies above threshold
            - top_findings: Top 5 most likely pathologies
            - processing_time_ms: Analysis time
        """
        try:
            return services.classification.classify(
                image_id=image_id,
                pathologies=pathologies,
                threshold=threshold,
            )
        except MedRAXError as e:
            return {"error": e.message, "details": e.details}
        except Exception as e:
            return {"error": str(e)}
    
    @app.tool()
    async def ask_cxr_expert(
        image_ids: List[str],
        question: str,
        max_tokens: int = 512,
    ) -> Dict[str, Any]:
        """
        Ask medical questions about chest X-ray images using CheXagent.
        
        CheXagent is a specialized vision-language model for chest X-ray analysis.
        
        Supported tasks:
        - Visual question answering ("Is there pneumonia in this X-ray?")
        - Report generation ("Generate a radiology report for this X-ray")
        - Abnormality detection ("What abnormalities are present?")
        - Comparative analysis ("Compare these two X-rays")
        - Anatomical description ("Describe the heart size")
        
        Args:
            image_ids: List of registered image IDs (supports multiple for comparison)
            question: Natural language question about the images
            max_tokens: Maximum length of the response
            
        Returns:
            Dictionary with:
            - question: The input question
            - answer: Expert response from CheXagent
            - images_analyzed: Number of images processed
            - processing_time_ms: Analysis time
        """
        try:
            return services.vqa.answer(
                image_ids=image_ids,
                question=question,
                max_tokens=max_tokens,
            )
        except MedRAXError as e:
            return {"error": e.message, "details": e.details}
        except Exception as e:
            return {"error": str(e)}
    
    @app.tool()
    async def segment_anatomy(
        image_id: str,
        organs: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Segment anatomical structures in a chest X-ray.
        
        Uses PSPNet model to identify and outline 14 anatomical structures.
        
        Supported organs:
        - Left/Right Clavicle (collar bones)
        - Left/Right Scapula (shoulder blades)
        - Left/Right Lung
        - Left/Right Hilus Pulmonis (lung roots)
        - Heart
        - Aorta
        - Facies Diaphragmatica (diaphragm)
        - Mediastinum (central chest cavity)
        - Weasand (esophagus)
        - Spine
        
        Args:
            image_id: ID of a registered chest X-ray image
            organs: Optional list to filter specific organs
            
        Returns:
            Dictionary with:
            - organs_segmented: List of successfully segmented organs
            - organ_metrics: Detailed metrics for each organ (area, position, etc.)
            - visualization: Base64-encoded overlay image
            - processing_time_ms: Analysis time
            
        Note: Area calculations are approximate unless the input was DICOM
        with proper pixel spacing information.
        """
        try:
            return services.segmentation.segment(
                image_id=image_id,
                organs=organs,
            )
        except MedRAXError as e:
            return {"error": e.message, "details": e.details}
        except Exception as e:
            return {"error": str(e)}
    
    @app.tool()
    async def process_dicom(
        dicom_path: str,
        window_center: Optional[float] = None,
        window_width: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Process a DICOM file and convert it to a viewable format.
        
        Extracts pixel data from DICOM, applies windowing (contrast adjustment),
        and returns a standard image format suitable for other analysis tools.
        
        Args:
            dicom_path: Absolute path to the DICOM file
            window_center: Optional center value for window/level adjustment
            window_width: Optional width value for window/level adjustment
            
        Returns:
            Dictionary with:
            - image_id: ID for the converted image (use with other tools)
            - image_base64: Base64-encoded PNG image
            - metadata: DICOM metadata (patient ID, study date, modality, etc.)
            - original_path: Original DICOM file path
            - processed_path: Path to the converted PNG file
            
        Note: If window_center/window_width are not specified, values from
        the DICOM file will be used if available.
        """
        try:
            return services.dicom.process(
                dicom_path=dicom_path,
                window_center=window_center,
                window_width=window_width,
            )
        except MedRAXError as e:
            return {"error": e.message, "details": e.details}
        except Exception as e:
            return {"error": str(e)}
    
    @app.tool()
    async def get_dicom_metadata(dicom_path: str) -> Dict[str, Any]:
        """
        Extract metadata from a DICOM file without converting it.
        
        Useful for inspecting DICOM files before processing.
        
        Args:
            dicom_path: Absolute path to the DICOM file
            
        Returns:
            Dictionary with DICOM metadata:
            - patient_id: Patient identifier
            - study_date: Date of the study
            - modality: Imaging modality (CR, DX, etc.)
            - pixel_spacing: Physical pixel size in mm
            - window_center/window_width: Display settings
            - bits_stored: Bit depth
            - manufacturer: Equipment manufacturer
        """
        try:
            return services.dicom.get_metadata(dicom_path)
        except MedRAXError as e:
            return {"error": e.message, "details": e.details}
        except Exception as e:
            return {"error": str(e)}
    
    @app.tool()
    async def list_registered_images() -> Dict[str, Any]:
        """
        List all currently registered images.
        
        Returns:
            Dictionary with:
            - image_ids: List of all registered image IDs
            - count: Total number of registered images
        """
        try:
            image_ids = services.image_storage.list_all()
            return {
                "image_ids": image_ids,
                "count": len(image_ids),
            }
        except Exception as e:
            return {"error": str(e)}
    
    @app.tool()
    async def get_supported_pathologies() -> Dict[str, Any]:
        """
        Get the list of pathologies supported by the classifier.
        
        Returns:
            Dictionary with:
            - pathologies: List of 18 supported pathology names
            - count: Number of pathologies
        """
        pathologies = services.classification.supported_pathologies
        return {
            "pathologies": pathologies,
            "count": len(pathologies),
        }
    
    @app.tool()
    async def get_supported_organs() -> Dict[str, Any]:
        """
        Get the list of organs supported by the segmentation model.
        
        Returns:
            Dictionary with:
            - organs: List of 14 supported organ names
            - count: Number of organs
        """
        organs = services.segmentation.supported_organs
        return {
            "organs": organs,
            "count": len(organs),
        }

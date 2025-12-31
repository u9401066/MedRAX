"""
VQA Wrapper - Wraps CheXagent for Visual Question Answering

Implements VQAProtocol from domain layer.
"""

import time
from pathlib import Path
from typing import Any, List, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from medrax.mcp.domain.entities import AnalysisStatus, VQAResult
from medrax.mcp.domain.exceptions import ImageNotFoundError, ModelError


class VQAWrapper:
    """
    Wrapper for CheXagent Visual Question Answering model.
    
    Implements VQAProtocol for use in MCP tools.
    
    Attributes:
        model: The CheXagent model instance
        tokenizer: The tokenizer for the model
        device: Device to run inference on
    """
    
    def __init__(
        self,
        model_name: str = "StanfordAIMI/CheXagent-2-3b",
        device: Optional[str] = None,
        dtype: torch.dtype = torch.bfloat16,
        cache_dir: Optional[str] = None,
    ):
        """
        Initialize the VQA wrapper.
        
        Args:
            model_name: HuggingFace model name
            device: Device to run on (cuda/cpu/mps)
            dtype: Data type for model weights
            cache_dir: Directory to cache model weights
        """
        self._model_name = model_name
        self._device = self._get_device(device)
        self._dtype = dtype
        self._cache_dir = cache_dir
        self._model = None
        self._tokenizer = None
        self._initialized = False
    
    def _get_device(self, device: Optional[str]) -> str:
        """Determine the best available device."""
        if device:
            return device
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"
    
    def _ensure_initialized(self) -> None:
        """Lazy initialization of model and tokenizer."""
        if self._initialized:
            return
        
        try:
            # Workaround for transformers version check
            import transformers
            original_version = transformers.__version__
            transformers.__version__ = "4.40.0"
            
            self._tokenizer = AutoTokenizer.from_pretrained(
                self._model_name,
                trust_remote_code=True,
                cache_dir=self._cache_dir,
            )
            
            self._model = AutoModelForCausalLM.from_pretrained(
                self._model_name,
                device_map=self._device,
                trust_remote_code=True,
                cache_dir=self._cache_dir,
            )
            self._model = self._model.to(dtype=self._dtype)
            self._model.eval()
            
            transformers.__version__ = original_version
            self._initialized = True
            
        except Exception as e:
            raise ModelError(
                model_name=self._model_name,
                message=f"Failed to initialize VQA model: {e}",
                original_error=e,
            )
    
    @property
    def model_name(self) -> str:
        """Name of the VQA model."""
        return self._model_name
    
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
        start_time = time.perf_counter()
        
        # Validate inputs
        for path in image_paths:
            if not path.exists():
                raise ImageNotFoundError(image_path=str(path))
        
        # Initialize model if needed
        self._ensure_initialized()
        
        try:
            # Build query with images
            str_paths = [str(p) for p in image_paths]
            query = self._tokenizer.from_list_format(
                [*[{"image": path} for path in str_paths], {"text": question}]
            )
            
            # Build conversation
            conv = [
                {"from": "system", "value": "You are a helpful medical assistant."},
                {"from": "human", "value": query},
            ]
            
            # Tokenize
            input_ids = self._tokenizer.apply_chat_template(
                conv,
                add_generation_prompt=True,
                return_tensors="pt"
            ).to(device=self._device)
            
            # Generate response
            with torch.inference_mode():
                output = self._model.generate(
                    input_ids,
                    do_sample=False,
                    num_beams=1,
                    temperature=1.0,
                    top_p=1.0,
                    use_cache=True,
                    max_new_tokens=max_tokens,
                )[0]
                
                response = self._tokenizer.decode(
                    output[input_ids.size(1):-1]
                )
            
            processing_time = (time.perf_counter() - start_time) * 1000
            
            return VQAResult(
                status=AnalysisStatus.COMPLETED,
                question=question,
                answer=response.strip(),
                images_analyzed=len(image_paths),
                model_name=self._model_name,
                processing_time_ms=processing_time,
            )
            
        except ImageNotFoundError:
            raise
        except Exception as e:
            return VQAResult(
                status=AnalysisStatus.FAILED,
                question=question,
                error=str(e),
            )
    
    def __del__(self):
        """Cleanup model resources."""
        if self._model is not None:
            del self._model
        if self._tokenizer is not None:
            del self._tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

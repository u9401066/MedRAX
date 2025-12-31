"""
Domain Exceptions - Custom exceptions for MedRAX MCP

Hierarchical exception structure for error handling.
"""


class MedRAXError(Exception):
    """Base exception for all MedRAX errors."""
    
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """Convert exception to dictionary for API response."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
        }


class ImageNotFoundError(MedRAXError):
    """Raised when an image cannot be found."""
    
    def __init__(self, image_id: str = None, image_path: str = None):
        message = "Image not found"
        details = {}
        if image_id:
            message = f"Image not found: {image_id}"
            details["image_id"] = image_id
        if image_path:
            message = f"Image file not found: {image_path}"
            details["image_path"] = image_path
        super().__init__(message, details)


class ModelError(MedRAXError):
    """Raised when a model fails to process."""
    
    def __init__(self, model_name: str, message: str, original_error: Exception = None):
        self.model_name = model_name
        self.original_error = original_error
        details = {"model_name": model_name}
        if original_error:
            details["original_error"] = str(original_error)
        super().__init__(f"Model '{model_name}' error: {message}", details)


class ValidationError(MedRAXError):
    """Raised when input validation fails."""
    
    def __init__(self, field: str, message: str, value: any = None):
        self.field = field
        self.value = value
        details = {"field": field}
        if value is not None:
            details["value"] = str(value)
        super().__init__(f"Validation error for '{field}': {message}", details)


class UnsupportedFormatError(MedRAXError):
    """Raised when an unsupported file format is provided."""
    
    def __init__(self, format: str, supported_formats: list = None):
        self.format = format
        self.supported_formats = supported_formats or []
        details = {"format": format, "supported_formats": self.supported_formats}
        super().__init__(f"Unsupported format: {format}", details)


class ResourceExhaustedError(MedRAXError):
    """Raised when resources (GPU memory, etc.) are exhausted."""
    
    def __init__(self, resource: str, message: str = None):
        self.resource = resource
        details = {"resource": resource}
        msg = message or f"Resource exhausted: {resource}"
        super().__init__(msg, details)


class ServiceUnavailableError(MedRAXError):
    """Raised when a required service is unavailable."""
    
    def __init__(self, service: str, message: str = None):
        self.service = service
        details = {"service": service}
        msg = message or f"Service unavailable: {service}"
        super().__init__(msg, details)

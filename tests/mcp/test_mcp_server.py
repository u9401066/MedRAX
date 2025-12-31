"""
MCP Server Tests - Basic functionality tests

These tests verify the MCP server components work correctly.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

# Test domain entities
class TestDomainEntities:
    """Test domain entity classes."""
    
    def test_classification_result_to_dict(self):
        """Test ClassificationResult serialization."""
        from medrax.mcp.domain.entities import (
            ClassificationResult,
            AnalysisStatus,
        )
        
        result = ClassificationResult(
            status=AnalysisStatus.COMPLETED,
            pathologies={"Pneumonia": 0.8, "Effusion": 0.3},
            threshold=0.5,
        )
        
        data = result.to_dict()
        
        assert data["status"] == "completed"
        assert "Pneumonia" in data["positive_findings"]
        assert "Effusion" not in data["positive_findings"]
        assert len(data["top_findings"]) == 2
    
    def test_classification_result_get_positive_findings(self):
        """Test positive findings filtering."""
        from medrax.mcp.domain.entities import (
            ClassificationResult,
            AnalysisStatus,
        )
        
        result = ClassificationResult(
            status=AnalysisStatus.COMPLETED,
            pathologies={
                "Pneumonia": 0.8,
                "Effusion": 0.3,
                "Cardiomegaly": 0.6,
            },
            threshold=0.5,
        )
        
        positive = result.get_positive_findings()
        
        assert len(positive) == 2
        assert "Pneumonia" in positive
        assert "Cardiomegaly" in positive
        assert "Effusion" not in positive
    
    def test_image_entity_properties(self):
        """Test ImageEntity properties."""
        from medrax.mcp.domain.entities import (
            ImageEntity,
            ImageFormat,
        )
        
        entity = ImageEntity(
            id="test_123",
            path=Path("/tmp/test.png"),
            format=ImageFormat.PNG,
        )
        
        assert entity.id == "test_123"
        assert entity.format == ImageFormat.PNG
        assert not entity.is_dicom
    
    def test_dicom_metadata_to_dict(self):
        """Test DicomMetadata serialization."""
        from medrax.mcp.domain.entities import DicomMetadata
        
        metadata = DicomMetadata(
            patient_id="P001",
            study_date="20240101",
            modality="CR",
        )
        
        data = metadata.to_dict()
        
        assert data["patient_id"] == "P001"
        assert data["modality"] == "CR"


class TestDomainExceptions:
    """Test domain exception classes."""
    
    def test_image_not_found_error(self):
        """Test ImageNotFoundError."""
        from medrax.mcp.domain.exceptions import ImageNotFoundError
        
        error = ImageNotFoundError(image_id="img_123")
        
        assert "img_123" in error.message
        assert error.details["image_id"] == "img_123"
    
    def test_validation_error(self):
        """Test ValidationError."""
        from medrax.mcp.domain.exceptions import ValidationError
        
        error = ValidationError(
            field="pathologies",
            message="Invalid value",
            value=["Unknown"],
        )
        
        assert "pathologies" in error.message
        assert error.field == "pathologies"
    
    def test_model_error(self):
        """Test ModelError."""
        from medrax.mcp.domain.exceptions import ModelError
        
        original = ValueError("GPU OOM")
        error = ModelError(
            model_name="DenseNet",
            message="Inference failed",
            original_error=original,
        )
        
        assert "DenseNet" in error.message
        assert error.model_name == "DenseNet"


class TestImageStorage:
    """Test image storage service."""
    
    def test_store_and_retrieve(self, tmp_path):
        """Test storing and retrieving images."""
        from medrax.mcp.infrastructure.image_storage import InMemoryImageStorage
        
        storage = InMemoryImageStorage()
        
        # Create a test file
        test_file = tmp_path / "test.png"
        test_file.write_bytes(b"fake image data")
        
        # Store
        entity = storage.store(test_file)
        assert entity.id.startswith("img_")
        
        # Retrieve
        retrieved = storage.get(entity.id)
        assert retrieved is not None
        assert retrieved.path == test_file
    
    def test_delete_image(self, tmp_path):
        """Test deleting images."""
        from medrax.mcp.infrastructure.image_storage import InMemoryImageStorage
        
        storage = InMemoryImageStorage()
        
        test_file = tmp_path / "test.png"
        test_file.write_bytes(b"fake image data")
        
        entity = storage.store(test_file)
        
        # Delete
        result = storage.delete(entity.id)
        assert result is True
        
        # Verify deleted
        assert storage.get(entity.id) is None
    
    def test_list_all_images(self, tmp_path):
        """Test listing all images."""
        from medrax.mcp.infrastructure.image_storage import InMemoryImageStorage
        
        storage = InMemoryImageStorage()
        
        # Store multiple
        for i in range(3):
            test_file = tmp_path / f"test_{i}.png"
            test_file.write_bytes(b"fake image data")
            storage.store(test_file)
        
        image_ids = storage.list_all()
        assert len(image_ids) == 3


class TestServiceContainer:
    """Test service container."""
    
    def test_lazy_loading(self):
        """Test that services are lazy loaded."""
        from medrax.mcp.application.services import MedRAXServiceContainer
        
        container = MedRAXServiceContainer(lazy_load=True)
        
        # Services should not be initialized yet
        assert container._classification_service is None
        assert container._vqa_service is None
    
    def test_image_storage_shared(self):
        """Test that image storage is shared across services."""
        from medrax.mcp.application.services import MedRAXServiceContainer
        
        container = MedRAXServiceContainer(lazy_load=True)
        
        # Image storage should be initialized
        assert container.image_storage is not None
    
    def test_register_image(self, tmp_path):
        """Test registering an image through container."""
        from medrax.mcp.application.services import MedRAXServiceContainer
        
        container = MedRAXServiceContainer(lazy_load=True)
        
        test_file = tmp_path / "test.png"
        test_file.write_bytes(b"fake image data")
        
        image_id = container.register_image(str(test_file))
        
        assert image_id.startswith("img_")
        assert container.image_storage.get(image_id) is not None


# Check if MCP is installed
def _check_mcp_installed():
    try:
        import mcp
        return True
    except ImportError:
        return False


class TestMCPServerCreation:
    """Test MCP server creation."""
    
    @pytest.mark.skipif(
        not _check_mcp_installed(),
        reason="MCP package not installed"
    )
    def test_create_mcp_app(self):
        """Test creating MCP app."""
        from medrax.mcp.server import create_mcp_app
        
        app = create_mcp_app(
            name="test-server",
            device="cpu",
            lazy_load=True,
        )
        
        assert app is not None


# Fixtures
@pytest.fixture
def sample_image(tmp_path):
    """Create a sample test image."""
    import numpy as np
    from PIL import Image
    
    # Create a simple grayscale image
    img_array = np.random.randint(0, 255, (224, 224), dtype=np.uint8)
    img = Image.fromarray(img_array)
    
    path = tmp_path / "sample.png"
    img.save(path)
    
    return path


@pytest.fixture
def service_container(tmp_path):
    """Create a service container for testing."""
    from medrax.mcp.application.services import MedRAXServiceContainer
    
    return MedRAXServiceContainer(
        device="cpu",
        temp_dir=tmp_path,
        lazy_load=True,
    )

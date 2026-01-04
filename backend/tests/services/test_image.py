import pytest


def test_image_service_interface():
    """Test image service has required interface."""
    from moana.services.image.base import BaseImageService

    assert hasattr(BaseImageService, "generate")


def test_flux_service_initialization():
    """Test Flux service can be initialized."""
    from moana.services.image.flux import FluxService

    service = FluxService()
    assert service is not None

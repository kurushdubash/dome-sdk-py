"""Tests for type definitions."""

from dome_api_sdk.types import APIResponse, HealthCheckResponse


class TestHealthCheckResponse:
    """Test cases for HealthCheckResponse."""

    def test_from_dict(self) -> None:
        """Test creating HealthCheckResponse from dictionary."""
        data = {
            "status": "healthy",
            "timestamp": "2023-01-01T00:00:00Z"
        }
        
        response = HealthCheckResponse.from_dict(data)
        
        assert response.status == "healthy"
        assert response.timestamp == "2023-01-01T00:00:00Z"

    def test_frozen_dataclass(self) -> None:
        """Test that HealthCheckResponse is immutable."""
        response = HealthCheckResponse(
            status="healthy",
            timestamp="2023-01-01T00:00:00Z"
        )
        
        # Should not be able to modify fields
        try:
            response.status = "unhealthy"  # type: ignore
            assert False, "Should not be able to modify frozen dataclass"
        except AttributeError:
            pass  # Expected

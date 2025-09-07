"""Tests for the DomeClient class."""

import os
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from dome_api_sdk import DomeClient
from dome_api_sdk.types import HealthCheckResponse


class TestDomeClient:
    """Test cases for DomeClient."""

    def test_constructor_default(self) -> None:
        """Test DomeClient constructor with default configuration."""
        client = DomeClient()
        assert client._api_key == ""
        assert client._base_url == "https://api.domeapi.io"
        assert client._timeout == 30.0

    def test_constructor_with_config(self) -> None:
        """Test DomeClient constructor with custom configuration."""
        config = {
            "api_key": "test-api-key",
            "base_url": "https://test.api.com",
            "timeout": 60.0,
        }
        client = DomeClient(config)
        assert client._api_key == "test-api-key"
        assert client._base_url == "https://test.api.com"
        assert client._timeout == 60.0

    @patch.dict(os.environ, {"DOME_API_KEY": "env-api-key"})
    def test_constructor_with_env_var(self) -> None:
        """Test DomeClient constructor uses environment variable."""
        client = DomeClient()
        assert client._api_key == "env-api-key"
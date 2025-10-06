"""Tests for the DomeClient class."""

import os
from unittest.mock import patch

import pytest

from dome_api_sdk import DomeClient


class TestDomeClient:
    """Test cases for DomeClient."""

    @patch.dict(os.environ, {"DOME_API_KEY": "test-env-key"})
    def test_constructor_default(self) -> None:
        """Test DomeClient constructor with default configuration."""
        client = DomeClient()
        assert client.polymarket is not None
        assert client.matching_markets is not None

    def test_constructor_with_config(self) -> None:
        """Test DomeClient constructor with custom configuration."""
        config = {
            "api_key": "test-api-key",
            "base_url": "https://test.api.com",
            "timeout": 60.0,
        }
        client = DomeClient(config)
        assert client.polymarket is not None
        assert client.matching_markets is not None

    @patch.dict(os.environ, {"DOME_API_KEY": "env-api-key"})
    def test_constructor_with_env_var(self) -> None:
        """Test DomeClient constructor uses environment variable."""
        client = DomeClient()
        assert client.polymarket is not None
        assert client.matching_markets is not None

    def test_constructor_raises_error_without_api_key(self) -> None:
        """Test DomeClient constructor raises error without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="DOME_API_KEY is required"):
                DomeClient()

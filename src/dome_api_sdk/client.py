"""Main Dome SDK Client implementation."""

import os
from typing import Any, Dict, Optional

import httpx

from .types import APIResponse, DomeSDKConfig, HTTPMethod, HealthCheckResponse

__all__ = ["DomeClient"]


class DomeClient:
    """Main Dome SDK Client.

    Provides a comprehensive Python SDK for interacting with Dome services.
    Features include user management, event handling, and API communication.

    Example:
        ```python
        from dome_api_sdk import DomeClient

        dome = DomeClient({
            "api_key": "your-api-key"
        })

        health = await dome.health_check()
        ```
    """

    def __init__(self, config: Optional[DomeSDKConfig] = None) -> None:
        """Creates a new instance of the Dome SDK.

        Args:
            config: Configuration options for the SDK
        """
        if config is None:
            config = {}

        self._api_key = config.get("api_key") or os.getenv("DOME_API_KEY", "")
        self._base_url = config.get("base_url") or "https://api.domeapi.io"
        self._timeout = config.get("timeout") or 30.0

        # Initialize HTTP client
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            headers=self._get_default_headers(),
        )

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for all requests."""
        headers = {
            "User-Agent": "dome-api-sdk-python/0.0.1",
            "Content-Type": "application/json",
        }

        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        return headers

    async def _make_request(
        self,
        method: HTTPMethod,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> APIResponse:
        """Makes a generic HTTP request.

        Args:
            method: HTTP method to use
            endpoint: API endpoint to call
            data: Request data to send
            headers: Additional headers to include

        Returns:
            APIResponse containing the response data

        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        request_headers = self._get_default_headers()
        if headers:
            request_headers.update(headers)

        try:
            response = await self._client.request(
                method=method,
                url=endpoint,
                json=data,
                headers=request_headers,
            )
            response.raise_for_status()

            return APIResponse(
                data=response.json(),
                status_code=response.status_code,
                headers=dict(response.headers),
            )

        except httpx.HTTPError as e:
            raise e

    async def health_check(self) -> HealthCheckResponse:
        """Performs a health check on the Dome API.

        Returns:
            HealthCheckResponse containing the health status

        Raises:
            httpx.HTTPStatusError: If the health check fails
        """
        response = await self._make_request("GET", "/health")
        return HealthCheckResponse.from_dict(response.data)

    async def close(self) -> None:
        """Close the HTTP client and cleanup resources."""
        await self._client.aclose()

    async def __aenter__(self) -> "DomeClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

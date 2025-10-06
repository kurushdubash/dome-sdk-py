"""Base client class for the Dome SDK."""

import os
from typing import Any, Dict, Optional

import httpx

from .types import DomeSDKConfig, RequestConfig

__all__ = ["BaseClient"]


class BaseClient:
    """Base client class that provides common HTTP functionality for all Dome API endpoints."""

    def __init__(self, config: DomeSDKConfig) -> None:
        """Initialize the base client.
        
        Args:
            config: Configuration options for the SDK
            
        Raises:
            ValueError: If API key is not provided
        """
        if not config.get("api_key") and not os.getenv("DOME_API_KEY"):
            raise ValueError("DOME_API_KEY is required")
        
        self._api_key = config.get("api_key") or os.getenv("DOME_API_KEY", "")
        self._base_url = config.get("base_url") or "https://api.domeapi.io/v1"
        self._timeout = config.get("timeout") or 30.0

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        options: Optional[RequestConfig] = None,
    ) -> Any:
        """Make a generic HTTP request with authentication.
        
        Args:
            method: HTTP method to use
            endpoint: API endpoint to call
            params: Request parameters
            options: Optional request configuration
            
        Returns:
            Response data
            
        Raises:
            httpx.HTTPStatusError: If the request fails
            ValueError: If there's an API error
        """
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        
        if options and options.get("headers"):
            headers.update(options["headers"])
        
        timeout = (options.get("timeout") if options else None) or self._timeout
        
        with httpx.Client(timeout=timeout) as client:
            try:
                if method.upper() == "GET":
                    response = client.get(
                        f"{self._base_url}{endpoint}",
                        headers=headers,
                        params=params,
                    )
                else:
                    response = client.request(
                        method=method,
                        url=f"{self._base_url}{endpoint}",
                        headers=headers,
                        json=params,
                    )
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 400:
                    try:
                        error_data = e.response.json()
                        if isinstance(error_data, dict) and "error" in error_data:
                            raise ValueError(
                                f"API Error: {error_data['error']} - {error_data.get('message', 'Unknown error')}"
                            )
                    except (ValueError, KeyError):
                        pass
                
                raise ValueError(f"Request failed: {e.response.status_code} {e.response.text}")
            except httpx.RequestError as e:
                raise ValueError(f"Request failed: {str(e)}")

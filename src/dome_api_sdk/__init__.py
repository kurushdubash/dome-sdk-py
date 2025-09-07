"""Dome SDK - A comprehensive Python SDK for Dome API.

This package provides a type-safe, async-first SDK for interacting with Dome services.

Example:
    ```python
    import asyncio
    from dome_api_sdk import DomeClient

    async def main():
        async with DomeClient({"api_key": "your-api-key"}) as dome:
            health = await dome.health_check()
            print(f"API Status: {health.status}")

    asyncio.run(main())
    ```
"""

from typing import Optional

from .client import DomeClient
from .types import (
    APIResponse,
    DomeSDKConfig,
    HTTPMethod,
    HealthCheckResponse,
)

__version__ = "0.0.1"
__author__ = "Kurush Dubash, Kunal Roy"
__email__ = "kurush@dome.com, kunal@dome.com"
__license__ = "MIT"

__all__ = [
    "DomeClient",
    "DomeSDKConfig", 
    "APIResponse",
    "HTTPMethod",
    "HealthCheckResponse",
    "__version__",
]

# Default client instance for convenience  
default_client: Optional[DomeClient] = None


def get_default_client() -> DomeClient:
    """Get or create the default client instance.
    
    Returns:
        DomeClient: The default client instance
        
    Note:
        This creates a client with default configuration (no API key).
        For production use, create a client with proper configuration.
    """
    global default_client
    if default_client is None:
        default_client = DomeClient()
    return default_client

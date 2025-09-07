"""Type definitions for the Dome SDK."""

import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Union

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = [
    "DomeSDKConfig",
    "HealthCheckResponse",
    "APIResponse",
    "HTTPMethod",
]

# Type aliases
HTTPMethod = Union["GET", "POST", "PUT", "DELETE"]


class DomeSDKConfig(TypedDict, total=False):
    """Configuration options for initializing the Dome SDK.
    
    Attributes:
        api_key: Authentication token for API requests
        base_url: Base URL for the API (defaults to production)
        timeout: Request timeout in seconds (defaults to 30)
    """
    
    api_key: Optional[str]
    base_url: Optional[str]
    timeout: Optional[float]


@dataclass(frozen=True)
class HealthCheckResponse:
    """Response from the health check endpoint.
    
    Attributes:
        status: Health status of the API
        timestamp: ISO timestamp of the health check
    """
    
    status: str
    timestamp: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HealthCheckResponse":
        """Create HealthCheckResponse from dictionary data."""
        return cls(
            status=data["status"],
            timestamp=data["timestamp"],
        )


@dataclass(frozen=True)
class APIResponse:
    """Generic API response wrapper.
    
    Attributes:
        data: The actual response data
        status_code: HTTP status code
        headers: Response headers
    """
    
    data: Any
    status_code: int
    headers: Dict[str, str]

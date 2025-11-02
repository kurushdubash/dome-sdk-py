"""Kalshi client for the Dome SDK."""

from ..types import DomeSDKConfig
from .kalshi_endpoints import KalshiEndpoints

__all__ = ["KalshiClient"]


class KalshiClient:
    """Kalshi client that provides access to all Kalshi-related endpoints.

    Groups Kalshi market data and orderbook functionality.
    """

    def __init__(self, config: DomeSDKConfig) -> None:
        """Initialize the Kalshi client.

        Args:
            config: Configuration options for the SDK
        """
        kalshi_endpoints = KalshiEndpoints(config)
        self.markets = kalshi_endpoints
        self.orderbooks = kalshi_endpoints

"""Main Dome SDK Client implementation."""

from typing import Optional

from .endpoints import (
    AsyncMatchingMarketsEndpoints,
    AsyncPolymarketClient,
    MatchingMarketsEndpoints,
    PolymarketClient,
)
from .types import DomeSDKConfig

__all__ = ["DomeClient", "AsyncDomeClient"]


class AsyncDomeClient:
    """Main Dome SDK Client (Async version).

    Provides a comprehensive Python SDK for interacting with Dome API.
    Features include market data, wallet analytics, order tracking, and cross-platform market matching.
    """

    def __init__(self, config: Optional[DomeSDKConfig] = None) -> None:
        """Creates a new instance of the Dome SDK.

        Args:
            config: Configuration options for the SDK
        """
        if config is None:
            config = {}

        # Initialize all endpoint modules with the same config
        self.polymarket = AsyncPolymarketClient(config)
        self.matching_markets = AsyncMatchingMarketsEndpoints(config)


class DomeClient:
    """Main Dome SDK Client.

    Provides a comprehensive Python SDK for interacting with Dome API.
    Features include market data, wallet analytics, order tracking, and cross-platform market matching.
    """

    def __init__(self, config: Optional[DomeSDKConfig] = None) -> None:
        """Creates a new instance of the Dome SDK.

        Args:
            config: Configuration options for the SDK
        """
        if config is None:
            config = {}

        # Initialize all endpoint modules with the same config
        self.polymarket = PolymarketClient(config)
        self.matching_markets = MatchingMarketsEndpoints(config)

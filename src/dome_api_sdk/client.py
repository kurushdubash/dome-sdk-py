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
    def __init__(self, config: Optional[DomeSDKConfig] = None) -> None:
        if config is None:
            config = {}

        # Initialize all endpoint modules with the same config
        self.polymarket = AsyncPolymarketClient(config)
        self.matching_markets = AsyncMatchingMarketsEndpoints(config)


class DomeClient:
    def __init__(self, config: Optional[DomeSDKConfig] = None) -> None:
        if config is None:
            config = {}

        # Initialize all endpoint modules with the same config
        self.polymarket = PolymarketClient(config)
        self.matching_markets = MatchingMarketsEndpoints(config)

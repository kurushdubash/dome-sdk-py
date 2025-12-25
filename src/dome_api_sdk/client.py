"""Main Dome SDK Client implementation."""

from typing import Optional

from .endpoints import (
    CryptoPricesClient,
    KalshiClient,
    MatchingMarketsEndpoints,
    PolymarketClient,
)
from .types import DomeSDKConfig

__all__ = ["DomeClient"]


class DomeClient:
    """Main Dome SDK Client.

    Provides a comprehensive Python SDK for interacting with Dome API.
    Features include market data, wallet analytics, order tracking, and cross-platform market matching.

    Example:
        ```python
        from dome_api_sdk import DomeClient

        # Initialize the client with your API key
        dome = DomeClient({"api_key": "your-api-key"})

        # Get market price
        market_price = dome.polymarket.markets.get_market_price({
            "token_id": "1234567890"
        })
        print(f"Market Price: {market_price.price}")
        ```
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
        self.kalshi = KalshiClient(config)
        self.matching_markets = MatchingMarketsEndpoints(config)
        self.crypto_prices = CryptoPricesClient(config)

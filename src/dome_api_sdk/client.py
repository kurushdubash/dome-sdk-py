"""Main Dome SDK Client implementation."""

from typing import Optional

from .endpoints import MatchingMarketsEndpoints, PolymarketClient
from .types import DomeSDKConfig

__all__ = ["DomeClient"]


class DomeClient:
    """Main Dome SDK Client.

    Provides a comprehensive Python SDK for interacting with Dome API.
    Features include market data, wallet analytics, order tracking, and cross-platform market matching.

    Example:
        ```python
        import asyncio
        from dome_api_sdk import DomeClient

        async def main():
            async with DomeClient({"api_key": "your-api-key"}) as dome:
                # Get market price
                market_price = await dome.polymarket.markets.get_market_price({
                    "token_id": "1234567890"
                })
                print(f"Market Price: {market_price.price}")

        asyncio.run(main())
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
        self.matching_markets = MatchingMarketsEndpoints(config)

    async def __aenter__(self) -> "DomeClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        # No cleanup needed as we don't maintain persistent connections
        pass

    def close(self) -> None:
        """Close the client (for synchronous usage).
        
        This method is provided for compatibility with synchronous usage patterns.
        Since we don't maintain persistent connections, this is a no-op.
        """
        # No cleanup needed as we don't maintain persistent connections
        pass

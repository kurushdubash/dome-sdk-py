"""Polymarket client for the Dome SDK."""

from ..types import DomeSDKConfig
from .market_endpoints import MarketEndpoints, AsyncMarketEndpoints
from .orders_endpoints import OrdersEndpoints, AsyncOrdersEndpoint
from .wallet_endpoints import WalletEndpoints

__all__ = ["PolymarketClient"]


class AsyncPolymarketClient:
    def __init__(self, config: DomeSDKConfig) -> None:
        self.markets = AsyncMarketEndpoints(config)
        self.orders = AsyncOrdersEndpoint(config)


class PolymarketClient:
    """Polymarket client that provides access to all Polymarket-related endpoints.

    Groups market data, wallet analytics, and order functionality.
    """

    def __init__(self, config: DomeSDKConfig) -> None:
        """Initialize the Polymarket client.

        Args:
            config: Configuration options for the SDK
        """
        self.markets = MarketEndpoints(config)
        self.wallet = WalletEndpoints(config)
        self.orders = OrdersEndpoints(config)

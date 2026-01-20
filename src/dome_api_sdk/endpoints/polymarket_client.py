"""Polymarket client for the Dome SDK."""

import os

from ..types import DomeSDKConfig
from .activity_endpoints import ActivityEndpoints
from .events_endpoints import EventsEndpoints
from .market_endpoints import MarketEndpoints
from .orders_endpoints import OrdersEndpoints
from .polymarket_websocket import PolymarketWebSocketClient
from .wallet_endpoints import WalletEndpoints

__all__ = ["PolymarketClient"]


class PolymarketClient:
    """Polymarket client that provides access to all Polymarket-related endpoints.

    Groups market data, wallet analytics, order functionality, and WebSocket support.
    """

    def __init__(self, config: DomeSDKConfig) -> None:
        """Initialize the Polymarket client.

        Args:
            config: Configuration options for the SDK
        """
        self.markets = MarketEndpoints(config)
        self.events = EventsEndpoints(config)
        self.wallet = WalletEndpoints(config)
        self.orders = OrdersEndpoints(config)
        self.activity = ActivityEndpoints(config)

        # Initialize WebSocket client
        api_key = config.get("api_key") or os.getenv("DOME_API_KEY", "")
        self.websocket = PolymarketWebSocketClient(api_key=api_key)

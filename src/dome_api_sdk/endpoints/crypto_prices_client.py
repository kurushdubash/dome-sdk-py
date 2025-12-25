"""Crypto prices client for the Dome SDK."""

from ..types import DomeSDKConfig
from .crypto_prices_endpoints import CryptoPricesEndpoints

__all__ = ["CryptoPricesClient"]


class CryptoPricesClient:
    """Crypto prices client that provides access to all crypto prices-related endpoints.

    Groups Binance and Chainlink crypto price data functionality.
    """

    def __init__(self, config: DomeSDKConfig) -> None:
        """Initialize the crypto prices client.

        Args:
            config: Configuration options for the SDK
        """
        crypto_prices_endpoints = CryptoPricesEndpoints(config)
        self.binance = crypto_prices_endpoints
        self.chainlink = crypto_prices_endpoints

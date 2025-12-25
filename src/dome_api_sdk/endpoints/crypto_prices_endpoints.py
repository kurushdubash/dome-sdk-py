"""Crypto prices-related endpoints for the Dome API."""

from typing import Any, Dict, Optional

from ..base_client import BaseClient
from ..types import (
    CryptoPrice,
    CryptoPricesResponse,
    GetBinanceCryptoPricesParams,
    GetChainlinkCryptoPricesParams,
    RequestConfig,
)

__all__ = ["CryptoPricesEndpoints"]


class CryptoPricesEndpoints(BaseClient):
    """Crypto prices-related endpoints for the Dome API.

    Handles crypto price data from Binance and Chainlink.
    """

    def get_binance_prices(
        self,
        params: GetBinanceCryptoPricesParams,
        options: Optional[RequestConfig] = None,
    ) -> CryptoPricesResponse:
        """Get Binance Crypto Prices.

        Fetches historical crypto price data from Binance. Returns price data for a specific
        currency pair over an optional time range. When no time range is provided, returns
        the most recent price (limit 1). All timestamps are in Unix milliseconds.

        Currency Format: Lowercase, no separators (e.g., btcusdt, ethusdt, solusdt, xrpusdt)

        Args:
            params: Parameters for the Binance crypto prices request
            options: Optional request configuration

        Returns:
            Crypto prices data with pagination

        Raises:
            ValueError: If the request fails
        """
        currency = params["currency"]
        start_time = params.get("start_time")
        end_time = params.get("end_time")
        limit = params.get("limit")
        pagination_key = params.get("pagination_key")

        query_params: Dict[str, Any] = {
            "currency": currency,
        }

        if start_time is not None:
            query_params["start_time"] = start_time
        if end_time is not None:
            query_params["end_time"] = end_time
        if limit is not None:
            query_params["limit"] = limit
        if pagination_key is not None:
            query_params["pagination_key"] = pagination_key

        response_data = self._make_request(
            "GET",
            "/crypto-prices/binance",
            query_params,
            options,
        )

        # Parse prices
        prices = []
        for price_data in response_data["prices"]:
            prices.append(
                CryptoPrice(
                    symbol=price_data["symbol"],
                    value=price_data["value"],
                    timestamp=price_data["timestamp"],
                )
            )

        return CryptoPricesResponse(
            prices=prices,
            pagination_key=response_data.get("pagination_key"),
            total=response_data.get("total", len(prices)),
        )

    def get_chainlink_prices(
        self,
        params: GetChainlinkCryptoPricesParams,
        options: Optional[RequestConfig] = None,
    ) -> CryptoPricesResponse:
        """Get Chainlink Crypto Prices.

        Fetches historical crypto price data from Chainlink. Returns price data for a specific
        currency pair over an optional time range. When no time range is provided, returns
        the most recent price (limit 1). All timestamps are in Unix milliseconds.

        Currency Format: Slash-separated (e.g., btc/usd, eth/usd, sol/usd, xrp/usd)

        Args:
            params: Parameters for the Chainlink crypto prices request
            options: Optional request configuration

        Returns:
            Crypto prices data with pagination

        Raises:
            ValueError: If the request fails
        """
        currency = params["currency"]
        start_time = params.get("start_time")
        end_time = params.get("end_time")
        limit = params.get("limit")
        pagination_key = params.get("pagination_key")

        query_params: Dict[str, Any] = {
            "currency": currency,
        }

        if start_time is not None:
            query_params["start_time"] = start_time
        if end_time is not None:
            query_params["end_time"] = end_time
        if limit is not None:
            query_params["limit"] = limit
        if pagination_key is not None:
            query_params["pagination_key"] = pagination_key

        response_data = self._make_request(
            "GET",
            "/crypto-prices/chainlink",
            query_params,
            options,
        )

        # Parse prices
        prices = []
        for price_data in response_data["prices"]:
            prices.append(
                CryptoPrice(
                    symbol=price_data["symbol"],
                    value=price_data["value"],
                    timestamp=price_data["timestamp"],
                )
            )

        return CryptoPricesResponse(
            prices=prices,
            pagination_key=response_data.get("pagination_key"),
            total=response_data.get("total", len(prices)),
        )

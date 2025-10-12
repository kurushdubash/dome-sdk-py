"""Market-related endpoints for the Dome API."""

from typing import Any, Optional, Union

from ..base_client import AsyncBaseClient, BaseClient
from ..types import (
    CandlesticksResponse,
    GetCandlesticksParams,
    GetMarketPriceParams,
    MarketPriceResponse,
    RequestConfig,
)

__all__ = ["AsyncMarketEndpoints", "MarketEndpoints"]


class BaseMarketEndpoints:
    def _prepare_get_candlesticks(
        self,
        params: GetCandlesticksParams,
        options: Optional[RequestConfig] = None,
    ) -> tuple[str, str, dict[str, Any], Optional[RequestConfig]]:
        condition_id = params["condition_id"]
        start_time = params["start_time"]
        end_time = params["end_time"]
        interval = params.get("interval")

        query_params = {
            "start_time": start_time,
            "end_time": end_time,
        }

        if interval is not None:
            query_params["interval"] = interval

        return (
            "GET",
            f"/polymarket/candlesticks/{condition_id}",
            query_params,
            options,
        )

    def _parse_get_candlesticks(
        self, raw_response: dict[str, Any]
    ) -> CandlesticksResponse:
        # Parse the complex candlestick response structure
        from ..types import CandlestickData, TokenMetadata

        candlesticks = []

        for candlestick_tuple in raw_response["candlesticks"]:
            # Each tuple contains [candlestick_data_list, token_metadata]
            if len(candlestick_tuple) == 2:
                candlestick_data_list, token_metadata = candlestick_tuple

                # Parse candlestick data
                parsed_candlestick_data = []
                for data in candlestick_data_list:
                    parsed_candlestick_data.append(
                        CandlestickData(
                            end_period_ts=data["end_period_ts"],
                            open_interest=data["open_interest"],
                            price=data["price"],
                            volume=data["volume"],
                            yes_ask=data["yes_ask"],
                            yes_bid=data["yes_bid"],
                        )
                    )

                # Parse token metadata
                parsed_token_metadata = TokenMetadata(
                    token_id=token_metadata["token_id"]
                )

                parsed_tuple: list[Union[CandlestickData, TokenMetadata]] = (
                    parsed_candlestick_data + [parsed_token_metadata]
                )
                candlesticks.append(parsed_tuple)

        return CandlesticksResponse(candlesticks=candlesticks)

    def _prepare_get_market_price(
        self,
        params: GetMarketPriceParams,
        options: Optional[RequestConfig] = None,
    ) -> tuple[str, str, dict[str, Any], Optional[RequestConfig]]:
        token_id = params["token_id"]
        at_time = params.get("at_time")

        query_params: dict[str, Any] = {}
        if at_time is not None:
            query_params["at_time"] = at_time

        return (
            "GET",
            f"/polymarket/market-price/{token_id}",
            query_params,
            options,
        )

    def _parse_get_market_price(
        self, raw_response: dict[str, Any]
    ) -> MarketPriceResponse:
        return MarketPriceResponse(
            price=raw_response["price"],
            at_time=raw_response["at_time"],
        )


class MarketEndpoints(BaseClient, BaseMarketEndpoints):
    """Market-related endpoints for the Dome API.

    Handles market price and candlestick data.
    """

    def get_candlesticks(
        self, params: GetCandlesticksParams, options: Optional[RequestConfig] = None
    ) -> CandlesticksResponse:
        """Get Candlestick Data.

        Fetches historical candlestick data for a market identified by condition_id,
        over a specified interval.

        Args:
            params: Parameters for the candlestick request
            options: Optional request configuration

        Returns:
            Candlestick data

        Raises:
            ValueError: If the request fails
        """
        raw_response = self._make_request(
            *self._prepare_get_candlesticks(params, options)
        )
        parsed_response = self._parse_get_candlesticks(raw_response)
        return parsed_response

    def get_market_price(
        self, params: GetMarketPriceParams, options: Optional[RequestConfig] = None
    ) -> MarketPriceResponse:
        """Get Market Price.

        Fetches the current market price for a market by token_id.
        Allows historical lookups via the at_time query parameter.

        Args:
            params: Parameters for the market price request
            options: Optional request configuration

        Returns:
            Market price data

        Raises:
            ValueError: If the request fails
        """
        raw_response = self._make_request(
            *self._prepare_get_market_price(params, options)
        )
        parsed_response = self._parse_get_market_price(raw_response)
        return parsed_response


class AsyncMarketEndpoints(AsyncBaseClient, BaseMarketEndpoints):
    async def get_candlesticks(
        self, params: GetCandlesticksParams, options: Optional[RequestConfig] = None
    ) -> CandlesticksResponse:
        """Get Candlestick Data.

        Fetches historical candlestick data for a market identified by condition_id,
        over a specified interval.

        Args:
            params: Parameters for the candlestick request
            options: Optional request configuration

        Returns:
            Candlestick data

        Raises:
            ValueError: If the request fails
        """
        raw_response = await self._make_request(
            *self._prepare_get_candlesticks(params, options)
        )
        parsed_response = self._parse_get_candlesticks(raw_response)
        return parsed_response

    async def get_market_price(
        self, params: GetMarketPriceParams, options: Optional[RequestConfig] = None
    ) -> MarketPriceResponse:
        """Get Market Price.

        Fetches the current market price for a market by token_id.
        Allows historical lookups via the at_time query parameter.

        Args:
            params: Parameters for the market price request
            options: Optional request configuration

        Returns:
            Market price data

        Raises:
            ValueError: If the request fails
        """
        raw_response = await self._make_request(
            *self._prepare_get_market_price(params, options)
        )
        parsed_response = self._parse_get_market_price(raw_response)
        return parsed_response

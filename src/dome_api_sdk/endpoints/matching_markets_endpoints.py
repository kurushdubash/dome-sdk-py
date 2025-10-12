"""Matching Markets-related endpoints for the Dome API."""

from typing import Any, Optional

from ..base_client import AsyncBaseClient, BaseClient
from ..types import (
    GetMatchingMarketsBySportParams,
    GetMatchingMarketsParams,
    KalshiMarket,
    MarketData,
    MatchingMarketsBySportResponse,
    MatchingMarketsResponse,
    PolymarketMarket,
    RequestConfig,
)

__all__ = ["MatchingMarketsEndpoints", "AsyncMatchingMarketsEndpoints"]


class BaseMatchingMarketsEndpoints:
    """Matching Markets-related endpoints for the Dome API.

    Handles cross-platform market matching functionality.
    """

    def _prepare_get_matching_markets(
        self,
        params: GetMatchingMarketsParams,
        options: Optional[RequestConfig] = None,
    ) -> tuple[str, str, dict[str, Any], Optional[RequestConfig]]:
        """Prepare the request for get_matching_markets. This does NOT handle transport, but rather prepares a request in the format needed for the BaseClient's _make_request."""
        query_params: dict[str, Any] = {}

        if params.get("polymarket_market_slug"):
            query_params["polymarket_market_slug"] = params["polymarket_market_slug"]

        if params.get("kalshi_event_ticker"):
            query_params["kalshi_event_ticker"] = params["kalshi_event_ticker"]

        return (
            "GET",
            "/matching-markets/sports/",
            query_params,
            options,
        )

    def _parse_get_matching_markets(
        self, raw_response: dict[str, Any]
    ) -> MatchingMarketsResponse:
        """Parses the raw json of the get_matching_markets endpoint."""
        # Parse market data
        parsed_markets: dict[str, list[MarketData]] = {}

        for key, markets in raw_response["markets"].items():
            parsed_markets[key] = []
            for market in markets:
                if market["platform"] == "KALSHI":
                    parsed_markets[key].append(
                        KalshiMarket(
                            platform="KALSHI",
                            event_ticker=market["event_ticker"],
                            market_tickers=market["market_tickers"],
                        )
                    )
                elif market["platform"] == "POLYMARKET":
                    parsed_markets[key].append(
                        PolymarketMarket(
                            platform="POLYMARKET",
                            market_slug=market["market_slug"],
                            token_ids=market["token_ids"],
                        )
                    )

        return MatchingMarketsResponse(markets=parsed_markets)

    def _prepare_get_matching_markets_by_sport(
        self,
        params: GetMatchingMarketsBySportParams,
        options: Optional[RequestConfig] = None,
    ) -> tuple[str, str, dict[str, Any], Optional[RequestConfig]]:
        """Prepare the request for get_matching_markets_by_sport. This does NOT handle transport, but rather prepares a request in the format needed for the BaseClient's _make_request."""
        sport = params["sport"]
        date = params["date"]

        query_params: dict[str, Any] = {"date": date}

        return (
            "GET",
            f"/matching-markets/sports/{sport}/",
            query_params,
            options,
        )

    def _parse_get_matching_markets_by_sport(
        self, raw_response: dict[str, Any]
    ) -> MatchingMarketsBySportResponse:
        """Parses the raw json of the get_matching_markets_by_sport endpoint."""
        # Parse market data
        parsed_markets: dict[str, list[MarketData]] = {}

        for key, markets in raw_response["markets"].items():
            parsed_markets[key] = []
            for market in markets:
                if market["platform"] == "KALSHI":
                    parsed_markets[key].append(
                        KalshiMarket(
                            platform="KALSHI",
                            event_ticker=market["event_ticker"],
                            market_tickers=market["market_tickers"],
                        )
                    )
                elif market["platform"] == "POLYMARKET":
                    parsed_markets[key].append(
                        PolymarketMarket(
                            platform="POLYMARKET",
                            market_slug=market["market_slug"],
                            token_ids=market["token_ids"],
                        )
                    )

        return MatchingMarketsBySportResponse(
            markets=parsed_markets,
            sport=raw_response["sport"],
            date=raw_response["date"],
        )


class AsyncMatchingMarketsEndpoints(AsyncBaseClient, BaseMatchingMarketsEndpoints):
    """Matching Markets-related endpoints for the Dome API (Async version).

    Handles cross-platform market matching functionality.
    """

    async def get_matching_markets(
        self, params: GetMatchingMarketsParams, options: Optional[RequestConfig] = None
    ) -> MatchingMarketsResponse:
        """Get Matching Markets for Sports.

        Find equivalent markets across different prediction market platforms (Polymarket, Kalshi, etc.) for sports events.

        Args:
            params: Parameters for the matching markets request
            options: Optional request configuration

        Returns:
            Matching markets data

        Raises:
            ValueError: If the request fails
        """
        raw_response = await self._make_request(
            *self._prepare_get_matching_markets(params, options)
        )
        parsed_response = self._parse_get_matching_markets(raw_response)
        return parsed_response

    async def get_matching_markets_by_sport(
        self,
        params: GetMatchingMarketsBySportParams,
        options: Optional[RequestConfig] = None,
    ) -> MatchingMarketsBySportResponse:
        """Get Matching Markets for Sports by Sport and Date.

        Find equivalent markets across different prediction market platforms for sports events by sport and date.

        Args:
            params: Parameters for the matching markets by sport request
            options: Optional request configuration

        Returns:
            Matching markets data with sport and date

        Raises:
            ValueError: If the request fails
        """
        raw_response = await self._make_request(
            *self._prepare_get_matching_markets_by_sport(params, options)
        )
        parsed_response = self._parse_get_matching_markets_by_sport(raw_response)
        return parsed_response


class MatchingMarketsEndpoints(BaseClient, BaseMatchingMarketsEndpoints):
    """Matching Markets-related endpoints for the Dome API.

    Handles cross-platform market matching functionality.
    """

    def get_matching_markets(
        self, params: GetMatchingMarketsParams, options: Optional[RequestConfig] = None
    ) -> MatchingMarketsResponse:
        """Get Matching Markets for Sports.

        Find equivalent markets across different prediction market platforms (Polymarket, Kalshi, etc.) for sports events.

        Args:
            params: Parameters for the matching markets request
            options: Optional request configuration

        Returns:
            Matching markets data

        Raises:
            ValueError: If the request fails
        """
        raw_response = self._make_request(
            *self._prepare_get_matching_markets(params, options)
        )
        parsed_response = self._parse_get_matching_markets(raw_response)
        return parsed_response

    def get_matching_markets_by_sport(
        self,
        params: GetMatchingMarketsBySportParams,
        options: Optional[RequestConfig] = None,
    ) -> MatchingMarketsBySportResponse:
        """Get Matching Markets for Sports by Sport and Date.

        Find equivalent markets across different prediction market platforms for sports events by sport and date.

        Args:
            params: Parameters for the matching markets by sport request
            options: Optional request configuration

        Returns:
            Matching markets data with sport and date

        Raises:
            ValueError: If the request fails
        """
        raw_response = self._make_request(
            *self._prepare_get_matching_markets_by_sport(params, options)
        )
        parsed_response = self._parse_get_matching_markets_by_sport(raw_response)
        return parsed_response

"""Kalshi-related endpoints for the Dome API."""

from typing import Any, Dict, Optional

from ..base_client import BaseClient
from ..types import (
    GetKalshiMarketPriceParams,
    GetKalshiMarketsParams,
    GetKalshiOrderbooksParams,
    GetKalshiTradesParams,
    KalshiMarketData,
    KalshiMarketPriceResponse,
    KalshiMarketsResponse,
    KalshiOrderbook,
    KalshiOrderbookPagination,
    KalshiOrderbookSnapshot,
    KalshiOrderbooksResponse,
    KalshiTradesResponse,
    Pagination,
    RequestConfig,
)

__all__ = ["KalshiEndpoints"]


class KalshiEndpoints(BaseClient):
    """Kalshi-related endpoints for the Dome API.

    Handles Kalshi market data and orderbook history.
    """

    def get_markets(
        self,
        params: GetKalshiMarketsParams,
        options: Optional[RequestConfig] = None,
    ) -> KalshiMarketsResponse:
        """Get Kalshi Markets.

        Fetches Kalshi market data with optional filtering by market ticker,
        event ticker, status, and volume.

        Args:
            params: Parameters for the Kalshi markets request
            options: Optional request configuration

        Returns:
            Kalshi markets data with pagination

        Raises:
            ValueError: If the request fails
        """
        query_params: Dict[str, Any] = {}

        # Handle array parameters
        if params.get("market_ticker"):
            query_params["market_ticker"] = params["market_ticker"]
        if params.get("event_ticker"):
            query_params["event_ticker"] = params["event_ticker"]
        if params.get("search"):
            query_params["search"] = params["search"]
        if params.get("status"):
            query_params["status"] = params["status"]
        if params.get("min_volume") is not None:
            query_params["min_volume"] = params["min_volume"]
        if params.get("limit") is not None:
            query_params["limit"] = params["limit"]
        if params.get("pagination_key"):
            query_params["pagination_key"] = params["pagination_key"]

        response_data = self._make_request(
            "GET",
            "/kalshi/markets",
            query_params,
            options,
        )

        # Parse markets
        markets = []
        for market_data in response_data["markets"]:
            markets.append(
                KalshiMarketData(
                    event_ticker=market_data["event_ticker"],
                    market_ticker=market_data["market_ticker"],
                    title=market_data["title"],
                    start_time=market_data["start_time"],
                    end_time=market_data["end_time"],
                    close_time=market_data.get("close_time"),
                    status=market_data["status"],
                    last_price=market_data["last_price"],
                    volume=market_data["volume"],
                    volume_24h=market_data["volume_24h"],
                    result=market_data.get("result"),
                )
            )

        # Parse pagination
        pagination_data = response_data["pagination"]
        pagination = Pagination(
            limit=pagination_data["limit"],
            total=pagination_data["total"],
            has_more=pagination_data["has_more"],
            offset=pagination_data.get("offset"),
            pagination_key=pagination_data.get("pagination_key"),
        )

        return KalshiMarketsResponse(markets=markets, pagination=pagination)

    def get_orderbooks(
        self,
        params: GetKalshiOrderbooksParams,
        options: Optional[RequestConfig] = None,
    ) -> KalshiOrderbooksResponse:
        """Get Kalshi Orderbook History.

        Fetches historical orderbook snapshots for a specific Kalshi market (ticker)
        over a specified time range.

        Args:
            params: Parameters for the Kalshi orderbooks request
            options: Optional request configuration

        Returns:
            Kalshi orderbook history data with pagination

        Raises:
            ValueError: If the request fails
        """
        ticker = params["ticker"]
        start_time = params["start_time"]
        end_time = params["end_time"]

        query_params = {
            "ticker": ticker,
            "start_time": start_time,
            "end_time": end_time,
        }

        if params.get("limit") is not None:
            query_params["limit"] = params["limit"]

        response_data = self._make_request(
            "GET",
            "/kalshi/orderbooks",
            query_params,
            options,
        )

        # Parse snapshots
        snapshots = []
        for snapshot_data in response_data["snapshots"]:
            orderbook_data = snapshot_data["orderbook"]
            snapshots.append(
                KalshiOrderbookSnapshot(
                    orderbook=KalshiOrderbook(
                        yes=orderbook_data["yes"],
                        no=orderbook_data["no"],
                        yes_dollars=orderbook_data["yes_dollars"],
                        no_dollars=orderbook_data["no_dollars"],
                    ),
                    timestamp=snapshot_data["timestamp"],
                    ticker=snapshot_data["ticker"],
                )
            )

        # Parse pagination
        pagination_data = response_data["pagination"]
        pagination = KalshiOrderbookPagination(
            limit=pagination_data["limit"],
            count=pagination_data["count"],
            has_more=pagination_data["has_more"],
        )

        return KalshiOrderbooksResponse(snapshots=snapshots, pagination=pagination)

    def get_market_price(
        self,
        params: GetKalshiMarketPriceParams,
        options: Optional[RequestConfig] = None,
    ) -> KalshiMarketPriceResponse:
        """Get Kalshi Market Price.

        Fetches the current or historical market price for a Kalshi market by market ticker.
        Returns separate prices for yes and no sides.

        Args:
            params: Parameters for the Kalshi market price request
            options: Optional request configuration

        Returns:
            Kalshi market price data with yes and no sides

        Raises:
            ValueError: If the request fails
        """
        market_ticker = params["market_ticker"]

        query_params: Dict[str, Any] = {}
        if params.get("at_time") is not None:
            query_params["at_time"] = params["at_time"]

        response_data = self._make_request(
            "GET",
            f"/kalshi/market-price/{market_ticker}",
            query_params,
            options,
        )

        # Parse price sides
        from ..types import KalshiPriceSide

        yes_side = KalshiPriceSide(
            price=response_data["yes"]["price"],
            at_time=response_data["yes"]["at_time"],
        )
        no_side = KalshiPriceSide(
            price=response_data["no"]["price"],
            at_time=response_data["no"]["at_time"],
        )

        return KalshiMarketPriceResponse(yes=yes_side, no=no_side)

    def get_trades(
        self,
        params: GetKalshiTradesParams,
        options: Optional[RequestConfig] = None,
    ) -> KalshiTradesResponse:
        """Get Kalshi Trades.

        Fetches historical trade data for Kalshi markets with optional filtering
        by ticker and time range.

        Args:
            params: Parameters for the Kalshi trades request
            options: Optional request configuration

        Returns:
            Kalshi trades data with pagination

        Raises:
            ValueError: If the request fails
        """
        query_params: Dict[str, Any] = {}

        if params.get("ticker"):
            query_params["ticker"] = params["ticker"]
        if params.get("start_time") is not None:
            query_params["start_time"] = params["start_time"]
        if params.get("end_time") is not None:
            query_params["end_time"] = params["end_time"]
        if params.get("limit") is not None:
            query_params["limit"] = params["limit"]
        if params.get("pagination_key"):
            query_params["pagination_key"] = params["pagination_key"]

        response_data = self._make_request(
            "GET",
            "/kalshi/trades",
            query_params,
            options,
        )

        # Parse trades
        from ..types import KalshiTrade

        trades = []
        for trade_data in response_data["trades"]:
            trades.append(
                KalshiTrade(
                    trade_id=trade_data["trade_id"],
                    market_ticker=trade_data["market_ticker"],
                    count=trade_data["count"],
                    yes_price=trade_data["yes_price"],
                    no_price=trade_data["no_price"],
                    yes_price_dollars=trade_data["yes_price_dollars"],
                    no_price_dollars=trade_data["no_price_dollars"],
                    taker_side=trade_data["taker_side"],
                    created_time=trade_data["created_time"],
                )
            )

        # Parse pagination
        pagination_data = response_data["pagination"]
        pagination = Pagination(
            limit=pagination_data["limit"],
            total=pagination_data["total"],
            has_more=pagination_data["has_more"],
            offset=pagination_data.get("offset"),
            pagination_key=pagination_data.get("pagination_key"),
        )

        return KalshiTradesResponse(trades=trades, pagination=pagination)

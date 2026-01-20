"""Market-related endpoints for the Dome API."""

from typing import Any, Dict, List, Optional, Union

from ..base_client import BaseClient
from ..types import (
    CandlesticksResponse,
    GetCandlesticksParams,
    GetMarketPriceParams,
    GetMarketsParams,
    GetOrderbooksParams,
    Market,
    MarketPriceResponse,
    MarketSide,
    MarketsResponse,
    OrderbookPagination,
    OrderbookSnapshot,
    OrderbooksResponse,
    Pagination,
    RequestConfig,
)

__all__ = ["MarketEndpoints"]


class MarketEndpoints(BaseClient):
    """Market-related endpoints for the Dome API.

    Handles market price and candlestick data.
    """

    def get_market_price(
        self,
        params: GetMarketPriceParams,
        options: Optional[RequestConfig] = None,
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
        token_id = params["token_id"]
        at_time = params.get("at_time")

        query_params: dict = {}
        if at_time is not None:
            query_params["at_time"] = at_time

        response_data = self._make_request(
            "GET",
            f"/polymarket/market-price/{token_id}",
            query_params,
            options,
        )

        return MarketPriceResponse(
            price=response_data["price"],
            at_time=response_data["at_time"],
        )

    def get_candlesticks(
        self,
        params: GetCandlesticksParams,
        options: Optional[RequestConfig] = None,
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

        response_data = self._make_request(
            "GET",
            f"/polymarket/candlesticks/{condition_id}",
            query_params,
            options,
        )

        # Parse the complex candlestick response structure
        from ..types import CandlestickData, TokenMetadata

        candlesticks = []

        for candlestick_tuple in response_data["candlesticks"]:
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

                parsed_tuple: List[Union[CandlestickData, TokenMetadata]] = (
                    parsed_candlestick_data + [parsed_token_metadata]
                )
                candlesticks.append(parsed_tuple)

        return CandlesticksResponse(candlesticks=candlesticks)

    def get_markets(
        self,
        params: GetMarketsParams,
        options: Optional[RequestConfig] = None,
    ) -> MarketsResponse:
        """Get Markets.

        Fetches market data with optional filtering and search functionality.
        Supports filtering by market slug, condition ID, or tags, as well as
        fuzzy search across market titles and descriptions.

        Args:
            params: Parameters for the markets request
            options: Optional request configuration

        Returns:
            Markets data with pagination

        Raises:
            ValueError: If the request fails
        """
        query_params: Dict[str, Any] = {}

        # Handle array parameters
        if params.get("market_slug"):
            query_params["market_slug"] = params["market_slug"]
        if params.get("event_slug"):
            query_params["event_slug"] = params["event_slug"]
        if params.get("condition_id"):
            query_params["condition_id"] = params["condition_id"]
        if params.get("token_id"):
            query_params["token_id"] = params["token_id"]
        if params.get("tags"):
            query_params["tags"] = params["tags"]
        if params.get("search"):
            query_params["search"] = params["search"]
        if params.get("status"):
            query_params["status"] = params["status"]
        if params.get("min_volume") is not None:
            query_params["min_volume"] = params["min_volume"]
        if params.get("start_time") is not None:
            query_params["start_time"] = params["start_time"]
        if params.get("end_time") is not None:
            query_params["end_time"] = params["end_time"]
        if params.get("limit") is not None:
            query_params["limit"] = params["limit"]
        if params.get("offset") is not None:
            query_params["offset"] = params["offset"]
        if params.get("pagination_key"):
            query_params["pagination_key"] = params["pagination_key"]

        response_data = self._make_request(
            "GET",
            "/polymarket/markets",
            query_params,
            options,
        )

        # Parse markets
        markets = []
        for market_data in response_data["markets"]:
            # Parse side_a
            side_a_data = market_data["side_a"]
            side_a = MarketSide(
                id=side_a_data["id"],
                label=side_a_data["label"],
            )

            # Parse side_b
            side_b_data = market_data["side_b"]
            side_b = MarketSide(
                id=side_b_data["id"],
                label=side_b_data["label"],
            )

            # Parse winning_side (nullable)
            winning_side = None
            if market_data.get("winning_side") is not None:
                winning_side_data = market_data["winning_side"]
                winning_side = MarketSide(
                    id=winning_side_data["id"],
                    label=winning_side_data["label"],
                )

            markets.append(
                Market(
                    market_slug=market_data["market_slug"],
                    condition_id=market_data["condition_id"],
                    title=market_data["title"],
                    start_time=market_data["start_time"],
                    end_time=market_data["end_time"],
                    completed_time=market_data.get("completed_time"),
                    close_time=market_data.get("close_time"),
                    game_start_time=market_data.get("game_start_time"),
                    tags=market_data.get("tags", []),
                    volume_1_week=market_data.get("volume_1_week", 0.0),
                    volume_1_month=market_data.get("volume_1_month", 0.0),
                    volume_1_year=market_data.get("volume_1_year", 0.0),
                    volume_total=market_data.get("volume_total", 0.0),
                    resolution_source=market_data.get("resolution_source", ""),
                    image=market_data.get("image", ""),
                    side_a=side_a,
                    side_b=side_b,
                    winning_side=winning_side,
                    status=market_data["status"],
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

        return MarketsResponse(markets=markets, pagination=pagination)

    def get_orderbooks(
        self,
        params: GetOrderbooksParams,
        options: Optional[RequestConfig] = None,
    ) -> OrderbooksResponse:
        """Get Orderbook History.

        Fetches historical orderbook snapshots for a specific asset (token ID)
        over a specified time range.

        Args:
            params: Parameters for the orderbooks request
            options: Optional request configuration

        Returns:
            Orderbook history data with pagination

        Raises:
            ValueError: If the request fails
        """
        token_id = params["token_id"]
        start_time = params["start_time"]
        end_time = params["end_time"]

        query_params = {
            "token_id": token_id,
            "start_time": start_time,
            "end_time": end_time,
        }

        if params.get("limit") is not None:
            query_params["limit"] = params["limit"]
        if params.get("pagination_key"):
            query_params["pagination_key"] = params["pagination_key"]

        response_data = self._make_request(
            "GET",
            "/polymarket/orderbooks",
            query_params,
            options,
        )

        # Parse snapshots
        snapshots = []
        for snapshot_data in response_data["snapshots"]:
            snapshots.append(
                OrderbookSnapshot(
                    asks=snapshot_data["asks"],
                    bids=snapshot_data["bids"],
                    hash=snapshot_data["hash"],
                    minOrderSize=snapshot_data["minOrderSize"],
                    negRisk=snapshot_data["negRisk"],
                    assetId=snapshot_data["assetId"],
                    timestamp=snapshot_data["timestamp"],
                    tickSize=snapshot_data["tickSize"],
                    indexedAt=snapshot_data["indexedAt"],
                    market=snapshot_data["market"],
                )
            )

        # Parse pagination
        pagination_data = response_data["pagination"]
        pagination = OrderbookPagination(
            limit=pagination_data["limit"],
            count=pagination_data["count"],
            pagination_key=pagination_data.get("pagination_key"),
            has_more=pagination_data["has_more"],
        )

        return OrderbooksResponse(snapshots=snapshots, pagination=pagination)

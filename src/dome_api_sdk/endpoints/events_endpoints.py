"""Events-related endpoints for the Dome API."""

from typing import Any, Dict, Optional

from ..base_client import BaseClient
from ..types import (
    Event,
    EventsResponse,
    GetEventsParams,
    Market,
    MarketSide,
    Pagination,
    RequestConfig,
)

__all__ = ["EventsEndpoints"]


class EventsEndpoints(BaseClient):
    """Events-related endpoints for the Dome API.

    Handles events (groups of related markets) data retrieval and filtering.
    """

    def get_events(
        self,
        params: Optional[GetEventsParams] = None,
        options: Optional[RequestConfig] = None,
    ) -> EventsResponse:
        """Get Events.

        Fetches events (groups of related markets) with optional filtering by event_slug,
        tags/categories and status. Events aggregate multiple markets under a single topic.

        Args:
            params: Parameters for the events request (optional)
            options: Optional request configuration

        Returns:
            Events data with pagination

        Raises:
            ValueError: If the request fails
        """
        if params is None:
            params = {}

        query_params: Dict[str, Any] = {}

        # Handle filter parameters
        if params.get("event_slug"):
            query_params["event_slug"] = params["event_slug"]
        if params.get("tags"):
            query_params["tags"] = params["tags"]
        if params.get("status"):
            query_params["status"] = params["status"]
        if params.get("include_markets"):
            query_params["include_markets"] = params["include_markets"]
        if params.get("start_time") is not None:
            query_params["start_time"] = params["start_time"]
        if params.get("end_time") is not None:
            query_params["end_time"] = params["end_time"]
        if params.get("game_start_time") is not None:
            query_params["game_start_time"] = params["game_start_time"]
        if params.get("limit") is not None:
            query_params["limit"] = params["limit"]
        if params.get("offset") is not None:
            query_params["offset"] = params["offset"]

        response_data = self._make_request(
            "GET",
            "/polymarket/events",
            query_params,
            options,
        )

        # Parse events
        events = []
        for event_data in response_data["events"]:
            # Parse markets if included
            markets = None
            if event_data.get("markets") is not None:
                markets = []
                for market_data in event_data["markets"]:
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

            events.append(
                Event(
                    event_slug=event_data["event_slug"],
                    title=event_data["title"],
                    subtitle=event_data.get("subtitle"),
                    status=event_data["status"],
                    start_time=event_data["start_time"],
                    end_time=event_data["end_time"],
                    volume_fiat_amount=event_data["volume_fiat_amount"],
                    settlement_sources=event_data.get("settlement_sources"),
                    rules_url=event_data.get("rules_url"),
                    image=event_data.get("image"),
                    tags=event_data.get("tags", []),
                    market_count=event_data["market_count"],
                    markets=markets,
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

        return EventsResponse(events=events, pagination=pagination)

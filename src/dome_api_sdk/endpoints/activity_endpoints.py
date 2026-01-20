"""Activity-related endpoints for the Dome API."""

from typing import Optional

from ..base_client import BaseClient
from ..types import (
    Activity,
    ActivityPagination,
    ActivityResponse,
    GetActivityParams,
    RequestConfig,
)

__all__ = ["ActivityEndpoints"]


class ActivityEndpoints(BaseClient):
    """Activity-related endpoints for the Dome API.

    Handles trading activity data including MERGES, SPLITS, and REDEEMS.
    """

    def get_activity(
        self,
        params: Optional[GetActivityParams] = None,
        options: Optional[RequestConfig] = None,
    ) -> ActivityResponse:
        """Get Activity.

        Fetches activity data with optional filtering by user, market,
        condition, and time range. Returns trading activity including MERGES,
        SPLITS, and REDEEMS.

        Args:
            params: Parameters for the activity request (optional)
            options: Optional request configuration

        Returns:
            Activity data with pagination

        Raises:
            ValueError: If the request fails
        """
        if params is None:
            params = {}

        user = params.get("user")
        start_time = params.get("start_time")
        end_time = params.get("end_time")
        market_slug = params.get("market_slug")
        condition_id = params.get("condition_id")
        limit = params.get("limit")
        pagination_key = params.get("pagination_key")

        query_params: dict = {}

        if user:
            query_params["user"] = user
        if start_time is not None:
            query_params["start_time"] = start_time
        if end_time is not None:
            query_params["end_time"] = end_time
        if market_slug:
            query_params["market_slug"] = market_slug
        if condition_id:
            query_params["condition_id"] = condition_id
        if limit is not None:
            query_params["limit"] = limit
        if pagination_key:
            query_params["pagination_key"] = pagination_key

        response_data = self._make_request(
            "GET",
            "/polymarket/activity",
            query_params,
            options,
        )

        # Parse activities
        activities = []
        for activity_data in response_data["activities"]:
            activities.append(
                Activity(
                    token_id=activity_data["token_id"],
                    side=activity_data["side"],
                    market_slug=activity_data["market_slug"],
                    condition_id=activity_data["condition_id"],
                    shares=activity_data["shares"],
                    shares_normalized=activity_data["shares_normalized"],
                    price=activity_data["price"],
                    tx_hash=activity_data["tx_hash"],
                    title=activity_data["title"],
                    timestamp=activity_data["timestamp"],
                    order_hash=activity_data["order_hash"],
                    user=activity_data["user"],
                )
            )

        # Parse pagination
        pagination_data = response_data["pagination"]
        pagination = ActivityPagination(
            limit=pagination_data["limit"],
            count=pagination_data["count"],
            has_more=pagination_data["has_more"],
            pagination_key=pagination_data.get("pagination_key"),
        )

        return ActivityResponse(activities=activities, pagination=pagination)

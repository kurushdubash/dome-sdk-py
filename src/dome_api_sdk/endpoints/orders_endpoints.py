"""Orders-related endpoints for the Dome API."""

from typing import Optional

from ..base_client import BaseClient
from ..types import (
    GetOrdersParams,
    OrdersResponse,
    RequestConfig,
)

__all__ = ["OrdersEndpoints"]


class OrdersEndpoints(BaseClient):
    """Orders-related endpoints for the Dome API.

    Handles order data retrieval and filtering.
    """

    def get_orders(
        self,
        params: GetOrdersParams,
        options: Optional[RequestConfig] = None,
    ) -> OrdersResponse:
        """Get Orders.

        Fetches order data with optional filtering by market, condition, token,
        time range, and user. Returns orders that match either primary or secondary
        token IDs for markets.

        Args:
            params: Parameters for the orders request
            options: Optional request configuration

        Returns:
            Orders data with pagination

        Raises:
            ValueError: If the request fails
        """
        query_params = {}

        if params.get("market_slug"):
            query_params["market_slug"] = params["market_slug"]
        if params.get("condition_id"):
            query_params["condition_id"] = params["condition_id"]
        if params.get("token_id"):
            query_params["token_id"] = params["token_id"]
        if params.get("start_time") is not None:
            query_params["start_time"] = str(params["start_time"])
        if params.get("end_time") is not None:
            query_params["end_time"] = str(params["end_time"])
        if params.get("limit") is not None:
            query_params["limit"] = str(params["limit"])
        if params.get("offset") is not None:
            query_params["offset"] = str(params["offset"])
        if params.get("user"):
            query_params["user"] = params["user"]

        response_data = self._make_request(
            "GET",
            "/polymarket/orders",
            query_params,
            options,
        )

        # Parse orders
        from ..types import Order, Pagination

        orders = []
        for order_data in response_data["orders"]:
            orders.append(
                Order(
                    token_id=order_data["token_id"],
                    side=order_data["side"],
                    market_slug=order_data["market_slug"],
                    condition_id=order_data["condition_id"],
                    shares=order_data["shares"],
                    shares_normalized=order_data["shares_normalized"],
                    price=order_data["price"],
                    tx_hash=order_data["tx_hash"],
                    title=order_data["title"],
                    timestamp=order_data["timestamp"],
                    order_hash=order_data["order_hash"],
                    user=order_data["user"],
                )
            )

        # Parse pagination
        pagination_data = response_data["pagination"]
        pagination = Pagination(
            limit=pagination_data["limit"],
            offset=pagination_data["offset"],
            total=pagination_data["total"],
            has_more=pagination_data["has_more"],
        )

        return OrdersResponse(
            orders=orders,
            pagination=pagination,
        )

"""Orders-related endpoints for the Dome API."""

from typing import Any, Optional

from ..base_client import AsyncBaseClient, BaseClient
from ..types import (
    GetOrdersParams,
    OrdersResponse,
    RequestConfig,
)

__all__ = ["AsyncOrdersEndpoints", "OrdersEndpoints"]


class BaseOrdersEndpoints:
    """A base class for Orders endpoints that encapsulates the core logic of the orders endpoints. Doesn't deal with transport, handled by subclasses."""

    def _prepare_get_orders(
        self,
        params: GetOrdersParams,
        options: Optional[RequestConfig] = None,
    ) -> tuple[str, str, dict[str, Any], Optional[RequestConfig]]:
        """Prepare the request for get_orders. This does NOT handle transport, but rather prepares a request in the format needed for the BaseClient's _make_request."""
        query_params: dict[str, Any] = {}

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

        return (
            "GET",
            "/polymarket/orders",
            query_params,
            options,
        )

    def _parse_get_orders(self, raw_response: dict[str, Any]) -> OrdersResponse:
        """Parses the raw json of the get_orders endpoint."""
        from ..types import Order, Pagination

        orders = []
        for order_data in raw_response["orders"]:
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
        pagination_data = raw_response["pagination"]
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


class AsyncOrdersEndpoints(AsyncBaseClient, BaseOrdersEndpoints):
    """Orders-related endpoints for the Dome API (Async version).

    Handles order data retrieval and filtering.
    """

    async def get_orders(
        self, params: GetOrdersParams, options: Optional[RequestConfig] = None
    ) -> OrdersResponse:
        """Get Orders.

        Fetches order data with optional filtering by market, condition, token, time range, and user.
        Returns orders that match either primary or secondary token IDs for markets.

        Args:
            params: Parameters for the orders request
            options: Optional request configuration

        Returns:
            Orders data with pagination

        Raises:
            ValueError: If the request fails
        """
        raw_response = await self._make_request(
            *self._prepare_get_orders(params, options)
        )
        parsed_response = self._parse_get_orders(raw_response)
        return parsed_response


class OrdersEndpoints(BaseClient, BaseOrdersEndpoints):
    """Orders-related endpoints for the Dome API.

    Handles order data retrieval and filtering.
    """

    def get_orders(
        self, params: GetOrdersParams, options: Optional[RequestConfig] = None
    ) -> OrdersResponse:
        """Get Orders.

        Fetches order data with optional filtering by market, condition, token, time range, and user.
        Returns orders that match either primary or secondary token IDs for markets.

        Args:
            params: Parameters for the orders request
            options: Optional request configuration

        Returns:
            Orders data with pagination

        Raises:
            ValueError: If the request fails
        """
        raw_response = self._make_request(*self._prepare_get_orders(params, options))
        parsed_response = self._parse_get_orders(raw_response)
        return parsed_response

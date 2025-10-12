"""Wallet-related endpoints for the Dome API."""

from typing import Any, Optional

from ..base_client import AsyncBaseClient, BaseClient
from ..types import (
    GetWalletPnLParams,
    RequestConfig,
    WalletPnLResponse,
)

__all__ = ["AsyncWalletEndpoints", "WalletEndpoints"]


class BaseWalletEndpoints:
    """A base class for Wallet endpoints that encapsulates the core logic of the wallet endpoints. Doesn't deal with transport, handled by subclasses."""

    def _prepare_get_wallet_pnl(
        self,
        params: GetWalletPnLParams,
        options: Optional[RequestConfig] = None,
    ) -> tuple[str, str, dict[str, Any], Optional[RequestConfig]]:
        """Prepare the request for get_wallet_pnl. This does NOT handle transport, but rather prepares a request in the format needed for the BaseClient's _make_request."""
        wallet_address = params["wallet_address"]
        granularity = params["granularity"]
        start_time = params.get("start_time")
        end_time = params.get("end_time")

        query_params: dict[str, str] = {
            "granularity": granularity,
        }

        if start_time is not None:
            query_params["start_time"] = str(start_time)

        if end_time is not None:
            query_params["end_time"] = str(end_time)

        return (
            "GET",
            f"/polymarket/wallet/pnl/{wallet_address}",
            query_params,
            options,
        )

    def _parse_get_wallet_pnl(self, raw_response: dict[str, Any]) -> WalletPnLResponse:
        """Parses the raw json of the get_wallet_pnl endpoint."""
        # Parse PnL data points
        from ..types import PnLDataPoint

        pnl_over_time = []
        for pnl_point in raw_response["pnl_over_time"]:
            pnl_over_time.append(
                PnLDataPoint(
                    timestamp=pnl_point["timestamp"],
                    pnl_to_date=pnl_point["pnl_to_date"],
                )
            )

        return WalletPnLResponse(
            granularity=raw_response["granularity"],
            start_time=raw_response["start_time"],
            end_time=raw_response["end_time"],
            wallet_address=raw_response["wallet_address"],
            pnl_over_time=pnl_over_time,
        )


class AsyncWalletEndpoints(AsyncBaseClient, BaseWalletEndpoints):
    """Wallet-related endpoints for the Dome API (Async version).

    Handles wallet analytics and PnL data.
    """

    async def get_wallet_pnl(
        self, params: GetWalletPnLParams, options: Optional[RequestConfig] = None
    ) -> WalletPnLResponse:
        """Get Wallet PnL.

        Fetches the profit and loss (PnL) for a specific wallet address over a specified time range and granularity.

        Args:
            params: Parameters for the wallet PnL request
            options: Optional request configuration

        Returns:
            Wallet PnL data

        Raises:
            ValueError: If the request fails
        """
        raw_response = await self._make_request(
            *self._prepare_get_wallet_pnl(params, options)
        )
        parsed_response = self._parse_get_wallet_pnl(raw_response)
        return parsed_response


class WalletEndpoints(BaseClient, BaseWalletEndpoints):
    """Wallet-related endpoints for the Dome API.

    Handles wallet analytics and PnL data.
    """

    def get_wallet_pnl(
        self, params: GetWalletPnLParams, options: Optional[RequestConfig] = None
    ) -> WalletPnLResponse:
        """Get Wallet PnL.

        Fetches the profit and loss (PnL) for a specific wallet address over a specified time range and granularity.

        Args:
            params: Parameters for the wallet PnL request
            options: Optional request configuration

        Returns:
            Wallet PnL data

        Raises:
            ValueError: If the request fails
        """
        raw_response = self._make_request(
            *self._prepare_get_wallet_pnl(params, options)
        )
        parsed_response = self._parse_get_wallet_pnl(raw_response)
        return parsed_response

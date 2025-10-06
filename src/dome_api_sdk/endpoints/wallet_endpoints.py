"""Wallet-related endpoints for the Dome API."""

from typing import Optional

from ..base_client import BaseClient
from ..types import (
    GetWalletPnLParams,
    RequestConfig,
    WalletPnLResponse,
)

__all__ = ["WalletEndpoints"]


class WalletEndpoints(BaseClient):
    """Wallet-related endpoints for the Dome API.

    Handles wallet analytics and PnL data.
    """

    def get_wallet_pnl(
        self,
        params: GetWalletPnLParams,
        options: Optional[RequestConfig] = None,
    ) -> WalletPnLResponse:
        """Get Wallet PnL.

        Fetches the profit and loss (PnL) for a specific wallet address
        over a specified time range and granularity.

        Args:
            params: Parameters for the wallet PnL request
            options: Optional request configuration

        Returns:
            Wallet PnL data

        Raises:
            ValueError: If the request fails
        """
        wallet_address = params["wallet_address"]
        granularity = params["granularity"]
        start_time = params.get("start_time")
        end_time = params.get("end_time")

        query_params = {
            "granularity": granularity,
        }

        if start_time is not None:
            query_params["start_time"] = start_time

        if end_time is not None:
            query_params["end_time"] = end_time

        response_data = self._make_request(
            "GET",
            f"/polymarket/wallet/pnl/{wallet_address}",
            query_params,
            options,
        )

        # Parse PnL data points
        from ..types import PnLDataPoint

        pnl_over_time = []
        for pnl_point in response_data["pnl_over_time"]:
            pnl_over_time.append(
                PnLDataPoint(
                    timestamp=pnl_point["timestamp"],
                    pnl_to_date=pnl_point["pnl_to_date"],
                )
            )

        return WalletPnLResponse(
            granularity=response_data["granularity"],
            start_time=response_data["start_time"],
            end_time=response_data["end_time"],
            wallet_address=response_data["wallet_address"],
            pnl_over_time=pnl_over_time,
        )

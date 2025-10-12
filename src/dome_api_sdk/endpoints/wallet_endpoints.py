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
    def _prepare_get_wallet_pnl(
        self,
        params: GetWalletPnLParams,
        options: Optional[RequestConfig] = None,
    ) -> tuple[str, str, dict[str, Any], Optional[RequestConfig]]:
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
    async def get_wallet_pnl(
        self, params: GetWalletPnLParams, options: Optional[RequestConfig] = None
    ) -> WalletPnLResponse:
        raw_response = await self._make_request(
            *self._prepare_get_wallet_pnl(params, options)
        )
        parsed_response = self._parse_get_wallet_pnl(raw_response)
        return parsed_response


class WalletEndpoints(BaseClient, BaseWalletEndpoints):
    def get_wallet_pnl(
        self, params: GetWalletPnLParams, options: Optional[RequestConfig] = None
    ) -> WalletPnLResponse:
        raw_response = self._make_request(
            *self._prepare_get_wallet_pnl(params, options)
        )
        parsed_response = self._parse_get_wallet_pnl(raw_response)
        return parsed_response

"""Wallet-related endpoints for the Dome API."""

from typing import Any, Dict, Optional

from ..base_client import BaseClient
from ..types import (
    GetPositionsParams,
    GetWalletParams,
    GetWalletPnLParams,
    PositionsResponse,
    RequestConfig,
    WalletPnLResponse,
    WalletResponse,
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

        query_params: Dict[str, Any] = {
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
            wallet_address=response_data.get("wallet_address", wallet_address),
            pnl_over_time=pnl_over_time,
        )

    def get_wallet(
        self,
        params: GetWalletParams,
        options: Optional[RequestConfig] = None,
    ) -> WalletResponse:
        """Get Wallet Information.

        Fetches wallet information by providing either an EOA (Externally Owned Account)
        address, a proxy wallet address, or a user handle. Returns the associated EOA,
        proxy, wallet type, handle, pseudonym, and profile image. Optionally returns
        trading metrics when with_metrics=true.

        Args:
            params: Parameters for the wallet request
            options: Optional request configuration

        Returns:
            Wallet information

        Raises:
            ValueError: If the request fails
        """
        query_params: Dict[str, Any] = {}

        if params.get("eoa"):
            query_params["eoa"] = params["eoa"]
        if params.get("proxy"):
            query_params["proxy"] = params["proxy"]
        if params.get("handle"):
            # Strip @ prefix if present
            handle = params["handle"]
            if handle.startswith("@"):
                handle = handle[1:]
            query_params["handle"] = handle
        if params.get("with_metrics") is not None:
            query_params["with_metrics"] = "true" if params["with_metrics"] else "false"
        if params.get("start_time") is not None:
            query_params["start_time"] = params["start_time"]
        if params.get("end_time") is not None:
            query_params["end_time"] = params["end_time"]

        response_data = self._make_request(
            "GET",
            "/polymarket/wallet",
            query_params,
            options,
        )

        # Parse wallet metrics if present
        from ..types import HighestVolumeDay, WalletMetrics

        wallet_metrics = None
        if "wallet_metrics" in response_data and response_data["wallet_metrics"]:
            metrics_data = response_data["wallet_metrics"]
            highest_volume_day_data = metrics_data.get("highest_volume_day")
            highest_volume_day = None
            if highest_volume_day_data:
                highest_volume_day = HighestVolumeDay(
                    date=highest_volume_day_data["date"],
                    volume=highest_volume_day_data["volume"],
                    trades=highest_volume_day_data["trades"],
                )
            wallet_metrics = WalletMetrics(
                total_volume=metrics_data["total_volume"],
                total_trades=metrics_data["total_trades"],
                total_markets=metrics_data["total_markets"],
                highest_volume_day=highest_volume_day,
                merges=metrics_data["merges"],
                splits=metrics_data["splits"],
                conversions=metrics_data["conversions"],
                redemptions=metrics_data["redemptions"],
            )

        return WalletResponse(
            eoa=response_data["eoa"],
            proxy=response_data["proxy"],
            wallet_type=response_data["wallet_type"],
            handle=response_data.get("handle"),
            pseudonym=response_data.get("pseudonym"),
            image=response_data.get("image"),
            wallet_metrics=wallet_metrics,
        )

    def get_positions(
        self,
        params: GetPositionsParams,
        options: Optional[RequestConfig] = None,
    ) -> PositionsResponse:
        """Get Wallet Positions.

        Fetches all positions for a specific proxy wallet address. Only returns positions
        with at least 10,000 shares. Includes market metadata and pagination support.

        Args:
            params: Parameters for the positions request
            options: Optional request configuration

        Returns:
            Wallet positions data

        Raises:
            ValueError: If the request fails
        """
        wallet_address = params["wallet_address"]

        query_params: Dict[str, Any] = {}
        if params.get("limit") is not None:
            query_params["limit"] = params["limit"]
        if params.get("pagination_key"):
            query_params["pagination_key"] = params["pagination_key"]

        response_data = self._make_request(
            "GET",
            f"/polymarket/positions/wallet/{wallet_address}",
            query_params,
            options,
        )

        # Parse positions
        from ..types import Position, PositionsPagination, WinningOutcome

        positions = []
        for position_data in response_data["positions"]:
            winning_outcome = None
            if position_data.get("winning_outcome"):
                wo_data = position_data["winning_outcome"]
                winning_outcome = WinningOutcome(
                    id=wo_data["id"],
                    label=wo_data["label"],
                )

            positions.append(
                Position(
                    wallet=position_data["wallet"],
                    token_id=position_data["token_id"],
                    condition_id=position_data["condition_id"],
                    title=position_data["title"],
                    shares=position_data["shares"],
                    shares_normalized=position_data["shares_normalized"],
                    redeemable=position_data["redeemable"],
                    market_slug=position_data["market_slug"],
                    event_slug=position_data["event_slug"],
                    image=position_data["image"],
                    label=position_data["label"],
                    winning_outcome=winning_outcome,
                    start_time=position_data["start_time"],
                    end_time=position_data["end_time"],
                    completed_time=position_data.get("completed_time"),
                    close_time=position_data.get("close_time"),
                    game_start_time=position_data.get("game_start_time"),
                    market_status=position_data["market_status"],
                    negativeRisk=position_data["negativeRisk"],
                )
            )

        pagination = PositionsPagination(
            has_more=response_data["pagination"]["has_more"],
            limit=response_data["pagination"]["limit"],
            pagination_key=response_data["pagination"].get("pagination_key"),
        )

        return PositionsResponse(
            wallet_address=response_data["wallet_address"],
            positions=positions,
            pagination=pagination,
        )

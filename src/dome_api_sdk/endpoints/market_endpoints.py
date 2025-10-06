"""Market-related endpoints for the Dome API."""

from typing import Optional

from ..base_client import BaseClient
from ..types import (
    CandlesticksResponse,
    GetCandlesticksParams,
    GetMarketPriceParams,
    MarketPriceResponse,
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
                    parsed_candlestick_data.append(CandlestickData(
                        end_period_ts=data["end_period_ts"],
                        open_interest=data["open_interest"],
                        price=data["price"],
                        volume=data["volume"],
                        yes_ask=data["yes_ask"],
                        yes_bid=data["yes_bid"]
                    ))
                
                # Parse token metadata
                parsed_token_metadata = TokenMetadata(
                    token_id=token_metadata["token_id"]
                )
                
                parsed_tuple = [parsed_candlestick_data, parsed_token_metadata]
                candlesticks.append(parsed_tuple)
        
        return CandlesticksResponse(candlesticks=candlesticks)

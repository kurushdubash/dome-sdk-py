"""Matching Markets-related endpoints for the Dome API."""

from typing import Optional

from ..base_client import BaseClient
from ..types import (
    GetMatchingMarketsBySportParams,
    GetMatchingMarketsParams,
    MatchingMarketsBySportResponse,
    MatchingMarketsResponse,
    RequestConfig,
)

__all__ = ["MatchingMarketsEndpoints"]


class MatchingMarketsEndpoints(BaseClient):
    """Matching Markets-related endpoints for the Dome API.
    
    Handles cross-platform market matching functionality.
    """

    async def get_matching_markets(
        self,
        params: GetMatchingMarketsParams,
        options: Optional[RequestConfig] = None,
    ) -> MatchingMarketsResponse:
        """Get Matching Markets for Sports.
        
        Find equivalent markets across different prediction market platforms
        (Polymarket, Kalshi, etc.) for sports events.
        
        Args:
            params: Parameters for the matching markets request
            options: Optional request configuration
            
        Returns:
            Matching markets data
            
        Raises:
            ValueError: If the request fails
        """
        query_params = {}
        
        if params.get("polymarket_market_slug"):
            query_params["polymarket_market_slug"] = params["polymarket_market_slug"]
        
        if params.get("kalshi_event_ticker"):
            query_params["kalshi_event_ticker"] = params["kalshi_event_ticker"]
        
        response_data = await self._make_request(
            "GET",
            "/matching-markets/sports/",
            query_params,
            options,
        )
        
        # Parse market data
        from ..types import KalshiMarket, PolymarketMarket
        parsed_markets = {}
        
        for key, markets in response_data["markets"].items():
            parsed_markets[key] = []
            for market in markets:
                if market["platform"] == "KALSHI":
                    parsed_markets[key].append(KalshiMarket(
                        platform="KALSHI",
                        event_ticker=market["event_ticker"],
                        market_tickers=market["market_tickers"]
                    ))
                elif market["platform"] == "POLYMARKET":
                    parsed_markets[key].append(PolymarketMarket(
                        platform="POLYMARKET",
                        market_slug=market["market_slug"],
                        token_ids=market["token_ids"]
                    ))
        
        return MatchingMarketsResponse(markets=parsed_markets)

    async def get_matching_markets_by_sport(
        self,
        params: GetMatchingMarketsBySportParams,
        options: Optional[RequestConfig] = None,
    ) -> MatchingMarketsBySportResponse:
        """Get Matching Markets for Sports by Sport and Date.
        
        Find equivalent markets across different prediction market platforms
        for sports events by sport and date.
        
        Args:
            params: Parameters for the matching markets by sport request
            options: Optional request configuration
            
        Returns:
            Matching markets data
            
        Raises:
            ValueError: If the request fails
        """
        sport = params["sport"]
        date = params["date"]
        
        query_params = {"date": date}
        
        response_data = await self._make_request(
            "GET",
            f"/matching-markets/sports/{sport}/",
            query_params,
            options,
        )
        
        # Parse market data
        from ..types import KalshiMarket, PolymarketMarket
        parsed_markets = {}
        
        for key, markets in response_data["markets"].items():
            parsed_markets[key] = []
            for market in markets:
                if market["platform"] == "KALSHI":
                    parsed_markets[key].append(KalshiMarket(
                        platform="KALSHI",
                        event_ticker=market["event_ticker"],
                        market_tickers=market["market_tickers"]
                    ))
                elif market["platform"] == "POLYMARKET":
                    parsed_markets[key].append(PolymarketMarket(
                        platform="POLYMARKET",
                        market_slug=market["market_slug"],
                        token_ids=market["token_ids"]
                    ))
        
        return MatchingMarketsBySportResponse(
            markets=parsed_markets,
            sport=response_data["sport"],
            date=response_data["date"],
        )

    def get_matching_markets_sync(
        self,
        params: GetMatchingMarketsParams,
        options: Optional[RequestConfig] = None,
    ) -> MatchingMarketsResponse:
        """Get Matching Markets for Sports (Synchronous).
        
        Find equivalent markets across different prediction market platforms
        (Polymarket, Kalshi, etc.) for sports events.
        
        Args:
            params: Parameters for the matching markets request
            options: Optional request configuration
            
        Returns:
            Matching markets data
            
        Raises:
            ValueError: If the request fails
        """
        query_params = {}
        
        if params.get("polymarket_market_slug"):
            query_params["polymarket_market_slug"] = params["polymarket_market_slug"]
        
        if params.get("kalshi_event_ticker"):
            query_params["kalshi_event_ticker"] = params["kalshi_event_ticker"]
        
        response_data = self._make_request_sync(
            "GET",
            "/matching-markets/sports/",
            query_params,
            options,
        )
        
        # Parse market data
        from ..types import KalshiMarket, PolymarketMarket
        parsed_markets = {}
        
        for key, markets in response_data["markets"].items():
            parsed_markets[key] = []
            for market in markets:
                if market["platform"] == "KALSHI":
                    parsed_markets[key].append(KalshiMarket(
                        platform="KALSHI",
                        event_ticker=market["event_ticker"],
                        market_tickers=market["market_tickers"]
                    ))
                elif market["platform"] == "POLYMARKET":
                    parsed_markets[key].append(PolymarketMarket(
                        platform="POLYMARKET",
                        market_slug=market["market_slug"],
                        token_ids=market["token_ids"]
                    ))
        
        return MatchingMarketsResponse(markets=parsed_markets)

    def get_matching_markets_by_sport_sync(
        self,
        params: GetMatchingMarketsBySportParams,
        options: Optional[RequestConfig] = None,
    ) -> MatchingMarketsBySportResponse:
        """Get Matching Markets for Sports by Sport and Date (Synchronous).
        
        Find equivalent markets across different prediction market platforms
        for sports events by sport and date.
        
        Args:
            params: Parameters for the matching markets by sport request
            options: Optional request configuration
            
        Returns:
            Matching markets data
            
        Raises:
            ValueError: If the request fails
        """
        sport = params["sport"]
        date = params["date"]
        
        query_params = {"date": date}
        
        response_data = self._make_request_sync(
            "GET",
            f"/matching-markets/sports/{sport}/",
            query_params,
            options,
        )
        
        # Parse market data
        from ..types import KalshiMarket, PolymarketMarket
        parsed_markets = {}
        
        for key, markets in response_data["markets"].items():
            parsed_markets[key] = []
            for market in markets:
                if market["platform"] == "KALSHI":
                    parsed_markets[key].append(KalshiMarket(
                        platform="KALSHI",
                        event_ticker=market["event_ticker"],
                        market_tickers=market["market_tickers"]
                    ))
                elif market["platform"] == "POLYMARKET":
                    parsed_markets[key].append(PolymarketMarket(
                        platform="POLYMARKET",
                        market_slug=market["market_slug"],
                        token_ids=market["token_ids"]
                    ))
        
        return MatchingMarketsBySportResponse(
            markets=parsed_markets,
            sport=response_data["sport"],
            date=response_data["date"],
        )

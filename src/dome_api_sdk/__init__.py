"""Dome SDK - A comprehensive Python SDK for Dome API.

This package provides a type-safe, async-first SDK for interacting with Dome services.

Example:
    ```python
    import asyncio
    from dome_api_sdk import DomeClient

    async def main():
        async with DomeClient({"api_key": "your-api-key"}) as dome:
            # Get market price
            market_price = await dome.polymarket.markets.get_market_price({
                "token_id": "1234567890"
            })
            print(f"Market Price: {market_price.price}")

    asyncio.run(main())
    ```
"""

from .client import DomeClient
from .types import (
    Activity,
    ActivityPagination,
    ActivityResponse,
    ApiError,
    CandlestickAskBid,
    CandlestickData,
    CandlestickPrice,
    CandlesticksResponse,
    DomeSDKConfig,
    GetActivityParams,
    GetCandlesticksParams,
    GetKalshiMarketsParams,
    GetKalshiOrderbooksParams,
    GetMarketPriceParams,
    GetMarketsParams,
    GetMatchingMarketsBySportParams,
    GetMatchingMarketsParams,
    GetOrderbooksParams,
    GetOrdersParams,
    GetWalletPnLParams,
    HTTPMethod,
    KalshiMarket,
    KalshiMarketData,
    KalshiMarketsResponse,
    KalshiOrderbook,
    KalshiOrderbookPagination,
    KalshiOrderbookSnapshot,
    KalshiOrderbooksResponse,
    Market,
    MarketData,
    MarketOutcome,
    MarketPriceResponse,
    MarketsResponse,
    MatchingMarketsBySportResponse,
    MatchingMarketsResponse,
    Order,
    OrderbookPagination,
    OrderbookSnapshot,
    OrderbooksResponse,
    OrdersResponse,
    Pagination,
    PnLDataPoint,
    PolymarketMarket,
    RequestConfig,
    TokenMetadata,
    ValidationError,
    WalletPnLResponse,
)

__version__ = "0.1.1"
__author__ = "Kurush Dubash, Kunal Roy"
__email__ = "kurush@domeapi.com, kunal@domeapi.com"
__license__ = "MIT"

__all__ = [
    # Main client
    "DomeClient",
    # Configuration
    "DomeSDKConfig",
    "RequestConfig",
    # Market Price Types
    "MarketPriceResponse",
    "GetMarketPriceParams",
    # Candlestick Types
    "CandlestickPrice",
    "CandlestickAskBid",
    "CandlestickData",
    "TokenMetadata",
    "CandlesticksResponse",
    "GetCandlesticksParams",
    # Wallet PnL Types
    "PnLDataPoint",
    "WalletPnLResponse",
    "GetWalletPnLParams",
    # Orders Types
    "Order",
    "Pagination",
    "OrdersResponse",
    "GetOrdersParams",
    # Polymarket Orderbooks Types
    "OrderbookSnapshot",
    "OrderbookPagination",
    "OrderbooksResponse",
    "GetOrderbooksParams",
    # Polymarket Markets Types
    "MarketOutcome",
    "Market",
    "MarketsResponse",
    "GetMarketsParams",
    # Polymarket Activity Types
    "Activity",
    "ActivityPagination",
    "ActivityResponse",
    "GetActivityParams",
    # Matching Markets Types
    "KalshiMarket",
    "PolymarketMarket",
    "MarketData",
    "MatchingMarketsResponse",
    "GetMatchingMarketsParams",
    "GetMatchingMarketsBySportParams",
    "MatchingMarketsBySportResponse",
    # Kalshi Markets Types
    "KalshiMarketData",
    "KalshiMarketsResponse",
    "GetKalshiMarketsParams",
    # Kalshi Orderbooks Types
    "KalshiOrderbook",
    "KalshiOrderbookSnapshot",
    "KalshiOrderbookPagination",
    "KalshiOrderbooksResponse",
    "GetKalshiOrderbooksParams",
    # Error Types
    "ApiError",
    "ValidationError",
    # HTTP Client Types
    "HTTPMethod",
    # Package info
    "__version__",
]

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

For Polymarket trading with external wallets (Privy, MetaMask, etc.):
    ```python
    import asyncio
    from dome_api_sdk import PolymarketRouter, create_privy_signer

    async def main():
        router = PolymarketRouter({
            "api_key": "your-dome-api-key",
            "privy": {
                "app_id": "your-privy-app-id",
                "app_secret": "your-privy-app-secret",
                "authorization_key": "your-privy-auth-key",
            },
        })

        # Link user to Polymarket
        credentials = await router.link_user({
            "user_id": "user-123",
            "signer": signer,
        })

        # Place orders
        result = await router.place_order({
            "user_id": "user-123",
            "market_id": "token-id",
            "side": "buy",
            "size": 10,
            "price": 0.65,
            "signer": signer,
        })

    asyncio.run(main())
    ```
"""

from .client import DomeClient

# Router and utilities
from .router import (
    PolymarketRouter,
    PolymarketRouterWithEscrow,
    PolymarketRouterWithEscrowConfig,
    PlaceOrderWithEscrowParams,
    EscrowConfig,
)

# Escrow module
from .escrow import (
    OrderParams,
    FeeAuthorization,
    SignedFeeAuthorization,
    FEE_AUTHORIZATION_TYPES,
    generate_order_id,
    verify_order_id,
    create_eip712_domain,
    create_fee_authorization,
    sign_fee_authorization,
    sign_fee_authorization_with_signer,
    verify_fee_authorization_signature,
    USDC_POLYGON,
    ESCROW_CONTRACT_POLYGON,
    format_usdc,
    parse_usdc,
    format_bps,
    calculate_fee,
    calculate_order_size_usdc,
)
from .types import (
    ActiveSubscription,
    Activity,
    ActivityPagination,
    ActivityResponse,
    AllowanceStatus,
    ApiError,
    CandlestickAskBid,
    CandlestickData,
    CandlestickPrice,
    CandlesticksResponse,
    CryptoPrice,
    CryptoPricesResponse,
    DomeSDKConfig,
    Eip712Payload,
    GetActivityParams,
    GetBinanceCryptoPricesParams,
    GetCandlesticksParams,
    GetChainlinkCryptoPricesParams,
    GetKalshiMarketPriceParams,
    GetKalshiMarketsParams,
    GetKalshiOrderbooksParams,
    GetKalshiTradesParams,
    GetMarketPriceParams,
    GetMarketsParams,
    GetMatchingMarketsBySportParams,
    GetMatchingMarketsParams,
    GetOrderbooksParams,
    GetOrdersParams,
    GetPositionsParams,
    GetWalletParams,
    GetWalletPnLParams,
    HighestVolumeDay,
    HTTPMethod,
    KalshiMarket,
    KalshiMarketData,
    KalshiMarketPriceResponse,
    KalshiMarketsResponse,
    KalshiOrderbook,
    KalshiOrderbookPagination,
    KalshiOrderbookSnapshot,
    KalshiOrderbooksResponse,
    KalshiPriceSide,
    KalshiTrade,
    KalshiTradesResponse,
    LinkPolymarketUserParams,
    Market,
    MarketData,
    MarketPriceResponse,
    MarketSide,
    MarketsResponse,
    MatchingMarketsBySportResponse,
    MatchingMarketsResponse,
    Order,
    OrderbookPagination,
    OrderbookSnapshot,
    OrderbooksResponse,
    OrdersResponse,
    Pagination,
    PlaceOrderParams,
    PnLDataPoint,
    PolymarketCredentials,
    PolymarketMarket,
    PolymarketOrderType,
    PolymarketRouterConfig,
    Position,
    PositionsPagination,
    PositionsResponse,
    PrivyRouterConfig,
    RequestConfig,
    SafeLinkResult,
    ServerPlaceOrderError,
    ServerPlaceOrderResult,
    SignedPolymarketOrder,
    SubscribeFilters,
    SubscribeMessage,
    SubscriptionAcknowledgment,
    TokenMetadata,
    UnsubscribeMessage,
    UpdateMessage,
    ValidationError,
    WalletMetrics,
    WalletPnLResponse,
    WalletResponse,
    WalletType,
    WebSocketOrderEvent,
    WinningOutcome,
)
from .utils import (
    POLYGON_ADDRESSES,
    PrivyClient,
    RouterSigner,
    check_all_allowances,
    check_privy_wallet_allowances,
    create_privy_client,
    create_privy_signer,
    create_privy_signer_from_env,
    get_polygon_provider,
    set_all_allowances,
    set_privy_wallet_allowances,
)

__version__ = "0.1.5"
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
    # Wallet Information Types
    "HighestVolumeDay",
    "WalletMetrics",
    "WalletResponse",
    "GetWalletParams",
    # Wallet Positions Types
    "WinningOutcome",
    "Position",
    "PositionsPagination",
    "PositionsResponse",
    "GetPositionsParams",
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
    "MarketSide",
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
    # Kalshi Market Price Types
    "KalshiPriceSide",
    "KalshiMarketPriceResponse",
    "GetKalshiMarketPriceParams",
    # Kalshi Trades Types
    "KalshiTrade",
    "KalshiTradesResponse",
    "GetKalshiTradesParams",
    # Kalshi Orderbooks Types
    "KalshiOrderbook",
    "KalshiOrderbookSnapshot",
    "KalshiOrderbookPagination",
    "KalshiOrderbooksResponse",
    "GetKalshiOrderbooksParams",
    # Crypto Prices Types
    "CryptoPrice",
    "CryptoPricesResponse",
    "GetBinanceCryptoPricesParams",
    "GetChainlinkCryptoPricesParams",
    # Error Types
    "ApiError",
    "ValidationError",
    # HTTP Client Types
    "HTTPMethod",
    # WebSocket Types
    "SubscribeFilters",
    "SubscribeMessage",
    "UnsubscribeMessage",
    "UpdateMessage",
    "SubscriptionAcknowledgment",
    "WebSocketOrderEvent",
    "ActiveSubscription",
    # Router Types
    "WalletType",
    "PolymarketOrderType",
    "Eip712Payload",
    "PrivyRouterConfig",
    "PolymarketRouterConfig",
    "LinkPolymarketUserParams",
    "PlaceOrderParams",
    "PolymarketCredentials",
    "SafeLinkResult",
    "AllowanceStatus",
    "SignedPolymarketOrder",
    "ServerPlaceOrderResult",
    "ServerPlaceOrderError",
    # Router
    "PolymarketRouter",
    "PolymarketRouterWithEscrow",
    "PolymarketRouterWithEscrowConfig",
    "PlaceOrderWithEscrowParams",
    "EscrowConfig",
    # Escrow
    "OrderParams",
    "FeeAuthorization",
    "SignedFeeAuthorization",
    "FEE_AUTHORIZATION_TYPES",
    "generate_order_id",
    "verify_order_id",
    "create_eip712_domain",
    "create_fee_authorization",
    "sign_fee_authorization",
    "sign_fee_authorization_with_signer",
    "verify_fee_authorization_signature",
    "USDC_POLYGON",
    "ESCROW_CONTRACT_POLYGON",
    "format_usdc",
    "parse_usdc",
    "format_bps",
    "calculate_fee",
    "calculate_order_size_usdc",
    # Utilities
    "PrivyClient",
    "RouterSigner",
    "create_privy_client",
    "create_privy_signer",
    "create_privy_signer_from_env",
    "check_privy_wallet_allowances",
    "set_privy_wallet_allowances",
    "POLYGON_ADDRESSES",
    "check_all_allowances",
    "set_all_allowances",
    "get_polygon_provider",
    # Package info
    "__version__",
]

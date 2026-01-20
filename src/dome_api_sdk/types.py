"""Type definitions for the Dome SDK."""

import sys
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Union

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = [
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
    # Polymarket Events Types
    "Event",
    "EventsResponse",
    "GetEventsParams",
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
    # Crypto Prices Types
    "CryptoPrice",
    "CryptoPricesResponse",
    "GetBinanceCryptoPricesParams",
    "GetChainlinkCryptoPricesParams",
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
]

# Type aliases
HTTPMethod = Literal["GET", "POST", "PUT", "DELETE"]


class DomeSDKConfig(TypedDict, total=False):
    """Configuration options for initializing the Dome SDK.

    Attributes:
        api_key: Authentication token for API requests
        base_url: Base URL for the API (defaults to https://api.domeapi.io/v1)
        timeout: Request timeout in seconds (defaults to 30)
    """

    api_key: Optional[str]
    base_url: Optional[str]
    timeout: Optional[float]


class RequestConfig(TypedDict, total=False):
    """Configuration for individual requests.

    Attributes:
        timeout: Request timeout in seconds
        headers: Additional headers to include
    """

    timeout: Optional[float]
    headers: Optional[Dict[str, str]]


# ===== Market Price Types =====


@dataclass(frozen=True)
class MarketPriceResponse:
    """Response from the market price endpoint.

    Attributes:
        price: Current market price
        at_time: Timestamp of the price data
    """

    price: float
    at_time: int


class GetMarketPriceParams(TypedDict, total=False):
    """Parameters for getting market price.

    Attributes:
        token_id: Token ID for the market (required)
        at_time: Unix timestamp for historical price (optional)
    """

    token_id: str
    at_time: Optional[int]


# ===== Candlestick Types =====


@dataclass(frozen=True)
class CandlestickPrice:
    """Price data for a candlestick.

    Attributes:
        open: Opening price
        high: Highest price
        low: Lowest price
        close: Closing price
        open_dollars: Opening price in dollars
        high_dollars: Highest price in dollars
        low_dollars: Lowest price in dollars
        close_dollars: Closing price in dollars
        mean: Mean price
        mean_dollars: Mean price in dollars
        previous: Previous price
        previous_dollars: Previous price in dollars
    """

    open: float
    high: float
    low: float
    close: float
    open_dollars: str
    high_dollars: str
    low_dollars: str
    close_dollars: str
    mean: float
    mean_dollars: str
    previous: float
    previous_dollars: str


@dataclass(frozen=True)
class CandlestickAskBid:
    """Ask/Bid data for a candlestick.

    Attributes:
        open: Opening price
        close: Closing price
        high: Highest price
        low: Lowest price
        open_dollars: Opening price in dollars
        close_dollars: Closing price in dollars
        high_dollars: Highest price in dollars
        low_dollars: Lowest price in dollars
    """

    open: float
    close: float
    high: float
    low: float
    open_dollars: str
    close_dollars: str
    high_dollars: str
    low_dollars: str


@dataclass(frozen=True)
class CandlestickData:
    """Candlestick data point.

    Attributes:
        end_period_ts: End period timestamp
        open_interest: Open interest
        price: Price data
        volume: Volume
        yes_ask: Yes ask data
        yes_bid: Yes bid data
    """

    end_period_ts: int
    open_interest: int
    price: CandlestickPrice
    volume: int
    yes_ask: CandlestickAskBid
    yes_bid: CandlestickAskBid


@dataclass(frozen=True)
class TokenMetadata:
    """Token metadata.

    Attributes:
        token_id: Token ID
    """

    token_id: str


@dataclass(frozen=True)
class CandlesticksResponse:
    """Response from the candlesticks endpoint.

    Attributes:
        candlesticks: List of candlestick data tuples
    """

    candlesticks: List[List[Union[CandlestickData, TokenMetadata]]]


class GetCandlesticksParams(TypedDict, total=False):
    """Parameters for getting candlestick data.

    Attributes:
        condition_id: Condition ID for the market (required)
        start_time: Start time as Unix timestamp (required)
        end_time: End time as Unix timestamp (required)
        interval: Interval in minutes (1, 60, or 1440) (optional)
    """

    condition_id: str
    start_time: int
    end_time: int
    interval: Optional[Literal[1, 60, 1440]]


# ===== Wallet PnL Types =====


@dataclass(frozen=True)
class PnLDataPoint:
    """PnL data point.

    Attributes:
        timestamp: Timestamp
        pnl_to_date: PnL to date
    """

    timestamp: int
    pnl_to_date: float


@dataclass(frozen=True)
class WalletPnLResponse:
    """Response from the wallet PnL endpoint.

    Attributes:
        granularity: Data granularity
        start_time: Start time
        end_time: End time
        wallet_address: Wallet address
        pnl_over_time: PnL data over time
    """

    granularity: str
    start_time: int
    end_time: int
    wallet_address: str
    pnl_over_time: List[PnLDataPoint]


class GetWalletPnLParams(TypedDict, total=False):
    """Parameters for getting wallet PnL.

    Attributes:
        wallet_address: Wallet address (required)
        granularity: Data granularity (required)
        start_time: Start time as Unix timestamp (optional)
        end_time: End time as Unix timestamp (optional)
    """

    wallet_address: str
    granularity: Literal["day", "week", "month", "year", "all"]
    start_time: Optional[int]
    end_time: Optional[int]


# ===== Wallet Information Types =====


@dataclass(frozen=True)
class HighestVolumeDay:
    """Highest volume day data.

    Attributes:
        date: Date in YYYY-MM-DD format
        volume: Total shares traded on that day (normalized)
        trades: Number of trades executed on that day
    """

    date: str
    volume: float
    trades: int


@dataclass(frozen=True)
class WalletMetrics:
    """Wallet trading metrics.

    Attributes:
        total_volume: Total trading volume in USD
        total_trades: Total number of trades
        total_markets: Total number of unique markets traded
        highest_volume_day: The day with the highest number of shares traded
        merges: Total number of token merges
        splits: Total number of token splits
        conversions: Total number of token conversions
        redemptions: Total number of token redemptions
    """

    total_volume: float
    total_trades: int
    total_markets: int
    highest_volume_day: HighestVolumeDay
    merges: int
    splits: int
    conversions: int
    redemptions: int


@dataclass(frozen=True)
class WalletResponse:
    """Response from the wallet endpoint.

    Attributes:
        eoa: EOA (Externally Owned Account) wallet address
        proxy: Proxy wallet address
        wallet_type: Type of wallet
        handle: User handle/username (nullable)
        pseudonym: User pseudonym/display name (nullable)
        image: Profile image URL (nullable)
        wallet_metrics: Trading metrics (only present when with_metrics=true)
    """

    eoa: str
    proxy: str
    wallet_type: str
    handle: Optional[str]
    pseudonym: Optional[str]
    image: Optional[str]
    wallet_metrics: Optional[WalletMetrics] = None


class GetWalletParams(TypedDict, total=False):
    """Parameters for getting wallet information.

    Attributes:
        eoa: EOA wallet address (optional)
        proxy: Proxy wallet address (optional)
        handle: User handle/username (optional)
        with_metrics: Include trading metrics (optional)
        start_time: Start time for metrics calculation as Unix timestamp (optional)
        end_time: End time for metrics calculation as Unix timestamp (optional)
    """

    eoa: Optional[str]
    proxy: Optional[str]
    handle: Optional[str]
    with_metrics: Optional[bool]
    start_time: Optional[int]
    end_time: Optional[int]


# ===== Wallet Positions Types =====


@dataclass(frozen=True)
class WinningOutcome:
    """Winning outcome information.

    Attributes:
        id: Token ID of the winning outcome
        label: Label of the winning outcome
    """

    id: str
    label: str


@dataclass(frozen=True)
class Position:
    """Position data.

    Attributes:
        wallet: Wallet address
        token_id: Polymarket token ID
        condition_id: Condition ID
        title: Market title
        shares: Raw shares (not normalized)
        shares_normalized: Normalized shares (divided by 1,000,000)
        redeemable: Whether the position can be redeemed
        market_slug: Market slug
        event_slug: Event slug
        image: Market image URL
        label: Outcome label (e.g., "Yes" or "No")
        winning_outcome: Winning outcome info (nullable)
        start_time: Market start time as Unix timestamp
        end_time: Market end time as Unix timestamp
        completed_time: Market completion time as Unix timestamp (nullable)
        close_time: Market close time as Unix timestamp (nullable)
        game_start_time: Game start time in ISO format for sports markets (nullable)
        market_status: Market status (open or closed)
        negativeRisk: Whether the position has negative risk
    """

    wallet: str
    token_id: str
    condition_id: str
    title: str
    shares: int
    shares_normalized: float
    redeemable: bool
    market_slug: str
    event_slug: str
    image: str
    label: str
    winning_outcome: Optional[WinningOutcome]
    start_time: int
    end_time: int
    completed_time: Optional[int]
    close_time: Optional[int]
    game_start_time: Optional[str]
    market_status: Literal["open", "closed"]
    negativeRisk: bool


@dataclass(frozen=True)
class PositionsPagination:
    """Positions pagination data.

    Attributes:
        has_more: Whether there are more positions available
        limit: Limit used
        pagination_key: Pagination key for the next page (nullable)
    """

    has_more: bool
    limit: int
    pagination_key: Optional[str]


@dataclass(frozen=True)
class PositionsResponse:
    """Response from the positions endpoint.

    Attributes:
        wallet_address: Wallet address (normalized lowercase)
        positions: List of positions
        pagination: Pagination information
    """

    wallet_address: str
    positions: List[Position]
    pagination: PositionsPagination


class GetPositionsParams(TypedDict, total=False):
    """Parameters for getting wallet positions.

    Attributes:
        wallet_address: Proxy wallet address (required)
        limit: Maximum positions per page (optional, default: 100, max: 100)
        pagination_key: Pagination key for next page (optional)
    """

    wallet_address: str
    limit: Optional[int]
    pagination_key: Optional[str]


# ===== Orders Types =====


@dataclass(frozen=True)
class Order:
    """Order data.

    Attributes:
        token_id: Token ID
        token_label: Human readable label for this outcome (yes/no etc)
        side: Order side (BUY or SELL)
        market_slug: Market slug
        condition_id: Condition ID
        shares: Number of shares
        shares_normalized: Normalized shares
        price: Price
        tx_hash: Transaction hash
        title: Market title
        timestamp: Timestamp
        order_hash: Order hash
        user: User address (maker)
        taker: Taker address that was part of this trade (optional, may be CTF exchange)
    """

    token_id: str
    token_label: str
    side: Literal["BUY", "SELL"]
    market_slug: str
    condition_id: str
    shares: int  # Raw number of shares purchased (from the blockchain)
    shares_normalized: (
        float  # Number of shares purchased normalized (this is raw divided by 1000000)
    )
    price: float
    tx_hash: str
    title: str
    timestamp: int
    order_hash: str
    user: str
    taker: Optional[str]


@dataclass(frozen=True)
class Pagination:
    """Pagination data.

    Attributes:
        limit: Limit
        offset: Offset (deprecated, use pagination_key) (optional)
        total: Total count
        has_more: Whether there are more results
        pagination_key: Base64-encoded cursor for the next page (optional)
    """

    limit: int
    total: int
    has_more: bool
    offset: Optional[int] = None
    pagination_key: Optional[str] = None


@dataclass(frozen=True)
class OrdersResponse:
    """Response from the orders endpoint.

    Attributes:
        orders: List of orders
        pagination: Pagination information
    """

    orders: List[Order]
    pagination: Pagination


class GetOrdersParams(TypedDict, total=False):
    """Parameters for getting orders.

    Attributes:
        market_slug: Market slug (optional). Can provide multiple values as array.
        condition_id: Condition ID (optional). Can provide multiple values as array.
        token_id: Token ID (optional). Can provide multiple values as array.
        start_time: Start time as Unix timestamp (optional)
        end_time: End time as Unix timestamp (optional)
        limit: Limit (optional)
        offset: Offset (deprecated, use pagination_key) (optional)
        pagination_key: Base64-encoded cursor for pagination (optional)
        user: User address (optional)
    """

    market_slug: Optional[Union[str, List[str]]]
    condition_id: Optional[Union[str, List[str]]]
    token_id: Optional[Union[str, List[str]]]
    start_time: Optional[int]
    end_time: Optional[int]
    limit: Optional[int]
    offset: Optional[int]
    pagination_key: Optional[str]
    user: Optional[str]


# ===== Matching Markets Types =====


@dataclass(frozen=True)
class KalshiMarket:
    """Kalshi market data.

    Attributes:
        platform: Platform name
        event_ticker: Event ticker
        market_tickers: Market tickers
    """

    platform: Literal["KALSHI"]
    event_ticker: str
    market_tickers: List[str]


@dataclass(frozen=True)
class PolymarketMarket:
    """Polymarket market data.

    Attributes:
        platform: Platform name
        market_slug: Market slug
        token_ids: Token IDs
    """

    platform: Literal["POLYMARKET"]
    market_slug: str
    token_ids: List[str]


MarketData = Union[KalshiMarket, PolymarketMarket]


@dataclass(frozen=True)
class MatchingMarketsResponse:
    """Response from the matching markets endpoint.

    Attributes:
        markets: Dictionary of matching markets
    """

    markets: Dict[str, List[MarketData]]


class GetMatchingMarketsParams(TypedDict, total=False):
    """Parameters for getting matching markets.

    Attributes:
        polymarket_market_slug: List of Polymarket market slugs (optional)
        kalshi_event_ticker: List of Kalshi event tickers (optional)
    """

    polymarket_market_slug: Optional[List[str]]
    kalshi_event_ticker: Optional[List[str]]


class GetMatchingMarketsBySportParams(TypedDict, total=False):
    """Parameters for getting matching markets by sport.

    Attributes:
        sport: Sport name (required)
        date: Date in YYYY-MM-DD format (required)
    """

    sport: Literal["nfl", "mlb", "cfb", "nba", "nhl"]
    date: str


@dataclass(frozen=True)
class MatchingMarketsBySportResponse:
    """Response from the matching markets by sport endpoint.

    Attributes:
        markets: Dictionary of matching markets
        sport: Sport name
        date: Date
    """

    markets: Dict[str, List[MarketData]]
    sport: str
    date: str


# ===== Error Types =====


@dataclass(frozen=True)
class ApiError:
    """API error response.

    Attributes:
        error: Error code
        message: Error message
    """

    error: str
    message: str


@dataclass(frozen=True)
class ValidationError(ApiError):
    """Validation error response.

    Attributes:
        error: Error code
        message: Error message
        required: Required field (optional)
    """

    required: Optional[str] = None


# ===== Polymarket Orderbooks Types =====


@dataclass(frozen=True)
class OrderbookSnapshot:
    """Orderbook snapshot data.

    Attributes:
        asks: Sell orders, ordered by price
        bids: Buy orders, ordered by price
        hash: Snapshot hash
        minOrderSize: Minimum order size
        negRisk: Negative risk flag
        assetId: Asset ID
        timestamp: Timestamp of the snapshot in milliseconds
        tickSize: Tick size
        indexedAt: When the snapshot was indexed in milliseconds
        market: Market identifier
    """

    asks: List[Dict[str, str]]
    bids: List[Dict[str, str]]
    hash: str
    minOrderSize: str
    negRisk: bool
    assetId: str
    timestamp: int
    tickSize: str
    indexedAt: int
    market: str


@dataclass(frozen=True)
class OrderbookPagination:
    """Orderbook pagination data.

    Attributes:
        limit: Limit
        count: Number of snapshots returned
        pagination_key: The pagination key to pass in to get the next chunk of data
        has_more: Whether there are more snapshots available
    """

    limit: int
    count: int
    pagination_key: Optional[str]
    has_more: bool


@dataclass(frozen=True)
class OrderbooksResponse:
    """Response from the orderbooks endpoint.

    Attributes:
        snapshots: Array of orderbook snapshots at different points in time
        pagination: Pagination information
    """

    snapshots: List[OrderbookSnapshot]
    pagination: OrderbookPagination


class GetOrderbooksParams(TypedDict, total=False):
    """Parameters for getting orderbooks.

    Attributes:
        token_id: The token id (asset) for the Polymarket market (required)
        start_time: Start time in Unix timestamp (milliseconds) (required)
        end_time: End time in Unix timestamp (milliseconds) (required)
        limit: Maximum number of snapshots to return (optional, default: 100, max: 500)
        pagination_key: Pagination key to get the next chunk of data (optional)
    """

    token_id: str
    start_time: int
    end_time: int
    limit: Optional[int]
    pagination_key: Optional[str]


# ===== Polymarket Markets Types =====


@dataclass(frozen=True)
class MarketSide:
    """Market side/outcome data.

    Attributes:
        id: Token ID for the side
        label: Label for the side
    """

    id: str
    label: str


@dataclass(frozen=True)
class Market:
    """Market data.

    Attributes:
        market_slug: Market slug
        condition_id: Condition ID
        title: Market title
        start_time: Unix timestamp in seconds when the market starts
        end_time: Unix timestamp in seconds when the market ends
        completed_time: Unix timestamp in seconds when the market was completed (nullable)
        close_time: Unix timestamp in seconds when the market was closed (nullable)
        game_start_time: Datetime string in UTC format (YYYY-MM-DD HH:MM:SS.000) for when the game/event starts (nullable, only present for sports markets)
        tags: List of tags
        volume_1_week: Trading volume in USD for the past week
        volume_1_month: Trading volume in USD for the past month
        volume_1_year: Trading volume in USD for the past year
        volume_total: Total trading volume in USD
        resolution_source: URL to the data source used for market resolution
        image: URL to the market image
        side_a: First side/outcome of the market
        side_b: Second side/outcome of the market
        winning_side: The winning side of the market (null if not yet resolved), contains id and label
        status: Market status (open or closed)
    """

    market_slug: str
    condition_id: str
    title: str
    start_time: int
    end_time: int
    completed_time: Optional[int]
    close_time: Optional[int]
    game_start_time: Optional[str]
    tags: List[str]
    volume_1_week: float
    volume_1_month: float
    volume_1_year: float
    volume_total: float
    resolution_source: str
    image: str
    side_a: MarketSide
    side_b: MarketSide
    winning_side: Optional[MarketSide]
    status: Literal["open", "closed"]


@dataclass(frozen=True)
class MarketsResponse:
    """Response from the markets endpoint.

    Attributes:
        markets: List of markets
        pagination: Pagination information
    """

    markets: List[Market]
    pagination: Pagination


class GetMarketsParams(TypedDict, total=False):
    """Parameters for getting markets.

    Attributes:
        market_slug: Filter markets by market slug(s). Can provide multiple values.
        event_slug: Filter markets by event slug(s). Can provide multiple values.
        condition_id: Filter markets by condition ID(s). Can provide multiple values.
        token_id: Filter markets by token ID(s). Can provide multiple values (max 100).
        tags: Filter markets by tag(s). Can provide multiple values.
        search: Search markets by keywords in title and description
        status: Filter markets by status (whether they're open or closed)
        min_volume: Filter markets with total trading volume greater than or equal to this amount (USD)
        start_time: Filter markets from this Unix timestamp in seconds (inclusive)
        end_time: Filter markets until this Unix timestamp in seconds (inclusive)
        limit: Number of markets to return (1-100). Default: 10
        offset: Number of markets to skip for pagination (deprecated, use pagination_key)
        pagination_key: Base64-encoded cursor for pagination
    """

    market_slug: Optional[Union[str, List[str]]]
    event_slug: Optional[Union[str, List[str]]]
    condition_id: Optional[Union[str, List[str]]]
    token_id: Optional[Union[str, List[str]]]
    tags: Optional[Union[str, List[str]]]
    search: Optional[str]
    status: Optional[Literal["open", "closed"]]
    min_volume: Optional[float]
    start_time: Optional[int]
    end_time: Optional[int]
    limit: Optional[int]
    offset: Optional[int]
    pagination_key: Optional[str]


# ===== Polymarket Events Types =====


@dataclass(frozen=True)
class Event:
    """Event data (group of related markets).

    Attributes:
        event_slug: Unique identifier for the event
        title: Event title
        subtitle: Event subtitle or description (nullable)
        status: Event status - 'open' if any market is open, 'closed' if all markets are closed
        start_time: Unix timestamp (seconds) when the event started
        end_time: Unix timestamp (seconds) when the event ends
        volume_fiat_amount: Total trading volume across all markets in the event (USD)
        settlement_sources: Resolution/settlement source for the event (nullable)
        rules_url: URL to the event rules (nullable)
        image: Event image URL (nullable)
        tags: Array of category tags for the event
        market_count: Number of markets in this event
        markets: List of markets in this event (only included when include_markets=true)
    """

    event_slug: str
    title: str
    subtitle: Optional[str]
    status: Literal["open", "closed"]
    start_time: int
    end_time: int
    volume_fiat_amount: float
    settlement_sources: Optional[str]
    rules_url: Optional[str]
    image: Optional[str]
    tags: List[str]
    market_count: int
    markets: Optional[List[Market]] = None


@dataclass(frozen=True)
class EventsResponse:
    """Response from the events endpoint.

    Attributes:
        events: List of events
        pagination: Pagination information
    """

    events: List[Event]
    pagination: Pagination


class GetEventsParams(TypedDict, total=False):
    """Parameters for getting events.

    Attributes:
        event_slug: Filter by specific event slug (optional)
        tags: Filter events by tag(s)/category. Can provide multiple values (optional)
        status: Filter events by status (open or closed) (optional)
        include_markets: Set to 'true' to include list of markets for each event (optional)
        start_time: Filter events starting after this Unix timestamp (seconds) (optional)
        end_time: Filter events starting before this Unix timestamp (seconds) (optional)
        game_start_time: Filter events by game start time (Unix timestamp in seconds) (optional)
        limit: Number of events to return (1-100). Default: 10 (optional)
        offset: Number of events to skip for pagination (optional)
    """

    event_slug: Optional[str]
    tags: Optional[Union[str, List[str]]]
    status: Optional[Literal["open", "closed"]]
    include_markets: Optional[str]
    start_time: Optional[int]
    end_time: Optional[int]
    game_start_time: Optional[int]
    limit: Optional[int]
    offset: Optional[int]


# ===== Polymarket Activity Types =====


@dataclass(frozen=True)
class Activity:
    """Activity data.

    Attributes:
        token_id: Token ID
        side: Activity side (MERGE, SPLIT, or REDEEM)
        market_slug: Market slug
        condition_id: Condition ID
        shares: Raw number of shares (from the blockchain)
        shares_normalized: Number of shares normalized (raw divided by 1000000)
        price: Price
        tx_hash: Transaction hash
        title: Market title
        timestamp: Unix timestamp in seconds when the activity occurred
        order_hash: Order hash
        user: User wallet address
    """

    token_id: str
    side: Literal["MERGE", "SPLIT", "REDEEM"]
    market_slug: str
    condition_id: str
    shares: int
    shares_normalized: float
    price: float
    tx_hash: str
    title: str
    timestamp: int
    order_hash: str
    user: str


@dataclass(frozen=True)
class ActivityPagination:
    """Activity pagination data.

    Attributes:
        limit: Limit
        count: Total number of activities matching the filters
        has_more: Whether there are more activities available
        pagination_key: Base64-encoded cursor for the next page (optional)
    """

    limit: int
    count: int
    has_more: bool
    pagination_key: Optional[str] = None


@dataclass(frozen=True)
class ActivityResponse:
    """Response from the activity endpoint.

    Attributes:
        activities: List of activities
        pagination: Pagination information
    """

    activities: List[Activity]
    pagination: ActivityPagination


class GetActivityParams(TypedDict, total=False):
    """Parameters for getting activity.

    Attributes:
        user: User wallet address to fetch activity for (optional, if not provided returns activity for all users)
        start_time: Filter activity from this Unix timestamp in seconds (inclusive) (optional)
        end_time: Filter activity until this Unix timestamp in seconds (inclusive) (optional)
        market_slug: Filter activity by market slug (optional)
        condition_id: Filter activity by condition ID (optional)
        limit: Number of activities to return (1-1000) (optional, default: 100)
        pagination_key: Base64-encoded cursor for pagination (optional)
    """

    user: Optional[str]
    start_time: Optional[int]
    end_time: Optional[int]
    market_slug: Optional[str]
    condition_id: Optional[str]
    limit: Optional[int]
    pagination_key: Optional[str]


# ===== Kalshi Markets Types =====


@dataclass(frozen=True)
class KalshiMarketData:
    """Kalshi market data.

    Attributes:
        event_ticker: The Kalshi event ticker
        market_ticker: The Kalshi market ticker
        title: Market question/title
        start_time: Unix timestamp in seconds when the market opens
        end_time: Unix timestamp in seconds when the market is scheduled to end
        close_time: Unix timestamp in seconds when the market actually resolves/closes (may be before end_time if market finishes early, null if not yet closed)
        status: Market status
        last_price: Last traded price in cents
        volume: Total trading volume in cents
        volume_24h: 24-hour trading volume in cents
        result: Market result (null if unresolved)
    """

    event_ticker: str
    market_ticker: str
    title: str
    start_time: int
    end_time: int
    close_time: Optional[int]
    status: Literal["open", "closed"]
    last_price: float
    volume: float  # Total trading volume in dollars
    volume_24h: float  # 24-hour trading volume in dollars
    result: Optional[str]


@dataclass(frozen=True)
class KalshiMarketsResponse:
    """Response from the Kalshi markets endpoint.

    Attributes:
        markets: List of Kalshi markets
        pagination: Pagination information
    """

    markets: List[KalshiMarketData]
    pagination: Pagination


class GetKalshiMarketsParams(TypedDict, total=False):
    """Parameters for getting Kalshi markets.

    Attributes:
        market_ticker: Filter markets by market ticker(s). Can provide multiple values.
        event_ticker: Filter markets by event ticker(s). Can provide multiple values.
        search: Search markets by keywords in title and description
        status: Filter markets by status (whether they're open or closed)
        min_volume: Filter markets with total trading volume greater than or equal to this amount (in dollars)
        limit: Number of markets to return (1-100). Default: 10
        pagination_key: Base64-encoded cursor for pagination
    """

    market_ticker: Optional[Union[str, List[str]]]
    event_ticker: Optional[Union[str, List[str]]]
    search: Optional[str]
    status: Optional[Literal["open", "closed"]]
    min_volume: Optional[float]
    limit: Optional[int]
    pagination_key: Optional[str]


# ===== Kalshi Orderbooks Types =====


@dataclass(frozen=True)
class KalshiOrderbook:
    """Kalshi orderbook data.

    Attributes:
        yes: Yes side orders with prices in cents (array of [price_in_cents, contract_count])
        no: No side orders with prices in cents (array of [price_in_cents, contract_count])
        yes_dollars: Yes side orders with prices in dollars (array of [price_as_dollar_string, contract_count])
        no_dollars: No side orders with prices in dollars (array of [price_as_dollar_string, contract_count])
    """

    yes: List[List[float]]
    no: List[List[float]]
    yes_dollars: List[List[Union[str, float]]]
    no_dollars: List[List[Union[str, float]]]


@dataclass(frozen=True)
class KalshiOrderbookSnapshot:
    """Kalshi orderbook snapshot data.

    Attributes:
        orderbook: Orderbook data
        timestamp: Timestamp of the snapshot in milliseconds
        ticker: The Kalshi market ticker
    """

    orderbook: KalshiOrderbook
    timestamp: int
    ticker: str


@dataclass(frozen=True)
class KalshiOrderbookPagination:
    """Kalshi orderbook pagination data.

    Attributes:
        limit: Limit
        count: Number of snapshots returned
        has_more: Whether there are more snapshots available
    """

    limit: int
    count: int
    has_more: bool


@dataclass(frozen=True)
class KalshiOrderbooksResponse:
    """Response from the Kalshi orderbooks endpoint.

    Attributes:
        snapshots: Array of orderbook snapshots at different points in time
        pagination: Pagination information
    """

    snapshots: List[KalshiOrderbookSnapshot]
    pagination: KalshiOrderbookPagination


class GetKalshiOrderbooksParams(TypedDict, total=False):
    """Parameters for getting Kalshi orderbooks.

    Attributes:
        ticker: The Kalshi market ticker (required)
        start_time: Start time in Unix timestamp (milliseconds) (required)
        end_time: End time in Unix timestamp (milliseconds) (required)
        limit: Maximum number of snapshots to return (default: 100, max: 500) (optional)
    """

    ticker: str
    start_time: int
    end_time: int
    limit: Optional[int]


# ===== Kalshi Market Price Types =====


@dataclass(frozen=True)
class KalshiPriceSide:
    """Kalshi price side data.

    Attributes:
        price: Price (0-1)
        at_time: Unix timestamp in seconds
    """

    price: float
    at_time: int


@dataclass(frozen=True)
class KalshiMarketPriceResponse:
    """Response from the Kalshi market price endpoint.

    Attributes:
        yes: Yes side price data
        no: No side price data
    """

    yes: KalshiPriceSide
    no: KalshiPriceSide


class GetKalshiMarketPriceParams(TypedDict, total=False):
    """Parameters for getting Kalshi market price.

    Attributes:
        market_ticker: Kalshi market ticker (required)
        at_time: Unix timestamp in seconds for historical price (optional)
    """

    market_ticker: str
    at_time: Optional[int]


# ===== Kalshi Trades Types =====


@dataclass(frozen=True)
class KalshiTrade:
    """Kalshi trade data.

    Attributes:
        trade_id: Unique trade identifier
        market_ticker: Kalshi market ticker
        count: Number of contracts traded
        yes_price: Yes side price in cents
        no_price: No side price in cents
        yes_price_dollars: Yes side price in dollars
        no_price_dollars: No side price in dollars
        taker_side: Which side the taker took (yes or no)
        created_time: Unix timestamp in seconds
    """

    trade_id: str
    market_ticker: str
    count: int
    yes_price: int
    no_price: int
    yes_price_dollars: float
    no_price_dollars: float
    taker_side: Literal["yes", "no"]
    created_time: int


@dataclass(frozen=True)
class KalshiTradesResponse:
    """Response from the Kalshi trades endpoint.

    Attributes:
        trades: List of trades
        pagination: Pagination information
    """

    trades: List[KalshiTrade]
    pagination: Pagination


class GetKalshiTradesParams(TypedDict, total=False):
    """Parameters for getting Kalshi trades.

    Attributes:
        ticker: Kalshi market ticker (optional)
        start_time: Start time as Unix timestamp in seconds (optional)
        end_time: End time as Unix timestamp in seconds (optional)
        limit: Number of trades to return (optional, default: 100)
        pagination_key: Base64-encoded cursor for pagination (optional)
    """

    ticker: Optional[str]
    start_time: Optional[int]
    end_time: Optional[int]
    limit: Optional[int]
    pagination_key: Optional[str]


# ===== WebSocket Types =====


class SubscribeFilters(TypedDict, total=False):
    """Filters for WebSocket subscription.

    Attributes:
        users: Array of wallet addresses to track
        condition_ids: Array of condition IDs to track
        market_slugs: Array of market slugs to track
    """

    users: Optional[List[str]]
    condition_ids: Optional[List[str]]
    market_slugs: Optional[List[str]]


class SubscribeMessage(TypedDict):
    """WebSocket subscription message.

    Attributes:
        action: Must be "subscribe"
        platform: Must be "polymarket"
        version: Currently 1
        type: Must be "orders"
        filters: Subscription filters
    """

    action: Literal["subscribe"]
    platform: Literal["polymarket"]
    version: int
    type: Literal["orders"]
    filters: SubscribeFilters


class UnsubscribeMessage(TypedDict):
    """WebSocket unsubscribe message.

    Attributes:
        action: Must be "unsubscribe"
        version: Currently 1
        subscription_id: The subscription ID to unsubscribe from
    """

    action: Literal["unsubscribe"]
    version: int
    subscription_id: str


class UpdateMessage(TypedDict):
    """WebSocket update subscription message.

    Attributes:
        action: Must be "update"
        subscription_id: The subscription ID to update
        platform: Must be "polymarket"
        version: Currently 1
        type: Must be "orders"
        filters: New subscription filters
    """

    action: Literal["update"]
    subscription_id: str
    platform: Literal["polymarket"]
    version: int
    type: Literal["orders"]
    filters: SubscribeFilters


@dataclass(frozen=True)
class SubscriptionAcknowledgment:
    """WebSocket subscription acknowledgment.

    Attributes:
        type: Always "ack"
        subscription_id: The subscription ID assigned by the server
    """

    type: Literal["ack"]
    subscription_id: str


@dataclass(frozen=True)
class WebSocketOrderEvent:
    """WebSocket order event.

    Attributes:
        type: Always "event"
        subscription_id: The subscription ID that triggered this event
        data: Order information matching the format of the orders API
    """

    type: Literal["event"]
    subscription_id: str
    data: Order


@dataclass(frozen=True)
class ActiveSubscription:
    """Active subscription information.

    Attributes:
        subscription_id: The subscription ID assigned by the server
        request: The original subscription request
    """

    subscription_id: str
    request: SubscribeMessage


# ===== Crypto Prices Types =====


@dataclass(frozen=True)
class CryptoPrice:
    """Crypto price data point.

    Attributes:
        symbol: The currency pair symbol
        value: The price value (can be string or number)
        timestamp: Unix timestamp in milliseconds when the price was recorded
    """

    symbol: str
    value: Union[str, float]
    timestamp: int


@dataclass(frozen=True)
class CryptoPricesResponse:
    """Response from the crypto prices endpoint.

    Attributes:
        prices: Array of crypto price data points
        pagination_key: Pagination key (base64-encoded) to fetch the next page (optional)
        total: Total number of prices returned in this response
    """

    prices: List[CryptoPrice]
    pagination_key: Optional[str]
    total: int


class GetBinanceCryptoPricesParams(TypedDict, total=False):
    """Parameters for getting Binance crypto prices.

    Attributes:
        currency: The currency pair symbol (required). Must be lowercase alphanumeric with no separators (e.g., btcusdt, ethusdt)
        start_time: Start time in Unix timestamp (milliseconds) (optional)
        end_time: End time in Unix timestamp (milliseconds) (optional)
        limit: Maximum number of prices to return (default: 100, max: 100) (optional)
        pagination_key: Pagination key to fetch the next page (optional)
    """

    currency: str
    start_time: Optional[int]
    end_time: Optional[int]
    limit: Optional[int]
    pagination_key: Optional[str]


class GetChainlinkCryptoPricesParams(TypedDict, total=False):
    """Parameters for getting Chainlink crypto prices.

    Attributes:
        currency: The currency pair symbol (required). Must be slash-separated (e.g., btc/usd, eth/usd)
        start_time: Start time in Unix timestamp (milliseconds) (optional)
        end_time: End time in Unix timestamp (milliseconds) (optional)
        limit: Maximum number of prices to return (default: 100, max: 100) (optional)
        pagination_key: Pagination key to fetch the next page (optional)
    """

    currency: str
    start_time: Optional[int]
    end_time: Optional[int]
    limit: Optional[int]
    pagination_key: Optional[str]


# ===== Router Types (Wallet-Agnostic) =====

# Type aliases for wallet types
WalletType = Literal["eoa", "safe"]
"""Wallet type for Polymarket trading.

- 'eoa': Standard Externally Owned Account (Privy embedded wallets, direct wallet signing)
  - Uses signatureType = 0
  - Signer address is the funder address
  - Funds (USDC) are held directly in the EOA

- 'safe': Safe Smart Account (external wallets like MetaMask, Rabby, etc.)
  - Uses signatureType = 2 (browser wallet with Safe)
  - Signer is the EOA, funder is the derived Safe address
  - Funds (USDC) are held in the Safe wallet
  - Requires Safe deployment before trading
"""

# Order type for Polymarket CLOB
PolymarketOrderType = Literal["GTC", "GTD", "FOK", "FAK"]
"""Order type for Polymarket CLOB.

- 'GTC': Good Till Cancelled - order stays on book until filled or cancelled
- 'GTD': Good Till Date - order expires at specified time
- 'FOK': Fill Or Kill - order must fill completely immediately or cancel entirely
- 'FAK': Fill And Kill - fills as much as possible immediately, cancels rest

For copy trading, use 'FOK' or 'FAK' for instant confirmation of fill status.
"""


class Eip712Payload(TypedDict):
    """EIP-712 payload shape used by Dome router / Polymarket.

    This is the structure that needs to be signed by the user's wallet.

    Attributes:
        domain: Domain information for EIP-712 signing
        types: Types definition for the structured data
        primaryType: Primary type being signed
        message: The actual message data to be signed
    """

    domain: Dict[str, any]
    types: Dict[str, List[Dict[str, str]]]
    primaryType: str
    message: Dict[str, any]


class PrivyRouterConfig(TypedDict):
    """Privy configuration for automatic signer creation.

    Attributes:
        app_id: Privy App ID
        app_secret: Privy App Secret
        authorization_key: Privy Authorization Private Key (wallet-auth:...)
    """

    app_id: str
    app_secret: str
    authorization_key: str


class PolymarketRouterConfig(TypedDict, total=False):
    """Configuration for Polymarket router helper.

    The router automatically uses Dome's builder server
    (https://builder-signer.domeapi.io/builder-signer/sign)
    for improved order execution, routing, and reduced MEV exposure.

    Orders are placed via Dome API (https://api.domeapi.io/v1) which requires an API key.

    Attributes:
        api_key: Dome API key for order placement (required for place_order)
        chain_id: Chain ID (137 for Polygon mainnet, 80002 for Amoy testnet)
        clob_endpoint: Polymarket CLOB endpoint (defaults to https://clob.polymarket.com)
        relayer_endpoint: Polymarket Relayer endpoint (defaults to https://relayer-v2.polymarket.com)
        rpc_url: Polygon RPC URL (defaults to https://polygon-rpc.com)
        privy: Optional Privy configuration for automatic signer creation
    """

    api_key: Optional[str]
    chain_id: Optional[int]
    clob_endpoint: Optional[str]
    relayer_endpoint: Optional[str]
    rpc_url: Optional[str]
    privy: Optional[PrivyRouterConfig]


class LinkPolymarketUserParams(TypedDict, total=False):
    """One-time setup to link a user to Polymarket via Dome router.

    This establishes the connection between your user and their Polymarket account.

    Attributes:
        user_id: Customer's internal user ID in your system (required)
        signer: Wallet/signing implementation (Privy, MetaMask, etc.) - must be a RouterSigner
        wallet_type: Type of wallet being used (default: 'eoa')
        auto_deploy_safe: Whether to auto-deploy Safe if not already deployed (default: True)
        privy_wallet_id: Optional Privy wallet ID (required for auto-setting allowances with Privy)
        auto_set_allowances: Whether to automatically set token allowances if missing (default: True)
        sponsor_gas: Use Privy gas sponsorship for allowance transactions (default: False)
    """

    user_id: str
    signer: any  # RouterSigner - can't type hint Protocol here
    wallet_type: Optional[WalletType]
    auto_deploy_safe: Optional[bool]
    privy_wallet_id: Optional[str]
    auto_set_allowances: Optional[bool]
    sponsor_gas: Optional[bool]


class PlaceOrderParams(TypedDict, total=False):
    """High-level order interface for routing via Dome backend.

    Abstracts away Polymarket CLOB specifics.

    Attributes:
        user_id: Your internal user ID (required)
        market_id: Market identifier (platform-specific) (required)
        side: Order side ('buy' or 'sell') (required)
        size: Order size (normalized) (required)
        price: Order price (0-1 for Polymarket) (required)
        signer: Wallet/signing implementation (required for signing orders)
        wallet_type: Type of wallet being used (default: 'eoa')
        funder_address: Safe smart account address that holds user's funds (required for 'safe' wallet)
        privy_wallet_id: Optional Privy wallet ID (if using Privy, avoids need for signer)
        wallet_address: Optional wallet address (if using Privy, avoids need for signer)
        neg_risk: Whether the market uses neg risk (default: False)
        order_type: Order type (default: 'GTC')
    """

    user_id: str
    market_id: str
    side: Literal["buy", "sell"]
    size: float
    price: float
    signer: Optional[any]  # RouterSigner
    wallet_type: Optional[WalletType]
    funder_address: Optional[str]
    privy_wallet_id: Optional[str]
    wallet_address: Optional[str]
    neg_risk: Optional[bool]
    order_type: Optional[PolymarketOrderType]


@dataclass
class PolymarketCredentials:
    """Polymarket CLOB credentials.

    Attributes:
        api_key: API key for CLOB authentication
        api_secret: API secret for CLOB authentication
        api_passphrase: API passphrase for CLOB authentication
    """

    api_key: str
    api_secret: str
    api_passphrase: str


@dataclass
class SafeLinkResult:
    """Result of linking a user with a Safe wallet.

    Attributes:
        credentials: Polymarket API credentials
        safe_address: Safe wallet address (funder for orders)
        signer_address: EOA wallet address (signer for orders)
        safe_deployed: Whether Safe was deployed during this call
        allowances_set: Number of allowances that were set
    """

    credentials: PolymarketCredentials
    safe_address: str
    signer_address: str
    safe_deployed: bool
    allowances_set: int


@dataclass
class AllowanceStatus:
    """Status of token allowances for Polymarket trading.

    Attributes:
        all_set: Whether all required allowances are set
        usdc_ctf_exchange: USDC allowance for CTF Exchange
        usdc_neg_risk_ctf_exchange: USDC allowance for Neg Risk CTF Exchange
        usdc_neg_risk_adapter: USDC allowance for Neg Risk Adapter
        ctf_ctf_exchange: CTF allowance for CTF Exchange
        ctf_neg_risk_ctf_exchange: CTF allowance for Neg Risk CTF Exchange
        ctf_neg_risk_adapter: CTF allowance for Neg Risk Adapter
    """

    all_set: bool
    usdc_ctf_exchange: bool
    usdc_neg_risk_ctf_exchange: bool
    usdc_neg_risk_adapter: bool
    ctf_ctf_exchange: bool
    ctf_neg_risk_ctf_exchange: bool
    ctf_neg_risk_adapter: bool


@dataclass
class SignedPolymarketOrder:
    """Signed order structure for Polymarket CLOB.

    This is the order that has been signed by the user's wallet.

    Attributes:
        salt: Random salt for the order
        maker: Maker address
        signer: Signer address
        taker: Taker address
        token_id: Token ID for the market
        maker_amount: Amount the maker is offering
        taker_amount: Amount the maker wants
        expiration: Order expiration timestamp
        nonce: Order nonce
        fee_rate_bps: Fee rate in basis points
        side: Order side (BUY or SELL)
        signature_type: Type of signature (0 for EOA, 2 for Safe)
        signature: The signature
    """

    salt: str
    maker: str
    signer: str
    taker: str
    token_id: str
    maker_amount: str
    taker_amount: str
    expiration: str
    nonce: str
    fee_rate_bps: str
    side: Literal["BUY", "SELL"]
    signature_type: int
    signature: str


@dataclass
class ServerPlaceOrderResult:
    """Successful order placement result.

    Attributes:
        success: Whether the order was placed successfully
        order_id: Order ID from Polymarket
        client_order_id: Client-provided order ID
        status: Order status
        order_hash: Hash of the order
        transaction_hashes: Transaction hashes for matched orders
        metadata: Additional metadata about the order
    """

    success: bool
    order_id: str
    client_order_id: str
    status: Literal["LIVE", "MATCHED", "DELAYED"]
    order_hash: Optional[str] = None
    transaction_hashes: Optional[List[str]] = None
    metadata: Optional[Dict[str, any]] = None


@dataclass
class ServerPlaceOrderError:
    """Error from server order placement.

    Attributes:
        code: Error code
        message: Error message
        data: Additional error data
    """

    code: int
    message: str
    data: Optional[Dict[str, any]] = None

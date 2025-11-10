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
    "SubscriptionAcknowledgment",
    "WebSocketOrderEvent",
    "ActiveSubscription",
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


# ===== Orders Types =====


@dataclass(frozen=True)
class Order:
    """Order data.

    Attributes:
        token_id: Token ID
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
        user: User address
    """

    token_id: str
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


@dataclass(frozen=True)
class Pagination:
    """Pagination data.

    Attributes:
        limit: Limit
        offset: Offset
        total: Total count
        has_more: Whether there are more results
    """

    limit: int
    offset: int
    total: int
    has_more: bool


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
        offset: Offset (optional)
        user: User address (optional)
    """

    market_slug: Optional[Union[str, List[str]]]
    condition_id: Optional[Union[str, List[str]]]
    token_id: Optional[Union[str, List[str]]]
    start_time: Optional[int]
    end_time: Optional[int]
    limit: Optional[int]
    offset: Optional[int]
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
        tags: Filter markets by tag(s). Can provide multiple values.
        status: Filter markets by status (whether they're open or closed)
        min_volume: Filter markets with total trading volume greater than or equal to this amount (USD)
        limit: Number of markets to return (1-100). Default: 10
        offset: Number of markets to skip for pagination
    """

    market_slug: Optional[Union[str, List[str]]]
    event_slug: Optional[Union[str, List[str]]]
    condition_id: Optional[Union[str, List[str]]]
    tags: Optional[Union[str, List[str]]]
    status: Optional[Literal["open", "closed"]]
    min_volume: Optional[float]
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
        offset: Offset
        count: Total number of activities matching the filters
        has_more: Whether there are more activities available
    """

    limit: int
    offset: int
    count: int
    has_more: bool


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
        user: User wallet address to fetch activity for (required)
        start_time: Filter activity from this Unix timestamp in seconds (inclusive) (optional)
        end_time: Filter activity until this Unix timestamp in seconds (inclusive) (optional)
        market_slug: Filter activity by market slug (optional)
        condition_id: Filter activity by condition ID (optional)
        limit: Number of activities to return (1-1000) (optional, default: 100)
        offset: Number of activities to skip for pagination (optional)
    """

    user: str
    start_time: Optional[int]
    end_time: Optional[int]
    market_slug: Optional[str]
    condition_id: Optional[str]
    limit: Optional[int]
    offset: Optional[int]


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
        status: Filter markets by status (whether they're open or closed)
        min_volume: Filter markets with total trading volume greater than or equal to this amount (in cents)
        limit: Number of markets to return (1-100). Default: 10
        offset: Number of markets to skip for pagination
    """

    market_ticker: Optional[Union[str, List[str]]]
    event_ticker: Optional[Union[str, List[str]]]
    status: Optional[Literal["open", "closed"]]
    min_volume: Optional[float]
    limit: Optional[int]
    offset: Optional[int]


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


# ===== WebSocket Types =====


class SubscribeFilters(TypedDict):
    """Filters for WebSocket subscription.

    Attributes:
        users: Array of wallet addresses to track
    """

    users: List[str]


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

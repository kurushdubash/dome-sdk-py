"""Type definitions for the Dome SDK."""

import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Union

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
    # Matching Markets Types
    "KalshiMarket",
    "PolymarketMarket",
    "MarketData",
    "MatchingMarketsResponse",
    "GetMatchingMarketsParams",
    "GetMatchingMarketsBySportParams",
    "MatchingMarketsBySportResponse",
    # Error Types
    "ApiError",
    "ValidationError",
    # HTTP Client Types
    "HTTPMethod",
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
    shares: int
    shares_normalized: float
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
        market_slug: Market slug (optional)
        condition_id: Condition ID (optional)
        token_id: Token ID (optional)
        start_time: Start time as Unix timestamp (optional)
        end_time: End time as Unix timestamp (optional)
        limit: Limit (optional)
        offset: Offset (optional)
        user: User address (optional)
    """
    
    market_slug: Optional[str]
    condition_id: Optional[str]
    token_id: Optional[str]
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
    
    sport: Literal["nfl", "mlb"]
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

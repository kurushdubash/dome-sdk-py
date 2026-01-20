# Dome Python SDK

[![PyPI version](https://badge.fury.io/py/dome-api-sdk.svg)](https://badge.fury.io/py/dome-api-sdk)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy.readthedocs.io/)

A comprehensive, type-safe Python SDK for [Dome API](https://www.domeapi.io/). Features include market data, wallet analytics, order tracking, cross-platform market matching, real-time WebSocket subscriptions, and Polymarket trading integration. For detailed API documentation, visit [DomeApi.io](https://www.domeapi.io/).

## Installation

```bash
# Using pip
pip install dome-api-sdk

# Using poetry  
poetry add dome-api-sdk

# Using pipenv
pipenv install dome-api-sdk
```

## Quick Start

```python
from dome_api_sdk import DomeClient

# Initialize the client with your API key
dome = DomeClient({"api_key": "your-dome-api-key-here"})

# Get market price
market_price = dome.polymarket.markets.get_market_price({
    "token_id": "98250445447699368679516529207365255018790721464590833209064266254238063117329"
})
print(f"Market Price: {market_price.price}")
```

## Configuration

The SDK accepts the following configuration options:

```python
from dome_api_sdk import DomeClient

config = {
    "api_key": "your-api-key",           # Authentication token (required)
    "base_url": "https://api.domeapi.io/v1",  # Base URL (optional)
    "timeout": 30.0,                     # Request timeout (optional)
}

client = DomeClient(config)
```

### Environment Variables

You can also configure the SDK using environment variables:

```bash
export DOME_API_KEY="your-api-key"
```

```python
from dome_api_sdk import DomeClient

# Will automatically use DOME_API_KEY from environment
client = DomeClient()
```

## Trading with Polymarket Router

The SDK includes a `PolymarketRouter` for integrating wallet providers (Privy, MetaMask, etc.) with Polymarket trading. This allows users to sign once to create API credentials, then trade without signing every order.

### Polymarket Router Endpoints

| Method | Description | Endpoint Path |
|--------|-------------|---------------|
| `router.link_user()` | Link a user to Polymarket by creating CLOB API credentials | Direct CLOB integration |
| `router.place_order()` | Place an order on Polymarket via Dome server | `/polymarket/placeOrder` |
| `router.check_allowances()` | Check if wallet has required token allowances | RPC call |

### Quick Start: Privy + Polymarket Trading

```python
from dome_api_sdk import (
    DomeClient,
    PolymarketRouter,
    create_privy_client,
    create_privy_signer,
)

# Initialize router with Privy config
router = PolymarketRouter({
    "api_key": "your-dome-api-key",
    "privy": {
        "app_id": "your-privy-app-id",
        "app_secret": "your-privy-app-secret",
        "authorization_key": "your-privy-auth-key",
    },
})

# Create signer for user's wallet
privy = create_privy_client({
    "app_id": "your-privy-app-id",
    "app_secret": "your-privy-app-secret",
    "authorization_key": "your-privy-auth-key",
})
signer = create_privy_signer(privy, privy_wallet_id, wallet_address)

# Step 1: Link user (one-time, creates API credentials)
credentials = await router.link_user({
    "user_id": "user-123",
    "signer": signer,
    "privy_wallet_id": privy_wallet_id,
    "auto_set_allowances": True,
})

# Step 2: Place orders (no signatures required after linking)
result = await router.place_order({
    "user_id": "user-123",
    "market_id": "104173557214744537570424345347209544585775842950109756851652855913015295701992",
    "side": "buy",
    "size": 10,
    "price": 0.65,
    "order_type": "GTC",  # 'GTC' | 'GTD' | 'FOK' | 'FAK'
    "signer": signer,
}, credentials)
```

**Order Types:**
- `GTC` (Good Till Cancel) - Stays on book until filled (default)
- `GTD` (Good Till Date) - Expires at specified time
- `FOK` (Fill Or Kill) - Fill completely immediately or cancel
- `FAK` (Fill And Kill) - Fill as much as possible, cancel rest

See the [examples/](./examples/) directory for complete integration examples.

## API Reference

### Complete API Endpoint List

The Dome SDK provides access to the following API endpoints, organized by platform:

#### Polymarket Endpoints

All Polymarket endpoints are accessed through `dome.polymarket.*`:

| Category | Method | Description | Endpoint Path |
|----------|--------|-------------|---------------|
| **Markets** | `markets.get_market_price()` | Get current or historical market price by token ID | `/polymarket/market-price/{token_id}` |
| **Markets** | `markets.get_candlesticks()` | Get historical candlestick data for a market | `/polymarket/candlesticks/{condition_id}` |
| **Markets** | `markets.get_markets()` | Get market data with filtering (slug, tags, search, status, etc.) | `/polymarket/markets` |
| **Markets** | `markets.get_orderbooks()` | Get historical orderbook snapshots for an asset | `/polymarket/orderbooks` |
| **Events** | `events.get_events()` | Get events (groups of related markets) with filtering | `/polymarket/events` |
| **Orders** | `orders.get_orders()` | Get order data with filtering (market, user, time range, etc.) | `/polymarket/orders` |
| **Trading** | `router.place_order()` | Place an order on Polymarket (requires PolymarketRouter) | `/polymarket/placeOrder` |
| **WebSocket** | `websocket.subscribe()` | Subscribe to real-time order events via WebSocket (supports users, condition_ids, market_slugs filters) | `wss://ws.domeapi.io/{api_key}` |
| **WebSocket** | `websocket.update()` | Update an existing subscription's filters | `wss://ws.domeapi.io/{api_key}` |
| **WebSocket** | `websocket.unsubscribe()` | Unsubscribe from order events | `wss://ws.domeapi.io/{api_key}` |
| **WebSocket** | `websocket.get_active_subscriptions()` | Get all active subscriptions | N/A |
| **Wallet** | `wallet.get_wallet()` | Get wallet information by EOA, proxy, or handle (with optional metrics) | `/polymarket/wallet` |
| **Wallet** | `wallet.get_wallet_pnl()` | Get realized profit and loss (PnL) for a wallet | `/polymarket/wallet/pnl/{wallet_address}` |
| **Wallet** | `wallet.get_positions()` | Get all positions for a wallet address | `/polymarket/positions/wallet/{wallet_address}` |
| **Activity** | `activity.get_activity()` | Get trading activity (MERGE, SPLIT, REDEEM) for a user | `/polymarket/activity` |

#### Kalshi Endpoints

All Kalshi endpoints are accessed through `dome.kalshi.*`:

| Category | Method | Description | Endpoint Path |
|----------|--------|-------------|---------------|
| **Markets** | `markets.get_markets()` | Get Kalshi market data with filtering | `/kalshi/markets` |
| **Markets** | `markets.get_market_price()` | Get current or historical Kalshi market price (yes/no sides) | `/kalshi/market-price/{market_ticker}` |
| **Orderbooks** | `orderbooks.get_orderbooks()` | Get historical Kalshi orderbook snapshots | `/kalshi/orderbooks` |
| **Trades** | `markets.get_trades()` | Get historical Kalshi trade data | `/kalshi/trades` |

#### Matching Markets Endpoints

Cross-platform market matching endpoints are accessed through `dome.matching_markets.*`:

| Method | Description | Endpoint Path |
|--------|-------------|---------------|
| `get_matching_markets()` | Find equivalent markets across platforms by Polymarket slug or Kalshi ticker | `/matching-markets/sports/` |
| `get_matching_markets_by_sport()` | Find equivalent markets by sport and date | `/matching-markets/sports/{sport}/` |

#### Crypto Prices Endpoints

Crypto price data endpoints are accessed through `dome.crypto_prices.*`:

| Method | Description | Endpoint Path |
|--------|-------------|---------------|
| **Binance** | `binance.get_binance_prices()` | Get historical crypto price data from Binance | `/crypto-prices/binance` |
| **Chainlink** | `chainlink.get_chainlink_prices()` | Get historical crypto price data from Chainlink | `/crypto-prices/chainlink` |

---

## API Endpoints

### Market Price

Get current or historical market prices:

```python
from dome_api_sdk import DomeClient

dome = DomeClient({"api_key": "your-api-key"})

# Current price
price = dome.polymarket.markets.get_market_price({
    "token_id": "1234567890"
})
print(f"Current Price: {price.price}")

# Historical price
historical_price = dome.polymarket.markets.get_market_price({
    "token_id": "1234567890",
    "at_time": 1740000000  # Unix timestamp
})
print(f"Historical Price: {historical_price.price}")
```

### Candlestick Data

Get historical candlestick data for market analysis:

```python
from dome_api_sdk import DomeClient

dome = DomeClient({"api_key": "your-api-key"})

candlesticks = dome.polymarket.markets.get_candlesticks({
    "condition_id": "0x4567b275e6b667a6217f5cb4f06a797d3a1eaf1d0281fb5bc8c75e2046ae7e57",
    "start_time": 1640995200,
    "end_time": 1672531200,
    "interval": 60  # 1 = 1m, 60 = 1h, 1440 = 1d
})
print(f"Candlesticks: {len(candlesticks.candlesticks)}")
```

### Markets

Get market data with filtering and search:

```python
from dome_api_sdk import DomeClient

dome = DomeClient({"api_key": "your-api-key"})

# Get markets by status
markets = dome.polymarket.markets.get_markets({
    "status": "open",
    "limit": 20,
    "min_volume": 100000
})
print(f"Markets: {len(markets.markets)}")

# Get markets by slug(s)
markets_filtered = dome.polymarket.markets.get_markets({
    "market_slug": ["bitcoin-up-or-down-july-25-8pm-et"],
    "limit": 10
})

# Get markets by tags
markets_by_tags = dome.polymarket.markets.get_markets({
    "tags": ["crypto", "politics"],
    "status": "open"
})

# Search markets
search_results = dome.polymarket.markets.get_markets({
    "search": "bitcoin",
    "limit": 20
})

# Pagination with pagination_key
first_page = dome.polymarket.markets.get_markets({
    "status": "open",
    "limit": 20
})
if first_page.pagination.has_more:
    next_page = dome.polymarket.markets.get_markets({
        "status": "open",
        "limit": 20,
        "pagination_key": first_page.pagination.pagination_key
    })
    print(f"Next page: {len(next_page.markets)} markets")
```

### Events

Get events (groups of related markets) with filtering:

```python
from dome_api_sdk import DomeClient

dome = DomeClient({"api_key": "your-api-key"})

# Get events by status
events = dome.polymarket.events.get_events({
    "status": "open",
    "limit": 10
})
print(f"Events: {len(events.events)}")

# Get event by slug with markets included
event_detail = dome.polymarket.events.get_events({
    "event_slug": "presidential-election-winner-2024",
    "include_markets": "true"
})
# Returns event with markets array populated
for event in event_detail.events:
    print(f"Event: {event.title}")
    if event.markets:
        print(f"  Markets: {len(event.markets)}")

# Get events by tags
events_by_tags = dome.polymarket.events.get_events({
    "tags": ["sports", "politics"],
    "status": "open"
})

# Get events with time filters
events_filtered = dome.polymarket.events.get_events({
    "start_time": 1640995200,  # Event start time
    "end_time": 1672531200,
    "limit": 20
})

# Pagination with pagination_key
first_page = dome.polymarket.events.get_events({
    "limit": 10
})
if first_page.pagination.has_more:
    next_page = dome.polymarket.events.get_events({
        "limit": 10,
        "pagination_key": first_page.pagination.pagination_key
    })
```

### Orderbooks

Get historical orderbook snapshots:

```python
from dome_api_sdk import DomeClient

dome = DomeClient({"api_key": "your-api-key"})

orderbooks = dome.polymarket.markets.get_orderbooks({
    "token_id": "18823838997443878656879952590502524526556504037944392973476854588563571859850",
    "start_time": 1760470000000,  # milliseconds
    "end_time": 1760480000000,    # milliseconds
    "limit": 100
})
print(f"Orderbook snapshots: {len(orderbooks.snapshots)}")
```

### Orders

Get order data with filtering:

```python
from dome_api_sdk import DomeClient

dome = DomeClient({"api_key": "your-api-key"})

# Get orders by market slug
orders = dome.polymarket.orders.get_orders({
    "market_slug": "bitcoin-up-or-down-july-25-8pm-et",
    "limit": 50,
    "start_time": 1640995200,
    "end_time": 1672531200
})
print(f"Orders: {len(orders.orders)}")

# Get orders by user
user_orders = dome.polymarket.orders.get_orders({
    "user": "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",
    "limit": 100
})

# Get orders with array filters
orders_array = dome.polymarket.orders.get_orders({
    "market_slug": ["slug1", "slug2"],
    "limit": 50
})

# Pagination with pagination_key
first_page = dome.polymarket.orders.get_orders({
    "limit": 50
})
if first_page.pagination.has_more:
    next_page = dome.polymarket.orders.get_orders({
        "limit": 50,
        "pagination_key": first_page.pagination.pagination_key
    })
    print(f"Next page: {len(next_page.orders)} orders")
```

### WebSocket - Real-time Order Events

Subscribe to real-time Polymarket order data via WebSocket. The SDK automatically handles reconnection with exponential backoff and subscription management.

#### Basic Usage - Subscribe by Users

```python
import asyncio
from dome_api_sdk import DomeClient, WebSocketOrderEvent

async def main():
    dome = DomeClient({"api_key": "your-api-key"})
    ws_client = dome.polymarket.websocket

    # Define event handler
    def on_order_event(event: WebSocketOrderEvent):
        print(f"New order: {event.data.side} {event.data.shares_normalized} shares")
        print(f"Market: {event.data.market_slug}")
        print(f"User: {event.data.user}")
        print(f"Price: {event.data.price}")

    # Connect and subscribe
    await ws_client.connect()
    subscription_id = await ws_client.subscribe(
        users=["0x6031b6eed1c97e853c6e0f03ad3ce3529351f96d"],
        on_event=on_order_event
    )
    print(f"Subscribed with ID: {subscription_id}")

    # Keep running to receive events
    await asyncio.sleep(60)

    # Unsubscribe when done
    await ws_client.unsubscribe(subscription_id)
    await ws_client.disconnect()

asyncio.run(main())
```

#### Subscribe by Condition IDs

```python
import asyncio
from dome_api_sdk import DomeClient, WebSocketOrderEvent

async def main():
    dome = DomeClient({"api_key": "your-api-key"})
    ws_client = dome.polymarket.websocket

    def on_order_event(event: WebSocketOrderEvent):
        print(f"Order for condition: {event.data.condition_id}")

    await ws_client.connect()
    subscription_id = await ws_client.subscribe(
        condition_ids=["0x17815081230e3b9c78b098162c33b1ffa68c4ec29c123d3d14989599e0c2e113"],
        on_event=on_order_event
    )

    await asyncio.sleep(60)
    await ws_client.unsubscribe(subscription_id)
    await ws_client.disconnect()

asyncio.run(main())
```

#### Subscribe by Market Slugs

```python
import asyncio
from dome_api_sdk import DomeClient, WebSocketOrderEvent

async def main():
    dome = DomeClient({"api_key": "your-api-key"})
    ws_client = dome.polymarket.websocket

    def on_order_event(event: WebSocketOrderEvent):
        print(f"Order in market: {event.data.market_slug}")

    await ws_client.connect()
    subscription_id = await ws_client.subscribe(
        market_slugs=["btc-updown-15m-1762755300"],
        on_event=on_order_event
    )

    await asyncio.sleep(60)
    await ws_client.unsubscribe(subscription_id)
    await ws_client.disconnect()

asyncio.run(main())
```

#### Update Subscription

Update an existing subscription's filters without creating a new subscription:

```python
import asyncio
from dome_api_sdk import DomeClient, WebSocketOrderEvent

async def main():
    dome = DomeClient({"api_key": "your-api-key"})
    ws_client = dome.polymarket.websocket

    def on_order_event(event: WebSocketOrderEvent):
        print(f"Order: {event.data.user}")

    await ws_client.connect()
    
    # Initial subscription
    subscription_id = await ws_client.subscribe(
        users=["0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b"],
        on_event=on_order_event
    )

    await asyncio.sleep(10)

    # Update to track different users (keeps same subscription_id)
    await ws_client.update(
        subscription_id=subscription_id,
        users=["0x6031b6eed1c97e853c6e0f03ad3ce3529351f96d"]
    )

    await asyncio.sleep(60)
    await ws_client.unsubscribe(subscription_id)
    await ws_client.disconnect()

asyncio.run(main())
```

#### Using Context Manager

```python
import asyncio
from dome_api_sdk import DomeClient, WebSocketOrderEvent

async def main():
    dome = DomeClient({"api_key": "your-api-key"})
    ws_client = dome.polymarket.websocket

    def on_order_event(event: WebSocketOrderEvent):
        print(f"Order event: {event.data}")

    # Context manager handles connection/disconnection
    async with ws_client:
        subscription_id = await ws_client.subscribe(
            users=["0x6031b6eed1c97e853c6e0f03ad3ce3529351f96d"],
            on_event=on_order_event
        )

        # Keep running
        await asyncio.sleep(60)

        # Unsubscribe before exiting context
        await ws_client.unsubscribe(subscription_id)

asyncio.run(main())
```

#### Multiple Subscriptions

```python
import asyncio
from dome_api_sdk import DomeClient, WebSocketOrderEvent

async def main():
    dome = DomeClient({"api_key": "your-api-key"})
    ws_client = dome.polymarket.websocket

    def on_order_event(event: WebSocketOrderEvent):
        print(f"Order from subscription {event.subscription_id}: {event.data.user}")

    await ws_client.connect()

    # Subscribe to multiple users
    sub1 = await ws_client.subscribe(
        users=["0x6031b6eed1c97e853c6e0f03ad3ce3529351f96d"],
        on_event=on_order_event
    )

    sub2 = await ws_client.subscribe(
        users=["0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b"],
        on_event=on_order_event
    )

    # Subscribe by condition IDs
    sub3 = await ws_client.subscribe(
        condition_ids=["0x17815081230e3b9c78b098162c33b1ffa68c4ec29c123d3d14989599e0c2e113"],
        on_event=on_order_event
    )

    # Get all active subscriptions
    active = ws_client.get_active_subscriptions()
    print(f"Active subscriptions: {len(active)}")
    for sub in active:
        filters = sub.request['filters']
        filter_desc = []
        if filters.get('users'):
            filter_desc.append(f"users: {len(filters['users'])}")
        if filters.get('condition_ids'):
            filter_desc.append(f"condition_ids: {len(filters['condition_ids'])}")
        if filters.get('market_slugs'):
            filter_desc.append(f"market_slugs: {len(filters['market_slugs'])}")
        print(f"  - {sub.subscription_id}: {', '.join(filter_desc)}")

    await asyncio.sleep(60)

    # Unsubscribe from all
    for sub in active:
        await ws_client.unsubscribe(sub.subscription_id)

    await ws_client.disconnect()

asyncio.run(main())
```

#### Automatic Reconnection

The SDK automatically handles reconnection with exponential backoff (up to 10 retries) and re-subscribes to all active subscriptions:

```python
import asyncio
from dome_api_sdk import DomeClient, WebSocketOrderEvent

async def main():
    dome = DomeClient({"api_key": "your-api-key"})
    ws_client = dome.polymarket.websocket

    def on_order_event(event: WebSocketOrderEvent):
        print(f"Order: {event.data}")

    await ws_client.connect()
    subscription_id = await ws_client.subscribe(
        users=["0x6031b6eed1c97e853c6e0f03ad3ce3529351f96d"],
        on_event=on_order_event
    )

    # If connection drops, SDK will:
    # 1. Attempt to reconnect with exponential backoff (1s, 2s, 4s, 8s, ...)
    # 2. Automatically re-subscribe to all active subscriptions
    # 3. Continue receiving events seamlessly

    await asyncio.sleep(300)  # Run for 5 minutes

    await ws_client.unsubscribe(subscription_id)
    await ws_client.disconnect()

asyncio.run(main())
```

#### WebSocket Features

- **Multiple Filter Types**: Subscribe by users, condition_ids, or market_slugs
- **Update Subscriptions**: Change filters without unsubscribing
- **Automatic Reconnection**: Exponential backoff up to 10 retries
- **Subscription Management**: Track and manage all active subscriptions
- **Event Handling**: Callback-based event processing
- **Re-subscription**: Automatically re-subscribes on reconnection
- **Type Safety**: Full type hints for all WebSocket messages and events

### Wallet Information

Get wallet information by EOA, proxy wallet address, or handle:

```python
from dome_api_sdk import DomeClient

dome = DomeClient({"api_key": "your-api-key"})

# Get wallet by EOA address
wallet = dome.polymarket.wallet.get_wallet({
    "eoa": "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b"
})
print(f"EOA: {wallet.eoa}")
print(f"Proxy: {wallet.proxy}")
print(f"Handle: {wallet.handle}")

# Get wallet by proxy address
wallet_by_proxy = dome.polymarket.wallet.get_wallet({
    "proxy": "0x1234567890abcdef1234567890abcdef12345678"
})

# Get wallet by handle (with or without @ prefix)
wallet_by_handle = dome.polymarket.wallet.get_wallet({
    "handle": "@username"  # or just "username"
})

# Get wallet with trading metrics
wallet_with_metrics = dome.polymarket.wallet.get_wallet({
    "eoa": "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",
    "with_metrics": True,
    "start_time": 1726857600,  # Optional: filter metrics by time range
    "end_time": 1758316829
})
if wallet_with_metrics.wallet_metrics:
    print(f"Total Volume: ${wallet_with_metrics.wallet_metrics.total_volume:,.2f}")
    print(f"Total Trades: {wallet_with_metrics.wallet_metrics.total_trades}")
    print(f"Markets Traded: {wallet_with_metrics.wallet_metrics.total_markets}")
```

### Wallet Positions

Get all positions for a wallet address:

```python
from dome_api_sdk import DomeClient

dome = DomeClient({"api_key": "your-api-key"})

# Get wallet positions (proxy wallet address required)
positions = dome.polymarket.wallet.get_positions({
    "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",  # Proxy wallet
    "limit": 100
})
print(f"Wallet: {positions.wallet_address}")
print(f"Positions: {len(positions.positions)}")

for position in positions.positions:
    print(f"  {position.title}: {position.shares_normalized} shares @ {position.label}")
    print(f"    Market: {position.market_slug}")
    print(f"    Redeemable: {position.redeemable}")
    if position.winning_outcome:
        print(f"    Winner: {position.winning_outcome.label}")

# Pagination with pagination_key
if positions.pagination.has_more:
    next_page = dome.polymarket.wallet.get_positions({
        "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
        "limit": 100,
        "pagination_key": positions.pagination.pagination_key
    })
    print(f"Next page: {len(next_page.positions)} positions")
```

### Wallet PnL

Get realized profit and loss for a wallet:

```python
from dome_api_sdk import DomeClient

dome = DomeClient({"api_key": "your-api-key"})

wallet_pnl = dome.polymarket.wallet.get_wallet_pnl({
    "wallet_address": "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",
    "granularity": "day",
    "start_time": 1726857600,
    "end_time": 1758316829
})
print(f"PnL data points: {len(wallet_pnl.pnl_over_time)}")
```

### Activity

Get trading activity (MERGE, SPLIT, REDEEM) for a user:

```python
from dome_api_sdk import DomeClient

dome = DomeClient({"api_key": "your-api-key"})

activity = dome.polymarket.activity.get_activity({
    "user": "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",
    "start_time": 1726857600,
    "end_time": 1758316829,
    "limit": 50
})
print(f"Activities: {len(activity.activities)}")

# Get all activity (no user filter)
all_activity = dome.polymarket.activity.get_activity({
    "limit": 100
})

# Pagination with pagination_key
first_page = dome.polymarket.activity.get_activity({
    "limit": 50
})
if first_page.pagination.has_more:
    next_page = dome.polymarket.activity.get_activity({
        "limit": 50,
        "pagination_key": first_page.pagination.pagination_key
    })
    print(f"Next page: {len(next_page.activities)} activities")
```

### Trading - Place Orders on Polymarket

Place orders on Polymarket using the PolymarketRouter. This requires one-time user linking and then allows gasless trading via API credentials.

```python
from dome_api_sdk import (
    PolymarketRouter,
    create_privy_client,
    create_privy_signer,
)

# Initialize router
router = PolymarketRouter({
    "api_key": "your-dome-api-key",
    "privy": {
        "app_id": "your-privy-app-id",
        "app_secret": "your-privy-app-secret",
        "authorization_key": "your-privy-auth-key",
    },
})

# Create Privy signer
privy = create_privy_client({
    "app_id": "your-privy-app-id",
    "app_secret": "your-privy-app-secret",
    "authorization_key": "your-privy-auth-key",
})
signer = create_privy_signer(privy, privy_wallet_id, wallet_address)

# Link user (one-time setup)
credentials = await router.link_user({
    "user_id": "user-123",
    "signer": signer,
    "privy_wallet_id": privy_wallet_id,
    "auto_set_allowances": True,  # Automatically set token approvals
    "sponsor_gas": False,  # Optional: Use Privy gas sponsorship
})

# Place a market order
result = await router.place_order({
    "user_id": "user-123",
    "market_id": "104173557214744537570424345347209544585775842950109756851652855913015295701992",
    "side": "buy",  # "buy" or "sell"
    "size": 10,  # Number of shares
    "price": 0.65,  # Price per share
    "order_type": "GTC",  # 'GTC', 'GTD', 'FOK', 'FAK'
    "signer": signer,
}, credentials)

print(f"Order placed! Order ID: {result.get('orderId')}")
print(f"Status: {result['status']}")

# Check allowances before trading
allowances = await router.check_allowances(wallet_address)
if not allowances.all_set:
    print("Token allowances need to be set")
```

**Router Features:**
- **Wallet Agnostic**: Works with Privy, MetaMask, or any EIP-712 signer
- **One-Time Linking**: User signs once to create Polymarket API credentials
- **Gasless Trading**: Orders placed via API keys, no gas required
- **Automatic Allowances**: Optionally auto-set token approvals during linking
- **Order Types**: Supports GTC, GTD, FOK, and FAK order types

See the [examples/](./examples/) directory for complete integration examples with Privy, including server-side signing.

### Kalshi Markets

Get Kalshi market data:

```python
from dome_api_sdk import DomeClient

dome = DomeClient({"api_key": "your-api-key"})

# Get Kalshi markets
kalshi_markets = dome.kalshi.markets.get_markets({
    "status": "open",
    "limit": 20,
    "min_volume": 10000000  # in dollars
})
print(f"Kalshi markets: {len(kalshi_markets.markets)}")

# Get Kalshi markets by ticker(s)
kalshi_filtered = dome.kalshi.markets.get_markets({
    "market_ticker": ["KXNFLGAME-25AUG16ARIDEN-ARI"],
    "limit": 10
})

# Pagination with pagination_key
first_page = dome.kalshi.markets.get_markets({
    "status": "open",
    "limit": 20
})
if first_page.pagination.has_more:
    next_page = dome.kalshi.markets.get_markets({
        "status": "open",
        "limit": 20,
        "pagination_key": first_page.pagination.pagination_key
    })
    print(f"Next page: {len(next_page.markets)} markets")
```

### Kalshi Market Price

Get current or historical Kalshi market prices (yes/no sides):

```python
from dome_api_sdk import DomeClient

dome = DomeClient({"api_key": "your-api-key"})

# Get current price
price = dome.kalshi.markets.get_market_price({
    "market_ticker": "KXNFLGAME-25AUG16ARIDEN-ARI"
})
print(f"Yes Price: {price.yes.price} (at {price.yes.at_time})")
print(f"No Price: {price.no.price} (at {price.no.at_time})")

# Get historical price
historical_price = dome.kalshi.markets.get_market_price({
    "market_ticker": "KXNFLGAME-25AUG16ARIDEN-ARI",
    "at_time": 1740000000  # Unix timestamp in seconds
})
print(f"Historical Yes: {historical_price.yes.price}")
print(f"Historical No: {historical_price.no.price}")
```

### Kalshi Trades

Get historical Kalshi trade data:

```python
from dome_api_sdk import DomeClient

dome = DomeClient({"api_key": "your-api-key"})

# Get all trades
all_trades = dome.kalshi.markets.get_trades({
    "limit": 100
})
print(f"Total trades: {len(all_trades.trades)}")

# Get trades for specific market
market_trades = dome.kalshi.markets.get_trades({
    "ticker": "KXNFLGAME-25AUG16ARIDEN-ARI",
    "limit": 50
})
for trade in market_trades.trades[:5]:  # Show first 5
    print(f"Trade {trade.trade_id}: {trade.count} contracts @ Yes: ${trade.yes_price_dollars:.2f}")
    print(f"  Taker side: {trade.taker_side}")
    print(f"  Time: {trade.created_time}")

# Get trades with time filter
filtered_trades = dome.kalshi.markets.get_trades({
    "ticker": "KXNFLGAME-25AUG16ARIDEN-ARI",
    "start_time": 1726857600,  # Unix timestamp in seconds
    "end_time": 1758316829,
    "limit": 100
})

# Pagination with pagination_key
first_page = dome.kalshi.markets.get_trades({
    "limit": 50
})
if first_page.pagination.has_more:
    next_page = dome.kalshi.markets.get_trades({
        "limit": 50,
        "pagination_key": first_page.pagination.pagination_key
    })
    print(f"Next page: {len(next_page.trades)} trades")
```

### Kalshi Orderbooks

Get historical Kalshi orderbook snapshots:

```python
from dome_api_sdk import DomeClient

dome = DomeClient({"api_key": "your-api-key"})

kalshi_orderbooks = dome.kalshi.orderbooks.get_orderbooks({
    "ticker": "KXNFLGAME-25AUG16ARIDEN-ARI",
    "start_time": 1760470000000,  # milliseconds
    "end_time": 1760480000000,    # milliseconds
    "limit": 100
})
print(f"Kalshi orderbook snapshots: {len(kalshi_orderbooks.snapshots)}")
```

### Matching Markets

Find equivalent markets across different platforms:

```python
from dome_api_sdk import DomeClient

dome = DomeClient({"api_key": "your-api-key"})

# By Polymarket market slugs
matching_markets = dome.matching_markets.get_matching_markets({
    "polymarket_market_slug": ["nfl-ari-den-2025-08-16"]
})
print(f"Matching Markets: {len(matching_markets.markets)}")

# By Kalshi event tickers
matching_markets_kalshi = dome.matching_markets.get_matching_markets({
    "kalshi_event_ticker": ["KXNFLGAME-25AUG16ARIDEN"]
})
print(f"Kalshi Markets: {len(matching_markets_kalshi.markets)}")

# By sport and date
matching_markets_by_sport = dome.matching_markets.get_matching_markets_by_sport({
    "sport": "nfl",
    "date": "2025-08-16"
})
print(f"Sport Markets: {len(matching_markets_by_sport.markets)}")
```

### Crypto Prices

Get historical crypto price data from Binance or Chainlink:

#### Binance Prices

```python
from dome_api_sdk import DomeClient

dome = DomeClient({"api_key": "your-api-key"})

# Get latest price (no time range)
binance_prices = dome.crypto_prices.binance.get_binance_prices({
    "currency": "btcusdt"  # Lowercase, no separators
})
print(f"Latest BTC/USDT price: {binance_prices.prices[0].value}")
print(f"Timestamp: {binance_prices.prices[0].timestamp}")

# Get historical prices with time range
binance_historical = dome.crypto_prices.binance.get_binance_prices({
    "currency": "btcusdt",
    "start_time": 1766130000000,  # milliseconds
    "end_time": 1766131000000,    # milliseconds
    "limit": 100
})
print(f"Historical prices: {binance_historical.total} data points")
for price in binance_historical.prices[:5]:  # Show first 5
    print(f"  {price.symbol}: {price.value} at {price.timestamp}")
```

#### Chainlink Prices

```python
from dome_api_sdk import DomeClient

dome = DomeClient({"api_key": "your-api-key"})

# Get latest price (no time range)
chainlink_prices = dome.crypto_prices.chainlink.get_chainlink_prices({
    "currency": "eth/usd"  # Slash-separated
})
print(f"Latest ETH/USD price: {chainlink_prices.prices[0].value}")
print(f"Timestamp: {chainlink_prices.prices[0].timestamp}")

# Get historical prices with time range
chainlink_historical = dome.crypto_prices.chainlink.get_chainlink_prices({
    "currency": "eth/usd",
    "start_time": 1766130000000,  # milliseconds
    "end_time": 1766131000000,    # milliseconds
    "limit": 100
})
print(f"Historical prices: {chainlink_historical.total} data points")
```

## Error Handling

The SDK provides comprehensive error handling:

```python
from dome_api_sdk import DomeClient

dome = DomeClient({"api_key": "your-api-key"})

try:
    result = dome.polymarket.markets.get_market_price({
        "token_id": "invalid-token"
    })
except ValueError as error:
    if "API Error" in str(error):
        print(f"API Error: {error}")
    else:
        print(f"Network Error: {error}")
```

## Integration Testing

The SDK includes a comprehensive integration test that makes live calls to the real API endpoints to verify everything works correctly.

```bash
# Using Makefile (recommended)
make integration-test API_KEY=your-api-key

# Or using Python directly
python tests/integration_test.py your-api-key

# Or set environment variable
export DOME_API_KEY=your-api-key
make integration-test
```

This smoke test covers all endpoints with various parameter combinations and provides detailed results.

## Development

### Setting up the Development Environment

1. Clone the repository:
```bash
git clone https://github.com/dome/dome-sdk-py.git
cd dome-sdk-py
```

2. Install development dependencies:
```bash
make dev-setup
```

3. Run tests:
```bash
make test
```

4. Run type checking:
```bash
make type-check
```

5. Run linting:
```bash
make lint
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- **Kurush Dubash** - [kurush@domeapi.com](mailto:kurush@domeapi.com)
- **Kunal Roy** - [kunal@domeapi.com](mailto:kunal@domeapi.com)

# Dome Python SDK

[![PyPI version](https://badge.fury.io/py/dome-api-sdk.svg)](https://badge.fury.io/py/dome-api-sdk)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy.readthedocs.io/)

A comprehensive, type-safe, async-first Python SDK for [Dome API](https://www.domeapi.io/). Features include market data, wallet analytics, order tracking, and cross-platform market matching for prediction markets. For detailed API documentation, visit [DomeApi.io](https://www.domeapi.io/).

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

### Async Usage (Recommended)

```python
import asyncio
from dome_api_sdk import DomeClient

async def main():
    # Initialize the client with your API key
    async with DomeClient({"api_key": "your-dome-api-key-here"}) as dome:
        # Get market price
        market_price = await dome.polymarket.markets.get_market_price({
            "token_id": "1234567890"
        })
        print(f"Market Price: {market_price.price}")

asyncio.run(main())
```

### Sync Usage (Alternative)

If you prefer not to use asyncio, you can use the synchronous wrapper methods. All async methods have corresponding `_sync` versions:

```python
from dome_api_sdk import DomeClient

# Initialize the client with your API key
dome = DomeClient({"api_key": "your-dome-api-key-here"})

# Get market price (synchronous)
market_price = dome.polymarket.markets.get_market_price_sync({
    "token_id": "1234567890"
})
print(f"Market Price: {market_price.price}")

# Don't forget to close the client when done
dome.close()
```

**Note**: All endpoint methods have both async and sync versions:
- `get_market_price()` → `get_market_price_sync()`
- `get_candlesticks()` → `get_candlesticks_sync()`
- `get_wallet_pnl()` → `get_wallet_pnl_sync()`
- `get_orders()` → `get_orders_sync()`
- `get_matching_markets()` → `get_matching_markets_sync()`
- `get_matching_markets_by_sport()` → `get_matching_markets_by_sport_sync()`

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

## API Endpoints

### Market Price

Get current or historical market prices:

#### Async Usage
```python
import asyncio
from dome_api_sdk import DomeClient

async def example():
    async with DomeClient({"api_key": "your-api-key"}) as dome:
        # Current price
        price = await dome.polymarket.markets.get_market_price({
            "token_id": "1234567890"
        })
        print(f"Current Price: {price.price}")
        
        # Historical price
        historical_price = await dome.polymarket.markets.get_market_price({
            "token_id": "1234567890",
            "at_time": 1740000000  # Unix timestamp
        })
        print(f"Historical Price: {historical_price.price}")

asyncio.run(example())
```

#### Sync Usage
```python
from dome_api_sdk import DomeClient

dome = DomeClient({"api_key": "your-api-key"})

# Current price
price = dome.polymarket.markets.get_market_price_sync({
    "token_id": "1234567890"
})
print(f"Current Price: {price.price}")

# Historical price
historical_price = dome.polymarket.markets.get_market_price_sync({
    "token_id": "1234567890",
    "at_time": 1740000000  # Unix timestamp
})
print(f"Historical Price: {historical_price.price}")

dome.close()
```

### Candlestick Data

Get historical candlestick data for market analysis:

#### Async Usage
```python
import asyncio
from dome_api_sdk import DomeClient

async def example():
    async with DomeClient({"api_key": "your-api-key"}) as dome:
        candlesticks = await dome.polymarket.markets.get_candlesticks({
            "condition_id": "0x4567b275e6b667a6217f5cb4f06a797d3a1eaf1d0281fb5bc8c75e2046ae7e57",
            "start_time": 1640995200,
            "end_time": 1672531200,
            "interval": 60  # 1 = 1m, 60 = 1h, 1440 = 1d
        })
        print(f"Candlesticks: {len(candlesticks.candlesticks)}")

asyncio.run(example())
```

#### Sync Usage
```python
from dome_api_sdk import DomeClient

dome = DomeClient({"api_key": "your-api-key"})

candlesticks = dome.polymarket.markets.get_candlesticks_sync({
    "condition_id": "0x4567b275e6b667a6217f5cb4f06a797d3a1eaf1d0281fb5bc8c75e2046ae7e57",
    "start_time": 1640995200,
    "end_time": 1672531200,
    "interval": 60  # 1 = 1m, 60 = 1h, 1440 = 1d
})
print(f"Candlesticks: {len(candlesticks.candlesticks)}")

dome.close()
```

### Wallet PnL

Get profit and loss data for a wallet:

```python
import asyncio
from dome_api_sdk import DomeClient

async def example():
    async with DomeClient({"api_key": "your-api-key"}) as dome:
        wallet_pnl = await dome.polymarket.wallet.get_wallet_pnl({
            "wallet_address": "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",
            "granularity": "day",  # 'day', 'week', 'month', 'year', 'all'
            "start_time": 1726857600,
            "end_time": 1758316829
        })
        print(f"Wallet PnL: {len(wallet_pnl.pnl_over_time)} data points")

asyncio.run(example())
```

### Orders

Get order data with filtering:

```python
import asyncio
from dome_api_sdk import DomeClient

async def example():
    async with DomeClient({"api_key": "your-api-key"}) as dome:
        orders = await dome.polymarket.orders.get_orders({
            "market_slug": "bitcoin-up-or-down-july-25-8pm-et",
            "limit": 50,
            "offset": 0,
            "start_time": 1640995200,
            "end_time": 1672531200
        })
        print(f"Orders: {len(orders.orders)}")

asyncio.run(example())
```

### Matching Markets

Find equivalent markets across different platforms:

```python
import asyncio
from dome_api_sdk import DomeClient

async def example():
    async with DomeClient({"api_key": "your-api-key"}) as dome:
        # By Polymarket market slugs
        matching_markets = await dome.matching_markets.get_matching_markets({
            "polymarket_market_slug": ["nfl-ari-den-2025-08-16"]
        })
        print(f"Matching Markets: {len(matching_markets.markets)}")
        
        # By Kalshi event tickers
        matching_markets_kalshi = await dome.matching_markets.get_matching_markets({
            "kalshi_event_ticker": ["KXNFLGAME-25AUG16ARIDEN"]
        })
        print(f"Kalshi Markets: {len(matching_markets_kalshi.markets)}")
        
        # By sport and date
        matching_markets_by_sport = await dome.matching_markets.get_matching_markets_by_sport({
            "sport": "nfl",
            "date": "2025-08-16"
        })
        print(f"Sport Markets: {len(matching_markets_by_sport.markets)}")

asyncio.run(example())
```

## Error Handling

The SDK provides comprehensive error handling:

```python
import asyncio
from dome_api_sdk import DomeClient

async def example():
    async with DomeClient({"api_key": "your-api-key"}) as dome:
        try:
            result = await dome.polymarket.markets.get_market_price({
                "token_id": "invalid-token"
            })
        except ValueError as error:
            if "API Error" in str(error):
                print(f"API Error: {error}")
            else:
                print(f"Network Error: {error}")

asyncio.run(example())
```

## Integration Testing

The SDK includes a comprehensive integration test that makes live calls to the real API endpoints to verify everything works correctly.

```bash
# Run integration tests with your API key
python -m dome_api_sdk.tests.integration_test YOUR_API_KEY
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

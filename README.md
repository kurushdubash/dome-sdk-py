# Dome Python SDK

[![PyPI version](https://badge.fury.io/py/dome-api-sdk.svg)](https://badge.fury.io/py/dome-api-sdk)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy.readthedocs.io/)

A comprehensive, type-safe, async-first Python SDK for [Dome API](https://www.domeapi.io/).

## Features

- 🔒 **Type Safe**: Full type annotations with mypy support
- ⚡ **Async First**: Built with modern async/await syntax
- 🏗️ **Production Ready**: Comprehensive error handling and testing
- 📦 **Easy to Use**: Simple, intuitive API design
- 🔧 **Developer Friendly**: Excellent IDE support with autocomplete
- 🧪 **Well Tested**: High test coverage with pytest

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

### Basic Usage

```python
import asyncio
from dome_api_sdk import DomeClient

async def main():
    # Initialize the client
    async with DomeClient({"api_key": "your-api-key"}) as dome:
        # Perform a health check
        health = await dome.health_check()
        print(f"API Status: {health.status}")

# Run the async function
asyncio.run(main())
```

### Configuration

The SDK accepts the following configuration options:

```python
from dome_api_sdk import DomeClient

config = {
    "api_key": "your-api-key",           # Authentication token
    "base_url": "https://api.dome.com",  # Custom API base URL (optional)
    "timeout": 30.0,                     # Request timeout in seconds (optional)
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

### Context Manager Usage

The recommended way to use the client is as an async context manager:

```python
import asyncio
from dome_api_sdk import DomeClient

async def example():
    async with DomeClient({"api_key": "your-api-key"}) as dome:
        # Use the client
        health = await dome.health_check()
        return health

result = asyncio.run(example())
```

This ensures proper cleanup of HTTP connections.

## API Reference

### DomeClient

The main client class for interacting with the Dome API.

#### Methods

##### `health_check() -> HealthCheckResponse`

Performs a health check on the Dome API.

```python
health = await dome.health_check()
print(f"Status: {health.status}")
print(f"Timestamp: {health.timestamp}")
```

**Returns:**
- `HealthCheckResponse`: Object containing the API health status and timestamp

**Raises:**
- `httpx.HTTPStatusError`: If the API request fails

## Type Definitions

### DomeSDKConfig

Configuration options for the SDK:

```python
from typing import TypedDict, Optional

class DomeSDKConfig(TypedDict, total=False):
    api_key: Optional[str]      # Authentication token
    base_url: Optional[str]     # Custom API base URL
    timeout: Optional[float]    # Request timeout in seconds
```

### HealthCheckResponse

Response from the health check endpoint:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class HealthCheckResponse:
    status: str      # Health status (e.g., "healthy")
    timestamp: str   # ISO timestamp of the check
```

## Error Handling

The SDK uses `httpx` for HTTP requests and will raise `httpx.HTTPStatusError` for HTTP errors:

```python
import httpx
from dome_api_sdk import DomeClient

async def handle_errors():
    async with DomeClient({"api_key": "invalid-key"}) as dome:
        try:
            await dome.health_check()
        except httpx.HTTPStatusError as e:
            print(f"HTTP Error: {e.response.status_code}")
            print(f"Error message: {e.response.text}")
        except httpx.RequestError as e:
            print(f"Request Error: {e}")
```

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

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run tests in watch mode
pytest --watch
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Run type checking
make type-check

# Run all quality checks
make quality
```

### Building and Publishing

```bash
# Build the package
make build

# Publish to PyPI (requires credentials)
make publish
```

## Examples

### Error Handling Example

```python
import asyncio
import httpx
from dome_api_sdk import DomeClient

async def robust_health_check():
    try:
        async with DomeClient({"api_key": "your-api-key"}) as dome:
            health = await dome.health_check()
            return health.status == "healthy"
    except httpx.HTTPStatusError as e:
        print(f"API returned error: {e.response.status_code}")
        return False
    except httpx.RequestError as e:
        print(f"Network error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

is_healthy = asyncio.run(robust_health_check())
print(f"API is healthy: {is_healthy}")
```

### Configuration Example

```python
import asyncio
from dome_api_sdk import DomeClient

async def main():
    # Production configuration
    prod_config = {
        "api_key": "prod-api-key",
        "base_url": "https://api.dome.com",
        "timeout": 60.0
    }
    
    # Development configuration  
    dev_config = {
        "api_key": "dev-api-key",
        "base_url": "https://dev-api.dome.com",
        "timeout": 10.0
    }
    
    # Use appropriate config
    config = prod_config  # or dev_config
    
    async with DomeClient(config) as dome:
        health = await dome.health_check()
        print(f"Environment health: {health.status}")

asyncio.run(main())
```

## Requirements

- Python 3.8+
- httpx >= 0.24.0
- typing-extensions >= 4.5.0 (for Python < 3.10)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- **Kurush Dubash** - [kurush@dome.com](mailto:kurush@dome.com)
- **Kunal Roy** - [kunal@dome.com](mailto:kunal@dome.com)

## Links

- [Documentation](https://docs.domeapi.io/)
- [Dome API Website](https://www.domeapi.io/)
- [PyPI Package](https://pypi.org/project/dome-api-sdk/)
- [GitHub Repository](https://github.com/dome/dome-sdk-py)
- [Report Issues](https://github.com/dome/dome-sdk-py/issues)

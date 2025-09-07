# Dome Python SDK

[![PyPI version](https://badge.fury.io/py/dome-api-sdk.svg)](https://badge.fury.io/py/dome-api-sdk)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy.readthedocs.io/)

A comprehensive, type-safe, async-first Python SDK for [Dome API](https://www.domeapi.io/).


## Installation

```bash
# Using pip
pip install dome-api-sdk

# Using poetry  
poetry add dome-api-sdk

# Using pipenv
pipenv install dome-api-sdk
```


### Configuration

The SDK accepts the following configuration options:

```python
from dome_api_sdk import DomeClient

config = {
    "api_key": "your-api-key",           # Authentication token
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

### Async Usage

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


This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- **Kurush Dubash** - [kurush@dome.com](mailto:kurush@dome.com)
- **Kunal Roy** - [kunal@dome.com](mailto:kunal@dome.com)

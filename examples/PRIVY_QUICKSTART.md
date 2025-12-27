# Privy Integration Quickstart

This guide shows how to integrate Privy embedded wallets with Dome SDK for Polymarket trading.

## Prerequisites

1. **Dome API Key** - Get from [Dome Dashboard](https://domeapi.io)
2. **Privy Account** - Get from [Privy Dashboard](https://privy.io)
3. **Privy Server Credentials**:
   - App ID
   - App Secret
   - Authorization Key (for server-side signing)

## Installation

```bash
pip install dome-api-sdk
```

## Environment Setup

Create a `.env` file:

```bash
# Dome API
DOME_API_KEY=your_dome_api_key

# Privy (from Dashboard > Settings > API Keys)
PRIVY_APP_ID=your_privy_app_id
PRIVY_APP_SECRET=your_privy_app_secret
PRIVY_AUTHORIZATION_KEY=wallet-auth:your_authorization_key
```

## Basic Usage

### Step 1: Initialize the Router

```python
import asyncio
import os
from dome_api_sdk import (
    PolymarketRouter,
    create_privy_client,
    create_privy_signer,
)

# Initialize router with Privy config
router = PolymarketRouter({
    "api_key": os.environ["DOME_API_KEY"],
    "privy": {
        "app_id": os.environ["PRIVY_APP_ID"],
        "app_secret": os.environ["PRIVY_APP_SECRET"],
        "authorization_key": os.environ["PRIVY_AUTHORIZATION_KEY"],
    },
})
```

### Step 2: Create a Signer for the User's Wallet

```python
# Get user's Privy wallet info (typically from your database)
privy_wallet_id = "your-user-privy-wallet-id"
wallet_address = "0x..."

# Create a signer using Privy client
privy = create_privy_client({
    "app_id": os.environ["PRIVY_APP_ID"],
    "app_secret": os.environ["PRIVY_APP_SECRET"],
    "authorization_key": os.environ["PRIVY_AUTHORIZATION_KEY"],
})
signer = create_privy_signer(privy, privy_wallet_id, wallet_address)
```

### Step 3: Link User to Polymarket

```python
async def link_user():
    # This signs ONE EIP-712 message to derive API credentials
    credentials = await router.link_user({
        "user_id": "your-internal-user-id",
        "signer": signer,
        "privy_wallet_id": privy_wallet_id,  # Enables auto-set allowances
        "auto_set_allowances": True,  # Automatically set token approvals
        "sponsor_gas": False,  # Optional: Use Privy gas sponsorship
    })

    print(f"API Key: {credentials.api_key}")
    print(f"User linked to Polymarket!")

    return credentials
```

### Step 4: Place Orders

```python
async def place_order(credentials):
    result = await router.place_order({
        "user_id": "your-internal-user-id",
        "market_id": "60487116984468020978247225474488676749601001829886755968952521846780452448915",
        "side": "buy",
        "size": 10,  # 10 shares
        "price": 0.65,  # $0.65 per share
        "signer": signer,
        "order_type": "GTC",  # Good Till Cancelled
    }, credentials)

    print(f"Order placed! Status: {result['status']}")
    print(f"Order ID: {result.get('orderId')}")
```

### Complete Example

```python
import asyncio
import os
from dome_api_sdk import (
    PolymarketRouter,
    create_privy_client,
    create_privy_signer,
)

async def main():
    # Initialize router
    router = PolymarketRouter({
        "api_key": os.environ["DOME_API_KEY"],
        "privy": {
            "app_id": os.environ["PRIVY_APP_ID"],
            "app_secret": os.environ["PRIVY_APP_SECRET"],
            "authorization_key": os.environ["PRIVY_AUTHORIZATION_KEY"],
        },
    })

    # Create signer for user's wallet
    privy = create_privy_client({
        "app_id": os.environ["PRIVY_APP_ID"],
        "app_secret": os.environ["PRIVY_APP_SECRET"],
        "authorization_key": os.environ["PRIVY_AUTHORIZATION_KEY"],
    })

    # Your user's Privy wallet info
    privy_wallet_id = "your-wallet-id"
    wallet_address = "0x..."

    signer = create_privy_signer(privy, privy_wallet_id, wallet_address)

    # Link user (one-time setup)
    credentials = await router.link_user({
        "user_id": "user-123",
        "signer": signer,
        "privy_wallet_id": privy_wallet_id,
        "auto_set_allowances": True,
    })

    print(f"User linked! API Key: {credentials.api_key[:10]}...")

    # Place an order
    result = await router.place_order({
        "user_id": "user-123",
        "market_id": "60487116984468020978247225474488676749601001829886755968952521846780452448915",
        "side": "buy",
        "size": 10,
        "price": 0.65,
        "signer": signer,
    }, credentials)

    print(f"Order placed! Status: {result['status']}")

    # Clean up
    await router.close()
    await privy.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Simplified Usage with Environment Variables

For even simpler usage, you can use `create_privy_signer_from_env`:

```python
from dome_api_sdk import create_privy_signer_from_env

# Automatically reads PRIVY_APP_ID, PRIVY_APP_SECRET, PRIVY_AUTHORIZATION_KEY
signer = create_privy_signer_from_env(privy_wallet_id, wallet_address)
```

## Checking and Setting Allowances

Before trading, users need token allowances set. You can check and set them:

```python
from dome_api_sdk import check_privy_wallet_allowances, set_privy_wallet_allowances

async def setup_allowances():
    # Check current allowances
    allowances = await check_privy_wallet_allowances(wallet_address)

    if not allowances.all_set:
        print("Setting allowances...")

        # Set allowances (requires Privy client)
        tx_hashes = await set_privy_wallet_allowances(
            privy,
            privy_wallet_id,
            wallet_address,
            on_progress=lambda step, curr, total: print(f"[{curr}/{total}] {step}"),
            sponsor=False,  # Set to True to use Privy gas sponsorship
        )

        print(f"Allowances set! TX hashes: {tx_hashes}")
    else:
        print("All allowances already set!")
```

## Order Types

Dome SDK supports all Polymarket order types:

- `GTC` (Good Till Cancelled) - Default, order stays on book until filled
- `GTD` (Good Till Date) - Order expires at specified time
- `FOK` (Fill Or Kill) - Must fill completely immediately or cancel
- `FAK` (Fill And Kill) - Fill as much as possible immediately, cancel rest

For copy trading, use `FOK` or `FAK` for instant confirmation:

```python
result = await router.place_order({
    "user_id": "user-123",
    "market_id": "...",
    "side": "buy",
    "size": 10,
    "price": 0.65,
    "signer": signer,
    "order_type": "FOK",  # Fill or Kill for instant confirmation
}, credentials)
```

## Error Handling

```python
async def safe_place_order():
    try:
        result = await router.place_order({
            "user_id": "user-123",
            "market_id": "...",
            "side": "buy",
            "size": 10,
            "price": 0.65,
            "signer": signer,
        }, credentials)
        return result
    except ValueError as e:
        print(f"Validation error: {e}")
    except Exception as e:
        print(f"Order failed: {e}")
```

## Next Steps

- Check out [EXTERNAL_WALLET_QUICKSTART.md](./EXTERNAL_WALLET_QUICKSTART.md) for MetaMask/Safe wallet integration
- See the example scripts in this directory for more advanced usage
- Visit [Dome API Documentation](https://docs.domeapi.io) for full API reference

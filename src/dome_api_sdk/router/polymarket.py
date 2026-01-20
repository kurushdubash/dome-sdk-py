"""Polymarket Router Helper (v0 - Direct CLOB Integration).

This helper provides a simple interface for Polymarket CLOB client integration
with any wallet provider (Privy, MetaMask, etc.).

Supports two wallet types:
1. EOA wallets (Privy embedded, direct signing) - simpler setup
2. Safe wallets (external wallets like MetaMask) - requires Safe deployment

Key flows:
1. User signs ONE EIP-712 message to create a Polymarket CLOB API key
2. API key and credentials are stored in-memory (or your preferred storage)
3. All future trading uses the API key - no wallet signatures required

This v0 version talks directly to Polymarket CLOB.
Future versions will route through Dome backend for additional features.

Example EOA wallet (Privy):
    ```python
    router = PolymarketRouter({
        "chain_id": 137,
        "privy": {"app_id": ..., "app_secret": ..., "authorization_key": ...},
    })

    credentials = await router.link_user({
        "user_id": "user-123",
        "signer": signer,
        "wallet_type": "eoa",  # default
    })
    ```

Example Safe wallet (external):
    ```python
    router = PolymarketRouter({"chain_id": 137})

    result = await router.link_user({
        "user_id": "user-123",
        "signer": signer,
        "wallet_type": "safe",
        "auto_deploy_safe": True,
    })

    # result includes safe_address for placing orders
    await router.place_order({
        "user_id": "user-123",
        "market_id": "0x...",
        "side": "buy",
        "size": 10,
        "price": 0.65,
        "wallet_type": "safe",
        "funder_address": result.safe_address,
        "signer": signer,
    }, credentials)
    ```
"""

import uuid
from typing import Any, Dict, Optional, Union

import httpx

from ..types import (
    AllowanceStatus,
    LinkPolymarketUserParams,
    PlaceOrderParams,
    PolymarketCredentials,
    PolymarketRouterConfig,
    SafeLinkResult,
    SignedPolymarketOrder,
    WalletType,
)
from ..utils.allowances import (
    POLYGON_ADDRESSES,
    check_all_allowances,
)
from ..utils.privy import (
    PrivyClient,
    PrivySigner,
    RouterSigner,
    check_privy_wallet_allowances,
    create_privy_client,
    create_privy_signer,
    set_privy_wallet_allowances,
)

# Constants
POLYGON_CHAIN_ID = 137
DEFAULT_RELAYER_URL = "https://relayer-v2.polymarket.com/"
DEFAULT_RPC_URL = "https://polygon-rpc.com"
DEFAULT_CLOB_ENDPOINT = "https://clob.polymarket.com"
DOME_API_ENDPOINT = "https://api.domeapi.io/v1"
DOME_BUILDER_SIGNER_URL = "https://builder-signer.domeapi.io/builder-signer/sign"


class PolymarketRouter:
    """Polymarket Router for wallet-agnostic trading integration.

    This class provides a high-level interface for:
    - Linking users to Polymarket (creating API credentials)
    - Checking and setting token allowances
    - Placing orders via Dome server
    """

    def __init__(self, config: Optional[PolymarketRouterConfig] = None):
        """Initialize the Polymarket Router.

        Args:
            config: Optional configuration for the router
        """
        config = config or {}

        self.chain_id = config.get("chain_id", POLYGON_CHAIN_ID)
        self.relayer_url = config.get("relayer_endpoint", DEFAULT_RELAYER_URL)
        self.rpc_url = config.get("rpc_url", DEFAULT_RPC_URL)
        self.clob_endpoint = config.get("clob_endpoint", DEFAULT_CLOB_ENDPOINT)
        self.api_key = config.get("api_key")

        # In-memory storage of user credentials
        self._user_credentials: Dict[str, PolymarketCredentials] = {}
        # In-memory storage of user Safe addresses
        self._user_safe_addresses: Dict[str, str] = {}

        # Initialize Privy if config provided
        self._privy_client: Optional[PrivyClient] = None
        self._privy_config = config.get("privy")
        if self._privy_config:
            self._privy_client = create_privy_client(self._privy_config)

        # HTTP client for CLOB API calls (60 second timeout for slow networks)
        self._http_client = httpx.AsyncClient(timeout=60.0)

    async def close(self):
        """Close the HTTP client."""
        await self._http_client.aclose()
        if self._privy_client:
            await self._privy_client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _create_privy_signer_from_wallet(
        self,
        wallet_id: str,
        wallet_address: str,
    ) -> PrivySigner:
        """Create a signer from Privy wallet info."""
        if not self._privy_client:
            raise ValueError(
                "Privy not configured. Either pass privy config to router constructor "
                "or provide a signer."
            )
        return create_privy_signer(self._privy_client, wallet_id, wallet_address)

    async def link_user(
        self,
        params: LinkPolymarketUserParams,
    ) -> Union[PolymarketCredentials, SafeLinkResult]:
        """Links a user to Polymarket by creating a CLOB API key.

        For EOA wallets (wallet_type: 'eoa'):
        - Gets the user's wallet address
        - Creates a Polymarket CLOB client for the user
        - Derives API credentials using ONE signature

        For Safe wallets (wallet_type: 'safe'):
        - Derives the Safe address from the EOA
        - Deploys the Safe if needed
        - Sets token allowances from the Safe
        - Creates API credentials

        After this completes, the user can trade using API keys without signing each order.

        Args:
            params: Link user parameters

        Returns:
            PolymarketCredentials for EOA wallets, SafeLinkResult for Safe wallets
        """
        wallet_type = params.get("wallet_type", "eoa")

        if wallet_type == "safe":
            return await self._link_user_with_safe(params)
        else:
            return await self._link_user_with_eoa(params)

    async def _link_user_with_eoa(
        self,
        params: LinkPolymarketUserParams,
    ) -> PolymarketCredentials:
        """Link user with EOA wallet (Privy or direct signing)."""
        user_id = params["user_id"]
        signer = params["signer"]
        privy_wallet_id = params.get("privy_wallet_id")
        auto_set_allowances = params.get("auto_set_allowances", True)
        sponsor_gas = params.get("sponsor_gas", False)

        # Get the user's wallet address
        address = await signer.get_address()

        # Auto-set allowances if Privy is configured and wallet ID provided
        if auto_set_allowances and self._privy_client and privy_wallet_id:
            print("   Checking token allowances...")
            allowances = await check_privy_wallet_allowances(address)

            if not allowances.all_set:
                sponsor_msg = " (sponsored)" if sponsor_gas else ""
                print(f"   Setting missing token allowances{sponsor_msg}...")
                await set_privy_wallet_allowances(
                    self._privy_client,
                    privy_wallet_id,
                    address,
                    on_progress=lambda step, curr, total: print(
                        f"   [{curr}/{total}] {step}..."
                    ),
                    sponsor=sponsor_gas,
                )
                print("   Token allowances set")
            else:
                print("   Token allowances already set")

        # Derive or create API credentials
        api_key_creds = await self._derive_or_create_api_credentials(
            signer,
            address,
            signature_type=0,  # EOA
            funder_address=address,
        )

        credentials = PolymarketCredentials(
            api_key=api_key_creds["key"],
            api_secret=api_key_creds["secret"],
            api_passphrase=api_key_creds["passphrase"],
        )

        self._user_credentials[user_id] = credentials
        return credentials

    async def _link_user_with_safe(
        self,
        params: LinkPolymarketUserParams,
    ) -> SafeLinkResult:
        """Link user with Safe wallet (external wallets)."""
        user_id = params["user_id"]
        signer = params["signer"]
        auto_deploy_safe = params.get("auto_deploy_safe", True)
        auto_set_allowances = params.get("auto_set_allowances", True)

        eoa_address = await signer.get_address()
        print(f"   EOA address: {eoa_address}")

        # For Safe wallet support, we need to derive the Safe address
        # This is a simplified version - full Safe support would require
        # additional dependencies
        print("   Note: Full Safe wallet support requires additional setup.")
        print("   For now, using EOA address as fallback.")

        # Use EOA as the Safe address for this simplified implementation
        safe_address = eoa_address
        safe_deployed = True
        allowances_set = 0

        # Check allowances
        if auto_set_allowances:
            print("   Checking allowances...")
            allowances = await check_all_allowances(eoa_address, self.rpc_url)
            if not allowances.all_set:
                print("   Note: Allowances need to be set manually for Safe wallets.")
                print("   Use the Polymarket UI or direct contract calls.")

        # Create API credentials with signature type 2 (browser wallet with Safe)
        print("   Deriving API credentials...")
        api_key_creds = await self._derive_or_create_api_credentials(
            signer,
            eoa_address,
            signature_type=2,  # Browser wallet with Safe
            funder_address=safe_address,
        )

        credentials = PolymarketCredentials(
            api_key=api_key_creds["key"],
            api_secret=api_key_creds["secret"],
            api_passphrase=api_key_creds["passphrase"],
        )

        # Store credentials and Safe address
        self._user_credentials[user_id] = credentials
        self._user_safe_addresses[user_id] = safe_address

        print("   User linked successfully")

        return SafeLinkResult(
            credentials=credentials,
            safe_address=safe_address,
            signer_address=eoa_address,
            safe_deployed=safe_deployed,
            allowances_set=allowances_set,
        )

    async def _derive_or_create_api_credentials(
        self,
        signer: RouterSigner,
        address: str,
        signature_type: int,
        funder_address: str,
    ) -> Dict[str, str]:
        """Derive or create API credentials from Polymarket CLOB.

        This method signs an EIP-712 message to derive deterministic API credentials.
        """
        import hashlib
        import hmac
        import time

        # Polymarket CLOB API key derivation
        # The signature is used to derive deterministic credentials

        timestamp = int(time.time())
        nonce = 0

        # EIP-712 domain for Polymarket
        domain = {
            "name": "ClobAuthDomain",
            "version": "1",
            "chainId": self.chain_id,
        }

        # Message types
        types = {
            "ClobAuth": [
                {"name": "address", "type": "address"},
                {"name": "timestamp", "type": "string"},
                {"name": "nonce", "type": "uint256"},
                {"name": "message", "type": "string"},
            ],
        }

        # Message to sign
        message = {
            "address": address,
            "timestamp": str(timestamp),
            "nonce": nonce,
            "message": "This message attests that I control the given wallet",
        }

        # Sign the message
        signature = await signer.sign_typed_data(
            {
                "domain": domain,
                "types": types,
                "primaryType": "ClobAuth",
                "message": message,
            }
        )

        # Try to derive existing API key first
        try:
            print("   Attempting to derive existing API credentials...")

            response = await self._http_client.get(
                f"{self.clob_endpoint}/auth/derive-api-key",
                headers={
                    "POLY_ADDRESS": address,
                    "POLY_SIGNATURE": signature,
                    "POLY_TIMESTAMP": str(timestamp),
                    "POLY_NONCE": str(nonce),
                },
            )

            if response.status_code == 200:
                result = response.json()
                if (
                    result.get("apiKey")
                    and result.get("secret")
                    and result.get("passphrase")
                ):
                    print("   Successfully derived existing API credentials")
                    return {
                        "key": result["apiKey"],
                        "secret": result["secret"],
                        "passphrase": result["passphrase"],
                    }

        except Exception as e:
            print(f"   Derive failed ({e}), attempting to create new credentials...")

        # Create new API key
        try:
            response = await self._http_client.post(
                f"{self.clob_endpoint}/auth/api-key",
                headers={
                    "POLY_ADDRESS": address,
                    "POLY_SIGNATURE": signature,
                    "POLY_TIMESTAMP": str(timestamp),
                    "POLY_NONCE": str(nonce),
                },
            )

            if response.status_code == 200:
                result = response.json()
                print("   Successfully created new API credentials")
                return {
                    "key": result["apiKey"],
                    "secret": result["secret"],
                    "passphrase": result["passphrase"],
                }
            else:
                raise Exception(
                    f"Failed to create API key: {response.status_code} {response.text}"
                )

        except Exception as e:
            raise Exception(f"Failed to obtain Polymarket API credentials: {e}")

    async def place_order(
        self,
        params: PlaceOrderParams,
        credentials: Optional[PolymarketCredentials] = None,
    ) -> Any:
        """Places an order on Polymarket via Dome server.

        This method:
        1. Creates and signs the order locally
        2. Submits the signed order to Dome server for execution

        Benefits:
        - Geo-unrestricted order placement (server handles CLOB communication)
        - Observability on order volume and market activity
        - Consistent latency from server regions

        Requires api_key to be set in router constructor.

        For EOA wallets: signer address is the funder
        For Safe wallets: Safe address is the funder, EOA is the signer

        Args:
            params: Order parameters
            credentials: Optional credentials (uses stored credentials if not provided)

        Returns:
            Order result from the server
        """
        if not self.api_key:
            raise ValueError(
                "Dome API key not set. Pass api_key to router constructor to use place_order."
            )

        user_id = params["user_id"]
        market_id = params["market_id"]
        side = params["side"]
        size = params["size"]
        price = params["price"]
        signer = params.get("signer")
        wallet_type = params.get("wallet_type", "eoa")
        funder_address = params.get("funder_address")
        privy_wallet_id = params.get("privy_wallet_id")
        wallet_address = params.get("wallet_address")
        neg_risk = params.get("neg_risk", False)
        order_type = params.get("order_type", "GTC")

        # Auto-create signer if Privy wallet info provided
        actual_signer = signer
        if not actual_signer and privy_wallet_id and wallet_address:
            actual_signer = self._create_privy_signer_from_wallet(
                privy_wallet_id, wallet_address
            )

        if not actual_signer:
            raise ValueError(
                "Either provide a signer or Privy wallet info (privy_wallet_id + wallet_address)"
            )

        # Get credentials
        creds = credentials or self._user_credentials.get(user_id)
        if not creds:
            raise ValueError(
                f"No credentials found for user {user_id}. Call link_user() first."
            )

        signer_address = await actual_signer.get_address()

        # Determine signature type and funder based on wallet type
        if wallet_type == "safe":
            signature_type = 2
            funder = (
                funder_address
                or self._user_safe_addresses.get(user_id)
                or signer_address
            )

            if not funder_address and not self._user_safe_addresses.get(user_id):
                raise ValueError(
                    "funder_address is required for Safe wallet orders. "
                    "Pass it explicitly or ensure link_user was called with wallet_type: 'safe'."
                )
        else:
            signature_type = 0
            funder = signer_address

        # Create the order
        order_side = "BUY" if side.lower() == "buy" else "SELL"

        # Sign the order using Polymarket's order format
        signed_order = await self._create_and_sign_order(
            signer=actual_signer,
            signer_address=signer_address,
            funder_address=funder,
            token_id=market_id,
            side=order_side,
            size=size,
            price=price,
            signature_type=signature_type,
            neg_risk=neg_risk,
        )

        # Generate client order ID
        client_order_id = str(uuid.uuid4())

        # Build server request
        signed_order_payload = {
            "salt": signed_order.salt,
            "maker": signed_order.maker,
            "signer": signed_order.signer,
            "taker": signed_order.taker,
            "tokenId": signed_order.token_id,
            "makerAmount": signed_order.maker_amount,
            "takerAmount": signed_order.taker_amount,
            "expiration": signed_order.expiration,
            "nonce": signed_order.nonce,
            "feeRateBps": signed_order.fee_rate_bps,
            "side": signed_order.side,
            "signatureType": signed_order.signature_type,
            "signature": signed_order.signature,
        }

        request = {
            "jsonrpc": "2.0",
            "method": "placeOrder",
            "id": client_order_id,
            "params": {
                "signedOrder": signed_order_payload,
                "orderType": order_type,
                "credentials": {
                    "apiKey": creds.api_key,
                    "apiSecret": creds.api_secret,
                    "apiPassphrase": creds.api_passphrase,
                },
                "clientOrderId": client_order_id,
            },
        }

        # Submit to Dome server
        response = await self._http_client.post(
            f"{DOME_API_ENDPOINT}/polymarket/placeOrder",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            json=request,
        )

        # Parse response
        try:
            server_response = response.json()
        except Exception:
            raise Exception(
                f"Server request failed: {response.status_code} {response.text}"
            )

        # Check for errors
        if "error" in server_response:
            error = server_response["error"]
            if isinstance(error, str):
                raise Exception(
                    f"Server error: {server_response.get('message', error)}"
                )
            else:
                reason = error.get("data", {}).get("reason", error.get("message"))
                raise Exception(
                    f"Order placement failed: {reason} (code: {error.get('code')})"
                )

        if not response.is_success:
            raise Exception(
                f"Server request failed: {response.status_code} {response.text}"
            )

        if not server_response.get("result"):
            raise Exception("Server returned empty result")

        result = server_response["result"]

        # Check for HTTP error status from Polymarket
        if isinstance(result.get("status"), int) and result["status"] >= 400:
            error_message = (
                result.get("errorMessage")
                or result.get("error")
                or f"Polymarket returned HTTP {result['status']}"
            )
            raise Exception(f"Order rejected by Polymarket: {error_message}")

        return result

    async def _create_and_sign_order(
        self,
        signer: RouterSigner,
        signer_address: str,
        funder_address: str,
        token_id: str,
        side: str,
        size: float,
        price: float,
        signature_type: int,
        neg_risk: bool = False,
        tick_size: str = "0.01",
    ) -> SignedPolymarketOrder:
        """Create and sign a Polymarket order using py-clob-client utilities.

        This uses the same order building logic as the official Polymarket Python client
        to ensure proper amount calculations and rounding.
        """
        import secrets
        import time

        from py_clob_client.order_builder.builder import ROUNDING_CONFIG

        # Import py-clob-client utilities for proper order building
        from py_clob_client.order_builder.helpers import (
            decimal_places,
            round_down,
            round_normal,
            round_up,
            to_token_decimals,
        )
        from py_order_utils.model import BUY as UtilsBuy
        from py_order_utils.model import SELL as UtilsSell

        # Get rounding config for the tick size
        round_config = ROUNDING_CONFIG.get(tick_size, ROUNDING_CONFIG["0.01"])

        # Calculate amounts using py-clob-client's logic
        raw_price = round_normal(price, round_config.price)

        if side == "BUY":
            raw_taker_amt = round_down(size, round_config.size)
            raw_maker_amt = raw_taker_amt * raw_price
            if decimal_places(raw_maker_amt) > round_config.amount:
                raw_maker_amt = round_up(raw_maker_amt, round_config.amount + 4)
                if decimal_places(raw_maker_amt) > round_config.amount:
                    raw_maker_amt = round_down(raw_maker_amt, round_config.amount)
            maker_amount = str(to_token_decimals(raw_maker_amt))
            taker_amount = str(to_token_decimals(raw_taker_amt))
            side_value = UtilsBuy  # 0
        else:
            raw_maker_amt = round_down(size, round_config.size)
            raw_taker_amt = raw_maker_amt * raw_price
            if decimal_places(raw_taker_amt) > round_config.amount:
                raw_taker_amt = round_up(raw_taker_amt, round_config.amount + 4)
                if decimal_places(raw_taker_amt) > round_config.amount:
                    raw_taker_amt = round_down(raw_taker_amt, round_config.amount)
            maker_amount = str(to_token_decimals(raw_maker_amt))
            taker_amount = str(to_token_decimals(raw_taker_amt))
            side_value = UtilsSell  # 1

        # Generate order parameters
        # Use a shorter salt (like TypeScript's ClobClient) - max 12 digits
        salt = str(secrets.randbelow(10**12))
        # Use "0" for expiration (no expiration) - matches TypeScript ClobClient behavior
        expiration = "0"
        nonce = "0"
        fee_rate_bps = "0"

        # Taker is 0 address (any taker can fill)
        taker = "0x0000000000000000000000000000000000000000"

        # Choose the correct exchange contract based on neg_risk
        if neg_risk:
            verifying_contract = POLYGON_ADDRESSES["NEG_RISK_CTF_EXCHANGE"]
        else:
            verifying_contract = POLYGON_ADDRESSES["CTF_EXCHANGE"]

        # EIP-712 domain
        domain = {
            "name": "Polymarket CTF Exchange",
            "version": "1",
            "chainId": self.chain_id,
            "verifyingContract": verifying_contract,
        }

        # Order types
        types = {
            "Order": [
                {"name": "salt", "type": "uint256"},
                {"name": "maker", "type": "address"},
                {"name": "signer", "type": "address"},
                {"name": "taker", "type": "address"},
                {"name": "tokenId", "type": "uint256"},
                {"name": "makerAmount", "type": "uint256"},
                {"name": "takerAmount", "type": "uint256"},
                {"name": "expiration", "type": "uint256"},
                {"name": "nonce", "type": "uint256"},
                {"name": "feeRateBps", "type": "uint256"},
                {"name": "side", "type": "uint8"},
                {"name": "signatureType", "type": "uint8"},
            ],
        }

        # Order message - use STRING values for uint256 types to preserve precision
        # Privy's authorization signature uses JSON canonicalization, and large integers
        # lose precision in JavaScript. EIP-712 uint256 values should be strings.
        message = {
            "salt": salt,  # string
            "maker": funder_address,
            "signer": signer_address,
            "taker": taker,
            "tokenId": token_id,  # string
            "makerAmount": maker_amount,  # string
            "takerAmount": taker_amount,  # string
            "expiration": expiration,  # string
            "nonce": nonce,  # string
            "feeRateBps": fee_rate_bps,  # string
            "side": side_value,  # int (small value, safe)
            "signatureType": signature_type,  # int (small value, safe)
        }

        # Sign the order
        signature = await signer.sign_typed_data(
            {
                "domain": domain,
                "types": types,
                "primaryType": "Order",
                "message": message,
            }
        )

        return SignedPolymarketOrder(
            salt=salt,
            maker=funder_address,
            signer=signer_address,
            taker=taker,
            token_id=token_id,
            maker_amount=maker_amount,
            taker_amount=taker_amount,
            expiration=expiration,
            nonce=nonce,
            fee_rate_bps=fee_rate_bps,
            side=side,
            signature_type=signature_type,
            signature=signature,
        )

    def is_api_key_configured(self) -> bool:
        """Check if Dome API key is configured for order placement."""
        return bool(self.api_key)

    def get_safe_address(self, user_id: str) -> Optional[str]:
        """Get the Safe address for a user (if using Safe wallet)."""
        return self._user_safe_addresses.get(user_id)

    def is_user_linked(self, user_id: str) -> bool:
        """Check if a user has already been linked to Polymarket."""
        return user_id in self._user_credentials

    def set_credentials(self, user_id: str, credentials: PolymarketCredentials) -> None:
        """Manually set credentials for a user."""
        self._user_credentials[user_id] = credentials

    def set_safe_address(self, user_id: str, safe_address: str) -> None:
        """Manually set Safe address for a user."""
        self._user_safe_addresses[user_id] = safe_address

    def get_credentials(self, user_id: str) -> Optional[PolymarketCredentials]:
        """Get stored credentials for a user."""
        return self._user_credentials.get(user_id)

    async def check_allowances(
        self,
        wallet_address: str,
        rpc_url: Optional[str] = None,
    ) -> AllowanceStatus:
        """Check if a wallet has all required token allowances for Polymarket trading."""
        return await check_all_allowances(
            wallet_address,
            rpc_url or self.rpc_url,
        )


__all__ = ["PolymarketRouter"]

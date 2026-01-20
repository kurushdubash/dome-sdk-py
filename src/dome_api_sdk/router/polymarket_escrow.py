"""Polymarket Router with Fee Escrow.

Drop-in replacement for PolymarketRouter that automatically handles
fee escrow for every order. Users simply swap the class name:

Before: router = PolymarketRouter({"api_key": ...})
After:  router = PolymarketRouterWithEscrow({"api_key": ..., "escrow": {...}})

The router will:
1. Generate a unique orderId for each order
2. Create and sign a fee authorization (EIP-712)
3. Include the signed fee auth in the order request
4. The Dome server then pulls the fee to escrow before placing the order
"""

import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional, TypedDict

from .polymarket import PolymarketRouter
from ..escrow import (
    OrderParams,
    generate_order_id,
    create_fee_authorization,
    sign_fee_authorization_with_signer,
    calculate_fee,
    calculate_order_size_usdc,
    ESCROW_CONTRACT_POLYGON,
    ZERO_ADDRESS,
)
from ..types import (
    PlaceOrderParams,
    PolymarketCredentials,
    PolymarketRouterConfig,
)


class EscrowConfig(TypedDict, total=False):
    """Escrow configuration for the router."""

    fee_bps: int
    """Fee in basis points (e.g., 25 = 0.25%). Default: 25"""

    escrow_address: str
    """Escrow contract address. Default: Polygon mainnet contract"""

    chain_id: int
    """Chain ID. Default: 137 (Polygon)"""

    affiliate: str
    """Affiliate address for fee sharing (optional)"""

    deadline_seconds: int
    """Deadline for fee authorization in seconds. Default: 3600 (1 hour)"""


class PolymarketRouterWithEscrowConfig(PolymarketRouterConfig, total=False):
    """Extended router config with escrow settings."""

    escrow: EscrowConfig


class PlaceOrderWithEscrowParams(PlaceOrderParams, total=False):
    """Extended place order params with escrow options."""

    fee_bps: int
    """Override fee basis points for this order"""

    affiliate: str
    """Override affiliate for this order"""

    skip_escrow: bool
    """Skip fee escrow for this order"""


@dataclass
class ResolvedEscrowConfig:
    """Resolved escrow configuration with all defaults applied."""

    fee_bps: int
    escrow_address: str
    chain_id: int
    affiliate: str
    deadline_seconds: int


class PolymarketRouterWithEscrow(PolymarketRouter):
    """Polymarket Router with automatic fee escrow.

    Extends PolymarketRouter to automatically generate and sign fee
    authorizations for every order placed.

    Example:
        ```python
        router = PolymarketRouterWithEscrow({
            "api_key": "your-dome-api-key",
            "escrow": {
                "fee_bps": 25,  # 0.25%
                "affiliate": "0x...",  # optional
            },
            "privy": {
                "app_id": "...",
                "app_secret": "...",
                "authorization_key": "...",
            },
        })

        # Link user first
        credentials = await router.link_user({
            "user_id": "user-123",
            "signer": signer,
        })

        # Place order with automatic fee escrow
        result = await router.place_order({
            "user_id": "user-123",
            "market_id": "token-id",
            "side": "buy",
            "size": 10,
            "price": 0.65,
            "signer": signer,
        })
        ```
    """

    def __init__(self, config: Optional[PolymarketRouterWithEscrowConfig] = None):
        """Initialize the Polymarket Router with Escrow.

        Args:
            config: Optional configuration for the router
        """
        config = config or {}
        super().__init__(config)

        # Set escrow defaults
        escrow_config = config.get("escrow", {})
        self._escrow_config = ResolvedEscrowConfig(
            fee_bps=escrow_config.get("fee_bps", 25),  # 0.25%
            escrow_address=escrow_config.get(
                "escrow_address", ESCROW_CONTRACT_POLYGON
            ),
            chain_id=escrow_config.get("chain_id", 137),
            affiliate=escrow_config.get("affiliate", ZERO_ADDRESS),
            deadline_seconds=escrow_config.get("deadline_seconds", 3600),
        )

    async def place_order(
        self,
        params: PlaceOrderWithEscrowParams,
        credentials: Optional[PolymarketCredentials] = None,
    ) -> Any:
        """Places an order on Polymarket with automatic fee escrow.

        This method:
        1. Generates a unique orderId from order parameters
        2. Creates and signs a fee authorization (EIP-712)
        3. Submits the order with fee auth to Dome server
        4. Server pulls fee to escrow, then places the order

        On fill: Server distributes fee to Dome + affiliate
        On cancel: Server refunds remaining fee to user

        Args:
            params: Order parameters (extends PlaceOrderParams with escrow options)
            credentials: Optional credentials (uses stored credentials if not provided)

        Returns:
            Order result from the server
        """
        # If skip_escrow is True, use parent implementation
        if params.get("skip_escrow"):
            return await super().place_order(params, credentials)

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
        fee_bps = params.get("fee_bps", self._escrow_config.fee_bps)
        affiliate = params.get("affiliate", self._escrow_config.affiliate)

        # Get or create signer
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

        # Determine payer (funder for escrow)
        if wallet_type == "safe":
            payer_address = (
                funder_address
                or self._user_safe_addresses.get(user_id)
                or signer_address
            )
            if not funder_address and not self._user_safe_addresses.get(user_id):
                raise ValueError("funder_address is required for Safe wallet orders.")
            signature_type = 2
        else:
            payer_address = signer_address
            signature_type = 0

        # Calculate order size in USDC and fee
        order_size_usdc = calculate_order_size_usdc(size, price)
        fee_amount = calculate_fee(order_size_usdc, fee_bps)

        # Generate unique orderId
        timestamp = int(time.time() * 1000)
        order_id = generate_order_id(
            OrderParams(
                chain_id=self._escrow_config.chain_id,
                user_address=payer_address,
                market_id=market_id,
                side=side,
                size=order_size_usdc,
                price=price,
                timestamp=timestamp,
            )
        )

        # Create fee authorization
        fee_auth = create_fee_authorization(
            order_id=order_id,
            payer=payer_address,
            fee_amount=fee_amount,
            deadline_seconds=self._escrow_config.deadline_seconds,
        )

        # Sign fee authorization
        signed_fee_auth = await sign_fee_authorization_with_signer(
            signer=actual_signer,
            escrow_address=self._escrow_config.escrow_address,
            fee_auth=fee_auth,
            chain_id=self._escrow_config.chain_id,
        )

        # Create signed order using parent's logic
        signed_order = await self._create_and_sign_order(
            signer=actual_signer,
            signer_address=signer_address,
            funder_address=payer_address,
            token_id=market_id,
            side="BUY" if side.lower() == "buy" else "SELL",
            size=size,
            price=price,
            signature_type=signature_type,
            neg_risk=neg_risk,
        )

        # Build request with fee auth
        client_order_id = str(uuid.uuid4())

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

        request: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": "placeOrder",
            "id": client_order_id,
            "params": {
                # Required for escrow: identify payer and signer
                "payerAddress": payer_address,
                "signerAddress": signer_address,
                "signedOrder": signed_order_payload,
                "orderType": order_type,
                "credentials": {
                    "apiKey": creds.api_key,
                    "apiSecret": creds.api_secret,
                    "apiPassphrase": creds.api_passphrase,
                },
                "clientOrderId": client_order_id,
                "feeAuth": {
                    "orderId": signed_fee_auth.order_id,
                    "payer": signed_fee_auth.payer,
                    "feeAmount": str(signed_fee_auth.fee_amount),
                    "deadline": signed_fee_auth.deadline,  # Must be number
                    "signature": signed_fee_auth.signature,
                },
            },
        }

        # Add affiliate if not zero address
        if affiliate != ZERO_ADDRESS:
            request["params"]["affiliate"] = affiliate

        # Submit to Dome server
        from ..router.polymarket import DOME_API_ENDPOINT

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

    def get_escrow_config(self) -> ResolvedEscrowConfig:
        """Get the escrow configuration."""
        return self._escrow_config

    def calculate_order_fee(
        self, size: float, price: float, fee_bps: Optional[int] = None
    ) -> int:
        """Calculate the fee for an order.

        Args:
            size: Order size in shares
            price: Price per share (0.00 to 1.00)
            fee_bps: Optional override for fee basis points

        Returns:
            Fee amount in USDC (6 decimals)
        """
        order_size_usdc = calculate_order_size_usdc(size, price)
        return calculate_fee(order_size_usdc, fee_bps or self._escrow_config.fee_bps)


__all__ = [
    "PolymarketRouterWithEscrow",
    "PolymarketRouterWithEscrowConfig",
    "PlaceOrderWithEscrowParams",
    "EscrowConfig",
    "ResolvedEscrowConfig",
]

"""Privy Utility Functions.

Helper functions to easily integrate Privy with Dome SDK for Polymarket trading.
These utilities handle server-side wallet signing using Privy's authorization keys.
"""

import base64
import hashlib
import json
import os
from typing import Any, Callable, Dict, List, Optional, Protocol, runtime_checkable

import httpx

from ..types import (
    AllowanceStatus,
    Eip712Payload,
    PrivyRouterConfig,
)

# Authorization key prefix used by Privy
AUTHORIZATION_PRIVATE_KEY_PREFIX = "wallet-auth:"


def _normalize_p256_private_key_to_scalar(authorization_key: str) -> bytes:
    """Extract P256 private key scalar from Privy authorization key.

    The authorization key is in format: wallet-auth:<base64-encoded-key>
    The base64 content contains DER-encoded key material.
    We need to extract the 32-byte private key scalar.
    """
    # Remove prefix
    key_data = authorization_key.replace(AUTHORIZATION_PRIVATE_KEY_PREFIX, "")

    # Decode base64
    raw_bytes = base64.b64decode(key_data)

    # Find the private key scalar (32 bytes after marker [0x04, 0x20])
    marker = bytes([0x04, 0x20])
    marker_pos = raw_bytes.find(marker)

    if marker_pos == -1:
        raise ValueError("Invalid wallet authorization private key")

    # Extract 32-byte scalar
    private_key_scalar = raw_bytes[marker_pos + 2 : marker_pos + 34]

    if len(private_key_scalar) != 32:
        raise ValueError("Invalid wallet authorization private key length")

    return private_key_scalar


def _create_authorization_signature(
    method: str,
    url: str,
    body: Dict[str, Any],
    app_id: str,
    authorization_key: str,
    idempotency_key: Optional[str] = None,
) -> str:
    """Create Privy authorization signature for a request.

    This follows Privy's authorization signature spec:
    1. Create canonical JSON payload
    2. SHA256 hash
    3. Sign with P256 (ECDSA)
    4. Return base64-encoded DER signature
    """
    try:
        from ecdsa import NIST256p, SigningKey
    except ImportError:
        raise ImportError(
            "The 'ecdsa' package is required for Privy authorization signatures. "
            "Install it with: pip install ecdsa"
        )

    # Build the payload to sign
    headers = {"privy-app-id": app_id}
    if idempotency_key:
        headers["privy-idempotency-key"] = idempotency_key

    payload = {
        "version": 1,
        "method": method,
        "url": url,
        "body": body,
        "headers": headers,
    }

    # Canonicalize JSON (sorted keys, no whitespace)
    canonical_json = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    canonical_bytes = canonical_json.encode("utf-8")

    # Hash with SHA256
    message_hash = hashlib.sha256(canonical_bytes).digest()

    # Get private key scalar
    private_key_scalar = _normalize_p256_private_key_to_scalar(authorization_key)

    # Create signing key and sign
    signing_key = SigningKey.from_string(private_key_scalar, curve=NIST256p)
    signature_der = signing_key.sign_digest(
        message_hash, sigencode=lambda r, s, order: _encode_der_signature(r, s)
    )

    return base64.b64encode(signature_der).decode("utf-8")


def _encode_der_signature(r: int, s: int) -> bytes:
    """Encode ECDSA signature (r, s) in DER format."""

    def encode_integer(value: int) -> bytes:
        # Convert to bytes, big-endian
        value_bytes = value.to_bytes((value.bit_length() + 7) // 8, byteorder="big")
        # Add leading zero if high bit is set (to indicate positive)
        if value_bytes[0] & 0x80:
            value_bytes = b"\x00" + value_bytes
        return bytes([0x02, len(value_bytes)]) + value_bytes

    r_encoded = encode_integer(r)
    s_encoded = encode_integer(s)

    # Sequence tag (0x30) + length + contents
    contents = r_encoded + s_encoded
    return bytes([0x30, len(contents)]) + contents


# Polygon contract addresses for Polymarket
POLYGON_ADDRESSES = {
    "USDC": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
    "CTF": "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045",
    "CTF_EXCHANGE": "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E",
    "NEG_RISK_CTF_EXCHANGE": "0xC5d563A36AE78145C45a50134d48A1215220f80a",
    "NEG_RISK_ADAPTER": "0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296",
}


@runtime_checkable
class RouterSigner(Protocol):
    """Minimal interface for any wallet implementation.

    This keeps the SDK wallet-agnostic (works with Privy, MetaMask, RainbowKit, etc.)
    """

    async def get_address(self) -> str:
        """Returns the EVM address of the user wallet."""
        ...

    async def sign_typed_data(self, payload: Eip712Payload) -> str:
        """Signs EIP-712 typed data and returns a 0x-prefixed signature."""
        ...


class PrivyClient:
    """Privy client for server-side wallet operations.

    This wraps Privy's server-side API for signing operations using authorization keys.
    """

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        authorization_key: str,
    ):
        """Initialize the Privy client.

        Args:
            app_id: Privy App ID
            app_secret: Privy App Secret
            authorization_key: Privy Authorization Private Key (wallet-auth:...)
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.authorization_key = authorization_key
        self._http_client = httpx.AsyncClient(timeout=30.0)

    async def sign_typed_data(
        self,
        wallet_id: str,
        typed_data: Dict[str, Any],
    ) -> str:
        """Sign EIP-712 typed data using Privy's server-side API.

        Args:
            wallet_id: Privy wallet ID
            typed_data: EIP-712 typed data to sign (with camelCase or snake_case keys)

        Returns:
            The signature as a hex string
        """
        # Create Basic Auth header
        credentials = f"{self.app_id}:{self.app_secret}"
        auth_header = base64.b64encode(credentials.encode()).decode()

        # Privy REST API expects snake_case keys for typed_data
        # Convert from camelCase if needed
        api_typed_data = {
            "domain": typed_data.get("domain", {}),
            "types": typed_data.get("types", {}),
            "primary_type": typed_data.get("primaryType")
            or typed_data.get("primary_type"),
            "message": typed_data.get("message", {}),
        }

        # Build the request body
        request_body = {
            "method": "eth_signTypedData_v4",
            "params": {
                "typed_data": api_typed_data,
            },
        }

        # Build the full URL for authorization signature
        url = f"https://auth.privy.io/api/v1/wallets/{wallet_id}/rpc"

        # Create authorization signature
        auth_signature = _create_authorization_signature(
            method="POST",
            url=url,
            body=request_body,
            app_id=self.app_id,
            authorization_key=self.authorization_key,
        )

        response = await self._http_client.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Basic {auth_header}",
                "privy-app-id": self.app_id,
                "privy-authorization-signature": auth_signature,
            },
            json=request_body,
        )

        if response.status_code != 200:
            raise Exception(
                f"Privy signing failed: {response.status_code} {response.text}"
            )

        result = response.json()
        return result.get("data", {}).get("signature", result.get("signature"))

    async def send_transaction(
        self,
        wallet_id: str,
        transaction: Dict[str, Any],
        chain_id: int = 137,
        sponsor: bool = False,
    ) -> str:
        """Send a transaction using Privy's server-side API.

        Args:
            wallet_id: Privy wallet ID
            transaction: Transaction data (to, data, value, etc.)
            chain_id: Chain ID (default: 137 for Polygon)
            sponsor: Whether to use Privy gas sponsorship

        Returns:
            The transaction hash
        """
        credentials = f"{self.app_id}:{self.app_secret}"
        auth_header = base64.b64encode(credentials.encode()).decode()

        # Build the request payload
        request_body = {
            "method": "eth_sendTransaction",
            "caip2": f"eip155:{chain_id}",
            "params": {
                "transaction": transaction,
            },
        }

        if sponsor:
            request_body["params"]["sponsor"] = True

        # Build the full URL for authorization signature
        url = f"https://auth.privy.io/api/v1/wallets/{wallet_id}/rpc"

        # Create authorization signature
        auth_signature = _create_authorization_signature(
            method="POST",
            url=url,
            body=request_body,
            app_id=self.app_id,
            authorization_key=self.authorization_key,
        )

        response = await self._http_client.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Basic {auth_header}",
                "privy-app-id": self.app_id,
                "privy-authorization-signature": auth_signature,
            },
            json=request_body,
        )

        if response.status_code != 200:
            raise Exception(
                f"Privy transaction failed: {response.status_code} {response.text}"
            )

        result = response.json()
        return result.get("data", {}).get("hash", result.get("hash"))

    async def create_user(
        self,
        create_embedded_wallet: bool = True,
    ) -> Dict[str, Any]:
        """Create a new Privy user with an embedded wallet.

        Args:
            create_embedded_wallet: Whether to create an embedded wallet for the user

        Returns:
            The created user data including wallet info
        """
        import base64

        credentials = f"{self.app_id}:{self.app_secret}"
        auth_header = base64.b64encode(credentials.encode()).decode()

        response = await self._http_client.post(
            "https://auth.privy.io/api/v1/users",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Basic {auth_header}",
                "privy-app-id": self.app_id,
            },
            json={
                "create_embedded_wallet": create_embedded_wallet,
            },
        )

        if response.status_code != 200:
            raise Exception(
                f"Privy user creation failed: {response.status_code} {response.text}"
            )

        return response.json()

    async def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get a Privy user by ID.

        Args:
            user_id: Privy user ID

        Returns:
            The user data
        """
        import base64

        credentials = f"{self.app_id}:{self.app_secret}"
        auth_header = base64.b64encode(credentials.encode()).decode()

        response = await self._http_client.get(
            f"https://auth.privy.io/api/v1/users/{user_id}",
            headers={
                "Authorization": f"Basic {auth_header}",
                "privy-app-id": self.app_id,
            },
        )

        if response.status_code != 200:
            raise Exception(
                f"Privy get user failed: {response.status_code} {response.text}"
            )

        return response.json()

    async def close(self):
        """Close the HTTP client."""
        await self._http_client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


def create_privy_client(config: PrivyRouterConfig) -> PrivyClient:
    """Creates a Privy client instance for server-side operations.

    Args:
        config: Privy configuration containing app_id, app_secret, authorization_key

    Returns:
        Configured PrivyClient instance

    Example:
        ```python
        privy = create_privy_client({
            "app_id": os.environ["PRIVY_APP_ID"],
            "app_secret": os.environ["PRIVY_APP_SECRET"],
            "authorization_key": os.environ["PRIVY_AUTHORIZATION_KEY"],
        })
        ```
    """
    return PrivyClient(
        app_id=config["app_id"],
        app_secret=config["app_secret"],
        authorization_key=config["authorization_key"],
    )


class PrivySigner:
    """RouterSigner implementation using Privy for server-side signing."""

    def __init__(
        self,
        privy: PrivyClient,
        wallet_id: str,
        wallet_address: str,
    ):
        """Create a Privy signer.

        Args:
            privy: Configured PrivyClient instance
            wallet_id: Privy wallet ID
            wallet_address: Wallet address (0x...)
        """
        self.privy = privy
        self.wallet_id = wallet_id
        self.wallet_address = wallet_address

    async def get_address(self) -> str:
        """Get the wallet address."""
        return self.wallet_address

    async def sign_typed_data(self, payload: Eip712Payload) -> str:
        """Sign EIP-712 typed data.

        Args:
            payload: EIP-712 payload to sign

        Returns:
            The signature as a hex string
        """
        return await self.privy.sign_typed_data(
            self.wallet_id,
            {
                "domain": payload["domain"],
                "types": payload["types"],
                "primaryType": payload["primaryType"],
                "message": payload["message"],
            },
        )


def create_privy_signer(
    privy: PrivyClient,
    wallet_id: str,
    wallet_address: str,
) -> PrivySigner:
    """Creates a RouterSigner from a Privy wallet for Polymarket trading.

    This signer can be used with PolymarketRouter to sign orders server-side
    without requiring user interaction.

    Args:
        privy: Configured PrivyClient instance
        wallet_id: Privy wallet ID
        wallet_address: Wallet address (0x...)

    Returns:
        RouterSigner that can be used with PolymarketRouter

    Example:
        ```python
        privy = create_privy_client({...})
        signer = create_privy_signer(
            privy,
            "wallet-id-from-privy",
            "0x1234..."
        )

        # Use with PolymarketRouter
        await router.link_user({"user_id": "user-123", "signer": signer})
        ```
    """
    return PrivySigner(privy, wallet_id, wallet_address)


def create_privy_signer_from_env(
    wallet_id: str,
    wallet_address: str,
) -> PrivySigner:
    """All-in-one helper to create a Privy signer from environment variables.

    Expects the following environment variables:
    - PRIVY_APP_ID
    - PRIVY_APP_SECRET
    - PRIVY_AUTHORIZATION_KEY

    Args:
        wallet_id: Privy wallet ID
        wallet_address: Wallet address (0x...)

    Returns:
        RouterSigner ready to use

    Example:
        ```python
        # Simplest usage - just pass wallet info
        signer = create_privy_signer_from_env(
            user.privy_wallet_id,
            user.wallet_address
        )

        await router.place_order({
            "user_id": user.id,
            "market_id": "60487...",
            "side": "buy",
            "size": 10,
            "price": 0.65,
            "signer": signer,
        }, credentials)
        ```
    """
    app_id = os.environ.get("PRIVY_APP_ID")
    app_secret = os.environ.get("PRIVY_APP_SECRET")
    authorization_key = os.environ.get("PRIVY_AUTHORIZATION_KEY")

    if not app_id or not app_secret or not authorization_key:
        raise ValueError(
            "Missing Privy environment variables: PRIVY_APP_ID, PRIVY_APP_SECRET, PRIVY_AUTHORIZATION_KEY"
        )

    privy = PrivyClient(
        app_id=app_id,
        app_secret=app_secret,
        authorization_key=authorization_key,
    )
    return PrivySigner(privy, wallet_id, wallet_address)


async def check_privy_wallet_allowances(
    wallet_address: str,
    rpc_url: str = "https://polygon-rpc.com",
) -> AllowanceStatus:
    """Check if a wallet has all required Polymarket token allowances.

    Args:
        wallet_address: The wallet address to check
        rpc_url: Optional Polygon RPC URL (defaults to public RPC)

    Returns:
        AllowanceStatus with allowance status for each contract
    """
    from .allowances import check_all_allowances

    return await check_all_allowances(wallet_address, rpc_url)


async def set_privy_wallet_allowances(
    privy: PrivyClient,
    wallet_id: str,
    wallet_address: str,
    on_progress: Optional[Callable[[str, int, int], None]] = None,
    sponsor: bool = False,
) -> Dict[str, Dict[str, Optional[str]]]:
    """Set all required token allowances for Polymarket trading using Privy's sendTransaction.

    This uses Privy's walletApi to send approval transactions directly from server-side.
    This is the recommended method for Privy-managed wallets.

    Args:
        privy: Configured PrivyClient instance
        wallet_id: Privy wallet ID
        wallet_address: Wallet address (0x...)
        on_progress: Optional callback for progress updates (step, current, total)
        sponsor: Whether to use Privy gas sponsorship (default: False)

    Returns:
        Object with transaction hashes for each approval

    Example:
        ```python
        privy = create_privy_client({...})
        txs = await set_privy_wallet_allowances(
            privy,
            "wallet-id",
            "0x1234...",
            on_progress=lambda step, curr, total: print(f"[{curr}/{total}] {step}"),
            sponsor=True,  # Use Privy gas sponsorship
        )
        ```
    """
    # Check current allowances
    allowances = await check_privy_wallet_allowances(wallet_address)

    if allowances.all_set:
        return {"usdc": {}, "ctf": {}}

    # ERC20 approve function signature
    # approve(address spender, uint256 amount)
    # function selector: 0x095ea7b3
    max_uint256 = "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"

    # ERC1155 setApprovalForAll function signature
    # setApprovalForAll(address operator, bool approved)
    # function selector: 0xa22cb465

    def encode_erc20_approve(spender: str) -> str:
        """Encode ERC20 approve call data."""
        # Remove 0x prefix from spender and pad to 32 bytes
        spender_padded = spender[2:].lower().zfill(64)
        # max uint256 without 0x prefix
        amount_padded = max_uint256[2:]
        return f"0x095ea7b3{spender_padded}{amount_padded}"

    def encode_erc1155_set_approval(operator: str) -> str:
        """Encode ERC1155 setApprovalForAll call data."""
        # Remove 0x prefix from operator and pad to 32 bytes
        operator_padded = operator[2:].lower().zfill(64)
        # true = 1, padded to 32 bytes
        approved_padded = (
            "0000000000000000000000000000000000000000000000000000000000000001"
        )
        return f"0xa22cb465{operator_padded}{approved_padded}"

    tx_hashes: Dict[str, Dict[str, Optional[str]]] = {"usdc": {}, "ctf": {}}

    # Build list of needed approvals
    approvals: List[Dict[str, Any]] = []

    if not allowances.usdc_ctf_exchange:
        approvals.append(
            {
                "name": "USDC -> CTF Exchange",
                "token": POLYGON_ADDRESSES["USDC"],
                "spender": POLYGON_ADDRESSES["CTF_EXCHANGE"],
                "is_erc20": True,
                "key": "ctf_exchange",
                "type": "usdc",
            }
        )
    if not allowances.usdc_neg_risk_ctf_exchange:
        approvals.append(
            {
                "name": "USDC -> Neg Risk CTF Exchange",
                "token": POLYGON_ADDRESSES["USDC"],
                "spender": POLYGON_ADDRESSES["NEG_RISK_CTF_EXCHANGE"],
                "is_erc20": True,
                "key": "neg_risk_ctf_exchange",
                "type": "usdc",
            }
        )
    if not allowances.usdc_neg_risk_adapter:
        approvals.append(
            {
                "name": "USDC -> Neg Risk Adapter",
                "token": POLYGON_ADDRESSES["USDC"],
                "spender": POLYGON_ADDRESSES["NEG_RISK_ADAPTER"],
                "is_erc20": True,
                "key": "neg_risk_adapter",
                "type": "usdc",
            }
        )
    if not allowances.ctf_ctf_exchange:
        approvals.append(
            {
                "name": "CTF -> CTF Exchange",
                "token": POLYGON_ADDRESSES["CTF"],
                "spender": POLYGON_ADDRESSES["CTF_EXCHANGE"],
                "is_erc20": False,
                "key": "ctf_exchange",
                "type": "ctf",
            }
        )
    if not allowances.ctf_neg_risk_ctf_exchange:
        approvals.append(
            {
                "name": "CTF -> Neg Risk CTF Exchange",
                "token": POLYGON_ADDRESSES["CTF"],
                "spender": POLYGON_ADDRESSES["NEG_RISK_CTF_EXCHANGE"],
                "is_erc20": False,
                "key": "neg_risk_ctf_exchange",
                "type": "ctf",
            }
        )
    if not allowances.ctf_neg_risk_adapter:
        approvals.append(
            {
                "name": "CTF -> Neg Risk Adapter",
                "token": POLYGON_ADDRESSES["CTF"],
                "spender": POLYGON_ADDRESSES["NEG_RISK_ADAPTER"],
                "is_erc20": False,
                "key": "neg_risk_adapter",
                "type": "ctf",
            }
        )

    # Send each approval transaction
    for i, approval in enumerate(approvals):
        if on_progress:
            on_progress(approval["name"], i + 1, len(approvals))

        if approval["is_erc20"]:
            data = encode_erc20_approve(approval["spender"])
        else:
            data = encode_erc1155_set_approval(approval["spender"])

        tx_hash = await privy.send_transaction(
            wallet_id,
            {
                "to": approval["token"],
                "data": data,
                "chainId": 137,
            },
            chain_id=137,
            sponsor=sponsor,
        )

        tx_hashes[approval["type"]][approval["key"]] = tx_hash

    return tx_hashes


__all__ = [
    "PrivyClient",
    "PrivySigner",
    "RouterSigner",
    "create_privy_client",
    "create_privy_signer",
    "create_privy_signer_from_env",
    "check_privy_wallet_allowances",
    "set_privy_wallet_allowances",
    "POLYGON_ADDRESSES",
]

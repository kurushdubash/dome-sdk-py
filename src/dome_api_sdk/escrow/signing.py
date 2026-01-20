"""Fee Authorization Signing for Dome Fee Escrow.

Provides EIP-712 signing functions that work with various wallet types:
- eth_account.Account (direct signing)
- RouterSigner (Privy, MetaMask, etc.)
"""

import time
from typing import Any, Dict, Protocol, TypedDict

from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_utils import is_address, to_checksum_address

from .types import FeeAuthorization, SignedFeeAuthorization, FEE_AUTHORIZATION_TYPES


# Deadline bounds
MIN_DEADLINE_SECONDS = 60  # 1 minute
MAX_DEADLINE_SECONDS = 86400  # 24 hours


class EIP712Domain(TypedDict):
    """EIP-712 domain separator."""

    name: str
    version: str
    chainId: int
    verifyingContract: str


def create_eip712_domain(escrow_address: str, chain_id: int) -> EIP712Domain:
    """Create EIP-712 domain for the escrow contract.

    Args:
        escrow_address: Address of the escrow contract
        chain_id: Chain ID (137 for Polygon)

    Returns:
        EIP-712 domain dictionary

    Raises:
        ValueError: If escrow address is invalid
    """
    if not is_address(escrow_address):
        raise ValueError(f"Invalid escrow address: {escrow_address}")

    return {
        "name": "DomeFeeEscrow",
        "version": "1",
        "chainId": chain_id,
        "verifyingContract": to_checksum_address(escrow_address),
    }


def create_fee_authorization(
    order_id: str,
    payer: str,
    fee_amount: int,
    deadline_seconds: int = 3600,
) -> FeeAuthorization:
    """Create a fee authorization object.

    Args:
        order_id: Unique order ID (bytes32 hex string)
        payer: Address that will pay the fee
        fee_amount: Fee amount in USDC (6 decimals)
        deadline_seconds: Seconds from now until authorization expires (default: 1 hour)

    Returns:
        FeeAuthorization object

    Raises:
        ValueError: If payer address is invalid or deadline is out of bounds
    """
    if not is_address(payer):
        raise ValueError(f"Invalid payer address: {payer}")

    if deadline_seconds < MIN_DEADLINE_SECONDS:
        raise ValueError(
            f"Deadline too short: {deadline_seconds}s. Minimum: {MIN_DEADLINE_SECONDS}s"
        )
    if deadline_seconds > MAX_DEADLINE_SECONDS:
        raise ValueError(
            f"Deadline too long: {deadline_seconds}s. Maximum: {MAX_DEADLINE_SECONDS}s"
        )

    deadline = int(time.time()) + deadline_seconds

    return FeeAuthorization(
        order_id=order_id,
        payer=to_checksum_address(payer),
        fee_amount=fee_amount,
        deadline=deadline,
    )


def sign_fee_authorization(
    private_key: str,
    escrow_address: str,
    fee_auth: FeeAuthorization,
    chain_id: int = 137,
) -> SignedFeeAuthorization:
    """Sign a fee authorization with EIP-712 using a private key.

    Use this when you have direct access to a private key.

    Args:
        private_key: Private key (hex string with or without 0x prefix)
        escrow_address: Address of the escrow contract
        fee_auth: Fee authorization to sign
        chain_id: Chain ID (default: 137 for Polygon)

    Returns:
        SignedFeeAuthorization with signature
    """
    domain = create_eip712_domain(escrow_address, chain_id)

    # Build the typed data structure
    typed_data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            **FEE_AUTHORIZATION_TYPES,
        },
        "primaryType": "FeeAuthorization",
        "domain": domain,
        "message": {
            "orderId": fee_auth.order_id,
            "payer": fee_auth.payer,
            "feeAmount": fee_auth.fee_amount,
            "deadline": fee_auth.deadline,
        },
    }

    # Sign the typed data
    account = Account.from_key(private_key)
    signed_message = account.sign_typed_data(
        domain_data=domain,
        message_types=FEE_AUTHORIZATION_TYPES,
        message_data=typed_data["message"],
    )

    return SignedFeeAuthorization(
        order_id=fee_auth.order_id,
        payer=fee_auth.payer,
        fee_amount=fee_auth.fee_amount,
        deadline=fee_auth.deadline,
        signature=signed_message.signature.hex(),
    )


class TypedDataSigner(Protocol):
    """Protocol for signers that can sign EIP-712 typed data."""

    async def get_address(self) -> str:
        """Get the signer's address."""
        ...

    async def sign_typed_data(self, params: Dict[str, Any]) -> str:
        """Sign EIP-712 typed data.

        Args:
            params: Dict with domain, types, primaryType, and message

        Returns:
            Signature as hex string
        """
        ...


async def sign_fee_authorization_with_signer(
    signer: TypedDataSigner,
    escrow_address: str,
    fee_auth: FeeAuthorization,
    chain_id: int = 137,
) -> SignedFeeAuthorization:
    """Sign a fee authorization with EIP-712 using any compatible signer.

    Use this when working with RouterSigner (Privy, MetaMask, etc.)
    or any wallet that implements the TypedDataSigner protocol.

    Args:
        signer: Signer that implements TypedDataSigner protocol
        escrow_address: Address of the escrow contract
        fee_auth: Fee authorization to sign
        chain_id: Chain ID (default: 137 for Polygon)

    Returns:
        SignedFeeAuthorization with signature
    """
    domain = create_eip712_domain(escrow_address, chain_id)

    message = {
        "orderId": fee_auth.order_id,
        "payer": fee_auth.payer,
        "feeAmount": str(fee_auth.fee_amount),  # Convert to string for signing
        "deadline": str(fee_auth.deadline),  # Convert to string for signing
    }

    signature = await signer.sign_typed_data(
        {
            "domain": domain,
            "types": FEE_AUTHORIZATION_TYPES,
            "primaryType": "FeeAuthorization",
            "message": message,
        }
    )

    return SignedFeeAuthorization(
        order_id=fee_auth.order_id,
        payer=fee_auth.payer,
        fee_amount=fee_auth.fee_amount,
        deadline=fee_auth.deadline,
        signature=signature,
    )


def verify_fee_authorization_signature(
    signed_auth: SignedFeeAuthorization,
    escrow_address: str,
    chain_id: int,
    expected_signer: str,
) -> bool:
    """Verify a fee authorization signature locally (for EOA signatures).

    Note: This only works for EOA signatures. For SAFE signatures,
    verification must happen on-chain via EIP-1271.

    Args:
        signed_auth: Signed fee authorization
        escrow_address: Address of the escrow contract
        chain_id: Chain ID
        expected_signer: Expected signer address

    Returns:
        True if signature is valid and from expected signer
    """
    from eth_account.messages import encode_typed_data

    domain = create_eip712_domain(escrow_address, chain_id)

    typed_data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            **FEE_AUTHORIZATION_TYPES,
        },
        "primaryType": "FeeAuthorization",
        "domain": domain,
        "message": {
            "orderId": signed_auth.order_id,
            "payer": signed_auth.payer,
            "feeAmount": signed_auth.fee_amount,
            "deadline": signed_auth.deadline,
        },
    }

    try:
        # Recover the signer from the signature
        signable_message = encode_typed_data(full_message=typed_data)
        recovered = Account.recover_message(
            signable_message,
            signature=bytes.fromhex(
                signed_auth.signature[2:]
                if signed_auth.signature.startswith("0x")
                else signed_auth.signature
            ),
        )
        return recovered.lower() == expected_signer.lower()
    except Exception:
        return False

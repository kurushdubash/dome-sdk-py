"""DomeFeeEscrow Signing.

Provides EIP-712 signing functions for the DomeFeeEscrow contract that supports
both order fees and performance fees with independent dome and affiliate amounts.

Works with various wallet types:
- eth_account.Account (direct signing)
- RouterSigner (Privy, MetaMask, etc.)
"""

import time
from typing import Any, Dict, Protocol, TypedDict

from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_utils import is_address, to_checksum_address

from .dome_types import (
    OrderFeeAuthorization,
    SignedOrderFeeAuthorization,
    PerformanceFeeAuthorization,
    SignedPerformanceFeeAuthorization,
    ORDER_FEE_AUTHORIZATION_TYPES,
    PERFORMANCE_FEE_AUTHORIZATION_TYPES,
)


# Deadline bounds
MIN_DEADLINE_SECONDS = 60  # 1 minute
MAX_DEADLINE_SECONDS = 86400  # 24 hours

# Fee constraints (matching contract constants)
MIN_ORDER_FEE = 10_000  # $0.01 USDC (6 decimals)
MIN_PERF_FEE = 100_000  # $0.10 USDC (6 decimals)
MAX_FEE_ABSOLUTE = 10_000_000_000  # $10,000 USDC (6 decimals)
MAX_ORDER_FEE_BPS = 100  # 1%
MAX_PERF_FEE_BPS = 1000  # 10%


class EIP712Domain(TypedDict):
    """EIP-712 domain separator for DomeFeeEscrow."""

    name: str
    version: str
    chainId: int
    verifyingContract: str


def create_eip712_domain(escrow_address: str, chain_id: int) -> EIP712Domain:
    """Create EIP-712 domain for the DomeFeeEscrow contract.

    Args:
        escrow_address: Address of the DomeFeeEscrow contract
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


def create_order_fee_authorization(
    order_id: str,
    payer: str,
    dome_amount: int,
    affiliate_amount: int,
    chain_id: int = 137,
    deadline_seconds: int = 3600,
) -> OrderFeeAuthorization:
    """Create an order fee authorization object.

    Args:
        order_id: Unique order ID (bytes32 hex string)
        payer: Address that will pay the fee
        dome_amount: Dome's fee amount in USDC (6 decimals)
        affiliate_amount: Affiliate's fee amount in USDC (6 decimals)
        chain_id: Chain ID for replay protection (default: 137 for Polygon)
        deadline_seconds: Seconds from now until authorization expires (default: 1 hour)

    Returns:
        OrderFeeAuthorization object

    Raises:
        ValueError: If validation fails
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

    total_fee = dome_amount + affiliate_amount
    if total_fee == 0:
        raise ValueError("Total fee cannot be zero")
    if total_fee < MIN_ORDER_FEE:
        raise ValueError(
            f"Total fee too low: {total_fee}. Minimum: {MIN_ORDER_FEE} ($0.01 USDC)"
        )
    if total_fee > MAX_FEE_ABSOLUTE:
        raise ValueError(
            f"Total fee too high: {total_fee}. Maximum: {MAX_FEE_ABSOLUTE} ($10,000 USDC)"
        )

    deadline = int(time.time()) + deadline_seconds

    return OrderFeeAuthorization(
        order_id=order_id,
        payer=to_checksum_address(payer),
        dome_amount=dome_amount,
        affiliate_amount=affiliate_amount,
        chain_id=chain_id,
        deadline=deadline,
    )


def create_performance_fee_authorization(
    position_id: str,
    payer: str,
    expected_winnings: int,
    dome_amount: int,
    affiliate_amount: int,
    chain_id: int = 137,
    deadline_seconds: int = 3600,
) -> PerformanceFeeAuthorization:
    """Create a performance fee authorization object.

    Args:
        position_id: Position identifier (bytes32 hex string)
        payer: Address that will pay the fee
        expected_winnings: Expected winnings amount in USDC (6 decimals)
        dome_amount: Dome's fee amount in USDC (6 decimals)
        affiliate_amount: Affiliate's fee amount in USDC (6 decimals)
        chain_id: Chain ID for replay protection (default: 137 for Polygon)
        deadline_seconds: Seconds from now until authorization expires (default: 1 hour)

    Returns:
        PerformanceFeeAuthorization object

    Raises:
        ValueError: If validation fails
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

    total_fee = dome_amount + affiliate_amount
    if total_fee == 0:
        raise ValueError("Total fee cannot be zero")
    if total_fee < MIN_PERF_FEE:
        raise ValueError(
            f"Total fee too low: {total_fee}. Minimum: {MIN_PERF_FEE} ($0.10 USDC)"
        )
    if total_fee > MAX_FEE_ABSOLUTE:
        raise ValueError(
            f"Total fee too high: {total_fee}. Maximum: {MAX_FEE_ABSOLUTE} ($10,000 USDC)"
        )

    if expected_winnings <= 0:
        raise ValueError("Expected winnings must be positive")

    deadline = int(time.time()) + deadline_seconds

    return PerformanceFeeAuthorization(
        position_id=position_id,
        payer=to_checksum_address(payer),
        expected_winnings=expected_winnings,
        dome_amount=dome_amount,
        affiliate_amount=affiliate_amount,
        chain_id=chain_id,
        deadline=deadline,
    )


def sign_order_fee_authorization(
    private_key: str,
    escrow_address: str,
    auth: OrderFeeAuthorization,
) -> SignedOrderFeeAuthorization:
    """Sign an order fee authorization with EIP-712 using a private key.

    Use this when you have direct access to a private key.

    Args:
        private_key: Private key (hex string with or without 0x prefix)
        escrow_address: Address of the DomeFeeEscrow contract
        auth: Order fee authorization to sign

    Returns:
        SignedOrderFeeAuthorization with signature
    """
    domain = create_eip712_domain(escrow_address, auth.chain_id)

    # Build the typed data structure
    typed_data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            **ORDER_FEE_AUTHORIZATION_TYPES,
        },
        "primaryType": "OrderFeeAuthorization",
        "domain": domain,
        "message": {
            "orderId": auth.order_id,
            "payer": auth.payer,
            "domeAmount": auth.dome_amount,
            "affiliateAmount": auth.affiliate_amount,
            "chainId": auth.chain_id,
            "deadline": auth.deadline,
        },
    }

    # Sign the typed data
    account = Account.from_key(private_key)
    signed_message = account.sign_typed_data(
        domain_data=domain,
        message_types=ORDER_FEE_AUTHORIZATION_TYPES,
        message_data=typed_data["message"],
    )

    return SignedOrderFeeAuthorization(
        order_id=auth.order_id,
        payer=auth.payer,
        dome_amount=auth.dome_amount,
        affiliate_amount=auth.affiliate_amount,
        chain_id=auth.chain_id,
        deadline=auth.deadline,
        signature=signed_message.signature.hex(),
    )


def sign_performance_fee_authorization(
    private_key: str,
    escrow_address: str,
    auth: PerformanceFeeAuthorization,
) -> SignedPerformanceFeeAuthorization:
    """Sign a performance fee authorization with EIP-712 using a private key.

    Use this when you have direct access to a private key.

    Args:
        private_key: Private key (hex string with or without 0x prefix)
        escrow_address: Address of the DomeFeeEscrow contract
        auth: Performance fee authorization to sign

    Returns:
        SignedPerformanceFeeAuthorization with signature
    """
    domain = create_eip712_domain(escrow_address, auth.chain_id)

    # Build the typed data structure
    typed_data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            **PERFORMANCE_FEE_AUTHORIZATION_TYPES,
        },
        "primaryType": "PerformanceFeeAuthorization",
        "domain": domain,
        "message": {
            "positionId": auth.position_id,
            "payer": auth.payer,
            "expectedWinnings": auth.expected_winnings,
            "domeAmount": auth.dome_amount,
            "affiliateAmount": auth.affiliate_amount,
            "chainId": auth.chain_id,
            "deadline": auth.deadline,
        },
    }

    # Sign the typed data
    account = Account.from_key(private_key)
    signed_message = account.sign_typed_data(
        domain_data=domain,
        message_types=PERFORMANCE_FEE_AUTHORIZATION_TYPES,
        message_data=typed_data["message"],
    )

    return SignedPerformanceFeeAuthorization(
        position_id=auth.position_id,
        payer=auth.payer,
        expected_winnings=auth.expected_winnings,
        dome_amount=auth.dome_amount,
        affiliate_amount=auth.affiliate_amount,
        chain_id=auth.chain_id,
        deadline=auth.deadline,
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


async def sign_order_fee_authorization_with_signer(
    signer: TypedDataSigner,
    escrow_address: str,
    auth: OrderFeeAuthorization,
) -> SignedOrderFeeAuthorization:
    """Sign an order fee authorization with EIP-712 using any compatible signer.

    Use this when working with RouterSigner (Privy, MetaMask, etc.)
    or any wallet that implements the TypedDataSigner protocol.

    Args:
        signer: Signer that implements TypedDataSigner protocol
        escrow_address: Address of the DomeFeeEscrow contract
        auth: Order fee authorization to sign

    Returns:
        SignedOrderFeeAuthorization with signature
    """
    domain = create_eip712_domain(escrow_address, auth.chain_id)

    message = {
        "orderId": auth.order_id,
        "payer": auth.payer,
        "domeAmount": str(auth.dome_amount),
        "affiliateAmount": str(auth.affiliate_amount),
        "chainId": str(auth.chain_id),
        "deadline": str(auth.deadline),
    }

    signature = await signer.sign_typed_data(
        {
            "domain": domain,
            "types": ORDER_FEE_AUTHORIZATION_TYPES,
            "primaryType": "OrderFeeAuthorization",
            "message": message,
        }
    )

    return SignedOrderFeeAuthorization(
        order_id=auth.order_id,
        payer=auth.payer,
        dome_amount=auth.dome_amount,
        affiliate_amount=auth.affiliate_amount,
        chain_id=auth.chain_id,
        deadline=auth.deadline,
        signature=signature,
    )


async def sign_performance_fee_authorization_with_signer(
    signer: TypedDataSigner,
    escrow_address: str,
    auth: PerformanceFeeAuthorization,
) -> SignedPerformanceFeeAuthorization:
    """Sign a performance fee authorization with EIP-712 using any compatible signer.

    Use this when working with RouterSigner (Privy, MetaMask, etc.)
    or any wallet that implements the TypedDataSigner protocol.

    Args:
        signer: Signer that implements TypedDataSigner protocol
        escrow_address: Address of the DomeFeeEscrow contract
        auth: Performance fee authorization to sign

    Returns:
        SignedPerformanceFeeAuthorization with signature
    """
    domain = create_eip712_domain(escrow_address, auth.chain_id)

    message = {
        "positionId": auth.position_id,
        "payer": auth.payer,
        "expectedWinnings": str(auth.expected_winnings),
        "domeAmount": str(auth.dome_amount),
        "affiliateAmount": str(auth.affiliate_amount),
        "chainId": str(auth.chain_id),
        "deadline": str(auth.deadline),
    }

    signature = await signer.sign_typed_data(
        {
            "domain": domain,
            "types": PERFORMANCE_FEE_AUTHORIZATION_TYPES,
            "primaryType": "PerformanceFeeAuthorization",
            "message": message,
        }
    )

    return SignedPerformanceFeeAuthorization(
        position_id=auth.position_id,
        payer=auth.payer,
        expected_winnings=auth.expected_winnings,
        dome_amount=auth.dome_amount,
        affiliate_amount=auth.affiliate_amount,
        chain_id=auth.chain_id,
        deadline=auth.deadline,
        signature=signature,
    )


def verify_order_fee_authorization_signature(
    signed_auth: SignedOrderFeeAuthorization,
    escrow_address: str,
    expected_signer: str,
) -> bool:
    """Verify an order fee authorization signature locally (for EOA signatures).

    Note: This only works for EOA signatures. For SAFE signatures,
    verification must happen on-chain via EIP-1271.

    Args:
        signed_auth: Signed order fee authorization
        escrow_address: Address of the DomeFeeEscrow contract
        expected_signer: Expected signer address

    Returns:
        True if signature is valid and from expected signer
    """
    domain = create_eip712_domain(escrow_address, signed_auth.chain_id)

    typed_data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            **ORDER_FEE_AUTHORIZATION_TYPES,
        },
        "primaryType": "OrderFeeAuthorization",
        "domain": domain,
        "message": {
            "orderId": signed_auth.order_id,
            "payer": signed_auth.payer,
            "domeAmount": signed_auth.dome_amount,
            "affiliateAmount": signed_auth.affiliate_amount,
            "chainId": signed_auth.chain_id,
            "deadline": signed_auth.deadline,
        },
    }

    try:
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


def verify_performance_fee_authorization_signature(
    signed_auth: SignedPerformanceFeeAuthorization,
    escrow_address: str,
    expected_signer: str,
) -> bool:
    """Verify a performance fee authorization signature locally (for EOA signatures).

    Note: This only works for EOA signatures. For SAFE signatures,
    verification must happen on-chain via EIP-1271.

    Args:
        signed_auth: Signed performance fee authorization
        escrow_address: Address of the DomeFeeEscrow contract
        expected_signer: Expected signer address

    Returns:
        True if signature is valid and from expected signer
    """
    domain = create_eip712_domain(escrow_address, signed_auth.chain_id)

    typed_data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            **PERFORMANCE_FEE_AUTHORIZATION_TYPES,
        },
        "primaryType": "PerformanceFeeAuthorization",
        "domain": domain,
        "message": {
            "positionId": signed_auth.position_id,
            "payer": signed_auth.payer,
            "expectedWinnings": signed_auth.expected_winnings,
            "domeAmount": signed_auth.dome_amount,
            "affiliateAmount": signed_auth.affiliate_amount,
            "chainId": signed_auth.chain_id,
            "deadline": signed_auth.deadline,
        },
    }

    try:
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

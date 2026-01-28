"""Order ID Generation for Dome Fee Escrow.

Generates unique, deterministic order IDs that provide:
- Cross-chain replay protection (via chain_id)
- Cross-user collision prevention (via user_address)
- Same-user collision prevention (via millisecond timestamp)
"""

from eth_abi import encode
from eth_utils import keccak, is_address, to_checksum_address

from .types import OrderParams


def generate_order_id(params: OrderParams) -> str:
    """Generate a unique orderId using deterministic hash.

    Args:
        params: Order parameters (timestamp should be in milliseconds)

    Returns:
        bytes32 hex string order ID

    Raises:
        ValueError: If price is outside valid range [0, 1] or address is invalid
    """
    # Validate price range for binary markets
    if params.price < 0 or params.price > 1:
        raise ValueError(f"Invalid price: {params.price}. Must be between 0 and 1")

    # Validate user address
    if not is_address(params.user_address):
        raise ValueError(f"Invalid user_address: {params.user_address}")

    # Normalize address to checksum
    checksum_address = to_checksum_address(params.user_address)

    # Encode parameters matching TypeScript implementation
    # Types: uint256, address, string, string, uint256, uint256, uint256
    encoded = encode(
        ["uint256", "address", "string", "string", "uint256", "uint256", "uint256"],
        [
            params.chain_id,  # Chain ID first for cross-chain replay protection
            checksum_address,  # Normalized to checksum
            params.market_id,
            params.side,
            params.size,  # Already in USDC decimals
            round(params.price * 10000),  # Price as basis points
            params.timestamp,  # Milliseconds
        ],
    )

    # Return keccak256 hash as hex string
    return "0x" + keccak(encoded).hex()


def verify_order_id(order_id: str, params: OrderParams) -> bool:
    """Verify an orderId matches the given parameters.

    Args:
        order_id: The order ID to verify
        params: Order parameters to check against

    Returns:
        True if the order ID matches, False otherwise
    """
    try:
        reconstructed = generate_order_id(params)
        return reconstructed.lower() == order_id.lower()
    except Exception:
        return False

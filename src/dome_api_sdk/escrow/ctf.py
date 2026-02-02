"""CTF (Conditional Token Framework) transaction builder utilities.

Provides helpers for building redeemPositions() calldata so EOA users
can sign the transaction offline before submitting to the Dome proxy.

Python SDK users handle their own transaction signing (via web3.py or
eth_account), so this module only provides calldata encoding — not signing.
"""

from eth_abi import encode

# CTF contract address (Polygon mainnet)
CTF_CONTRACT_ADDRESS = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"

# USDC on Polygon (collateral token for redeemPositions)
_USDC_POLYGON = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

# parentCollectionId is always bytes32(0) for top-level conditions
_PARENT_COLLECTION_ID = b"\x00" * 32

# Function selector for redeemPositions(address,bytes32,bytes32,uint256[])
# keccak256("redeemPositions(address,bytes32,bytes32,uint256[])") => first 4 bytes
_REDEEM_POSITIONS_SELECTOR = bytes.fromhex("6a338026")


def build_redeem_positions_calldata(condition_id: str, outcome_index: int) -> str:
    """Encode redeemPositions calldata for the CTF contract.

    For a binary market, outcome_index 0 maps to indexSets=[1] and
    outcome_index 1 maps to indexSets=[2] (i.e. 1 << outcome_index).

    Args:
        condition_id: bytes32 condition ID hex string (with or without 0x prefix)
        outcome_index: Winning outcome index (0 or 1)

    Returns:
        Hex-encoded calldata string with 0x prefix
    """
    if outcome_index < 0:
        raise ValueError(f"outcome_index must be non-negative, got {outcome_index}")

    # Normalize condition_id
    cid = condition_id
    if cid.startswith("0x") or cid.startswith("0X"):
        cid = cid[2:]
    if len(cid) != 64:
        raise ValueError(
            f"condition_id must be 32 bytes (64 hex chars), got {len(cid)}"
        )
    condition_id_bytes = bytes.fromhex(cid)

    # indexSets: for a binary market, outcome 0 -> [1], outcome 1 -> [2]
    index_sets = [1 << outcome_index]

    # ABI encode the parameters
    encoded_params = encode(
        ["address", "bytes32", "bytes32", "uint256[]"],
        [
            _USDC_POLYGON,
            _PARENT_COLLECTION_ID,
            condition_id_bytes,
            index_sets,
        ],
    )

    return "0x" + _REDEEM_POSITIONS_SELECTOR.hex() + encoded_params.hex()


def build_redeem_positions_tx(condition_id: str, outcome_index: int) -> dict:
    """Build an unsigned transaction dict for redeemPositions.

    Returns a dict with ``to``, ``data``, and ``value`` fields suitable for
    use with web3.py or eth_account for offline signing.

    Args:
        condition_id: bytes32 condition ID hex string (with or without 0x prefix)
        outcome_index: Winning outcome index (0 or 1)

    Returns:
        Dict with keys: ``to`` (CTF contract address), ``data`` (hex calldata),
        ``value`` (always 0)
    """
    return {
        "to": CTF_CONTRACT_ADDRESS,
        "data": build_redeem_positions_calldata(condition_id, outcome_index),
        "value": 0,
    }

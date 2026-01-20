"""Token Allowance Utilities for Polymarket Trading.

Polymarket requires two types of token approvals for trading:
1. USDC token allowance - allows exchange contracts to move USDC
2. Conditional Token Framework (CTF) approval - allows trading outcome tokens

These approvals only need to be set ONCE per wallet. After that, the wallet
can trade freely without additional approval transactions.

See: https://github.com/Polymarket/py-clob-client?tab=readme-ov-file#important-token-allowances-for-metamaskeoa-users
"""

from typing import Any, Callable, Dict, List, Optional

import httpx

from ..types import AllowanceStatus

# Polygon Mainnet Contract Addresses
POLYGON_ADDRESSES = {
    # USDC token contract (bridged USDC from Ethereum)
    "USDC": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
    # Conditional Token Framework (CTF) - for outcome tokens
    "CTF": "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045",
    # Exchange contracts that need approvals
    "CTF_EXCHANGE": "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E",
    "NEG_RISK_CTF_EXCHANGE": "0xC5d563A36AE78145C45a50134d48A1215220f80a",
    "NEG_RISK_ADAPTER": "0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296",
}

# Default RPC URL for Polygon
DEFAULT_RPC_URL = "https://polygon-rpc.com"

# Chain ID for Polygon mainnet
POLYGON_CHAIN_ID = 137


def get_polygon_provider(rpc_url: str = DEFAULT_RPC_URL) -> httpx.AsyncClient:
    """Get an HTTP client configured for Polygon RPC calls.

    Args:
        rpc_url: Optional custom RPC URL. Defaults to Polygon public RPC.

    Returns:
        Async HTTP client for JSON-RPC calls
    """
    return httpx.AsyncClient(
        base_url=rpc_url,
        timeout=30.0,
        headers={"Content-Type": "application/json"},
    )


async def _eth_call(
    client: httpx.AsyncClient,
    to: str,
    data: str,
    rpc_url: str = DEFAULT_RPC_URL,
) -> str:
    """Make an eth_call to the blockchain.

    Args:
        client: HTTP client
        to: Contract address
        data: Encoded call data
        rpc_url: RPC URL

    Returns:
        The result of the call (hex string)
    """
    response = await client.post(
        rpc_url,
        json={
            "jsonrpc": "2.0",
            "method": "eth_call",
            "params": [
                {"to": to, "data": data},
                "latest",
            ],
            "id": 1,
        },
    )

    if response.status_code != 200:
        raise Exception(f"RPC call failed: {response.status_code} {response.text}")

    result = response.json()
    if "error" in result:
        raise Exception(f"RPC error: {result['error']}")

    return result.get("result", "0x")


def _encode_allowance_call(owner: str, spender: str) -> str:
    """Encode an ERC20 allowance call.

    allowance(address owner, address spender) -> uint256
    function selector: 0xdd62ed3e
    """
    owner_padded = owner[2:].lower().zfill(64)
    spender_padded = spender[2:].lower().zfill(64)
    return f"0xdd62ed3e{owner_padded}{spender_padded}"


def _encode_is_approved_for_all_call(owner: str, operator: str) -> str:
    """Encode an ERC1155 isApprovedForAll call.

    isApprovedForAll(address owner, address operator) -> bool
    function selector: 0xe985e9c5
    """
    owner_padded = owner[2:].lower().zfill(64)
    operator_padded = operator[2:].lower().zfill(64)
    return f"0xe985e9c5{owner_padded}{operator_padded}"


async def check_usdc_allowance(
    wallet_address: str,
    spender: str,
    rpc_url: str = DEFAULT_RPC_URL,
) -> bool:
    """Check if USDC allowance is set for a specific spender.

    Args:
        wallet_address: The wallet address to check
        spender: The spender address
        rpc_url: RPC URL

    Returns:
        True if allowance is greater than zero
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        data = _encode_allowance_call(wallet_address, spender)
        result = await _eth_call(client, POLYGON_ADDRESSES["USDC"], data, rpc_url)

        # Result is a uint256 - check if it's greater than 0
        if result == "0x" or result == "0x0":
            return False

        # Parse hex result
        try:
            allowance = int(result, 16)
            return allowance > 0
        except ValueError:
            return False


async def check_ctf_approval(
    wallet_address: str,
    operator: str,
    rpc_url: str = DEFAULT_RPC_URL,
) -> bool:
    """Check if CTF (ERC1155) approval is set for a specific operator.

    Args:
        wallet_address: The wallet address to check
        operator: The operator address
        rpc_url: RPC URL

    Returns:
        True if approval is set
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        data = _encode_is_approved_for_all_call(wallet_address, operator)
        result = await _eth_call(client, POLYGON_ADDRESSES["CTF"], data, rpc_url)

        # Result is a bool - 0x01 = true, 0x00 = false
        if result == "0x" or result == "0x0":
            return False

        try:
            # Bool is returned as uint256 (32 bytes)
            value = int(result, 16)
            return value > 0
        except ValueError:
            return False


async def check_all_allowances(
    wallet_address: str,
    rpc_url: str = DEFAULT_RPC_URL,
) -> AllowanceStatus:
    """Check all required allowances for Polymarket trading.

    Args:
        wallet_address: The wallet address to check
        rpc_url: RPC URL

    Returns:
        AllowanceStatus with status for each required allowance
    """
    import asyncio

    # Check all allowances in parallel
    results = await asyncio.gather(
        check_usdc_allowance(
            wallet_address, POLYGON_ADDRESSES["CTF_EXCHANGE"], rpc_url
        ),
        check_usdc_allowance(
            wallet_address, POLYGON_ADDRESSES["NEG_RISK_CTF_EXCHANGE"], rpc_url
        ),
        check_usdc_allowance(
            wallet_address, POLYGON_ADDRESSES["NEG_RISK_ADAPTER"], rpc_url
        ),
        check_ctf_approval(wallet_address, POLYGON_ADDRESSES["CTF_EXCHANGE"], rpc_url),
        check_ctf_approval(
            wallet_address, POLYGON_ADDRESSES["NEG_RISK_CTF_EXCHANGE"], rpc_url
        ),
        check_ctf_approval(
            wallet_address, POLYGON_ADDRESSES["NEG_RISK_ADAPTER"], rpc_url
        ),
    )

    (
        usdc_ctf_exchange,
        usdc_neg_risk_ctf_exchange,
        usdc_neg_risk_adapter,
        ctf_ctf_exchange,
        ctf_neg_risk_ctf_exchange,
        ctf_neg_risk_adapter,
    ) = results

    all_set = all(
        [
            usdc_ctf_exchange,
            usdc_neg_risk_ctf_exchange,
            usdc_neg_risk_adapter,
            ctf_ctf_exchange,
            ctf_neg_risk_ctf_exchange,
            ctf_neg_risk_adapter,
        ]
    )

    return AllowanceStatus(
        all_set=all_set,
        usdc_ctf_exchange=usdc_ctf_exchange,
        usdc_neg_risk_ctf_exchange=usdc_neg_risk_ctf_exchange,
        usdc_neg_risk_adapter=usdc_neg_risk_adapter,
        ctf_ctf_exchange=ctf_ctf_exchange,
        ctf_neg_risk_ctf_exchange=ctf_neg_risk_ctf_exchange,
        ctf_neg_risk_adapter=ctf_neg_risk_adapter,
    )


async def set_all_allowances(
    signer: Any,  # RouterSigner
    rpc_url: str = DEFAULT_RPC_URL,
    on_progress: Optional[Callable[[str, int, int], None]] = None,
) -> Dict[str, Dict[str, Optional[str]]]:
    """Set all required token allowances for Polymarket trading.

    This will:
    1. Approve USDC for all 3 exchange contracts
    2. Approve CTF tokens for all 3 exchange contracts

    Each approval requires a separate transaction, so this may take some time.
    Only sets approvals that are not already set.

    Note: This function requires the signer to have transaction sending capabilities
    beyond just signing. For most use cases, you'll want to use set_privy_wallet_allowances
    from the privy module instead.

    Args:
        signer: RouterSigner implementation (must support sending transactions)
        rpc_url: Polygon RPC URL
        on_progress: Optional callback for progress updates (step, current, total)

    Returns:
        Object with transaction hashes for each approval
    """
    wallet_address = await signer.get_address()

    # Check which allowances are already set
    allowances = await check_all_allowances(wallet_address, rpc_url)

    tx_hashes: Dict[str, Dict[str, Optional[str]]] = {"usdc": {}, "ctf": {}}

    # If signer doesn't have send_transaction, we can't set allowances
    if not hasattr(signer, "send_transaction"):
        raise NotImplementedError(
            "This signer doesn't support sending transactions. "
            "Use set_privy_wallet_allowances for Privy wallets."
        )

    # ERC20 approve function signature
    max_uint256 = "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"

    def encode_erc20_approve(spender: str) -> str:
        spender_padded = spender[2:].lower().zfill(64)
        amount_padded = max_uint256[2:]
        return f"0x095ea7b3{spender_padded}{amount_padded}"

    def encode_erc1155_set_approval(operator: str) -> str:
        operator_padded = operator[2:].lower().zfill(64)
        approved_padded = (
            "0000000000000000000000000000000000000000000000000000000000000001"
        )
        return f"0xa22cb465{operator_padded}{approved_padded}"

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

        tx_hash = await signer.send_transaction(
            {
                "to": approval["token"],
                "data": data,
                "chainId": POLYGON_CHAIN_ID,
            }
        )

        tx_hashes[approval["type"]][approval["key"]] = tx_hash

    return tx_hashes


__all__ = [
    "POLYGON_ADDRESSES",
    "POLYGON_CHAIN_ID",
    "DEFAULT_RPC_URL",
    "get_polygon_provider",
    "check_usdc_allowance",
    "check_ctf_approval",
    "check_all_allowances",
    "set_all_allowances",
]

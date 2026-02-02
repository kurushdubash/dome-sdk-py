"""Tests for Claim Winnings support.

Tests CTF calldata encoding, ClaimWinningsResult dataclass,
and the router claim_winnings() method (with mocked HTTP).
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.dome_api_sdk.escrow.ctf import (
    CTF_CONTRACT_ADDRESS,
    build_redeem_positions_calldata,
    build_redeem_positions_tx,
)
from src.dome_api_sdk.escrow.dome_types import ClaimWinningsResult


# =============================================================================
# CTF Utilities
# =============================================================================


class TestBuildRedeemPositionsCalldata:
    """Tests for build_redeem_positions_calldata()."""

    def test_basic_encoding_outcome_0(self):
        """Test calldata encoding for outcome index 0."""
        condition_id = "0x" + "ab" * 32
        calldata = build_redeem_positions_calldata(condition_id, outcome_index=0)

        # Should be a hex string starting with 0x
        assert calldata.startswith("0x")
        # Should start with the redeemPositions function selector
        assert calldata[2:10] == "6a338026"
        # Should be long enough: 4 bytes selector + at least 5 ABI slots (160 bytes)
        assert len(calldata) > 2 + 8 + 320  # 0x + selector + encoded data

    def test_basic_encoding_outcome_1(self):
        """Test calldata encoding for outcome index 1."""
        condition_id = "0x" + "cd" * 32
        calldata = build_redeem_positions_calldata(condition_id, outcome_index=1)

        assert calldata.startswith("0x")
        assert calldata[2:10] == "6a338026"

    def test_different_outcomes_produce_different_calldata(self):
        """Outcome 0 and 1 should produce different calldata (different indexSets)."""
        condition_id = "0x" + "ab" * 32
        calldata_0 = build_redeem_positions_calldata(condition_id, outcome_index=0)
        calldata_1 = build_redeem_positions_calldata(condition_id, outcome_index=1)

        assert calldata_0 != calldata_1

    def test_condition_id_without_prefix(self):
        """Should accept condition_id without 0x prefix."""
        cid = "ab" * 32
        calldata = build_redeem_positions_calldata(cid, outcome_index=0)

        assert calldata.startswith("0x")
        assert calldata[2:10] == "6a338026"

    def test_condition_id_with_0X_prefix(self):
        """Should accept condition_id with 0X prefix."""
        cid = "0X" + "ab" * 32
        calldata = build_redeem_positions_calldata(cid, outcome_index=0)

        assert calldata.startswith("0x")

    def test_invalid_condition_id_length(self):
        """Should raise ValueError for wrong-length condition ID."""
        with pytest.raises(ValueError, match="32 bytes"):
            build_redeem_positions_calldata("0xabcd", outcome_index=0)

    def test_negative_outcome_index(self):
        """Should raise ValueError for negative outcome index."""
        condition_id = "0x" + "ab" * 32
        with pytest.raises(ValueError, match="non-negative"):
            build_redeem_positions_calldata(condition_id, outcome_index=-1)

    def test_same_condition_id_produces_same_calldata(self):
        """Deterministic: same inputs -> same output."""
        condition_id = "0x" + "ff" * 32
        calldata_a = build_redeem_positions_calldata(condition_id, outcome_index=1)
        calldata_b = build_redeem_positions_calldata(condition_id, outcome_index=1)

        assert calldata_a == calldata_b


class TestBuildRedeemPositionsTx:
    """Tests for build_redeem_positions_tx()."""

    def test_returns_correct_structure(self):
        """Should return dict with to, data, value keys."""
        condition_id = "0x" + "ab" * 32
        tx = build_redeem_positions_tx(condition_id, outcome_index=0)

        assert "to" in tx
        assert "data" in tx
        assert "value" in tx

    def test_to_is_ctf_address(self):
        """The 'to' field should be the CTF contract address."""
        condition_id = "0x" + "ab" * 32
        tx = build_redeem_positions_tx(condition_id, outcome_index=0)

        assert tx["to"] == CTF_CONTRACT_ADDRESS

    def test_value_is_zero(self):
        """The 'value' field should be 0 (no ETH/MATIC sent)."""
        condition_id = "0x" + "ab" * 32
        tx = build_redeem_positions_tx(condition_id, outcome_index=0)

        assert tx["value"] == 0

    def test_data_matches_calldata(self):
        """The 'data' field should match build_redeem_positions_calldata output."""
        condition_id = "0x" + "ab" * 32
        outcome = 1
        tx = build_redeem_positions_tx(condition_id, outcome)
        calldata = build_redeem_positions_calldata(condition_id, outcome)

        assert tx["data"] == calldata

    def test_ctf_contract_address_is_checksum(self):
        """CTF_CONTRACT_ADDRESS should be a valid checksum address."""
        assert CTF_CONTRACT_ADDRESS == "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"


# =============================================================================
# ClaimWinningsResult
# =============================================================================


class TestClaimWinningsResult:
    """Tests for ClaimWinningsResult dataclass."""

    def test_basic_construction(self):
        """Test creating a result with required fields."""
        result = ClaimWinningsResult(
            success=True,
            position_id="0x" + "ab" * 32,
            wallet_type="eoa",
            status="completed",
        )

        assert result.success is True
        assert result.position_id == "0x" + "ab" * 32
        assert result.wallet_type == "eoa"
        assert result.status == "completed"

    def test_optional_fields_default_to_none(self):
        """Optional fields should default to None."""
        result = ClaimWinningsResult(
            success=True,
            position_id="0x" + "ab" * 32,
            wallet_type="eoa",
            status="completed",
        )

        assert result.fee_pulled is None
        assert result.dome_amount is None
        assert result.affiliate_amount is None
        assert result.pull_fee_tx_hash is None
        assert result.distribute_tx_hash is None
        assert result.redeemed is None
        assert result.claim_tx_hash is None

    def test_full_construction(self):
        """Test creating a result with all fields."""
        result = ClaimWinningsResult(
            success=True,
            position_id="0xabc123",
            wallet_type="privy",
            status="completed",
            fee_pulled=True,
            dome_amount="2500000",
            affiliate_amount="500000",
            pull_fee_tx_hash="0xtx1",
            distribute_tx_hash="0xtx2",
            redeemed=True,
            claim_tx_hash="0xtx3",
        )

        assert result.success is True
        assert result.wallet_type == "privy"
        assert result.fee_pulled is True
        assert result.dome_amount == "2500000"
        assert result.affiliate_amount == "500000"
        assert result.pull_fee_tx_hash == "0xtx1"
        assert result.distribute_tx_hash == "0xtx2"
        assert result.redeemed is True
        assert result.claim_tx_hash == "0xtx3"

    def test_failed_status(self):
        """Test creating a result with failed status."""
        result = ClaimWinningsResult(
            success=False,
            position_id="0xabc",
            wallet_type="eoa",
            status="failed",
        )

        assert result.success is False
        assert result.status == "failed"


# =============================================================================
# Router claim_winnings()
# =============================================================================


class TestClaimWinningsRouter:
    """Tests for PolymarketRouter.claim_winnings() request validation."""

    def _make_router(self):
        """Create a router with a mocked HTTP client."""
        from src.dome_api_sdk.router.polymarket import PolymarketRouter

        router = PolymarketRouter({
            "api_key": "test-api-key",
        })
        return router

    def _make_valid_params(self, wallet_type="eoa"):
        """Create valid claim winnings params."""
        base = {
            "position_id": "0x" + "ab" * 32,
            "wallet_type": wallet_type,
            "payer_address": "0x" + "11" * 20,
            "signer_address": "0x" + "11" * 20,
            "performance_fee_auth": {
                "positionId": "0x" + "ab" * 32,
                "payer": "0x" + "11" * 20,
                "expectedWinnings": "100000000",
                "domeAmount": "2500000",
                "affiliateAmount": "500000",
                "chainId": 137,
                "deadline": 1700000000,
                "signature": "0x" + "ff" * 65,
            },
        }
        if wallet_type == "eoa":
            base["signed_redeem_tx"] = "0x" + "ee" * 100
        elif wallet_type == "privy":
            base["privy_wallet_id"] = "wallet-123"
            base["condition_id"] = "0x" + "ab" * 32
            base["outcome_index"] = 1
        return base

    @pytest.mark.asyncio
    async def test_missing_api_key(self):
        """Should raise ValueError when api_key is not set."""
        from src.dome_api_sdk.router.polymarket import PolymarketRouter

        router = PolymarketRouter({})
        params = self._make_valid_params()

        with pytest.raises(ValueError, match="Dome API key required"):
            await router.claim_winnings(params)

    @pytest.mark.asyncio
    async def test_missing_position_id(self):
        """Should raise ValueError when position_id is missing."""
        router = self._make_router()
        params = self._make_valid_params()
        del params["position_id"]

        with pytest.raises(ValueError, match="position_id"):
            await router.claim_winnings(params)

    @pytest.mark.asyncio
    async def test_missing_wallet_type(self):
        """Should raise ValueError when wallet_type is missing."""
        router = self._make_router()
        params = self._make_valid_params()
        del params["wallet_type"]

        with pytest.raises(ValueError, match="wallet_type"):
            await router.claim_winnings(params)

    @pytest.mark.asyncio
    async def test_invalid_wallet_type(self):
        """Should raise ValueError for invalid wallet_type."""
        router = self._make_router()
        params = self._make_valid_params()
        params["wallet_type"] = "metamask"

        with pytest.raises(ValueError, match="'eoa' or 'privy'"):
            await router.claim_winnings(params)

    @pytest.mark.asyncio
    async def test_missing_performance_fee_auth(self):
        """Should raise ValueError when performance_fee_auth is missing."""
        router = self._make_router()
        params = self._make_valid_params()
        del params["performance_fee_auth"]

        with pytest.raises(ValueError, match="performance_fee_auth"):
            await router.claim_winnings(params)

    @pytest.mark.asyncio
    async def test_eoa_missing_signed_redeem_tx(self):
        """Should raise ValueError when EOA is missing signed_redeem_tx."""
        router = self._make_router()
        params = self._make_valid_params("eoa")
        del params["signed_redeem_tx"]

        with pytest.raises(ValueError, match="signed_redeem_tx"):
            await router.claim_winnings(params)

    @pytest.mark.asyncio
    async def test_privy_missing_wallet_id(self):
        """Should raise ValueError when Privy is missing privy_wallet_id."""
        router = self._make_router()
        params = self._make_valid_params("privy")
        del params["privy_wallet_id"]

        with pytest.raises(ValueError, match="privy_wallet_id"):
            await router.claim_winnings(params)

    @pytest.mark.asyncio
    async def test_privy_missing_condition_id(self):
        """Should raise ValueError when Privy is missing condition_id."""
        router = self._make_router()
        params = self._make_valid_params("privy")
        del params["condition_id"]

        with pytest.raises(ValueError, match="condition_id"):
            await router.claim_winnings(params)

    @pytest.mark.asyncio
    async def test_privy_missing_outcome_index(self):
        """Should raise ValueError when Privy is missing outcome_index."""
        router = self._make_router()
        params = self._make_valid_params("privy")
        del params["outcome_index"]

        with pytest.raises(ValueError, match="outcome_index"):
            await router.claim_winnings(params)

    @pytest.mark.asyncio
    async def test_successful_eoa_claim(self):
        """Test successful EOA claim with mocked HTTP."""
        router = self._make_router()
        params = self._make_valid_params("eoa")

        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "positionId": params["position_id"],
            "walletType": "eoa",
            "status": "completed",
            "feePulled": True,
            "domeAmount": "2500000",
            "affiliateAmount": "500000",
            "pullFeeTxHash": "0xtxhash1",
            "distributeTxHash": "0xtxhash2",
            "redeemed": True,
            "claimTxHash": "0xtxhash3",
        }

        router._http_client = AsyncMock()
        router._http_client.post = AsyncMock(return_value=mock_response)

        result = await router.claim_winnings(params)

        assert isinstance(result, ClaimWinningsResult)
        assert result.success is True
        assert result.position_id == params["position_id"]
        assert result.wallet_type == "eoa"
        assert result.status == "completed"
        assert result.fee_pulled is True
        assert result.dome_amount == "2500000"
        assert result.affiliate_amount == "500000"
        assert result.claim_tx_hash == "0xtxhash3"

    @pytest.mark.asyncio
    async def test_successful_privy_claim(self):
        """Test successful Privy claim with mocked HTTP."""
        router = self._make_router()
        params = self._make_valid_params("privy")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "positionId": params["position_id"],
            "walletType": "privy",
            "status": "completed",
            "feePulled": True,
            "redeemed": True,
            "claimTxHash": "0xprivytxhash",
        }

        router._http_client = AsyncMock()
        router._http_client.post = AsyncMock(return_value=mock_response)

        result = await router.claim_winnings(params)

        assert result.success is True
        assert result.wallet_type == "privy"
        assert result.claim_tx_hash == "0xprivytxhash"

    @pytest.mark.asyncio
    async def test_request_body_eoa(self):
        """Verify the request body shape for EOA claims (camelCase keys)."""
        router = self._make_router()
        params = self._make_valid_params("eoa")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "success": True,
            "positionId": params["position_id"],
            "walletType": "eoa",
            "status": "completed",
        }

        router._http_client = AsyncMock()
        router._http_client.post = AsyncMock(return_value=mock_response)

        await router.claim_winnings(params)

        # Verify the HTTP call
        call_args = router._http_client.post.call_args
        url = call_args[0][0]
        assert "/polymarket/claimWinnings" in url

        body = call_args[1]["json"]
        assert body["positionId"] == params["position_id"]
        assert body["walletType"] == "eoa"
        assert body["payerAddress"] == params["payer_address"]
        assert body["signerAddress"] == params["signer_address"]
        assert body["signedRedeemTx"] == params["signed_redeem_tx"]
        assert "performanceFeeAuth" in body
        assert body["performanceFeeAuth"]["positionId"] == params["performance_fee_auth"]["positionId"]

    @pytest.mark.asyncio
    async def test_request_body_privy(self):
        """Verify the request body shape for Privy claims (camelCase keys)."""
        router = self._make_router()
        params = self._make_valid_params("privy")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "success": True,
            "positionId": params["position_id"],
            "walletType": "privy",
            "status": "completed",
        }

        router._http_client = AsyncMock()
        router._http_client.post = AsyncMock(return_value=mock_response)

        await router.claim_winnings(params)

        body = router._http_client.post.call_args[1]["json"]
        assert body["walletType"] == "privy"
        assert body["privyWalletId"] == params["privy_wallet_id"]
        assert body["conditionId"] == params["condition_id"]
        assert body["outcomeIndex"] == params["outcome_index"]
        # EOA-only field should NOT be present
        assert "signedRedeemTx" not in body

    @pytest.mark.asyncio
    async def test_server_error_response(self):
        """Should raise Exception on server error."""
        router = self._make_router()
        params = self._make_valid_params("eoa")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "error": "Position not found",
        }

        router._http_client = AsyncMock()
        router._http_client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(Exception, match="Position not found"):
            await router.claim_winnings(params)

    @pytest.mark.asyncio
    async def test_http_error(self):
        """Should raise Exception on HTTP error."""
        router = self._make_router()
        params = self._make_valid_params("eoa")

        mock_response = MagicMock()
        mock_response.is_success = False
        mock_response.status_code = 500
        mock_response.reason_phrase = "Internal Server Error"
        mock_response.text = "Internal Server Error"
        mock_response.json.return_value = {}

        router._http_client = AsyncMock()
        router._http_client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(Exception, match="500"):
            await router.claim_winnings(params)

    @pytest.mark.asyncio
    async def test_unsuccessful_claim(self):
        """Should raise Exception when server returns success=false."""
        router = self._make_router()
        params = self._make_valid_params("eoa")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "success": False,
            "positionId": params["position_id"],
        }

        router._http_client = AsyncMock()
        router._http_client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(Exception, match="unsuccessful"):
            await router.claim_winnings(params)

    @pytest.mark.asyncio
    async def test_bearer_token_header(self):
        """Should send Bearer token in Authorization header."""
        router = self._make_router()
        params = self._make_valid_params("eoa")

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "success": True,
            "positionId": params["position_id"],
            "walletType": "eoa",
            "status": "completed",
        }

        router._http_client = AsyncMock()
        router._http_client.post = AsyncMock(return_value=mock_response)

        await router.claim_winnings(params)

        headers = router._http_client.post.call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer test-api-key"
        assert headers["Content-Type"] == "application/json"

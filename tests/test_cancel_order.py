"""Tests for cancel_order support.

Tests validation, request body shape, success responses,
escrow refund handling, and error handling for the router cancel_order() method.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.dome_api_sdk.router.polymarket import PolymarketRouter
from src.dome_api_sdk.types import (
    CancelOrderParams,
    ClobCancelResult,
    EscrowRefundInfo,
    PolymarketCredentials,
    ServerCancelOrderResult,
)


# =============================================================================
# Helpers
# =============================================================================


def _make_router(api_key="test-api-key"):
    """Create a router with the given API key."""
    config = {}
    if api_key:
        config["api_key"] = api_key
    return PolymarketRouter(config)


def _make_credentials():
    """Create test CLOB credentials."""
    return PolymarketCredentials(
        api_key="clob-key",
        api_secret="clob-secret",
        api_passphrase="clob-passphrase",
    )


def _make_valid_params():
    """Create valid cancel order params."""
    return CancelOrderParams(
        order_id="order-123-abc",
        signer_address="0x" + "11" * 20,
        credentials=_make_credentials(),
    )


# =============================================================================
# Validation
# =============================================================================


class TestCancelOrderValidation:
    """Tests for required field validation."""

    @pytest.mark.asyncio
    async def test_missing_order_id(self):
        """Should raise ValueError when order_id is missing."""
        router = _make_router()
        params = CancelOrderParams(
            signer_address="0x" + "11" * 20,
            credentials=_make_credentials(),
        )

        with pytest.raises(ValueError, match="order_id"):
            await router.cancel_order(params)

    @pytest.mark.asyncio
    async def test_missing_signer_address(self):
        """Should raise ValueError when signer_address is missing."""
        router = _make_router()
        params = CancelOrderParams(
            order_id="order-123",
            credentials=_make_credentials(),
        )

        with pytest.raises(ValueError, match="signer_address"):
            await router.cancel_order(params)

    @pytest.mark.asyncio
    async def test_missing_credentials(self):
        """Should raise ValueError when credentials is missing."""
        router = _make_router()
        params = CancelOrderParams(
            order_id="order-123",
            signer_address="0x" + "11" * 20,
        )

        with pytest.raises(ValueError, match="credentials"):
            await router.cancel_order(params)


class TestCancelOrderApiKeyRequired:
    """Tests for API key requirement."""

    @pytest.mark.asyncio
    async def test_no_api_key(self):
        """Should raise ValueError when no API key is set."""
        router = _make_router(api_key=None)
        params = _make_valid_params()

        with pytest.raises(ValueError, match="Dome API key required"):
            await router.cancel_order(params)


# =============================================================================
# Request Body
# =============================================================================


class TestCancelOrderRequestBody:
    """Tests for the request body shape sent to the server."""

    @pytest.mark.asyncio
    async def test_request_body_shape(self):
        """Verify camelCase JSON body, URL, and auth headers."""
        router = _make_router()
        params = _make_valid_params()

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "orderId": "order-123-abc",
            "clobCancelResult": {
                "canceled": ["order-123-abc"],
                "not_canceled": {},
            },
            "latencyMs": 42.5,
        }

        router._http_client = AsyncMock()
        router._http_client.post = AsyncMock(return_value=mock_response)

        await router.cancel_order(params)

        # Verify URL
        call_args = router._http_client.post.call_args
        url = call_args[0][0]
        assert "/polymarket/cancelOrder" in url

        # Verify headers
        headers = call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer test-api-key"
        assert headers["Content-Type"] == "application/json"

        # Verify body uses camelCase
        body = call_args[1]["json"]
        assert body["orderId"] == "order-123-abc"
        assert body["signerAddress"] == "0x" + "11" * 20
        assert "credentials" in body
        assert body["credentials"]["apiKey"] == "clob-key"
        assert body["credentials"]["apiSecret"] == "clob-secret"
        assert body["credentials"]["apiPassphrase"] == "clob-passphrase"


# =============================================================================
# Success Responses
# =============================================================================


class TestCancelOrderSuccess:
    """Tests for successful cancel responses."""

    @pytest.mark.asyncio
    async def test_basic_success(self):
        """Test successful cancel without escrow info."""
        router = _make_router()
        params = _make_valid_params()

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "orderId": "order-123-abc",
            "clobCancelResult": {
                "canceled": ["order-123-abc"],
                "not_canceled": {},
            },
            "latencyMs": 42.5,
        }

        router._http_client = AsyncMock()
        router._http_client.post = AsyncMock(return_value=mock_response)

        result = await router.cancel_order(params)

        assert isinstance(result, ServerCancelOrderResult)
        assert result.success is True
        assert result.order_id == "order-123-abc"
        assert isinstance(result.clob_cancel_result, ClobCancelResult)
        assert result.clob_cancel_result.canceled == ["order-123-abc"]
        assert result.clob_cancel_result.not_canceled == {}
        assert result.escrow is None
        assert result.latency_ms == 42.5


class TestCancelOrderWithEscrowRefund:
    """Tests for cancel with escrow refund info."""

    @pytest.mark.asyncio
    async def test_escrow_refund(self):
        """Test cancel response with escrow refund details."""
        router = _make_router()
        params = _make_valid_params()

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "orderId": "order-123-abc",
            "clobCancelResult": {
                "canceled": ["order-123-abc"],
                "not_canceled": {},
            },
            "escrow": {
                "escrowOrderId": "0x" + "ee" * 32,
                "previousStatus": "escrowed",
                "refundTriggered": True,
                "refundTxHash": "0xtxhash123",
                "refundedAmount": "500000",
            },
            "latencyMs": 55.0,
        }

        router._http_client = AsyncMock()
        router._http_client.post = AsyncMock(return_value=mock_response)

        result = await router.cancel_order(params)

        assert result.success is True
        assert result.escrow is not None
        assert isinstance(result.escrow, EscrowRefundInfo)
        assert result.escrow.escrow_order_id == "0x" + "ee" * 32
        assert result.escrow.previous_status == "escrowed"
        assert result.escrow.refund_triggered is True
        assert result.escrow.refund_tx_hash == "0xtxhash123"
        assert result.escrow.refunded_amount == "500000"

    @pytest.mark.asyncio
    async def test_escrow_no_refund(self):
        """Test cancel response with escrow but no refund triggered."""
        router = _make_router()
        params = _make_valid_params()

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "orderId": "order-123-abc",
            "clobCancelResult": {
                "canceled": ["order-123-abc"],
                "not_canceled": {},
            },
            "escrow": {
                "escrowOrderId": "0x" + "ee" * 32,
                "previousStatus": "none",
                "refundTriggered": False,
            },
        }

        router._http_client = AsyncMock()
        router._http_client.post = AsyncMock(return_value=mock_response)

        result = await router.cancel_order(params)

        assert result.escrow is not None
        assert result.escrow.refund_triggered is False
        assert result.escrow.refund_tx_hash is None
        assert result.escrow.refunded_amount is None


# =============================================================================
# Error Handling
# =============================================================================


class TestCancelOrderServerError:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_http_error(self):
        """Should raise Exception on HTTP error."""
        router = _make_router()
        params = _make_valid_params()

        mock_response = MagicMock()
        mock_response.is_success = False
        mock_response.status_code = 500
        mock_response.reason_phrase = "Internal Server Error"
        mock_response.text = "Internal Server Error"

        router._http_client = AsyncMock()
        router._http_client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(Exception, match="500"):
            await router.cancel_order(params)

    @pytest.mark.asyncio
    async def test_server_error_message(self):
        """Should raise Exception when server returns error field."""
        router = _make_router()
        params = _make_valid_params()

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "error": "Order not found",
        }

        router._http_client = AsyncMock()
        router._http_client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(Exception, match="Order not found"):
            await router.cancel_order(params)

    @pytest.mark.asyncio
    async def test_unsuccessful_cancellation(self):
        """Should raise Exception when server returns success=false."""
        router = _make_router()
        params = _make_valid_params()

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": False,
            "orderId": "order-123-abc",
        }

        router._http_client = AsyncMock()
        router._http_client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(Exception, match="unsuccessful"):
            await router.cancel_order(params)

    @pytest.mark.asyncio
    async def test_server_message_field(self):
        """Should raise Exception when server returns message field."""
        router = _make_router()
        params = _make_valid_params()

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": "Rate limited",
        }

        router._http_client = AsyncMock()
        router._http_client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(Exception, match="Rate limited"):
            await router.cancel_order(params)

"""Tests for the endpoint classes."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from dome_api_sdk import DomeClient
from dome_api_sdk.types import (
    CandlesticksResponse,
    MarketPriceResponse,
    MatchingMarketsBySportResponse,
    MatchingMarketsResponse,
    OrdersResponse,
    WalletPnLResponse,
)


class TestMarketEndpoints:
    """Test cases for MarketEndpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return DomeClient({"api_key": "test-api-key"})

    @pytest.mark.asyncio
    async def test_get_market_price_success(self, client):
        """Test successful market price fetch."""
        mock_response = {
            "price": 0.215,
            "at_time": 1757008834,
        }

        with patch.object(client.polymarket.markets, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.polymarket.markets.get_market_price({
                "token_id": "1234567890"
            })

            mock_request.assert_called_once_with(
                "GET",
                "/polymarket/market-price/1234567890",
                {},
                None,
            )

            assert isinstance(result, MarketPriceResponse)
            assert result.price == 0.215
            assert result.at_time == 1757008834

    @pytest.mark.asyncio
    async def test_get_market_price_with_historical_timestamp(self, client):
        """Test market price fetch with historical timestamp."""
        mock_response = {
            "price": 0.215,
            "at_time": 1740000000,
        }

        with patch.object(client.polymarket.markets, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.polymarket.markets.get_market_price({
                "token_id": "1234567890",
                "at_time": 1740000000
            })

            mock_request.assert_called_once_with(
                "GET",
                "/polymarket/market-price/1234567890",
                {"at_time": 1740000000},
                None,
            )

            assert isinstance(result, MarketPriceResponse)
            assert result.price == 0.215
            assert result.at_time == 1740000000

    @pytest.mark.asyncio
    async def test_get_candlesticks_success(self, client):
        """Test successful candlestick data fetch."""
        mock_response = {
            "candlesticks": [
                [
                    [
                        {
                            "end_period_ts": 1727827200,
                            "open_interest": 8456498,
                            "price": {
                                "open": 0,
                                "high": 0,
                                "low": 0,
                                "close": 0,
                                "open_dollars": "0.0049",
                                "high_dollars": "0.0049",
                                "low_dollars": "0.0048",
                                "close_dollars": "0.0048",
                                "mean": 0,
                                "mean_dollars": "0.0049",
                                "previous": 0,
                                "previous_dollars": "0.0049",
                            },
                            "volume": 8456498,
                            "yes_ask": {
                                "open": 0.00489,
                                "close": 0.0048200000000000005,
                                "high": 0.00491,
                                "low": 0.0048,
                                "open_dollars": "0.0049",
                                "close_dollars": "0.0048",
                                "high_dollars": "0.0049",
                                "low_dollars": "0.0048",
                            },
                            "yes_bid": {
                                "open": 0.00489,
                                "close": 0.004829999990880811,
                                "high": 0.004910000000138527,
                                "low": 0.0048,
                                "open_dollars": "0.0049",
                                "close_dollars": "0.0048",
                                "high_dollars": "0.0049",
                                "low_dollars": "0.0048",
                            },
                        }
                    ],
                    {
                        "token_id": "21742633143463906290569050155826241533067272736897614950488156847949938836455"
                    }
                ]
            ]
        }

        with patch.object(client.polymarket.markets, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.polymarket.markets.get_candlesticks({
                "condition_id": "0x4567b275e6b667a6217f5cb4f06a797d3a1eaf1d0281fb5bc8c75e2046ae7e57",
                "start_time": 1640995200,
                "end_time": 1672531200,
                "interval": 60
            })

            mock_request.assert_called_once_with(
                "GET",
                "/polymarket/candlesticks/0x4567b275e6b667a6217f5cb4f06a797d3a1eaf1d0281fb5bc8c75e2046ae7e57",
                {
                    "start_time": 1640995200,
                    "end_time": 1672531200,
                    "interval": 60
                },
                None,
            )

            assert isinstance(result, CandlesticksResponse)
            assert len(result.candlesticks) == 1


class TestWalletEndpoints:
    """Test cases for WalletEndpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return DomeClient({"api_key": "test-api-key"})

    @pytest.mark.asyncio
    async def test_get_wallet_pnl_success(self, client):
        """Test successful wallet PnL fetch."""
        mock_response = {
            "granularity": "day",
            "start_time": 1726857600,
            "end_time": 1758316829,
            "wallet_address": "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",
            "pnl_over_time": [
                {
                    "timestamp": 1726857600,
                    "pnl_to_date": 2001
                }
            ]
        }

        with patch.object(client.polymarket.wallet, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.polymarket.wallet.get_wallet_pnl({
                "wallet_address": "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",
                "granularity": "day",
                "start_time": 1726857600,
                "end_time": 1758316829
            })

            mock_request.assert_called_once_with(
                "GET",
                "/polymarket/wallet/pnl/0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",
                {
                    "granularity": "day",
                    "start_time": 1726857600,
                    "end_time": 1758316829
                },
                None,
            )

            assert isinstance(result, WalletPnLResponse)
            assert result.granularity == "day"
            assert result.wallet_address == "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b"
            assert len(result.pnl_over_time) == 1
            assert result.pnl_over_time[0].timestamp == 1726857600
            assert result.pnl_over_time[0].pnl_to_date == 2001


class TestOrdersEndpoints:
    """Test cases for OrdersEndpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return DomeClient({"api_key": "test-api-key"})

    @pytest.mark.asyncio
    async def test_get_orders_success(self, client):
        """Test successful orders fetch."""
        mock_response = {
            "orders": [
                {
                    "token_id": "58519484510520807142687824915233722607092670035910114837910294451210534222702",
                    "side": "BUY",
                    "market_slug": "bitcoin-up-or-down-july-25-8pm-et",
                    "condition_id": "0x4567b275e6b667a6217f5cb4f06a797d3a1eaf1d0281fb5bc8c75e2046ae7e57",
                    "shares": 4995000,
                    "shares_normalized": 4.995,
                    "price": 0.65,
                    "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef12",
                    "title": "Will Bitcoin be above $50,000 on July 25, 2025 at 8:00 PM ET?",
                    "timestamp": 1757008834,
                    "order_hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                    "user": "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b"
                }
            ],
            "pagination": {
                "limit": 50,
                "offset": 0,
                "total": 1250,
                "has_more": True
            }
        }

        with patch.object(client.polymarket.orders, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.polymarket.orders.get_orders({
                "market_slug": "bitcoin-up-or-down-july-25-8pm-et",
                "limit": 50,
                "offset": 0
            })

            mock_request.assert_called_once_with(
                "GET",
                "/polymarket/orders",
                {
                    "market_slug": "bitcoin-up-or-down-july-25-8pm-et",
                    "limit": 50,
                    "offset": 0
                },
                None,
            )

            assert isinstance(result, OrdersResponse)
            assert len(result.orders) == 1
            assert result.orders[0].side == "BUY"
            assert result.pagination.total == 1250


class TestMatchingMarketsEndpoints:
    """Test cases for MatchingMarketsEndpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return DomeClient({"api_key": "test-api-key"})

    @pytest.mark.asyncio
    async def test_get_matching_markets_success(self, client):
        """Test successful matching markets fetch."""
        mock_response = {
            "markets": {
                "nfl-ari-den-2025-08-16": [
                    {
                        "platform": "KALSHI",
                        "event_ticker": "KXNFLGAME-25AUG16ARIDEN",
                        "market_tickers": [
                            "KXNFLGAME-25AUG16ARIDEN-ARI",
                            "KXNFLGAME-25AUG16ARIDEN-DEN"
                        ]
                    },
                    {
                        "platform": "POLYMARKET",
                        "market_slug": "nfl-ari-den-2025-08-16",
                        "token_ids": [
                            "34541522652444763571858406546623861155130750437169507355470933750634189084033",
                            "104612081187206848956763018128517335758189185749897027211060738913329108425255"
                        ]
                    }
                ]
            }
        }

        with patch.object(client.matching_markets, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.matching_markets.get_matching_markets({
                "polymarket_market_slug": ["nfl-ari-den-2025-08-16"]
            })

            mock_request.assert_called_once_with(
                "GET",
                "/matching-markets/sports/",
                {
                    "polymarket_market_slug": ["nfl-ari-den-2025-08-16"]
                },
                None,
            )

            assert isinstance(result, MatchingMarketsResponse)
            assert "nfl-ari-den-2025-08-16" in result.markets

    @pytest.mark.asyncio
    async def test_get_matching_markets_by_sport_success(self, client):
        """Test successful matching markets by sport fetch."""
        mock_response = {
            "markets": {
                "nfl-ari-den-2025-08-16": [
                    {
                        "platform": "KALSHI",
                        "event_ticker": "KXNFLGAME-25AUG16ARIDEN",
                        "market_tickers": [
                            "KXNFLGAME-25AUG16ARIDEN-ARI",
                            "KXNFLGAME-25AUG16ARIDEN-DEN"
                        ]
                    }
                ]
            },
            "sport": "nfl",
            "date": "2025-08-16"
        }

        with patch.object(client.matching_markets, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.matching_markets.get_matching_markets_by_sport({
                "sport": "nfl",
                "date": "2025-08-16"
            })

            mock_request.assert_called_once_with(
                "GET",
                "/matching-markets/sports/nfl/",
                {"date": "2025-08-16"},
                None,
            )

            assert isinstance(result, MatchingMarketsBySportResponse)
            assert result.sport == "nfl"
            assert result.date == "2025-08-16"
            assert "nfl-ari-den-2025-08-16" in result.markets


class TestErrorHandling:
    """Test error handling across endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return DomeClient({"api_key": "test-api-key"})

    @pytest.mark.asyncio
    async def test_api_error_handling(self, client):
        """Test API error handling."""
        with patch.object(client.polymarket.markets, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = ValueError("API Error: BAD_REQUEST - Invalid parameters")

            with pytest.raises(ValueError, match="API Error: BAD_REQUEST - Invalid parameters"):
                await client.polymarket.markets.get_market_price({
                    "token_id": "invalid"
                })

    @pytest.mark.asyncio
    async def test_network_error_handling(self, client):
        """Test network error handling."""
        with patch.object(client.polymarket.markets, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = ValueError("Request failed: Network Error")

            with pytest.raises(ValueError, match="Request failed: Network Error"):
                await client.polymarket.markets.get_market_price({
                    "token_id": "123"
                })

#!/usr/bin/env python3
"""
Integration test for the Dome API SDK.

This script tests the SDK against the live API to ensure all endpoints work correctly.
Run with: python -m dome_api_sdk.tests.integration_test <api_key>
"""

import asyncio
import sys
from typing import Any, Dict, Optional

from dome_api_sdk import DomeClient, WebSocketOrderEvent


def _test_market_endpoints(dome: DomeClient) -> Dict[str, Any]:
    """Test market-related endpoints."""
    results = {}

    try:
        # Test get_market_price
        print("Testing get_market_price...")
        market_price = dome.polymarket.markets.get_market_price(
            {
                "token_id": "18823838997443878656879952590502524526556504037944392973476854588563571859850"
            }
        )
        results["get_market_price"] = {
            "success": True,
            "price": market_price.price,
            "at_time": market_price.at_time,
        }
        print(f"✅ get_market_price: {market_price.price}")
    except Exception as e:
        results["get_market_price"] = {"success": False, "error": str(e)}
        print(f"❌ get_market_price failed: {e}")

    try:
        # Test get_market_price with at_time
        print("Testing get_market_price with at_time...")
        market_price_historical = dome.polymarket.markets.get_market_price(
            {
                "token_id": "18823838997443878656879952590502524526556504037944392973476854588563571859850",
                "at_time": 1759720853,
            }
        )
        results["get_market_price_historical"] = {
            "success": True,
            "price": market_price_historical.price,
            "at_time": market_price_historical.at_time,
        }
        print(
            f"✅ get_market_price with at_time: {market_price_historical.price} at {market_price_historical.at_time}"
        )
    except Exception as e:
        results["get_market_price_historical"] = {"success": False, "error": str(e)}
        print(f"❌ get_market_price with at_time failed: {e}")

    try:
        # Test get_candlesticks
        print("Testing get_candlesticks...")
        candlesticks = dome.polymarket.markets.get_candlesticks(
            {
                "condition_id": "0x4567b275e6b667a6217f5cb4f06a797d3a1eaf1d0281fb5bc8c75e2046ae7e57",
                "start_time": 1759471500,
                "end_time": 1759711620,
                "interval": 60,
            }
        )
        results["get_candlesticks"] = {
            "success": True,
            "candlesticks_count": len(candlesticks.candlesticks),
        }
        print(f"✅ get_candlesticks: {len(candlesticks.candlesticks)} candlesticks")
    except Exception as e:
        results["get_candlesticks"] = {"success": False, "error": str(e)}
        print(f"❌ get_candlesticks failed: {e}")

    try:
        # Test get_markets
        print("Testing get_markets...")
        markets = dome.polymarket.markets.get_markets(
            {
                "status": "open",
                "limit": 5,
                "offset": 0,
            }
        )
        results["get_markets"] = {
            "success": True,
            "markets_count": len(markets.markets),
            "total": markets.pagination.total,
            "has_more": markets.pagination.has_more,
        }
        print(
            f"✅ get_markets: {len(markets.markets)} markets (total: {markets.pagination.total})"
        )
    except Exception as e:
        results["get_markets"] = {"success": False, "error": str(e)}
        print(f"❌ get_markets failed: {e}")

    try:
        # Test get_markets with filters and validate all fields
        print("Testing get_markets with market_slug filter...")
        # Test with string (single value)
        markets_filtered = dome.polymarket.markets.get_markets(
            {
                "market_slug": "bitcoin-up-or-down-july-25-8pm-et",
                "limit": 10,
            }
        )

        # Validate all fields from the response
        if markets_filtered.markets:
            market = markets_filtered.markets[0]
            validation_results = {
                "market_slug": market.market_slug
                == "bitcoin-up-or-down-july-25-8pm-et",
                "title": isinstance(market.title, str) and len(market.title) > 0,
                "condition_id": isinstance(market.condition_id, str)
                and len(market.condition_id) > 0,
                "start_time": isinstance(market.start_time, int),
                "end_time": isinstance(market.end_time, int),
                "completed_time": market.completed_time is None
                or isinstance(market.completed_time, int),
                "close_time": market.close_time is None
                or isinstance(market.close_time, int),
                "tags": isinstance(market.tags, list),
                "volume_1_week": isinstance(market.volume_1_week, (int, float)),
                "volume_1_month": isinstance(market.volume_1_month, (int, float)),
                "volume_1_year": isinstance(market.volume_1_year, (int, float)),
                "volume_total": isinstance(market.volume_total, (int, float)),
                "resolution_source": isinstance(market.resolution_source, str),
                "image": isinstance(market.image, str),
                "side_a": isinstance(market.side_a.id, str)
                and isinstance(market.side_a.label, str),
                "side_b": isinstance(market.side_b.id, str)
                and isinstance(market.side_b.label, str),
                "winning_side": market.winning_side is None
                or (
                    isinstance(market.winning_side.id, str)
                    and isinstance(market.winning_side.label, str)
                ),
                "status": market.status in ["open", "closed"],
            }

            all_valid = all(validation_results.values())
            results["get_markets_filtered"] = {
                "success": True,
                "markets_count": len(markets_filtered.markets),
                "field_validation": validation_results,
                "all_fields_valid": all_valid,
            }

            if all_valid:
                print(
                    f"✅ get_markets (filtered): {len(markets_filtered.markets)} markets - all fields validated"
                )
            else:
                invalid_fields = [k for k, v in validation_results.items() if not v]
                print(
                    f"⚠️  get_markets (filtered): {len(markets_filtered.markets)} markets - invalid fields: {invalid_fields}"
                )
        else:
            results["get_markets_filtered"] = {
                "success": True,
                "markets_count": 0,
                "field_validation": {},
                "all_fields_valid": False,
            }
            print("✅ get_markets (filtered): 0 markets (no markets found)")
    except Exception as e:
        results["get_markets_filtered"] = {"success": False, "error": str(e)}
        print(f"❌ get_markets (filtered) failed: {e}")

    try:
        # Test get_orderbooks
        print("Testing get_orderbooks...")
        # Using a timestamp in milliseconds for a recent date
        orderbooks = dome.polymarket.markets.get_orderbooks(
            {
                "token_id": "18823838997443878656879952590502524526556504037944392973476854588563571859850",
                "start_time": 1760470000000,  # milliseconds
                "end_time": 1760480000000,  # milliseconds
                "limit": 10,
            }
        )
        results["get_orderbooks"] = {
            "success": True,
            "snapshots_count": len(orderbooks.snapshots),
            "has_more": orderbooks.pagination.has_more,
        }
        print(
            f"✅ get_orderbooks: {len(orderbooks.snapshots)} snapshots (has_more: {orderbooks.pagination.has_more})"
        )
    except Exception as e:
        results["get_orderbooks"] = {"success": False, "error": str(e)}
        print(f"❌ get_orderbooks failed: {e}")

    return results


def _test_wallet_endpoints(dome: DomeClient) -> Dict[str, Any]:
    """Test wallet-related endpoints."""
    results = {}

    try:
        # Test get_wallet_pnl
        print("Testing get_wallet_pnl...")
        wallet_pnl = dome.polymarket.wallet.get_wallet_pnl(
            {
                "wallet_address": "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",
                "granularity": "day",
                "start_time": 1726857600,
                "end_time": 1758316829,
            }
        )
        results["get_wallet_pnl"] = {
            "success": True,
            "data_points": len(wallet_pnl.pnl_over_time),
            "granularity": wallet_pnl.granularity,
        }
        print(f"✅ get_wallet_pnl: {len(wallet_pnl.pnl_over_time)} data points")
    except Exception as e:
        results["get_wallet_pnl"] = {"success": False, "error": str(e)}
        print(f"❌ get_wallet_pnl failed: {e}")

    return results


def _test_activity_endpoints(dome: DomeClient) -> Dict[str, Any]:
    """Test activity-related endpoints."""
    results = {}

    try:
        # Test get_activity
        print("Testing get_activity...")
        activity = dome.polymarket.activity.get_activity(
            {
                "user": "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",
                "limit": 10,
                "offset": 0,
            }
        )
        results["get_activity"] = {
            "success": True,
            "activities_count": len(activity.activities),
            "count": activity.pagination.count,
            "has_more": activity.pagination.has_more,
        }
        print(
            f"✅ get_activity: {len(activity.activities)} activities (total: {activity.pagination.count})"
        )
    except Exception as e:
        results["get_activity"] = {"success": False, "error": str(e)}
        print(f"❌ get_activity failed: {e}")

    try:
        # Test get_activity with time range
        print("Testing get_activity with time range...")
        activity_filtered = dome.polymarket.activity.get_activity(
            {
                "user": "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",
                "start_time": 1726857600,
                "end_time": 1758316829,
                "limit": 5,
            }
        )
        results["get_activity_filtered"] = {
            "success": True,
            "activities_count": len(activity_filtered.activities),
        }
        print(
            f"✅ get_activity (filtered): {len(activity_filtered.activities)} activities"
        )
    except Exception as e:
        results["get_activity_filtered"] = {"success": False, "error": str(e)}
        print(f"❌ get_activity (filtered) failed: {e}")

    return results


def _test_kalshi_endpoints(dome: DomeClient) -> Dict[str, Any]:
    """Test Kalshi-related endpoints."""
    results = {}

    try:
        # Test get_kalshi_markets
        print("Testing get_kalshi_markets...")
        kalshi_markets = dome.kalshi.markets.get_markets(
            {
                "status": "open",
                "limit": 5,
                "offset": 0,
            }
        )
        results["get_kalshi_markets"] = {
            "success": True,
            "markets_count": len(kalshi_markets.markets),
            "total": kalshi_markets.pagination.total,
            "has_more": kalshi_markets.pagination.has_more,
        }
        print(
            f"✅ get_kalshi_markets: {len(kalshi_markets.markets)} markets (total: {kalshi_markets.pagination.total})"
        )
    except Exception as e:
        results["get_kalshi_markets"] = {"success": False, "error": str(e)}
        print(f"❌ get_kalshi_markets failed: {e}")

    try:
        # Test get_kalshi_markets with array filters
        print("Testing get_kalshi_markets with array filters...")
        kalshi_markets_filtered = dome.kalshi.markets.get_markets(
            {
                "market_ticker": ["KXNFLGAME-25AUG16ARIDEN-ARI"],
                "limit": 5,
            }
        )
        results["get_kalshi_markets_filtered"] = {
            "success": True,
            "markets_count": len(kalshi_markets_filtered.markets),
        }
        print(
            f"✅ get_kalshi_markets (filtered): {len(kalshi_markets_filtered.markets)} markets"
        )
    except Exception as e:
        results["get_kalshi_markets_filtered"] = {"success": False, "error": str(e)}
        print(f"❌ get_kalshi_markets (filtered) failed: {e}")

    try:
        # Test get_kalshi_orderbooks
        print("Testing get_kalshi_orderbooks...")
        # Using a timestamp in milliseconds for a recent date
        kalshi_orderbooks = dome.kalshi.orderbooks.get_orderbooks(
            {
                "ticker": "KXNFLGAME-25AUG16ARIDEN-ARI",
                "start_time": 1760470000000,  # milliseconds
                "end_time": 1760480000000,  # milliseconds
                "limit": 10,
            }
        )
        results["get_kalshi_orderbooks"] = {
            "success": True,
            "snapshots_count": len(kalshi_orderbooks.snapshots),
            "has_more": kalshi_orderbooks.pagination.has_more,
        }
        print(
            f"✅ get_kalshi_orderbooks: {len(kalshi_orderbooks.snapshots)} snapshots (has_more: {kalshi_orderbooks.pagination.has_more})"
        )
    except Exception as e:
        results["get_kalshi_orderbooks"] = {"success": False, "error": str(e)}
        print(f"❌ get_kalshi_orderbooks failed: {e}")

    return results


def _test_orders_endpoints(dome: DomeClient) -> Dict[str, Any]:
    """Test orders-related endpoints."""
    results = {}

    try:
        # Test get_orders
        print("Testing get_orders...")
        orders = dome.polymarket.orders.get_orders(
            {
                "market_slug": "bitcoin-up-or-down-july-25-8pm-et",
                "limit": 10,
                "offset": 0,
            }
        )
        results["get_orders"] = {
            "success": True,
            "orders_count": len(orders.orders),
            "total": orders.pagination.total,
            "has_more": orders.pagination.has_more,
        }
        print(
            f"✅ get_orders: {len(orders.orders)} orders (total: {orders.pagination.total})"
        )
    except Exception as e:
        results["get_orders"] = {"success": False, "error": str(e)}
        print(f"❌ get_orders failed: {e}")

    try:
        # Test get_orders with array parameter
        print("Testing get_orders with array market_slug...")
        orders_array = dome.polymarket.orders.get_orders(
            {
                "market_slug": ["bitcoin-up-or-down-july-25-8pm-et"],
                "limit": 5,
            }
        )
        results["get_orders_array"] = {
            "success": True,
            "orders_count": len(orders_array.orders),
        }
        print(f"✅ get_orders (array): {len(orders_array.orders)} orders")
    except Exception as e:
        results["get_orders_array"] = {"success": False, "error": str(e)}
        print(f"❌ get_orders (array) failed: {e}")

    try:
        # Test get_orders with user filter
        print("Testing get_orders with user filter...")
        orders_user = dome.polymarket.orders.get_orders(
            {
                "user": "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",
                "limit": 5,
            }
        )
        results["get_orders_user"] = {
            "success": True,
            "orders_count": len(orders_user.orders),
        }
        print(f"✅ get_orders (user): {len(orders_user.orders)} orders")
    except Exception as e:
        results["get_orders_user"] = {"success": False, "error": str(e)}
        print(f"❌ get_orders (user) failed: {e}")

    return results


def _test_matching_markets_endpoints(dome: DomeClient) -> Dict[str, Any]:
    """Test matching markets-related endpoints."""
    results = {}

    try:
        # Test get_matching_markets
        print("Testing get_matching_markets...")
        matching_markets = dome.matching_markets.get_matching_markets(
            {"polymarket_market_slug": ["nfl-ari-den-2025-08-16"]}
        )
        results["get_matching_markets"] = {
            "success": True,
            "markets_count": len(matching_markets.markets),
        }
        print(f"✅ get_matching_markets: {len(matching_markets.markets)} market groups")
    except Exception as e:
        results["get_matching_markets"] = {"success": False, "error": str(e)}
        print(f"❌ get_matching_markets failed: {e}")

    try:
        # Test get_matching_markets with multiple slugs
        print("Testing get_matching_markets with multiple slugs...")
        matching_markets_multi = dome.matching_markets.get_matching_markets(
            {
                "polymarket_market_slug": [
                    "nfl-ari-den-2025-08-16",
                    "nfl-dal-phi-2025-09-04",
                ]
            }
        )
        results["get_matching_markets_multi"] = {
            "success": True,
            "markets_count": len(matching_markets_multi.markets),
        }
        print(
            f"✅ get_matching_markets (multi): {len(matching_markets_multi.markets)} market groups"
        )
    except Exception as e:
        results["get_matching_markets_multi"] = {"success": False, "error": str(e)}
        print(f"❌ get_matching_markets (multi) failed: {e}")

    try:
        # Test get_matching_markets_by_sport
        print("Testing get_matching_markets_by_sport...")
        matching_markets_by_sport = dome.matching_markets.get_matching_markets_by_sport(
            {"sport": "nfl", "date": "2025-08-16"}
        )
        results["get_matching_markets_by_sport"] = {
            "success": True,
            "markets_count": len(matching_markets_by_sport.markets),
            "sport": matching_markets_by_sport.sport,
            "date": matching_markets_by_sport.date,
        }
        print(
            f"✅ get_matching_markets_by_sport: {len(matching_markets_by_sport.markets)} market groups"
        )
    except Exception as e:
        results["get_matching_markets_by_sport"] = {"success": False, "error": str(e)}
        print(f"❌ get_matching_markets_by_sport failed: {e}")

    return results


async def _test_websocket_endpoints(dome: DomeClient) -> Dict[str, Any]:
    """Test WebSocket-related endpoints."""
    results = {}
    ws_client = dome.polymarket.websocket
    subscription_id: Optional[str] = None

    try:
        print("Testing WebSocket connection and subscription...")

        # Event received flag
        event_received = asyncio.Event()
        received_event: Optional[WebSocketOrderEvent] = None

        def on_order_event(event: WebSocketOrderEvent) -> None:
            """Handle order event."""
            nonlocal received_event
            received_event = event
            event_received.set()

        # Connect to WebSocket
        await ws_client.connect()
        print("✅ WebSocket connected")

        # Subscribe to orders for the specified user
        subscription_id = await ws_client.subscribe(
            users=["0x6031b6eed1c97e853c6e0f03ad3ce3529351f96d"],
            on_event=on_order_event,
        )
        print(f"✅ Subscribed to orders (subscription_id: {subscription_id})")

        # Check active subscriptions
        active_subscriptions = ws_client.get_active_subscriptions()
        if len(active_subscriptions) == 1:
            print(f"✅ Active subscriptions tracked correctly: {len(active_subscriptions)}")
        else:
            print(
                f"⚠️  Expected 1 active subscription, got {len(active_subscriptions)}"
            )

        # Wait up to 30 seconds for an order event
        print("Waiting up to 30 seconds for an order event...")
        try:
            await asyncio.wait_for(event_received.wait(), timeout=30.0)
            print("✅ Order event received!")

            if received_event:
                results["websocket_subscription"] = {
                    "success": True,
                    "subscription_id": received_event.subscription_id,
                    "order_token_id": received_event.data.token_id,
                    "order_user": received_event.data.user,
                    "order_side": received_event.data.side,
                    "order_market_slug": received_event.data.market_slug,
                }
                print(
                    f"✅ Order event details: user={received_event.data.user}, "
                    f"side={received_event.data.side}, market={received_event.data.market_slug}"
                )
            else:
                results["websocket_subscription"] = {
                    "success": False,
                    "error": "Event received but data is None",
                }
                print("❌ Event received but data is None")

        except asyncio.TimeoutError:
            results["websocket_subscription"] = {
                "success": False,
                "error": "Timeout: No order event received within 30 seconds",
            }
            print("❌ Timeout: No order event received within 30 seconds")

        # Test unsubscribe
        if subscription_id:
            try:
                await ws_client.unsubscribe(subscription_id)
                print(f"✅ Unsubscribed successfully (subscription_id: {subscription_id})")

                # Verify subscription was removed
                active_after_unsubscribe = ws_client.get_active_subscriptions()
                if len(active_after_unsubscribe) == 0:
                    print("✅ Subscription removed from active subscriptions")
                else:
                    print(
                        f"⚠️  Expected 0 active subscriptions after unsubscribe, got {len(active_after_unsubscribe)}"
                    )

            except Exception as e:
                print(f"⚠️  Unsubscribe failed: {e}")

    except Exception as e:
        results["websocket_subscription"] = {"success": False, "error": str(e)}
        print(f"❌ WebSocket test failed: {e}")
    finally:
        # Always disconnect, even if there was an error
        try:
            await ws_client.disconnect()
            print("✅ WebSocket disconnected")
        except Exception as e:
            print(f"⚠️  Error disconnecting WebSocket: {e}")

    return results


def main():
    """Run all integration tests."""
    if len(sys.argv) != 2:
        print("Usage: python -m dome_api_sdk.tests.integration_test <api_key>")
        sys.exit(1)

    api_key = sys.argv[1]

    print("🚀 Starting Dome API SDK Integration Tests")
    print("=" * 50)

    # Initialize the client
    dome = DomeClient({"api_key": api_key})
    print(f"✅ Client initialized with API key: {api_key[:8]}...")

    try:
        # Run all tests
        all_results = {}

        print("\n📊 Testing Market Endpoints...")
        all_results["market"] = _test_market_endpoints(dome)

        print("\n💰 Testing Wallet Endpoints...")
        all_results["wallet"] = _test_wallet_endpoints(dome)

        print("\n📋 Testing Orders Endpoints...")
        all_results["orders"] = _test_orders_endpoints(dome)

        print("\n📝 Testing Activity Endpoints...")
        all_results["activity"] = _test_activity_endpoints(dome)

        print("\n🔗 Testing Matching Markets Endpoints...")
        all_results["matching_markets"] = _test_matching_markets_endpoints(dome)

        print("\n🎯 Testing Kalshi Endpoints...")
        all_results["kalshi"] = _test_kalshi_endpoints(dome)

        print("\n🔌 Testing WebSocket Endpoints...")
        all_results["websocket"] = asyncio.run(_test_websocket_endpoints(dome))

        # Summary
        print("\n" + "=" * 50)
        print("📈 INTEGRATION TEST SUMMARY")
        print("=" * 50)

        total_tests = 0
        passed_tests = 0

        for category, tests in all_results.items():
            print(f"\n{category.upper()}:")
            for test_name, result in tests.items():
                total_tests += 1
                if result["success"]:
                    passed_tests += 1
                    print(f"  ✅ {test_name}")
                else:
                    print(f"  ❌ {test_name}: {result['error']}")

        print(f"\n🎯 Results: {passed_tests}/{total_tests} tests passed")

        if passed_tests == total_tests:
            print("🎉 All tests passed! The SDK is working correctly.")
            sys.exit(0)
        else:
            print("⚠️  Some tests failed. Check the errors above.")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

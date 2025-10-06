#!/usr/bin/env python3
"""
Integration test for the Dome API SDK.

This script tests the SDK against the live API to ensure all endpoints work correctly.
Run with: python -m dome_api_sdk.tests.integration_test <api_key>
"""

import sys
from typing import Dict, Any

from dome_api_sdk import DomeClient


def _test_market_endpoints(dome: DomeClient) -> Dict[str, Any]:
    """Test market-related endpoints."""
    results = {}
    
    try:
        # Test get_market_price
        print("Testing get_market_price...")
        market_price = dome.polymarket.markets.get_market_price({
            "token_id": "18823838997443878656879952590502524526556504037944392973476854588563571859850"
        })
        results["get_market_price"] = {
            "success": True,
            "price": market_price.price,
            "at_time": market_price.at_time
        }
        print(f"✅ get_market_price: {market_price.price}")
    except Exception as e:
        results["get_market_price"] = {"success": False, "error": str(e)}
        print(f"❌ get_market_price failed: {e}")
    
    try:
        # Test get_market_price with at_time
        print("Testing get_market_price with at_time...")
        market_price_historical = dome.polymarket.markets.get_market_price({
            "token_id": "18823838997443878656879952590502524526556504037944392973476854588563571859850",
            "at_time": 1759720853
        })
        results["get_market_price_historical"] = {
            "success": True,
            "price": market_price_historical.price,
            "at_time": market_price_historical.at_time
        }
        print(f"✅ get_market_price with at_time: {market_price_historical.price} at {market_price_historical.at_time}")
    except Exception as e:
        results["get_market_price_historical"] = {"success": False, "error": str(e)}
        print(f"❌ get_market_price with at_time failed: {e}")
    
    try:
        # Test get_candlesticks
        print("Testing get_candlesticks...")
        candlesticks = dome.polymarket.markets.get_candlesticks({
            "condition_id": "0x4567b275e6b667a6217f5cb4f06a797d3a1eaf1d0281fb5bc8c75e2046ae7e57",
            "start_time": 1759471500,
            "end_time": 1759711620,
            "interval": 60
        })
        results["get_candlesticks"] = {
            "success": True,
            "candlesticks_count": len(candlesticks.candlesticks)
        }
        print(f"✅ get_candlesticks: {len(candlesticks.candlesticks)} candlesticks")
    except Exception as e:
        results["get_candlesticks"] = {"success": False, "error": str(e)}
        print(f"❌ get_candlesticks failed: {e}")
    
    return results


# def _test_wallet_endpoints(dome: DomeClient) -> Dict[str, Any]:
#     """Test wallet-related endpoints."""
#     results = {}
    
#     try:
#         # Test get_wallet_pnl
#         print("Testing get_wallet_pnl...")
#         wallet_pnl = dome.polymarket.wallet.get_wallet_pnl({
#             "wallet_address": "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",
#             "granularity": "day",
#             "start_time": 1726857600,
#             "end_time": 1758316829
#         })
#         results["get_wallet_pnl"] = {
#             "success": True,
#             "data_points": len(wallet_pnl.pnl_over_time),
#             "granularity": wallet_pnl.granularity
#         }
#         print(f"✅ get_wallet_pnl: {len(wallet_pnl.pnl_over_time)} data points")
#     except Exception as e:
#         results["get_wallet_pnl"] = {"success": False, "error": str(e)}
#         print(f"❌ get_wallet_pnl failed: {e}")
    
#     return results


def _test_orders_endpoints(dome: DomeClient) -> Dict[str, Any]:
    """Test orders-related endpoints."""
    results = {}
    
    try:
        # Test get_orders
        print("Testing get_orders...")
        orders = dome.polymarket.orders.get_orders({
            "market_slug": "bitcoin-up-or-down-july-25-8pm-et",
            "limit": 10,
            "offset": 0
        })
        results["get_orders"] = {
            "success": True,
            "orders_count": len(orders.orders),
            "total": orders.pagination.total,
            "has_more": orders.pagination.has_more
        }
        print(f"✅ get_orders: {len(orders.orders)} orders (total: {orders.pagination.total})")
    except Exception as e:
        results["get_orders"] = {"success": False, "error": str(e)}
        print(f"❌ get_orders failed: {e}")
    
    return results


def _test_matching_markets_endpoints(dome: DomeClient) -> Dict[str, Any]:
    """Test matching markets-related endpoints."""
    results = {}
    
    try:
        # Test get_matching_markets
        print("Testing get_matching_markets...")
        matching_markets = dome.matching_markets.get_matching_markets({
            "polymarket_market_slug": ["nfl-ari-den-2025-08-16"]
        })
        results["get_matching_markets"] = {
            "success": True,
            "markets_count": len(matching_markets.markets)
        }
        print(f"✅ get_matching_markets: {len(matching_markets.markets)} market groups")
    except Exception as e:
        results["get_matching_markets"] = {"success": False, "error": str(e)}
        print(f"❌ get_matching_markets failed: {e}")
    
    try:
        # Test get_matching_markets_by_sport
        print("Testing get_matching_markets_by_sport...")
        matching_markets_by_sport = dome.matching_markets.get_matching_markets_by_sport({
            "sport": "nfl",
            "date": "2025-08-16"
        })
        results["get_matching_markets_by_sport"] = {
            "success": True,
            "markets_count": len(matching_markets_by_sport.markets),
            "sport": matching_markets_by_sport.sport,
            "date": matching_markets_by_sport.date
        }
        print(f"✅ get_matching_markets_by_sport: {len(matching_markets_by_sport.markets)} market groups")
    except Exception as e:
        results["get_matching_markets_by_sport"] = {"success": False, "error": str(e)}
        print(f"❌ get_matching_markets_by_sport failed: {e}")
    
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
        
        # print("\n💰 Testing Wallet Endpoints...")
        # all_results["wallet"] = _test_wallet_endpoints(dome)
        
        print("\n📋 Testing Orders Endpoints...")
        all_results["orders"] = _test_orders_endpoints(dome)
        
        print("\n🔗 Testing Matching Markets Endpoints...")
        all_results["matching_markets"] = _test_matching_markets_endpoints(dome)
        
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

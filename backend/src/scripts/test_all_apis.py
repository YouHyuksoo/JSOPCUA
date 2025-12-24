"""
Test script to verify all API routes work correctly after schema fixes
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_api(method, endpoint, description, data=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*70}")
    print(f"Testing: {description}")
    print(f"{method} {url}")

    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, timeout=5)

        print(f"Status: {response.status_code}")

        if response.status_code < 400:
            result = response.json()
            print(f"✅ SUCCESS")
            if isinstance(result, dict):
                if 'items' in result:
                    print(f"   Returned {len(result['items'])} items")
                    if result['items']:
                        print(f"   First item keys: {list(result['items'][0].keys())}")
                else:
                    print(f"   Response keys: {list(result.keys())}")
            return True
        else:
            print(f"❌ FAILED")
            print(f"   Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def main():
    print("="*70)
    print("API SCHEMA VALIDATION TEST")
    print("="*70)

    results = []

    # Test Lines API
    results.append(test_api("GET", "/api/lines", "List all lines"))
    results.append(test_api("GET", "/api/lines?page=1&limit=10", "List lines with pagination"))

    # Test Processes API
    results.append(test_api("GET", "/api/processes", "List all processes"))
    results.append(test_api("GET", "/api/processes?page=1&limit=10", "List processes with pagination"))

    # Test PLC Connections API
    results.append(test_api("GET", "/api/plc-connections", "List all PLC connections"))
    results.append(test_api("GET", "/api/plc-connections?page=1&limit=10", "List PLC connections with pagination"))

    # Test Tags API
    results.append(test_api("GET", "/api/tags", "List all tags"))
    results.append(test_api("GET", "/api/tags?page=1&limit=10", "List tags with pagination"))

    # Test Polling Groups API
    results.append(test_api("GET", "/api/polling-groups", "List all polling groups"))
    results.append(test_api("GET", "/api/polling-groups?page=1&limit=10", "List polling groups with pagination"))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")

    if passed == total:
        print("\n✅ ALL TESTS PASSED - All API routes are working correctly!")
    else:
        print("\n❌ SOME TESTS FAILED - Please check the errors above")

    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

"""
Test script for Lines API

Feature 5: Database Management REST API
Tests CRUD operations on /api/lines endpoints
"""

import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"


def print_response(response: requests.Response, operation: str):
    """Print formatted response"""
    print(f"\n{'=' * 60}")
    print(f"{operation}")
    print(f"{'=' * 60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")


def test_create_line():
    """Test POST /api/lines"""
    line_data = {
        "line_code": "LINE001",
        "line_name": "Assembly Line 1",
        "location": "Factory A - Building 1",
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/lines", json=line_data)
    print_response(response, "CREATE LINE")
    if response.status_code == 201:
        return response.json()["id"]
    return None


def test_list_lines():
    """Test GET /api/lines"""
    response = requests.get(f"{BASE_URL}/api/lines?page=1&limit=10")
    print_response(response, "LIST LINES (Page 1)")


def test_get_line(line_id: int):
    """Test GET /api/lines/{id}"""
    response = requests.get(f"{BASE_URL}/api/lines/{line_id}")
    print_response(response, f"GET LINE {line_id}")


def test_update_line(line_id: int):
    """Test PUT /api/lines/{id}"""
    update_data = {
        "line_name": "Assembly Line 1 (Updated)",
        "enabled": False
    }
    response = requests.put(f"{BASE_URL}/api/lines/{line_id}", json=update_data)
    print_response(response, f"UPDATE LINE {line_id}")


def test_delete_line(line_id: int):
    """Test DELETE /api/lines/{id}"""
    response = requests.delete(f"{BASE_URL}/api/lines/{line_id}")
    print_response(response, f"DELETE LINE {line_id}")


def test_duplicate_line_code():
    """Test duplicate line_code error"""
    line_data = {
        "line_code": "LINE001",
        "line_name": "Duplicate Line",
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/lines", json=line_data)
    print_response(response, "CREATE DUPLICATE LINE (Should fail)")


def test_invalid_line_id():
    """Test get non-existent line"""
    response = requests.get(f"{BASE_URL}/api/lines/99999")
    print_response(response, "GET NON-EXISTENT LINE (Should fail)")


def test_validation_error():
    """Test validation error (missing required field)"""
    line_data = {
        "line_code": "LINE002"
        # Missing line_name (required)
    }
    response = requests.post(f"{BASE_URL}/api/lines", json=line_data)
    print_response(response, "CREATE LINE WITH MISSING FIELD (Should fail)")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("LINES API TEST SUITE")
    print("=" * 60)

    # Test server health
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_response(response, "SERVER HEALTH CHECK")
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server. Is it running?")
        print("   Start with: cd backend && python -m uvicorn src.api.main:app --reload")
        return

    # Test CRUD operations
    line_id = test_create_line()

    if line_id:
        test_list_lines()
        test_get_line(line_id)
        test_update_line(line_id)

    # Test error cases
    test_duplicate_line_code()
    test_invalid_line_id()
    test_validation_error()

    # Cleanup
    if line_id:
        test_delete_line(line_id)

    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()

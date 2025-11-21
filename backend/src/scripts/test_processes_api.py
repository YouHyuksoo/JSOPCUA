"""
Test script for Workstages API

Feature 5: Database Management REST API
Tests CRUD operations on /api/workstages endpoints
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


def create_test_line():
    """Create a test line for workstage testing"""
    line_data = {
        "line_code": "TESTLINE",
        "line_name": "Test Line for Workstages",
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/lines", json=line_data)
    if response.status_code == 201:
        return response.json()["id"]
    return None


def test_create_workstage(line_id: int):
    """Test POST /api/workstages"""
    workstage_data = {
        "line_id": line_id,
        "workstage_sequence": 1,
        "workstage_code": "KRCWO12ELOA101",  # 14-char format
        "workstage_name": "Electroplating Workstage A",
        "equipment_type": "ELO",
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/workstages", json=workstage_data)
    print_response(response, "CREATE WORKSTAGE")
    if response.status_code == 201:
        return response.json()["id"]
    return None


def test_list_workstages(line_id: Optional[int] = None):
    """Test GET /api/workstages"""
    url = f"{BASE_URL}/api/workstages?page=1&limit=10"
    if line_id:
        url += f"&line_id={line_id}"
    response = requests.get(url)
    print_response(response, f"LIST WORKSTAGES (line_id={line_id if line_id else 'all'})")


def test_get_workstage(workstage_id: int):
    """Test GET /api/workstages/{id}"""
    response = requests.get(f"{BASE_URL}/api/workstages/{workstage_id}")
    print_response(response, f"GET WORKSTAGE {workstage_id}")


def test_update_workstage(workstage_id: int):
    """Test PUT /api/workstages/{id}"""
    update_data = {
        "workstage_name": "Electroplating Workstage A (Updated)",
        "enabled": False
    }
    response = requests.put(f"{BASE_URL}/api/workstages/{workstage_id}", json=update_data)
    print_response(response, f"UPDATE WORKSTAGE {workstage_id}")


def test_delete_workstage(workstage_id: int):
    """Test DELETE /api/workstages/{id}"""
    response = requests.delete(f"{BASE_URL}/api/workstages/{workstage_id}")
    print_response(response, f"DELETE WORKSTAGE {workstage_id}")


def test_invalid_workstage_code(line_id: int):
    """Test invalid workstage_code format"""
    workstage_data = {
        "line_id": line_id,
        "workstage_sequence": 2,
        "workstage_code": "INVALID",  # Wrong format
        "workstage_name": "Invalid Workstage",
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/workstages", json=workstage_data)
    print_response(response, "CREATE WORKSTAGE WITH INVALID CODE (Should fail)")


def test_invalid_line_id():
    """Test with non-existent line_id"""
    workstage_data = {
        "line_id": 99999,
        "workstage_sequence": 1,
        "workstage_code": "KRCWO12ELOB102",
        "workstage_name": "Test Workstage",
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/workstages", json=workstage_data)
    print_response(response, "CREATE WORKSTAGE WITH INVALID LINE_ID (Should fail)")


def test_duplicate_workstage_code(line_id: int):
    """Test duplicate workstage_code error"""
    workstage_data = {
        "line_id": line_id,
        "workstage_sequence": 2,
        "workstage_code": "KRCWO12ELOA101",  # Same as first workstage
        "workstage_name": "Duplicate Workstage",
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/workstages", json=workstage_data)
    print_response(response, "CREATE DUPLICATE WORKSTAGE (Should fail)")


def delete_test_line(line_id: int):
    """Delete test line (cleanup)"""
    response = requests.delete(f"{BASE_URL}/api/lines/{line_id}")
    print_response(response, f"DELETE TEST LINE {line_id}")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("WORKSTAGES API TEST SUITE")
    print("=" * 60)

    # Test server health
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_response(response, "SERVER HEALTH CHECK")
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server. Is it running?")
        print("   Start with: cd backend && python -m uvicorn src.api.main:app --reload")
        return

    # Create test line
    line_id = create_test_line()
    if not line_id:
        print("\n❌ ERROR: Failed to create test line")
        return

    # Test CRUD operations
    workstage_id = test_create_workstage(line_id)

    if workstage_id:
        test_list_workstages()
        test_list_workstages(line_id)
        test_get_workstage(workstage_id)
        test_update_workstage(workstage_id)

    # Test error cases
    test_invalid_workstage_code(line_id)
    test_invalid_line_id()
    test_duplicate_workstage_code(line_id)

    # Cleanup
    if workstage_id:
        test_delete_workstage(workstage_id)
    delete_test_line(line_id)

    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()

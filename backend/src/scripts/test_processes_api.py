"""
Test script for Processes API

Feature 5: Database Management REST API
Tests CRUD operations on /api/processes endpoints
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
    """Create a test line for process testing"""
    line_data = {
        "line_code": "TESTLINE",
        "line_name": "Test Line for Processes",
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/lines", json=line_data)
    if response.status_code == 201:
        return response.json()["id"]
    return None


def test_create_process(line_id: int):
    """Test POST /api/processes"""
    process_data = {
        "line_id": line_id,
        "process_sequence": 1,
        "process_code": "KRCWO12ELOA101",  # 14-char format
        "process_name": "Electroplating Process A",
        "equipment_type": "ELO",
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/processes", json=process_data)
    print_response(response, "CREATE PROCESS")
    if response.status_code == 201:
        return response.json()["id"]
    return None


def test_list_processes(line_id: Optional[int] = None):
    """Test GET /api/processes"""
    url = f"{BASE_URL}/api/processes?page=1&limit=10"
    if line_id:
        url += f"&line_id={line_id}"
    response = requests.get(url)
    print_response(response, f"LIST PROCESSES (line_id={line_id if line_id else 'all'})")


def test_get_process(process_id: int):
    """Test GET /api/processes/{id}"""
    response = requests.get(f"{BASE_URL}/api/processes/{process_id}")
    print_response(response, f"GET PROCESS {process_id}")


def test_update_process(process_id: int):
    """Test PUT /api/processes/{id}"""
    update_data = {
        "process_name": "Electroplating Process A (Updated)",
        "enabled": False
    }
    response = requests.put(f"{BASE_URL}/api/processes/{process_id}", json=update_data)
    print_response(response, f"UPDATE PROCESS {process_id}")


def test_delete_process(process_id: int):
    """Test DELETE /api/processes/{id}"""
    response = requests.delete(f"{BASE_URL}/api/processes/{process_id}")
    print_response(response, f"DELETE PROCESS {process_id}")


def test_invalid_process_code(line_id: int):
    """Test invalid process_code format"""
    process_data = {
        "line_id": line_id,
        "process_sequence": 2,
        "process_code": "INVALID",  # Wrong format
        "process_name": "Invalid Process",
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/processes", json=process_data)
    print_response(response, "CREATE PROCESS WITH INVALID CODE (Should fail)")


def test_invalid_line_id():
    """Test with non-existent line_id"""
    process_data = {
        "line_id": 99999,
        "process_sequence": 1,
        "process_code": "KRCWO12ELOB102",
        "process_name": "Test Process",
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/processes", json=process_data)
    print_response(response, "CREATE PROCESS WITH INVALID LINE_ID (Should fail)")


def test_duplicate_process_code(line_id: int):
    """Test duplicate process_code error"""
    process_data = {
        "line_id": line_id,
        "process_sequence": 2,
        "process_code": "KRCWO12ELOA101",  # Same as first process
        "process_name": "Duplicate Process",
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/processes", json=process_data)
    print_response(response, "CREATE DUPLICATE PROCESS (Should fail)")


def delete_test_line(line_id: int):
    """Delete test line (cleanup)"""
    response = requests.delete(f"{BASE_URL}/api/lines/{line_id}")
    print_response(response, f"DELETE TEST LINE {line_id}")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("PROCESSES API TEST SUITE")
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
    process_id = test_create_process(line_id)

    if process_id:
        test_list_processes()
        test_list_processes(line_id)
        test_get_process(process_id)
        test_update_process(process_id)

    # Test error cases
    test_invalid_process_code(line_id)
    test_invalid_line_id()
    test_duplicate_process_code(line_id)

    # Cleanup
    if process_id:
        test_delete_process(process_id)
    delete_test_line(line_id)

    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()

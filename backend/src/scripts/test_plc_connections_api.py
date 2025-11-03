"""
Test script for PLC Connections API

Feature 5: Database Management REST API
Tests CRUD operations on /api/plc-connections endpoints including connectivity testing
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
    """Create a test line"""
    line_data = {
        "line_code": "PLCTEST",
        "line_name": "Test Line for PLCs",
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/lines", json=line_data)
    if response.status_code == 201:
        return response.json()["id"]
    return None


def create_test_process(line_id: int):
    """Create a test process"""
    process_data = {
        "line_id": line_id,
        "process_sequence": 1,
        "process_code": "KRCWO12PLCA201",
        "process_name": "Test Process for PLCs",
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/processes", json=process_data)
    if response.status_code == 201:
        return response.json()["id"]
    return None


def test_create_plc_connection(process_id: int):
    """Test POST /api/plc-connections"""
    plc_data = {
        "process_id": process_id,
        "plc_code": "PLC001",
        "ip_address": "192.168.1.100",
        "port": 5000,
        "network_no": 0,
        "station_no": 0,
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/plc-connections", json=plc_data)
    print_response(response, "CREATE PLC CONNECTION")
    if response.status_code == 201:
        return response.json()["id"]
    return None


def test_list_plc_connections(process_id: Optional[int] = None):
    """Test GET /api/plc-connections"""
    url = f"{BASE_URL}/api/plc-connections?page=1&limit=10"
    if process_id:
        url += f"&process_id={process_id}"
    response = requests.get(url)
    print_response(response, f"LIST PLC CONNECTIONS (process_id={process_id if process_id else 'all'})")


def test_get_plc_connection(plc_id: int):
    """Test GET /api/plc-connections/{id}"""
    response = requests.get(f"{BASE_URL}/api/plc-connections/{plc_id}")
    print_response(response, f"GET PLC CONNECTION {plc_id}")


def test_plc_connection_test(plc_id: int):
    """Test POST /api/plc-connections/{id}/test"""
    response = requests.post(f"{BASE_URL}/api/plc-connections/{plc_id}/test")
    print_response(response, f"TEST PLC CONNECTION {plc_id}")


def test_update_plc_connection(plc_id: int):
    """Test PUT /api/plc-connections/{id}"""
    update_data = {
        "ip_address": "192.168.1.101",
        "enabled": False
    }
    response = requests.put(f"{BASE_URL}/api/plc-connections/{plc_id}", json=update_data)
    print_response(response, f"UPDATE PLC CONNECTION {plc_id}")


def test_delete_plc_connection(plc_id: int):
    """Test DELETE /api/plc-connections/{id}"""
    response = requests.delete(f"{BASE_URL}/api/plc-connections/{plc_id}")
    print_response(response, f"DELETE PLC CONNECTION {plc_id}")


def test_invalid_ip_address(process_id: int):
    """Test invalid IP address format"""
    plc_data = {
        "process_id": process_id,
        "plc_code": "PLC002",
        "ip_address": "999.999.999.999",  # Invalid IP
        "port": 5000,
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/plc-connections", json=plc_data)
    print_response(response, "CREATE PLC WITH INVALID IP (Should fail)")


def test_invalid_process_id():
    """Test with non-existent process_id"""
    plc_data = {
        "process_id": 99999,
        "plc_code": "PLC003",
        "ip_address": "192.168.1.102",
        "port": 5000,
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/plc-connections", json=plc_data)
    print_response(response, "CREATE PLC WITH INVALID PROCESS_ID (Should fail)")


def test_duplicate_plc_code(process_id: int):
    """Test duplicate plc_code error"""
    plc_data = {
        "process_id": process_id,
        "plc_code": "PLC001",  # Same as first PLC
        "ip_address": "192.168.1.103",
        "port": 5000,
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/plc-connections", json=plc_data)
    print_response(response, "CREATE DUPLICATE PLC CODE (Should fail)")


def cleanup(line_id: int, process_id: int):
    """Cleanup test data"""
    requests.delete(f"{BASE_URL}/api/processes/{process_id}")
    requests.delete(f"{BASE_URL}/api/lines/{line_id}")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("PLC CONNECTIONS API TEST SUITE")
    print("=" * 60)

    # Test server health
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_response(response, "SERVER HEALTH CHECK")
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server. Is it running?")
        print("   Start with: cd backend && python -m uvicorn src.api.main:app --reload")
        return

    # Create test dependencies
    line_id = create_test_line()
    if not line_id:
        print("\n❌ ERROR: Failed to create test line")
        return

    process_id = create_test_process(line_id)
    if not process_id:
        print("\n❌ ERROR: Failed to create test process")
        cleanup(line_id, None)
        return

    # Test CRUD operations
    plc_id = test_create_plc_connection(process_id)

    if plc_id:
        test_list_plc_connections()
        test_list_plc_connections(process_id)
        test_get_plc_connection(plc_id)
        test_plc_connection_test(plc_id)
        test_update_plc_connection(plc_id)

    # Test error cases
    test_invalid_ip_address(process_id)
    test_invalid_process_id()
    test_duplicate_plc_code(process_id)

    # Cleanup
    if plc_id:
        test_delete_plc_connection(plc_id)
    cleanup(line_id, process_id)

    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()

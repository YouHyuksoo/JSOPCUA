"""
Test script for Polling Groups API

Feature 5: Database Management REST API
Tests CRUD operations on /api/polling-groups endpoints
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


def setup_test_data():
    """Create test line, process, and PLC for polling group testing"""
    print("\n" + "=" * 60)
    print("SETUP: Creating test data")
    print("=" * 60)

    # Create test line
    line_data = {
        "line_code": "PGTEST",
        "line_name": "Polling Group Test Line",
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/lines", json=line_data)
    if response.status_code != 201:
        print(f"❌ Failed to create test line")
        return None, None, None

    line_id = response.json()["id"]
    print(f"✓ Created test line (id={line_id})")

    # Create test process
    process_data = {
        "line_id": line_id,
        "process_sequence": 1,
        "process_code": "KRCWO12POLG101",
        "process_name": "Polling Group Test Process",
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/processes", json=process_data)
    if response.status_code != 201:
        print(f"❌ Failed to create test process")
        return line_id, None, None

    process_id = response.json()["id"]
    print(f"✓ Created test process (id={process_id})")

    # Create test PLC
    plc_data = {
        "process_id": process_id,
        "plc_code": "PGPLC001",
        "ip_address": "192.168.1.150",
        "port": 5000,
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/plc-connections", json=plc_data)
    if response.status_code != 201:
        print(f"❌ Failed to create test PLC")
        return line_id, process_id, None

    plc_id = response.json()["id"]
    print(f"✓ Created test PLC (id={plc_id})")

    return line_id, process_id, plc_id


def test_create_polling_group_fixed(plc_id: int):
    """Test POST /api/polling-groups (FIXED mode)"""
    group_data = {
        "group_name": "FIXED Polling Group 1",
        "line_code": "LINE01",
        "process_code": "PROC01",
        "plc_id": plc_id,
        "mode": "FIXED",
        "interval_ms": 1000,
        "priority": "NORMAL",
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/polling-groups", json=group_data)
    print_response(response, "CREATE POLLING GROUP (FIXED mode)")
    if response.status_code == 201:
        return response.json()["id"]
    return None


def test_create_polling_group_handshake(plc_id: int):
    """Test POST /api/polling-groups (HANDSHAKE mode)"""
    group_data = {
        "group_name": "HANDSHAKE Polling Group 1",
        "plc_id": plc_id,
        "mode": "HANDSHAKE",
        "interval_ms": 500,
        "trigger_bit_address": "M100",
        "trigger_bit_offset": 0,
        "auto_reset_trigger": True,
        "priority": "HIGH",
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/polling-groups", json=group_data)
    print_response(response, "CREATE POLLING GROUP (HANDSHAKE mode)")
    if response.status_code == 201:
        return response.json()["id"]
    return None


def test_list_polling_groups(plc_id: Optional[int] = None):
    """Test GET /api/polling-groups"""
    url = f"{BASE_URL}/api/polling-groups?page=1&limit=10"
    if plc_id:
        url += f"&plc_id={plc_id}"
    response = requests.get(url)
    print_response(response, f"LIST POLLING GROUPS (plc_id={plc_id if plc_id else 'all'})")


def test_get_polling_group(group_id: int):
    """Test GET /api/polling-groups/{id}"""
    response = requests.get(f"{BASE_URL}/api/polling-groups/{group_id}")
    print_response(response, f"GET POLLING GROUP {group_id}")


def test_get_polling_group_tags(group_id: int):
    """Test GET /api/polling-groups/{id}/tags"""
    response = requests.get(f"{BASE_URL}/api/polling-groups/{group_id}/tags")
    print_response(response, f"GET POLLING GROUP {group_id} TAGS")


def test_update_polling_group(group_id: int):
    """Test PUT /api/polling-groups/{id}"""
    update_data = {
        "group_name": "Updated Polling Group",
        "interval_ms": 2000,
        "enabled": False
    }
    response = requests.put(f"{BASE_URL}/api/polling-groups/{group_id}", json=update_data)
    print_response(response, f"UPDATE POLLING GROUP {group_id}")


def test_delete_polling_group(group_id: int):
    """Test DELETE /api/polling-groups/{id}"""
    response = requests.delete(f"{BASE_URL}/api/polling-groups/{group_id}")
    print_response(response, f"DELETE POLLING GROUP {group_id}")


def test_invalid_handshake_mode(plc_id: int):
    """Test HANDSHAKE mode without trigger_bit_address (should fail)"""
    group_data = {
        "group_name": "Invalid HANDSHAKE Group",
        "plc_id": plc_id,
        "mode": "HANDSHAKE",
        "interval_ms": 1000,
        # Missing trigger_bit_address
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/polling-groups", json=group_data)
    print_response(response, "CREATE HANDSHAKE WITHOUT TRIGGER (Should fail)")


def test_invalid_plc_id():
    """Test with non-existent plc_id"""
    group_data = {
        "group_name": "Invalid PLC Group",
        "plc_id": 99999,
        "mode": "FIXED",
        "interval_ms": 1000,
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/polling-groups", json=group_data)
    print_response(response, "CREATE GROUP WITH INVALID PLC_ID (Should fail)")


def cleanup(line_id, process_id, plc_id):
    """Cleanup test data"""
    if plc_id:
        requests.delete(f"{BASE_URL}/api/plc-connections/{plc_id}")
    if process_id:
        requests.delete(f"{BASE_URL}/api/processes/{process_id}")
    if line_id:
        requests.delete(f"{BASE_URL}/api/lines/{line_id}")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("POLLING GROUPS API TEST SUITE")
    print("=" * 60)

    # Test server health
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_response(response, "SERVER HEALTH CHECK")
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server. Is it running?")
        print("   Start with: cd backend && python -m uvicorn src.api.main:app --reload")
        return

    # Setup test data
    line_id, process_id, plc_id = setup_test_data()
    if not (line_id and process_id and plc_id):
        print("\n❌ Failed to setup test data. Aborting.")
        return

    # Test CRUD operations
    fixed_group_id = test_create_polling_group_fixed(plc_id)
    handshake_group_id = test_create_polling_group_handshake(plc_id)

    if fixed_group_id:
        test_list_polling_groups()
        test_list_polling_groups(plc_id)
        test_get_polling_group(fixed_group_id)
        test_get_polling_group_tags(fixed_group_id)
        test_update_polling_group(fixed_group_id)

    # Test error cases
    test_invalid_handshake_mode(plc_id)
    test_invalid_plc_id()

    # Cleanup
    if fixed_group_id:
        test_delete_polling_group(fixed_group_id)
    if handshake_group_id:
        test_delete_polling_group(handshake_group_id)

    cleanup(line_id, process_id, plc_id)

    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()

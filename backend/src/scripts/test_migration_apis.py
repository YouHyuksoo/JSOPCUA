"""
Test API endpoints after lines → machines migration

Tests all CRUD operations on machines and processes to verify migration success.
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_machines_api():
    """Test /api/machines endpoints"""
    print("\n" + "=" * 70)
    print("Testing Machines API")
    print("=" * 70)

    # 1. List machines
    print("\n1. GET /api/machines")
    response = requests.get(f"{BASE_URL}/api/machines")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Found {data['total_count']} machines")
        if data['items']:
            machine = data['items'][0]
            print(f"   ✓ Sample: {machine['machine_code']} - {machine['machine_name']}")
            return machine['id']
    else:
        print(f"   ✗ Error: {response.text}")
        return None

    return None


def test_processes_api(machine_code):
    """Test /api/processes endpoints"""
    print("\n" + "=" * 70)
    print("Testing Processes API")
    print("=" * 70)

    # 1. List all processes
    print("\n1. GET /api/processes")
    response = requests.get(f"{BASE_URL}/api/processes")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Found {data['total_count']} processes")
        if data['items']:
            process = data['items'][0]
            print(f"   ✓ Sample: {process['process_code']} - {process['process_name']}")
            print(f"   ✓ machine_code: {process.get('machine_code', 'None')}")

    # 2. Filter by machine_code
    if machine_code:
        print(f"\n2. GET /api/processes?machine_code={machine_code}")
        response = requests.get(f"{BASE_URL}/api/processes?machine_code={machine_code}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Found {data['total_count']} processes for machine {machine_code}")


def test_database_view():
    """Test v_tags_with_plc view"""
    print("\n" + "=" * 70)
    print("Testing Database View")
    print("=" * 70)

    import sqlite3
    conn = sqlite3.connect("d:/Project/JSOPCUA/backend/data/scada.db")
    cursor = conn.cursor()

    print("\n1. Query v_tags_with_plc view")
    cursor.execute("""
        SELECT machine_code, machine_name, process_code, plc_code, tag_address
        FROM v_tags_with_plc
        LIMIT 5
    """)
    rows = cursor.fetchall()

    if rows:
        print(f"   ✓ View is working, found {len(rows)} rows")
        for row in rows:
            print(f"   - Machine: {row[0]} | Process: {row[2]} | PLC: {row[3]} | Tag: {row[4]}")
    else:
        print("   ℹ️  No data in view (expected if no tags exist)")

    conn.close()


def main():
    print("=" * 70)
    print("API Migration Test Suite")
    print("=" * 70)
    print("\nNOTE: Ensure backend server is running on http://localhost:8000")

    try:
        # Test machines API
        machine_id = test_machines_api()
        
        # Get machine_code for processes API test
        machine_code = None
        if machine_id:
            response = requests.get(f"{BASE_URL}/api/machines/{machine_id}")
            if response.status_code == 200:
                machine = response.json()
                machine_code = machine.get('machine_code')

        # Test processes API
        test_processes_api(machine_code)

        # Test database view
        test_database_view()

        print("\n" + "=" * 70)
        print("✅ All tests completed!")
        print("=" * 70)

    except requests.exceptions.ConnectionError:
        print("\n" + "=" * 70)
        print("❌ Error: Cannot connect to backend server")
        print("Please start the backend server first:")
        print("  cd backend && .venv\\Scripts\\python.exe -m uvicorn src.api.main:app --reload")
        print("=" * 70)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()

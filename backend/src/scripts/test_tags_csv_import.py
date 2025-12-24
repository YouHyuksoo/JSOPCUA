"""
Test script for Tags CSV Import

Feature 5: Database Management REST API
Tests CSV import functionality including performance validation
"""

import requests
import json
import time
import subprocess
import sys

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
    """Create test lines, processes, and PLCs for CSV import"""
    print("\n" + "=" * 60)
    print("SETUP: Creating test data for CSV import")
    print("=" * 60)

    # Create test line
    line_data = {
        "line_code": "CSVTEST",
        "line_name": "CSV Import Test Line",
        "enabled": True
    }
    response = requests.post(f"{BASE_URL}/api/lines", json=line_data)
    if response.status_code != 201:
        print(f"❌ Failed to create test line: {response.text}")
        return None, None, None

    line_id = response.json()["id"]
    print(f"✓ Created test line (id={line_id})")

    # Create 3 test processes
    process_codes = ['KRCWO12ELOA101', 'KRCWO12ELOB102', 'KRCWO12ELOC103']
    process_ids = []

    for i, code in enumerate(process_codes):
        process_data = {
            "line_id": line_id,
            "process_sequence": i + 1,
            "process_code": code,
            "process_name": f"CSV Test Process {i+1}",
            "enabled": True
        }
        response = requests.post(f"{BASE_URL}/api/processes", json=process_data)
        if response.status_code != 201:
            print(f"❌ Failed to create process {code}: {response.text}")
            return line_id, None, None

        process_ids.append(response.json()["id"])
        print(f"✓ Created test process {code} (id={process_ids[-1]})")

    # Create 3 test PLCs
    plc_codes = ['PLC001', 'PLC002', 'PLC003']
    plc_ids = []

    for i, (plc_code, process_id) in enumerate(zip(plc_codes, process_ids)):
        plc_data = {
            "process_id": process_id,
            "plc_code": plc_code,
            "ip_address": f"192.168.1.{100 + i}",
            "port": 5000,
            "enabled": True
        }
        response = requests.post(f"{BASE_URL}/api/plc-connections", json=plc_data)
        if response.status_code != 201:
            print(f"❌ Failed to create PLC {plc_code}: {response.text}")
            return line_id, process_ids, None

        plc_ids.append(response.json()["id"])
        print(f"✓ Created test PLC {plc_code} (id={plc_ids[-1]})")

    print("\n✓ Test data setup complete")
    return line_id, process_ids, plc_ids


def generate_sample_csvs():
    """Generate sample CSV files"""
    print("\n" + "=" * 60)
    print("Generating sample CSV files")
    print("=" * 60)

    try:
        result = subprocess.run(
            [sys.executable, "backend/src/scripts/generate_sample_csv.py"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Failed to generate CSV files: {e}")
        return False


def test_valid_csv_import():
    """Test importing valid CSV file (1000 tags)"""
    print("\n" + "=" * 60)
    print("TEST: Import 1000 valid tags from CSV")
    print("=" * 60)

    try:
        with open('backend/data/sample_tags_1000.csv', 'rb') as f:
            files = {'file': ('sample_tags_1000.csv', f, 'text/csv')}

            start_time = time.time()
            response = requests.post(f"{BASE_URL}/api/tags/import-csv", files=files)
            elapsed_time = time.time() - start_time

            print_response(response, "CSV IMPORT (1000 tags)")
            print(f"\n⏱  Import time: {elapsed_time:.2f} seconds")

            if response.status_code == 200:
                result = response.json()
                print(f"\n✓ Import successful:")
                print(f"  - Success: {result['success_count']} tags")
                print(f"  - Failures: {result['failure_count']} tags")

                # Performance check (<30s for 3000 tags = <10s for 1000 tags)
                if elapsed_time < 10:
                    print(f"  - Performance: ✓ PASS (<10s)")
                else:
                    print(f"  - Performance: ⚠ SLOW (>10s)")

                return result['success_count']

    except FileNotFoundError:
        print("❌ Sample CSV file not found. Run generate_sample_csv.py first.")
        return 0
    except Exception as e:
        print(f"❌ Error during import: {e}")
        return 0


def test_error_csv_import():
    """Test importing CSV with errors"""
    print("\n" + "=" * 60)
    print("TEST: Import CSV with errors")
    print("=" * 60)

    try:
        with open('backend/data/sample_tags_errors.csv', 'rb') as f:
            files = {'file': ('sample_tags_errors.csv', f, 'text/csv')}
            response = requests.post(f"{BASE_URL}/api/tags/import-csv", files=files)

            print_response(response, "CSV IMPORT (with errors)")

            if response.status_code == 200:
                result = response.json()
                print(f"\n✓ Import completed with errors:")
                print(f"  - Success: {result['success_count']} tags")
                print(f"  - Failures: {result['failure_count']} tags")
                print(f"\n  Error details:")
                for err in result['errors']:
                    print(f"    Row {err['row']}: {err['error']}")

    except FileNotFoundError:
        print("❌ Sample CSV file not found. Run generate_sample_csv.py first.")
    except Exception as e:
        print(f"❌ Error during import: {e}")


def test_list_tags():
    """Test listing imported tags"""
    print("\n" + "=" * 60)
    print("TEST: List imported tags")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/api/tags?page=1&limit=10")
    print_response(response, "LIST TAGS (first 10)")


def test_tag_crud():
    """Test basic tag CRUD operations"""
    print("\n" + "=" * 60)
    print("TEST: Tag CRUD operations")
    print("=" * 60)

    # Get first tag to test
    response = requests.get(f"{BASE_URL}/api/tags?page=1&limit=1")
    if response.status_code == 200 and response.json()['total_count'] > 0:
        tag_id = response.json()['items'][0]['id']

        # Test GET single tag
        response = requests.get(f"{BASE_URL}/api/tags/{tag_id}")
        print_response(response, f"GET TAG {tag_id}")

        # Test UPDATE tag
        update_data = {"tag_name": "Updated_Tag_Name", "enabled": False}
        response = requests.put(f"{BASE_URL}/api/tags/{tag_id}", json=update_data)
        print_response(response, f"UPDATE TAG {tag_id}")


def cleanup_test_data(line_id, process_ids, plc_ids):
    """Cleanup all test data"""
    print("\n" + "=" * 60)
    print("CLEANUP: Deleting test data")
    print("=" * 60)

    # Delete all tags
    response = requests.get(f"{BASE_URL}/api/tags?limit=1000")
    if response.status_code == 200:
        tags = response.json()['items']
        if tags:
            tag_ids = [tag['id'] for tag in tags]
            response = requests.delete(f"{BASE_URL}/api/tags/batch", json=tag_ids)
            print(f"✓ Deleted {len(tag_ids)} tags")

    # Delete PLCs
    if plc_ids:
        for plc_id in plc_ids:
            requests.delete(f"{BASE_URL}/api/plc-connections/{plc_id}")
        print(f"✓ Deleted {len(plc_ids)} PLCs")

    # Delete processes
    if process_ids:
        for process_id in process_ids:
            requests.delete(f"{BASE_URL}/api/processes/{process_id}")
        print(f"✓ Deleted {len(process_ids)} processes")

    # Delete line
    if line_id:
        requests.delete(f"{BASE_URL}/api/lines/{line_id}")
        print(f"✓ Deleted test line")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("TAGS CSV IMPORT TEST SUITE")
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
    line_id, process_ids, plc_ids = setup_test_data()
    if not (line_id and process_ids and plc_ids):
        print("\n❌ Failed to setup test data. Aborting.")
        return

    # Generate sample CSV files
    if not generate_sample_csvs():
        print("\n❌ Failed to generate CSV files. Aborting.")
        cleanup_test_data(line_id, process_ids, plc_ids)
        return

    # Test CSV imports
    success_count = test_valid_csv_import()
    test_error_csv_import()

    # Test tag operations
    if success_count > 0:
        test_list_tags()
        test_tag_crud()

    # Cleanup
    cleanup_test_data(line_id, process_ids, plc_ids)

    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()

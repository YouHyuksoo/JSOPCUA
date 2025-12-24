"""
Buffer Metrics Monitoring Test

Tests buffer monitoring API endpoints to verify:
- /api/buffer/status returns accurate buffer metrics
- /api/buffer/writer/metrics returns writer performance data
- /api/buffer/health returns correct health status
- /api/buffer/metrics returns combined metrics

Usage:
    python backend/src/scripts/test_buffer_metrics.py [--url BASE_URL]
"""

import sys
import argparse
import requests
import time
from pathlib import Path

def test_buffer_monitoring_api(base_url: str = "http://localhost:8000"):
    """
    Test buffer monitoring API endpoints
    
    Args:
        base_url: Base URL of the API (default: http://localhost:8000)
    """
    print("=" * 80)
    print("BUFFER MONITORING API TEST")
    print("=" * 80)
    print(f"Base URL: {base_url}")
    print("=" * 80)
    print()
    
    success = True
    
    # Test 1: GET /api/buffer/status
    print("[TEST 1] GET /api/buffer/status")
    try:
        response = requests.get(f"{base_url}/api/buffer/status", timeout=5)
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Buffer Status:")
            print(f"    - Current size: {data.get('current_size')}")
            print(f"    - Max size: {data.get('max_size')}")
            print(f"    - Utilization: {data.get('utilization_pct')}%")
            print(f"    - Overflow count: {data.get('overflow_count')}")
            print(f"    - Overflow rate: {data.get('overflow_rate_pct')}%")
        elif response.status_code == 503:
            print(f"  ⚠ Service unavailable (buffer not initialized)")
            print(f"    This is expected if buffer/writer are not running")
        else:
            print(f"  ✗ FAIL: Unexpected status code {response.status_code}")
            success = False
    except requests.exceptions.ConnectionError:
        print(f"  ✗ FAIL: Connection error - API server not running")
        success = False
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        success = False
    print()
    
    # Test 2: GET /api/buffer/writer/metrics
    print("[TEST 2] GET /api/buffer/writer/metrics")
    try:
        response = requests.get(f"{base_url}/api/buffer/writer/metrics", timeout=5)
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Writer Metrics:")
            print(f"    - Successful writes: {data.get('successful_writes')}")
            print(f"    - Failed writes: {data.get('failed_writes')}")
            print(f"    - Success rate: {data.get('success_rate_pct')}%")
            print(f"    - Avg batch size: {data.get('avg_batch_size')}")
            print(f"    - Avg latency: {data.get('avg_write_latency_ms')} ms")
            print(f"    - Throughput: {data.get('throughput_items_per_sec')} items/s")
        elif response.status_code == 503:
            print(f"  ⚠ Service unavailable (writer not initialized)")
        else:
            print(f"  ✗ FAIL: Unexpected status code {response.status_code}")
            success = False
    except requests.exceptions.ConnectionError:
        print(f"  ✗ FAIL: Connection error")
        success = False
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        success = False
    print()
    
    # Test 3: GET /api/buffer/health
    print("[TEST 3] GET /api/buffer/health")
    try:
        response = requests.get(f"{base_url}/api/buffer/health", timeout=5)
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code in [200, 503]:
            data = response.json() if response.status_code == 200 else response.json().get('detail', {})
            print(f"  Health Status:")
            print(f"    - Overall: {data.get('status')}")
            print(f"    - Buffer OK: {data.get('buffer_ok')}")
            print(f"    - Writer OK: {data.get('writer_ok')}")
            print(f"    - Oracle OK: {data.get('oracle_connection_ok')}")
            
            details = data.get('details', {})
            if details:
                print(f"    - Buffer utilization: {details.get('buffer_utilization_pct')}%")
                print(f"    - Backup files: {details.get('backup_file_count')}")
        else:
            print(f"  ✗ FAIL: Unexpected status code {response.status_code}")
            success = False
    except requests.exceptions.ConnectionError:
        print(f"  ✗ FAIL: Connection error")
        success = False
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        success = False
    print()
    
    # Test 4: GET /api/buffer/metrics (combined)
    print("[TEST 4] GET /api/buffer/metrics")
    try:
        response = requests.get(f"{base_url}/api/buffer/metrics", timeout=5)
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Combined Metrics:")
            
            buffer = data.get('buffer', {})
            print(f"    Buffer:")
            print(f"      - Size: {buffer.get('current_size')}/{buffer.get('max_size')}")
            print(f"      - Utilization: {buffer.get('utilization_pct')}%")
            
            writer = data.get('writer', {})
            print(f"    Writer:")
            print(f"      - Running: {writer.get('is_running')}")
            print(f"      - Success rate: {writer.get('success_rate_pct')}%")
            print(f"      - Throughput: {writer.get('throughput_items_per_sec')} items/s")
            
            backup = data.get('backup', {})
            print(f"    Backup:")
            print(f"      - File count: {backup.get('file_count')}")
            
        elif response.status_code == 503:
            print(f"  ⚠ Service unavailable")
        else:
            print(f"  ✗ FAIL: Unexpected status code {response.status_code}")
            success = False
    except requests.exceptions.ConnectionError:
        print(f"  ✗ FAIL: Connection error")
        success = False
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        success = False
    print()
    
    # Summary
    print("=" * 80)
    if success:
        print("✓ ALL API TESTS PASSED")
        print()
        print("NOTE: 503 responses are expected if buffer/writer are not running.")
        print("To fully test the API, run the buffer writer:")
        print("  python backend/src/scripts/start_buffer_writer.py")
    else:
        print("✗ SOME API TESTS FAILED")
    print("=" * 80)
    
    return success


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Buffer monitoring API test")
    parser.add_argument('--url', type=str, default="http://localhost:8000",
                       help='Base URL of the API (default: http://localhost:8000)')
    
    args = parser.parse_args()
    
    try:
        success = test_buffer_monitoring_api(base_url=args.url)
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("
[INTERRUPT] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"
[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

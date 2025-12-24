"""
Test Script for Polling Failure Logging

폴링 실패 로그 기능 테스트용 스크립트
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from src.polling.polling_logger import get_failure_logger
from src.config.logging_config import initialize_logging


def test_connection_failure():
    """Test logging connection failure"""
    print("\n=== Test 1: Connection Failure ===")

    logger = get_failure_logger()
    logger.log_connection_failure(
        plc_code="PLC01",
        group_name="Group1_Elevator",
        ip_address="192.168.1.10",
        port=5010,
        error_message="Connection refused: PLC not responding",
        connection_timeout=5
    )

    print("✓ Connection failure logged")


def test_read_failure():
    """Test logging read failure"""
    print("\n=== Test 2: Read Failure ===")

    logger = get_failure_logger()
    logger.log_read_failure(
        plc_code="PLC02",
        group_name="Group2_Welding",
        tag_addresses=["D100", "D200", "D300", "W100"],
        error_message="Read error: Invalid response code 0x4001",
        poll_duration_ms=1250.5,
        response_code="0x4001"
    )

    print("✓ Read failure logged")


def test_timeout_failure():
    """Test logging timeout failure"""
    print("\n=== Test 3: Timeout Failure ===")

    logger = get_failure_logger()
    logger.log_timeout_failure(
        plc_code="PLC03",
        group_name="Group3_Press",
        tag_addresses=["M100", "M101", "M102"],
        timeout_ms=5000.0
    )

    print("✓ Timeout failure logged")


def test_custom_failure():
    """Test logging custom failure with all parameters"""
    print("\n=== Test 4: Custom Failure (Full Parameters) ===")

    logger = get_failure_logger()
    logger.log_failure(
        plc_code="PLC01",
        group_name="Group1_Elevator",
        error_type="DATA_CORRUPTION",
        error_message="Received corrupted data: checksum mismatch",
        request_data={
            "command": "BATCH_READ",
            "start_address": "D100",
            "count": 10
        },
        response_data={
            "status_code": "0x0000",
            "data_length": 20,
            "checksum": "0xABCD",
            "expected_checksum": "0x1234"
        },
        tag_addresses=["D100", "D101", "D102"],
        poll_duration_ms=856.3,
        retry_count=2
    )

    print("✓ Custom failure logged with full details")


def check_log_files():
    """Check created log files"""
    print("\n=== Checking Log Files ===")

    from datetime import datetime
    today = datetime.now().strftime("%Y%m%d")
    log_dir = Path("logs/polling_failures") / today

    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        print(f"✓ Found {len(log_files)} log files in {log_dir}")
        for log_file in log_files:
            print(f"  - {log_file.name} ({log_file.stat().st_size} bytes)")
    else:
        print(f"✗ Log directory not found: {log_dir}")


def main():
    print("=" * 70)
    print("Polling Failure Logging Test")
    print("=" * 70)

    # Initialize logging
    initialize_logging()

    # Run tests
    test_connection_failure()
    test_read_failure()
    test_timeout_failure()
    test_custom_failure()

    # Check results
    check_log_files()

    print("\n" + "=" * 70)
    print("All tests completed!")
    print("Check logs/polling_failures/YYYYMMDD/ for log files")
    print("=" * 70)


if __name__ == "__main__":
    main()

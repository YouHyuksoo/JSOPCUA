"""
Test Script for Terminal Logging with Colors and Level Control

터미널 로그 기능 테스트용 스크립트
- 컬러풀한 로그 출력
- 환경변수 LOG_LEVEL 제어
- 런타임 로그 레벨 변경
"""

import sys
import logging
import time
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from src.config.logging_config import initialize_logging, set_console_log_level


def test_all_log_levels():
    """Test all log levels with colorful output"""
    print("\n" + "=" * 70)
    print("Test 1: All Log Levels (Colorful Output)")
    print("=" * 70)

    logger = logging.getLogger("test.terminal")

    logger.debug("DEBUG: Detailed diagnostic information")
    logger.info("INFO: General informational message")
    logger.warning("WARNING: Warning message - something unusual")
    logger.error("ERROR: Error occurred - operation failed")
    logger.critical("CRITICAL: Critical error - system unstable")

    print("\n✓ All log levels displayed with colors")


def test_environment_variable():
    """Test environment variable control"""
    print("\n" + "=" * 70)
    print("Test 2: Environment Variable Control")
    print("=" * 70)

    import os
    current_level = os.getenv('LOG_LEVEL', 'INFO')
    print(f"Current LOG_LEVEL environment variable: {current_level}")
    print("\nTo change log level, set environment variable before running:")
    print("  Windows: set LOG_LEVEL=DEBUG && python test_terminal_logging.py")
    print("  Linux/Mac: LOG_LEVEL=DEBUG python test_terminal_logging.py")
    print("\nAvailable levels: DEBUG, INFO, WARNING, ERROR, CRITICAL")

    logger = logging.getLogger("test.env")
    logger.debug("This DEBUG message only shows if LOG_LEVEL=DEBUG")
    logger.info("This INFO message shows at INFO level and above")
    logger.warning("This WARNING message shows at WARNING level and above")


def test_runtime_level_change():
    """Test runtime log level change"""
    print("\n" + "=" * 70)
    print("Test 3: Runtime Log Level Change")
    print("=" * 70)

    logger = logging.getLogger("test.runtime")

    print("\n[Current Level: INFO]")
    logger.debug("DEBUG: This won't show at INFO level")
    logger.info("INFO: This will show")

    print("\n[Changing level to DEBUG...]")
    set_console_log_level(logging.DEBUG)

    logger.debug("DEBUG: Now this DEBUG message shows!")
    logger.info("INFO: This still shows")

    print("\n[Changing level to ERROR...]")
    set_console_log_level(logging.ERROR)

    logger.info("INFO: This won't show at ERROR level")
    logger.error("ERROR: Only ERROR and above show now")

    print("\n[Resetting to INFO...]")
    set_console_log_level(logging.INFO)

    print("✓ Runtime level change working")


def test_polling_simulation():
    """Simulate polling logs with different scenarios"""
    print("\n" + "=" * 70)
    print("Test 4: Polling Simulation (Real-world Usage)")
    print("=" * 70)

    polling_logger = logging.getLogger("polling.engine")
    perf_logger = logging.getLogger("polling.performance")
    comm_logger = logging.getLogger("pymcprotocol")

    # Successful polling
    print("\n[Scenario 1: Successful Polling]")
    polling_logger.info("Starting polling group: Group1_Elevator")
    comm_logger.debug("Connecting to PLC01 at 192.168.1.10:5010")
    comm_logger.debug("Reading batch: ['D100', 'D200', 'D300']")
    perf_logger.info("Group=Group1_Elevator | PLC=PLC01 | Tags=3 | Time=125.50ms | Status=SUCCESS")
    polling_logger.info("Polling completed successfully: 3 tags read")

    time.sleep(0.5)

    # Connection failure
    print("\n[Scenario 2: Connection Failure]")
    polling_logger.warning("Attempting to connect to PLC02...")
    comm_logger.error("Connection timeout: PLC02 at 192.168.1.20:5010")
    polling_logger.error("Polling failed: Connection refused - PLC not responding")

    time.sleep(0.5)

    # Read error
    print("\n[Scenario 3: Read Error]")
    polling_logger.info("Starting polling group: Group3_Press")
    comm_logger.debug("Connected to PLC03")
    comm_logger.error("Invalid response code: 0x4001")
    polling_logger.error("Read error: Invalid response from PLC")

    time.sleep(0.5)

    # Performance warning
    print("\n[Scenario 4: Performance Warning]")
    polling_logger.info("Starting polling group: Group2_Welding")
    perf_logger.info("Group=Group2_Welding | PLC=PLC02 | Tags=50 | Time=4850.20ms | Status=SUCCESS")
    polling_logger.warning("Polling took longer than expected: 4850ms (threshold: 3000ms)")

    print("\n✓ Polling simulation completed")


def test_multiline_exception():
    """Test exception logging with traceback"""
    print("\n" + "=" * 70)
    print("Test 5: Exception Logging with Traceback")
    print("=" * 70)

    logger = logging.getLogger("test.exception")

    try:
        # Simulate an error
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error("Exception occurred during calculation", exc_info=True)

    print("\n✓ Exception logged with traceback")


def main():
    """Main test function"""
    print("\n" + "=" * 70)
    print("Terminal Logging Test - Colorful Output & Level Control")
    print("=" * 70)

    # Initialize logging with colors enabled
    print("\nInitializing logging system...")
    initialize_logging(use_colors=True)

    # Run all tests
    test_all_log_levels()
    test_environment_variable()
    test_runtime_level_change()
    test_polling_simulation()
    test_multiline_exception()

    # Final summary
    print("\n" + "=" * 70)
    print("All Tests Completed!")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Colorful log output (DEBUG=gray, INFO=blue, WARNING=yellow, ERROR/CRITICAL=red)")
    print("  ✓ Environment variable control (LOG_LEVEL)")
    print("  ✓ Runtime log level changes")
    print("  ✓ Real-world polling scenarios")
    print("  ✓ Exception logging with tracebacks")
    print("\nUsage in Your Application:")
    print("  1. Set LOG_LEVEL environment variable:")
    print("     set LOG_LEVEL=DEBUG  (Windows)")
    print("     export LOG_LEVEL=DEBUG  (Linux/Mac)")
    print("  2. Or set programmatically:")
    print("     initialize_logging(console_level=logging.DEBUG)")
    print("  3. Change at runtime:")
    print("     set_console_log_level(logging.DEBUG)")
    print("=" * 70)


if __name__ == "__main__":
    main()

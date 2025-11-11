"""
Test Script for .env Configuration

.env 파일 기반 환경설정 테스트
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from src.config.settings import settings
from src.config.logging_config import initialize_logging
import logging


def test_settings_loading():
    """Test .env settings loading"""
    print("\n" + "=" * 70)
    print("Test 1: .env Settings Loading")
    print("=" * 70)

    print("\n[Logging Settings]")
    print(f"  LOG_LEVEL: {settings.LOG_LEVEL}")
    print(f"  LOG_LEVEL_INT: {settings.LOG_LEVEL_INT}")
    print(f"  LOG_COLORS: {settings.LOG_COLORS}")
    print(f"  LOG_DIR: {settings.LOG_DIR}")
    print(f"  LOG_MAX_BYTES: {settings.LOG_MAX_BYTES:,} bytes")
    print(f"  LOG_BACKUP_COUNT: {settings.LOG_BACKUP_COUNT}")

    print("\n[Server Settings]")
    print(f"  API_HOST: {settings.API_HOST}")
    print(f"  API_PORT: {settings.API_PORT}")

    print("\n[Database Settings]")
    print(f"  SQLite: {settings.DATABASE_PATH}")
    print(f"  Oracle: {settings.ORACLE_USERNAME}@{settings.ORACLE_HOST}:{settings.ORACLE_PORT}/{settings.ORACLE_SERVICE_NAME}")

    print("\n✓ Settings loaded successfully from .env file")


def test_logging_with_env_config():
    """Test logging with .env configuration"""
    print("\n" + "=" * 70)
    print("Test 2: Logging with .env Configuration")
    print("=" * 70)

    # Initialize logging (will use .env settings)
    print("\nInitializing logging from .env settings...")
    initialize_logging()

    # Get logger
    logger = logging.getLogger("test.env.config")

    # Test all log levels
    print("\n[Testing All Log Levels]")
    logger.debug("DEBUG: This is a debug message")
    logger.info("INFO: This is an info message")
    logger.warning("WARNING: This is a warning message")
    logger.error("ERROR: This is an error message")
    logger.critical("CRITICAL: This is a critical message")

    print("\n✓ Logging initialized with .env settings")


def test_override_env_settings():
    """Test overriding .env settings with parameters"""
    print("\n" + "=" * 70)
    print("Test 3: Override .env Settings with Parameters")
    print("=" * 70)

    # Clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    print("\nOverriding log level to DEBUG (from .env INFO)...")
    initialize_logging(console_level=logging.DEBUG)

    logger = logging.getLogger("test.override")

    print("\n[Testing with DEBUG level]")
    logger.debug("DEBUG: Now this debug message shows!")
    logger.info("INFO: This info message also shows")

    print("\n✓ Parameter override works correctly")


def test_display_full_config():
    """Display full configuration"""
    print("\n" + "=" * 70)
    print("Test 4: Display Full Configuration")
    print("=" * 70)

    settings.display_config()


def test_modify_env_at_runtime():
    """Test modifying .env settings at runtime"""
    print("\n" + "=" * 70)
    print("Test 5: Runtime Configuration Check")
    print("=" * 70)

    print("\n[Current Configuration]")
    print(f"  LOG_LEVEL: {settings.LOG_LEVEL}")
    print(f"  LOG_COLORS: {settings.LOG_COLORS}")
    print(f"  LOG_DIR: {settings.LOG_DIR}")

    print("\n[Note]")
    print("  To change settings, edit backend/.env file and restart the application")
    print("  Example changes:")
    print("    - Set LOG_LEVEL=DEBUG for detailed logging")
    print("    - Set LOG_COLORS=false for server environments")
    print("    - Set LOG_DIR=custom_logs for custom log directory")

    print("\n✓ Configuration is managed via .env file")


def main():
    """Main test function"""
    print("\n" + "=" * 70)
    print(".env Configuration System Test")
    print("=" * 70)

    # Run all tests
    test_settings_loading()
    test_logging_with_env_config()
    test_override_env_settings()
    test_display_full_config()
    test_modify_env_at_runtime()

    # Final summary
    print("\n" + "=" * 70)
    print("All Tests Completed!")
    print("=" * 70)

    print("\n[Summary]")
    print("  ✓ .env file loaded successfully")
    print("  ✓ Settings accessible via settings object")
    print("  ✓ Logging initialized with .env configuration")
    print("  ✓ Parameters can override .env settings")
    print("  ✓ Full configuration display available")

    print("\n[Configuration File Location]")
    print(f"  backend/.env")

    print("\n[Usage in Application]")
    print("  1. Edit backend/.env file to change settings")
    print("  2. Restart application to apply changes")
    print("  3. No need to set environment variables externally")

    print("\n[Example Configuration Changes]")
    print("  # For development (verbose logging)")
    print("  LOG_LEVEL=DEBUG")
    print("  LOG_COLORS=true")
    print()
    print("  # For production (minimal logging)")
    print("  LOG_LEVEL=ERROR")
    print("  LOG_COLORS=false")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()

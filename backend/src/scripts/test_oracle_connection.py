"""
Test Oracle Database Connection

Verify Oracle connectivity and pool functionality before proceeding with implementation.

Usage:
    python backend/src/scripts/test_oracle_connection.py
"""

import sys
import os
from pathlib import Path

# Add backend/src to path for imports
backend_src = Path(__file__).parent.parent
sys.path.insert(0, str(backend_src))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('backend/.env')

import logging
import oracledb
from datetime import datetime

from oracle_writer.config import load_config_from_env
from oracle_writer.connection_pool import OracleConnectionPool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_oracle_version(pool: OracleConnectionPool):
    """
    Test 1: Query Oracle database version

    Args:
        pool: OracleConnectionPool instance

    Returns:
        True if successful, False otherwise
    """
    logger.info("=" * 60)
    logger.info("Test 1: Query Oracle Database Version")
    logger.info("=" * 60)

    try:
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT banner FROM v$version WHERE banner LIKE 'Oracle%'")
            row = cursor.fetchone()

            if row:
                version = row[0]
                logger.info(f"✓ Oracle version: {version}")
                return True
            else:
                logger.error("✗ Could not retrieve Oracle version")
                return False

    except oracledb.Error as e:
        logger.error(f"✗ Failed to query Oracle version: {e}")
        return False


def test_pool_stats(pool: OracleConnectionPool):
    """
    Test 2: Check connection pool statistics

    Args:
        pool: OracleConnectionPool instance

    Returns:
        True if successful, False otherwise
    """
    logger.info("")
    logger.info("=" * 60)
    logger.info("Test 2: Connection Pool Statistics")
    logger.info("=" * 60)

    try:
        stats = pool.get_stats()
        logger.info(f"✓ Pool statistics:")
        logger.info(f"  - Open connections: {stats['open']}")
        logger.info(f"  - Busy connections: {stats['busy']}")
        logger.info(f"  - Min pool size: {stats['min']}")
        logger.info(f"  - Max pool size: {stats['max']}")
        logger.info(f"  - Increment: {stats['increment']}")
        logger.info(f"  - Is open: {stats['is_open']}")
        return True

    except Exception as e:
        logger.error(f"✗ Failed to get pool stats: {e}")
        return False


def test_simple_query(pool: OracleConnectionPool):
    """
    Test 3: Execute simple query (dual table)

    Args:
        pool: OracleConnectionPool instance

    Returns:
        True if successful, False otherwise
    """
    logger.info("")
    logger.info("=" * 60)
    logger.info("Test 3: Execute Simple Query (DUAL)")
    logger.info("=" * 60)

    try:
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 + 1 AS result, SYSDATE FROM dual")
            row = cursor.fetchone()

            if row:
                result = row[0]
                timestamp = row[1]
                logger.info(f"✓ Query result: 1 + 1 = {result}")
                logger.info(f"✓ Oracle server time: {timestamp}")
                return True
            else:
                logger.error("✗ Query returned no results")
                return False

    except oracledb.Error as e:
        logger.error(f"✗ Failed to execute query: {e}")
        return False


def test_multiple_connections(pool: OracleConnectionPool):
    """
    Test 4: Acquire multiple connections from pool

    Args:
        pool: OracleConnectionPool instance

    Returns:
        True if successful, False otherwise
    """
    logger.info("")
    logger.info("=" * 60)
    logger.info("Test 4: Multiple Concurrent Connections")
    logger.info("=" * 60)

    try:
        # Test acquiring up to pool max
        connections = []
        max_connections = min(3, pool.config.pool_max)

        for i in range(max_connections):
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT SYS_CONTEXT('USERENV', 'SID') FROM dual")
                sid = cursor.fetchone()[0]
                logger.info(f"✓ Connection {i+1}: Session ID = {sid}")

        logger.info(f"✓ Successfully acquired {max_connections} connections")
        return True

    except oracledb.Error as e:
        logger.error(f"✗ Failed to acquire multiple connections: {e}")
        return False


def test_tag_values_table(pool: OracleConnectionPool):
    """
    Test 5: Check if tag_values table exists and is accessible

    Args:
        pool: OracleConnectionPool instance

    Returns:
        True if successful, False otherwise
    """
    logger.info("")
    logger.info("=" * 60)
    logger.info("Test 5: Check TAG_VALUES Table")
    logger.info("=" * 60)

    try:
        with pool.get_connection() as conn:
            cursor = conn.cursor()

            # Check if table exists
            cursor.execute("""
                SELECT COUNT(*)
                FROM user_tables
                WHERE table_name = 'TAG_VALUES'
            """)
            count = cursor.fetchone()[0]

            if count == 0:
                logger.warning("⚠ TAG_VALUES table does not exist yet")
                logger.warning("  Note: This table will be created during Feature 4 setup")
                logger.warning("  Expected schema:")
                logger.warning("    - timestamp (TIMESTAMP)")
                logger.warning("    - plc_code (VARCHAR2(20))")
                logger.warning("    - tag_address (VARCHAR2(50))")
                logger.warning("    - tag_value (NUMBER)")
                logger.warning("    - quality (VARCHAR2(10))")
                return True  # Not an error, just informational

            # Table exists, check structure
            cursor.execute("""
                SELECT column_name, data_type
                FROM user_tab_columns
                WHERE table_name = 'TAG_VALUES'
                ORDER BY column_id
            """)
            columns = cursor.fetchall()

            logger.info(f"✓ TAG_VALUES table exists with {len(columns)} columns:")
            for col_name, col_type in columns:
                logger.info(f"  - {col_name}: {col_type}")

            return True

    except oracledb.Error as e:
        logger.error(f"✗ Failed to check TAG_VALUES table: {e}")
        return False


def main():
    """
    Main test function

    Runs all Oracle connection tests and reports results.
    """
    logger.info("")
    logger.info("*" * 60)
    logger.info("Oracle Connection Test Suite")
    logger.info("*" * 60)
    logger.info("")

    # Load configuration
    try:
        config = load_config_from_env()
        logger.info("Configuration loaded:")
        logger.info(f"  - Connection: {config.get_connect_string()}")
        logger.info(f"  - Pool size: {config.pool_min}-{config.pool_max}")
        logger.info("")

    except ValueError as e:
        logger.error(f"✗ Configuration error: {e}")
        logger.error("")
        logger.error("Required environment variables:")
        logger.error("  - ORACLE_HOST")
        logger.error("  - ORACLE_PORT (default: 1521)")
        logger.error("  - ORACLE_SERVICE_NAME")
        logger.error("  - ORACLE_USERNAME")
        logger.error("  - ORACLE_PASSWORD")
        logger.error("  - ORACLE_POOL_MIN (default: 2)")
        logger.error("  - ORACLE_POOL_MAX (default: 5)")
        return 1

    # Create connection pool
    pool = None
    try:
        pool = OracleConnectionPool(config)
        pool.create_pool()
        logger.info("✓ Connection pool created successfully")
        logger.info("")

    except oracledb.Error as e:
        logger.error(f"✗ Failed to create connection pool: {e}")
        logger.error("")
        logger.error("Common issues:")
        logger.error("  1. Oracle server is not running")
        logger.error("  2. Incorrect hostname, port, or service name")
        logger.error("  3. Invalid username or password")
        logger.error("  4. Firewall blocking connection")
        logger.error("  5. Oracle listener not configured")
        return 1

    # Run tests
    results = []
    try:
        results.append(("Oracle Version", test_oracle_version(pool)))
        results.append(("Pool Statistics", test_pool_stats(pool)))
        results.append(("Simple Query", test_simple_query(pool)))
        results.append(("Multiple Connections", test_multiple_connections(pool)))
        results.append(("TAG_VALUES Table", test_tag_values_table(pool)))

    finally:
        # Clean up
        if pool is not None:
            pool.close()
            logger.info("")
            logger.info("✓ Connection pool closed")

    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("Test Results Summary")
    logger.info("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info("")
    logger.info(f"Total: {passed}/{total} tests passed")
    logger.info("=" * 60)

    if passed == total:
        logger.info("")
        logger.info("✓ All tests passed! Oracle connectivity verified.")
        logger.info("  Ready to proceed with Feature 4 implementation.")
        return 0
    else:
        logger.error("")
        logger.error(f"✗ {total - passed} test(s) failed. Please fix issues before proceeding.")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)

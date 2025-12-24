"""
Oracle Connection Pool Wrapper

Thread-safe connection pool using python-oracledb (Thin mode).
"""

import logging
import oracledb
from typing import Optional, ContextManager
from contextlib import contextmanager

from .config import OracleConfig

logger = logging.getLogger(__name__)


class OracleConnectionPool:
    """
    Thread-safe Oracle connection pool wrapper

    Uses python-oracledb's built-in connection pooling with Thin mode
    (no Oracle Instant Client required).

    Attributes:
        config: OracleConfig instance
        pool: oracledb.ConnectionPool instance
    """

    def __init__(self, config: OracleConfig):
        """
        Initialize connection pool (does not create pool yet)

        Args:
            config: OracleConfig with connection parameters

        Note:
            Call create_pool() to actually create the pool
        """
        self.config = config
        self.pool: Optional[oracledb.ConnectionPool] = None
        self._is_closed = False

    def create_pool(self):
        """
        Create the connection pool

        Raises:
            oracledb.Error: If pool creation fails
            ValueError: If pool already exists
        """
        if self.pool is not None:
            raise ValueError("Connection pool already exists")

        try:
            logger.info(
                f"Creating Oracle connection pool: {self.config.get_connect_string()} "
                f"(min={self.config.pool_min}, max={self.config.pool_max})"
            )

            # Create pool using Thin mode (no Instant Client needed)
            self.pool = oracledb.create_pool(
                user=self.config.username,
                password=self.config.password,
                dsn=self.config.get_dsn(),
                min=self.config.pool_min,
                max=self.config.pool_max,
                increment=1,  # Grow pool by 1 connection at a time
                threaded=True,  # Enable thread safety
                getmode=oracledb.POOL_GETMODE_WAIT,  # Wait for connection if pool is busy
                timeout=30,  # Wait up to 30 seconds for a connection
                wait_timeout=5000,  # Wait 5 seconds for a free connection in the pool
                max_lifetime_session=3600,  # Recycle connections after 1 hour
                session_callback=None,
                soda_metadata_cache=False
            )

            self._is_closed = False

            logger.info(
                f"Oracle connection pool created successfully: "
                f"min={self.pool.min}, max={self.pool.max}, increment={self.pool.increment}"
            )

        except oracledb.Error as e:
            logger.error(f"Failed to create Oracle connection pool: {e}")
            raise

    @contextmanager
    def get_connection(self) -> ContextManager[oracledb.Connection]:
        """
        Get a connection from the pool (context manager)

        Usage:
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")

        Yields:
            oracledb.Connection: Database connection

        Raises:
            ValueError: If pool not initialized or closed
            oracledb.Error: If connection acquisition fails
        """
        if self.pool is None:
            raise ValueError("Connection pool not initialized. Call create_pool() first.")

        if self._is_closed:
            raise ValueError("Connection pool is closed")

        connection = None
        try:
            # Acquire connection from pool
            connection = self.pool.acquire()
            logger.debug(f"Connection acquired from pool (open={self.pool.open}, busy={self.pool.busy})")

            yield connection

        except oracledb.Error as e:
            logger.error(f"Database error: {e}")
            raise

        finally:
            # Release connection back to pool
            if connection is not None:
                try:
                    connection.close()  # Returns connection to pool
                    logger.debug("Connection released back to pool")
                except oracledb.Error as e:
                    logger.error(f"Error releasing connection: {e}")

    def close(self):
        """
        Close the connection pool and release all connections

        Safe to call multiple times.
        """
        if self.pool is not None and not self._is_closed:
            try:
                logger.info("Closing Oracle connection pool...")
                self.pool.close()
                self._is_closed = True
                logger.info("Oracle connection pool closed successfully")
            except oracledb.Error as e:
                logger.error(f"Error closing connection pool: {e}")
                raise
            finally:
                self.pool = None

    def is_open(self) -> bool:
        """
        Check if pool is open and available

        Returns:
            True if pool is open, False otherwise
        """
        return self.pool is not None and not self._is_closed

    def get_stats(self) -> dict:
        """
        Get connection pool statistics

        Returns:
            Dictionary with pool stats (open, busy, max, min)

        Raises:
            ValueError: If pool not initialized
        """
        if self.pool is None:
            raise ValueError("Connection pool not initialized")

        return {
            'open': self.pool.open,  # Current number of connections
            'busy': self.pool.busy,  # Connections currently in use
            'max': self.pool.max,    # Maximum pool size
            'min': self.pool.min,    # Minimum pool size
            'increment': self.pool.increment,
            'is_open': self.is_open()
        }

    def __enter__(self):
        """Context manager entry"""
        self.create_pool()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    def __del__(self):
        """Destructor - ensure pool is closed"""
        if self.pool is not None and not self._is_closed:
            try:
                self.close()
            except:
                pass  # Ignore errors during cleanup


def create_pool_from_env() -> OracleConnectionPool:
    """
    Create connection pool from environment variables

    Convenience function that loads config from env and creates pool.

    Returns:
        OracleConnectionPool instance (pool not yet created)

    Raises:
        ValueError: If required environment variables missing

    Usage:
        pool = create_pool_from_env()
        pool.create_pool()
        with pool.get_connection() as conn:
            # Use connection
        pool.close()
    """
    from .config import load_config_from_env

    config = load_config_from_env()
    return OracleConnectionPool(config)

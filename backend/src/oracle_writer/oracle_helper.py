"""
Oracle Database Helper for Machine Synchronization

Provides connection and query utilities for syncing machine data
from Oracle ICOM_MACHINE_MASTER table.
"""

import oracledb
from typing import List, Dict, Optional
from src.oracle_writer.config import load_config_from_env
from src.config.logging_config import get_logger

logger = get_logger(__name__)


class OracleHelper:
    """Helper class for Oracle database operations"""

    def __init__(self):
        """Initialize Oracle helper with config from environment"""
        self.config = load_config_from_env()
        self.connection = None

    def connect(self):
        """
        Establish connection to Oracle database

        Returns:
            oracledb.Connection: Active database connection

        Raises:
            oracledb.Error: If connection fails
        """
        try:
            self.connection = oracledb.connect(
                user=self.config.username,
                password=self.config.password,
                dsn=self.config.get_dsn()
            )
            logger.info(f"Connected to Oracle: {self.config.get_connect_string()}")
            return self.connection
        except oracledb.Error as e:
            logger.error(f"Oracle connection failed: {e}")
            raise

    def disconnect(self):
        """Close Oracle database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Oracle connection closed")

    def fetch_machines(self) -> List[Dict]:
        """
        Fetch all active machines from Oracle ICOM_MACHINE_MASTER table

        Returns:
            List of dictionaries with machine data:
            - machine_code: Machine code (max 20 chars)
            - machine_name: Machine name (max 200 chars)
            - machine_location: Location (max 50 chars)
            - use_yn: Active status ('Y' or 'N')

        Raises:
            oracledb.Error: If query fails
        """
        if not self.connection:
            self.connect()

        try:
            cursor = self.connection.cursor()

            # Query active machines from Oracle
            query = """
                SELECT
                    MACHINE_CODE,
                    MACHINE_NAME,
                    MACHINE_LOCATION,
                    USE_YN
                FROM ICOM_MACHINE_MASTER
                WHERE USE_YN = 'Y'
                ORDER BY MACHINE_CODE
            """

            cursor.execute(query)
            rows = cursor.fetchall()

            machines = []
            for row in rows:
                machine = {
                    'machine_code': row[0].strip() if row[0] else None,
                    'machine_name': row[1].strip() if row[1] else None,
                    'machine_location': row[2].strip() if row[2] and row[2] != '*' else None,
                    'use_yn': row[3]
                }

                # Skip if machine_code or machine_name is missing
                if not machine['machine_code'] or not machine['machine_name']:
                    logger.warning(f"Skipping machine with missing code or name: {row}")
                    continue

                machines.append(machine)

            logger.info(f"Fetched {len(machines)} active machines from Oracle")
            cursor.close()

            return machines

        except oracledb.Error as e:
            logger.error(f"Failed to fetch machines from Oracle: {e}")
            raise

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


def get_oracle_machines() -> List[Dict]:
    """
    Convenience function to fetch machines from Oracle

    Returns:
        List of machine dictionaries

    Raises:
        Exception: If Oracle connection or query fails
    """
    with OracleHelper() as oracle:
        return oracle.fetch_machines()

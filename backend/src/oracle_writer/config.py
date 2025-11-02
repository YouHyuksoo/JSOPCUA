"""
Oracle Database Configuration

Load Oracle connection parameters from environment variables with validation.
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class OracleConfig:
    """
    Oracle database connection configuration

    Attributes:
        host: Oracle server hostname or IP
        port: Oracle listener port (default: 1521)
        service_name: Oracle service name (not SID)
        username: Database user
        password: Database password
        pool_min: Minimum connections in pool
        pool_max: Maximum connections in pool
    """
    host: str
    port: int
    service_name: str
    username: str
    password: str
    pool_min: int = 2
    pool_max: int = 5

    def __post_init__(self):
        """Validate configuration after initialization"""
        self.validate()

    def validate(self):
        """
        Validate configuration parameters

        Raises:
            ValueError: If any required field is missing or invalid
        """
        # Required string fields
        if not self.host or not self.host.strip():
            raise ValueError("Oracle host is required")

        if not self.service_name or not self.service_name.strip():
            raise ValueError("Oracle service_name is required")

        if not self.username or not self.username.strip():
            raise ValueError("Oracle username is required")

        if not self.password:
            raise ValueError("Oracle password is required")

        # Port validation
        if not isinstance(self.port, int) or self.port <= 0 or self.port > 65535:
            raise ValueError(f"Invalid Oracle port: {self.port} (must be 1-65535)")

        # Pool size validation
        if not isinstance(self.pool_min, int) or self.pool_min < 1:
            raise ValueError(f"Invalid pool_min: {self.pool_min} (must be >= 1)")

        if not isinstance(self.pool_max, int) or self.pool_max < self.pool_min:
            raise ValueError(f"Invalid pool_max: {self.pool_max} (must be >= pool_min)")

    def get_dsn(self) -> str:
        """
        Get Oracle Data Source Name (DSN) for connection

        Returns:
            DSN string in format: host:port/service_name
        """
        return f"{self.host}:{self.port}/{self.service_name}"

    def get_connect_string(self) -> str:
        """
        Get full connection string (without password for logging)

        Returns:
            Connection string: username@host:port/service_name
        """
        return f"{self.username}@{self.host}:{self.port}/{self.service_name}"

    def to_dict(self) -> dict:
        """
        Convert config to dictionary (excludes password)

        Returns:
            Dictionary with configuration (password masked)
        """
        return {
            'host': self.host,
            'port': self.port,
            'service_name': self.service_name,
            'username': self.username,
            'password': '***',  # Masked for security
            'pool_min': self.pool_min,
            'pool_max': self.pool_max,
            'dsn': self.get_dsn()
        }


def load_config_from_env() -> OracleConfig:
    """
    Load Oracle configuration from environment variables

    Required environment variables:
        - ORACLE_HOST: Oracle server hostname/IP
        - ORACLE_PORT: Oracle listener port (default: 1521)
        - ORACLE_SERVICE_NAME: Oracle service name
        - ORACLE_USERNAME: Database username
        - ORACLE_PASSWORD: Database password

    Optional environment variables:
        - ORACLE_POOL_MIN: Minimum pool connections (default: 2)
        - ORACLE_POOL_MAX: Maximum pool connections (default: 5)

    Returns:
        OracleConfig instance with validated configuration

    Raises:
        ValueError: If required environment variables are missing or invalid
    """
    # Required fields
    host = os.getenv('ORACLE_HOST')
    if not host:
        raise ValueError("Missing required environment variable: ORACLE_HOST")

    service_name = os.getenv('ORACLE_SERVICE_NAME')
    if not service_name:
        raise ValueError("Missing required environment variable: ORACLE_SERVICE_NAME")

    username = os.getenv('ORACLE_USERNAME')
    if not username:
        raise ValueError("Missing required environment variable: ORACLE_USERNAME")

    password = os.getenv('ORACLE_PASSWORD')
    if not password:
        raise ValueError("Missing required environment variable: ORACLE_PASSWORD")

    # Optional fields with defaults
    try:
        port = int(os.getenv('ORACLE_PORT', '1521'))
    except ValueError:
        raise ValueError(f"Invalid ORACLE_PORT: must be an integer")

    try:
        pool_min = int(os.getenv('ORACLE_POOL_MIN', '2'))
    except ValueError:
        raise ValueError(f"Invalid ORACLE_POOL_MIN: must be an integer")

    try:
        pool_max = int(os.getenv('ORACLE_POOL_MAX', '5'))
    except ValueError:
        raise ValueError(f"Invalid ORACLE_POOL_MAX: must be an integer")

    # Create and validate config
    return OracleConfig(
        host=host,
        port=port,
        service_name=service_name,
        username=username,
        password=password,
        pool_min=pool_min,
        pool_max=pool_max
    )


def load_buffer_config_from_env() -> dict:
    """
    Load buffer configuration from environment variables

    Optional environment variables:
        - BUFFER_MAX_SIZE: Maximum buffer capacity (default: 100000)
        - BUFFER_BATCH_SIZE: Default batch size (default: 500)
        - BUFFER_BATCH_SIZE_MAX: Maximum batch size (default: 1000)
        - BUFFER_WRITE_INTERVAL: Write trigger interval in seconds (default: 1.0)
        - BUFFER_RETRY_COUNT: Number of retry attempts (default: 3)
        - BACKUP_FILE_PATH: Directory for CSV backups (default: backend/backup)

    Returns:
        Dictionary with buffer configuration
    """
    try:
        buffer_max_size = int(os.getenv('BUFFER_MAX_SIZE', '100000'))
    except ValueError:
        buffer_max_size = 100000

    try:
        buffer_batch_size = int(os.getenv('BUFFER_BATCH_SIZE', '500'))
    except ValueError:
        buffer_batch_size = 500

    try:
        buffer_batch_size_max = int(os.getenv('BUFFER_BATCH_SIZE_MAX', '1000'))
    except ValueError:
        buffer_batch_size_max = 1000

    try:
        buffer_write_interval = float(os.getenv('BUFFER_WRITE_INTERVAL', '1.0'))
    except ValueError:
        buffer_write_interval = 1.0

    try:
        buffer_retry_count = int(os.getenv('BUFFER_RETRY_COUNT', '3'))
    except ValueError:
        buffer_retry_count = 3

    backup_file_path = os.getenv('BACKUP_FILE_PATH', 'backend/backup')

    return {
        'buffer_max_size': buffer_max_size,
        'buffer_batch_size': buffer_batch_size,
        'buffer_batch_size_max': buffer_batch_size_max,
        'buffer_write_interval': buffer_write_interval,
        'buffer_retry_count': buffer_retry_count,
        'backup_file_path': backup_file_path
    }

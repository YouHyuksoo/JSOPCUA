"""
Polling Engine Module

Multi-threaded polling engine for reading PLC tags at fixed intervals or on-demand.
Supports FIXED mode (automatic polling) and HANDSHAKE mode (manual trigger).
"""

import logging
from logging.handlers import RotatingFileHandler
import os
from src.config.paths import get_logs_dir

# Configure logging for polling module
logger = logging.getLogger(__name__)

def setup_logging(log_dir=None, log_level=logging.INFO):
    """
    Setup logging configuration for polling module

    Args:
        log_dir: Directory for log files
        log_level: Logging level (default: INFO)
    """
    if log_dir is None:
        log_dir = get_logs_dir()
    os.makedirs(log_dir, exist_ok=True)

    # Create rotating file handler
    log_file = os.path.join(log_dir, "polling.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(log_level)

# Initialize logging on module import
setup_logging()

__all__ = [
    'setup_logging',
]

"""
Buffer Package

Thread-safe circular buffer for consuming polling data and preparing for Oracle writes.
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(log_dir="backend/logs", log_level=logging.INFO):
    """
    Configure logging for buffer package
    
    Args:
        log_dir: Directory for log files
        log_level: Logging level (default: INFO)
    """
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "buffer.log")
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation (10MB, 5 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # Get logger for this package
    logger = logging.getLogger('buffer')
    logger.setLevel(log_level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Initialize logger when package is imported
logger = setup_logging()

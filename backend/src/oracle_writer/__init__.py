"""
Oracle Writer Package

Oracle Database writer with connection pooling, batch writes, and CSV backup.
"""

import logging

# Use the global logging configuration from src.config.logging_config
# The oracle_writer logger is already configured in logging_config.py
# No need for separate configuration here - just get the logger

logger = logging.getLogger('oracle_writer')

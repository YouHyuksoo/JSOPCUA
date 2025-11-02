"""
CSV Backup Module

Save failed Oracle writes to timestamped CSV files for manual recovery.
"""

import os
import csv
import logging
from datetime import datetime
from typing import List
from pathlib import Path

logger = logging.getLogger(__name__)


class CSVBackup:
    """
    CSV backup writer for failed Oracle writes

    Creates timestamped CSV files in the backup directory when
    Oracle writes fail after all retries are exhausted.

    Attributes:
        backup_dir: Directory path for backup files
    """

    def __init__(self, backup_dir: str = "backend/backup"):
        """
        Initialize CSV backup handler

        Args:
            backup_dir: Directory path for backup files (default: backend/backup)
        """
        self.backup_dir = backup_dir
        self.total_backups = 0
        self.total_items_backed_up = 0

        # Ensure backup directory exists
        self._ensure_backup_dir()

    def _ensure_backup_dir(self):
        """
        Ensure backup directory exists

        Creates directory if it doesn't exist.
        """
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            logger.info(f"Backup directory ready: {self.backup_dir}")
        except Exception as e:
            logger.error(f"Failed to create backup directory {self.backup_dir}: {e}")
            raise

    def save_failed_batch(self, items: List) -> str:
        """
        Save failed batch to timestamped CSV file

        File format: backup_YYYYMMDD_HHMMSS_<count>.csv

        Args:
            items: List of BufferedTagValue items that failed to write

        Returns:
            Path to created backup file

        Raises:
            IOError: If file creation or writing fails
        """
        if not items:
            logger.warning("No items to backup")
            return ""

        try:
            # Generate timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_{timestamp}_{len(items)}.csv"
            filepath = os.path.join(self.backup_dir, filename)

            # Write CSV file
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['timestamp', 'plc_code', 'tag_address', 'tag_value', 'quality']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write header
                writer.writeheader()

                # Write data rows
                for item in items:
                    writer.writerow({
                        'timestamp': item.timestamp.isoformat(),
                        'plc_code': item.plc_code,
                        'tag_address': item.tag_address,
                        'tag_value': item.tag_value,
                        'quality': item.quality
                    })

            # Update statistics
            self.total_backups += 1
            self.total_items_backed_up += len(items)

            logger.warning(
                f"Failed batch backed up to CSV: {filepath} ({len(items)} items)"
            )

            return filepath

        except IOError as e:
            logger.error(f"Failed to write backup CSV {filepath}: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error writing backup CSV: {e}", exc_info=True)
            raise

    def get_backup_file_count(self) -> int:
        """
        Count CSV backup files in backup directory

        Returns:
            Number of backup_*.csv files
        """
        try:
            if not os.path.exists(self.backup_dir):
                return 0

            backup_files = [
                f for f in os.listdir(self.backup_dir)
                if f.startswith('backup_') and f.endswith('.csv')
            ]

            return len(backup_files)

        except Exception as e:
            logger.error(f"Error counting backup files: {e}")
            return 0

    def get_backup_files(self) -> List[str]:
        """
        Get list of all backup CSV files

        Returns:
            List of backup file paths (full paths)
        """
        try:
            if not os.path.exists(self.backup_dir):
                return []

            backup_files = [
                os.path.join(self.backup_dir, f)
                for f in os.listdir(self.backup_dir)
                if f.startswith('backup_') and f.endswith('.csv')
            ]

            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

            return backup_files

        except Exception as e:
            logger.error(f"Error listing backup files: {e}")
            return []

    def get_total_backup_size(self) -> int:
        """
        Get total size of all backup files in bytes

        Returns:
            Total size in bytes
        """
        try:
            backup_files = self.get_backup_files()
            total_size = sum(os.path.getsize(f) for f in backup_files if os.path.exists(f))
            return total_size

        except Exception as e:
            logger.error(f"Error calculating backup size: {e}")
            return 0

    def cleanup_old_backups(self, max_age_days: int = 30, max_count: int = 100):
        """
        Clean up old backup files

        Removes backup files older than max_age_days or keeps only max_count newest files.

        Args:
            max_age_days: Maximum age of backup files in days (default: 30)
            max_count: Maximum number of backup files to keep (default: 100)

        Returns:
            Number of files deleted
        """
        try:
            backup_files = self.get_backup_files()

            if not backup_files:
                return 0

            deleted_count = 0
            now = datetime.now()

            # Delete old files
            for filepath in backup_files:
                try:
                    # Check age
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    age_days = (now - file_mtime).days

                    if age_days > max_age_days:
                        os.remove(filepath)
                        deleted_count += 1
                        logger.info(f"Deleted old backup file: {filepath} (age: {age_days} days)")

                except Exception as e:
                    logger.error(f"Error deleting backup file {filepath}: {e}")

            # Keep only max_count newest files
            if len(backup_files) > max_count:
                files_to_delete = backup_files[max_count:]
                for filepath in files_to_delete:
                    try:
                        if os.path.exists(filepath):
                            os.remove(filepath)
                            deleted_count += 1
                            logger.info(f"Deleted excess backup file: {filepath}")
                    except Exception as e:
                        logger.error(f"Error deleting backup file {filepath}: {e}")

            if deleted_count > 0:
                logger.info(f"Cleanup complete: {deleted_count} backup files deleted")

            return deleted_count

        except Exception as e:
            logger.error(f"Error during backup cleanup: {e}")
            return 0

    def stats(self) -> dict:
        """
        Get backup statistics

        Returns:
            Dictionary with backup stats
        """
        return {
            'backup_dir': self.backup_dir,
            'total_backups_created': self.total_backups,
            'total_items_backed_up': self.total_items_backed_up,
            'current_backup_file_count': self.get_backup_file_count(),
            'total_backup_size_bytes': self.get_total_backup_size()
        }

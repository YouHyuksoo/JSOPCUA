"""
Polling Engine

Orchestrates all polling threads and manages polling group lifecycle.
"""

import logging
import sqlite3
from typing import Dict, List, Optional
from pathlib import Path
from .models import PollingGroup, PollingMode, ThreadState
from .data_queue import DataQueue
from .polling_thread import PollingThread
from .fixed_polling_thread import FixedPollingThread
from .handshake_polling_thread import HandshakePollingThread
from .exceptions import (
    PollingGroupNotFoundError,
    PollingGroupAlreadyRunningError,
    PollingGroupNotRunningError,
    MaxPollingGroupsReachedError
)

logger = logging.getLogger(__name__)


class PollingEngine:
    """
    Main polling engine orchestrator

    Manages all polling threads, loads configuration from database,
    and provides control APIs for starting/stopping/status queries.

    Attributes:
        db_path: Path to SQLite database
        pool_manager: PoolManager instance from Feature 2
        data_queue: Shared DataQueue for all threads
        polling_threads: Dict of group_name → PollingThread
        max_groups: Maximum number of concurrent polling groups
    """

    MAX_POLLING_GROUPS = 10

    def __init__(self, db_path: str, pool_manager):
        """
        Initialize polling engine

        Args:
            db_path: Path to SQLite database (Feature 1)
            pool_manager: PoolManager instance (Feature 2)
        """
        self.db_path = Path(db_path)
        self.pool_manager = pool_manager
        self.data_queue = DataQueue(maxsize=10000)
        self.polling_threads: Dict[str, PollingThread] = {}
        self.max_groups = self.MAX_POLLING_GROUPS

        logger.info(f"PollingEngine initialized: db={db_path}, max_groups={self.max_groups}")

    def initialize(self):
        """
        Initialize polling engine

        Loads polling group configurations from database and creates
        thread instances for each group. Does not start threads.
        """
        logger.info("Initializing polling engine...")
        groups = self._load_polling_groups()

        for group in groups:
            if group.is_active:
                # Create thread instance based on polling mode
                if group.mode == PollingMode.FIXED:
                    thread = FixedPollingThread(group, self.pool_manager, self.data_queue, db_path=str(self.db_path))
                    self.polling_threads[group.group_name] = thread
                    logger.info(
                        f"Created FIXED polling thread: {group.group_name} "
                        f"(interval={group.interval_ms}ms, tags={len(group.tag_addresses)})"
                    )
                elif group.mode == PollingMode.HANDSHAKE:
                    thread = HandshakePollingThread(group, self.pool_manager, self.data_queue, db_path=str(self.db_path))
                    self.polling_threads[group.group_name] = thread
                    logger.info(
                        f"Created HANDSHAKE polling thread: {group.group_name} "
                        f"(tags={len(group.tag_addresses)})"
                    )
                else:
                    logger.warning(f"Unknown polling mode for group {group.group_name}: {group.mode.value}")

        logger.info(f"Polling engine initialization complete: {len(self.polling_threads)} threads created")

    def _load_polling_groups(self) -> List[PollingGroup]:
        """
        Load polling group configurations from SQLite database

        Reads from polling_groups table and tags table to build PollingGroup objects.

        Returns:
            List of PollingGroup configurations

        Raises:
            sqlite3.Error: If database query fails
        """
        if not self.db_path.exists():
            logger.error(f"Database not found: {self.db_path}")
            return []

        groups = []

        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Load polling groups with PLC info
            cursor.execute("""
                SELECT pg.id, pg.group_name, pg.polling_mode, pg.polling_interval_ms,
                       pg.group_category, pg.is_active, pg.plc_code
                FROM polling_groups pg
                ORDER BY pg.id
            """)

            rows = cursor.fetchall()
            logger.info(f"Found {len(rows)} polling groups in database")

            for row in rows:
                # Skip if no PLC assigned
                if not row['plc_code']:
                    logger.warning(f"Polling group {row['group_name']} has no PLC assigned, skipping")
                    continue

                # Load tags for this group (must match both polling_group_id and plc_code)
                cursor.execute("""
                    SELECT tag_address
                    FROM tags
                    WHERE polling_group_id = ?
                      AND plc_code = ?
                      AND is_active = 1
                    ORDER BY tag_address
                """, (row['id'], row['plc_code']))

                tag_rows = cursor.fetchall()

                # Skip if no tags
                if not tag_rows:
                    logger.warning(f"Polling group {row['group_name']} has no active tags, skipping")
                    continue

                plc_code = row['plc_code']
                tag_addresses = [tag_row['tag_address'] for tag_row in tag_rows]

                # Create PollingGroup
                try:
                    group = PollingGroup(
                        group_id=row['id'],
                        group_name=row['group_name'],
                        plc_code=plc_code,
                        mode=PollingMode(row['polling_mode']),
                        interval_ms=row['polling_interval_ms'],
                        group_category=row['group_category'] if row['group_category'] else 'OPERATION',
                        is_active=bool(row['is_active']),
                        tag_addresses=tag_addresses
                    )
                    groups.append(group)
                    logger.debug(f"Loaded group {group.group_name}: {len(tag_addresses)} tags, PLC={plc_code}, category={group.group_category}")

                except ValueError as e:
                    logger.error(f"Invalid polling group configuration for {row['group_name']}: {e}")
                    continue

            conn.close()

        except sqlite3.Error as e:
            logger.error(f"Database error loading polling groups: {e}")
            raise

        return groups

    def get_status_all(self) -> List[Dict]:
        """
        Get status of all polling groups

        Returns:
            List of status dictionaries for all groups
        """
        statuses = []

        for group_name, thread in self.polling_threads.items():
            statuses.append(thread.get_status())

        # Also include queue size
        queue_info = {
            "queue_size": self.data_queue.size(),
            "queue_maxsize": self.data_queue.maxsize,
            "queue_is_full": self.data_queue.is_full()
        }

        logger.debug(f"Status query: {len(statuses)} groups, queue_size={queue_info['queue_size']}")

        return statuses

    def start_all(self):
        """
        Start all polling threads

        Starts all active polling groups that are not already running.
        """
        logger.info("Starting all polling groups...")

        started_count = 0
        for group_name, thread in self.polling_threads.items():
            if not thread.is_running():
                try:
                    self._check_max_groups()
                    thread.start()
                    started_count += 1
                    logger.info(f"Started polling group: {group_name}")
                except MaxPollingGroupsReachedError as e:
                    logger.error(f"Cannot start {group_name}: {e}")
                    break
                except Exception as e:
                    logger.error(f"Failed to start {group_name}: {e}")

        logger.info(f"Started {started_count} polling groups")

    def stop_all(self, timeout: float = 5.0):
        """
        Stop all running polling threads

        Gracefully stops all running threads, waiting up to timeout seconds for each.

        Args:
            timeout: Maximum time to wait for each thread to stop (seconds)
        """
        logger.info("Stopping all polling groups...")

        stopped_count = 0
        for group_name, thread in self.polling_threads.items():
            if thread.is_running():
                try:
                    thread.stop(timeout=timeout)
                    stopped_count += 1
                    logger.info(f"Stopped polling group: {group_name}")
                except Exception as e:
                    logger.error(f"Error stopping {group_name}: {e}")

        logger.info(f"Stopped {stopped_count} polling groups")

    def start_group(self, group_name: str):
        """
        Start a specific polling group

        Args:
            group_name: Name of polling group to start

        Raises:
            PollingGroupNotFoundError: If group doesn't exist
            PollingGroupAlreadyRunningError: If group is already running
            MaxPollingGroupsReachedError: If maximum groups already running
        """
        if group_name not in self.polling_threads:
            raise PollingGroupNotFoundError(f"Polling group not found: {group_name}")

        thread = self.polling_threads[group_name]

        if thread.is_running():
            raise PollingGroupAlreadyRunningError(f"Group {group_name} is already running")

        # Check max groups
        self._check_max_groups()

        # Start the thread
        thread.start()
        logger.info(f"Started polling group: {group_name}")

    def stop_group(self, group_name: str, timeout: float = 5.0):
        """
        Stop a specific polling group

        Args:
            group_name: Name of polling group to stop
            timeout: Maximum time to wait for thread termination (seconds)

        Raises:
            PollingGroupNotFoundError: If group doesn't exist
            PollingGroupNotRunningError: If group is not running
        """
        if group_name not in self.polling_threads:
            raise PollingGroupNotFoundError(f"Polling group not found: {group_name}")

        thread = self.polling_threads[group_name]

        if not thread.is_running():
            raise PollingGroupNotRunningError(f"Group {group_name} is not running")

        # Stop the thread
        thread.stop(timeout=timeout)
        logger.info(f"Stopped polling group: {group_name}")

    def trigger_handshake(self, group_name: str) -> Dict[str, any]:
        """
        Manually trigger polling for a HANDSHAKE mode group

        Args:
            group_name: Name of polling group to trigger

        Returns:
            Dictionary with trigger result:
            {
                "success": bool,
                "group_name": str,
                "mode": str,
                "message": str,
                "tag_count": int (if success)
            }

        Raises:
            PollingGroupNotFoundError: If group doesn't exist
        """
        # Find group
        if group_name not in self.polling_threads:
            raise PollingGroupNotFoundError(f"Polling group not found: {group_name}")

        thread = self.polling_threads[group_name]

        # Verify it's HANDSHAKE mode
        if thread.group.mode != PollingMode.HANDSHAKE:
            return {
                "success": False,
                "group_name": group_name,
                "mode": thread.group.mode.value,
                "message": f"Group {group_name} is not in HANDSHAKE mode"
            }

        # Verify thread is running
        if not thread.is_running():
            return {
                "success": False,
                "group_name": group_name,
                "mode": "HANDSHAKE",
                "message": f"Group {group_name} is not running"
            }

        # Trigger the poll
        triggered = thread.trigger()

        if triggered:
            logger.info(f"HANDSHAKE poll triggered: group={group_name}")
            return {
                "success": True,
                "group_name": group_name,
                "mode": "HANDSHAKE",
                "message": "Poll triggered successfully",
                "tag_count": len(thread.group.tag_addresses)
            }
        else:
            return {
                "success": False,
                "group_name": group_name,
                "mode": "HANDSHAKE",
                "message": "Trigger ignored (deduplication or not running)"
            }

    def get_queue_size(self) -> int:
        """
        Get current data queue size

        Returns:
            Number of items in queue
        """
        return self.data_queue.size()

    def shutdown(self):
        """
        Shutdown polling engine

        Stops all running threads and clears data queue.
        """
        logger.info("Shutting down polling engine...")

        # Stop all threads
        active_threads = [
            thread for thread in self.polling_threads.values()
            if thread.is_running()
        ]

        for thread in active_threads:
            thread.stop(timeout=5.0)

        # Clear queue
        self.data_queue.clear()

        logger.info("Polling engine shutdown complete")

    def _check_max_groups(self):
        """
        Check if maximum number of running groups is reached

        Raises:
            MaxPollingGroupsReachedError: If 10 groups are already running
        """
        running_count = sum(
            1 for thread in self.polling_threads.values()
            if thread.is_running()
        )

        if running_count >= self.max_groups:
            raise MaxPollingGroupsReachedError(
                f"Maximum polling groups ({self.max_groups}) already running"
            )

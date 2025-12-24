"""
Polling Group Manager

Singleton manager for controlling polling groups through REST API.
Manages PollingEngine lifecycle, tracks status, and persists state to database.
"""

import logging
import threading
from typing import Dict, Optional, List
from pathlib import Path
from datetime import datetime

from src.database.sqlite_manager import SQLiteManager
from src.plc.pool_manager import PoolManager
from .polling_engine import PollingEngine
from .oracle_writer_thread import OracleWriterThread
from .tag_value_cache import TagValueCache
from .exceptions import (
    PollingGroupNotFoundError,
    PollingGroupAlreadyRunningError,
    PollingGroupNotRunningError
)

logger = logging.getLogger(__name__)


class PollingGroupManager:
    """
    Singleton manager for polling groups

    Provides centralized control for starting/stopping polling groups,
    tracks runtime status, and persists state changes to database.

    Attributes:
        db_path: Path to SQLite database
        pool_manager: PLC connection pool manager
        polling_engine: PollingEngine instance
        _instance: Singleton instance
        _lock: Thread lock for singleton initialization
        _initialized: Initialization flag
    """

    _instance: Optional['PollingGroupManager'] = None
    _lock = threading.Lock()

    def __new__(cls, db_path: str = None, pool_manager: PoolManager = None):
        """
        Singleton pattern implementation

        Args:
            db_path: Path to SQLite database (required on first call)
            pool_manager: PoolManager instance (required on first call)

        Returns:
            Singleton instance of PollingGroupManager
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    if db_path is None or pool_manager is None:
                        raise ValueError(
                            "First initialization requires db_path and pool_manager"
                        )
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: str = None, pool_manager: PoolManager = None):
        """
        Initialize polling group manager

        변경된 점:
        - TagValueCache 인스턴스 생성 및 DB에서 로드
        - 메모리 기반 변경 감지 시스템 준비

        Args:
            db_path: Path to SQLite database
            pool_manager: PoolManager instance
        """
        # Skip if already initialized
        if self._initialized:
            return

        self.db_path = Path(db_path)
        self.pool_manager = pool_manager
        self.polling_engine: Optional[PollingEngine] = None
        self.oracle_writer: Optional[OracleWriterThread] = None
        self._db = SQLiteManager(str(self.db_path))

        # ✅ TagValueCache 생성 (메모리 기반 변경 감지용)
        self.tag_value_cache = TagValueCache()
        # 시작 시 SQLite에서 모든 활성 태그의 last_value 로드
        loaded_count = self.tag_value_cache.load_from_db(self._db)
        logger.info(f"TagValueCache loaded with {loaded_count} tag values")

        self._initialized = True

        logger.info(f"PollingGroupManager initialized: db={db_path}, cache_size={self.tag_value_cache.size()}")

    def initialize(self, enable_oracle: bool = True):
        """
        Initialize polling engine and load groups from database

        Creates PollingEngine instance and loads all active polling groups.
        Also starts Oracle writer thread with TagValueCache for fast change detection.
        Does not start any groups automatically.

        변경된 점:
        - OracleWriterThread 생성 시 tag_value_cache 주입 (메모리 기반 변경 감지)
        - 성능: 매 폴링마다 DB 조회 없음 (O(1) 메모리 캐시 사용)

        Args:
            enable_oracle: Enable Oracle writing (default: True)
        """
        if self.polling_engine is not None:
            logger.warning("PollingEngine already initialized")
            return

        logger.info("Initializing PollingEngine...")

        # Create polling engine
        self.polling_engine = PollingEngine(
            db_path=str(self.db_path),
            pool_manager=self.pool_manager
        )

        # Load groups from database
        self.polling_engine.initialize()

        logger.info("PollingEngine initialized successfully")

        # Start Oracle writer thread with TagValueCache
        logger.info("Starting Oracle writer thread with TagValueCache...")
        self.oracle_writer = OracleWriterThread(
            data_queue=self.polling_engine.data_queue,
            db_path=str(self.db_path),
            tag_value_cache=self.tag_value_cache,  # ✅ 캐시 주입
            batch_size=10,
            batch_timeout=5.0,
            enable_oracle=enable_oracle
        )
        self.oracle_writer.start()
        logger.info(f"Oracle writer thread started with cache size: {self.tag_value_cache.size()} tags")

    def start_group(self, group_id: int) -> Dict[str, any]:
        """
        Start a specific polling group by ID

        Args:
            group_id: Polling group ID from database

        Returns:
            Dictionary with start result:
            {
                "success": bool,
                "message": str,
                "group_id": int,
                "group_name": str,
                "new_status": str
            }

        Raises:
            PollingGroupNotFoundError: If group doesn't exist
            PollingGroupAlreadyRunningError: If group is already running
        """
        if self.polling_engine is None:
            self.initialize()

        # Get group name from database
        group_name = self._get_group_name(group_id)
        if not group_name:
            raise PollingGroupNotFoundError(f"Polling group {group_id} not found in database")

        try:
            # Start the group through PollingEngine
            self.polling_engine.start_group(group_name)

            # Update status in database (optional - can track in memory only)
            self._update_group_status(group_id, "running")

            logger.info(f"Started polling group: id={group_id}, name={group_name}")

            return {
                "success": True,
                "message": f"Polling group {group_name} started successfully",
                "group_id": group_id,
                "group_name": group_name,
                "new_status": "running"
            }

        except PollingGroupAlreadyRunningError as e:
            logger.warning(f"Group {group_id} already running: {e}")
            return {
                "success": False,
                "message": str(e),
                "group_id": group_id,
                "group_name": group_name,
                "new_status": "running"
            }

        except Exception as e:
            logger.error(f"Failed to start group {group_id}: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to start group: {str(e)}",
                "group_id": group_id,
                "group_name": group_name,
                "new_status": "error"
            }

    def stop_group(self, group_id: int, timeout: float = 5.0) -> Dict[str, any]:
        """
        Stop a specific polling group by ID

        Args:
            group_id: Polling group ID from database
            timeout: Maximum time to wait for thread termination (seconds)

        Returns:
            Dictionary with stop result:
            {
                "success": bool,
                "message": str,
                "group_id": int,
                "group_name": str,
                "new_status": str
            }

        Raises:
            PollingGroupNotFoundError: If group doesn't exist
            PollingGroupNotRunningError: If group is not running
        """
        if self.polling_engine is None:
            self.initialize()

        # Get group name from database
        group_name = self._get_group_name(group_id)
        if not group_name:
            raise PollingGroupNotFoundError(f"Polling group {group_id} not found in database")

        try:
            # Stop the group through PollingEngine
            self.polling_engine.stop_group(group_name, timeout=timeout)

            # Update status in database (optional)
            self._update_group_status(group_id, "stopped")

            logger.info(f"Stopped polling group: id={group_id}, name={group_name}")

            return {
                "success": True,
                "message": f"Polling group {group_name} stopped successfully",
                "group_id": group_id,
                "group_name": group_name,
                "new_status": "stopped"
            }

        except PollingGroupNotRunningError as e:
            logger.warning(f"Group {group_id} not running: {e}")
            return {
                "success": False,
                "message": str(e),
                "group_id": group_id,
                "group_name": group_name,
                "new_status": "stopped"
            }

        except Exception as e:
            logger.error(f"Failed to stop group {group_id}: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to stop group: {str(e)}",
                "group_id": group_id,
                "group_name": group_name,
                "new_status": "error"
            }

    def restart_group(self, group_id: int, timeout: float = 5.0) -> Dict[str, any]:
        """
        Restart a specific polling group by ID

        Stops the group (if running) and then starts it again.

        Args:
            group_id: Polling group ID from database
            timeout: Maximum time to wait for thread termination (seconds)

        Returns:
            Dictionary with restart result
        """
        if self.polling_engine is None:
            self.initialize()

        # Get group name from database
        group_name = self._get_group_name(group_id)
        if not group_name:
            raise PollingGroupNotFoundError(f"Polling group {group_id} not found in database")

        try:
            # Try to stop if running (ignore if not running)
            try:
                self.polling_engine.stop_group(group_name, timeout=timeout)
                logger.info(f"Stopped group {group_id} for restart")
            except PollingGroupNotRunningError:
                logger.info(f"Group {group_id} was not running, starting fresh")

            # Start the group
            self.polling_engine.start_group(group_name)

            # Update status in database
            self._update_group_status(group_id, "running")

            logger.info(f"Restarted polling group: id={group_id}, name={group_name}")

            return {
                "success": True,
                "message": f"Polling group {group_name} restarted successfully",
                "group_id": group_id,
                "group_name": group_name,
                "new_status": "running"
            }

        except Exception as e:
            logger.error(f"Failed to restart group {group_id}: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to restart group: {str(e)}",
                "group_id": group_id,
                "group_name": group_name,
                "new_status": "error"
            }

    def get_group_status(self, group_id: int) -> Dict[str, any]:
        """
        Get status of a specific polling group

        Args:
            group_id: Polling group ID from database

        Returns:
            Dictionary with group status

        Raises:
            PollingGroupNotFoundError: If group doesn't exist
        """
        if self.polling_engine is None:
            self.initialize()

        group_name = self._get_group_name(group_id)
        if not group_name:
            raise PollingGroupNotFoundError(f"Polling group {group_id} not found in database")

        # Get status from polling engine
        if group_name not in self.polling_engine.polling_threads:
            return {
                "group_id": group_id,
                "group_name": group_name,
                "status": "not_initialized",
                "message": "Group not loaded in polling engine"
            }

        thread = self.polling_engine.polling_threads[group_name]
        status = thread.get_status()

        return {
            "group_id": group_id,
            **status
        }

    def get_all_status(self) -> List[Dict[str, any]]:
        """
        Get status of all polling groups

        Returns:
            List of status dictionaries for all groups
        """
        if self.polling_engine is None:
            self.initialize()

        return self.polling_engine.get_status_all()

    def start_all(self):
        """Start all active polling groups"""
        if self.polling_engine is None:
            self.initialize()

        self.polling_engine.start_all()
        logger.info("Started all polling groups")

    def stop_all(self, timeout: float = 5.0):
        """Stop all running polling groups"""
        if self.polling_engine is None:
            return

        self.polling_engine.stop_all(timeout=timeout)
        logger.info("Stopped all polling groups")

    def shutdown(self):
        """
        Shutdown polling group manager

        Stops all running groups, Oracle writer, and cleans up resources.
        """
        logger.info("Shutting down PollingGroupManager...")

        # Stop polling engine (all groups)
        if self.polling_engine:
            self.polling_engine.shutdown()

        # Stop Oracle writer thread
        if self.oracle_writer:
            self.oracle_writer.stop(timeout=10.0)

        # Close database connection
        if self._db:
            self._db.close()

        logger.info("PollingGroupManager shutdown complete")

    def _get_group_name(self, group_id: int) -> Optional[str]:
        """
        Get group name from database by ID

        Args:
            group_id: Polling group ID

        Returns:
            Group name or None if not found
        """
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT group_name FROM polling_groups WHERE id = ?",
                (group_id,)
            )
            row = cursor.fetchone()
            return row[0] if row else None

    def _update_group_status(self, group_id: int, status: str):
        """
        Update group status in database (optional feature)

        Note: Current schema doesn't have status column.
        This is a placeholder for future enhancement.

        Args:
            group_id: Polling group ID
            status: Status string ("running", "stopped", "error")
        """
        # TODO: Add status column to polling_groups table if needed
        # For now, just log
        logger.debug(f"Group {group_id} status updated to: {status}")

    @classmethod
    def get_instance(cls) -> Optional['PollingGroupManager']:
        """
        Get singleton instance without initializing

        Returns:
            Instance if already initialized, None otherwise
        """
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """
        Reset singleton instance (for testing)

        Warning: Only use this in tests or during shutdown
        """
        with cls._lock:
            if cls._instance:
                cls._instance.shutdown()
            cls._instance = None
            logger.info("PollingGroupManager instance reset")

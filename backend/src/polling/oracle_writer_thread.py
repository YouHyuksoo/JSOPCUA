"""
Oracle Writer Thread

Background thread that consumes polling data from DataQueue and writes to Oracle DB.
Also updates SQLite tags table with last_value and last_updated_at.
"""

import threading
import logging
import time
from datetime import datetime
from typing import Optional
from queue import Empty

from .data_queue import DataQueue
from .models import PollingData
from src.oracle_writer.oracle_helper import OracleHelper
from src.database.sqlite_manager import SQLiteManager

logger = logging.getLogger(__name__)


class OracleWriterThread:
    """
    Background thread for writing polling data to Oracle DB

    Consumes PollingData from DataQueue and:
    1. Writes to Oracle DB (ICOM_PLC_TAG_LOG table)
    2. Updates SQLite tags table (last_value, last_updated_at)
    3. Optionally broadcasts to monitoring WebSocket

    Attributes:
        data_queue: DataQueue to consume from
        db_path: Path to SQLite database
        thread: Threading.Thread instance
        stop_event: Event to signal thread shutdown
        batch_size: Number of records to batch before writing
        batch_timeout: Maximum time to wait before flushing batch (seconds)
    """

    def __init__(
        self,
        data_queue: DataQueue,
        db_path: str,
        batch_size: int = 10,
        batch_timeout: float = 5.0,
        enable_oracle: bool = True
    ):
        """
        Initialize Oracle writer thread

        Args:
            data_queue: DataQueue to consume polling results from
            db_path: Path to SQLite database
            batch_size: Number of records to batch before writing to Oracle
            batch_timeout: Maximum seconds to wait before flushing batch
            enable_oracle: Enable/disable Oracle writing (for testing)
        """
        self.data_queue = data_queue
        self.db_path = db_path
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.enable_oracle = enable_oracle

        # Thread management
        self.thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self._running = False

        # SQLite connection
        self._sqlite_db = SQLiteManager(db_path)

        # Oracle connection
        self._oracle: Optional[OracleHelper] = None

        # Statistics
        self.records_written = 0
        self.records_failed = 0
        self.batches_written = 0
        self.last_write_time: Optional[datetime] = None

        logger.info(
            f"OracleWriterThread initialized: batch_size={batch_size}, "
            f"batch_timeout={batch_timeout}s, oracle_enabled={enable_oracle}"
        )

    def start(self):
        """Start the writer thread"""
        if self._running:
            logger.warning("Oracle writer thread already running")
            return

        self.stop_event.clear()
        self._running = True
        self.thread = threading.Thread(
            target=self._run,
            name="OracleWriter",
            daemon=False  # Ensure clean shutdown
        )
        self.thread.start()
        logger.info("Oracle writer thread started")

    def stop(self, timeout: float = 10.0):
        """
        Stop the writer thread gracefully

        Args:
            timeout: Maximum time to wait for thread termination (seconds)
        """
        if not self._running:
            logger.warning("Oracle writer thread not running")
            return

        logger.info("Stopping Oracle writer thread...")
        self.stop_event.set()

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=timeout)
            if self.thread.is_alive():
                logger.error(f"Oracle writer thread did not stop within {timeout}s")
            else:
                self._running = False
                logger.info("Oracle writer thread stopped")
        else:
            self._running = False

    def _run(self):
        """Main writer loop"""
        logger.info("Oracle writer thread running")

        # Connect to Oracle if enabled
        if self.enable_oracle:
            try:
                self._oracle = OracleHelper()
                self._oracle.connect()
                logger.info("Oracle connection established for writer thread")
            except Exception as e:
                logger.error(f"Failed to connect to Oracle: {e}", exc_info=True)
                logger.warning("Oracle writing disabled for this session")
                self.enable_oracle = False

        batch = []
        last_flush_time = time.time()

        try:
            while not self.stop_event.is_set():
                try:
                    # Get data from queue with timeout
                    polling_data = self.data_queue.get(timeout=1.0)

                    # Add to batch
                    batch.append(polling_data)

                    # Check if batch is full or timeout reached
                    current_time = time.time()
                    batch_full = len(batch) >= self.batch_size
                    timeout_reached = (current_time - last_flush_time) >= self.batch_timeout

                    if batch_full or timeout_reached:
                        # Write batch
                        self._write_batch(batch)
                        batch.clear()
                        last_flush_time = current_time

                except Empty:
                    # Queue timeout - check if we have pending data
                    if batch:
                        current_time = time.time()
                        if (current_time - last_flush_time) >= self.batch_timeout:
                            self._write_batch(batch)
                            batch.clear()
                            last_flush_time = current_time
                    continue

        except Exception as e:
            logger.error(f"Oracle writer thread crashed: {e}", exc_info=True)

        finally:
            # Flush remaining batch
            if batch:
                logger.info(f"Flushing {len(batch)} remaining records...")
                self._write_batch(batch)

            # Cleanup
            if self._oracle:
                self._oracle.disconnect()
            if self._sqlite_db:
                self._sqlite_db.close()

            self._running = False
            logger.info("Oracle writer thread exited")

    def _write_batch(self, batch: list[PollingData]):
        """
        Write a batch of polling data to Oracle and SQLite

        Args:
            batch: List of PollingData objects
        """
        if not batch:
            return

        try:
            # 1. Write to Oracle DB (if enabled)
            if self.enable_oracle and self._oracle:
                self._write_to_oracle(batch)

            # 2. Update SQLite tags table
            self._update_sqlite_tags(batch)

            # Update statistics
            self.records_written += len(batch)
            self.batches_written += 1
            self.last_write_time = datetime.now()

            logger.debug(
                f"Batch written: {len(batch)} records "
                f"(total: {self.records_written}, batches: {self.batches_written})"
            )

        except Exception as e:
            logger.error(f"Failed to write batch: {e}", exc_info=True)
            self.records_failed += len(batch)

    def _write_to_oracle(self, batch: list[PollingData]):
        """
        Write batch to Oracle tables (XSCADA_OPERATION and XSCADA_DATATAG_LOG)

        Args:
            batch: List of PollingData objects
        """
        if not self._oracle or not self._oracle.connection:
            return

        try:
            cursor = self._oracle.connection.cursor()

            # Separate data for Operation and Alarm/State tables
            operation_data = []
            datatag_log_data = []

            for polling_data in batch:
                category = polling_data.group_category.upper()

                for tag_address, tag_value in polling_data.tag_values.items():
                    # Get tag info (machine_code, log_mode, last_value)
                    tag_info = self._get_tag_info(
                        polling_data.plc_code,
                        tag_address
                    )

                    if not tag_info:
                        continue

                    machine_code = tag_info['machine_code']
                    log_mode = tag_info['log_mode']
                    last_value = tag_info['last_value']

                    # Check log_mode
                    if log_mode == 'NEVER':
                        continue

                    # Check if value changed (for ON_CHANGE mode)
                    value_changed = str(tag_value) != str(last_value) if last_value is not None else True

                    if log_mode == 'ON_CHANGE' and not value_changed:
                        continue

                    # Determine target table
                    if category == 'OPERATION':
                        # XSCADA_OPERATION table (always for OPERATION)
                        if machine_code:
                            name = f"{polling_data.plc_code}.Operation.{machine_code}.{tag_address}"
                        else:
                            name = f"{polling_data.plc_code}.Operation.UNKNOWN.{tag_address}"

                        operation_data.append({
                            'time': polling_data.timestamp,
                            'name': name,
                            'value': str(tag_value)
                        })

                    elif category in ('STATE', 'ALARM'):
                        # XSCADA_DATATAG_LOG table (for STATE and ALARM)
                        if machine_code:
                            name = f"{polling_data.plc_code}.{category.capitalize()}.{machine_code}.{tag_address}"
                        else:
                            name = f"{polling_data.plc_code}.{category.capitalize()}.UNKNOWN.{tag_address}"

                        # Get sequence for ID
                        cursor.execute("SELECT XSCADA_DATATAG_LOG_SEQ.NEXTVAL FROM DUAL")
                        seq_id = cursor.fetchone()[0]

                        datatag_log_data.append({
                            'id': seq_id,
                            'ctime': polling_data.timestamp,
                            'otime': polling_data.timestamp,
                            'datatag_name': name,
                            'datatag_type': 'D',  # D for Digital/Discrete
                            'value_str': str(tag_value),
                            'value_num': self._to_number(tag_value),
                            'value_raw': str(tag_value)
                        })

            # Insert into XSCADA_OPERATION
            if operation_data:
                operation_query = """
                    INSERT INTO XSCADA_OPERATION (TIME, NAME, VALUE)
                    VALUES (:time, :name, :value)
                """
                cursor.executemany(operation_query, operation_data)
                logger.debug(f"Wrote {len(operation_data)} records to XSCADA_OPERATION")

            # Insert into XSCADA_DATATAG_LOG (state and alarms)
            if datatag_log_data:
                datatag_query = """
                    INSERT INTO XSCADA_DATATAG_LOG (
                        ID, CTIME, OTIME, DATATAG_NAME, DATATAG_TYPE,
                        VALUE_STR, VALUE_NUM, VALUE_RAW
                    )
                    VALUES (
                        :id, :ctime, :otime, :datatag_name, :datatag_type,
                        :value_str, :value_num, :value_raw
                    )
                """
                cursor.executemany(datatag_query, datatag_log_data)
                logger.debug(f"Wrote {len(datatag_log_data)} records to XSCADA_DATATAG_LOG")

            self._oracle.connection.commit()

        except Exception as e:
            logger.error(f"Failed to write to Oracle: {e}", exc_info=True)
            if self._oracle and self._oracle.connection:
                self._oracle.connection.rollback()
            raise

    def _update_sqlite_tags(self, batch: list[PollingData]):
        """
        Update SQLite tags table with last_value and last_updated_at

        Args:
            batch: List of PollingData objects
        """
        try:
            with self._sqlite_db.get_connection() as conn:
                cursor = conn.cursor()

                for polling_data in batch:
                    for tag_address, tag_value in polling_data.tag_values.items():
                        # Update last_value and last_updated_at
                        cursor.execute("""
                            UPDATE tags
                            SET last_value = ?,
                                last_updated_at = ?
                            WHERE tag_address = ?
                              AND plc_code = ?
                        """, (
                            str(tag_value),
                            polling_data.timestamp.isoformat(),
                            tag_address,
                            polling_data.plc_code
                        ))

                conn.commit()

            logger.debug(f"Updated SQLite tags for {len(batch)} polling records")

        except Exception as e:
            logger.error(f"Failed to update SQLite tags: {e}", exc_info=True)
            raise

    def _get_tag_info(self, plc_code: str, tag_address: str) -> Optional[dict]:
        """
        Get tag information from SQLite

        Args:
            plc_code: PLC code
            tag_address: Tag address

        Returns:
            Dictionary with machine_code, log_mode, last_value or None
        """
        try:
            with self._sqlite_db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT t.machine_code, t.log_mode, t.last_value
                    FROM tags t
                    JOIN plc_connections pc ON t.plc_id = pc.id
                    WHERE pc.plc_code = ?
                      AND t.tag_address = ?
                """, (plc_code, tag_address))

                row = cursor.fetchone()
                if row:
                    return {
                        'machine_code': row[0],
                        'log_mode': row[1] if row[1] else 'ALWAYS',
                        'last_value': row[2]
                    }
                return None

        except Exception as e:
            logger.error(f"Failed to get tag info: {e}")
            return None

    def _to_number(self, value) -> Optional[float]:
        """
        Convert value to number for VALUE_NUM field

        Args:
            value: Value to convert

        Returns:
            Float value or None
        """
        try:
            # Handle boolean
            if isinstance(value, bool):
                return 1.0 if value else 0.0

            # Handle numeric
            return float(value)
        except (ValueError, TypeError):
            return None

    def get_stats(self) -> dict:
        """
        Get writer statistics

        Returns:
            Dictionary with statistics
        """
        return {
            "running": self._running,
            "records_written": self.records_written,
            "records_failed": self.records_failed,
            "batches_written": self.batches_written,
            "last_write_time": self.last_write_time.isoformat() if self.last_write_time else None,
            "queue_size": self.data_queue.size(),
            "oracle_enabled": self.enable_oracle
        }

    def is_running(self) -> bool:
        """Check if writer thread is running"""
        return self._running

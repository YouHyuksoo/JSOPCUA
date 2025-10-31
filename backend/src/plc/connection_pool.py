"""
PLC Connection Pool

PLC 연결을 풀로 관리하여 재사용성을 높이고 성능을 최적화합니다.
"""

import time
import queue
import threading
from typing import Optional
from datetime import datetime
from .mc3e_client import MC3EClient
from .exceptions import PLCConnectionError, PLCPoolExhaustedError
from . import logger


class PooledConnection:
    """
    Connection Pool에서 관리되는 PLC 연결 wrapper

    연결 생성 시간, 마지막 사용 시간, 에러 카운터 등을 추적합니다.
    """

    def __init__(self, client: MC3EClient, plc_id: int):
        """
        PooledConnection 초기화

        Args:
            client: MC3EClient 인스턴스
            plc_id: PLC ID
        """
        self.client = client
        self.plc_id = plc_id
        self.created_at = datetime.now()
        self.last_used = datetime.now()
        self.is_connected = False
        self.error_count = 0

    def mark_used(self):
        """마지막 사용 시간 갱신"""
        self.last_used = datetime.now()

    def increment_error(self):
        """에러 카운터 증가"""
        self.error_count += 1

    def reset_error(self):
        """에러 카운터 리셋"""
        self.error_count = 0

    def is_idle(self, timeout: int = 600) -> bool:
        """
        유휴 상태 확인

        Args:
            timeout: 유휴 타임아웃 (초, 기본 10분)

        Returns:
            유휴 상태 여부
        """
        idle_time = (datetime.now() - self.last_used).total_seconds()
        return idle_time > timeout

    def __str__(self) -> str:
        return f"PooledConnection(plc_id={self.plc_id}, created={self.created_at}, errors={self.error_count})"


class ConnectionPool:
    """
    PLC Connection Pool

    PLC당 최대 N개의 연결을 관리하고 재사용합니다.
    """

    def __init__(self, plc_id: int, plc_code: str, ip_address: str, port: int,
                 max_size: int = 5, timeout: int = 5, idle_timeout: int = 600):
        """
        ConnectionPool 초기화

        Args:
            plc_id: PLC ID
            plc_code: PLC 코드
            ip_address: PLC IP 주소
            port: PLC 포트
            max_size: 최대 연결 수 (기본 5)
            timeout: 연결 타임아웃 (초, 기본 5)
            idle_timeout: 유휴 연결 타임아웃 (초, 기본 600 = 10분)
        """
        self.plc_id = plc_id
        self.plc_code = plc_code
        self.ip_address = ip_address
        self.port = port
        self.max_size = max_size
        self.timeout = timeout
        self.idle_timeout = idle_timeout

        # 사용 가능한 연결 큐
        self._available: queue.Queue = queue.Queue(maxsize=max_size)

        # 현재 총 연결 수 (사용 중 + 사용 가능)
        self._total_connections = 0
        self._lock = threading.Lock()

        # 백그라운드 정리 스레드
        self._cleanup_thread: Optional[threading.Thread] = None
        self._stop_cleanup = threading.Event()

        logger.info(f"ConnectionPool created: {plc_code} (max_size={max_size})")

    def start_cleanup_thread(self):
        """백그라운드 정리 스레드 시작"""
        if self._cleanup_thread is None or not self._cleanup_thread.is_alive():
            self._stop_cleanup.clear()
            self._cleanup_thread = threading.Thread(
                target=self._cleanup_idle_connections,
                daemon=True,
                name=f"cleanup-{self.plc_code}"
            )
            self._cleanup_thread.start()
            logger.info(f"[{self.plc_code}] Cleanup thread started")

    def _cleanup_idle_connections(self):
        """유휴 연결 정리 (백그라운드 스레드)"""
        while not self._stop_cleanup.is_set():
            try:
                time.sleep(60)  # 1분마다 체크

                # 큐에서 연결을 꺼내서 유휴 상태 확인
                temp_connections = []

                while not self._available.empty():
                    try:
                        conn = self._available.get_nowait()

                        if conn.is_idle(self.idle_timeout):
                            # 유휴 연결 제거
                            conn.client.disconnect()
                            with self._lock:
                                self._total_connections -= 1
                            logger.info(f"[{self.plc_code}] Idle connection removed: {conn}")
                        else:
                            # 아직 유효한 연결은 보관
                            temp_connections.append(conn)

                    except queue.Empty:
                        break

                # 유효한 연결들을 다시 큐에 넣기
                for conn in temp_connections:
                    self._available.put(conn)

            except Exception as e:
                logger.error(f"[{self.plc_code}] Cleanup thread error: {e}")

    def get_connection(self, timeout: int = 5) -> PooledConnection:
        """
        Connection Pool에서 연결 가져오기

        사용 가능한 연결이 있으면 재사용하고, 없으면 새로 생성합니다.
        Pool이 가득 찬 경우 대기하거나 타임아웃 에러를 발생시킵니다.

        Args:
            timeout: 대기 타임아웃 (초)

        Returns:
            PooledConnection

        Raises:
            PLCPoolExhaustedError: Pool 고갈 시
            PLCConnectionError: 연결 실패 시
        """
        try:
            # 사용 가능한 연결이 있으면 재사용
            conn = self._available.get(timeout=timeout)
            conn.mark_used()
            logger.debug(f"[{self.plc_code}] Reusing connection from pool")
            return conn

        except queue.Empty:
            # 사용 가능한 연결이 없음
            with self._lock:
                if self._total_connections < self.max_size:
                    # 새 연결 생성 가능
                    self._total_connections += 1
                    logger.info(f"[{self.plc_code}] Creating new connection (total: {self._total_connections}/{self.max_size})")
                else:
                    # Pool 고갈
                    error_msg = f"Connection pool exhausted (max: {self.max_size})"
                    logger.error(f"[{self.plc_code}] {error_msg}")
                    raise PLCPoolExhaustedError(error_msg, self.plc_code)

            # 새 연결 생성
            client = MC3EClient(self.ip_address, self.port, self.plc_code, self.timeout)
            conn = PooledConnection(client, self.plc_id)

            try:
                client.connect()
                conn.is_connected = True
                conn.mark_used()
                return conn

            except Exception as e:
                # 연결 실패 시 카운터 감소
                with self._lock:
                    self._total_connections -= 1
                raise

    def return_connection(self, conn: PooledConnection):
        """
        Connection Pool에 연결 반환

        Args:
            conn: 반환할 PooledConnection
        """
        if conn is None:
            return

        try:
            # 연결이 유효한지 확인
            if conn.client.is_connected():
                self._available.put_nowait(conn)
                logger.debug(f"[{self.plc_code}] Connection returned to pool")
            else:
                # 연결이 끊어진 경우 제거
                with self._lock:
                    self._total_connections -= 1
                logger.warning(f"[{self.plc_code}] Disconnected connection removed from pool")

        except queue.Full:
            # 큐가 가득 찬 경우 (정상적으로는 발생하지 않음)
            conn.client.disconnect()
            with self._lock:
                self._total_connections -= 1
            logger.warning(f"[{self.plc_code}] Connection closed due to full queue")

    def close_all(self):
        """모든 연결 종료"""
        logger.info(f"[{self.plc_code}] Closing all connections...")

        # 정리 스레드 중지
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._stop_cleanup.set()
            self._cleanup_thread.join(timeout=2)

        # 모든 연결 종료
        while not self._available.empty():
            try:
                conn = self._available.get_nowait()
                conn.client.disconnect()
            except queue.Empty:
                break

        with self._lock:
            self._total_connections = 0

        logger.info(f"[{self.plc_code}] All connections closed")

    def get_stats(self) -> dict:
        """
        Connection Pool 통계 조회

        Returns:
            통계 정보 딕셔너리
        """
        return {
            'plc_code': self.plc_code,
            'max_size': self.max_size,
            'total_connections': self._total_connections,
            'available_connections': self._available.qsize(),
            'in_use_connections': self._total_connections - self._available.qsize()
        }

    def __str__(self) -> str:
        stats = self.get_stats()
        return (f"ConnectionPool({stats['plc_code']}: "
                f"{stats['in_use_connections']}/{stats['total_connections']} in use, "
                f"{stats['available_connections']} available)")

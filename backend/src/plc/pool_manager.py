"""
PLC Pool Manager

여러 PLC의 Connection Pool을 중앙에서 관리합니다.
"""

import sys
import os
from typing import Dict, Any, Optional, List

# 상위 디렉토리를 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.database.sqlite_manager import SQLiteManager
from .connection_pool import ConnectionPool
from .exceptions import PLCConnectionError, PLCInactiveError
from . import logger


class PoolManager:
    """
    멀티 PLC Connection Pool 관리자

    SQLite DB에서 PLC 목록을 읽어서 각 PLC마다 Connection Pool을 생성하고 관리합니다.
    """

    def __init__(self, db_path: str, pool_size: int = 5):
        """
        PoolManager 초기화

        Args:
            db_path: SQLite 데이터베이스 경로
            pool_size: PLC당 Connection Pool 크기 (기본 5)
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self._pools: Dict[str, ConnectionPool] = {}
        self._plc_info: Dict[str, dict] = {}
        self._db: Optional[SQLiteManager] = None

        logger.info(f"PoolManager initialized (pool_size={pool_size})")

    def initialize(self):
        """
        SQLite DB에서 모든 활성 PLC를 로드하고 Connection Pool 생성

        Raises:
            Exception: DB 연결 또는 Pool 생성 실패 시
        """
        logger.info("Initializing PoolManager from database...")

        self._db = SQLiteManager(self.db_path)

        try:
            # 활성 PLC 목록 조회
            query = """
                SELECT id, plc_code, plc_name, ip_address, port,
                       protocol, connection_timeout, is_active
                FROM plc_connections
                WHERE is_active = 1
            """
            plcs = self._db.execute_query(query)

            logger.info(f"Found {len(plcs)} active PLC(s)")

            # 각 PLC에 대해 Connection Pool 생성
            for plc in plcs:
                plc_code = plc['plc_code']
                self._plc_info[plc_code] = plc

                # Connection Pool 생성
                pool = ConnectionPool(
                    plc_id=plc['id'],
                    plc_code=plc_code,
                    ip_address=plc['ip_address'],
                    port=plc['port'],
                    max_size=self.pool_size,
                    timeout=plc['connection_timeout']
                )

                # 백그라운드 정리 스레드 시작
                pool.start_cleanup_thread()

                self._pools[plc_code] = pool

                logger.info(f"Pool created for PLC: {plc_code} ({plc['ip_address']}:{plc['port']})")

            logger.info(f"PoolManager initialized: {len(self._pools)} PLC(s)")

        except Exception as e:
            logger.error(f"Failed to initialize PoolManager: {e}")
            raise

    def read_single(self, plc_code: str, tag_address: str) -> Any:
        """
        단일 태그 읽기 (Connection Pool 사용)

        Args:
            plc_code: PLC 코드
            tag_address: 태그 주소

        Returns:
            태그 값

        Raises:
            PLCInactiveError: PLC가 비활성 상태
            PLCConnectionError: 연결 실패
        """
        # PLC Pool 가져오기
        pool = self._get_pool(plc_code)

        # Pool에서 연결 가져오기
        conn = None
        try:
            conn = pool.get_connection()

            # 태그 읽기
            value = conn.client.read_single(tag_address)

            # 에러 카운터 리셋
            conn.reset_error()

            return value

        except Exception as e:
            # 에러 카운터 증가
            if conn:
                conn.increment_error()
            raise

        finally:
            # 연결 반환
            if conn:
                pool.return_connection(conn)

    def read_batch(self, plc_code: str, tag_addresses: List[str]) -> Dict[str, Any]:
        """
        배치 태그 읽기 (Connection Pool 사용)

        Args:
            plc_code: PLC 코드
            tag_addresses: 태그 주소 리스트

        Returns:
            태그 주소 → 값 매핑 딕셔너리

        Raises:
            PLCInactiveError: PLC가 비활성 상태
            PLCConnectionError: 연결 실패
        """
        # PLC Pool 가져오기
        pool = self._get_pool(plc_code)

        # Pool에서 연결 가져오기
        conn = None
        try:
            conn = pool.get_connection()

            # 배치 읽기
            values = conn.client.read_batch(tag_addresses)

            # 에러 카운터 리셋
            conn.reset_error()

            return values

        except Exception as e:
            # 에러 카운터 증가
            if conn:
                conn.increment_error()
            raise

        finally:
            # 연결 반환
            if conn:
                pool.return_connection(conn)

    def _get_pool(self, plc_code: str) -> ConnectionPool:
        """
        PLC 코드로 Connection Pool 가져오기

        Args:
            plc_code: PLC 코드

        Returns:
            ConnectionPool

        Raises:
            PLCInactiveError: PLC가 없거나 비활성 상태
        """
        if plc_code not in self._pools:
            error_msg = f"PLC not found or inactive: {plc_code}"
            logger.error(error_msg)
            raise PLCInactiveError(error_msg, plc_code)

        return self._pools[plc_code]

    def get_plc_count(self) -> int:
        """
        관리 중인 PLC 수 반환

        Returns:
            PLC 수
        """
        return len(self._pools)

    def get_pool_stats(self, plc_code: str = None) -> Dict[str, Any]:
        """
        Connection Pool 통계 조회

        Args:
            plc_code: PLC 코드 (None이면 전체)

        Returns:
            통계 정보 딕셔너리
        """
        if plc_code:
            pool = self._get_pool(plc_code)
            return pool.get_stats()

        # 전체 통계
        stats = {}
        for code, pool in self._pools.items():
            stats[code] = pool.get_stats()

        return stats

    def shutdown(self):
        """
        모든 Connection Pool 종료

        모든 PLC 연결을 정리하고 DB 연결을 닫습니다.
        """
        logger.info("Shutting down PoolManager...")

        # 모든 Pool 종료
        for plc_code, pool in self._pools.items():
            try:
                pool.close_all()
            except Exception as e:
                logger.error(f"Error closing pool for {plc_code}: {e}")

        self._pools.clear()
        self._plc_info.clear()

        # DB 연결 종료
        if self._db:
            self._db.close()

        logger.info("PoolManager shutdown complete")

    def __enter__(self):
        """Context manager enter"""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.shutdown()

    def __del__(self):
        """Destructor - 리소스 정리"""
        self.shutdown()

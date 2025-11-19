"""
SQLite Database Manager for JSScada.
Handles connection, queries, and database operations.
"""
import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple, Any
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class SQLiteManager:
    """SQLite 데이터베이스 연결 및 쿼리 관리"""

    def __init__(self, db_path: str):
        """
        SQLite 데이터베이스 매니저 초기화

        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"SQLiteManager initialized with db_path: {self.db_path}")

    @contextmanager
    def get_connection(self):
        """
        데이터베이스 연결 컨텍스트 매니저

        Yields:
            sqlite3.Connection: SQLite 연결 객체

        Example:
            with manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM lines")
        """
        conn = None
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            conn.row_factory = sqlite3.Row
            # Enable Foreign Key constraints
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def execute_script(self, sql_script: str) -> None:
        """
        SQL 스크립트 실행 (여러 개의 SQL 문)

        Args:
            sql_script: 실행할 SQL 스크립트

        Raises:
            sqlite3.Error: SQL 실행 오류
        """
        with self.get_connection() as conn:
            try:
                conn.executescript(sql_script)
                conn.commit()
                logger.info("SQL script executed successfully")
            except sqlite3.Error as e:
                logger.error(f"Error executing SQL script: {e}")
                raise

    def execute_query(
        self,
        query: str,
        params: Optional[Tuple[Any, ...]] = None
    ) -> List[sqlite3.Row]:
        """
        SELECT 쿼리 실행

        Args:
            query: SQL 쿼리
            params: 쿼리 파라미터 (선택사항)

        Returns:
            List[sqlite3.Row]: 쿼리 결과 목록

        Example:
            results = manager.execute_query(
                "SELECT * FROM lines WHERE is_active = ?",
                (True,)
            )
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            logger.debug(f"Query returned {len(results)} rows")
            return results

    def execute_update(
        self,
        query: str,
        params: Optional[Tuple[Any, ...]] = None
    ) -> int:
        """
        INSERT, UPDATE, DELETE 쿼리 실행

        Args:
            query: SQL 쿼리
            params: 쿼리 파라미터 (선택사항)

        Returns:
            int: 영향받은 행의 수

        Example:
            rows_affected = manager.execute_update(
                "UPDATE lines SET is_active = ? WHERE id = ?",
                (False, 1)
            )
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            rows_affected = cursor.rowcount
            logger.debug(f"Query affected {rows_affected} rows")
            return rows_affected

    def execute_many(
        self,
        query: str,
        params_list: List[Tuple[Any, ...]]
    ) -> int:
        """
        배치 INSERT/UPDATE 실행 (executemany)

        Args:
            query: SQL 쿼리
            params_list: 파라미터 리스트

        Returns:
            int: 영향받은 행의 수

        Example:
            manager.execute_many(
                "INSERT INTO tags (plc_id, tag_address, tag_name) VALUES (?, ?, ?)",
                [(1, 'D100', 'Temp1'), (1, 'D101', 'Temp2')]
            )
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            rows_affected = cursor.rowcount
            logger.info(f"Batch query affected {rows_affected} rows")
            return rows_affected

    def get_last_insert_id(self) -> int:
        """
        마지막으로 삽입된 행의 ID 반환

        Returns:
            int: 마지막 INSERT된 행의 ID

        Note:
            이 메서드는 get_connection() 컨텍스트 내에서 사용해야 합니다.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            return cursor.lastrowid

    def table_exists(self, table_name: str) -> bool:
        """
        테이블 존재 여부 확인

        Args:
            table_name: 테이블 이름

        Returns:
            bool: 테이블 존재 여부
        """
        query = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name=?
        """
        results = self.execute_query(query, (table_name,))
        return len(results) > 0

    def get_table_names(self) -> List[str]:
        """
        모든 테이블 이름 조회

        Returns:
            List[str]: 테이블 이름 목록
        """
        query = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """
        results = self.execute_query(query)
        return [row['name'] for row in results]

    def get_table_count(self, table_name: str) -> int:
        """
        테이블의 행 개수 조회

        Args:
            table_name: 테이블 이름

        Returns:
            int: 행 개수
        """
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        results = self.execute_query(query)
        return results[0]['count'] if results else 0

    def database_exists(self) -> bool:
        """
        데이터베이스 파일 존재 여부 확인

        Returns:
            bool: 데이터베이스 파일 존재 여부
        """
        return self.db_path.exists()

    def close(self):
        """
        SQLiteManager 인스턴스 종료 (호환성을 위한 메서드)
        
        Note:
            SQLiteManager는 매번 새로운 연결을 생성하므로
            인스턴스 레벨에서 닫을 연결이 없습니다.
            이 메서드는 기존 코드와의 호환성을 위해 제공됩니다.
        """
        logger.debug("SQLiteManager.close() called (no-op, connections are managed per-request)")
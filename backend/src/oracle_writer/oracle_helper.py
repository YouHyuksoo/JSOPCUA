"""
Oracle Database Helper for SCADA System Synchronization

Oracle 테이블과 SQLite 동기화를 위한 헬퍼 클래스

매핑 정보:
- ICOM_MACHINE_MASTER (Oracle) ↔ machines (SQLite): 설비 정보
- ICOM_PLC_MASTER (Oracle) ↔ plc_connections (SQLite): PLC 정보
- ICOM_PLC_TAG_MASTER (Oracle) ↔ tags (SQLite): 태그 정보
- ICOM_WORKSTAGE_MASTER (Oracle) ↔ processes (SQLite): 공정 정보
"""

import oracledb
from typing import List, Dict, Optional
from src.oracle_writer.config import load_config_from_env
from src.oracle_writer.table_mapping import TableMapping, get_mapping, get_all_mappings
from src.config.logging_config import get_logger

logger = get_logger(__name__)


class OracleHelper:
    """Helper class for Oracle database operations"""

    def __init__(self):
        """Initialize Oracle helper with config from environment"""
        self.config = load_config_from_env()
        self.connection = None

    def connect(self):
        """
        Establish connection to Oracle database

        Returns:
            oracledb.Connection: Active database connection

        Raises:
            oracledb.Error: If connection fails
        """
        try:
            # Log connection attempt with detailed credentials
            logger.info(f"Oracle 접속 시도:")
            logger.info(f"  - Host: {self.config.host}")
            logger.info(f"  - Port: {self.config.port}")
            logger.info(f"  - Service Name: {self.config.service_name}")
            logger.info(f"  - Username: {self.config.username}")
            logger.info(f"  - Password Length: {len(self.config.password)} characters")
            logger.info(f"  - Password Preview: {self._mask_password(self.config.password)}")
            logger.info(f"  - DSN: {self.config.get_dsn()}")

            self.connection = oracledb.connect(
                user=self.config.username,
                password=self.config.password,
                dsn=self.config.get_dsn()
            )
            logger.info(f"✓ Oracle 연결 성공: {self.config.get_connect_string()}")
            return self.connection
        except oracledb.Error as e:
            # Log detailed error information
            logger.error("=" * 80)
            logger.error("✗ Oracle 연결 실패")
            logger.error(f"  - Host: {self.config.host}")
            logger.error(f"  - Port: {self.config.port}")
            logger.error(f"  - Service Name: {self.config.service_name}")
            logger.error(f"  - Username: {self.config.username}")
            logger.error(f"  - Password Length: {len(self.config.password)} characters")
            logger.error(f"  - Password Preview: {self._mask_password(self.config.password)}")
            logger.error(f"  - DSN: {self.config.get_dsn()}")
            logger.error(f"  - Error Code: {e.args[0].code if hasattr(e.args[0], 'code') else 'N/A'}")
            logger.error(f"  - Error Message: {str(e)}")
            logger.error("=" * 80)
            raise

    def _mask_password(self, password: str) -> str:
        """
        Create a partially masked password for debugging
        Shows first 2 and last 2 characters, masks the middle

        Examples:
            "MyPassword123" -> "My********23"
            "abc" -> "a*c"
            "ab" -> "**"
            "a" -> "*"

        Args:
            password: Password to mask

        Returns:
            Partially masked password string
        """
        if not password:
            return "(empty)"

        length = len(password)

        if length == 1:
            return "*"
        elif length == 2:
            return "**"
        elif length == 3:
            return f"{password[0]}*{password[-1]}"
        elif length <= 6:
            # For short passwords, show first and last char only
            return f"{password[0]}{'*' * (length - 2)}{password[-1]}"
        else:
            # For longer passwords, show first 2 and last 2 chars
            middle_length = length - 4
            return f"{password[:2]}{'*' * middle_length}{password[-2:]}"

    def disconnect(self):
        """Close Oracle database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Oracle connection closed")

    def fetch_machines(self) -> List[Dict]:
        """
        Fetch all active machines from Oracle ICOM_MACHINE_MASTER table

        Returns:
            List of dictionaries with machine data:
            - machine_code: Machine code (max 20 chars)
            - machine_name: Machine name (max 200 chars)
            - machine_location: Location (max 50 chars)
            - use_yn: Active status ('Y' or 'N')

        Raises:
            oracledb.Error: If query fails
        """
        if not self.connection:
            self.connect()

        try:
            cursor = self.connection.cursor()

            # Query active machines from Oracle
            query = """
                SELECT
                    MACHINE_CODE,
                    MACHINE_NAME,
                    MACHINE_LOCATION,
                    USE_YN
                FROM ICOM_MACHINE_MASTER
                WHERE USE_YN = 'Y'
                ORDER BY MACHINE_CODE
            """

            cursor.execute(query)
            rows = cursor.fetchall()

            machines = []
            for row in rows:
                machine = {
                    'machine_code': row[0].strip() if row[0] else None,
                    'machine_name': row[1].strip() if row[1] else None,
                    'machine_location': row[2].strip() if row[2] and row[2] != '*' else None,
                    'use_yn': row[3]
                }

                # Skip if machine_code or machine_name is missing
                if not machine['machine_code'] or not machine['machine_name']:
                    logger.warning(f"Skipping machine with missing code or name: {row}")
                    continue

                machines.append(machine)

            logger.info(f"Fetched {len(machines)} active machines from Oracle")
            cursor.close()

            return machines

        except oracledb.Error as e:
            logger.error(f"Failed to fetch machines from Oracle: {e}")
            raise

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

    def fetch_data_by_mapping(self, mapping: TableMapping) -> List[Dict]:
        """
        매핑 정보를 사용하여 Oracle 데이터를 조회하고 SQLite 형식으로 변환

        Args:
            mapping: TableMapping 객체

        Returns:
            SQLite 형식으로 변환된 데이터 리스트

        Raises:
            oracledb.Error: If query fails
        """
        if not self.connection:
            self.connect()

        try:
            cursor = self.connection.cursor()

            # Oracle 쿼리 생성 및 실행
            query = mapping.get_oracle_select_query()
            logger.info(f"Executing Oracle query: {query}")
            cursor.execute(query)

            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            # 데이터 변환
            result = []
            for row in rows:
                # Oracle 행을 딕셔너리로 변환
                oracle_row = dict(zip(columns, row))

                # SQLite 형식으로 변환
                sqlite_row = mapping.transform_row(oracle_row)

                # 필수 필드 검증 (key columns)
                skip = False
                for key_col in mapping.key_columns:
                    sqlite_col = mapping.column_mapping[key_col]
                    if not sqlite_row.get(sqlite_col):
                        logger.warning(
                            f"Skipping row with missing key column {sqlite_col}: {oracle_row}"
                        )
                        skip = True
                        break

                if not skip:
                    result.append(sqlite_row)

            logger.info(
                f"Fetched {len(result)} rows from {mapping.oracle_table} "
                f"(total: {len(rows)}, skipped: {len(rows) - len(result)})"
            )
            cursor.close()

            return result

        except oracledb.Error as e:
            logger.error(f"Failed to fetch data from {mapping.oracle_table}: {e}")
            raise

    def fetch_plcs(self) -> List[Dict]:
        """
        Fetch all active PLCs from Oracle ICOM_PLC_MASTER table

        SQLite plc_connections 테이블과 동기화하기 위한 데이터 조회

        Returns:
            List of dictionaries with PLC data:
            - plc_code: PLC 코드
            - plc_name: PLC명
            - ip_address: IP 주소
            - port: 포트 번호
            - network_no: 네트워크 번호
            - station_no: 국번

        Raises:
            oracledb.Error: If query fails
        """
        if not self.connection:
            self.connect()

        try:
            cursor = self.connection.cursor()

            query = """
                SELECT
                    PLC_CODE,
                    PLC_NAME,
                    PLC_IP,
                    PLC_PORT,
                    PLC_NETWORK_NO,
                    PLC_STATION_NO
                FROM ICOM_PLC_MASTER
                WHERE PLC_USE_YN = 'Y'
                ORDER BY PLC_CODE
            """

            cursor.execute(query)
            rows = cursor.fetchall()

            plcs = []
            for row in rows:
                plc = {
                    'plc_code': row[0].strip() if row[0] else None,
                    'plc_name': row[1].strip() if row[1] and row[1] != '*' else None,
                    'ip_address': row[2].strip() if row[2] and row[2] != '*' else '',
                    'port': int(row[3]) if row[3] and row[3] != '*' else 5010,
                    'network_no': int(row[4]) if row[4] is not None else 0,
                    'station_no': int(row[5]) if row[5] is not None else 0
                }

                if not plc['plc_code'] or not plc['plc_name']:
                    logger.warning(f"Skipping PLC with missing code or name: {row}")
                    continue

                plcs.append(plc)

            logger.info(f"Fetched {len(plcs)} active PLCs from Oracle")
            cursor.close()

            return plcs

        except oracledb.Error as e:
            logger.error(f"Failed to fetch PLCs from Oracle: {e}")
            raise

    def fetch_tags(self) -> List[Dict]:
        """
        Fetch all active tags from Oracle ICOM_PLC_TAG_MASTER table

        SQLite tags 테이블과 동기화하기 위한 데이터 조회

        Returns:
            List of dictionaries with tag data:
            - plc_code: PLC 코드
            - machine_code: 설비 코드
            - tag_address: 태그 주소
            - tag_name: 태그명
            - tag_type: 데이터 타입
            - unit: 단위
            - scale: 스케일
            - min_value: 최소값
            - max_value: 최대값

        Raises:
            oracledb.Error: If query fails
        """
        if not self.connection:
            self.connect()

        try:
            cursor = self.connection.cursor()

            query = """
                SELECT
                    PLC_CODE,
                    MACHINE_CODE,
                    TAG_ADDRESS,
                    TAG_NAME,
                    TAG_DATA_TYPE,
                    TAG_UNIT,
                    TAG_SCALE,
                    TARGET_MIN_VALUE,
                    TARGET_MAX_VALUE
                FROM ICOM_PLC_TAG_MASTER
                WHERE TAG_USE_YN = 'Y'
                ORDER BY PLC_CODE, TAG_ADDRESS
            """

            cursor.execute(query)
            rows = cursor.fetchall()

            tags = []
            for row in rows:
                tag = {
                    'plc_code': row[0].strip() if row[0] else None,
                    'machine_code': row[1].strip() if row[1] and row[1] != '*' else None,
                    'tag_address': row[2].strip() if row[2] else None,
                    'tag_name': row[3].strip() if row[3] else None,
                    'tag_type': row[4].strip() if row[4] else 'INT',
                    'unit': row[5].strip() if row[5] else '',
                    'scale': float(row[6]) if row[6] else 1.0,
                    'min_value': float(row[7]) if row[7] is not None else None,
                    'max_value': float(row[8]) if row[8] is not None else None
                }

                if not tag['plc_code'] or not tag['tag_address'] or not tag['tag_name']:
                    logger.warning(f"Skipping tag with missing required fields: {row}")
                    continue

                tags.append(tag)

            logger.info(f"Fetched {len(tags)} active tags from Oracle")
            cursor.close()

            return tags

        except oracledb.Error as e:
            logger.error(f"Failed to fetch tags from Oracle: {e}")
            raise

    def fetch_processes(self) -> List[Dict]:
        """
        Fetch all active processes from Oracle ICOM_WORKSTAGE_MASTER table

        SQLite processes 테이블과 동기화하기 위한 데이터 조회

        Returns:
            List of dictionaries with process data:
            - process_code: 공정 코드
            - process_name: 공정명
            - description: 설명
            - sequence_order: 순서

        Raises:
            oracledb.Error: If query fails
        """
        if not self.connection:
            self.connect()

        try:
            cursor = self.connection.cursor()

            query = """
                SELECT
                    WORKSTAGE_CODE,
                    WORKSTAGE_NAME,
                    WORKSTAGE_DESC,
                    WORKSTAGE_SEQ
                FROM ICOM_WORKSTAGE_MASTER
                WHERE USE_YN = 'Y'
                ORDER BY WORKSTAGE_SEQ, WORKSTAGE_CODE
            """

            cursor.execute(query)
            rows = cursor.fetchall()

            processes = []
            for row in rows:
                process = {
                    'process_code': row[0].strip() if row[0] else None,
                    'process_name': row[1].strip() if row[1] else None,
                    'description': row[2].strip() if row[2] and row[2] != '*' else '',
                    'sequence_order': int(row[3]) if row[3] is not None else 0
                }

                if not process['process_code'] or not process['process_name']:
                    logger.warning(f"Skipping process with missing code or name: {row}")
                    continue

                processes.append(process)

            logger.info(f"Fetched {len(processes)} active processes from Oracle")
            cursor.close()

            return processes

        except oracledb.Error as e:
            logger.error(f"Failed to fetch processes from Oracle: {e}")
            raise


# ==============================================================================
# Convenience functions (간편 함수)
# ==============================================================================

def get_oracle_machines() -> List[Dict]:
    """
    Convenience function to fetch machines from Oracle
    ICOM_MACHINE_MASTER (Oracle) → machines (SQLite)

    Returns:
        List of machine dictionaries

    Raises:
        Exception: If Oracle connection or query fails
    """
    mapping = get_mapping("machines")
    with OracleHelper() as oracle:
        return oracle.fetch_data_by_mapping(mapping)


def get_oracle_plcs() -> List[Dict]:
    """
    Convenience function to fetch PLCs from Oracle
    ICOM_PLC_MASTER (Oracle) → plc_connections (SQLite)

    Returns:
        List of PLC dictionaries

    Raises:
        Exception: If Oracle connection or query fails
    """
    mapping = get_mapping("plc_connections")
    with OracleHelper() as oracle:
        return oracle.fetch_data_by_mapping(mapping)


def get_oracle_tags() -> List[Dict]:
    """
    Convenience function to fetch tags from Oracle
    ICOM_PLC_TAG_MASTER (Oracle) → tags (SQLite)

    Returns:
        List of tag dictionaries

    Raises:
        Exception: If Oracle connection or query fails
    """
    mapping = get_mapping("tags")
    with OracleHelper() as oracle:
        return oracle.fetch_data_by_mapping(mapping)


def get_oracle_processes() -> List[Dict]:
    """
    Convenience function to fetch processes from Oracle
    ICOM_WORKSTAGE_MASTER (Oracle) → processes (SQLite)

    Returns:
        List of process dictionaries

    Raises:
        Exception: If Oracle connection or query fails
    """
    mapping = get_mapping("processes")
    with OracleHelper() as oracle:
        return oracle.fetch_data_by_mapping(mapping)

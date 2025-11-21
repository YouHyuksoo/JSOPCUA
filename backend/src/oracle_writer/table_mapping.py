"""
Oracle ↔ SQLite Table Mapping Configuration

Oracle 테이블과 SQLite 테이블 간의 매핑 정보를 정의합니다.
각 테이블마다 컬럼 매핑, 데이터 변환 규칙, 동기화 조건을 설정합니다.
"""

from typing import Dict, List, Callable, Any, Optional


class TableMapping:
    """테이블 매핑 설정 클래스"""

    def __init__(
        self,
        oracle_table: str,
        sqlite_table: str,
        key_columns: List[str],
        column_mapping: Dict[str, str],
        value_transformers: Optional[Dict[str, Callable]] = None,
        sync_filter: Optional[str] = None
    ):
        """
        Args:
            oracle_table: Oracle 테이블명
            sqlite_table: SQLite 테이블명
            key_columns: 기본키 컬럼 (Oracle 기준)
            column_mapping: 컬럼 매핑 {oracle_column: sqlite_column}
            value_transformers: 값 변환 함수 {sqlite_column: transformer_func}
            sync_filter: Oracle SELECT 시 WHERE 조건
        """
        self.oracle_table = oracle_table
        self.sqlite_table = sqlite_table
        self.key_columns = key_columns
        self.column_mapping = column_mapping
        self.value_transformers = value_transformers or {}
        self.sync_filter = sync_filter

    def get_oracle_select_query(self) -> str:
        """Oracle SELECT 쿼리 생성"""
        columns = ", ".join(self.column_mapping.keys())
        query = f"SELECT {columns} FROM {self.oracle_table}"
        if self.sync_filter:
            query += f" WHERE {self.sync_filter}"
        return query

    def transform_row(self, oracle_row: Dict[str, Any]) -> Dict[str, Any]:
        """Oracle 행을 SQLite 형식으로 변환"""
        sqlite_row = {}

        for oracle_col, sqlite_col in self.column_mapping.items():
            value = oracle_row.get(oracle_col)

            # 값 변환 함수 적용
            if sqlite_col in self.value_transformers:
                transformer = self.value_transformers[sqlite_col]
                value = transformer(value)

            sqlite_row[sqlite_col] = value

        return sqlite_row


# ==============================================================================
# 값 변환 함수들
# ==============================================================================

def yn_to_bool(value: Optional[str]) -> int:
    """Y/N → 1/0 변환"""
    if value is None:
        return 1
    return 1 if value == 'Y' else 0


def strip_or_none(value: Optional[str]) -> Optional[str]:
    """문자열 trim, 빈 문자열이면 None"""
    if value is None:
        return None
    stripped = value.strip()
    if stripped == '' or stripped == '*':
        return None
    return stripped


def int_or_default(default: int = 0) -> Callable:
    """정수 변환, 실패 시 기본값"""
    def transformer(value: Any) -> int:
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    return transformer


def float_or_default(default: float = 1.0) -> Callable:
    """실수 변환, 실패 시 기본값"""
    def transformer(value: Any) -> float:
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    return transformer


# ==============================================================================
# 테이블 매핑 정의
# ==============================================================================

# 1. ICOM_MACHINE_MASTER → machines
MACHINE_MAPPING = TableMapping(
    oracle_table="ICOM_MACHINE_MASTER",
    sqlite_table="machines",
    key_columns=["MACHINE_CODE"],
    column_mapping={
        "MACHINE_CODE": "machine_code",
        "MACHINE_NAME": "machine_name",
        "MACHINE_LOCATION": "location",
        "USE_YN": "is_active"
    },
    value_transformers={
        "machine_code": strip_or_none,
        "machine_name": strip_or_none,
        "location": strip_or_none,
        "is_active": yn_to_bool
    },
    sync_filter="USE_YN = 'Y'"
)


# 2. ICOM_PLC_MASTER → plc_connections
PLC_MAPPING = TableMapping(
    oracle_table="ICOM_PLC_MASTER",
    sqlite_table="plc_connections",
    key_columns=["PLC_CODE"],
    column_mapping={
        "PLC_CODE": "plc_code",
        "PLC_NAME": "plc_name",
        "PLC_SPEC": "plc_spec",
        "PLC_TYPE": "plc_type",
        "PLC_IP": "ip_address",
        "PLC_PORT": "port",
        "PLC_NETWORK_NO": "network_no",
        "PLC_STATION_NO": "station_no",
        "PLC_USE_YN": "is_active"
    },
    value_transformers={
        "plc_code": strip_or_none,
        "plc_name": strip_or_none,
        "plc_spec": strip_or_none,
        "plc_type": strip_or_none,
        "ip_address": strip_or_none,
        "port": int_or_default(5010),
        "network_no": int_or_default(0),
        "station_no": int_or_default(0),
        "is_active": yn_to_bool
    },
    sync_filter="PLC_USE_YN = 'Y'"
)


# 3. ICOM_PLC_TAG_MASTER → tags
TAG_MAPPING = TableMapping(
    oracle_table="ICOM_PLC_TAG_MASTER",
    sqlite_table="tags",
    key_columns=["PLC_CODE", "TAG_ADDRESS"],
    column_mapping={
        "PLC_CODE": "plc_code",
        "MACHINE_CODE": "machine_code",
        "TAG_ADDRESS": "tag_address",
        "TAG_NAME": "tag_name",
        "TAG_TYPE": "tag_category",
        "TAG_DATA_TYPE": "tag_type",
        "TAG_UNIT": "unit",
        "TAG_SCALE": "scale",
        "TARGET_MIN_VALUE": "min_value",
        "TARGET_MAX_VALUE": "max_value",
        "TAG_USE_YN": "is_active"
    },
    value_transformers={
        "plc_code": strip_or_none,
        "machine_code": strip_or_none,
        "tag_address": strip_or_none,
        "tag_name": strip_or_none,
        "tag_category": strip_or_none,
        "tag_type": lambda v: strip_or_none(v) or "INT",
        "unit": lambda v: strip_or_none(v) or "",
        "scale": float_or_default(1.0),
        "min_value": lambda v: None if v is None else float(v),
        "max_value": lambda v: None if v is None else float(v),
        "is_active": yn_to_bool
    },
    sync_filter="TAG_USE_YN = 'Y'"
)


# 4. ICOM_WORKSTAGE_MASTER → workstages
WORKSTAGE_MAPPING = TableMapping(
    oracle_table="ICOM_WORKSTAGE_MASTER",
    sqlite_table="workstages",
    key_columns=["WORKSTAGE_CODE"],
    column_mapping={
        "WORKSTAGE_CODE": "workstage_code",
        "WORKSTAGE_NAME": "workstage_name",
        "WORKSTAGE_DESC": "description",
        "WORKSTAGE_SEQ": "sequence_order",
        "USE_YN": "is_active"
    },
    value_transformers={
        "workstage_code": strip_or_none,
        "workstage_name": strip_or_none,
        "description": lambda v: strip_or_none(v) or "",
        "sequence_order": int_or_default(0),
        "is_active": yn_to_bool
    },
    sync_filter="USE_YN = 'Y'"
)


# ==============================================================================
# 매핑 레지스트리
# ==============================================================================

ALL_MAPPINGS = {
    "machines": MACHINE_MAPPING,
    "plc_connections": PLC_MAPPING,
    "tags": TAG_MAPPING,
    "workstages": WORKSTAGE_MAPPING
}


def get_mapping(sqlite_table: str) -> Optional[TableMapping]:
    """SQLite 테이블명으로 매핑 정보 조회"""
    return ALL_MAPPINGS.get(sqlite_table)


def get_all_mappings() -> List[TableMapping]:
    """모든 매핑 정보 조회"""
    return list(ALL_MAPPINGS.values())

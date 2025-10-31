"""
Data models for JSScada SQLite database.
Corresponds to tables: lines, processes, plc_connections, tags, polling_groups
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Line:
    """생산 라인 (lines 테이블)"""
    id: Optional[int] = None
    line_code: str = ""
    line_name: str = ""
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Process:
    """공정 (processes 테이블)

    14자리 설비 코드 예시: KRCWO12ELOA101
    - KR: 국가 코드
    - CWO: 공장 코드
    - 12: 라인 번호
    - ELO: 설비 유형
    - A: 카테고리
    - 101: 순번
    """
    id: Optional[int] = None
    line_id: int = 0
    process_code: str = ""  # 14자리 설비 코드
    process_name: str = ""
    description: Optional[str] = None
    sequence_order: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class PLCConnection:
    """PLC 연결 정보 (plc_connections 테이블)"""
    id: Optional[int] = None
    process_id: int = 0
    plc_code: str = ""
    plc_name: str = ""
    ip_address: str = ""
    port: int = 5010
    protocol: str = "MC_3E_ASCII"
    connection_timeout: int = 5
    is_active: bool = True
    last_connected_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class PollingGroup:
    """폴링 그룹 (polling_groups 테이블)

    polling_mode:
    - FIXED: 고정 주기 폴링
    - HANDSHAKE: 핸드셰이크 모드
    """
    id: Optional[int] = None
    group_name: str = ""
    polling_mode: str = "FIXED"  # FIXED or HANDSHAKE
    polling_interval_ms: int = 1000
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Tag:
    """PLC 태그 (tags 테이블)

    최대 3,491개 태그 지원
    """
    id: Optional[int] = None
    plc_id: int = 0
    polling_group_id: Optional[int] = None
    tag_address: str = ""  # 예: D100, D101
    tag_name: str = ""
    tag_type: str = "INT"  # INT, REAL, STRING, BOOL 등
    unit: Optional[str] = None  # 단위: °C, bar, %, 등
    scale: float = 1.0
    offset: float = 0.0
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    machine_code: Optional[str] = None  # 14자리 설비 코드
    description: Optional[str] = None
    is_active: bool = True
    last_value: Optional[str] = None
    last_updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

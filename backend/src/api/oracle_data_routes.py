"""
Oracle Data Query Routes

Oracle 테이블(XSCADA_OPERATION, XSCADA_DATATAG_LOG)에 저장된 데이터 조회 API
"""

from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/api/oracle-data", tags=["oracle-data"])


# ==============================================================================
# Response Models
# ==============================================================================

class OperationRecord(BaseModel):
    """XSCADA_OPERATION 테이블 레코드"""
    time: str
    name: str
    value: Optional[str] = None


class DatatagLogRecord(BaseModel):
    """XSCADA_DATATAG_LOG 테이블 레코드"""
    id: int
    ctime: str
    otime: Optional[str] = None
    datatag_name: str
    datatag_type: Optional[str] = None
    value_str: Optional[str] = None
    value_num: Optional[float] = None
    value_raw: Optional[str] = None


class OperationResponse(BaseModel):
    """XSCADA_OPERATION 조회 응답"""
    success: bool
    total_count: int
    items: List[OperationRecord]
    message: Optional[str] = None


class DatatagLogResponse(BaseModel):
    """XSCADA_DATATAG_LOG 조회 응답"""
    success: bool
    total_count: int
    items: List[DatatagLogRecord]
    message: Optional[str] = None


class OracleConnectionStatus(BaseModel):
    """Oracle 연결 상태"""
    connected: bool
    host: str
    port: int
    service_name: str
    message: Optional[str] = None


# ==============================================================================
# Helper Functions
# ==============================================================================

def get_oracle_connection():
    """Oracle 연결 획득"""
    try:
        from src.oracle_writer.config import load_config_from_env
        import oracledb

        config = load_config_from_env()
        connection = oracledb.connect(
            user=config.username,
            password=config.password,
            dsn=config.get_dsn()
        )
        return connection, config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Oracle 연결 실패: {str(e)}"
        )


# ==============================================================================
# GET /api/oracle-data/connection-status - Oracle 연결 상태 확인
# ==============================================================================

@router.get("/connection-status", response_model=OracleConnectionStatus)
def check_oracle_connection():
    """
    Oracle 데이터베이스 연결 상태 확인
    """
    try:
        from src.oracle_writer.config import load_config_from_env
        import oracledb

        config = load_config_from_env()

        # 연결 테스트
        connection = oracledb.connect(
            user=config.username,
            password=config.password,
            dsn=config.get_dsn()
        )
        connection.close()

        return OracleConnectionStatus(
            connected=True,
            host=config.host,
            port=config.port,
            service_name=config.service_name,
            message="연결 성공"
        )
    except Exception as e:
        from src.oracle_writer.config import load_config_from_env
        try:
            config = load_config_from_env()
            return OracleConnectionStatus(
                connected=False,
                host=config.host,
                port=config.port,
                service_name=config.service_name,
                message=str(e)
            )
        except:
            return OracleConnectionStatus(
                connected=False,
                host="unknown",
                port=0,
                service_name="unknown",
                message=str(e)
            )


# ==============================================================================
# GET /api/oracle-data/operations - XSCADA_OPERATION 조회
# ==============================================================================

@router.get("/operations", response_model=OperationResponse)
def get_operations(
    limit: int = Query(default=100, ge=1, le=1000, description="조회 개수"),
    name_filter: Optional[str] = Query(default=None, description="NAME 필터 (LIKE 검색)"),
    hours: int = Query(default=24, ge=1, le=168, description="최근 N시간 데이터")
):
    """
    XSCADA_OPERATION 테이블 데이터 조회

    - **limit**: 조회 개수 (기본: 100, 최대: 1000)
    - **name_filter**: NAME 컬럼 필터 (LIKE 검색, 예: 'PLC001%')
    - **hours**: 최근 N시간 데이터 (기본: 24시간, 최대: 168시간/7일)
    """
    try:
        connection, config = get_oracle_connection()
        cursor = connection.cursor()

        # 시간 범위 계산
        time_threshold = datetime.now() - timedelta(hours=hours)

        # SQL 구성
        sql = """
            SELECT TIME, NAME, VALUE
            FROM XSCADA_OPERATION
            WHERE TIME >= :time_threshold
        """
        params = {"time_threshold": time_threshold}

        if name_filter:
            sql += " AND NAME LIKE :name_filter"
            params["name_filter"] = f"%{name_filter}%"

        sql += " ORDER BY TIME DESC FETCH FIRST :limit ROWS ONLY"
        params["limit"] = limit

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        items = []
        for row in rows:
            items.append(OperationRecord(
                time=row[0].isoformat() if row[0] else "",
                name=row[1] or "",
                value=str(row[2]) if row[2] is not None else None
            ))

        cursor.close()
        connection.close()

        return OperationResponse(
            success=True,
            total_count=len(items),
            items=items
        )

    except HTTPException:
        raise
    except Exception as e:
        return OperationResponse(
            success=False,
            total_count=0,
            items=[],
            message=str(e)
        )


# ==============================================================================
# GET /api/oracle-data/datatag-logs - XSCADA_DATATAG_LOG 조회
# ==============================================================================

@router.get("/datatag-logs", response_model=DatatagLogResponse)
def get_datatag_logs(
    limit: int = Query(default=100, ge=1, le=1000, description="조회 개수"),
    datatag_name_filter: Optional[str] = Query(default=None, description="DATATAG_NAME 필터"),
    datatag_type_filter: Optional[str] = Query(default=None, description="DATATAG_TYPE 필터 (STATE, ALARM)"),
    hours: int = Query(default=24, ge=1, le=168, description="최근 N시간 데이터")
):
    """
    XSCADA_DATATAG_LOG 테이블 데이터 조회

    - **limit**: 조회 개수 (기본: 100, 최대: 1000)
    - **datatag_name_filter**: DATATAG_NAME 필터 (LIKE 검색)
    - **datatag_type_filter**: DATATAG_TYPE 필터 (STATE, ALARM 등)
    - **hours**: 최근 N시간 데이터 (기본: 24시간, 최대: 168시간/7일)
    """
    try:
        connection, config = get_oracle_connection()
        cursor = connection.cursor()

        # 시간 범위 계산
        time_threshold = datetime.now() - timedelta(hours=hours)

        # SQL 구성
        sql = """
            SELECT ID, CTIME, OTIME, DATATAG_NAME, DATATAG_TYPE,
                   VALUE_STR, VALUE_NUM, VALUE_RAW
            FROM XSCADA_DATATAG_LOG
            WHERE CTIME >= :time_threshold
        """
        params = {"time_threshold": time_threshold}

        if datatag_name_filter:
            sql += " AND DATATAG_NAME LIKE :datatag_name_filter"
            params["datatag_name_filter"] = f"%{datatag_name_filter}%"

        if datatag_type_filter:
            sql += " AND DATATAG_TYPE = :datatag_type_filter"
            params["datatag_type_filter"] = datatag_type_filter

        sql += " ORDER BY CTIME DESC FETCH FIRST :limit ROWS ONLY"
        params["limit"] = limit

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        items = []
        for row in rows:
            items.append(DatatagLogRecord(
                id=row[0],
                ctime=row[1].isoformat() if row[1] else "",
                otime=row[2].isoformat() if row[2] else None,
                datatag_name=row[3] or "",
                datatag_type=row[4],
                value_str=row[5],
                value_num=float(row[6]) if row[6] is not None else None,
                value_raw=row[7]
            ))

        cursor.close()
        connection.close()

        return DatatagLogResponse(
            success=True,
            total_count=len(items),
            items=items
        )

    except HTTPException:
        raise
    except Exception as e:
        return DatatagLogResponse(
            success=False,
            total_count=0,
            items=[],
            message=str(e)
        )


# ==============================================================================
# GET /api/oracle-data/summary - 데이터 요약 통계
# ==============================================================================

@router.get("/summary")
def get_data_summary(
    hours: int = Query(default=24, ge=1, le=168, description="최근 N시간 데이터")
):
    """
    Oracle 데이터 요약 통계

    - XSCADA_OPERATION 레코드 수
    - XSCADA_DATATAG_LOG 레코드 수 (타입별)
    """
    try:
        connection, config = get_oracle_connection()
        cursor = connection.cursor()

        time_threshold = datetime.now() - timedelta(hours=hours)

        # XSCADA_OPERATION 카운트
        cursor.execute(
            "SELECT COUNT(*) FROM XSCADA_OPERATION WHERE TIME >= :t",
            {"t": time_threshold}
        )
        operation_count = cursor.fetchone()[0]

        # XSCADA_DATATAG_LOG 전체 카운트
        cursor.execute(
            "SELECT COUNT(*) FROM XSCADA_DATATAG_LOG WHERE CTIME >= :t",
            {"t": time_threshold}
        )
        datatag_total_count = cursor.fetchone()[0]

        # XSCADA_DATATAG_LOG 타입별 카운트
        cursor.execute("""
            SELECT DATATAG_TYPE, COUNT(*)
            FROM XSCADA_DATATAG_LOG
            WHERE CTIME >= :t
            GROUP BY DATATAG_TYPE
        """, {"t": time_threshold})
        type_counts = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.close()
        connection.close()

        return {
            "success": True,
            "hours": hours,
            "time_range": {
                "from": time_threshold.isoformat(),
                "to": datetime.now().isoformat()
            },
            "xscada_operation": {
                "count": operation_count
            },
            "xscada_datatag_log": {
                "total_count": datatag_total_count,
                "by_type": type_counts
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

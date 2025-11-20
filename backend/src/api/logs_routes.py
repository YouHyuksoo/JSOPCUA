"""
Log Query Routes

REST API endpoints for querying log files:
- GET /api/logs/{log_type} - Query logs with filters
- GET /api/logs/{log_type}/download - Download logs as file
- DELETE /api/logs/{log_type} - Delete all logs for a specific log type
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
from typing import List, Optional, Literal
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel
import re

router = APIRouter(prefix="/api/logs")


class LogEntry(BaseModel):
    """로그 엔트리"""
    timestamp: str
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    message: str
    stack_trace: Optional[str] = None


class LogQueryResponse(BaseModel):
    """로그 조회 응답"""
    logs: List[LogEntry]
    total: int
    page: int
    page_size: int
    total_pages: int
    log_type: str


LogType = Literal["scada", "error", "communication", "performance", "plc", "polling", "oracle_writer"]


def get_log_file_path(log_type: str) -> Path:
    """
    로그 타입에 따른 파일 경로 반환

    Args:
        log_type: 로그 타입 (scada, error, communication, performance)

    Returns:
        Path: 로그 파일 경로
    """
    # Get backend directory
    current_file = Path(__file__).resolve()
    backend_dir = current_file.parent.parent.parent

    log_dir = backend_dir / "logs"

    log_files = {
        "scada": log_dir / "scada.log",
        "error": log_dir / "error.log",
        "communication": log_dir / "communication.log",
        "performance": log_dir / "performance.log",
        "plc": log_dir / "plc.log",
        "polling": log_dir / "polling.log",
        "oracle_writer": log_dir / "oracle_writer.log"
    }

    return log_files.get(log_type)


def parse_log_line(line: str, log_type: str) -> Optional[LogEntry]:
    """
    로그 라인을 파싱하여 LogEntry 객체로 변환

    Args:
        line: 로그 라인
        log_type: 로그 타입

    Returns:
        LogEntry or None
    """
    line = line.strip()
    if not line:
        return None

    try:
        # Standard format: 2025-01-15 10:30:45 | INFO     | module.name | message
        # Performance format: 2025-01-15 10:30:45 | message

        if log_type == "performance":
            # Performance log has simpler format
            match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*\|\s*(.+)$', line)
            if match:
                timestamp, message = match.groups()
                return LogEntry(
                    timestamp=timestamp,
                    level="INFO",
                    message=message.strip()
                )
        else:
            # Standard log format
            match = re.match(
                r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*\|\s*(\w+)\s*\|.*?\|\s*(.+)$',
                line
            )
            if match:
                timestamp, level, message = match.groups()
                return LogEntry(
                    timestamp=timestamp,
                    level=level.strip(),
                    message=message.strip()
                )

        # If parsing fails, treat entire line as message
        return LogEntry(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            level="INFO",
            message=line
        )

    except Exception as e:
        # Fallback for unparseable lines
        return LogEntry(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            level="INFO",
            message=line
        )


@router.get("/{log_type}", response_model=LogQueryResponse)
async def get_logs(
    log_type: LogType,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    start_time: Optional[str] = Query(None, description="Start time (YYYY-MM-DD HH:MM:SS)"),
    end_time: Optional[str] = Query(None, description="End time (YYYY-MM-DD HH:MM:SS)"),
    levels: Optional[str] = Query(None, description="Comma-separated log levels (e.g., ERROR,WARNING)"),
    search: Optional[str] = Query(None, description="Search keyword in message")
):
    """
    로그 조회 API (페이지네이션)

    Args:
        log_type: 로그 타입 (scada, error, communication, performance, plc, polling, oracle_writer)
        page: 페이지 번호 (1부터 시작)
        page_size: 페이지 크기 (기본값: 50)
        start_time: 시작 시간 필터
        end_time: 종료 시간 필터
        levels: 로그 레벨 필터 (쉼표로 구분)
        search: 메시지 검색 키워드

    Returns:
        LogQueryResponse: 로그 목록 및 페이지네이션 메타데이터
    """
    log_file = get_log_file_path(log_type)

    if not log_file or not log_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Log file not found: {log_type}.log"
        )

    # Parse filter levels
    level_filter = None
    if levels:
        level_filter = set(level.strip().upper() for level in levels.split(","))

    # Parse time filters
    start_dt = None
    end_dt = None
    if start_time:
        try:
            start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_time format")

    if end_time:
        try:
            end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_time format")

    # Read and parse log file with filters
    all_logs: List[LogEntry] = []

    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Reverse to get newest first
            lines.reverse()

            for line in lines:
                entry = parse_log_line(line, log_type)
                if not entry:
                    continue

                # Apply filters
                if level_filter and entry.level not in level_filter:
                    continue

                if search and search.lower() not in entry.message.lower():
                    continue

                # Time filter
                if start_dt or end_dt:
                    try:
                        entry_dt = datetime.strptime(entry.timestamp, "%Y-%m-%d %H:%M:%S")
                        if start_dt and entry_dt < start_dt:
                            continue
                        if end_dt and entry_dt > end_dt:
                            continue
                    except ValueError:
                        pass

                all_logs.append(entry)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read log file: {str(e)}"
        )

    # Calculate pagination
    total = len(all_logs)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    # Get page slice
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_logs = all_logs[start_idx:end_idx]

    return LogQueryResponse(
        logs=paginated_logs,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        log_type=log_type
    )


@router.get("/{log_type}/download")
async def download_logs(
    log_type: LogType,
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    levels: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """
    로그 파일 다운로드 API

    Args:
        log_type: 로그 타입
        start_time: 시작 시간 필터
        end_time: 종료 시간 필터
        levels: 로그 레벨 필터
        search: 검색 키워드

    Returns:
        FileResponse: 로그 파일
    """
    log_file = get_log_file_path(log_type)

    if not log_file or not log_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Log file not found: {log_type}.log"
        )

    # If no filters, return entire file
    if not any([start_time, end_time, levels, search]):
        return FileResponse(
            path=log_file,
            filename=f"{log_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            media_type="text/plain"
        )

    # Apply filters and create temporary file
    # For simplicity, we'll use the get_logs endpoint logic
    result = await get_logs(
        log_type=log_type,
        limit=100000,  # Large limit for download
        start_time=start_time,
        end_time=end_time,
        levels=levels,
        search=search
    )

    # Create temporary filtered log file
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log', encoding='utf-8')

    for entry in result.logs:
        temp_file.write(f"{entry.timestamp} | {entry.level:8s} | {entry.message}\n")

    temp_file.close()

    return FileResponse(
        path=temp_file.name,
        filename=f"{log_type}_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
        media_type="text/plain"
    )


@router.delete("/{log_type}")
async def delete_logs(log_type: LogType):
    """
    로그 파일 삭제 API

    Args:
        log_type: 로그 타입 (scada, error, communication, performance, plc, polling, oracle_writer)

    Returns:
        dict: 삭제 성공 메시지
    """
    log_file = get_log_file_path(log_type)

    if not log_file:
        raise HTTPException(
            status_code=404,
            detail=f"Log type not found: {log_type}"
        )

    try:
        # 파일이 존재하면 내용을 지우고, 존재하지 않으면 새로 생성
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write('')  # 빈 파일로 만들기

        return {
            "success": True,
            "message": f"{log_type}.log 파일이 성공적으로 삭제되었습니다.",
            "log_type": log_type
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete log file: {str(e)}"
        )

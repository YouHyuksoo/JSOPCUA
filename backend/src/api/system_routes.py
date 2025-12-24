"""
System Control API Routes

Provides endpoints to start/stop the SCADA system and check its status.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
import os
from pathlib import Path
import logging

router = APIRouter(prefix="/api/system", tags=["system"])
logger = logging.getLogger(__name__)

# Global engine instance (will be set by main app)
_polling_engine = None
_system_started_at: Optional[datetime] = None


def set_system_engine(engine):
    """Set the global polling engine instance"""
    global _polling_engine
    _polling_engine = engine


class SystemStatusResponse(BaseModel):
    status: str  # "stopped", "starting", "running", "stopping"
    started_at: Optional[str] = None
    uptime_seconds: Optional[int] = None
    polling_groups_loaded: int = 0
    polling_groups_running: int = 0


@router.post("/start")
async def start_system():
    """
    Start the SCADA system (initialize polling engine and start all groups)

    This must be called before the system can collect data from PLCs.
    """
    global _system_started_at

    if not _polling_engine:
        raise HTTPException(
            status_code=503,
            detail="Polling engine not available"
        )

    # Check if already initialized
    if hasattr(_polling_engine, '_initialized') and _polling_engine._initialized:
        return {
            "success": False,
            "message": "System is already running",
            "status": "running"
        }

    try:
        # Initialize polling engine (loads polling groups from database)
        _polling_engine.initialize()
        _system_started_at = datetime.now()

        # Optionally auto-start all polling groups
        # Uncomment if you want auto-start behavior:
        # _polling_engine.start_all()

        return {
            "success": True,
            "message": "System started successfully. Polling groups are loaded but not running. Use /api/polling/start-all to start polling.",
            "status": "running",
            "started_at": _system_started_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start system: {str(e)}"
        )


@router.post("/stop")
async def stop_system():
    """
    Stop the SCADA system (stop all polling groups and shutdown engine)

    This will gracefully stop all data collection.
    """
    global _system_started_at

    if not _polling_engine:
        raise HTTPException(
            status_code=503,
            detail="Polling engine not available"
        )

    if not hasattr(_polling_engine, '_initialized') or not _polling_engine._initialized:
        return {
            "success": False,
            "message": "System is already stopped",
            "status": "stopped"
        }

    try:
        # Stop all polling groups first
        _polling_engine.stop_all(timeout=5.0)

        # Shutdown engine
        _polling_engine.shutdown()
        _system_started_at = None

        return {
            "success": True,
            "message": "System stopped successfully",
            "status": "stopped"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop system: {str(e)}"
        )


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status():
    """
    Get current system status

    Returns whether the system is running, uptime, and polling group statistics.
    """
    if not _polling_engine:
        return SystemStatusResponse(
            status="unavailable",
            polling_groups_loaded=0,
            polling_groups_running=0
        )

    is_initialized = hasattr(_polling_engine, '_initialized') and _polling_engine._initialized

    if not is_initialized:
        return SystemStatusResponse(
            status="stopped",
            polling_groups_loaded=0,
            polling_groups_running=0
        )

    # Get polling groups status
    try:
        groups_status = _polling_engine.get_status_all()
        running_count = sum(1 for g in groups_status if g.get('state') == 'running')

        uptime_seconds = None
        if _system_started_at:
            uptime_seconds = int((datetime.now() - _system_started_at).total_seconds())

        return SystemStatusResponse(
            status="running",
            started_at=_system_started_at.isoformat() if _system_started_at else None,
            uptime_seconds=uptime_seconds,
            polling_groups_loaded=len(groups_status),
            polling_groups_running=running_count
        )
    except Exception as e:
        return SystemStatusResponse(
            status="error",
            polling_groups_loaded=0,
            polling_groups_running=0
        )


@router.post("/restart")
async def restart_system():
    """
    Restart the SCADA system (stop then start)

    Useful for reloading configuration changes.
    """
    # Stop system
    stop_result = await stop_system()
    if not stop_result.get("success", False) and stop_result.get("status") != "stopped":
        raise HTTPException(
            status_code=500,
            detail="Failed to stop system during restart"
        )

    # Start system
    start_result = await start_system()
    if not start_result.get("success", False):
        raise HTTPException(
            status_code=500,
            detail="Failed to start system during restart"
        )

    return {
        "success": True,
        "message": "System restarted successfully",
        "status": "running"
    }


class PLCStatusItem(BaseModel):
    plc_id: int
    plc_name: str
    is_online: bool
    last_seen: Optional[str] = None


class SystemInfo(BaseModel):
    cpu_percent: float
    memory_used_gb: float
    memory_total_gb: float
    memory_percent: float
    disk_used_gb: float
    disk_total_gb: float
    disk_percent: float
    timestamp: str


class BufferInfo(BaseModel):
    current_size: int
    max_size: int
    utilization_percent: float
    overflow_count: int = 0
    last_overflow_time: Optional[str] = None


class OracleWriterInfo(BaseModel):
    success_count: int = 0
    fail_count: int = 0
    success_rate_percent: float = 0.0
    backup_file_count: int = 0


class DashboardDataResponse(BaseModel):
    system: SystemInfo
    plc_status: List[PLCStatusItem] = []
    active_polling_groups: int = 0
    total_polling_groups: int = 0
    buffer: BufferInfo
    oracle_writer: OracleWriterInfo


@router.get("/dashboard", response_model=DashboardDataResponse)
async def get_dashboard_data():
    """
    Get comprehensive dashboard data including system resources and SCADA status

    Returns CPU, memory, disk usage, PLC connections, polling groups, and buffer status.
    """
    import psutil
    from src.api.dependencies import DB_PATH
    from src.database.sqlite_manager import SQLiteManager

    # Get system resource usage
    cpu_usage = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    # Initialize default values
    plc_status_list: List[PLCStatusItem] = []
    groups_running = 0
    groups_total = 0
    buffer_size = 0
    buffer_max = 10000
    buffer_util = 0.0
    overflow_count = 0

    # Get PLC list from database
    db = SQLiteManager(DB_PATH)
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, plc_name, last_connected_at
            FROM plc_connections
            WHERE is_active = 1
        """)
        plc_rows = cursor.fetchall()

        for plc_row in plc_rows:
            plc_id, plc_name, last_connected = plc_row
            # Check if PLC is online (connected in last 5 minutes)
            is_online = False
            last_seen = None

            if last_connected:
                last_seen = last_connected
                # Simple check: if engine is running and has this PLC pool
                if _polling_engine and hasattr(_polling_engine, 'pool_manager'):
                    is_online = plc_id in _polling_engine.pool_manager._pools

            plc_status_list.append(PLCStatusItem(
                plc_id=plc_id,
                plc_name=plc_name,
                is_online=is_online,
                last_seen=last_seen
            ))

        cursor.close()

    # Get SCADA-specific data if engine is available
    if _polling_engine and hasattr(_polling_engine, '_initialized') and _polling_engine._initialized:
        try:
            # Get polling groups status
            groups_status = _polling_engine.get_status_all()
            groups_total = len(groups_status)
            groups_running = sum(1 for g in groups_status if g.get('state') == 'running')

            # Get buffer status
            if hasattr(_polling_engine, 'data_buffer'):
                buffer = _polling_engine.data_buffer
                buffer_size = buffer.size() if hasattr(buffer, 'size') else 0
                buffer_max = buffer._queue.maxsize if hasattr(buffer, '_queue') else 10000
                buffer_util = (buffer_size / buffer_max * 100) if buffer_max > 0 else 0.0
        except Exception as e:
            # Log error but continue with default values
            logger.error(f"Error getting SCADA data: {e}")

    return DashboardDataResponse(
        system=SystemInfo(
            cpu_percent=cpu_usage,
            memory_used_gb=round(memory.used / (1024**3), 2),
            memory_total_gb=round(memory.total / (1024**3), 2),
            memory_percent=memory.percent,
            disk_used_gb=round(disk.used / (1024**3), 2),
            disk_total_gb=round(disk.total / (1024**3), 2),
            disk_percent=disk.percent,
            timestamp=datetime.now().isoformat()
        ),
        plc_status=plc_status_list,
        active_polling_groups=groups_running,
        total_polling_groups=groups_total,
        buffer=BufferInfo(
            current_size=buffer_size,
            max_size=buffer_max,
            utilization_percent=round(buffer_util, 2),
            overflow_count=overflow_count
        ),
        oracle_writer=OracleWriterInfo()
    )


# ==============================================================================
# Environment Configuration Management
# ==============================================================================

class EnvConfigUpdate(BaseModel):
    """Request model for updating environment configuration"""
    # Database
    DATABASE_PATH: Optional[str] = None

    # API Server
    API_HOST: Optional[str] = None
    API_PORT: Optional[int] = None
    API_RELOAD: Optional[bool] = None

    # CORS
    CORS_ORIGINS: Optional[str] = None

    # Logging
    LOG_LEVEL: Optional[str] = None
    LOG_DIR: Optional[str] = None

    # Polling Engine
    MAX_POLLING_GROUPS: Optional[int] = None
    DATA_QUEUE_SIZE: Optional[int] = None

    # PLC Connection Pool
    POOL_SIZE_PER_PLC: Optional[int] = None
    CONNECTION_TIMEOUT: Optional[int] = None
    READ_TIMEOUT: Optional[int] = None

    # Oracle Database
    ORACLE_HOST: Optional[str] = None
    ORACLE_PORT: Optional[int] = None
    ORACLE_SERVICE_NAME: Optional[str] = None
    ORACLE_USERNAME: Optional[str] = None
    ORACLE_PASSWORD: Optional[str] = None
    ORACLE_POOL_MIN: Optional[int] = None
    ORACLE_POOL_MAX: Optional[int] = None

    # Buffer Configuration
    BUFFER_MAX_SIZE: Optional[int] = None
    BUFFER_BATCH_SIZE: Optional[int] = None
    BUFFER_WRITE_INTERVAL: Optional[float] = None


def get_env_file_path() -> Path:
    """Get the path to the .env file"""
    # Assuming the backend directory structure
    backend_dir = Path(__file__).parent.parent.parent  # Go up to backend/
    env_path = backend_dir / '.env'
    return env_path


def parse_env_file(env_path: Path) -> Dict[str, str]:
    """Parse .env file and return key-value pairs"""
    env_vars = {}

    if not env_path.exists():
        return env_vars

    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()

    return env_vars


def write_env_file(env_path: Path, env_vars: Dict[str, str]):
    """Write environment variables to .env file"""
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write("# JSScada Backend Environment Configuration\n")
        f.write("# Auto-generated by System Settings\n\n")

        # Group configurations
        groups = {
            "Database": ["DATABASE_PATH"],
            "API Server": ["API_HOST", "API_PORT", "API_RELOAD"],
            "CORS Origins": ["CORS_ORIGINS"],
            "Logging": ["LOG_LEVEL", "LOG_DIR", "LOG_COLORS", "LOG_MAX_BYTES", "LOG_BACKUP_COUNT"],
            "Polling Engine": ["MAX_POLLING_GROUPS", "DATA_QUEUE_SIZE", "WEBSOCKET_BROADCAST_INTERVAL"],
            "PLC Connection Pool": ["POOL_SIZE_PER_PLC", "CONNECTION_TIMEOUT", "READ_TIMEOUT", "IDLE_TIMEOUT"],
            "Oracle Database": ["ORACLE_HOST", "ORACLE_PORT", "ORACLE_SERVICE_NAME", "ORACLE_USERNAME", "ORACLE_PASSWORD", "ORACLE_POOL_MIN", "ORACLE_POOL_MAX"],
            "Buffer Configuration": ["BUFFER_MAX_SIZE", "BUFFER_BATCH_SIZE", "BUFFER_BATCH_SIZE_MAX", "BUFFER_WRITE_INTERVAL", "BUFFER_RETRY_COUNT", "BACKUP_FILE_PATH"],
        }

        for group_name, keys in groups.items():
            f.write(f"# {group_name}\n")
            for key in keys:
                if key in env_vars:
                    f.write(f"{key}={env_vars[key]}\n")
            f.write("\n")


@router.get("/env-config")
async def get_env_config() -> Dict[str, str]:
    """
    Get current environment configuration from .env file

    Returns all environment variables (passwords are masked)
    """
    try:
        env_path = get_env_file_path()
        env_vars = parse_env_file(env_path)

        # Mask sensitive information
        if 'ORACLE_PASSWORD' in env_vars:
            env_vars['ORACLE_PASSWORD'] = '***'

        return env_vars

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read environment configuration: {str(e)}"
        )


class EnvConfigUpdateResponse(BaseModel):
    """Response model for environment configuration update"""
    success: bool
    message: str
    config: Dict[str, str]


@router.put("/env-config")
async def update_env_config(config: EnvConfigUpdate) -> EnvConfigUpdateResponse:
    """
    Update environment configuration and save to .env file

    Only updates fields that are provided (non-null values)
    Returns the updated configuration
    """
    try:
        env_path = get_env_file_path()

        # Read current configuration
        env_vars = parse_env_file(env_path)

        # Update with new values (only non-null fields)
        update_data = config.dict(exclude_none=True)
        for key, value in update_data.items():
            # Convert boolean to string
            if isinstance(value, bool):
                value = 'true' if value else 'false'
            # Convert to string
            env_vars[key] = str(value)

        # Write back to file
        write_env_file(env_path, env_vars)

        # Mask sensitive information in response
        if 'ORACLE_PASSWORD' in env_vars:
            env_vars['ORACLE_PASSWORD'] = '***'

        return EnvConfigUpdateResponse(
            success=True,
            message="Environment configuration updated successfully. Restart required for changes to take effect.",
            config=env_vars
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update environment configuration: {str(e)}"
        )


class OracleConnectionTestResponse(BaseModel):
    """Response model for Oracle connection test"""
    success: bool
    message: str
    connection_info: Optional[Dict[str, str]] = None
    error_details: Optional[str] = None


@router.post("/test-oracle-connection")
async def test_oracle_connection() -> OracleConnectionTestResponse:
    """
    Test Oracle database connection with current configuration

    Returns connection status and details
    """
    try:
        from src.oracle_writer.config import load_config_from_env
        from src.oracle_writer.oracle_helper import OracleHelper

        # Load Oracle configuration
        config = load_config_from_env()

        # Attempt to connect
        with OracleHelper() as oracle:
            # Simple test query
            cursor = oracle.connection.cursor()
            cursor.execute("SELECT 1 FROM DUAL")
            result = cursor.fetchone()
            cursor.close()

            if result:
                return OracleConnectionTestResponse(
                    success=True,
                    message="Oracle 데이터베이스 연결 성공",
                    connection_info={
                        "host": config.host,
                        "port": str(config.port),
                        "service_name": config.service_name,
                        "username": config.username,
                        "dsn": config.get_dsn()
                    }
                )
            else:
                return OracleConnectionTestResponse(
                    success=False,
                    message="Oracle 연결 테스트 쿼리 실패",
                    error_details="SELECT 1 FROM DUAL returned no result"
                )

    except Exception as e:
        error_message = str(e)
        return OracleConnectionTestResponse(
            success=False,
            message="Oracle 데이터베이스 연결 실패",
            error_details=error_message
        )

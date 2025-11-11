"""
System Control API Routes

Provides endpoints to start/stop the SCADA system and check its status.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/system", tags=["system"])

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


class DashboardDataResponse(BaseModel):
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    plc_status: dict = {"connected": 0, "total": 0}
    polling_groups: dict = {"running": 0, "total": 0}
    buffer_status: dict = {"current_size": 0, "max_size": 0, "utilization_percent": 0.0}


@router.get("/dashboard", response_model=DashboardDataResponse)
async def get_dashboard_data():
    """
    Get comprehensive dashboard data including system resources and SCADA status

    Returns CPU, memory, disk usage, PLC connections, polling groups, and buffer status.
    """
    import psutil

    # Get system resource usage
    cpu_usage = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    # Initialize default values
    plc_connected = 0
    plc_total = 0
    groups_running = 0
    groups_total = 0
    buffer_size = 0
    buffer_max = 10000
    buffer_util = 0.0

    # Get SCADA-specific data if engine is available
    if _polling_engine and hasattr(_polling_engine, '_initialized') and _polling_engine._initialized:
        try:
            # Get polling groups status
            groups_status = _polling_engine.get_status_all()
            groups_total = len(groups_status)
            groups_running = sum(1 for g in groups_status if g.get('state') == 'running')

            # Get PLC connection status
            if hasattr(_polling_engine, 'pool_manager'):
                # Count active PLC pools
                plc_total = len(_polling_engine.pool_manager._pools)
                plc_connected = plc_total  # Assume all are connected if pools exist

            # Get buffer status
            if hasattr(_polling_engine, 'data_buffer'):
                buffer = _polling_engine.data_buffer
                buffer_size = buffer.size() if hasattr(buffer, 'size') else 0
                buffer_max = buffer._queue.maxsize if hasattr(buffer, '_queue') else 10000
                buffer_util = (buffer_size / buffer_max * 100) if buffer_max > 0 else 0.0
        except Exception as e:
            # Log error but continue with default values
            print(f"Error getting SCADA data: {e}")

    return DashboardDataResponse(
        cpu_usage=cpu_usage,
        memory_usage=memory.percent,
        disk_usage=disk.percent,
        plc_status={"connected": plc_connected, "total": plc_total},
        polling_groups={"running": groups_running, "total": groups_total},
        buffer_status={
            "current_size": buffer_size,
            "max_size": buffer_max,
            "utilization_percent": buffer_util
        }
    )

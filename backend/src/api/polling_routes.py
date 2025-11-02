"""
Polling API Routes

REST API endpoints for polling engine control and monitoring.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

from polling.polling_engine import PollingEngine
from polling.exceptions import (
    PollingGroupNotFoundError,
    PollingGroupAlreadyRunningError,
    PollingGroupNotRunningError,
    MaxPollingGroupsReachedError
)

router = APIRouter(prefix="/api/polling", tags=["polling"])

# Global engine instance (will be initialized by main app)
engine: Optional[PollingEngine] = None


def set_polling_engine(polling_engine: PollingEngine):
    """Set the global polling engine instance"""
    global engine
    engine = polling_engine


# Request/Response Models
class TriggerResponse(BaseModel):
    success: bool
    group_name: str
    mode: str
    message: str
    tag_count: Optional[int] = None


class GroupStatusResponse(BaseModel):
    group_id: int
    group_name: str
    mode: str
    state: str
    last_poll_time: Optional[str]
    total_polls: int
    success_count: int
    error_count: int
    avg_poll_time_ms: float


class QueueStatusResponse(BaseModel):
    queue_size: int
    queue_maxsize: int
    queue_is_full: bool


class EngineStatusResponse(BaseModel):
    groups: List[GroupStatusResponse]
    queue: QueueStatusResponse
    timestamp: str


# API Endpoints

@router.get("/status", response_model=EngineStatusResponse)
async def get_engine_status():
    """
    Get complete polling engine status

    Returns status of all polling groups and queue information.
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Polling engine not initialized")

    groups_status = engine.get_status_all()
    queue_size = engine.get_queue_size()

    return EngineStatusResponse(
        groups=[GroupStatusResponse(**s) for s in groups_status],
        queue=QueueStatusResponse(
            queue_size=queue_size,
            queue_maxsize=engine.data_queue.maxsize,
            queue_is_full=engine.data_queue.is_full()
        ),
        timestamp=datetime.now().isoformat()
    )


@router.post("/groups/{group_name}/start")
async def start_polling_group(group_name: str):
    """
    Start a specific polling group

    Args:
        group_name: Name of the polling group to start

    Returns:
        Success message with group information
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Polling engine not initialized")

    try:
        engine.start_group(group_name)
        return {
            "success": True,
            "message": f"Polling group '{group_name}' started successfully",
            "group_name": group_name
        }
    except PollingGroupNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PollingGroupAlreadyRunningError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except MaxPollingGroupsReachedError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start group: {str(e)}")


@router.post("/groups/{group_name}/stop")
async def stop_polling_group(group_name: str, timeout: float = 5.0):
    """
    Stop a specific polling group

    Args:
        group_name: Name of the polling group to stop
        timeout: Maximum time to wait for graceful shutdown (seconds)

    Returns:
        Success message with group information
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Polling engine not initialized")

    try:
        engine.stop_group(group_name, timeout=timeout)
        return {
            "success": True,
            "message": f"Polling group '{group_name}' stopped successfully",
            "group_name": group_name
        }
    except PollingGroupNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PollingGroupNotRunningError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop group: {str(e)}")


@router.post("/groups/{group_name}/trigger", response_model=TriggerResponse)
async def trigger_handshake_poll(group_name: str):
    """
    Manually trigger a HANDSHAKE mode polling group

    Args:
        group_name: Name of the HANDSHAKE polling group

    Returns:
        Trigger execution result
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Polling engine not initialized")

    try:
        result = engine.trigger_handshake(group_name)
        return TriggerResponse(**result)
    except PollingGroupNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger poll: {str(e)}")


@router.post("/start-all")
async def start_all_groups():
    """
    Start all polling groups

    Returns:
        Summary of started groups
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Polling engine not initialized")

    try:
        before_status = engine.get_status_all()
        stopped_groups = [s for s in before_status if s['state'] == 'stopped']

        engine.start_all()

        after_status = engine.get_status_all()
        running_groups = [s for s in after_status if s['state'] == 'running']

        return {
            "success": True,
            "message": "All polling groups started",
            "total_groups": len(before_status),
            "running_count": len(running_groups)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start all groups: {str(e)}")


@router.post("/stop-all")
async def stop_all_groups(timeout: float = 5.0):
    """
    Stop all polling groups

    Args:
        timeout: Maximum time to wait for graceful shutdown per group (seconds)

    Returns:
        Summary of stopped groups
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Polling engine not initialized")

    try:
        before_status = engine.get_status_all()
        running_groups = [s for s in before_status if s['state'] == 'running']

        engine.stop_all(timeout=timeout)

        after_status = engine.get_status_all()
        stopped_groups = [s for s in after_status if s['state'] == 'stopped']

        return {
            "success": True,
            "message": "All polling groups stopped",
            "total_groups": len(before_status),
            "stopped_count": len(stopped_groups)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop all groups: {str(e)}")


@router.get("/groups/{group_name}/status", response_model=GroupStatusResponse)
async def get_group_status(group_name: str):
    """
    Get status of a specific polling group

    Args:
        group_name: Name of the polling group

    Returns:
        Group status information
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Polling engine not initialized")

    all_status = engine.get_status_all()
    group_status = next((s for s in all_status if s['group_name'] == group_name), None)

    if not group_status:
        raise HTTPException(status_code=404, detail=f"Polling group not found: {group_name}")

    return GroupStatusResponse(**group_status)


@router.get("/queue/status", response_model=QueueStatusResponse)
async def get_queue_status():
    """
    Get data queue status

    Returns:
        Queue size and capacity information
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Polling engine not initialized")

    return QueueStatusResponse(
        queue_size=engine.get_queue_size(),
        queue_maxsize=engine.data_queue.maxsize,
        queue_is_full=engine.data_queue.is_full()
    )

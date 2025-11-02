"""
Buffer and Oracle Writer Monitoring API

REST endpoints for monitoring buffer status and Oracle writer metrics.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/buffer", tags=["Buffer Monitoring"])

# Global references to buffer and writer (set by main.py)
_circular_buffer = None
_oracle_writer = None
_csv_backup = None


def set_buffer_components(circular_buffer, oracle_writer, csv_backup):
    """Set global references to buffer components"""
    global _circular_buffer, _oracle_writer, _csv_backup
    _circular_buffer = circular_buffer
    _oracle_writer = oracle_writer
    _csv_backup = csv_backup
    logger.info("Buffer components registered with monitoring API")


@router.get("/status")
async def get_buffer_status():
    """Get current buffer status"""
    if _circular_buffer is None:
        raise HTTPException(status_code=503, detail="Buffer not initialized")
    
    try:
        stats = _circular_buffer.stats()
        return {
            "current_size": stats["current_size"],
            "max_size": stats["max_size"],
            "utilization_pct": stats["utilization_pct"],
            "total_inserted": stats["total_added"],
            "total_removed": stats["total_added"] - stats["current_size"],
            "overflow_count": stats["overflow_count"],
            "overflow_rate_pct": stats["overflow_rate_pct"]
        }
    except Exception as e:
        logger.error(f"Error getting buffer status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get buffer status: {str(e)}")


@router.get("/writer/metrics")
async def get_writer_metrics():
    """Get Oracle writer performance metrics"""
    if _oracle_writer is None:
        raise HTTPException(status_code=503, detail="Oracle writer not initialized")
    
    try:
        writer_stats = _oracle_writer.get_stats()
        metrics = writer_stats["metrics"]
        return {
            "successful_writes": metrics["total_successful_writes"],
            "failed_writes": metrics["total_failed_writes"],
            "success_rate_pct": metrics["success_rate_pct"],
            "avg_batch_size": metrics["avg_batch_size"],
            "avg_write_latency_ms": metrics["avg_write_latency_ms"],
            "throughput_items_per_sec": metrics["throughput_items_per_sec"],
            "last_write_timestamp": metrics["last_write_time"]
        }
    except Exception as e:
        logger.error(f"Error getting writer metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get writer metrics: {str(e)}")


@router.get("/health")
async def get_buffer_health():
    """Get overall buffer and writer health status"""
    if _circular_buffer is None or _oracle_writer is None:
        raise HTTPException(status_code=503, detail="Buffer components not initialized")
    
    try:
        buffer_stats = _circular_buffer.stats()
        buffer_ok = buffer_stats["utilization_pct"] < 80.0
        
        writer_stats = _oracle_writer.get_stats()
        writer_ok = writer_stats["is_running"]
        
        metrics = writer_stats["metrics"]
        oracle_ok = metrics["success_rate_pct"] > 99.0 or metrics["total_successful_writes"] == 0
        
        backup_count = 0
        if _csv_backup is not None:
            try:
                backup_count = _csv_backup.get_backup_file_count()
            except Exception:
                pass
        
        if buffer_ok and writer_ok and oracle_ok:
            status = "healthy"
            status_code = 200
        elif buffer_ok and writer_ok:
            status = "degraded"
            status_code = 200
        else:
            status = "unhealthy"
            status_code = 503
        
        response = {
            "status": status,
            "buffer_ok": buffer_ok,
            "writer_ok": writer_ok,
            "oracle_connection_ok": oracle_ok,
            "details": {
                "buffer_utilization_pct": buffer_stats["utilization_pct"],
                "recent_write_success": oracle_ok,
                "last_write_age_seconds": None,
                "backup_file_count": backup_count
            }
        }
        
        if status_code == 503:
            raise HTTPException(status_code=503, detail=response)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting health status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get health status: {str(e)}")


@router.get("/metrics")
async def get_all_metrics():
    """Get comprehensive buffer and writer metrics"""
    if _circular_buffer is None or _oracle_writer is None:
        raise HTTPException(status_code=503, detail="Buffer components not initialized")
    
    try:
        buffer_stats = _circular_buffer.stats()
        writer_stats = _oracle_writer.get_stats()
        metrics = writer_stats["metrics"]
        
        backup_count = 0
        if _csv_backup is not None:
            try:
                backup_count = _csv_backup.get_backup_file_count()
            except Exception:
                pass
        
        return {
            "buffer": {
                "current_size": buffer_stats["current_size"],
                "max_size": buffer_stats["max_size"],
                "utilization_pct": buffer_stats["utilization_pct"],
                "overflow_count": buffer_stats["overflow_count"],
                "overflow_rate_pct": buffer_stats["overflow_rate_pct"]
            },
            "writer": {
                "is_running": writer_stats["is_running"],
                "batch_size": writer_stats["batch_size"],
                "write_interval": writer_stats["write_interval"],
                "total_writes": metrics["total_successful_writes"],
                "successful_writes": metrics["total_successful_writes"],
                "failed_writes": metrics["total_failed_writes"],
                "success_rate_pct": metrics["success_rate_pct"],
                "avg_batch_size": metrics["avg_batch_size"],
                "avg_write_latency_ms": metrics["avg_write_latency_ms"],
                "throughput_items_per_sec": metrics["throughput_items_per_sec"],
                "last_write_time": metrics["last_write_time"]
            },
            "backup": {
                "file_count": backup_count
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting all metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

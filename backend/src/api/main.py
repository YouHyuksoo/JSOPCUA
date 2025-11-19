"""
FastAPI Application

Main FastAPI application for polling engine REST API.
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.polling.polling_engine import PollingEngine
from src.plc.pool_manager import PoolManager
from src.config.logging_config import initialize_logging
from .polling_routes import router as polling_router, set_polling_engine
from .websocket_handler import websocket_endpoint, set_websocket_engine
from .buffer_routes import router as buffer_router, set_buffer_components
from .system_routes import router as system_router, set_system_engine
from .machines_routes import router as machines_router
from .workstages_routes import router as workstages_router
from .plc_connections_routes import router as plc_connections_router
from .tags_routes import router as tags_router
from .polling_groups_routes import router as polling_groups_router
from .alarm_routes import router as alarm_router
from .logs_routes import router as logs_router
from .websocket_monitor import websocket_monitor_endpoint, set_monitor_engine
from .monitor_routes import router as monitor_router

# Initialize logging on module import
initialize_logging()

# Global instances
pool_manager: PoolManager = None
polling_engine: PollingEngine = None
polling_group_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager

    Initializes resources including PollingGroupManager for REST API control.
    The polling groups must be started manually via API endpoints.
    """
    global pool_manager, polling_engine, polling_group_manager

    # Startup
    print("Starting SCADA API Server...")
    print("⚠️  Polling groups are NOT started automatically")
    print("   Use /api/polling-groups/{id}/start to start polling groups")

    # Use absolute path for database
    import os
    from pathlib import Path
    from src.polling.polling_group_manager import PollingGroupManager

    # Get the project root directory (JSOPCUA)
    current_file = Path(__file__).resolve()  # .../backend/src/api/main.py
    backend_dir = current_file.parent.parent.parent  # .../backend
    db_path = str(backend_dir / "data" / "scada.db")

    # Initialize PoolManager
    pool_manager = PoolManager(db_path)
    pool_manager.initialize()
    print(f"✅ PoolManager initialized: {pool_manager.get_plc_count()} PLC(s)")

    # Initialize PollingGroupManager (singleton)
    polling_group_manager = PollingGroupManager(db_path, pool_manager)
    polling_group_manager.initialize()
    print("✅ PollingGroupManager initialized")

    # Also keep legacy polling_engine reference for backwards compatibility
    polling_engine = polling_group_manager.polling_engine

    # Set engine in routes and WebSocket handler
    set_polling_engine(polling_engine)
    set_websocket_engine(polling_engine)
    set_monitor_engine(polling_engine)
    set_system_engine(polling_engine)

    print("✅ SCADA API Server ready (polling groups stopped)")

    yield

    # Shutdown
    print("Shutting down SCADA API Server...")
    if polling_group_manager:
        polling_group_manager.shutdown()
    if pool_manager:
        pool_manager.shutdown()
    print("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Polling Engine API",
    description="REST API for multi-threaded PLC polling engine control and monitoring",
    version="1.0.1",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# Feature 5: Database Management API - Exception Handlers
# ==============================================================================

from fastapi.exceptions import RequestValidationError
import sqlite3
from . import exceptions as custom_exceptions

# Register exception handlers BEFORE including routers
app.add_exception_handler(
    RequestValidationError,
    custom_exceptions.validation_exception_handler
)

app.add_exception_handler(
    sqlite3.Error,
    custom_exceptions.sqlite_exception_handler
)

app.add_exception_handler(
    custom_exceptions.ResourceNotFoundError,
    custom_exceptions.resource_not_found_handler
)

app.add_exception_handler(
    custom_exceptions.DuplicateResourceError,
    custom_exceptions.duplicate_resource_handler
)

app.add_exception_handler(
    custom_exceptions.ForeignKeyError,
    custom_exceptions.foreign_key_handler
)

app.add_exception_handler(
    custom_exceptions.ValidationError,
    custom_exceptions.validation_error_handler
)

# ==============================================================================
# Feature 5: Database Management API - Routers
# ==============================================================================

# 라우터(router)는 FastAPI에서 애플리케이션의 다양한 API 엔드포인트들을 논리적으로 구분하여 관리할 수 있도록 해주는 객체입니다.
# 여러 기능별로 라우터를 정의하고 app.include_router()를 통해 FastAPI 앱에 등록하면, 하나의 app에 다수의 URL 그룹이 깔끔하게 추가됩니다.
#
# 예시:
# from .machines_routes import router as machines_router
#
# app.include_router(machines_router, tags=["machines"])
#
# - from ... import router as ... : 해당 라우터 객체를 임포트합니다.
# - app.include_router(...): 애플리케이션(app)에 API 라우터를 등록(포함)합니다.
# - tags 매개변수는 이 라우터에 속한 엔드포인트들을 그룹화할 때 사용됩니다 (문서에 표시됨).
#
# 아래처럼 모든 주요 도메인별 라우터를 하나씩 app에 포함시켜, 각 도메인(예: machines, processes 등)별로 URL 경로가 자동으로 분리되어 관리됩니다.

app.include_router(machines_router, tags=["machines"])
app.include_router(workstages_router, tags=["workstages"])
app.include_router(plc_connections_router, tags=["plc-connections"])
app.include_router(tags_router, tags=["tags"])
app.include_router(polling_groups_router, tags=["polling-groups"])
app.include_router(alarm_router, tags=["alarms"])
app.include_router(logs_router, tags=["logs"])
app.include_router(monitor_router, tags=["monitor"])
app.include_router(system_router)  # System control (start/stop)
app.include_router(polling_router)
# NOTE: buffer_router is included but components must be set via set_buffer_components()
# app.include_router(buffer_router)  # Uncomment when buffer/writer are running


# WebSocket endpoint
@app.websocket("/ws/polling")
async def websocket_route(websocket: WebSocket):
    """WebSocket endpoint for real-time polling status updates"""
    await websocket_endpoint(websocket)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Polling Engine API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "engine_initialized": polling_engine is not None,
        "pool_manager_initialized": pool_manager is not None
    }


# WebSocket endpoint for Monitor UI
@app.websocket("/ws/monitor")
async def websocket_monitor_route(websocket: WebSocket):
    """WebSocket endpoint for Monitor UI real-time equipment status updates"""
    await websocket_monitor_endpoint(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

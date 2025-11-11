"""
FastAPI Application

Main FastAPI application for polling engine REST API.
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.polling.polling_engine import PollingEngine
from src.plc.pool_manager import PoolManager
from .polling_routes import router as polling_router, set_polling_engine
from .websocket_handler import websocket_endpoint, set_websocket_engine
from .buffer_routes import router as buffer_router, set_buffer_components
from .system_routes import router as system_router, set_system_engine

# Global instances
pool_manager: PoolManager = None
polling_engine: PollingEngine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager

    Initializes resources but does NOT start the polling engine automatically.
    The engine must be started manually via /api/system/start endpoint.
    """
    global pool_manager, polling_engine

    # Startup
    print("Starting SCADA API Server...")
    print("⚠️  Polling engine is NOT started automatically")
    print("   Use /api/system/start to start the system")

    # Use absolute path for database
    import os
    from pathlib import Path

    # Get the project root directory (JSOPCUA)
    current_file = Path(__file__).resolve()  # .../backend/src/api/main.py
    backend_dir = current_file.parent.parent.parent  # .../backend
    db_path = str(backend_dir / "config" / "scada.db")

    # Initialize components but don't start them
    pool_manager = PoolManager(db_path)
    polling_engine = PollingEngine(db_path, pool_manager)
    # NOTE: polling_engine.initialize() is NOT called here
    # It will be called when /api/system/start is invoked

    # Set engine in routes and WebSocket handler
    set_polling_engine(polling_engine)
    set_websocket_engine(polling_engine)
    set_monitor_engine(polling_engine)
    set_system_engine(polling_engine)

    print("✅ SCADA API Server ready (system stopped)")

    yield

    # Shutdown
    print("Shutting down SCADA API Server...")
    if polling_engine and polling_engine._initialized:
        polling_engine.shutdown()
    if pool_manager:
        pool_manager.shutdown()
    print("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Polling Engine API",
    description="REST API for multi-threaded PLC polling engine control and monitoring",
    version="1.0.0",
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

from .machines_routes import router as machines_router
from .processes_routes import router as processes_router
from .plc_connections_routes import router as plc_connections_router
from .tags_routes import router as tags_router
from .polling_groups_routes import router as polling_groups_router
from .alarm_routes import router as alarm_router
from .websocket_monitor import websocket_monitor_endpoint, set_monitor_engine

# Include all routers
app.include_router(system_router)  # System control (start/stop)
app.include_router(polling_router)
app.include_router(machines_router, tags=["machines"])
app.include_router(processes_router, tags=["processes"])
app.include_router(plc_connections_router, tags=["plc-connections"])
app.include_router(tags_router, tags=["tags"])
app.include_router(polling_groups_router, tags=["polling-groups"])
app.include_router(alarm_router, tags=["alarms"])
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

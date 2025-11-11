"""
FastAPI Application

Main FastAPI application for polling engine REST API.
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from polling.polling_engine import PollingEngine
from plc.pool_manager import PoolManager
from .polling_routes import router as polling_router, set_polling_engine
from .websocket_handler import websocket_endpoint, set_websocket_engine
from .buffer_routes import router as buffer_router, set_buffer_components

# Global instances
pool_manager: PoolManager = None
polling_engine: PollingEngine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager

    Initializes and cleans up resources.
    """
    global pool_manager, polling_engine

    # Startup
    print("Starting polling engine API...")

    db_path = "backend/config/scada.db"
    pool_manager = PoolManager(db_path)
    polling_engine = PollingEngine(db_path, pool_manager)
    polling_engine.initialize()

    # Set engine in routes and WebSocket handler
    set_polling_engine(polling_engine)
    set_websocket_engine(polling_engine)

    print("Polling engine API ready")

    yield

    # Shutdown
    print("Shutting down polling engine API...")
    if polling_engine:
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

# Include routers
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# ==============================================================================
# Feature 5: Database Management API - Exception Handlers
# ==============================================================================

from fastapi.exceptions import RequestValidationError
import sqlite3
from . import exceptions as custom_exceptions

# Register exception handlers
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

# Routers will be added here as they are implemented (T020, T027, T039, T055, T068)
# Example:
# from .lines_routes import router as lines_router
# app.include_router(lines_router, prefix="/api", tags=["lines"])

# ==============================================================================
# Feature 5: Database Management API - Lines Router
# ==============================================================================

from .lines_routes import router as lines_router
app.include_router(lines_router, tags=["lines"])

# ==============================================================================
# Feature 5: Database Management API - Processes Router
# ==============================================================================

from .processes_routes import router as processes_router
app.include_router(processes_router, tags=["processes"])

# ==============================================================================
# Feature 5: Database Management API - PLC Connections Router
# ==============================================================================

from .plc_connections_routes import router as plc_connections_router
app.include_router(plc_connections_router, tags=["plc-connections"])

# ==============================================================================
# Feature 5: Database Management API - Tags Router
# ==============================================================================

from .tags_routes import router as tags_router
app.include_router(tags_router, tags=["tags"])

# ==============================================================================
# Feature 5: Database Management API - Polling Groups Router
# ==============================================================================

from .polling_groups_routes import router as polling_groups_router
app.include_router(polling_groups_router, tags=["polling-groups"])

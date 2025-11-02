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

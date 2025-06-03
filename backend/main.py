"""
SolarRally Backend API
FastAPI application for EV charging station control and monitoring
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Dict, List

import paho.mqtt.client as mqtt
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from paho.mqtt.enums import CallbackAPIVersion

from api.sessions import router as sessions_router
from api.auth import router as auth_router
from utils.mqtt_client import MQTTManager
from utils.websocket_manager import WebSocketManager
from db.database import create_db_and_tables, init_default_roles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global managers
mqtt_manager = None
websocket_manager = WebSocketManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global mqtt_manager
    
    # Startup
    logger.info("Starting SolarRally Backend API...")
    
    # Initialize database
    logger.info("Initializing database...")
    await create_db_and_tables()
    await init_default_roles()
    logger.info("Database initialized")
    
    # Start MQTT
    mqtt_manager = MQTTManager(websocket_manager)
    await mqtt_manager.start()
    logger.info("MQTT client connected and subscribed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SolarRally Backend API...")
    if mqtt_manager:
        await mqtt_manager.stop()
    logger.info("Cleanup complete")


# Create FastAPI app
app = FastAPI(
    title="SolarRally API",
    description="Backend API for hybrid solar/grid EV charging station control and monitoring with authentication",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sessions_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/auth")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "SolarRally Backend API with Authentication",
        "status": "running",
        "version": "2.0.0",
        "features": [
            "EVSE Monitoring",
            "Real-time Telemetry", 
            "User Authentication",
            "Role-based Access Control",
            "Session Management"
        ]
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "mqtt_connected": mqtt_manager.is_connected() if mqtt_manager else False,
        "active_websockets": websocket_manager.connection_count(),
        "database": "connected",
        "authentication": "enabled"
    }


@app.websocket("/ws/live/{session_id}")
async def websocket_live_data(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time telemetry data"""
    await websocket_manager.connect(websocket, session_id)
    try:
        while True:
            # Keep connection alive - data is pushed via MQTT handler
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, session_id)


@app.websocket("/ws/live")
async def websocket_live_all(websocket: WebSocket):
    """WebSocket endpoint for all real-time telemetry data"""
    await websocket_manager.connect(websocket, "all")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, "all")

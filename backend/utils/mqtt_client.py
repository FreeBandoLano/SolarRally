"""
MQTT client manager for receiving telemetry data
"""

import asyncio
import json
import logging
import os
import threading
from datetime import datetime
from typing import Optional

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from dotenv import load_dotenv

from models.telemetry import TelemetryData

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class MQTTManager:
    """Manages MQTT connection and forwards telemetry data to WebSocket clients"""
    
    def __init__(self, websocket_manager):
        self.websocket_manager = websocket_manager
        self.client: Optional[mqtt.Client] = None
        self.connected = False
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        
        # MQTT configuration
        self.broker_host = os.getenv("MQTT_BROKER_HOST", "localhost")
        self.broker_port = int(os.getenv("MQTT_BROKER_PORT", 1883))
        self.username = os.getenv("MQTT_USERNAME")
        self.password = os.getenv("MQTT_PASSWORD")
        
        # Topics to subscribe to
        self.telemetry_topic = "evse/+/telemetry"  # + is wildcard for device ID
        
    async def start(self):
        """Start the MQTT client and connect to broker"""
        logger.info(f"Connecting to MQTT broker at {self.broker_host}:{self.broker_port}")
        
        # Store the event loop for later use
        self.loop = asyncio.get_event_loop()
        
        # Create client with CallbackAPIVersion.VERSION2
        self.client = mqtt.Client(
            client_id="solarrally_backend", 
            callback_api_version=CallbackAPIVersion.VERSION2
        )
        
        # Set credentials if provided
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Connect to broker
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()  # Start background thread
            
            # Wait a moment for connection
            await asyncio.sleep(1)
            
            if not self.connected:
                raise ConnectionError("Failed to connect to MQTT broker")
                
        except Exception as e:
            logger.error(f"MQTT connection failed: {e}")
            raise
    
    async def stop(self):
        """Stop the MQTT client"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            logger.info("MQTT client disconnected")
    
    def is_connected(self) -> bool:
        """Check if MQTT client is connected"""
        return self.connected
    
    def _on_connect(self, client, userdata, flags, reason_code, properties):
        """Callback for when the client receives a CONNACK response from the server"""
        if reason_code == 0:
            self.connected = True
            logger.info(f"Connected to MQTT broker")
            
            # Subscribe to telemetry topic
            client.subscribe(self.telemetry_topic, qos=1)
            logger.info(f"Subscribed to topic: {self.telemetry_topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code {reason_code}")
    
    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        """Callback for when the client disconnects from the server"""
        self.connected = False
        logger.warning(f"Disconnected from MQTT broker with result code {reason_code}")
    
    def _on_message(self, client, userdata, msg):
        """Callback for when a PUBLISH message is received from the server"""
        try:
            # Parse the JSON payload
            payload_str = msg.payload.decode('utf-8')
            payload_data = json.loads(payload_str)
            
            logger.debug(f"Received telemetry data from {msg.topic}: {payload_str}")
            
            # Validate the data using Pydantic model
            try:
                # Convert ISO timestamp to datetime object
                if 'timestamp' in payload_data:
                    payload_data['timestamp'] = datetime.fromisoformat(
                        payload_data['timestamp'].replace('Z', '+00:00')
                    )
                
                telemetry = TelemetryData(**payload_data)
                
                # Convert back to dict for JSON serialization
                telemetry_dict = telemetry.dict()
                telemetry_dict['timestamp'] = telemetry.timestamp.isoformat()
                
                # Forward to WebSocket clients using thread-safe async call
                if self.loop and not self.loop.is_closed():
                    asyncio.run_coroutine_threadsafe(
                        self.websocket_manager.broadcast_telemetry(telemetry_dict),
                        self.loop
                    )
                    logger.debug(f"Telemetry data forwarded to WebSocket clients")
                else:
                    logger.warning("Event loop not available, cannot forward telemetry data")
                
            except Exception as validation_error:
                logger.warning(f"Invalid telemetry data received: {validation_error}")
                logger.debug(f"Raw payload: {payload_str}")
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from MQTT message: {e}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}") 
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import time
import json
import os
import uuid
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MQTT Configuration with better error handling
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
try:
    MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
except (ValueError, TypeError):
    MQTT_BROKER_PORT = 1883
    
MQTT_USERNAME = os.getenv("MQTT_USERNAME") # Add if your broker needs auth
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD") # Add if your broker needs auth

DEVICE_ID = os.getenv("MOCK_DEVICE_ID", "evse_mock_001")

# Parse publish interval with better error handling
try:
    interval_str = os.getenv("MOCK_PUBLISH_INTERVAL", "10")
    # Remove any comments from the environment variable value
    interval_str = interval_str.split('#')[0].strip()
    PUBLISH_INTERVAL_SECONDS = int(interval_str)
except (ValueError, TypeError):
    PUBLISH_INTERVAL_SECONDS = 10
    print(f"Warning: Could not parse MOCK_PUBLISH_INTERVAL, using default: {PUBLISH_INTERVAL_SECONDS} seconds")

# Telemetry Topic
TELEMETRY_TOPIC = f"evse/{DEVICE_ID}/telemetry"

# Global state for the mock device
current_session_id = None
session_energy_kwh_solar = 0.0
session_energy_kwh_grid = 0.0
session_total_energy_kwh = 0.0
is_charging = False
current_status = "available" # Initial status

def get_iso_timestamp():
    """Returns the current time in ISO 8601 UTC format."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def on_connect(client, userdata, flags, reason_code, properties):
    """Callback for when the client receives a CONNACK response from the server."""
    if reason_code == 0:
        print(f"Connected to MQTT Broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT} as {DEVICE_ID}")
        # client.subscribe(f"evse/{DEVICE_ID}/control/request") # Example: if we want to listen for commands
        # print(f"Subscribed to evse/{DEVICE_ID}/control/request")
    else:
        print(f"Failed to connect, return code {reason_code}\n")

def on_disconnect(client, userdata, reason_code, properties):
    print(f"Disconnected from MQTT Broker with result code {reason_code}")

# def on_message(client, userdata, msg):
#     """Callback for when a PUBLISH message is received from the server."""
#     print(f"Received message on {msg.topic}: {str(msg.payload.decode())}")
#     # Here you could add logic to handle control commands if subscribed

def simulate_charging_data():
    """Simulates data for a charging EVSE."""
    global current_session_id, session_energy_kwh_solar, session_energy_kwh_grid, session_total_energy_kwh, is_charging, current_status

    if not is_charging:
        # 10% chance to start a new charging session if available
        if current_status == "available" and random.random() < 0.1:
            is_charging = True
            current_status = "preparing"
            current_session_id = f"sid_{uuid.uuid4().hex[:12]}"
            session_energy_kwh_solar = 0.0
            session_energy_kwh_grid = 0.0
            session_total_energy_kwh = 0.0
            print(f"[{get_iso_timestamp()}] New session started: {current_session_id}, Status: {current_status}")
        elif current_status == "preparing":
             current_status = "charging" # Move from preparing to charging
             print(f"[{get_iso_timestamp()}] Session {current_session_id}, Status: {current_status}")


    if is_charging:
        voltage = round(random.uniform(220.0, 240.0), 1)
        current = round(random.uniform(5.0, 32.0), 1) # Assuming up to 32A charging
        power_w = round(voltage * current, 2)
        
        # Determine energy source (simple simulation: 70% solar, 30% grid)
        source_rand = random.random()
        if source_rand < 0.7:
            energy_source = "solar"
            session_energy_kwh_solar += round(power_w / 1000 * (PUBLISH_INTERVAL_SECONDS / 3600), 4)
        else:
            energy_source = "grid"
            session_energy_kwh_grid += round(power_w / 1000 * (PUBLISH_INTERVAL_SECONDS / 3600), 4)
        
        session_total_energy_kwh = round(session_energy_kwh_solar + session_energy_kwh_grid, 4)
        temperature_c = round(random.uniform(25.0, 45.0), 1)

        payload = {
            "timestamp": get_iso_timestamp(),
            "session_id": current_session_id,
            "voltage_v": voltage,
            "current_a": current,
            "power_w": power_w,
            "session_energy_kwh_solar": session_energy_kwh_solar,
            "session_energy_kwh_grid": session_energy_kwh_grid,
            "session_total_energy_kwh": session_total_energy_kwh,
            "energy_source": energy_source,
            "temperature_c": temperature_c,
            "status": current_status
        }

        # 5% chance to stop charging after some energy has been accumulated
        if session_total_energy_kwh > 0.5 and random.random() < 0.05:
            is_charging = False
            current_status = "finishing"
            print(f"[{get_iso_timestamp()}] Session {current_session_id} finishing. Total Energy: {session_total_energy_kwh} kWh")
            # Keep session_id for one last "finishing" message, then it will clear
    
    else: # Not charging
        if current_status == "finishing":
            # After "finishing", move to "available" and clear session
            payload = {
                "timestamp": get_iso_timestamp(),
                "session_id": current_session_id, # Send last session_id with finishing status
                "voltage_v": 0.0,
                "current_a": 0.0,
                "power_w": 0.0,
                "session_energy_kwh_solar": session_energy_kwh_solar,
                "session_energy_kwh_grid": session_energy_kwh_grid,
                "session_total_energy_kwh": session_total_energy_kwh,
                "energy_source": "none",
                "temperature_c": round(random.uniform(20.0, 30.0), 1),
                "status": current_status
            }
            current_status = "available"
            current_session_id = None # Clear session for next cycle
            print(f"[{get_iso_timestamp()}] Session ended. Status: {current_status}")

        else: # Available, faulted, etc.
            payload = {
                "timestamp": get_iso_timestamp(),
                "session_id": None,
                "voltage_v": 0.0,
                "current_a": 0.0,
                "power_w": 0.0,
                "session_energy_kwh_solar": 0.0, # No session, so session energy is 0
                "session_energy_kwh_grid": 0.0,
                "session_total_energy_kwh": 0.0,
                "energy_source": "none",
                "temperature_c": round(random.uniform(20.0, 30.0), 1),
                "status": current_status # Could be "available", "faulted" etc.
            }
            # Randomly set to faulted for a bit
            if current_status == "available" and random.random() < 0.02:
                current_status = "faulted"
            elif current_status == "faulted" and random.random() < 0.2: # Higher chance to recover from fault
                current_status = "available"

    return payload

def run_publisher():
    client = mqtt.Client(client_id=f"mock_pub_{DEVICE_ID}_{uuid.uuid4().hex[:6]}", callback_api_version=CallbackAPIVersion.VERSION2)
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    # client.on_message = on_message # Uncomment if you implement control message handling

    try:
        print(f"Attempting to connect to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}...")
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
        client.loop_start() # Starts a background thread to handle network traffic, dispatches, and callbacks

        while True:
            telemetry_payload = simulate_charging_data()
            payload_json = json.dumps(telemetry_payload)
            
            result = client.publish(TELEMETRY_TOPIC, payload_json, qos=1)
            result.wait_for_publish(timeout=5) # Wait for publish to complete for QoS 1 or 2

            if result.is_published():
                print(f"[{get_iso_timestamp()}] Published to {TELEMETRY_TOPIC}: {payload_json}")
            else:
                print(f"[{get_iso_timestamp()}] Failed to publish to {TELEMETRY_TOPIC}. MID: {result.mid}")

            time.sleep(PUBLISH_INTERVAL_SECONDS)

    except ConnectionRefusedError:
        print(f"Connection refused. Check if MQTT broker is running at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT} and accessible.")
    except KeyboardInterrupt:
        print("Publisher interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Disconnecting publisher...")
        client.loop_stop() # Stop the background thread
        client.disconnect()
        print("Publisher disconnected.")

if __name__ == "__main__":
    run_publisher() 
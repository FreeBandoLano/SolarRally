#!/usr/bin/env python3
"""
Enhanced Mock EVSE Publisher for SolarRally
Simulates multiple realistic EV charging scenarios with:
- Multiple EVSE units
- Time-based solar availability  
- Dynamic charging sessions
- Different charging speeds (Level 1/2/3)
- Grid load balancing
- Realistic charging patterns
"""

import json
import time
import random
import uuid
import os
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

# Parse publish interval with better error handling
try:
    interval_str = os.getenv("MOCK_PUBLISH_INTERVAL", "5")
    # Remove any comments from the environment variable value
    interval_str = interval_str.split('#')[0].strip()
    PUBLISH_INTERVAL = int(interval_str)
except (ValueError, TypeError):
    PUBLISH_INTERVAL = 5
    print(f"Warning: Could not parse MOCK_PUBLISH_INTERVAL, using default: {PUBLISH_INTERVAL} seconds")

# EVSE Configuration
NUM_EVSE_UNITS = 3  # Simulate 3 charging stations
CHARGING_LEVELS = {
    1: {"max_current": 16, "voltage": 230, "name": "Level 1 (Slow)"},
    2: {"max_current": 32, "voltage": 230, "name": "Level 2 (Fast)"},
    3: {"max_current": 63, "voltage": 400, "name": "Level 3 (Rapid)"}
}

class EVSEUnit:
    """Represents a single EVSE charging unit with realistic behavior"""
    
    def __init__(self, unit_id: str, charging_level: int = 2):
        self.unit_id = unit_id
        self.charging_level = charging_level
        self.session_id: Optional[str] = None
        self.status = "available"  # available, preparing, charging, finishing, faulted
        self.current_power_w = 0.0
        self.session_energy_solar = 0.0
        self.session_energy_grid = 0.0
        self.temperature = random.uniform(20, 25)
        self.fault_start_time = None
        self.session_start_time = None
        self.target_energy = 0.0  # kWh target for this session
        
        # Charging characteristics
        self.max_current = CHARGING_LEVELS[charging_level]["max_current"]
        self.voltage = CHARGING_LEVELS[charging_level]["voltage"]
        self.max_power = self.voltage * self.max_current
        
    def get_solar_availability(self) -> float:
        """Get solar availability based on time of day (0.0 to 1.0)"""
        current_hour = datetime.now().hour
        
        # Solar panel simulation: peak at midday, none at night
        if 6 <= current_hour <= 18:  # Daylight hours
            # Peak solar at 12 PM, gradually decreasing
            if current_hour <= 12:
                return (current_hour - 6) / 6  # Ramp up
            else:
                return (18 - current_hour) / 6  # Ramp down
        else:
            return 0.0  # No solar at night
            
    def should_start_session(self) -> bool:
        """Determine if a new charging session should start"""
        if self.status != "available":
            return False
            
        # Higher probability during peak hours (7-9 AM, 5-7 PM)
        current_hour = datetime.now().hour
        base_probability = 0.02  # 2% base chance per interval
        
        if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:
            probability = base_probability * 3  # Peak hours
        elif 10 <= current_hour <= 16:
            probability = base_probability * 1.5  # Moderate hours
        elif 22 <= current_hour or current_hour <= 6:
            probability = base_probability * 0.3  # Low activity at night
        else:
            probability = base_probability
            
        return random.random() < probability
        
    def should_end_session(self) -> bool:
        """Determine if current session should end"""
        if self.status != "charging":
            return False
            
        # End session if target energy reached
        total_energy = self.session_energy_solar + self.session_energy_grid
        if total_energy >= self.target_energy:
            return True
            
        # Small random chance to end early (user disconnects)
        return random.random() < 0.01
        
    def should_fault(self) -> bool:
        """Determine if unit should go into fault state"""
        if self.status == "faulted":
            # Recovery from fault after some time
            if self.fault_start_time and time.time() - self.fault_start_time > 30:
                return random.random() < 0.3  # 30% chance to recover
        else:
            # Random fault occurrence (very low probability)
            return random.random() < 0.005
            
    def update_status(self):
        """Update the EVSE unit status based on conditions"""
        
        # Handle fault states
        if self.should_fault():
            if self.status != "faulted":
                self.status = "faulted"
                self.fault_start_time = time.time()
                self.current_power_w = 0
                print(f"⚠️  Unit {self.unit_id}: FAULT occurred!")
            elif self.fault_start_time and time.time() - self.fault_start_time > 30:
                if random.random() < 0.3:  # 30% chance to recover
                    self.status = "available"
                    self.fault_start_time = None
                    print(f"✅ Unit {self.unit_id}: Recovered from fault")
            return
            
        # Handle status transitions
        if self.status == "available" and self.should_start_session():
            self.status = "preparing"
            self.session_id = f"sess_{uuid.uuid4().hex[:8]}"
            self.session_start_time = time.time()
            self.session_energy_solar = 0.0
            self.session_energy_grid = 0.0
            # Random target energy between 10-80 kWh
            self.target_energy = random.uniform(10, 80)
            print(f"🔌 Unit {self.unit_id}: New session {self.session_id} started (target: {self.target_energy:.1f} kWh)")
            
        elif self.status == "preparing":
            # Move from preparing to charging after a brief delay
            if self.session_start_time and time.time() - self.session_start_time > 10:
                self.status = "charging"
                print(f"⚡ Unit {self.unit_id}: Started charging session {self.session_id}")
                
        elif self.status == "charging":
            if self.should_end_session():
                self.status = "finishing"
                print(f"🔋 Unit {self.unit_id}: Session {self.session_id} finishing (delivered: {self.session_energy_solar + self.session_energy_grid:.2f} kWh)")
                
        elif self.status == "finishing":
            # Move back to available after finishing
            self.status = "available"
            self.session_id = None
            self.current_power_w = 0
            self.session_start_time = None
            print(f"✅ Unit {self.unit_id}: Session completed, now available")
            
    def simulate_charging_power(self) -> float:
        """Simulate realistic charging power based on status and conditions"""
        if self.status != "charging":
            return 0.0
            
        # Simulate realistic charging curve (starts high, tapers off near end)
        total_energy = self.session_energy_solar + self.session_energy_grid
        charge_percentage = min(total_energy / self.target_energy, 1.0) if self.target_energy > 0 else 0
        
        # Charging curve: 100% power until 80%, then taper to 20%
        if charge_percentage < 0.8:
            power_factor = 1.0
        else:
            # Linear taper from 80% to 100%
            power_factor = 1.0 - (charge_percentage - 0.8) * 4 * 0.8  # Reduce to 20%
            power_factor = max(0.2, power_factor)
            
        # Add some random variation (±10%)
        power_factor *= random.uniform(0.9, 1.1)
        
        # Calculate actual power
        target_power = self.max_power * power_factor
        
        # Add grid load balancing (reduce power during peak hours)
        current_hour = datetime.now().hour
        if 17 <= current_hour <= 20:  # Peak grid hours
            target_power *= 0.7  # Reduce to 70%
            
        return min(target_power, self.max_power)
        
    def get_energy_source(self) -> str:
        """Determine energy source based on solar availability and grid conditions"""
        if self.status != "charging":
            return "none"
            
        solar_availability = self.get_solar_availability()
        
        # Smart charging logic
        if solar_availability > 0.7:
            return "solar"  # High solar
        elif solar_availability > 0.3:
            # Mix of solar and grid
            return "solar" if random.random() < solar_availability else "grid"
        else:
            return "grid"  # Low/no solar
            
    def generate_telemetry(self) -> Dict:
        """Generate telemetry data for this EVSE unit"""
        self.update_status()
        
        # Update temperature based on charging
        if self.status == "charging":
            self.temperature += random.uniform(-0.5, 1.0)  # Heating up
            self.temperature = min(self.temperature, 60)  # Max temp
        else:
            self.temperature += random.uniform(-0.8, 0.2)  # Cooling down
            self.temperature = max(self.temperature, 15)  # Min temp
            
        # Calculate power and energy
        self.current_power_w = self.simulate_charging_power()
        
        if self.status == "charging" and self.current_power_w > 0:
            # Add energy based on power and time interval
            energy_added = (self.current_power_w / 1000) * (PUBLISH_INTERVAL / 3600)
            
            energy_source = self.get_energy_source()
            if energy_source == "solar":
                self.session_energy_solar += energy_added
            elif energy_source == "grid":
                self.session_energy_grid += energy_added
        else:
            energy_source = "none"
            
        # Calculate voltage and current from power
        if self.current_power_w > 0:
            voltage = self.voltage + random.uniform(-5, 5)  # Voltage fluctuation
            current = self.current_power_w / voltage
        else:
            voltage = 0.0
            current = 0.0
            
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "voltage_v": round(voltage, 1),
            "current_a": round(current, 1),
            "power_w": round(self.current_power_w, 1),
            "session_energy_kwh_solar": round(self.session_energy_solar, 4),
            "session_energy_kwh_grid": round(self.session_energy_grid, 4),
            "session_total_energy_kwh": round(self.session_energy_solar + self.session_energy_grid, 4),
            "energy_source": energy_source,
            "temperature_c": round(self.temperature, 1),
            "status": self.status
        }

class EnhancedMockPublisher:
    """Enhanced mock publisher managing multiple EVSE units"""
    
    def __init__(self):
        self.client = None
        self.evse_units: List[EVSEUnit] = []
        self.running = False
        
        # Create EVSE units with different charging levels
        for i in range(NUM_EVSE_UNITS):
            unit_id = f"evse_unit_{i+1:02d}"
            # Mix of charging levels
            level = 2 if i < 2 else 3  # First 2 are Level 2, last is Level 3
            unit = EVSEUnit(unit_id, level)
            self.evse_units.append(unit)
            
    def setup_mqtt(self):
        """Setup MQTT client"""
        client_id = f"enhanced_mock_pub_{uuid.uuid4().hex[:8]}"
        self.client = mqtt.Client(client_id=client_id, callback_api_version=CallbackAPIVersion.VERSION2)
        
        if MQTT_USERNAME and MQTT_PASSWORD:
            self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
            
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        
    def on_connect(self, client, userdata, flags, reason_code, properties):
        """MQTT connection callback"""
        if reason_code == 0:
            print(f"🔗 Connected to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
            print(f"📊 Managing {NUM_EVSE_UNITS} EVSE units with enhanced scenarios")
        else:
            print(f"❌ Failed to connect to MQTT broker, code: {reason_code}")
            
    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        """MQTT disconnection callback"""
        print(f"🔌 Disconnected from MQTT broker (code: {reason_code})")
        
    def publish_unit_data(self, unit: EVSEUnit):
        """Publish telemetry data for a single EVSE unit"""
        try:
            telemetry = unit.generate_telemetry()
            topic = f"evse/{unit.unit_id}/telemetry"
            payload = json.dumps(telemetry)
            
            result = self.client.publish(topic, payload, qos=1)
            
            # Log interesting events
            if unit.status in ["preparing", "charging", "finishing", "faulted"]:
                status_emoji = {
                    "preparing": "🔄",
                    "charging": "⚡",
                    "finishing": "🔋", 
                    "faulted": "⚠️"
                }
                emoji = status_emoji.get(unit.status, "📊")
                energy_total = telemetry["session_total_energy_kwh"]
                print(f"{emoji} {unit.unit_id}: {unit.status.upper()} | "
                      f"Power: {telemetry['power_w']:.0f}W | "
                      f"Source: {telemetry['energy_source']} | "
                      f"Energy: {energy_total:.2f}kWh | "
                      f"Temp: {telemetry['temperature_c']}°C")
                      
        except Exception as e:
            print(f"❌ Error publishing data for {unit.unit_id}: {e}")
            
    def print_system_status(self):
        """Print overall system status"""
        available = sum(1 for unit in self.evse_units if unit.status == "available")
        charging = sum(1 for unit in self.evse_units if unit.status == "charging")
        preparing = sum(1 for unit in self.evse_units if unit.status == "preparing")
        finishing = sum(1 for unit in self.evse_units if unit.status == "finishing")
        faulted = sum(1 for unit in self.evse_units if unit.status == "faulted")
        
        total_power = sum(unit.current_power_w for unit in self.evse_units)
        solar_availability = self.evse_units[0].get_solar_availability() * 100
        
        print(f"\n🏢 SYSTEM STATUS | Solar: {solar_availability:.0f}% | Total Power: {total_power:.0f}W")
        print(f"   Available: {available} | Charging: {charging} | Preparing: {preparing} | Finishing: {finishing} | Faulted: {faulted}")
        print("-" * 80)
        
    def run(self):
        """Main publisher loop"""
        self.setup_mqtt()
        
        try:
            print(f"🚀 Starting Enhanced Mock Publisher...")
            print(f"📡 Connecting to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
            
            self.client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
            self.client.loop_start()
            
            self.running = True
            cycle_count = 0
            
            while self.running:
                # Publish data for all units
                for unit in self.evse_units:
                    self.publish_unit_data(unit)
                    
                # Print system status every 10 cycles
                if cycle_count % 10 == 0:
                    self.print_system_status()
                    
                cycle_count += 1
                time.sleep(PUBLISH_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n🛑 Publisher stopped by user")
        except Exception as e:
            print(f"❌ Publisher error: {e}")
        finally:
            self.stop()
            
    def stop(self):
        """Stop the publisher"""
        self.running = False
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
        print("👋 Enhanced Mock Publisher stopped")

if __name__ == "__main__":
    publisher = EnhancedMockPublisher()
    publisher.run() 
#!/usr/bin/env python3
"""
SolarRally Scenario Launcher
Interactive script to launch different charging scenarios
"""

import os
import sys
import subprocess
import signal
import time

def print_banner():
    """Print the SolarRally banner"""
    print("="*60)
    print("🌞⚡ SOLARRALLY - EV Charging Scenarios ⚡🌞")
    print("="*60)
    print("Choose a scenario to simulate realistic EV charging patterns")
    print()

def print_scenarios():
    """Print available scenarios"""
    scenarios = {
        "1": {
            "name": "🔄 Enhanced Mock Publisher",
            "description": "Standard multi-unit simulation with realistic patterns",
            "script": "enhanced_mock_publisher.py",
            "features": ["3 EVSE units", "Time-based solar", "Dynamic sessions", "Smart charging"]
        },
        "2": {
            "name": "🚗💨 Rush Hour Peak Demand",
            "description": "High-demand evening charging with grid constraints",
            "script": "scenarios/rush_hour_scenario.py",
            "features": ["5 EVSE units", "Low solar (10%)", "High demand", "Grid load balancing"]
        },
        "3": {
            "name": "☀️⚡ Solar Peak Optimization",
            "description": "Optimal charging during peak solar hours",
            "script": "scenarios/solar_peak_scenario.py",
            "features": ["4 EVSE units", "Peak solar (85-100%)", "Smart scheduling", "Renewable priority"]
        },
        "4": {
            "name": "🌙🔋 Night Charging",
            "description": "Low-cost night charging with grid energy",
            "script": "scenarios/night_charging_scenario.py",
            "features": ["2 EVSE units", "No solar", "Off-peak rates", "Slow charging"]
        },
        "5": {
            "name": "⚠️🔧 Fault & Recovery",
            "description": "Scenario with equipment faults and recovery",
            "script": "scenarios/fault_scenario.py",
            "features": ["3 EVSE units", "Random faults", "Auto recovery", "Fault handling"]
        }
    }
    
    for key, scenario in scenarios.items():
        print(f"{key}. {scenario['name']}")
        print(f"   {scenario['description']}")
        print(f"   Features: {', '.join(scenario['features'])}")
        print()
    
    return scenarios

def run_scenario(script_path):
    """Run the selected scenario"""
    try:
        print(f"🚀 Starting scenario: {script_path}")
        print("💡 Press Ctrl+C to stop the scenario")
        print("-" * 50)
        
        # Run the script
        process = subprocess.Popen([sys.executable, script_path], 
                                 cwd=os.path.dirname(os.path.abspath(__file__)))
        
        # Wait for process to complete or be interrupted
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Scenario stopped by user")
        if process:
            process.terminate()
            process.wait()
    except Exception as e:
        print(f"❌ Error running scenario: {e}")

def create_missing_scenarios():
    """Create missing scenario files"""
    
    # Night charging scenario
    night_scenario = """#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from enhanced_mock_publisher import EVSEUnit, EnhancedMockPublisher
import random, time

class NightChargingScenario(EnhancedMockPublisher):
    def __init__(self):
        super().__init__()
        self.scenario_name = "Night Charging Off-Peak"
        self.evse_units = []
        for i in range(2):
            unit_id = f"evse_night_{i+1:02d}"
            unit = EVSEUnit(unit_id, 2)
            if i == 0:  # Start one charging
                unit.status = "charging"
                unit.session_id = f"night_sess_{i+1}"
                unit.session_start_time = time.time() - 1800
                unit.target_energy = random.uniform(40, 80)
                unit.session_energy_grid = random.uniform(5, 15)
            self.evse_units.append(unit)
    
    def simulate_night_conditions(self):
        for unit in self.evse_units:
            unit.get_solar_availability = lambda: 0.0  # No solar at night
            unit.should_start_session = lambda: unit.status == "available" and random.random() < 0.08
            original_power = unit.simulate_charging_power
            unit.simulate_charging_power = lambda: original_power() * 0.8  # Slower night charging
    
    def run(self):
        print(f"🌙🔋 Starting {self.scenario_name} Scenario")
        print("🌃 Night time off-peak charging with grid energy only")
        print("-" * 60)
        self.simulate_night_conditions()
        super().run()

if __name__ == "__main__":
    NightChargingScenario().run()
"""
    
    # Fault scenario
    fault_scenario = """#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from enhanced_mock_publisher import EVSEUnit, EnhancedMockPublisher
import random, time

class FaultScenario(EnhancedMockPublisher):
    def __init__(self):
        super().__init__()
        self.scenario_name = "Fault & Recovery Testing"
        self.evse_units = []
        for i in range(3):
            unit_id = f"evse_fault_{i+1:02d}"
            unit = EVSEUnit(unit_id, 2)
            # Start one unit in fault state
            if i == 0:
                unit.status = "faulted"
                unit.fault_start_time = time.time() - 20
            elif i == 1:  # One charging normally
                unit.status = "charging"
                unit.session_id = f"fault_sess_{i+1}"
                unit.session_start_time = time.time() - 600
                unit.target_energy = 30
                unit.session_energy_solar = 3
            self.evse_units.append(unit)
    
    def simulate_fault_conditions(self):
        for unit in self.evse_units:
            original_fault = unit.should_fault
            unit.should_fault = lambda: random.random() < 0.02 if unit.status != "faulted" else (
                random.random() < 0.4 if unit.fault_start_time and time.time() - unit.fault_start_time > 15 else False
            )
    
    def run(self):
        print(f"⚠️🔧 Starting {self.scenario_name} Scenario")
        print("🔧 Testing equipment faults and automatic recovery")
        print("-" * 60)
        self.simulate_fault_conditions()
        super().run()

if __name__ == "__main__":
    FaultScenario().run()
"""
    
    # Create scenario directories and files
    scenarios_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scenarios")
    os.makedirs(scenarios_dir, exist_ok=True)
    
    # Write night charging scenario
    with open(os.path.join(scenarios_dir, "night_charging_scenario.py"), "w", encoding='utf-8') as f:
        f.write(night_scenario)
    
    # Write fault scenario  
    with open(os.path.join(scenarios_dir, "fault_scenario.py"), "w", encoding='utf-8') as f:
        f.write(fault_scenario)

def main():
    """Main launcher function"""
    # Create missing scenario files
    create_missing_scenarios()
    
    while True:
        print_banner()
        scenarios = print_scenarios()
        
        try:
            choice = input("🎯 Select a scenario (1-5) or 'q' to quit: ").strip().lower()
            
            if choice == 'q' or choice == 'quit':
                print("👋 Goodbye!")
                break
            
            if choice in scenarios:
                script_path = scenarios[choice]["script"]
                script_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_path)
                
                if os.path.exists(script_full_path):
                    run_scenario(script_full_path)
                else:
                    print(f"❌ Scenario script not found: {script_full_path}")
                
                input("\n⏎ Press Enter to return to menu...")
            else:
                print("❌ Invalid choice. Please select 1-5 or 'q' to quit.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(1)
        
        # Clear screen for next iteration (works on most terminals)
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main() 
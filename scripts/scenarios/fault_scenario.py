#!/usr/bin/env python3
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

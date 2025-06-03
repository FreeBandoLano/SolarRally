#!/usr/bin/env python3
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

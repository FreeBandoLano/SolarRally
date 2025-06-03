#!/usr/bin/env python3
"""
Rush Hour Scenario for SolarRally
Simulates high-demand charging during peak hours (5-7 PM)
with limited solar availability and grid load balancing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_mock_publisher import EVSEUnit, EnhancedMockPublisher
import random
import time

class RushHourScenario(EnhancedMockPublisher):
    """Simulates rush hour charging scenario"""
    
    def __init__(self):
        super().__init__()
        self.scenario_name = "Rush Hour Peak Demand"
        
        # Override units for rush hour - more units, higher demand
        self.evse_units = []
        for i in range(5):  # 5 units for rush hour
            unit_id = f"evse_rush_{i+1:02d}"
            level = 2 if i < 3 else 3  # Mix of Level 2 and 3
            unit = EVSEUnit(unit_id, level)
            
            # Force some units to start charging immediately
            if i < 3:
                unit.status = "preparing"
                unit.session_id = f"rush_sess_{i+1}"
                unit.session_start_time = time.time() - 5
                unit.target_energy = random.uniform(20, 60)  # Higher energy needs
                
            self.evse_units.append(unit)
    
    def simulate_rush_hour_conditions(self):
        """Override conditions for rush hour"""
        for unit in self.evse_units:
            # Override solar availability (very low in evening)
            original_get_solar = unit.get_solar_availability
            unit.get_solar_availability = lambda: 0.1  # Only 10% solar
            
            # Increase session start probability
            original_should_start = unit.should_start_session
            unit.should_start_session = lambda: (
                unit.status == "available" and random.random() < 0.15  # 15% chance
            )
            
            # Reduce power due to grid constraints
            original_simulate_power = unit.simulate_charging_power
            def grid_constrained_power():
                base_power = original_simulate_power()
                return base_power * 0.8  # 20% reduction due to grid load
            unit.simulate_charging_power = grid_constrained_power
    
    def run(self):
        """Run rush hour scenario"""
        print(f"🚗💨 Starting {self.scenario_name} Scenario")
        print(f"🌅 Simulating evening rush hour with high demand and low solar")
        print(f"⚡ {len(self.evse_units)} charging stations active")
        print(f"🔋 Grid load balancing in effect")
        print("-" * 60)
        
        self.simulate_rush_hour_conditions()
        super().run()

if __name__ == "__main__":
    scenario = RushHourScenario()
    scenario.run() 
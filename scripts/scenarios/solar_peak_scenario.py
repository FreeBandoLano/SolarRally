#!/usr/bin/env python3
"""
Solar Peak Scenario for SolarRally
Simulates optimal charging conditions during peak solar hours (11 AM - 2 PM)
with maximum renewable energy usage and smart charging
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_mock_publisher import EVSEUnit, EnhancedMockPublisher
import random
import time

class SolarPeakScenario(EnhancedMockPublisher):
    """Simulates optimal solar charging scenario"""
    
    def __init__(self):
        super().__init__()
        self.scenario_name = "Solar Peak Optimization"
        
        # Create units optimized for solar charging
        self.evse_units = []
        for i in range(4):  # 4 units for solar scenario
            unit_id = f"evse_solar_{i+1:02d}"
            level = 2  # Level 2 optimal for solar charging
            unit = EVSEUnit(unit_id, level)
            
            # Start some units already charging to show solar usage
            if i < 2:
                unit.status = "charging"
                unit.session_id = f"solar_sess_{i+1}"
                unit.session_start_time = time.time() - 900  # 15 mins ago
                unit.target_energy = random.uniform(25, 45)
                unit.session_energy_solar = random.uniform(3, 8)  # Already some solar energy
                
            self.evse_units.append(unit)
    
    def simulate_solar_peak_conditions(self):
        """Override conditions for solar peak"""
        for unit in self.evse_units:
            # Override solar availability (peak solar)
            unit.get_solar_availability = lambda: random.uniform(0.85, 1.0)  # 85-100% solar
            
            # Smart charging: prefer solar times
            original_should_start = unit.should_start_session
            unit.should_start_session = lambda: (
                unit.status == "available" and random.random() < 0.12  # 12% chance during solar peak
            )
            
            # Boost power during high solar availability
            original_simulate_power = unit.simulate_charging_power
            def solar_boosted_power():
                base_power = original_simulate_power()
                solar_factor = unit.get_solar_availability()
                return base_power * (1.0 + solar_factor * 0.1)  # Up to 10% boost
            unit.simulate_charging_power = solar_boosted_power
            
            # Force solar energy source during peak
            original_get_source = unit.get_energy_source
            def prioritize_solar():
                if unit.status == "charging":
                    solar_avail = unit.get_solar_availability()
                    if solar_avail > 0.8:
                        return "solar"
                    elif solar_avail > 0.4:
                        return "solar" if random.random() < 0.85 else "grid"  # 85% solar preference
                    else:
                        return "grid"
                return "none"
            unit.get_energy_source = prioritize_solar
    
    def print_system_status(self):
        """Enhanced status for solar scenario"""
        available = sum(1 for unit in self.evse_units if unit.status == "available")
        charging = sum(1 for unit in self.evse_units if unit.status == "charging")
        preparing = sum(1 for unit in self.evse_units if unit.status == "preparing")
        finishing = sum(1 for unit in self.evse_units if unit.status == "finishing")
        
        total_power = sum(unit.current_power_w for unit in self.evse_units)
        solar_availability = self.evse_units[0].get_solar_availability() * 100
        
        # Calculate solar vs grid energy
        total_solar_energy = sum(unit.session_energy_solar for unit in self.evse_units)
        total_grid_energy = sum(unit.session_energy_grid for unit in self.evse_units)
        total_energy = total_solar_energy + total_grid_energy
        
        solar_percentage = (total_solar_energy / total_energy * 100) if total_energy > 0 else 0
        
        print(f"\n☀️ SOLAR PEAK STATUS | Solar Avail: {solar_availability:.0f}% | Total Power: {total_power:.0f}W")
        print(f"   🌱 Solar Energy: {solar_percentage:.1f}% ({total_solar_energy:.2f} kWh)")
        print(f"   ⚡ Grid Energy: {100-solar_percentage:.1f}% ({total_grid_energy:.2f} kWh)")
        print(f"   📊 Available: {available} | Charging: {charging} | Preparing: {preparing} | Finishing: {finishing}")
        print("-" * 80)
    
    def run(self):
        """Run solar peak scenario"""
        print(f"☀️⚡ Starting {self.scenario_name} Scenario")
        print(f"🌞 Simulating peak solar hours with maximum renewable energy")
        print(f"🔋 {len(self.evse_units)} charging stations optimized for solar")
        print(f"🌱 Smart charging prioritizing renewable energy")
        print("-" * 60)
        
        self.simulate_solar_peak_conditions()
        super().run()

if __name__ == "__main__":
    scenario = SolarPeakScenario()
    scenario.run() 
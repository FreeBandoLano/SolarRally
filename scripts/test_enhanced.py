#!/usr/bin/env python3
"""
Quick test for enhanced mock publisher
"""

import sys
import os

# Test environment variable parsing
os.environ["MOCK_PUBLISH_INTERVAL"] = "10 # Publish every 10 seconds"

try:
    from enhanced_mock_publisher import EnhancedMockPublisher
    print("✅ Enhanced mock publisher imported successfully!")
    
    # Test creating the publisher
    publisher = EnhancedMockPublisher()
    print(f"✅ Publisher created with {len(publisher.evse_units)} EVSE units")
    
    # Test generating telemetry
    for i, unit in enumerate(publisher.evse_units):
        telemetry = unit.generate_telemetry()
        print(f"✅ Unit {unit.unit_id}: {telemetry['status']} - {telemetry['power_w']:.1f}W")
        if i >= 2:  # Only show first 3
            break
    
    print("🎉 Enhanced mock publisher test completed successfully!")
    
except Exception as e:
    print(f"❌ Error testing enhanced mock publisher: {e}")
    import traceback
    traceback.print_exc() 
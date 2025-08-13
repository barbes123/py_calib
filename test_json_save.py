#!/usr/bin/env python3
"""
Simple test script to verify JSON saving functionality
"""
import os
import sys
import json

# Add lib path
sys.path.insert(1, 'lib')

from plot_multiple_function import plot_peak_positions_vs_time

def test_json_save():
    """Test the JSON saving functionality with mock data"""
    print("Testing JSON save functionality...")
    
    # Test parameters - adjust these based on your actual data
    target_run = 63  # Adjust based on available data
    domain_start = 100
    domain_end = 109  
    target_S = 9
    
    try:
        # Test with annotations disabled
        result = plot_peak_positions_vs_time(
            target_run=target_run,
            domain_start=domain_start,
            domain_end=domain_end,
            target_S=target_S,
            verbose=True,
            create_plots=False,  # Only test JSON saving, no plots
            show_annotations=False  # Test the new annotation control
        )
        
        if result is None:
            print("❌ Function returned None - likely no data found")
            return False
            
        print(f"✅ Function returned result with {len(result.get('y', []))} data points")
        
        # Check if JSON file was created
        if 'json_output_path' in result and result['json_output_path']:
            json_path = result['json_output_path']
            if os.path.exists(json_path):
                print(f"✅ JSON file created: {json_path}")
                
                # Verify JSON content
                with open(json_path, 'r') as f:
                    json_data = json.load(f)
                
                print(f"✅ JSON structure verified:")
                print(f"   - Metadata keys: {list(json_data.get('metadata', {}).keys())}")
                print(f"   - Data points: {len(json_data.get('data_points', []))}")
                print(f"   - Total data points: {json_data.get('metadata', {}).get('total_data_points', 0)}")
                
                return True
            else:
                print(f"❌ JSON file not found at: {json_path}")
                return False
        else:
            print("❌ JSON output path not provided in result")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_json_save()
    if success:
        print("\n🎉 JSON saving functionality test PASSED!")
    else:
        print("\n💥 JSON saving functionality test FAILED!")
        sys.exit(1)

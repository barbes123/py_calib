"""
Bulk ROOT File Timing Extraction Tool

This script processes multiple ROOT files from nuclear physics experiments to extract
timing information from the ELIADE detector system. It's designed to work with files
that follow a specific naming convention and contain timing data in picosecond resolution.

FUNCTIONALITY:
--------------
1. Searches for ROOT files matching the pattern: run{NUMBER}_*_eliadeS2.root
2. Opens each file and accesses the "ELIADE_Tree" tree structure
3. Extracts "FineTS" (Fine Time Stamps) data arrays
4. Calculates the duration of each recording as (max_timestamp - min_timestamp)
5. Outputs results in both human-readable format and JSON file

FILE NAMING CONVENTION:
-----------------------
Expected input files: run171_0_eliadeS2.root, run171_1_eliadeS2.root, etc.
Where:
- 171 is the run number
- 0, 1, etc. are file sequence numbers
- eliadeS2 indicates the detector/system type

OUTPUT:
-------
- Console output showing processing progress and timing summaries
- JSON file containing all durations in picoseconds for further analysis
- Total recording time calculation across all processed files

USAGE EXAMPLES:
---------------
# Process all files for run 171, save to default output file
python bulk_extract_times.py 171

# Process run 205 and save to custom output file
python bulk_extract_times.py 205 --output run205_times.json

# Process run 150 with short option for output
python bulk_extract_times.py 150 -o my_results.json

REQUIREMENTS:
-------------
- uproot: For reading ROOT files
- numpy: For numerical array operations
- Input ROOT files must contain "ELIADE_Tree" with "FineTS" branch
- Files must be in the current working directory
"""

import uproot
import numpy as np
import json
import os
import glob
import argparse

def process_single_file(filename):
    """Process a single ROOT file and return duration in picoseconds"""
    try:
        # Open the ROOT file
        file = uproot.open(filename)
        tree = file["ELIADE_Tree"]
        
        # Extract FineTS data
        fine_timestamps = np.array(tree["FineTS"].array())
        
        if len(fine_timestamps) == 0:
            return None
        
        # Calculate duration in picoseconds
        duration_picoseconds = int(fine_timestamps.max() - fine_timestamps.min())
        
        file.close()
        return duration_picoseconds
        
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return None

def bulk_process_runs(run_number):
    """Process all files for a given run number"""
    
    # Pattern to match files like run171_0_eliadeS2.root, run171_1_eliadeS2.root, etc.
    pattern = f"run{run_number}_*_eliadeS2.root"
    
    # Find all matching files
    files = glob.glob(pattern)
    files.sort()  # Sort to ensure consistent ordering
    
    print(f"Found {len(files)} files for run {run_number}")
    
    results = {}
    
    for filepath in files:
        print(f"Processing {filepath}...")
        
        # Extract filename without .root extension
        filename_no_ext = os.path.splitext(os.path.basename(filepath))[0]
        
        # Process the file
        duration = process_single_file(filepath)
        
        if duration is not None:
            results[filename_no_ext] = duration
            print(f"  Duration: {duration} picoseconds ({duration/1e12:.3f} seconds)")
        else:
            print(f"  Failed to process")
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Extract timing information from multiple ROOT files')
    parser.add_argument('run_number', type=int, help='Run number to process (e.g., 171)')
    parser.add_argument('--output', '-o', default='run_durations.json', help='Output JSON filename')
    
    args = parser.parse_args()
    
    print(f"Processing run {args.run_number}...")
    
    # Process all files for the run
    durations = bulk_process_runs(args.run_number)
    
    if not durations:
        print("No files processed successfully!")
        return
    
    # Create output structure
    output_data = {
        "run_durations_picoseconds": durations
    }
    
    # Write to JSON file
    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nResults written to {args.output}")
    print(f"Processed {len(durations)} files:")
    
    # Print summary
    total_duration_ps = sum(durations.values())
    total_duration_s = total_duration_ps / 1e12
    
    for filename, duration_ps in durations.items():
        duration_s = duration_ps / 1e12
        print(f"  {filename}: {duration_ps} ps ({duration_s:.3f} s)")
    
    print(f"\nTotal recording time: {total_duration_ps} ps ({total_duration_s:.3f} s)")

if __name__ == "__main__":
    main()
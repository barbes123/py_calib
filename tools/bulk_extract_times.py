#! /usr/bin/python3

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
#        print("Tree is taken")
    except Exception as e:
        print(f"Cannot get Tree")
        return None

        
    try:
        # Extract FineTS data
        fine_timestamps = np.array(tree["FineTS"].array())
        fine_timestamps = fine_timestamps[~np.isnan(fine_timestamps)]
    except Exception as e:
        print(f"Cannot get FineTS")
        return None
        
    try:        
        if len(fine_timestamps) == 0:
            return None
        
        # Calculate duration in picoseconds
        duration_picoseconds = float(fine_timestamps.max() - fine_timestamps.min())/1e12
        print(f'duration_picoseconds {duration_picoseconds} fine_timestamps.max(), fine_timestamps.min()')
        
        file.close()
        return duration_picoseconds
        
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return None

def bulk_process_runs(serverID, run_number):
    """Process all files for a given run number"""
    
    # Pattern to match files like run171_0_eliadeS2.root, run171_1_eliadeS2.root, etc.
    pattern = f"run{run_number}_*_eliadeS{serverID}.root"
    
    # Find all matching files
    files = glob.glob(pattern)
    files.sort()  # Sort to ensure consistent ordering
    
    print(f"Found {len(files)} files for run {run_number}")
    
    results = {}
    
    print(files)
    
    for filepath in files:
        print(f"Processing {filepath}...")
        
        # Extract filename without .root extension
        filename_no_ext = os.path.splitext(os.path.basename(filepath))[0]
        
        # Process the file
        print('>>> ready to go to process_single_file')
        duration = process_single_file(filepath)
        print('>>> out of process_single_file')
        
        if duration is not None:
            results[filename_no_ext] = duration
            print(f"  Duration: {duration} picoseconds ({duration:.3f} seconds)")
        else:
            print(f"  Failed to process")
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Extract timing information from multiple ROOT files')
    parser.add_argument('serverID', type=int, help='Server Number)')
    parser.add_argument('run_number', type=int, help='Run number to process (e.g., 171)')
#    parser.add_argument('--output', '-o', default='run_durations.json', help='Output JSON filename')

    
    args = parser.parse_args()
    runID = args.run_number
    serID = args.serverID
    
    print(f'Processing server {serID} run {runID}')
    
#    if 0< args.sereverID > 9:
    
    # Process all files for the run
    durations = bulk_process_runs(args.serverID, args.run_number)
    
    if not durations:
        print("No files processed successfully!")
        return
    
    # Create output structure
    output_data = {
        "run_durations_picoseconds": durations
    }
    
    # Write to JSON file
    
    foutput = f"duration_{args.run_number}_eliadeS{args.serverID}.json"
    
#    with open(args.output, 'w') as f:
    with open(foutput, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nResults written to {foutput}")
    print(f"Processed {len(durations)} files:")
    
    # Print summary
    total_duration_ps = sum(durations.values())
    total_duration_s = total_duration_ps 
    
    for filename, duration_ps in durations.items():
        duration_s = duration_ps
        print(f"  {filename}: {duration_ps} ps ({duration_s:.3f} s)")
    
    print(f"\nTotal recording time: {total_duration_ps} ps ({total_duration_s:.3f} s)")

if __name__ == "__main__":
    main()

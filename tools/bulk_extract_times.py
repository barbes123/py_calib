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
- 0, 1, etc. are volume numbers
- eliadeS2 indicates server

OUTPUT:
-------
- Console output showing processing progress and timing summaries
- JSON file containing all durations in picoseconds for further analysis
- Total recording time calculation across all processed files

USAGE EXAMPLES:
---------------
python3 /home/eliade/py_calib/tools/bulk_extract_times.py -s 7 -r 186 -vmin 97 -vmax 98 -t 1e15
Treshold is necessary because the density of events over time might vary between detectors/setups

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


def clean_largest_cluster(timestamps, threshold=1e10, min_cluster_size=10):
    """
    Keep only the largest cluster of timestamps with consecutive differences below a threshold.

    Args:
        timestamps (np.array): sorted array of timestamps.
        threshold (float): max allowed difference between consecutive timestamps.
        min_cluster_size (int): discard clusters smaller than this.

    Returns:
        np.array: cleaned timestamps from the largest valid cluster
    """
    if len(timestamps) < min_cluster_size:
        return timestamps

    diffs = np.diff(timestamps)
    split_indices = np.where(diffs > threshold)[0] + 1

    # Start and end indices of clusters
    cluster_bounds = np.split(timestamps, split_indices)

    # Filter by min cluster size and find the largest one
    valid_clusters = [cluster for cluster in cluster_bounds if len(cluster) >= min_cluster_size]
    if not valid_clusters:
        return np.array([])

    largest_cluster = max(valid_clusters, key=len)
    return largest_cluster


def process_single_file(filename, threshold=1e10):
    """Process a single ROOT file and return duration in picoseconds"""
    print(f"\n--- Processing file: {filename} ---")
    try:
        file = uproot.open(filename)
        tree = file["ELIADE_Tree"]
    except Exception as e:
        print(f"  ERROR: Cannot open tree in file: {filename}\n    Reason: {e}")
        return None

    try:
        fine_timestamps = np.array(tree["FineTS"].array())
        fine_timestamps = fine_timestamps[~np.isnan(fine_timestamps)]
        fine_timestamps = np.sort(fine_timestamps)

        fine_timestamps = clean_largest_cluster(fine_timestamps, threshold=threshold)

        print(f"  First 20 FineTS values (total {len(fine_timestamps)}):")
        print(f"   {fine_timestamps[:20]}")

        diffs_start = np.diff(fine_timestamps)
        print(f"  First 20 differences between consecutive FineTS values:")
        print(f"   {diffs_start[:20]}")

        print(f"  Last 20 FineTS values:")
        print(f"   {fine_timestamps[-20:]}")

        diffs_end = np.diff(fine_timestamps[-21:])
        print(f"  Last 20 differences between consecutive FineTS values:")
        print(f"   {diffs_end}")

    except Exception as e:
        print(f"  ERROR: Cannot extract FineTS from file: {filename}\n    Reason: {e}")
        return None

    try:
        if len(fine_timestamps) == 0:
            print(f"  WARNING: No FineTS data found in file: {filename}")
            return None

        duration_seconds = float(fine_timestamps.max() - fine_timestamps.min()) / 1e12
        print(f"  Duration: {duration_seconds:.6f} seconds ({duration_seconds*1e12:.0f} ps)")

        file.close()
        return duration_seconds

    except Exception as e:
        print(f"  ERROR: Failed to calculate duration for file: {filename}\n    Reason: {e}")
        return None


def bulk_process_runs(serverID, run_number, vol_min=0, vol_max=100, threshold=1e10):
    """Process all files for a given run number within volume limits"""
    pattern = f"run{run_number}_*_eliadeS{serverID}.root"
    files = glob.glob(pattern)
    files.sort()

    print(f"\nFound {len(files)} files matching pattern '{pattern}'")

    results = []

    for filepath in files:
        filename = os.path.basename(filepath)
        parts = filename.split('_')

        if len(parts) >= 2:
            try:
                volnbr = int(parts[1])
            except ValueError:
                print(f"  -> Skipping file with unrecognized volume: {filename}")
                continue

            if volnbr == 999 or not (vol_min <= volnbr <= vol_max):
                print(f"  -> Skipping volume {volnbr}: outside range {vol_min}-{vol_max}")
                continue
        else:
            print(f"  -> Skipping file with unexpected filename format: {filename}")
            continue

        duration = process_single_file(filepath, threshold=threshold)
        if duration is not None:
            results.append({
                "runnbr": run_number,
                "volnbr": volnbr,
                "server": serverID,
                "duration": duration
            })
            print(f"  -> Duration recorded: {duration:.2f} s")
        else:
            print(f"  -> Failed to process {filename}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Extract timing information from ROOT files for ELIADE DAQ system"
    )

    parser.add_argument(
        "-s", "--server",
        dest="server",
        default=2,
        type=int,
        choices=range(0, 10),
        help="DAQ ELIADE server number (0–9), default: 2"
    )

    parser.add_argument(
        "-r", "--run",
        dest="runnbr",
        default=162,
        type=int,
        help="Run number to process, default: 162"
    )

    parser.add_argument(
        "-vmin", "--volmin",
        dest="vol_min",
        default=0,
        type=int,
        help="Minimum volume number to process, default: 0"
    )

    parser.add_argument(
        "-vmax", "--volmax",
        dest="vol_max",
        default=900,
        type=int,
        help="Maximum volume number to process, default: 900"
    )

    parser.add_argument(
        "-t", "--threshold",
        dest="threshold",
        default=1e15,
        type=float,
        help="Max allowed difference between consecutive timestamps in clean_largest_cluster (default: 1e15)"
    )

    args = parser.parse_args()
    server_id = args.server
    run_id = args.runnbr
    vol_min = args.vol_min
    vol_max = args.vol_max
    threshold = args.threshold

    print(f"Processing run {run_id} on server S{server_id}, volumes {vol_min} to {vol_max}")
    print(f"Using threshold = {threshold}")

    durations = bulk_process_runs(server_id, run_id, vol_min, vol_max, threshold)

    if not durations:
        print("No files processed successfully!")
        return

    output_data = {
        "run_durations_seconds": durations
    }

    output_file = f"duration_{run_id}_eliadeS{server_id}.json"
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\nResults written to {output_file}")

    total_duration_s = sum(entry['duration'] for entry in durations)
    print(f"\nTotal recording time: {total_duration_s:.6f} seconds\n")


if __name__ == "__main__":
    main()

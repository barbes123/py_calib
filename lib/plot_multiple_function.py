import os
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import re
import numpy as np
import argparse

def find_dicts_with_domain(obj, target_domain):
    """Find all dictionaries that contain the                          col            ax.scatter(energy_x_sorted, energy_y_sorted, c=colors, alpha=0.7, s=50, zorder=5)
            ax.set_xlabel("Cumulative Time (s)")
            ax.set_ylabel("pos_ch/kev")
            
            # Format x-axis with scientific notation and reduce tick density
            ax.ticklabel_format(style='scientific', axis='x', scilimits=(0,0))
            ax.locator_params(axis='x', nbins=5)  # Limit to 5 ticks on x-axis
            
            # Only show detailed titles if show_annotations is True [isotope_color_map[isotope] for isotope indef _create_volume_subplots(domain, domain_x, domain_y, domain_isotopes, domain_energies, 
                           domain_filenames, domain_unique_energies, target_run, target_S, output_path, show_annotations=False):nergy_isotopes_sorted]
            
            ax.scatter(energy_x_sorted, energy_y_sorted, c=colors, alpha=0.7, s=50, zorder=5)
            ax.set_xlabel("Cumulative Time (s)")
            ax.set_ylabel("pos_ch/kev")
            
            # Format x-axis with scientific notation for large numbers
            ax.ticklabel_format(style='scientific', axis='x', scilimits=(0,0))
            
            # Only show detailed titles if show_annotations is True           colors = [isotope_color_map[isotope] for isotope in energy_isotopes_sorted]
            
            ax.scatter(energy_x_sorted, energy_y_sorted, c=colors, alpha=0.7, s=50, zorder=5)
            ax.set_xlabel("Cumulative Time (s)")
            ax.set_ylabel("pos_ch/kev")
            colors = [isotope_color_map[isotope] for isotope in energy_isotopes_sorted]
            
            ax.scatter(energy_x_sorted, energy_y_sorted, c=colors, alpha=0.7, s=50, zorder=5)
            ax.set_xlabel("Cumulative Time (s)")
            ax.set_ylabel("pos_ch/kev")  colors = [isotope_color_map[isotope] for isotope in energy_isotopes_sorted]
            
            ax.scatter(energy_x_sorted, energy_y_sorted, c=colors, alpha=0.7, s=50, zorder=5)
            ax.set_xlabel("Cumulative Time (s)")
            ax.set_ylabel("pos_ch/kev")t domain"""
    matches = []
    if isinstance(obj, dict):
        if obj.get("domain") == target_domain:
            matches.append(obj)
        for v in obj.values():
            matches.extend(find_dicts_with_domain(v, target_domain))
    elif isinstance(obj, list):
        for item in obj:
            matches.extend(find_dicts_with_domain(item, target_domain))
    return matches

def load_run_durations(parent_dir, durations_file):
    """Load run durations from new JSON format and convert to old-style dictionary (in picoseconds)"""
    durations_path = os.path.join(parent_dir, durations_file)
    if not os.path.exists(durations_path):
        raise FileNotFoundError(f"Error: {durations_file} not found in {parent_dir}")
    
    with open(durations_path, "r") as f:
        durations_data = json.load(f)

    if "run_durations_seconds" not in durations_data:
        raise KeyError("Missing 'run_durations_seconds' key in JSON file")

    duration_dict = {}
    for entry in durations_data["run_durations_seconds"]:
        try:
            runnbr = entry["runnbr"]
            volnbr = entry["volnbr"]
            server = entry["server"]
            duration_seconds = entry["duration"]

            # Convert seconds to picoseconds
            duration_ps = int(duration_seconds * 1e12)

            key = f"run{runnbr}_{volnbr}_eliadeS{server}"
            duration_dict[key] = duration_ps
        except KeyError as e:
            print(f"Skipping entry due to missing key: {e}")
    
    return duration_dict



def find_matching_folders(parent_dir, target_run, target_S, run_durations, vol_start=None, vol_end=None):
    """Find folders matching the pattern and with valid run durations, optionally filtered by volume range"""
    folder_pattern = re.compile(rf"selected_run_{target_run}_(\d+)_eliadeS{target_S}_calib")
    subfolders = []

    for d in sorted(os.listdir(parent_dir)):
        full_path = os.path.join(parent_dir, d)
        if os.path.isdir(full_path):
            match = folder_pattern.fullmatch(d)
            if match:
                index = int(match.group(1))
                
                # Apply volume range filter if specified
                if vol_start is not None and index < vol_start:
                    continue
                if vol_end is not None and index > vol_end:
                    continue
                
                run_key = f"run{target_run}_{index}_eliadeS{target_S}"
                if run_key in run_durations:
                    subfolders.append((d, index))
    
    return subfolders

def extract_data_from_folders(parent_dir, subfolders, target_run, target_S, domain_start, domain_end, run_durations, verbose=True):
    """Extract peak position data from matching folders"""
    all_x = []
    all_y = []
    all_isotopes = []
    all_energies = []
    all_filenames = []
    all_domains = []
    unique_isotopes = set()
    cumulative_time = 0

    for folder_name, index in subfolders:
        run_key = f"run{target_run}_{index}_eliadeS{target_S}"
        
        if run_key not in run_durations:
            if verbose:
                print(f"  Warning: No duration data found for {run_key}, skipping folder {folder_name}")
            continue
            
        duration = run_durations[run_key]
        cumulative_time += duration
        
        json_filename = f"selected_run_{target_run}_{index}_eliadeS{target_S}.json"
        json_path = os.path.join(parent_dir, folder_name, json_filename)
        
        if verbose:
            print(f"\nProcessing {folder_name}:")
            print(f"  Duration: {duration} ps (using key: {run_key})")
            print(f"  Cumulative time: {cumulative_time} ps")
            print(f"  JSON file: {json_filename}")
        
        if not os.path.exists(json_path):
            if verbose:
                print(f"  Warning: JSON file not found, skipping.")
            continue
        
        try:
            with open(json_path, "r") as f:
                detector_data = json.load(f)
            
            folder_pos_ch_count = 0
            for target_domain in range(domain_start, domain_end + 1):
                domain_dicts = find_dicts_with_domain(detector_data, target_domain)
                if domain_dicts and verbose:
                    print(f"  Found {len(domain_dicts)} domains matching {target_domain}")
                    
                for d in domain_dicts:
                    for key, value in d.items():
                        if key in ["domain", "serial", "detType", "PT", "pol_list"] or not isinstance(value, dict):
                            continue
                        
                        isotope = key
                        isotope_data = value
                        unique_isotopes.add(isotope)
                        
                        if verbose:
                            print(f"  Domain {target_domain} - {isotope} section found with keys: {list(isotope_data.keys())}")
                        
                        for energy_key, energy_data in isotope_data.items():
                            if energy_key != "0" and isinstance(energy_data, dict) and "pos_ch" in energy_data:
                                pos_ch = energy_data["pos_ch"]
                                all_x.append(cumulative_time)
                                all_y.append(pos_ch)
                                all_isotopes.append(isotope)
                                all_energies.append(energy_key)
                                all_domains.append(target_domain)
                                all_filenames.append(f"run_{target_run}_{index}")
                                folder_pos_ch_count += 1
                                
                                if verbose:
                                    print(f"    Domain {target_domain} - {isotope} Energy {energy_key}: pos_ch = {pos_ch} at cumulative time {cumulative_time}")
            
            if verbose:
                print(f"  Total pos_ch values extracted: {folder_pos_ch_count}")
            
        except Exception as e:
            if verbose:
                print(f"  Error reading JSON file: {e}")
            continue

    return {
        'x': all_x,
        'y': all_y,
        'isotopes': all_isotopes,
        'energies': all_energies,
        'filenames': all_filenames,
        'domains': all_domains,
        'unique_isotopes': unique_isotopes
    }

def create_plots_for_domain(domain, data, target_run, target_S, output_path, verbose=True, show_annotations=False):
    """Create plots for a specific domain"""
    # Filter data for this domain
    domain_indices = [i for i, d in enumerate(data['domains']) if d == domain]
    
    if not domain_indices:
        if verbose:
            print(f"  No data found for domain {domain}, skipping.")
        return False
    
    domain_x = [data['x'][i] for i in domain_indices]
    domain_y = [data['y'][i] for i in domain_indices]
    domain_isotopes = [data['isotopes'][i] for i in domain_indices]
    domain_energies = [data['energies'][i] for i in domain_indices]
    domain_filenames = [data['filenames'][i] for i in domain_indices]
    
    domain_unique_energies = sorted(set(domain_energies))
    if verbose:
        print(f"  Energies found for domain {domain}: {domain_unique_energies}")
    
    # Create subplot figure
    _create_energy_subplots(domain, domain_x, domain_y, domain_isotopes, domain_energies, 
                           domain_filenames, domain_unique_energies, target_run, target_S, output_path, show_annotations)
    
    # Create volume-based plots (x-axis = volumes instead of time)
    _create_volume_subplots(domain, domain_x, domain_y, domain_isotopes, domain_energies, 
                           domain_filenames, domain_unique_energies, target_run, target_S, output_path, show_annotations)
    
    # Create combined plot (disabled)
    # _create_combined_plot(domain, domain_x, domain_y, domain_isotopes, domain_energies, 
    #                      domain_filenames, domain_unique_energies, target_run, target_S, output_path, show_annotations)
    
    return True

def _create_energy_subplots(domain, domain_x, domain_y, domain_isotopes, domain_energies, 
                           domain_filenames, domain_unique_energies, target_run, target_S, output_path, show_annotations=False):
    """Create separate subplots for each energy"""
    n_plots = len(domain_unique_energies)
    if n_plots == 0:
        return
        
    cols = min(3, n_plots)
    rows = (n_plots + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 4*rows))
    
    if n_plots == 1:
        axes = [axes]
    elif rows == 1:
        axes = axes if n_plots > 1 else [axes]
    else:
        axes = axes.flatten()
    
    # Color map for isotopes
    domain_unique_isotopes = sorted(set(domain_isotopes))
    isotope_colors = plt.cm.Set1(np.linspace(0, 1, len(domain_unique_isotopes)))
    isotope_color_map = {isotope: color for isotope, color in zip(domain_unique_isotopes, isotope_colors)}
    
    for i, energy in enumerate(domain_unique_energies):
        ax = axes[i]
        
        # Filter and sort data for this energy
        energy_data = []
        for x, y, isotope, e, filename in zip(domain_x, domain_y, domain_isotopes, domain_energies, domain_filenames):
            if e == energy:
                energy_data.append((x, y, isotope, filename))
        
        energy_data.sort(key=lambda item: item[0])
        
        if energy_data:
            energy_x_sorted = [item[0] / 1e12 for item in energy_data]  # Convert to seconds
            energy_y_sorted = [item[1] for item in energy_data]
            energy_isotopes_sorted = [item[2] for item in energy_data]
            energy_filenames_sorted = [item[3] for item in energy_data]
            
            colors = [isotope_color_map[isotope] for isotope in energy_isotopes_sorted]
            
            ax.scatter(energy_x_sorted, energy_y_sorted, c=colors, alpha=0.7, s=50, zorder=5)
            ax.set_xlabel("Cumulative Time (s)")
            ax.set_ylabel("kev")
            
            # Format x-axis with scientific notation and reduce tick density
            ax.ticklabel_format(style='scientific', axis='x', scilimits=(0,0))
            ax.locator_params(axis='x', nbins=5)  # Limit to 5 ticks on x-axis
            
            # Only show detailed titles if show_annotations is True
            if show_annotations:
                ax.set_title(f"Energy {energy} keV\n({len(energy_y_sorted)} points)")
            else:
                ax.set_title(f"{energy} keV")
            
            ax.grid(True, alpha=0.3)
            
            # Only add annotations if show_annotations is True
            if show_annotations:
                for x, y, filename in zip(energy_x_sorted, energy_y_sorted, energy_filenames_sorted):
                    ax.annotate(filename, (x, y), xytext=(5, 5), textcoords='offset points', 
                               fontsize=8, alpha=0.7)
            
            if len(set(energy_isotopes_sorted)) > 1 and show_annotations:
                isotopes_str = ", ".join(set(energy_isotopes_sorted))
                ax.set_title(f"Energy {energy} keV\nIsotopes: {isotopes_str}\n({len(energy_y_sorted)} points)")
    
    # Hide empty subplots
    for i in range(n_plots, len(axes)):
        axes[i].set_visible(False)
    
    # Adjust main title based on show_annotations
    if show_annotations:
        fig.suptitle(f"Peak Positions vs Run Duration by Energy\n(domain {domain}, run {target_run}, S{target_S})", 
                     fontsize=14, y=0.95)
    else:
        fig.suptitle(f"Domain {domain} - Run {target_run} - S{target_S}", 
                     fontsize=14, y=0.95)
    
    if len(domain_unique_isotopes) > 1:
        legend_patches = [mpatches.Patch(color=color, label=isotope) 
                         for isotope, color in isotope_color_map.items()]
        fig.legend(handles=legend_patches, loc='upper right', bbox_to_anchor=(0.98, 0.92))
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.82, hspace=0.4)
    
    # Add suffix to filename if annotations are enabled
    suffix = "_ann" if show_annotations else ""
    subplot_filename = f"R{target_run}_S{target_S}_D{domain}_calib_over_time{suffix}.png"
    subplot_path = os.path.join(output_path, subplot_filename)
    plt.savefig(subplot_path, dpi=300, bbox_inches='tight')
    plt.close()

def _create_volume_subplots(domain, domain_x, domain_y, domain_isotopes, domain_energies, 
                           domain_filenames, domain_unique_energies, target_run, target_S, output_path, show_annotations=True):
    """Create separate subplots for each energy with volumes on x-axis"""
    n_plots = len(domain_unique_energies)
    if n_plots == 0:
        return
        
    cols = min(3, n_plots)
    rows = (n_plots + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 4*rows))
    
    if n_plots == 1:
        axes = [axes]
    elif rows == 1:
        axes = axes if n_plots > 1 else [axes]
    else:
        axes = axes.flatten()
    
    # Color map for isotopes
    domain_unique_isotopes = sorted(set(domain_isotopes))
    isotope_colors = plt.cm.Set1(np.linspace(0, 1, len(domain_unique_isotopes)))
    isotope_color_map = {isotope: color for isotope, color in zip(domain_unique_isotopes, isotope_colors)}
    
    # Create volume mapping for x-axis using actual volume numbers
    def extract_volume_number(filename):
        # Extract volume number from filename like "run_171_91" -> 91
        parts = filename.split('_')
        if len(parts) >= 3:
            return int(parts[2])
        return 0
    
    for i, energy in enumerate(domain_unique_energies):
        ax = axes[i]
        
        # Filter and sort data for this energy by actual volume number
        energy_data = []
        for x, y, isotope, e, filename in zip(domain_x, domain_y, domain_isotopes, domain_energies, domain_filenames):
            if e == energy:
                volume_number = extract_volume_number(filename)
                energy_data.append((volume_number, y, isotope, filename))
        
        energy_data.sort(key=lambda item: item[0])
        
        if energy_data:
            energy_x_volumes = [item[0] for item in energy_data]  # Actual volume numbers
            energy_y_sorted = [item[1] for item in energy_data]
            energy_isotopes_sorted = [item[2] for item in energy_data]
            energy_filenames_sorted = [item[3] for item in energy_data]
            
            colors = [isotope_color_map[isotope] for isotope in energy_isotopes_sorted]
            
            ax.scatter(energy_x_volumes, energy_y_sorted, c=colors, alpha=0.7, s=50, zorder=5)
            ax.set_xlabel("Volume Number")
            ax.set_ylabel("kev")
            
            # Only show detailed titles if show_annotations is True
            if show_annotations:
                ax.set_title(f"Energy {energy} keV\n({len(energy_y_sorted)} points)")
            else:
                ax.set_title(f"{energy} keV")
            
            ax.grid(True, alpha=0.3)
            
            # Only add annotations if show_annotations is True
            if show_annotations:
                for x, y, filename in zip(energy_x_volumes, energy_y_sorted, energy_filenames_sorted):
                    ax.annotate(str(x), (x, y), xytext=(5, 5), 
                               textcoords='offset points', fontsize=6, alpha=0.7)
            
            if len(set(energy_isotopes_sorted)) > 1 and show_annotations:
                isotopes_str = ", ".join(set(energy_isotopes_sorted))
                ax.set_title(f"Energy {energy} keV\nIsotopes: {isotopes_str}\n({len(energy_y_sorted)} points)")
    
    # Hide empty subplots
    for i in range(n_plots, len(axes)):
        axes[i].set_visible(False)
    
    # Adjust main title based on show_annotations
    if show_annotations:
        fig.suptitle(f"Peak Positions vs Volume\n(domain {domain}, run {target_run}, S{target_S})", 
                     fontsize=14, y=0.95)
    else:
        fig.suptitle(f"Domain {domain} - Run {target_run} - S{target_S} (by Volume)", 
                     fontsize=14, y=0.95)
    
    if len(domain_unique_isotopes) > 1:
        legend_patches = [mpatches.Patch(color=color, label=isotope) 
                         for isotope, color in isotope_color_map.items()]
        fig.legend(handles=legend_patches, loc='upper right', bbox_to_anchor=(0.98, 0.92))
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.82, hspace=0.4)
    
    # Add suffix to filename if annotations are enabled
    suffix = "_ann" if show_annotations else ""
    subplot_filename = f"R{target_run}_S{target_S}_D{domain}_calib_by_volume{suffix}.png"
    subplot_path = os.path.join(output_path, subplot_filename)
    plt.savefig(subplot_path, dpi=300, bbox_inches='tight')
    plt.close()

def _create_combined_plot(domain, domain_x, domain_y, domain_isotopes, domain_energies, 
                         domain_filenames, domain_unique_energies, target_run, target_S, output_path, show_annotations=False):
    """Create combined plot for all energies in a domain"""
    plt.figure(figsize=(12, 8))
    
    domain_unique_combinations = list(set(zip(domain_isotopes, domain_energies)))
    colors = plt.cm.tab10(np.linspace(0, 1, len(domain_unique_combinations)))
    color_map = {combo: color for combo, color in zip(domain_unique_combinations, colors)}
    
    for energy in domain_unique_energies:
        energy_data = []
        for x, y, isotope, e, filename in zip(domain_x, domain_y, domain_isotopes, domain_energies, domain_filenames):
            if e == energy:
                energy_data.append((x, y, isotope, e, filename))
        
        energy_data.sort(key=lambda item: item[0])
        
        if energy_data:
            energy_x = [item[0] / 1e12 for item in energy_data]  # Convert to seconds
            energy_y = [item[1] for item in energy_data]
            energy_isotopes = [item[2] for item in energy_data]
            
            line_color = color_map[(energy_isotopes[0], energy)]
            plt.scatter(energy_x, energy_y, color=line_color, alpha=0.7, s=50, 
                       label=f"{energy_isotopes[0]} {energy} keV")
    
    point_colors = [color_map[(isotope, energy)] for isotope, energy in zip(domain_isotopes, domain_energies)]
    domain_x_seconds = [x / 1e12 for x in domain_x]  # Convert to seconds
    plt.scatter(domain_x_seconds, domain_y, c=point_colors, alpha=0.7, s=50, zorder=5)
    
    # Only add annotations if show_annotations is True
    if show_annotations:
        for x, y, filename in zip(domain_x_seconds, domain_y, domain_filenames):
            plt.annotate(filename, (x, y), xytext=(5, 5), textcoords='offset points', 
                        fontsize=8, alpha=0.7)
    
    plt.xlabel("Cumulative Time (seconds)")
    plt.ylabel("kev")
    
    # Format x-axis with scientific notation and reduce tick density
    plt.ticklabel_format(style='scientific', axis='x', scilimits=(0,0))
    plt.locator_params(axis='x', nbins=5)  # Limit to 5 ticks on x-axis
    
    # Adjust title based on show_annotations
    if show_annotations:
        plt.title(f"All Peak Positions vs Cumulative Time\n(domain {domain}, run {target_run}, S{target_S})")
    else:
        plt.title(f"Domain {domain} - Run {target_run} - S{target_S}")
    
    plt.grid(True, alpha=0.3)
    
    legend_patches = [mpatches.Patch(color=color, label=f"{isotope} {energy} keV")
                     for (isotope, energy), color in color_map.items()]
    plt.legend(handles=legend_patches, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    # Add suffix to filename if annotations are enabled
    suffix = "_ann" if show_annotations else ""
    combined_filename = f"R{target_run}_S{target_S}_D{domain}_calib_over_time_combined{suffix}.png"
    combined_path = os.path.join(output_path, combined_filename)
    plt.savefig(combined_path, dpi=300, bbox_inches='tight')
    plt.close()

def plot_peak_positions_vs_time(target_run, domain_start, domain_end, target_S, 
                               parent_dir=None, durations_file="run_durations.json", 
                               vol_start=None, vol_end=None,
                               verbose=True, create_plots=True, show_annotations=False):
    """
    Main function to plot peak positions vs cumulative time for detector calibration data.
    Also saves the extracted data to a JSON file for further analysis.
    
    Args:
        target_run (int): Target run number (e.g., 171)
        domain_start (int): Starting domain number (e.g., 109)
        domain_end (int): Ending domain number (e.g., 115)
        target_S (int): Target S number (e.g., 2)
        parent_dir (str, optional): Parent directory path. Defaults to current working directory.
        durations_file (str): Name of the durations JSON file
        vol_start (int, optional): Starting volume number to filter data
        vol_end (int, optional): Ending volume number to filter data
        verbose (bool): Whether to print progress information
        create_plots (bool): Whether to create and save plots
        show_annotations (bool): Whether to show text annotations next to data points
    
    Returns:
        dict: Dictionary containing extracted data and metadata, including:
            - 'x', 'y': lists of time and position data
            - 'isotopes', 'energies', 'filenames', 'domains': corresponding metadata
            - 'unique_isotopes': set of unique isotopes found
            - 'output_path': path where plots/data are saved
            - 'json_output_path': path to the saved JSON data file
    """
    if parent_dir is None:
        parent_dir = os.getcwd()
    
    if verbose:
        print(f"Looking for domains {domain_start}-{domain_end} in run {target_run} S{target_S}")
        print(f"Working directory: {parent_dir}")
    
    # Construct the duration file name based on run and S
    durations_file = f"duration_{target_run}_eliadeS{target_S}.json"

    try:
        run_durations = load_run_durations(parent_dir, durations_file)
        if verbose:
            print(f"Loaded {len(run_durations)} run durations from {durations_file}")
    except FileNotFoundError as e:
        print(str(e))
        return None
    
    # Find matching folders
    subfolders = find_matching_folders(parent_dir, target_run, target_S, run_durations, vol_start, vol_end)
    if verbose:
        print(f"Found {len(subfolders)} matching folders")
        for folder_name, index in subfolders:
            run_key = f"run{target_run}_{index}_eliadeS{target_S}"
            print(f"Found matching folder: {folder_name} -> {run_key}")
    
    if not subfolders:
        if verbose:
            print("No matching folders found. Check your folder names and target parameters.")
        return None
    
    # Extract data
    data = extract_data_from_folders(parent_dir, subfolders, target_run, target_S, 
                                   domain_start, domain_end, run_durations, verbose)
    
    if verbose:
        print(f"\n=== FINAL RESULTS ===")
        print(f"Total data points: {len(data['y'])}")
        print(f"Domains processed: {domain_start}-{domain_end}")
        print(f"Isotopes found: {sorted(data['unique_isotopes'])}")
    
    if not data['y']:
        if verbose:
            print(f"No pos_ch values found for domains {domain_start}-{domain_end} in run {target_run} S{target_S}.")
        return data
    
    # Create output folder (needed for both plots and JSON)
    output_folder = f"compare_shift_run_{target_run}_domains_{domain_start}-{domain_end}_S{target_S}"
    output_path = os.path.join(parent_dir, output_folder)
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        if verbose:
            print(f"\nCreated output folder: {output_path}")
    else:
        if verbose:
            print(f"\nUsing existing output folder: {output_path}")

    plots_created = 0
    if create_plots:
        # Create plots for each domain
        unique_domains = sorted(set(data['domains']))
        if verbose:
            print(f"\nCreating separate plots for domains: {unique_domains}")
        
        for domain in unique_domains:
            if verbose:
                print(f"\nProcessing plots for domain {domain}...")
            
            if create_plots_for_domain(domain, data, target_run, target_S, output_path, verbose, show_annotations):
                plots_created += 1
        
        if verbose:
            print(f"\nAll plots saved in: {output_path}")
            print(f"Created plots for {plots_created} domains")
    
    data['output_path'] = output_path
    data['plots_created'] = plots_created
    
    # Save extracted data to JSON file (always save, regardless of create_plots)
    json_output_filename = f"R{target_run}_S{target_S}_D{domain_start}-{domain_end}_data.json"
    json_output_path = os.path.join(output_path, json_output_filename)
    
    # Organize data by domain first, then by volume
    # Structure: domain -> volume -> [TS, true_energy1, analyzed_energy1, true_energy2, analyzed_energy2, ...]
    organized_data = {}
    for i in range(len(data['x'])):
        volume = data['filenames'][i]
        domain = data['domains'][i]
        time_seconds = round(data['x'][i] / 1e12, 2)
        true_energy = float(data['energies'][i]) if str(data['energies'][i]).replace('.', '', 1).isdigit() else data['energies'][i]
        analyzed_energy = data['y'][i]  # pos_ch value
        
        # Create domain group if it doesn't exist
        if domain not in organized_data:
            organized_data[domain] = {}
        
        # Create volume within domain if it doesn't exist
        if volume not in organized_data[domain]:
            organized_data[domain][volume] = [time_seconds]
        
        # Append true energy followed by analyzed energy
        organized_data[domain][volume].extend([true_energy, analyzed_energy])
    
    # Prepare new efficient JSON data
    json_data = {
        'metadata': {
            'target_run': target_run,
            'domain_start': domain_start,
            'domain_end': domain_end,
            'target_S': target_S,
            'total_data_points': len(data['y']),
            'unique_domains': sorted(list(organized_data.keys())),
            'plots_created': plots_created,
            'time_unit': 'seconds (cumulative time, truncated to 2 decimals)',
            'data_format': 'Each volume array: [time_seconds, true_energy1, analyzed_energy1, true_energy2, analyzed_energy2, ...]',
            'data_explanation': {
                'time_seconds': 'Cumulative time in seconds (first element of each array)',
                'true_energy': 'Original/reference energy value in keV (odd-indexed elements after time)',
                'analyzed_energy': 'Measured position channel value - pos_ch (even-indexed elements after time)'
            }
        },
        'domains': organized_data
    }
    
    try:
        with open(json_output_path, 'w') as json_file:
            # Custom formatting: compact arrays, readable structure
            json_str = json.dumps(json_data, indent=4, separators=(',', ': '))
            # Replace multi-line arrays with single-line arrays
            import re
            json_str = re.sub(r'\[\s*\n\s*([\d\.,\s\n]*?)\s*\n\s*\]', 
                            lambda m: '[' + re.sub(r'\s*\n\s*', ', ', m.group(1)).strip() + ']', 
                            json_str)
            json_file.write(json_str)
        
        if verbose:
            print(f"Saved extracted data to: {json_output_path}")
        
        data['json_output_path'] = json_output_path
        
    except Exception as e:
        if verbose:
            print(f"Error saving JSON data: {e}")
        data['json_output_path'] = None
    
    return data

def main():
    """Main function for command line execution"""
    parser = argparse.ArgumentParser(description='Plot peak positions vs cumulative time for detector calibration data')
    parser.add_argument('target_run', type=int, help='Target run number (e.g., 171)')
    parser.add_argument('domain_start', type=int, help='Starting domain number (e.g., 109)')
    parser.add_argument('domain_end', type=int, help='Ending domain number (e.g., 115)')
    parser.add_argument('target_S', type=int, help='Target S number (e.g., 2)')
    parser.add_argument('--parent_dir', type=str, help='Parent directory path (default: current directory)')
    parser.add_argument('--vol_start', type=int, help='Starting volume number to filter data')
    parser.add_argument('--vol_end', type=int, help='Ending volume number to filter data')
    parser.add_argument('--no_plots', action='store_true', help='Skip creating plots')
    parser.add_argument('--annotations', action='store_true', help='Enable text annotations on data points')
    parser.add_argument('--quiet', action='store_true', help='Suppress verbose output')
    
    args = parser.parse_args()
    
    result = plot_peak_positions_vs_time(
        target_run=args.target_run,
        domain_start=args.domain_start,
        domain_end=args.domain_end,
        target_S=args.target_S,
        parent_dir=args.parent_dir,
        vol_start=args.vol_start,
        vol_end=args.vol_end,
        verbose=not args.quiet,
        create_plots=not args.no_plots,
        show_annotations=args.annotations
    )
    
    if result is None:
        exit(1)

if __name__ == "__main__":
    main()
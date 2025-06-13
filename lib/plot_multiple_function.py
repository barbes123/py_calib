import os
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import re
import numpy as np
import argparse

def find_dicts_with_domain(obj, target_domain):
    """Find all dictionaries that contain the target domain"""
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

def load_run_durations(parent_dir, durations_file="run_durations.json"):
    """Load run durations from JSON file"""
    durations_path = os.path.join(parent_dir, durations_file)
    if not os.path.exists(durations_path):
        raise FileNotFoundError(f"Error: {durations_file} not found in {parent_dir}")
    
    with open(durations_path, "r") as f:
        durations_data = json.load(f)
    
    return durations_data["run_durations_picoseconds"]

def find_matching_folders(parent_dir, target_run, target_S, run_durations):
    """Find folders matching the pattern and with valid run durations"""
    folder_pattern = re.compile(rf"selected_run_{target_run}_(\d+)_eliadeS{target_S}_calib")
    subfolders = []

    for d in sorted(os.listdir(parent_dir)):
        full_path = os.path.join(parent_dir, d)
        if os.path.isdir(full_path):
            match = folder_pattern.fullmatch(d)
            if match:
                index = int(match.group(1))
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

def create_plots_for_domain(domain, data, target_run, target_S, output_path, verbose=True):
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
                           domain_filenames, domain_unique_energies, target_run, target_S, output_path)
    
    # Create combined plot
    _create_combined_plot(domain, domain_x, domain_y, domain_isotopes, domain_energies, 
                         domain_filenames, domain_unique_energies, target_run, target_S, output_path)
    
    return True

def _create_energy_subplots(domain, domain_x, domain_y, domain_isotopes, domain_energies, 
                           domain_filenames, domain_unique_energies, target_run, target_S, output_path):
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
            energy_x_sorted = [item[0] for item in energy_data]
            energy_y_sorted = [item[1] for item in energy_data]
            energy_isotopes_sorted = [item[2] for item in energy_data]
            energy_filenames_sorted = [item[3] for item in energy_data]
            
            colors = [isotope_color_map[isotope] for isotope in energy_isotopes_sorted]
            
            ax.plot(energy_x_sorted, energy_y_sorted, 'o-', alpha=0.7, linewidth=2, markersize=8)
            ax.scatter(energy_x_sorted, energy_y_sorted, c=colors, alpha=0.7, s=50, zorder=5)
            ax.set_xlabel("Cumulative Time (ps)")
            ax.set_ylabel("pos_ch/kev")
            ax.set_title(f"Energy {energy} keV\n({len(energy_y_sorted)} points)")
            ax.grid(True, alpha=0.3)
            
            for x, y, filename in zip(energy_x_sorted, energy_y_sorted, energy_filenames_sorted):
                ax.annotate(filename, (x, y), xytext=(5, 5), textcoords='offset points', 
                           fontsize=8, alpha=0.7)
            
            if len(set(energy_isotopes_sorted)) > 1:
                isotopes_str = ", ".join(set(energy_isotopes_sorted))
                ax.set_title(f"Energy {energy} keV\nIsotopes: {isotopes_str}\n({len(energy_y_sorted)} points)")
    
    # Hide empty subplots
    for i in range(n_plots, len(axes)):
        axes[i].set_visible(False)
    
    fig.suptitle(f"Peak Positions vs Run Duration by Energy\n(domain {domain}, run {target_run}, S{target_S})", 
                 fontsize=14, y=0.98)
    
    if len(domain_unique_isotopes) > 1:
        legend_patches = [mpatches.Patch(color=color, label=isotope) 
                         for isotope, color in isotope_color_map.items()]
        fig.legend(handles=legend_patches, loc='upper right', bbox_to_anchor=(0.98, 0.95))
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.90)
    
    subplot_filename = f"energy_subplots_run_{target_run}_domain_{domain}_S{target_S}.png"
    subplot_path = os.path.join(output_path, subplot_filename)
    plt.savefig(subplot_path, dpi=300, bbox_inches='tight')
    plt.close()

def _create_combined_plot(domain, domain_x, domain_y, domain_isotopes, domain_energies, 
                         domain_filenames, domain_unique_energies, target_run, target_S, output_path):
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
            energy_x = [item[0] for item in energy_data]
            energy_y = [item[1] for item in energy_data]
            energy_isotopes = [item[2] for item in energy_data]
            
            line_color = color_map[(energy_isotopes[0], energy)]
            plt.plot(energy_x, energy_y, 'o-', color=line_color, alpha=0.7, linewidth=2, 
                    markersize=8, label=f"{energy_isotopes[0]} {energy} keV")
    
    point_colors = [color_map[(isotope, energy)] for isotope, energy in zip(domain_isotopes, domain_energies)]
    plt.scatter(domain_x, domain_y, c=point_colors, alpha=0.7, s=50, zorder=5)
    
    for x, y, filename in zip(domain_x, domain_y, domain_filenames):
        plt.annotate(filename, (x, y), xytext=(5, 5), textcoords='offset points', 
                    fontsize=8, alpha=0.7)
    
    plt.xlabel("Cumulative Time (picoseconds)")
    plt.ylabel("pos_ch/kev")
    plt.title(f"All Peak Positions vs Cumulative Time\n(domain {domain}, run {target_run}, S{target_S})")
    plt.grid(True, alpha=0.3)
    
    legend_patches = [mpatches.Patch(color=color, label=f"{isotope} {energy} keV")
                     for (isotope, energy), color in color_map.items()]
    plt.legend(handles=legend_patches, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    combined_filename = f"combined_plot_run_{target_run}_domain_{domain}_S{target_S}.png"
    combined_path = os.path.join(output_path, combined_filename)
    plt.savefig(combined_path, dpi=300, bbox_inches='tight')
    plt.close()

def plot_peak_positions_vs_time(target_run, domain_start, domain_end, target_S, 
                               parent_dir=None, durations_file="run_durations.json", 
                               verbose=True, create_plots=True):
    """
    Main function to plot peak positions vs cumulative time for detector calibration data.
    
    Args:
        target_run (int): Target run number (e.g., 171)
        domain_start (int): Starting domain number (e.g., 109)
        domain_end (int): Ending domain number (e.g., 115)
        target_S (int): Target S number (e.g., 2)
        parent_dir (str, optional): Parent directory path. Defaults to current working directory.
        durations_file (str): Name of the durations JSON file
        verbose (bool): Whether to print progress information
        create_plots (bool): Whether to create and save plots
    
    Returns:
        dict: Dictionary containing extracted data and metadata
    """
    if parent_dir is None:
        parent_dir = os.getcwd()
    
    if verbose:
        print(f"Looking for domains {domain_start}-{domain_end} in run {target_run} S{target_S}")
        print(f"Working directory: {parent_dir}")
    
    # Load run durations
    try:
        run_durations = load_run_durations(parent_dir, durations_file)
        if verbose:
            print(f"Loaded {len(run_durations)} run durations")
    except FileNotFoundError as e:
        print(str(e))
        return None
    
    # Find matching folders
    subfolders = find_matching_folders(parent_dir, target_run, target_S, run_durations)
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
    
    if create_plots:
        # Create output folder
        output_folder = f"compare_shift_run_{target_run}_domains_{domain_start}-{domain_end}_S{target_S}"
        output_path = os.path.join(parent_dir, output_folder)
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            if verbose:
                print(f"\nCreated output folder: {output_path}")
        else:
            if verbose:
                print(f"\nUsing existing output folder: {output_path}")
        
        # Create plots for each domain
        unique_domains = sorted(set(data['domains']))
        if verbose:
            print(f"\nCreating separate plots for domains: {unique_domains}")
        
        plots_created = 0
        for domain in unique_domains:
            if verbose:
                print(f"\nProcessing plots for domain {domain}...")
            
            if create_plots_for_domain(domain, data, target_run, target_S, output_path, verbose):
                plots_created += 1
        
        if verbose:
            print(f"\nAll plots saved in: {output_path}")
            print(f"Created plots for {plots_created} domains")
        
        data['output_path'] = output_path
        data['plots_created'] = plots_created
    
    return data

def main():
    """Main function for command line execution"""
    parser = argparse.ArgumentParser(description='Plot peak positions vs cumulative time for detector calibration data')
    parser.add_argument('target_run', type=int, help='Target run number (e.g., 171)')
    parser.add_argument('domain_start', type=int, help='Starting domain number (e.g., 109)')
    parser.add_argument('domain_end', type=int, help='Ending domain number (e.g., 115)')
    parser.add_argument('target_S', type=int, help='Target S number (e.g., 2)')
    parser.add_argument('--parent_dir', type=str, help='Parent directory path (default: current directory)')
    parser.add_argument('--durations_file', type=str, default="run_durations.json", help='Durations file name')
    parser.add_argument('--no_plots', action='store_true', help='Skip creating plots')
    parser.add_argument('--quiet', action='store_true', help='Suppress verbose output')
    
    args = parser.parse_args()
    
    result = plot_peak_positions_vs_time(
        target_run=args.target_run,
        domain_start=args.domain_start,
        domain_end=args.domain_end,
        target_S=args.target_S,
        parent_dir=args.parent_dir,
        durations_file=args.durations_file,
        verbose=not args.quiet,
        create_plots=not args.no_plots
    )
    
    if result is None:
        exit(1)

if __name__ == "__main__":
    main()
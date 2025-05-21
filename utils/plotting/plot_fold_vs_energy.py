#! /usr/bin/python3
import json, sys
import matplotlib.pyplot as plt
import numpy as np
from colorama import Fore, Back, Style
from math import sqrt as sqrt
from uncertainties import ufloat  # For error propagation

# clover = 29
server = 1
exclude_energies = {160.609, 511.006, 1460.820}

clover =  None

if len(sys.argv) > 1:
    clover = sys.argv[1]
    print("cloverID:", clover)
else:
    print("No CloverID provided, default None")
    clover = None

# print('-------------------------------------------------------------------------------------------------------------')
# print('I will plot on efficiency for fold: 1-4 from data in merged.json (all sources and gamma-rays presented)')
# print('Define in the code server, clover (for labels) and energies to be excluded')
# print('-------------------------------------------------------------------------------------------------------------')

from colorama import Fore, Back, Style

# Print beautiful header
print('\n')
print(Fore.YELLOW + '╔' + '═'*78 + '╗')
print(Fore.YELLOW + '║' + Fore.CYAN + ' EFFICIENCY CALIBRATION ANALYSIS '.center(78) + Fore.YELLOW + '║')
print(Fore.YELLOW + '╠' + '═'*78 + '╣')
print(Fore.YELLOW + '║' + Fore.WHITE + f' • Will process fold: {Fore.GREEN}1-4{Fore.WHITE} from {Fore.GREEN}merged.json{Fore.WHITE}'.ljust(98) + Fore.YELLOW + '║')
print(Fore.YELLOW + '║' + Fore.WHITE + f' • Includes all sources and gamma-rays present in data'.ljust(78) + Fore.YELLOW + '║')
print(Fore.YELLOW + '║' + Fore.WHITE + f' • Current Clover{Fore.GREEN} {clover} {Fore.WHITE} Server {Fore.GREEN}{server}{Fore.WHITE} and excluded energies below'.ljust(98) + Fore.YELLOW + '║')
print(Fore.YELLOW + '║' + Fore.WHITE + f' • Current Clover{Fore.GREEN} {exclude_energies}'.ljust(83) + Fore.YELLOW + '║')

print(Fore.YELLOW + '╚' + '═'*78 + '╝' + Style.RESET_ALL)
print('\n')



def load_json_data(filepath):
    """Load JSON data from file with error handling"""
    try:
        with open(filepath, 'r') as fin:
            return json.load(fin)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in file: {e}")
        return None
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return None

# Your provided JSON data
data = load_json_data('merged.json')
if data is None:
    exit()

# # Initialize dictionaries to hold energy and efficiency values for each fold
# folds = {1: {'energy': [], 'eff': [], 'eff_err': []},
#          2: {'energy': [], 'eff': [], 'eff_err': []},
#          3: {'energy': [], 'eff': [], 'eff_err': []},
#          4: {'energy': [], 'eff': [], 'eff_err': []}}

fold_farea = {1: {'energy': [], 'farea': [], 'farea_err': []}, #farea - fraction from total area for the given peak
         2: {'energy': [], 'farea': [], 'farea_err': []},
         3: {'energy': [], 'farea': [], 'farea_err': []},
         4: {'energy': [], 'farea': [], 'farea_err': []}}

sum_of_fold_for_ener = {}

bad_peaks = {'411.111', '511.006', '1460.820'}

isotope_energy_fold_areas = {}

for entry in data:
    fold = entry["fold"]

    # Loop through all isotopes (e.g., "152Eu", "60Co", etc.)
    for isotope, energies in entry.items():
        if isotope in ["fold", "PT", "pol_list"]:
            continue  # Skip non-isotope keys

        for energy, details in energies.items():
            key = (isotope, energy)
            if key not in isotope_energy_fold_areas:
                isotope_energy_fold_areas[key] = {}
            isotope_energy_fold_areas[key][fold] = details["area"]

# Step 2: Calculate new areas
new_structure = []

for (isotope, energy), fold_areas in isotope_energy_fold_areas.items():
    new_areas = {"isotope": isotope, "energy": energy}

    # Calculate new_area for each fold
    for fold in sorted(fold_areas.keys()):
        if fold == 1:
            new_areas[f"new_area_fold{fold}"] = fold_areas[fold]
        else:
            prev_fold = fold - 1
            if prev_fold in fold_areas:
                new_areas[f"new_area_fold{fold}"] = fold_areas[fold] - fold_areas[prev_fold]
                if new_areas[f"new_area_fold{fold}"] < 0:
                    new_areas[f"new_area_fold{fold}"] = 0
            else:
                new_areas[f"new_area_fold{fold}"] = fold_areas[fold]  # if previous fold missing

    new_structure.append(new_areas)

# Print or save as JSON
print(json.dumps(new_structure, indent=2))

# =============================================
# STEP 3: Normalize by area_fold4
# =============================================
# First, find area_fold4 for each (isotope, energy)
area_fold4_lookup = {}
for entry in data:
    if entry["fold"] == 4:  # Only process fold 4
        for isotope, energies in entry.items():
            if isotope in ["fold", "PT", "pol_list"]:
                continue
            for energy, details in energies.items():
                area_fold4_lookup[(isotope, energy)] = details["area"]



normalized_structure = []
for entry in new_structure:
    isotope = entry["isotope"]
    energy = entry["energy"]
    normalized_entry = {"isotope": isotope, "energy": energy}

    # Get area_fold4 (default to 1.0 if missing)
    area_fold4 = area_fold4_lookup.get((isotope, energy), ufloat(1.0, 0.0))

    # Normalize each new_area_foldN
    for key, value in entry.items():
        if key.startswith("new_area_fold"):
            fold = int(key.split("_")[-1][4:])  # Extract fold number
            if area_fold4 != 0:
                norm_value = value / area_fold4
                if value != 0:
                    norm_value_err = 1/sqrt(value) + 1 /sqrt(area_fold4)
                else:
                    norm_value_err = 1 /sqrt(area_fold4)

                normalized_entry[f"norm_{key}"] = [
                norm_value,  # Value
                norm_value_err        # Error
                ]
            else:
                normalized_entry[f"norm_{key}"] = [0.0, 0.0]  # Avoid division by zero


    normalized_structure.append(normalized_entry)
    print(normalized_entry)


    # Group data by fold
colors = {1: '#1f77b4', 2: '#ff7f0e', 3: '#2ca02c', 4: '#d62728'}  # Colorblind-friendly
markers = {1: 'o', 2: 's', 3: '^', 4: 'D'}
alpha = 0.8
capsize = 3
fold_data = {fold: {'x': [], 'y': [], 'yerr': []} for fold in range(1, 5)}

for entry in normalized_structure:
    if entry['energy'] in bad_peaks:
        continue
    if entry['isotope'] == '133Ba':
        continue

    energy = float(entry["energy"])

    for fold in range(1, 5):
        key = f"norm_new_area_fold{fold}"
        if key in entry:
            fold_data[fold]['x'].append(energy)
            fold_data[fold]['y'].append(entry[key][0])  # Value
            fold_data[fold]['yerr'].append(entry[key][1])  # Error

# Plot each fold
for fold, data in fold_data.items():
    if data['x']:  # Only plot if data exists
        plt.errorbar(
            x=data['x'],
            y=data['y'],
            yerr=data['yerr'],
            fmt=markers[fold],
            color=colors[fold],
            label=f'Fold {fold}',
            alpha=alpha,
            capsize=capsize,
            linestyle='',
            markersize=6
        )

# Format plot
plt.xlabel('Energy (keV)', fontsize=12)
plt.ylabel('% of the total events', fontsize=12)
plt.title(f'Clover {clover}', fontsize=14)
# plt.title('Normalized Gamma-Ray Areas with Error Bars', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.3)
# plt.xticks(rotation=45)

# Custom legend
handles, labels = plt.gca().get_legend_handles_labels()
if handles:  # Only show legend if there's data
    plt.legend(
        handles,
        labels,
        frameon=True,
        framealpha=0.9,
        edgecolor='black'
    )

plt.tight_layout()

# Save high-quality figure
plt.savefig(
    f'normalized_areas_with_errors_Clover{clover}.png',
    dpi=300,
    bbox_inches='tight',
    transparent=False
)
plt.show()


exit()
# Output final normalized structure
# print(json.dumps(normalized_structure, indent=2))


# =============================================
# STEP 3: Plotting
# =============================================
plt.figure(figsize=(12, 6))

# Color map for folds
colors = {1: 'blue', 2: 'green', 3: 'red', 4: 'purple'}

# Prepare data for plotting
plot_data = {}
for entry in normalized_structure:
    print('entry',entry)
    energy = float(entry["energy"])
    for fold in range(1, 5):
        key = f"norm_new_area_fold{fold}"
        print('entry',entry)
        print(key)
        if key in entry:
            if fold not in plot_data:
                plot_data[fold] = {'x': [], 'y': []}
            plot_data[fold]['x'].append(energy)
            plot_data[fold]['y'].append(entry[key])

print(plot_data)
# Plot each fold
for fold, values in plot_data.items():
    plt.scatter(values['x'], values['y'],
                color=colors[fold],
                label=f'Fold {fold}',
                alpha=0.7)

plt.xlabel('Energy (keV)', fontsize=12)
plt.ylabel('% of total events', fontsize=12)
plt.title('Normalized Area vs Energy by Fold', fontsize=14)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
# plt.xticks(rotation=45)
plt.tight_layout()

# Save and show plot
plt.savefig(f'normalized_areas_Clover{clover}.png', dpi=300)
plt.show()


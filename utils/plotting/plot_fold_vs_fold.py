import json
import matplotlib.pyplot as plt
import numpy as np

clover = 30
server = 2

exclude_energies = {79.623, 160.609, 511.006, 1460.820}

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

# Initialize dictionaries to hold energy and efficiency values for each fold
folds = {1: {'energy': [], 'eff': [], 'eff_err': []},
         2: {'energy': [], 'eff': [], 'eff_err': []},
         3: {'energy': [], 'eff': [], 'eff_err': []},
         4: {'energy': [], 'eff': [], 'eff_err': []}}

# Extract data for each fold
for fold_data in data:
    fold_num = fold_data['fold']
    for isotope, peaks in fold_data.items():
        if isotope == 'fold':
            continue
        for energy_str, peak_info in peaks.items():
            if 'eff' in peak_info:
                energy = float(energy_str)
                if energy in exclude_energies:
                    continue  # Skip excluded energies
                eff, eff_err = peak_info['eff']
                folds[fold_num]['energy'].append(energy)
                folds[fold_num]['eff'].append(eff)
                folds[fold_num]['eff_err'].append(eff_err)

# Create the plot
plt.figure(figsize=(10, 6))

# Plot each fold with different colors and markers
colors = ['b', 'g', 'c', 'r']
markers = ['o', 's', '^', 'D']

for fold_num in range(1, 5):
    fold = folds[fold_num]
    # Sort by energy for better plotting
    sorted_indices = np.argsort(fold['energy'])
    energy_sorted = np.array(fold['energy'])[sorted_indices]
    eff_sorted = np.array(fold['eff'])[sorted_indices]
    eff_err_sorted = np.array(fold['eff_err'])[sorted_indices]

    plt.errorbar(energy_sorted, eff_sorted, yerr=eff_err_sorted,
                 fmt=markers[fold_num-1], color=colors[fold_num-1],
                 label=f'Fold {fold_num}', capsize=3,
                 linestyle='none')  # No connecting lines

plt.xlim(50, 4000)  # Extended x-axis limits
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.xlabel('Energy (keV)', fontsize=12)
plt.ylabel('Efficiency', fontsize=12)
plt.title(f'Efficiency CL{clover}S{server}', fontsize=14)
plt.grid(True, which="both", ls="-", alpha=0.3)
plt.legend(fontsize=10)
plt.tight_layout()

plt.savefig(f'eff_fold_1_4_CL{clover}S{server}.png', dpi=300)


# Show the plot
plt.show()
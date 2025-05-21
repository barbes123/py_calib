#! /usr/bin/python3


import json, sys
import matplotlib.pyplot as plt
import numpy as np

cloverID = ''

if len(sys.argv) > 1:
    cloverID = sys.argv[1]
    print("cloverID:", cloverID)
else:
    print("No CloverID provided, default 29")
    cloverID = 29


# Load your JSON data
with open('merged.json') as f:
    data = json.load(f)

# Extract fold 1 and fold 4 data
fold1 = [item for item in data if item['fold'] == 1][0]
fold4 = [item for item in data if item['fold'] == 4][0]

# Prepare data for plotting
sources = []
energies = []
res_fold1 = []
res_fold4 = []
errors_fold1 = []
errors_fold4 = []

# Iterate through all sources in fold1
for source in fold1:
    if source == 'fold':
        continue
    source_data = fold1[source]
    for energy in source_data:
        if 'res' in source_data[energy]:
            sources.append(source)
            energies.append(float(energy)/1000)
            res_fold1.append(source_data[energy]['res'][0])
            errors_fold1.append(source_data[energy]['res'][1])

            # Get corresponding fold4 data
            if source in fold4 and energy in fold4[source] and 'res' in fold4[source][energy]:
                res_fold4.append(fold4[source][energy]['res'][0])
                errors_fold4.append(fold4[source][energy]['res'][1])
            else:
                res_fold4.append(np.nan)
                errors_fold4.append(np.nan)

# Create the plot
plt.figure(figsize=(12, 8))


print(min(energies))
norm = plt.Normalize(min(energies), max(energies))
cmap = plt.cm.viridis  # or any other like plasma, inferno, etc.
colors = cmap(norm(energies))


for x, y, errx, erry, c in zip(res_fold1, res_fold4, errors_fold1, errors_fold4, colors):
    plt.errorbar(x, y, yerr=erry, xerr=errx, fmt='o', color=c, alpha=0.8)

plt.xticks(fontsize=16)
plt.yticks(fontsize=16)

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])  # Only needed for colorbar
cbar = plt.colorbar(sm)
cbar.set_label('Energy, MeV', fontsize=16)
cbar.ax.tick_params(labelsize=16)

# Plot resolution vs energy for both folds
# plt.errorbar(res_fold1, res_fold4, yerr=errors_fold1, fmt='o', label='Fold 1', alpha=0.7)
# plt.errorbar(energies, res_fold1, yerr=errors_fold1, fmt='o', label='Fold 1', alpha=0.7)
# plt.errorbar(energies, res_fold4, yerr=errors_fold4, fmt='s', label='Fold 4', alpha=0.7)

# Add x = y line
min_val = min(min(res_fold1), min(res_fold4))
max_val = max(max(res_fold1), max(res_fold4))
# plt.plot([min_val, max_val], [min_val, max_val], 'k--')
plt.plot([2, max_val], [2, max_val], 'k--')

# Add labels and title
plt.xlabel('Fold 1, keV', fontsize=16)
plt.ylabel('Fold 4, keV', fontsize=16)
plt.title(f'Resolution, Clover {cloverID}', fontsize=16)
plt.grid(True, which='both', linestyle='--', alpha=0.5)
# plt.legend(fontsize=12)
plt.xlim(2,5)
plt.ylim(2,5)

# Add source annotations
# for i, src in enumerate(sources):
#     plt.annotate(src, (energies[i], max(res_fold1[i], res_fold4[i])),
#                  textcoords="offset points", xytext=(0,5), ha='center', fontsize=8)

plt.tight_layout()
plt.savefig(f'res_vs_res_Clover{cloverID}.png', dpi=300)
plt.show()

#! /usr/bin/python3

import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import json
import sys, os
from tabulate import tabulate
ourpath = os.getenv('PY_CALIB')
ourpath_default = '/data10/live/IT/py_calib'

# Check if path is set
if ourpath is None:
    print(f"PY_CALIB environment variable is not set. Using default: {ourpath_default}")
    ourpath = ourpath_default
    if not os.path.exists(ourpath):
        print(f"Error: Default path {ourpath} does not exist")
        sys.exit(1)
else:
    print(f"PY_CALIB is set to: {ourpath}")

# Add to Python path (platform-independent way)
lib_path = os.path.join(ourpath, 'lib')
if os.path.exists(lib_path):
    sys.path.append(lib_path)
else:
    print(f"Error: Library path {lib_path} does not exist")
    sys.exit(1)

from libFitFunctions import *

my_fits = ["Radware","Debertin","Fazekas","Kane","Gray"]
my_fits = ["Radware","Debertin","Fazekas","Kane"]

clover = 30
server = 2
fold = 4
exclude_energies = [79.623, 160.609, 511.006, 1460.820]

plt.figure(figsize=(10, 6))
energy_range = np.logspace(np.log10(50), np.log10(3700), 500)  # 50 to 4000 keV

# Main processing
all_folds = load_json_data('merged.json')
if all_folds is None:
    exit()

fold4_data = extract_fold_data(all_folds, fold)
if fold4_data is None:
    exit()

energies, efficiencies, errs = process_efficiency_data(fold4_data)
if energies is None:
    exit()

# Sort all data by energy
sort_idx = np.argsort(energies)
energies = energies[sort_idx]
efficiencies = efficiencies[sort_idx]
errs = errs[sort_idx]

# Create table of all data points (sorted)
print("\nComplete Efficiency Data (Sorted by Energy):")
print(tabulate([[e, eff, err] for e, eff, err in zip(energies, efficiencies, errs)],
               headers=["Energy (keV)", "Efficiency", "Error"],
               floatfmt=".3f"))

mask = ~np.isin(energies, exclude_energies)

# Print included points (sorted)
print("\nPoints included in fit (Sorted by Energy):")
print(tabulate([[e, eff, err] for e, eff, err, m in
                zip(energies, efficiencies, errs, mask) if m],
               headers=["Energy (keV)", "Efficiency", "Error"],
               floatfmt=".3f"))


#-----------------------------------------------------------------------------
#--------------------------------- Radware  Fit ------------------------------
#-----------------------------------------------------------------------------
if "Radware" in my_fits:
    p0_rw = [0.5, -0.2, 0.03, 0.5, -0.2, 0.03, 2.0]
    bounds_rw = ([0.1, -1, -1, 0.1, -1, -1, 0.1],
              [10, 1, 1, 10, 1, 1, 10])

    popt_radware =  RunFit(fitRadware, "Radware", energies, efficiencies, mask, p0_rw, errs,bounds_rw,10000)
    param_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

    if popt_radware is not None:
        plt.plot(energy_range, fitRadware(energy_range, *popt_radware),
             'r-', linewidth=2, label='Radware Fit')

        param_text_rw = "\n".join([f"{name} = {value:.4f}" for name, value in zip(param_names, popt_radware)])


    else:
        print(f"\n Fit Radware FAILED")

#-----------------------------------------------------------------------------
#--------------------------------- Debertin Fit ------------------------------
#-----------------------------------------------------------------------------
if "Debertin" in my_fits:
    # Better initial guesses (empirically tuned)
    p0_debertin = [0.1, -0.1, 0.01, 0.001, 0.0001]  # Adjust based on your data scale

    # Constrain parameters (prevent runaway negative terms)
    bounds_debertin = (
        [0, -np.inf, -np.inf, -np.inf, -np.inf],  # a1 ≥ 0 (dominant positive term)
        [np.inf, np.inf, np.inf, np.inf, np.inf]
    )
    # Find the index of the 223.116 keV point
    # idx_223 = np.where(np.isclose(energies, 223.116, atol=0.1))[0]  # Tolerance ±0.1 keV
    # if len(idx_223) == 0:
    #     raise ValueError("223.116 keV point not found in the data!")
    # Reduce the error for 223.116 keV (increase its weight)
    # modified_errs = errs.copy()
    # modified_errs[idx_223] *= 0.1  # 100x higher weight

    popt_debertin =  RunFit(fitDebertin, "Debertin", energies, efficiencies, mask, p0_debertin, errs,bounds_debertin)
    debertin_names = ['a1', 'a2', 'a3', 'a4', 'a5']
    param_text_debretin = "\n".join([f"{name} = {value:.4f}" for name, value in zip(debertin_names, popt_debertin)])


#-----------------------------------------------------------------------------
#--------------------------------- Fazekas Fit -------------------------------
#-----------------------------------------------------------------------------
if "Fazekas" in my_fits:

    log_eff = np.log(efficiencies[mask])
    log_E = np.log(energies[mask])

    # Fit a quadratic to estimate initial a1, a2, a3
    coeffs = np.polyfit(log_E, log_eff, 2)
    p0_fazekas = [
        coeffs[2], coeffs[1], coeffs[0],  # a1, a2, a3
        0, 0, 0, 0, 0, 0                   # Higher-order terms (start near zero)
    ]

    bounds_fazekas = (
        [-np.inf, -np.inf, -np.inf, -1e-2, -1e-3, -1e-4, -1e-5, -1e-6, -1e-7],  # Lower bounds
        [np.inf,  np.inf,  np.inf,  1e-2,  1e-3,  1e-4,  1e-5,  1e-6,  1e-7]   # Upper bounds
    )
    popt_fazekas =  RunFit(fitFazekas, "Fazekas", energies, efficiencies, mask, p0_fazekas, errs,bounds_fazekas)
    fazekas_names = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9']

    plt.plot(energy_range, fitFazekas(energy_range, *popt_fazekas),
             'b:', linewidth=2, label='Fazekas Fit')


#-----------------------------------------------------------------------------
#--------------------------------- Kane Fit ----------------------------------
#-----------------------------------------------------------------------------
if "Kane" in my_fits:
    mask_kane = mask & (energies >= 215) & (energies <= 2614)
    p0_kane = [0.7, 0.05]  # Slightly different defaults for this range
    bounds_kane=([0.1, 0], [5, 0.5])

    popt_kane =  RunFit(fitKane, "Kane", energies, efficiencies, mask_kane, p0_kane, errs,bounds_kane)

    if popt_kane is not None:
        E_plot = np.linspace(200, 2700, 500)  # Slightly beyond limits for visualization
        plt.plot(E_plot, fitKane(E_plot, *popt_kane),
                 'm-.', linewidth=2, label='Kane Fit (215-2614 keV)')
    else:
        print(f"\n Fit Kane FAILED")

#-----------------------------------------------------------------------------
#--------------------------------- Gray Efficiency Fit -----------------------
#-----------------------------------------------------------------------------
if "Gray" in my_fits:

    mask_gray = mask & (energies >= 120) & (energies <= 1400) & ~np.isin(energies, exclude_energies)
    p0_gray = [0.5, -0.3, 0.05, -0.001]  # More reasonable starting values
    bounds_gray = (
        [0.01, -1.0, -0.2, -0.05],  # Lower bounds
        [2.0,  0.0,  0.2,  0.05]    # Upper bounds
    )

    popt_gray =  RunFit(fitGray, "Gray", energies, efficiencies, mask_gray, p0_gray, errs,bounds_gray)

    if popt_gray is not None:
        E_plot = np.logspace(np.log10(50), np.log10(3000), 500)

        # Plot with distinct orange color
        plt.plot(E_plot, fitGray(E_plot, *popt_gray),
                 'y-', linewidth=2, alpha=0.7, label='Gray Fit (120-1400 keV)')

        # Add parameters to parameter box
        gray_text = f"Gray:\ng0 = {popt_gray[0]:.3f}\ng1 = {popt_gray[1]:.3f}\ng2 = {popt_gray[2]:.3f}\ng3 = {popt_gray[3]:.3f}"
        plt.text(0.98, 0.25, gray_text,
                 transform=plt.gca().transAxes,
                 fontsize=9,
                 ha='right', va='top',
                 bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))

#-----------------------------------------------------------------------------
# Visualization
#-----------------------------------------------------------------------------
plt.errorbar(energies[mask], efficiencies[mask], yerr=errs[mask],
             fmt='o', markersize=6, capsize=3,
             label='Included in fit', color='blue')

# Mark excluded points without connecting lines
plt.scatter(energies[~mask], efficiencies[~mask],
            color='red', marker='x', s=100,
            linewidths=1.5, label='Excluded (160, 511, 1460 keV)')

# Highlight 160 keV in the plot
if 160.609 in energies[mask]:
    idx_160 = np.where(energies == 160.609)[0][0]
    plt.scatter(energies[idx_160], efficiencies[idx_160],
                color='green', marker='s', s=80,
                label='160 keV (included)')

# Plot fit curve
# Modify the energy range for plotting to include lower energies
# energy_range = np.logspace(np.log10(50), np.log10(3700), 500)  # 50 to 4000 keV

# Plot all data points first (for context)
plt.errorbar(energies, efficiencies, yerr=errs,
             fmt='o', markersize=5, alpha=0.3,
             color='gray', label='All data')

# Highlight included points
# plt.errorbar(energies[mask], efficiencies[mask], yerr=errs[mask],
#              fmt='o', markersize=6, capsize=3,
#              label='Included in fit', color='blue')

# Highlight excluded points
# plt.scatter(energies[~mask], efficiencies[~mask],
#             color='red', marker='x', s=100,
#             linewidths=1.5, label='Excluded points')

# plt.plot(energy_range, fitRadware(energy_range, *popt_radware),
#          'r-', linewidth=2, label='Radware Fit')
plt.plot(energy_range, fitDebertin(energy_range, *popt_debertin),
         'g--', linewidth=2, label='Debertin Fit')
# plt.plot(energy_range, fitFazekas(energy_range, *popt_fazekas),
#          'b:', linewidth=2, label='Fazekas Fit')
# plt.plot(energy_range, fitGray(energy_range, *popt_gray),
#          color='orange', linewidth=2, label='Gray Fit')





plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.xlim(50, 4000)  # Extended x-axis limits
plt.ylim(0, 1.4)  # Extended x-axis limits
print('I am using forced limits for Y-axis')
plt.xlabel('Energy, keV', fontsize=14)
plt.ylabel('Efficiency, %', fontsize=14)
plt.title(f'Efficiency CL{clover}S{server} (Fold {fold})', fontsize=14)
plt.legend(fontsize=10, framealpha=1)
plt.grid(which='both', alpha=0.3)
plt.tight_layout()

if 'param_text_rw' in globals():
    plt.text(0.98, 0.6,  # Top-right corner
             f"RadWare:\n{param_text_rw}",
             transform=plt.gca().transAxes,
             fontsize=10,
             ha='right', va='top',  # Right-aligned text
             bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))



if 'param_text_debretin' in globals():
    plt.text(0.86, 0.6,  # Top-right corner
             f"Debretin:\n{param_text_debretin}",
             transform=plt.gca().transAxes,
             fontsize=10,
             ha='right', va='top',  # Right-aligned text
             bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))

param_text_fazekas = "\n".join([f"{name} = {value:.4f}" for name, value in zip(fazekas_names, popt_fazekas)])
# param_text_fazekas = "\n".join([f"{n} = {v:.3g}" for n,v in zip(fazekas_names[:5], popt_fazekas[:5])] +
#                                ["..."] +
#                                [f"{n} = {v:.3g}" for n,v in zip(fazekas_names[-2:], popt_fazekas[-2:])])
plt.text(0.72, 0.6,  # Top-right corner
         f"Fazekas:\n{param_text_fazekas}",
         transform=plt.gca().transAxes,
         fontsize=10,
         ha='right', va='top',  # Right-aligned text
         bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))


#-----------------------------------------------------------------------------


def calculate_chi2(fit_func, params):
    pred = fit_func(energies[mask], *params)
    return np.sum(((efficiencies[mask] - pred) / errs[mask])**2)

chi2_radware = calculate_chi2(fitRadware, popt_radware)
chi2_debertin = calculate_chi2(fitDebertin, popt_debertin)
chi2_fazekas = calculate_chi2(fitFazekas, popt_fazekas)

dof = len(energies[mask]) - len(popt_radware)  # degrees of freedom

print("\nGoodness-of-fit comparison:")
print(f"Radware χ²/dof = {chi2_radware:.1f}/{dof} = {chi2_radware/dof:.2f}")
print(f"Debertin χ²/dof = {chi2_debertin:.1f}/{dof} = {chi2_debertin/dof:.2f}")
print(f"Fazekas χ²/dof = {chi2_fazekas:.1f}/{dof} = {chi2_fazekas/dof:.2f}")


# Save and show
plt.savefig(f'efficiency_CL{clover}S{server}_fold{fold}.png', dpi=300)
plt.show()
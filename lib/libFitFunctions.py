import sys, os, json

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# from utils.plotting.plot_eff_all_clovers import label


# ourpath = os.getenv('PY_CALIB')
# sys.path.append(ourpath+'/lib')
# from libLists import lists_of_gamma_background as lists_of_gamma_background

#---------------------------------fit Fazekas--------------------------------------------
def fitFazekas(E, a1, a2, a3, a4, a5, a6, a7, a8, a9):
    """
    Correct Fazekas efficiency function:
    ε(E) = exp(a1 + a2*ln(E) + a3*ln(E)^2 + ... + a9*ln(E)^8)
    with numerical stabilization
    """
    E = np.maximum(E, 1e-10)  # Avoid log(0)
    logE = np.log(E)

    # Compute polynomial with careful handling of extreme values
    poly = a1
    poly += a2 * logE
    poly += a3 * logE**2
    poly += a4 * logE**3
    poly += a5 * logE**4
    poly += a6 * logE**5
    poly += a7 * logE**6
    poly += a8 * logE**7
    poly += a9 * logE**8

    # Stabilize the exponential
    poly = np.clip(poly, -100, 100)  # Prevent overflow
    return np.exp(poly)

# ------------------------------ Fit Debertin with Constraints ---------------------------------
def fitDebertin(E, a1, a2, a3, a4, a5):
    eff = a1 * np.log(E) + a2 * np.log(E) / E + a3 * np.log(E)**2 / E + a4 * np.log(E)**4 / E + a5 * np.log(E)**5 / E
    return np.maximum(eff, 1e-6)  # Force efficiency ≥ 0 (with small cutoff)

# def fitDebertin(E, a1, a2, a3, a4, a5):
#     """
#     Debertin efficiency function limited to 120-1400 keV range:
#     ε(E) = a1*ln(E) + a2*ln(E)/E + a3*ln(E)²/E + a4*ln(E)⁴/E + a5*ln(E)⁵/E
#     Returns NaN outside this range for clear visualization
#     """
#     E = np.asarray(E)
#     mask = (E >= 120) & (E <= 1400)
#     result = np.full_like(E, np.nan, dtype=float)
#
#     # Only compute for energies in range
#     E_valid = np.maximum(E[mask], 1.0)  # Still avoid log(0)
#     logE = np.log(E_valid)
#
#     # Compute efficiency
#     eff = (a1 * logE +
#            a2 * logE / E_valid +
#            a3 * logE**2 / E_valid +
#            a4 * logE**4 / E_valid +
#            a5 * logE**5 / E_valid)
#     result[mask] = np.maximum(eff, 1e-6)
#
#     return result


# ------------------------------ Fit Resolution ---------------------------------
def fitResolution(E, a1, b1, c1):
    return np.sqrt(a1+b1*E+c1*E*E)

# ------------------------------ Fit Radware ---------------------------------

def fitRadware(energy, A, B, C, D, E, F, G, E1=100, E2=1000):
    x = np.log(energy/E1)
    y = np.log(energy/E2)

    # Numerically stable computation
    with np.errstate(all='ignore'):
        base1 = np.exp(np.clip(A + B*x + C*x**2, -100, 100))
        base2 = np.exp(np.clip(D + E*y + F*y**2, -100, 100))
        G_safe = np.clip(G, 0.1, 10)
        eff = (base1**(-G_safe) + base2**(-G_safe))**(-1/G_safe)
        return np.nan_to_num(eff, nan=0)


#--------------------------------- Kane Fit ---------------------------------
def fitKane(E, b, c, E0=121):
    """
    Kane efficiency function limited to 215-2614 keV range:
    ε(E) = (E0/E)^b * exp(-c*(ln(E/E0))^2) for 215 ≤ E ≤ 2614 keV
    Returns NaN outside this range for clear visualization
    """
    E = np.asarray(E)
    mask = (E >= 215) & (E <= 2614)
    result = np.full_like(E, np.nan, dtype=float)

    # Only compute for energies in range
    E_valid = np.maximum(E[mask], 1.0)  # Still avoid log(0)
    ratio = E_valid / E0
    log_ratio = np.log(ratio)

    # Compute efficiency
    eff = np.power(ratio, -b) * np.exp(-c * log_ratio**2)
    result[mask] = np.clip(eff, 1e-10, 1.0)

    return result

def fitGray(E, g0, g1, g2, g3, E0=100):
    """
    Stabilized Gray efficiency function:
    ε(E) = exp(g0 + g1*ln(E/E0) + g2*ln(E/E0)^2 + g3*ln(E/E0)^3) / (1 + (E/E0)^2)
    Ensures proper behavior at all energies
    """
    E = np.maximum(E, 1.0)  # Minimum 1 keV
    ratio = E/E0
    ln_ratio = np.log(ratio)

    # Numerator (exponential of polynomial)
    exponent = g0 + g1*ln_ratio + g2*ln_ratio**2 + g3*ln_ratio**3
    numerator = np.exp(np.clip(exponent, -10, 10))  # Tighter clipping

    # Denominator (stabilization term)
    denominator = 1 + ratio**2  # Changed from ^4 to ^2 for smoother transition

    return numerator / denominator

def fitGrayOld(E, g0, g1, g2, g3):
    """
    Gray efficiency function:
    ε(E) = (g0 + g1*ln(E) + g2*ln(E)^2 + g3*ln(E)^3)/E
    Provides a complementary efficiency parameterization
    """
    E = np.maximum(E, 1.0)  # Minimum 1 keV to avoid log(0)
    lnE = np.log(E)
    numerator = g0 + g1*lnE + g2*lnE**2 + g3*lnE**3
    return numerator / E

#--------------------------------- ancillary functions ---------------------------------


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

def extract_fold_data(all_folds, fold_number=4):
    """Extract specific fold data from loaded JSON"""
    if not isinstance(all_folds, list):
        print("Error: Expected list of folds in JSON data")
        return None

    for fold in all_folds:
        if isinstance(fold, dict) and fold.get("fold") == fold_number:
            return fold
    print(f"Error: Fold {fold_number} not found in data")
    return None

def process_efficiency_data(fold_data):
    """Process efficiency data from fold data"""
    if not fold_data:
        return None

    energies, efficiencies, errors = [], [], []

    for isotope, peaks in fold_data.items():
        if isotope == "fold":
            continue

        if not isinstance(peaks, dict):
            print(f"Warning: Invalid data format for isotope {isotope}")
            continue

        for energy_str, peak_data in peaks.items():
            try:
                energy = float(energy_str)
                eff_data = peak_data.get("eff")

                if eff_data and len(eff_data) >= 2:
                    energies.append(energy)
                    efficiencies.append(eff_data[0])
                    errors.append(eff_data[1])
            except (ValueError, AttributeError) as e:
                print(f"Skipping invalid entry {isotope} {energy_str}: {e}")

    return (
        np.array(energies),
        np.array(efficiencies),
        np.array(errors)
    )


def RunFit(fitFunc, lbFunc, ener, eff, mask, p0, err, bounds, maxfev=5000):
    try:
        if mask is not None:
            ener = ener[mask]
            eff = eff[mask]
            err = err[mask]

        popt, pcov = curve_fit(
            fitFunc,          # The model function to fit
            ener,             # Independent variable (energy)
            eff,              # Dependent variable (efficiency)
            p0=p0,            # Initial guess for the parameters
            sigma=err,        # Standard deviation of the data points
            bounds=bounds,    # Bounds on parameters
            maxfev=maxfev     # Maximum number of function evaluations
        )

        # Print the fitted parameters
        print(f"\n{lbFunc} Fit Parameters:")
        for i, param in enumerate(popt):
            print(f"Parameter {i}: {param:.6f}")

        pred = fitFunc(ener, *popt)
        chi2 = np.nansum(((eff - pred)/err**2))
        dof = len(ener) - len(popt)
        # dof = np.sum(mask) - len(popt)
        print(f"Kane reduced χ² = {chi2/dof:.2f}")

    except Exception as e:
        print(f"\n{lbFunc} fitting failed: {e}")
        popt = None

    return popt

# def save_plot_data_to_ascii(js_new, index, source, output_filename="plotted_data.txt"):
#     # Open the file in write mode
#     with open(output_filename, 'a') as f:
#         # Iterate through the elements in js_new and extract el, eff data
#         # f.write("# energy efficiency area resolution \n")
#         for el in js_new[index][source]:
#             if el in lists_of_gamma_background:
#                 continue
#             # Extract x (el) and y (eff) values
#             x = float(el)
#             eff = js_new[index][source][el]['eff'][0]
#             res = js_new[index][source][el]['res'][0]
#             try:
#                 area = js_new[index][source][el]['area']
#             except:
#                 area = -1
#
#             # Write the data to the file (as a line in the form: el, eff)
#             # f.write(f"{source} {x} {eff} {res} {area} \n")
#             f.write("{} {} {} {} {} \n".format(source, x, eff, res, area))
#
#         print(f"Data saved to {output_filename}")
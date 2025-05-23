import sys, os

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
ourpath = os.getenv('PY_CALIB')
sys.path.append(ourpath+'/lib')
from libLists import lists_of_gamma_background as lists_of_gamma_background

def fitResolution(E, a1, b1, c1):
    return np.sqrt(a1+b1*E+c1*E*E)

def fitDebertin(E, a1,a2,a3,a4,a5):
    return a1 * np.log(E) + a2 * np.log(E) / E + a3 * np.log(E) ** 2 / E + a4 * np.log(E) ** 4 / E + a5 * np.log(E) ** 5 / E

def fitRadware(energy, A, B, C, D, E, F, G):
    E1 = 100
    E2 = 1000
    x = np.log(energy / E1)
    y = np.log(energy / E2)

    # Compute bases
    base1 = A + B * x + C * x * x
    base2 = D + E * y + F * y * y

    # Ensure bases are positive to avoid invalid exponentiation
    base1 = np.where(base1 <= 0, np.nan, base1)
    base2 = np.where(base2 <= 0, np.nan, base2)

    # Handle G = 0 safely
    G_safe = G if G != 0 else 1e-10

    # Compute efficiency
    eff = np.exp(((base1 ** (-G_safe) + base2 ** (-G_safe)) ** (-1 / G_safe)))

    return eff



def fitFazekas(E, a1, a2, a3, a4, a5, a6, a7, a8, a9):
    """
    Computes the sum: sum(log(a_i * log(E)^(i-1))) for i = 1 to 9

    Parameters:
    - E: Energy value (scalar or array)
    - a1, a2, ..., a9: Fit coefficients

    Returns:
    - Computed fit function values
    """
    E = np.maximum(E, 1e-10)  # Prevent log(0)
    logE = np.log(E)

    total_sum = 0
    coeffs = [a1, a2, a3, a4, a5, a6, a7, a8, a9]  # Store coefficients in a list

    for i, ai in enumerate(coeffs, start=1):
        term = ai * logE**(i-1)  # Compute a_i * (log(E))^(i-1)
        term = np.maximum(term, 1e-10)  # Prevent log of negative/zero
        total_sum += np.log(term)  # Log of the term

    return total_sum


def read_data_for_fit(input_filename):
    data_full = {}
    with open(input_filename, 'r') as file:
        for line in file:
            elements = line.split()
            key = float(elements[1])  # Use the second column as the key
            isotope_name = elements[0]

            values = [isotope_name] + list(map(float, elements[1:]))
            data_full[key] = values

    # Print the dictionary
    # for key, value in data_full.items():
    #     print(f"{key}: {value}")

    return data_full

def save_plot_data_to_ascii(js_new, index, source, output_filename="plotted_data.txt"):
    # Open the file in write mode
    with open(output_filename, 'a') as f:
        # Iterate through the elements in js_new and extract el, eff data
        # f.write("# energy efficiency area resolution \n")
        for el in js_new[index][source]:
            if el in lists_of_gamma_background:
                continue
            # Extract x (el) and y (eff) values
            x = float(el)
            eff = js_new[index][source][el]['eff'][0]
            res = js_new[index][source][el]['res'][0]
            try:
                area = js_new[index][source][el]['area']
            except:
                area = -1

            # Write the data to the file (as a line in the form: el, eff)
            # f.write(f"{source} {x} {eff} {res} {area} \n")
            f.write("{} {} {} {} {} \n".format(source, x, eff, res, area))

        print(f"Data saved to {output_filename}")
import sys

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def fitDebertin(E, a1,a2,a3,a4,a5):
    return a1 * np.log(E) + a2 * np.log(E) / E + a3 * np.log(E) ** 2 / E + a4 * np.log(E) ** 4 / E + a5 * np.log(E) ** 5 / E

def fit_data_from_file(input_filename):
    # Load data from the ASCII file
    data = np.loadtxt(input_filename)

    # Assuming the first column is 'el' (E) and the second column is 'eff' (n(epsilon))
    E = data[:, 0]  # First column: E (Energy)
    n_epsilon = data[:, 1]  # Second column: n(epsilon)
    n_resolution = data[:, 2]  # Second column: n(epsilon)
    data_eff = {}
    data_res = {}

    for i in range(len(E)):
        data_eff[E[i]] = n_epsilon[i]
        data_res[E[i]] = n_resolution[i]

    data_eff = dict(sorted(data_eff.items()))
    data_res = dict(sorted(data_res.items()))

    ener = np.array(list(data_eff.keys()))
    eff = np.array(list(data_eff.values()))
    res = np.array(list(data_res.values()))

    return  ener, eff, res

def save_plot_data_to_ascii(js_new, index, source, output_filename="plotted_data.txt"):
    # Open the file in write mode
    with open(output_filename, 'a') as f:
        # Write header line
        # f.write("el, eff\n")

        # Iterate through the elements in js_new and extract el, eff data
        f.write("# energy efficiency area resolution \n")
        for el in js_new[index][source]:
            # Extract x (el) and y (eff) values
            x = float(el)
            eff = js_new[index][source][el]['eff']
            res = js_new[index][source][el]['res']
            area = js_new[index][source][el]['area']

            # Write the data to the file (as a line in the form: el, eff)
            f.write(f"{x} {eff} {area} {res}\n")

        print(f"Data saved to {output_filename}")
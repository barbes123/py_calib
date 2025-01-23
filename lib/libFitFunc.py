import sys

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def fitResolution(E, a1, b1, c1):
    return np.sqrt(a1+b1*E+c1*E*E)

def fitDebertin(E, a1,a2,a3,a4,a5):
    return a1 * np.log(E) + a2 * np.log(E) / E + a3 * np.log(E) ** 2 / E + a4 * np.log(E) ** 4 / E + a5 * np.log(E) ** 5 / E

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
            # Extract x (el) and y (eff) values
            x = float(el)
            eff = js_new[index][source][el]['eff']
            res = js_new[index][source][el]['res']
            try:
                area = js_new[index][source][el]['area']
            except:
                area = -1

            # Write the data to the file (as a line in the form: el, eff)
            # f.write(f"{source} {x} {eff} {res} {area} \n")
            f.write("{} {} {} {} {} \n".format(source, x, eff, res, area))

        print(f"Data saved to {output_filename}")
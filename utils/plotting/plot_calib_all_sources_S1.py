#! /usr/bin/python3
import json, os
import os.path



import matplotlib.pyplot as plt
import numpy as np
import sys

from sympy.printing.pretty.pretty_symbology import line_width

RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
RESET = '\033[0m'



my_colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'orange', 'purple', 'brown']
my_markers = ['o', 's', '^', 'v', 'x', '+', '*', 'D', 'p', ',']
list_of_lut_2024 = {"S1":"CL29", "S2":"CL30", "S6":"CL31", "S3":"CL32", "S7":"CL33", "S5":"CL34", "S4":"CL35", "S8":"CL36"}
list_of_runs = {'60Co': 161, '152Eu': 162, '22Na':163, '54Mn':165,'133Ba':166,'137Cs':167,'56Co':170}
# list_of_runs = {'60Co': 161}
prefix = 'selected_run'
server = 1
volume = 999
files = []
save_results_to = '{}/fig_calib_S{}'.format(os.getcwd(),server)
grType = 'jpg'
dpi = 300


plt.figure(figsize=(10, 6))

# Number of datasets and number of data points
num_datasets = len(list_of_runs)

# Create positions for the bars

# Set bar width (bars for each dataset will be placed next to each other)
width = 0.1  # Adjust this to control how much space between bars

import os
import json

def GetDataFromFiles1():

    plot_index = 0
    pos_ch_dict = {}

    for isotope, run in list_of_runs.items():
        if plot_index >= len(my_colors):  # Ensure we don't exceed the color list
            plot_index = 0  # Reset to 0 if we run out of colors

        file = f's{server}/{prefix}_{run}_{volume}_eliadeS{server}/calib_res_{run}.json'

        if not os.path.exists(file):
            print(f'{RED} file {file} does not exist {RESET}')
            continue  # Skip this iteration if the file doesn't exist

        try:
            with open(file, 'r') as fin:
                js_data = json.load(fin)
            print(f'Loaded file {file}')
        except Exception as e:
            print(f'Cannot load file {file}: {e}')
            continue  # Skip this iteration if loading the file fails

        # Building pos_ch_dict for each run and isotope
        for datum in js_data:
            if isotope in datum:
                if datum["domain"] not in pos_ch_dict:
                    pos_ch_dict[datum["domain"]] = {}

                for energy, energy_data in datum[isotope].items():
                    pos_ch_dict[datum["domain"]][energy] = energy_data["pos_ch"]

    for domain, energies in pos_ch_dict.items():
        sorted_energies = dict(sorted(energies.items(), key=lambda item: float(item[0])))
        pos_ch_dict[domain] = sorted_energies

    return pos_ch_dict

def GetDataFromFiles():

    plot_index = 0
    i = 0
    for isotope, run in list_of_runs.items():
        if plot_index >= len(my_colors):  # Ensure we don't exceed the color list
            plot_index = 0  # Reset to 0 if we run out of colors

        file = f's{server}/{prefix}_{run}_{volume}_eliadeS{server}/calib_res_{run}.json'

        if not os.path.exists(file):
            print(f'{RED} file {file} does not exsist {RESET}')

        try:
            with open(file,'r') as fin:
                js_data = json.load(fin)
            print(f'Loaded file {file}')
        except:
            print(f'Cannot load file {file}')
            continue


        # pos_ch_values = [energy_data["pos_ch"] for datum in js_data for energy_data in datum[isotope].values()]
        # pos_ch_dict = {energy: energy_data["pos_ch"] for datum in js_data for energy, energy_data in datum[isotope].items()}
        pos_ch_dict = {
            datum["domain"]: {energy: energy_data["pos_ch"] for energy, energy_data in datum[isotope].items()}
            for datum in js_data
        }
    return  pos_ch_dict

def MakePlotCalib(pos_ch_dict):

    print(save_results_to)
    if not os.path.exists(save_results_to):
        os.makedirs(save_results_to)

    js_calib = {}

    for domain, energy_data in pos_ch_dict.items():
        energies = list(energy_data.keys())  # x-axis labels (energy values)
        energies = [float(energy) for energy in energy_data.keys()]  # Convert to float
        pos_ch_values = list(energy_data.values())  # y-axis values (pos_ch)

        coefficients_poly1 = np.polyfit(energies, pos_ch_values, 1)
        pol1y_values = np.polyval(coefficients_poly1, energies)

        coefficients_poly2 = np.polyfit(energies, pos_ch_values, 2)
        pol2y_values = np.polyval(coefficients_poly2, energies)

        poly1_coef_text = f"{coefficients_poly1[0]:.4f}x + {coefficients_poly1[1]:.4f}"
        poly2_coef_text = f"{coefficients_poly2[0]:.1f} x² $10^{{{np.log10(abs(coefficients_poly2[0])):.0f}}}$ + " \
                          f"{coefficients_poly2[1]:.4f} x $10^{{{np.log10(abs(coefficients_poly2[1])):.0f}}}$ + " \
                          f"{coefficients_poly2[2]:.4f}"

        # print(pos_ch_dict[domain])
        if domain not in js_calib:
            js_calib[domain] = {}

        js_calib[domain]['poly1'] = [coefficients_poly1[0], coefficients_poly1[1]]
        js_calib[domain]['poly2'] = [coefficients_poly2[0], coefficients_poly2[1], coefficients_poly2[2]]



        plt.figure(figsize=(6, 4))  # Create a new figure for each domain
        plt.scatter(energies, pos_ch_values, color='black')
        plt.xticks(range(500, 4001, 500), size=12)

        plt.xlabel("Energy (keV)", size=10)
        plt.ylabel("pos_ch", size=10)
        plt.title(f"Calibration Domain {domain}", size=12)

        # Annotate each bar with its value
        # for i, value in enumerate(pos_ch_values):
        #     plt.text(energies[i], value + 5, f"{value:.2f}", ha='center', fontsize=10)

        # plt.figure(0)

        plt.ylim(min(pos_ch_values) - 20, max(pos_ch_values) + 50)  # Adjust Y limits for visibility
        plt.plot(energies, pol1y_values, color='r', label=f'poly1')  # Polynomial curve
        plt.plot(energies, pol2y_values, color='g', label=f'poly2')  # Polynomial curve
        # plt.grid(axis="y", linestyle="--", alpha=0.6)
        plt.grid(True, linestyle="--", alpha=0.6)
        # plt.legend()
        plt.text(0.05, 0.95, poly1_coef_text, transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
        plt.text(0.05, .85, poly2_coef_text, transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')

        plt.savefig(f'{save_results_to}/calib_dom_{domain}.{grType}', dpi = dpi)
        plt.close()

    return js_calib

def make_palette(N):
    cmap = plt.cm.viridis  # You can replace 'viridis' with any other colormap
    palette = [cmap(i / N) for i in range(N)]
    color_index = 0
    return palette, cmap

def PlotAllCalib(data, poly):
    N = len(data)
    # cmap = plt.cm.viridis  # You can replace 'viridis' with any other colormap
    # palette = [cmap(i / N) for i in range(N)]
    palette, cmap = make_palette(N)
    color_index = 0

    # plt.figure()
    fig, ax = plt.subplots()
    for domain, energy_data in data.items():
        energies = list(energy_data.keys())  # x-axis labels (energy values)
        energies = [float(energy) for energy in energy_data.keys()]  # Convert to float
        pos_ch_values = list(energy_data.values())  # y-axis values (pos_ch)
        ax.scatter(energies, pos_ch_values, color=palette[color_index], linewidth=1, label = f'dom{domain}')
        pol1y_values = np.polyval(poly[domain]['poly1'], energies)
        ax.plot(energies, pol1y_values, color=palette[color_index])
        color_index+=1

    # Create a color bar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=N))
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label("Domain")  # Label for the color bar

    plt.xlabel("Energy (keV)", size=10)
    plt.ylabel("pos_ch", size=10)
    cloverID = list_of_lut_2024[f'S{server}']
    plt.title(f"Calibration S{server} Clover {cloverID}", size=12)
    # plt.legend()
    plt.savefig(f'{save_results_to}/calib_dom_all.{grType}', dpi=dpi)


def Plot2D(data):
    palette, cmap = make_palette(len(data))
    domains = list(data.keys())  # Domain labels
    poly1_0 = [data[d]["poly1"][0] for d in domains]  # X-axis (poly1[0])
    poly1_1 = [data[d]["poly1"][1] for d in domains]  # Y-axis (poly1[1])
    # plt.figure(figsize=(6, 4))
    # plt.scatter(poly1_0, poly1_1, c='b', edgecolors='k', linewidths=1.5, s=100)

    fig, ax = plt.subplots()

    color_index = 0
    for i, domain in enumerate(domains):
        ax.scatter(poly1_0[i], poly1_1[i], color=palette[color_index], label=f"Domain {domain}")
        color_index+=1

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=len(data)))
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label("Domain")  # Label for the color bar

    plt.xlabel("pol0", size=12)
    plt.ylabel("pol1", size=12)
    cloverID = list_of_lut_2024[f'S{server}']
    plt.title(f"Calibration S{server} Clover {cloverID}", size=12)
    # plt.legend()
    plt.savefig(f'{save_results_to}/poly1_all.{grType}', dpi=dpi)
    # plt.show()
    plt.close()



def Plot3D(data):

    palette, cmap = make_palette(len(data))
    domains = list(data.keys())  # Domain labels
    poly2_0 = [data[d]["poly2"][0] for d in domains]  # X-axis (poly1[0])
    poly2_1 = [data[d]["poly2"][1] for d in domains]  # Y-axis (poly1[1])
    poly2_2 = [data[d]["poly2"][2] for d in domains]  # Y-axis (poly1[1])

    fig = plt.figure(figsize=(7, 5))
    ax = fig.add_subplot(111, projection='3d')
    sc = ax.scatter(poly2_0, poly2_1, poly2_2, c=list(map(int, domains)), cmap=cmap, edgecolors='k', s=100)

    # Scatter plot with colors
    color_index = 0
    for i, domain in enumerate(domains):
        ax.scatter(poly2_0[i], poly2_1[i], poly2_2[i], color=palette[color_index], label=f"Domain {domain}")
        color_index+=1
        # ax.text(poly2_0[i], poly2_1[i], poly2_2[i], domain, fontsize=10)

    ax.set_xlabel("poly0", size=12)
    ax.set_ylabel("poly1", size=12)
    ax.set_zlabel("poly2", size=12)
    cloverID = list_of_lut_2024[f'S{server}']
    ax.set_title(f"Calibration S{server} Clover {cloverID}", size=12)

    cbar = fig.colorbar(sc, ax=ax, orientation="vertical")
    cbar.set_label("Domain")


    plt.savefig(f'{save_results_to}/poly2_all.{grType}', dpi=dpi)
    plt.show()

# for domain, poly in poly.items():
#     print(poly['poly1'][0])
#     poly1x = list(poly['poly1'][0])  # x-axis labels (energy values)
#     # energies = [float(energy) for energy in energy_data.keys()]  # Convert to float
#     # pos_ch_values = list(energy_data.values())  # y-axis values (pos_ch)


dic_e_ch = GetDataFromFiles1()

with open(f'calib_e_ch_run_S{server}.json','w') as fout:
    json.dump(dic_e_ch, fout, indent = 4)

# print(dic_e_ch)

js_polys = MakePlotCalib(dic_e_ch)
PlotAllCalib(dic_e_ch, js_polys)
Plot2D(js_polys)
Plot3D(js_polys)

with open(f'calib_polys_S{server}.json','w') as fout:
    json.dump(js_polys, fout, indent = 4)




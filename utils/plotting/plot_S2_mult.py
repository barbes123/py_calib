#! /usr/bin/python3
import matplotlib.pyplot as plt
import numpy as np
import sys
my_colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'orange', 'purple', 'brown']
my_markers = ['o', 's', '^', 'v', 'x', '+', '*', 'D', 'p', ',']
list_of_lut_2024 = {"S1":"CL29", "S2":"CL30", "S6":"CL31", "S3":"CL32", "S7":"CL33", "S5":"CL34", "S4":"CL35", "S8":"CL36"}


list_of_runs = {'60Co': 157, '152Eu': 158, '22Na':160, '54Mn':162,'133Ba':163,'137Cs':164,'56Co':167}
server = 2
volume = 999
files = []

plt.figure(figsize=(10, 6))

# Number of datasets and number of data points
num_datasets = len(list_of_runs)

# Create positions for the bars

# Set bar width (bars for each dataset will be placed next to each other)
width = 0.1  # Adjust this to control how much space between bars

plot_index = 0
i = 0
for isotope, run in list_of_runs.items():
    if plot_index >= len(my_colors):  # Ensure we don't exceed the color list
        plot_index = 0  # Reset to 0 if we run out of colors

    file = f's{server}/addback_run_{run}_{volume}_eliadeS{server}/px_mult.spe'

    try:
        data = np.loadtxt(file)
        print(f'Loaded file {file}')
    except:
        print(f'Cannot load file {file}')
        continue

    num_points = len(data)
    x = np.arange(num_points)

    sum_tot = sum(data)
    norm_data = [x / sum_tot for x in data]

    # plt.plot(norm_data, marker=my_markers[plot_index], linestyle='-', color=my_colors[plot_index], label=isotope)
    # plt.fill_between(range(len(norm_data)), norm_data, color=my_colors[plot_index], alpha=0.1)  # alpha sets transparency

    plt.bar(x + i * width, norm_data, width=width, label=isotope, alpha=0.7)

    x = range(len(norm_data))  # x positions for the bars
    # plt.bar(x, norm_data, color=my_colors[plot_index], label=isotope, alpha=0.7)


    plot_index += 1  # Increment the plot_index to choose the next color
    i+=1

try:
    s = f'S{server}'
    clover = list_of_lut_2024[s]
    print(f'Clover Name {clover} server S{server}')
except:
    print(f'Clover name is not found server S{server}, never mind')
    clover = ''

plt.title(f"fold Clover {clover} server{server}")
plt.xlabel("fold")  # Assuming energy values are in the x-axis
plt.ylabel("Counts")
plt.xlim(0,5)
plt.legend()
plt.grid(True)
plt.yscale('log')
# plt.savefig('54Mn_fold_all.jpg', dpi = 300)
plt.savefig(f'fold_spectra_S{server}.jpg', dpi = 300)

# Show the plot
plt.show()

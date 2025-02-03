import json, os, sys
import matplotlib.pyplot as plt
import glob

# Get list of JSON files (assumes they follow the naming pattern 'merger*.json')
json_files = sorted(glob.glob("mergedS*.json"))
list_of_bad_lines = ['79.623', '160.609']

save_results_to =''

ourpath = os.getenv('PY_CALIB')
if ourpath == None:
    ourpath = '/data10/live/IT/py_calib'
    print(f'Setting up as {ourpath}')
else:
    print('PY_CALIB path: ', ourpath)

lib_path = '{}/lib'.format(ourpath)
# print(lib_path)
sys.path.insert(1, lib_path)
# sys.path.insert(1, '{}/json'.format(ourpath))
# print(sys.path)
# sys.exit()
from libLists import list_of_sources as list_of_sources
from libLists import lists_of_gamma_background as lists_of_gamma_background
from libColorsAnsi import *

color_index = 0

jsfile = f'{ourpath}/json/gamma_sources.json'
if os.path.exists(jsfile):
    with open(jsfile, 'r') as file:
        js_sources = json.load(file)

legend_added = {}

for idx, filename in enumerate(json_files):
    if color_index > 9:
        color_index = 0
    with open(filename, "r") as f:
        js_new = json.load(f)

        for index in range(0, len(js_new)):
            if index < 3:
                continue

            for source in list_of_sources:
                if source in js_new[index]:
                    print(f'{BLUE} {source} {RESET}',end='')

                    for el in js_new[index][source]:
                        if el in list_of_bad_lines:
                            continue

                        label = 'Server S{}'.format(color_index + 1)
                        if label not in legend_added:
                            legend_added[label] = True
                            print('\n Plotting for server ', label)
                        else:
                            label = None

                        if source != '56Co':
                            plt.figure(0)
                            if el not in lists_of_gamma_background:
                                plt.scatter(
                                    x=float(el),
                                    y=js_new[index][source][el]['eff'][0],
                                    color=my_colors[color_index],
                                    label=label
                                )
                                plt.errorbar(
                                    x=float(el),
                                    y=js_new[index][source][el]['eff'][0],
                                    yerr=js_new[index][source][el]['eff'][1],
                                    color=my_colors[color_index]
                                )
                            # plt.scatter(x=float(el), y=js_new[index][source][el]['eff'][0], color = colors[source][index])
                            # plt.errorbar(x=float(el), y=js_new[index][source][el]['eff'][0], yerr=js_new[index][source][el]['eff'][1], color=colors[source][index] )
                        plt.figure(1)
                        plt.scatter(x=float(el), y=js_new[index][source][el]['res'][0], color=my_colors[color_index], label=label)
                        plt.errorbar(x=float(el), y=js_new[index][source][el]['res'][0],
                                     yerr=js_new[index][source][el]['res'][1], color=my_colors[color_index])
                        if index > 0:
                            plt.figure(2)
                            if el not in lists_of_gamma_background and el not in list_of_bad_lines:
                                plt.scatter(
                                    x=float(el),
                                    y=js_new[index][source][el]['addback'][0],
                                    color=my_colors[color_index],
                                    label=label
                                )
                                plt.errorbar(
                                    x=float(el),
                                    y=js_new[index][source][el]['addback'][0],
                                    yerr=js_new[index][source][el]['addback'][1],
                                    color=my_colors[color_index]
                                )
    color_index+=1

cloverName = 'All Clover: 29, 30, 31'
pltFold = 4
opt = 'jpg'
dpi = 300

plt.figure(0)
max_y = max([line.get_ydata().max() for line in plt.gca().get_lines()])
plt.ylim(0, 1.5 * max_y)

plt.title('Efficiency {}'.format(cloverName))
plt.xlabel('E$\gamma$')
plt.ylabel('Efficiency, %')
plt.legend(loc='upper right', fontsize='medium', shadow=False, ncol=2)

file_name_eff = 'fold_eff_all_{}.{}'.format(pltFold, opt)
plt.savefig(save_results_to + file_name_eff, dpi=dpi)

plt.figure(1)
plt.title('Resolution {}'.format(cloverName))
plt.xlabel('E$\gamma$')
plt.ylabel('Resolution, keV')
# plt.legend(loc='upper left', fontsize='medium', shadow=False, ncol=2)
plt.legend(loc='upper left', fontsize='medium', shadow=False, ncol=2)

file_name_res = 'fold_res_all_{}.{}'.format(pltFold, opt)
plt.savefig(save_results_to + file_name_res, dpi=dpi)

plt.figure(2)
plt.title('Addback {}'.format(cloverName))
plt.grid()
plt.xlabel('E$\gamma$', fontsize=14)
plt.tick_params(axis='both', labelsize=12)  # Increase tick label size to 12
plt.ylim(0.8, 2)
plt.legend(loc='upper left', fontsize='medium', shadow=False, ncol=2)
file_name_ab = 'fold_eff_ab_{}.{}'.format(pltFold, opt)
plt.savefig(save_results_to + file_name_ab, dpi=dpi)

# plt.show()

for i in range(0,3):
    plt.figure(i)
    plt.close()


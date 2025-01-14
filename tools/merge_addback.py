import json
import sys

import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from matplotlib import interactive
import numpy as np
import os
import matplotlib.colors as mcolors
from random import choice


def MakeDir(path):
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
        print("The new directory {} is created!".format(path))

opt = 'jpg'
opt = 'eps'

# ourpath = '/data10/live/IT/py_calib'
ourpath = os.getenv('PY_CALIB')

current_directory = os.getcwd()
datapath = '{}/'.format(current_directory)


# global save_results_to
# save_results_to = '/home/rmiron/Desktop/dir/python_exercises/calibrations/figures/'
save_results_to = '{}/figures/'.format(datapath)
MakeDir(save_results_to)


list_of_clovers = {"CL29", "CL30", "CL31", "CL32", "CL33", "CL34", "CL35", "CL36", "HPGe", "SEG", "LaBr"}
list_of_sources = {'60Co','60CoWeak', '152Eu','137Cs', '133Ba', '54Mn','22Na','252Cf','bg'}
list_of_cebr = {"CEBR1","CEBR2","CEBR3","CEBR4"}

#res and eff vs ener for each domain




f60Co = '/data10/data/eliade/addback/s2/addback_run_157_999_eliadeS2/addback_157.json'
f152Eu = '/data10/data/eliade/addback/s2/addback_run_158_999_eliadeS2/addback_158.json'

run60Co = f60Co.split('addback_run_')[1].split('_')[0]
run152Eu = f152Eu.split('addback_run_')[1].split('_')[0]
server = f60Co.split('_eliadeS')[1].split('/')[0]
meta_data = 'Runs {}_{}_eliadeS{}'.format(run60Co,run152Eu,server)

with open(f60Co, 'r') as file:
    js60Co = json.load(file)

with open(f152Eu, 'r') as file:
    js152Eu = json.load(file)


if len(js60Co) != len(js152Eu):
    print('Files do not contain the same fold')
    sys.exit()


js_new=[]
for i in range(0,len(js152Eu)):
    js_element = {}
    js_element['fold'] = i+1
    js_element['60Co'] = js60Co[i]['60Co']
    js_element['152Eu'] = js152Eu[i]['152Eu']
    js_new.append(js_element)

with open('merged.json','w') as ofile:
    js_tab = json.dump(js_new, ofile, indent=3, default=str)

palette_size = len(js_new)+2
cmap1 = plt.cm.plasma  # You can use other colormaps like 'viridis', 'plasma', 'cividis', etc.
my_colors1 = [cmap1(i / palette_size) for i in range(palette_size)]

cmap2 = plt.cm.cividis  # You can use other colormaps like 'viridis', 'plasma', 'cividis', etc.
my_colors2 = [cmap2(i / palette_size) for i in range(palette_size)]


color60Co = []
color152Eu = []
colors = {}
# ColorList = []

for i in range (1,5):
    color1 = my_colors1[i]
    color2 = my_colors2[i]
    color60Co.append(color1)
    color152Eu.append(color2)

colors['152Eu'] = color152Eu
colors['60Co'] = color60Co

index = 0
for index in range (0,len(js_new)):
    for source in list_of_sources:
        if source in js_new[index]:
            for el in js_new[index][source]:
                plt.figure(0)
                plt.scatter(x=float(el), y=js_new[index][source][el]['eff'], color = colors[source][index])
                plt.figure(1)
                plt.scatter(x=float(el), y=js_new[index][source][el]['res'], color=colors[source][index])
                if index > 0:
                    plt.figure(2)
                    plt.scatter(x=float(el), y=js_new[index][source][el]['addback'], color=colors[source][index])
        # print( float(el), js_new[index]['60Co'][el]['eff'])
            plt.figure(0)
            plt.scatter(x=float(el), y=js_new[index][source][el]['eff'], color = colors[source][index], label='Fold {}'.format(index+1))
            plt.legend(loc='upper right', fontsize='medium', shadow=False, ncol=2)
            plt.figure(1)
            plt.scatter(x=float(el), y=js_new[index][source][el]['res'], color=colors[source][index], label='Fold {}'.format(index + 1))
            plt.legend(loc='upper right', fontsize='medium', shadow=False, ncol=2)

            if index > 0:
                plt.figure(2)
                plt.scatter(x=float(el), y=js_new[index][source][el]['addback'], color=colors[source][index], label='Fold {}'.format(index + 1))
                plt.legend(loc='upper left', fontsize='medium', shadow=False, ncol=2)

            # plt.figure(1)
    # plt.scatter(x=1, y=key[source][element]["res"], color=cc, label='Fold {}'.format(key['fold']))
    # plt.legend(loc='upper left', fontsize='medium', shadow=False)

plt.figure(0)
# plt.xticks(np.arange(0, 1500, 100))
plt.title('Efficiency {}'.format(meta_data))
plt.xlabel('E$\gamma$')
plt.ylabel('Efficiency, %')
file_name_ab = 'fold_eff_all.{}'.format(opt)
plt.savefig(save_results_to + file_name_ab)
plt.close()

plt.figure(1)
# plt.xticks(np.arange(0, 1500, 100))
plt.title('Resolution {}' .format(meta_data))
plt.xlabel('E$\gamma$')
plt.ylabel('Resolution, keV')
file_name_ab = 'fold_res_all.{}'.format(opt)
plt.savefig(save_results_to + file_name_ab)
plt.close()

plt.figure(2)
# plt.xticks(np.arange(0, 1500, 100))
plt.title('Add Back Factor Fold {} '.format(meta_data))
plt.xlabel('E$\gamma$')
plt.ylabel('Add Back factor fold')
file_name_ab = 'fold_ab_all.{}'.format(opt)
plt.savefig(save_results_to + file_name_ab)
plt.close()



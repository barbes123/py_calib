#! /usr/bin/python3

from os.path import exists #check if file exists

import os
from time import process_time

import numpy as np
import matplotlib.pyplot as plt
import math, sys, os, json, subprocess
from pathlib import Path
from argparse import ArgumentParser
import inspect


ourpath = os.getenv('PY_CALIB')

import sys
sys.path.append(ourpath+'/lib')
from libLists import list_of_sources
from libLists import list_of_clovers
from libFitFunc import *
from libColorsAnsi import *
from utilities import json_oneline_lists


from sympy.printing.pretty.pretty_symbology import line_width


def MakeDir(path):
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
        print("The new directory {} is created!".format(path))

current_directory = os.getcwd()
datapath = '{}/'.format(current_directory)

save_results_to = '{}/figures/'.format(datapath)
MakeDir(save_results_to)

# list_of_clovers = {"CL29", "CL30", "CL31", "CL32", "CL33", "CL34", "CL35", "CL36", "HPGe", "SEG", "LaBr"}
# list_of_sources = {'60Co','60CoWeak', '152Eu','137Cs', '133Ba','22Na','54Mn'}
list_of_sources_presented = []
# list_of_cebr = {"CEBR1","CEBR2","CEBR3","CEBR4"}
list_of_data = {}
js_all =[]


import os
import json


def ReadSimEffData(run, ener1=100, ener2=10000):
    json_data = {}
    for energy in range(ener1, ener2 + 1, 100):
        file_path = f'run_{run}/fold_data_run_{run}_{energy}.txt'

        # print(f"Processing file: {file_path}")

        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                # Loop over each line in the file
                if energy not in json_data:
                    json_data[energy] = {}
                for line in file:
                    # Split the line into columns based on spaces (you may need to adjust if tabs are used)
                    columns = line.split()

                    # Get the first and 11th columns (index 0 and index 10 in a 0-indexed list)
                    if len(columns) >= 12:  # Ensure there are enough columns
                        foldID = int(columns[0])
                        eff = float(columns[11])
                        json_data[energy][foldID] = eff

        else:
            # print(f"File '{file_path}' does not exist for energy {energy}.")
            pass

    # Convert the dictionary to a JSON string after processing all energies
    json_output = json.dumps(json_data, indent=4)

    # Optionally, save the JSON data to a new file
    with open(f'sim_run_{run}.json', 'w') as json_file:
        json_file.write(json_output)

    # Print the JSON to the console
    # print(json_output)

    # Return the final data
    return json_data





def ReadSimData(filename, colx, coly):
    energy = []
    ratio = []

    with open(filename, 'r') as file:
        for line in file:
            # Split each line into words
            parts = line.split()
            # Check if the line starts with "Energy" (assuming the format is consistent)
            if parts[0] == 'Energy':
                energy_value = int(parts[colx])  # The Energy value is the second item
                ratio_value = float(parts[coly])  # The ratio (or measurement) is the 9th item
                energy.append(energy_value)
                ratio.append(ratio_value)

    return energy, ratio


def MergeJsonData(js60Co=None, js152Eu=None, js22Na=None, js54Mn=None, js137Cs=None, js56Co=None, js133Ba=None, meta_data=''):
# def MergeJsonData(js60Co, js152Eu, meta_data):
    js_new=[]
    # print(len(js152Eu))
    # print(js152Eu)
    max_fold = 4

    # for i in range(0,len(js152Eu)):
    for i in range(0,max_fold):
        js_element = {}
        js_element['fold'] = i+1
        try:
            js_element['60Co'] = js60Co[i]['60Co']
        except:
            pass
        try:
            js_element['152Eu'] = js152Eu[i]['152Eu']
        except:
            pass
        try:
            js_element['22Na'] = js22Na[i]['22Na']
        except:
            pass
        try:
            js_element['54Mn'] = js54Mn[i]['54Mn']
        except:
            pass
        try:
            js_element['137Cs'] = js137Cs[i]['137Cs']
        except:
            print(f'{RED}Data for 137Cs are not found that addback_* folder and addback_run.json is okay {RESET}')
            pass
        try:
            js_element['56Co'] = js56Co[i]['56Co']
        except:
            print(f'{RED}Data for 56Co are not found that addback_* folder and addback_run.json is okay {RESET}')
            pass
        try:
            js_element['133Ba'] = js133Ba[i]['133Ba']
        except:
            pass
        js_new.append(js_element)


    blCompactJSON = True
    if blCompactJSON:
        js_compact = json_oneline_lists(js_new, 4)
        with open('merged.json', 'w') as ofile:
            ofile.write(js_compact)
    else:
        with open('merged.json', 'w') as ofile:
            js_tab = json.dump(js_new, ofile, indent=3, default=str)


    # with open(f'merged.json','w') as ofile:
    #     js_tab = json.dump(js_new, ofile, indent=3, default=str)

    palette_size = len(js_new)+2
    cmap1 = plt.cm.plasma  # You can use other colormaps like 'viridis', 'plasma', 'cividis', etc.
    my_colors1 = [cmap1(i / palette_size) for i in range(palette_size)]

    cmap2 = plt.cm.cividis  # You can use other colormaps like 'viridis', 'plasma', 'cividis', etc.
    my_colors2 = [cmap2(i / palette_size) for i in range(palette_size)]

    cmap3 = plt.cm.Greys  # You can use other colormaps like 'viridis', 'plasma', 'cividis', etc.
    my_colors3 = [cmap3(i / palette_size) for i in range(palette_size)]

    cmap4 = plt.cm.Purples  # You can use other colormaps like 'viridis', 'plasma', 'cividis', 'inferno', 'magma', etc.
    my_colors4 = [cmap4(i / palette_size) for i in range(palette_size)]

    cmap5 = plt.cm.Oranges  # You can use other colormaps like 'viridis', 'plasma', 'cividis', 'inferno', 'magma', etc.
    my_colors5 = [cmap5(i / palette_size) for i in range(palette_size)]

    cmap6 = plt.cm.Reds  # You can use other colormaps like 'viridis', 'plasma', 'cividis', 'inferno', 'magma', etc.
    my_colors6 = [cmap6(i / palette_size) for i in range(palette_size)]


    cmap7 = plt.cm.Blues  # You can use other colormaps like 'viridis', 'plasma', 'cividis', 'inferno', 'magma', etc.
    my_colors7 = [cmap7(i / palette_size) for i in range(palette_size)]




    color60Co = []
    color152Eu = []
    color22Na = []
    color54Mn = []
    color137Cs = []
    color56Co = []
    color133Ba = []
    colors = {}

    for i in range (1,palette_size):
        color1 = my_colors1[i]
        color2 = my_colors2[i]
        color3 = my_colors3[i]
        color4 = my_colors4[i]
        color5 = my_colors5[i]
        color6 = my_colors6[i]
        color7 = my_colors7[i]
        color60Co.append(color1)
        color152Eu.append(color2)
        color22Na.append(color3)
        color54Mn.append(color4)
        color137Cs.append(color5)
        color133Ba.append(color6)
        color56Co.append(color7)

    colors['152Eu'] = color152Eu
    colors['60Co'] = color60Co
    colors['22Na'] = color22Na
    colors['54Mn'] = color54Mn
    colors['137Cs'] = color137Cs
    colors['133Ba'] = color133Ba
    colors['56Co'] = color56Co

    # print(js_new)
    index = 0
    for index in range (0,len(js_new)):
        PlotThisFold = True
        # print(len(plotTheseFolds))
        # sys.exit()
        if len(plotTheseFolds) > 0:
            PlotThisFold = False
            for ifold in plotTheseFolds:
                if index == ifold:
                    PlotThisFold = True
                    # print(ifold, index, PlotThisFold)
                    break
        if not PlotThisFold:
            continue
        for source in list_of_sources_presented:
            if source in js_new[index]:
                print(f'{BLUE} {source} {RESET}')


                for el in js_new[index][source]:
                    if source!='56Co':
                        plt.figure(0)
                        plt.scatter(x=float(el), y=js_new[index][source][el]['eff'][0], color = colors[source][index])
                        plt.errorbar(x=float(el), y=js_new[index][source][el]['eff'][0], yerr=js_new[index][source][el]['eff'][1], color=colors[source][index])
                    plt.figure(1)
                    plt.scatter(x=float(el), y=js_new[index][source][el]['res'][0], color=colors[source][index])
                    plt.errorbar(x=float(el), y=js_new[index][source][el]['res'][0],yerr=js_new[index][source][el]['res'][1], color=colors[source][index])
                    if index > 0:
                        plt.figure(2)
                        # uncomment for color dots
                        # plt.scatter(x=float(el), y=js_new[index][source][el]['addback'], color=colors[source][index])
                        # plt.errorbar(x=float(el), y=js_new[index][source][el]['addback'], yerr=js_new[index][source][el]["err_ab"], color=colors[source][index])
                        plt.scatter(x=float(el), y=js_new[index][source][el]['addback'][0], color='black')
                        plt.errorbar(x=float(el), y=js_new[index][source][el]['addback'][0], yerr=js_new[index][source][el]["addback"][1], color='black')
            # print( float(el), js_new[index]['60Co'][el]['eff'])
                if source != '56Co':
                    plt.figure(0)
                    plt.scatter(x=float(el), y=js_new[index][source][el]['eff'][0], color = colors[source][index], label=f'Fold {index+1} {source}')

                # plt.legend(loc='upper right', fontsize='medium', shadow=False, ncol=2)
                plt.figure(1)
                plt.scatter(x=float(el), y=js_new[index][source][el]['res'][0], color=colors[source][index], label=f'Fold {(index + 1)} {source}')
                # plt.legend(loc='upper right', fontsize='medium', shadow=False, ncol=2)
                save_plot_data_to_ascii(js_new,index,source,f'data_fold_{ifold}.dat')

                if index > 0:
                    plt.figure(2)
                    #uncomment for color dots
                    # plt.scatter(x=float(el), y=js_new[index][source][el]['addback'], color=colors[source][index], label='Fold {}'.format(index + 1))
                    plt.scatter(x=float(el), y=js_new[index][source][el]['addback'][0], color='black', label='Fold {}'.format(index + 1))
                # if index == 3:
                #     plt.figure(2)
                #     plt.scatter(x=energy, y=ab_sim, color='black', label='Fold {} simulations'.format(index + 1))
                    # plt.legend(loc='upper left', fontsize='medium', shadow=False, ncol=2)#uncomment to plot legend

                # plt.figure(1)
        # plt.scatter(x=1, y=key[source][element]["res"], color=cc, label='Fold {}'.format(key['fold']))
        # plt.legend(loc='upper left', fontsize='medium', shadow=False)




    if blFit:
        dataFull = read_data_for_fit(f'data_fold_{plotTheseFolds[0]}.dat')
        ener_short  = [value[1] for value in dataFull.values() if value[0] != '56Co']
        eff_short = [value[2] for value in dataFull.values() if value[0] != '56Co']
        ener_full = [value[1] for value in dataFull.values()]
        res_full = [value[3] for value in dataFull.values()]

        params, covariance = curve_fit(fitDebertin, ener_short, eff_short)
        a1f, a2f, a3f, a4f, a5f = params
        ener1 = np.linspace(min(ener_short), max(ener_short), 500)  # Generate 500 points for smoothness
        smooth_fit = fitDebertin(ener1, *params)  # Evaluate the fitted function on the generated points
        plt.figure(0)
        plt.plot(ener1, smooth_fit, color='green', linestyle='--', label='Debertin Fit')

        if blFitRes:
            # ener, eff, res = fit_data_from_file('data_fold_3.dat')
            init = (0.5, 5e-4, -8e-9)
            params, covariance = curve_fit(fitResolution, ener_full, res_full, p0=init)
            # print(params)
            ener1 = np.linspace(min(ener_full), max(ener_full), 500)  # Generate 500 points for smoothness
            smooth_fit_res = fitResolution(ener1, *params)  # Evaluate the fitted function
            plt.figure(1)
            plt.plot(ener1, smooth_fit_res, color='green', label='Fit Resolution')
            # plt.legend(loc='upper right')


    pltFold = plotTheseFolds[0] + 1 #images are done only for the first fold mentioned

    plt.figure(0)
    ax = plt.gca()
    line = ax.get_lines()[0]  # Get the first line in the plot
    max_y = max(line.get_ydata())
    plt.ylim(0, 1.5*max_y)





    plt.title('Efficiency {}'.format(meta_data))
    plt.xlabel('E$\gamma$')
    plt.ylabel('Efficiency, %')
    plt.legend(loc='upper right', fontsize='medium', shadow=False, ncol=2)




    file_name_eff = 'fold_eff_all_{}.{}'.format(pltFold, opt)
    plt.savefig(save_results_to + file_name_eff,dpi=300)
    plt.close()

    plt.figure(1)
    # plt.xticks(np.arange(0, 1500, 100))
    plt.title('Resolution {}' .format(meta_data))
    plt.xlabel('E$\gamma$')
    plt.ylabel('Resolution, keV')
    plt.legend(loc='upper left', fontsize='medium', shadow=False, ncol=2)
    file_name_res = 'fold_res_all_{}.{}'.format(pltFold, opt)
    # file_name_res = f'fold_res_all_{pltFold}.{opt}'
    plt.savefig(save_results_to + file_name_res, dpi=300)
    plt.close()

    plt.figure(2)
    # plt.xticks(np.arange(0, 1500, 100))
    # plt.title('Add Back Factor Fold {} '.format(meta_data))
    # plt.title('Add Back Factor Fold')#remove to allow automatic title
    plt.grid()
    plt.xlabel('E$\gamma$',fontsize=14)


    plt.tick_params(axis='both', labelsize=12)  # Increase tick label size to 12
    # plt.ylabel('Add Back factor fold')
    plt.ylim(0.8,2)
    # file_name_ab = f'fold_ab_all_{pltFold}.{opt}'
    file_name_ab = 'fold_eff_ab_{}.{}'.format(pltFold, opt)
    plt.savefig(save_results_to + file_name_ab, dpi=300)
    plt.close()

def main():
    meta = ''
    js60Co = None
    js152Eu = None
    js22Na = None
    js54Mn = None
    js137Cs = None
    js56Co = None
    js133Ba = None
    list_of_names = {}
    for el in list_of_data:
        # print(list_of_data[el])

        try:
            name = 'addback_run_{}_{}_eliadeS{}/addback_{}.json'.format(list_of_data[el][1],list_of_data[el][2],list_of_data[el][0],list_of_data[el][1])
            # meta = meta + 'run_' + list_of_data[el][1]+'_S'+ list_of_data[el][0] + '_' + el + ' '
            meta = meta + el + ' '
            list_of_names[el] = name
        except:
            continue


        print('{} file name: '.format(el), name)

        if el == '60Co':
            with open(name, 'r') as file:
                js60Co = json.load(file)
                list_of_sources_presented.append(el)
                js = {}
                js[el] = js60Co
                js_all.append(js)
        elif el == '152Eu':
            with open(name, 'r') as file:
                js152Eu = json.load(file)
                list_of_sources_presented.append(el)
                js = {}
                js[el] = js152Eu
                js_all.append(js)
        elif el == '22Na':
            with open(name, 'r') as file:
                js22Na = json.load(file)
                list_of_sources_presented.append(el)
                js = {}
                js[el] = js22Na
                js_all.append(js)
        elif el == '54Mn':
            with open(name, 'r') as file:
                js54Mn = json.load(file)
                list_of_sources_presented.append(el)
                js = {}
                js[el] = js54Mn
                js_all.append(js)
        elif el == '137Cs':
            with open(name, 'r') as file:
                js137Cs = json.load(file)
                list_of_sources_presented.append(el)
                js = {}
                js[el] = js137Cs
                js_all.append(js)
        if el == '56Co':
            with open(name, 'r') as file:
                js56Co = json.load(file)
                list_of_sources_presented.append(el)
                js = {}
                js[el] = js56Co
                js_all.append(js)
        if el == '133Ba':
            with open(name, 'r') as file:
                js133Ba = json.load(file)
                list_of_sources_presented.append(el)
                js = {}
                js[el] = js133Ba
                js_all.append(js)

    MergeJsonData(js60Co, js152Eu, js22Na, js54Mn, js137Cs, js56Co, js133Ba, meta)








if __name__ == "__main__":

    server = -1
    run = 100
    grType = 'jpg'
    prefix = 'sum_fold_1'
    vol = 999
    plotTheseFolds = {}
    plotFolds = {}
    AddSimul = False
    AddSimulEff = False
    list_of_data = {}
    parser = ArgumentParser()
    runnbr = -1
    blFit = True
    blFitRes = True
    fitFunc = 'deb'


    for el in list_of_sources:
        parser.add_argument('-{}'.format(el), '--data{}'.format(el), nargs='+', help='Data for {} server run vol'.format(el))

    # parser.add_argument("-folds", "--plotFolds",
    #                     dest="plotFolds", default=0, type=str,
    #                     help="Folds to be plotted, default {} - all".format(0))

    parser.add_argument("-folds", "--plotFolds",
                        dest="plotFolds", default=[3], type=int, nargs='+',
                        help="Folds to be plotted, default is all (0), can provide a list like 1 2 3, mind that fold1 corresponds to 0")

    parser.add_argument("-gr", "--graphic type: eps, jpg or none ",
                        dest="grType", default=grType, type=str, choices=('eps', 'jpeg', 'jpg', 'png', 'svg', 'svgz', 'tif', 'tiff', 'webp','none'),
                        # eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff, webp
                        help="Available graphic output: eps, jpeg, jpg, png, svg, svgz, tif, tiff, webp or none (no graphs); default = {}".format(grType))

    parser.add_argument("-prefix", "--prefix to the files to be analyzed",
                        dest="prefix", default=grType, type=str, help="Prefix for matrix (TH2) to be analyzed mDelila_raw or mDelila or ...".format(prefix))

    parser.add_argument("-sim", "--run from simul", type=int,
                        dest="runnbr", default=runnbr,
                        help="Run number from simul, default = {}".format(runnbr))

    parser.add_argument("-fit", "--fitting the efficiency",
                        dest="fitFunc", default=fitFunc, type=str,
                        choices=('deb','None'),
                        # eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff, webp
                        help="Available fit Debertin [deb], ...; default = {}".format(fitFunc))

    # parser.add_argument("-s", "--sim", dest="sim", action="store_true",
    #                     help="Activate simulation mode.")

    config = parser.parse_args()

    plotTheseFolds = config.plotFolds
    AddSimul = (config.runnbr > 0)
    blFit = (config.fitFunc != 'None')

    if AddSimul:
        # energy, ab_sim = ReadSimData('simul/add_back_all_run4.txt',1,17)
        # energy_sim, ab_sim = ReadSimData(f'simul/add_back_all_run{config.runnbr}.txt', 1, 17)

        ncol = 17
        selected_fold = plotTheseFolds[0]+1

        if selected_fold == 4:
            ncol = 17
        elif selected_fold == 3:
            ncol = 13
        elif selected_fold == 2:
            ncol = 9
        elif selected_fold == 1:
            ncol = 5
        # print(ncol, selected_fold)
        # sys.exit()

        energy_sim, ab_sim = ReadSimData(f'run_{config.runnbr}/add_back_all_run_{config.runnbr}.txt', 1, ncol)
        plt.figure(2)#add sim to addback
        # plt.grid()
        # plt.plot(energy, ab_sim, marker='', linestyle='-', color='gray', linewidth=1)
        plt.plot(energy_sim, ab_sim, marker='', linestyle='-', color='red', linewidth=1)
        # plt.title('Energy vs Simulated Addback')
        plt.savefig('figures/simulations_ab.{}'.format('jpg'), dpi=300)
        # plt.grid()
    if AddSimul:
        js_sim = ReadSimEffData(config.runnbr)
        plt.figure(0)#add sim to eff
        energy_levels = []
        efficiencies = []

        selected_fold = plotTheseFolds[0]+1

        # Loop through each energy level in the json_data
        for energy, folds in js_sim.items():
            # Check if the selected fold exists in the current energy level
            if selected_fold in folds:
                energy_levels.append(energy)  # Append the energy level
                efficiencies.append(folds[selected_fold])  # Append the efficiency for the selected fold

        # If no data for the selected fold, show a message
            # if not energy_levels:
            #     print(f"Fold {selected_fold} not found in the data.")
            #     return

        # Plotting the efficiency vs energy for the selected fold
        plt.plot(energy_levels, efficiencies, label=f'Fold {selected_fold} Sim Run {config.runnbr}')
        plt.savefig('figures/simulations_eff.{}'.format('jpg'),dpi=300)

        # Customize the plot
        plt.xlabel('Energy (keV)')
        plt.ylabel('Efficiency (%)')
        plt.title(f'Efficiency for Fold {selected_fold} Across Different Energy Levels')
        plt.legend(loc='upper right')
        plt.grid(True)

    if blFit:
        # fname = f'data_fold_{plotTheseFolds[0]+1}.dat'
        fname = f'data_fold_{plotTheseFolds[0]}.dat'
        if os.path.exists(fname):
            # If it exists, delete the file
            os.remove(fname)
            print(f"The file {fname} has been deleted.")
        else:
            print(f"The file {fname} does not exist.")



    if len(config.grType) > 0:
        opt = config.grType
    else:
        opt = 'jpg'

    for el in list_of_sources:
        if el == '60Co':
            try:
                list_of_data[el] = config.data60Co
            except:
                pass
        elif el == '152Eu':
            try:
                list_of_data[el] = config.data152Eu
            except:
                pass
        elif el == '22Na':
            try:
                list_of_data[el] = config.data22Na
            except:
                pass
        elif el == '54Mn':
            try:
                list_of_data[el] = config.data54Mn
            except:
                pass
        elif el == '137Cs':
            try:
                list_of_data[el] = config.data137Cs
            except:
                pass
        elif el == '56Co':
            try:
                list_of_data[el] = config.data56Co
            except:
                pass
        elif el == '133Ba':
            try:
                list_of_data[el] = config.data133Ba
            except:
                pass
    main()



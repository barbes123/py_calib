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


from sympy.printing.pretty.pretty_symbology import line_width


def MakeDir(path):
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
        print("The new directory {} is created!".format(path))

# opt = 'jpg'

# meta_data = ''
# opt = 'eps'

# ourpath = '/data10/live/IT/py_calib'


current_directory = os.getcwd()
datapath = '{}/'.format(current_directory)

save_results_to = '{}/figures/'.format(datapath)
MakeDir(save_results_to)

# from ../lib/libLists import list_of_sources


# list_of_clovers = {"CL29", "CL30", "CL31", "CL32", "CL33", "CL34", "CL35", "CL36", "HPGe", "SEG", "LaBr"}
# list_of_sources = {'60Co','60CoWeak', '152Eu','137Cs', '133Ba','22Na','54Mn'}
list_of_sources_presented = []
list_of_cebr = {"CEBR1","CEBR2","CEBR3","CEBR4"}
list_of_data = {}
js_all =[]


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


def MergeJsonData(js60Co=None, js152Eu=None, js22Na=None, js54Mn=None, js137Cs=None, js56Co=None, meta_data=''):
# def MergeJsonData(js60Co, js152Eu, meta_data):
    js_new=[]
    for i in range(0,len(js152Eu)):
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
            print('22Na no file')
        try:
            js_element['54Mn'] = js54Mn[i]['54Mn']
        except:
            print('54Mn no file')
            pass
        try:
            js_element['137Cs'] = js137Cs[i]['137Cs']
        except:
            print('137Cs no file')
            pass
        try:
            js_element['56Co'] = js56Co[i]['56Co']
        except:
            print('56Co no file')
            pass
        js_new.append(js_element)

    with open('merged.json','w') as ofile:
        js_tab = json.dump(js_new, ofile, indent=3, default=str)

    palette_size = len(js_new)+2
    cmap1 = plt.cm.plasma  # You can use other colormaps like 'viridis', 'plasma', 'cividis', etc.
    my_colors1 = [cmap1(i / palette_size) for i in range(palette_size)]

    cmap2 = plt.cm.cividis  # You can use other colormaps like 'viridis', 'plasma', 'cividis', etc.
    my_colors2 = [cmap2(i / palette_size) for i in range(palette_size)]

    cmap3 = plt.cm.viridis  # You can use other colormaps like 'viridis', 'plasma', 'cividis', etc.
    my_colors3 = [cmap3(i / palette_size) for i in range(palette_size)]

    cmap4 = plt.cm.inferno  # You can use other colormaps like 'viridis', 'plasma', 'cividis', 'inferno', 'magma', etc.
    my_colors4 = [cmap3(i / palette_size) for i in range(palette_size)]




    color60Co = []
    color152Eu = []
    color22Na = []
    color54Mn = []
    color137Cs = []
    color56Co = []
    colors = {}

    for i in range (1,5):
        color1 = my_colors1[i]
        color2 = my_colors2[i]
        color3 = my_colors3[i]
        color4 = my_colors4[i]
        color60Co.append(color1)
        color152Eu.append(color2)
        color22Na.append(color3)
        color54Mn.append(color1)
        color137Cs.append(color1)
        color56Co.append(color4)

    colors['152Eu'] = color152Eu
    colors['60Co'] = color60Co
    colors['22Na'] = color22Na
    colors['54Mn'] = color54Mn
    colors['137Cs'] = color137Cs
    colors['56Co'] = color56Co

    index = 0
    for index in range (0,len(js_new)):
        PlotThisFold = True
        # print(len(plotTheseFolds))
        # sys.exit()
        if len(plotTheseFolds) > 0:
            PlotThisFold = False
            for el in plotTheseFolds:
                if index == el:
                    PlotThisFold = True
                    # print(el, index, PlotThisFold)
                    break
        if not PlotThisFold:
            continue
        # if index <= 2:
        #     continue
        for source in list_of_sources:
            if source in js_new[index]:
                for el in js_new[index][source]:
                    plt.figure(0)
                    plt.scatter(x=float(el), y=js_new[index][source][el]['eff'], color = colors[source][index])
                    plt.figure(1)
                    plt.scatter(x=float(el), y=js_new[index][source][el]['res'], color=colors[source][index])
                    if index > 0:
                        plt.figure(2)
                        # uncomment for color dots
                        # plt.scatter(x=float(el), y=js_new[index][source][el]['addback'], color=colors[source][index])
                        # plt.errorbar(x=float(el), y=js_new[index][source][el]['addback'], yerr=js_new[index][source][el]["err_ab"], color=colors[source][index])
                        plt.scatter(x=float(el), y=js_new[index][source][el]['addback'], color='black')
                        plt.errorbar(x=float(el), y=js_new[index][source][el]['addback'], yerr=js_new[index][source][el]["err_ab"] , color='black')
            # print( float(el), js_new[index]['60Co'][el]['eff'])
                plt.figure(0)
                plt.scatter(x=float(el), y=js_new[index][source][el]['eff'], color = colors[source][index], label='Fold {}'.format(index+1))
                plt.legend(loc='upper right', fontsize='medium', shadow=False, ncol=2)
                plt.figure(1)
                plt.scatter(x=float(el), y=js_new[index][source][el]['res'], color=colors[source][index], label='Fold {}'.format(index + 1))
                plt.legend(loc='upper right', fontsize='medium', shadow=False, ncol=2)

                if index > 0:
                    plt.figure(2)
                    #uncomment for color dots
                    # plt.scatter(x=float(el), y=js_new[index][source][el]['addback'], color=colors[source][index], label='Fold {}'.format(index + 1))
                    plt.scatter(x=float(el), y=js_new[index][source][el]['addback'], color='black',
                                label='Fold {}'.format(index + 1))
                # if index == 3:
                #     plt.figure(2)
                #     plt.scatter(x=energy, y=ab_sim, color='black', label='Fold {} simulations'.format(index + 1))
                    # plt.legend(loc='upper left', fontsize='medium', shadow=False, ncol=2)#uncomment to plot legend

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
    # plt.title('Add Back Factor Fold {} '.format(meta_data))
    # plt.title('Add Back Factor Fold')#remove to allow automatic title
    plt.grid()
    plt.xlabel('E$\gamma$',fontsize=14)


    plt.tick_params(axis='both', labelsize=12)  # Increase tick label size to 12
    # plt.ylabel('Add Back factor fold')
    plt.ylim(0.8,2)
    file_name_ab = 'fold_ab_all.{}'.format(opt)
    plt.savefig(save_results_to + file_name_ab)
    plt.close()

def main():
    meta = ''
    js60Co = None
    js152Eu = None
    js22Na = None
    js137Cs = None
    js56Co = None
    list_of_names = {}
    for el in list_of_data:
        # print(list_of_data[el])
        name = 'addback_run_{}_{}_eliadeS{}/addback_{}.json'.format(list_of_data[el][1],list_of_data[el][2],list_of_data[el][0],list_of_data[el][1])
        meta = meta + 'run_' + list_of_data[el][1]+'_S'+ list_of_data[el][0] + '_' + el + ' '
        list_of_names[el] = name

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

    MergeJsonData(js60Co, js152Eu, js22Na, js54Mn, js137Cs, js56Co, meta)

if __name__ == "__main__":

    server = -1
    run = 100
    grType = 'jpg'
    prefix = 'sum_fold_1'
    vol = 999
    plotTheseFolds = {}
    plotFolds = {}
    AddSimul = False
    list_of_data = {}
    parser = ArgumentParser()

    for el in list_of_sources:
        parser.add_argument('-{}'.format(el), '--data{}'.format(el), nargs='+', help='Data for {} server run vol'.format(el))

    # parser.add_argument("-folds", "--plotFolds",
    #                     dest="plotFolds", default=0, type=str,
    #                     help="Folds to be plotted, default {} - all".format(0))

    parser.add_argument("-folds", "--plotFolds",
                        dest="plotFolds", default=[], type=int, nargs='+',
                        help="Folds to be plotted, default is all (0), can provide a list like 1 2 3, mind that fold1 corresponds to 0")

    parser.add_argument("-gr", "--graphic type: eps, jpg or none ",
                        dest="grType", default=grType, type=str, choices=('eps', 'jpeg', 'jpg', 'png', 'svg', 'svgz', 'tif', 'tiff', 'webp','none'),
                        # eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff, webp
                        help="Available graphic output: eps, jpeg, jpg, png, svg, svgz, tif, tiff, webp or none (no graphs); default = {}".format(grType))
    parser.add_argument("-prefix", "--prefix to the files to be analyzed",
                        dest="prefix", default=grType, type=str, help="Prefix for matrix (TH2) to be analyzed mDelila_raw or mDelila or ...".format(prefix))

    parser.add_argument("-s", "--sim", dest="sim", action="store_true",
                        help="Activate simulation mode.")

    config = parser.parse_args()

    plotTheseFolds = config.plotFolds
    AddSimul = config.sim

    if AddSimul:
        energy, ab_sim = ReadSimData('simul/add_back_all_run4.txt',1,17)
        energy5, ab_sim5 = ReadSimData('simul/add_back_all_run5.txt', 1, 17)
        plt.figure(2)
        # plt.grid()
        # plt.plot(energy, ab_sim, marker='', linestyle='-', color='gray', linewidth=1)
        plt.plot(energy5, ab_sim5, marker='', linestyle='-', color='red', linewidth=1)
        # plt.title('Energy vs Simulated Addback')
        plt.savefig('figures/simulations.{}'.format('jpg'))
        # plt.grid()



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
    main()

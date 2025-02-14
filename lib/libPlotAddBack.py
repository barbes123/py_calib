import json
import sys

import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from matplotlib import interactive
import numpy as np
import os
import matplotlib.colors as mcolors
from random import choice
from libColorsAnsi import *

opt = 'jpg'
ourpath = os.getenv('PY_CALIB')

current_directory = os.getcwd()
datapath = '{}/'.format(current_directory)


global save_results_to
save_results_to = '{}figures/'.format(datapath)
title_clover = ''
from libLists import list_of_sources

#res and eff vs ener for each domain


def MakeDir(path):
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
        print("The new directory {} is created!".format(path))


# def PlotJsonFold(data, gammatab, source, my_det_type, opt='eps'):
def PlotJsonFold(data, gammatab, source, pars):
    print('<<<<< I am in PlotJsonFold >>>>>')
    MakeDir(save_results_to)
    opt=pars.grType
    dpi=pars.dpi
    meta_data='run_{}_eliaseS{}'.format(pars.runnbr,pars.server)
    print(meta_data)

    #Plot PT
    plt.figure(0)
    try:
        for key in data:
            plt.scatter(x=key["fold"], y=key["PT"][0], color='red')
            plt.errorbar(x=key["fold"], y=key["PT"][0], yerr=key['PT'][1], color='red', fmt='o', capsize=5)
            # print(f'{GREEN}PT vs Fold plot OK {RESET}')
    except:
        print(f'{RED}PT vs Fold FAILED {RESET}')
        pass

    # Plotting Resolution, Eff, AddBack vs Fold
    for key in data:
        for gammakey in list_of_sources:  # browse through the list of sources
            if source == gammakey:  # if our source is in the list
                for element in gammatab[source]["gammas"]:  # for each gamma energy of the source
                    plot_color = "k"
                    with open('{}/json/gamma_set.json'.format(ourpath), 'r') as jason_file:
                        gammaset = json.load(jason_file)
                        plot_color = gammaset[source]['gammas'][element]  # using different colors for each energy

                    plt.figure(1)  # efficiency plot
                    try:
                        plt.scatter(x=key["fold"], y=key[source][element]["eff"][0], color=plot_color, label=f"{element}")
                        plt.errorbar(x=key["fold"], y=key[source][element]["eff"][0], yerr=key[source][element]["eff"][1], fmt='o', color=plot_color, ecolor=plot_color, capsize=5)
                    except:
                        print(f'{RED}Fold efficiency Plot for {element} keV FAILED{RESET}')
                        pass
                        # continue  # print("Energy {} missing from domain {}".format(key[source][element], key["domain"]))
                    plt.figure(2)  # resolution plot
                    try:
                        plt.scatter(x=key["fold"], y=key[source][element]["res"][0], color=plot_color, label=f"{element}")
                        plt.errorbar(x=key["fold"], y=key[source][element]["res"][0],yerr=key[source][element]["res"][1], fmt='o', color=plot_color, ecolor=plot_color, capsize=5)
                    except:
                        print(f'{RED}Fold resolution Plot for {element} keV line FAILED {RESET}')
                        pass
                        # continue  # print("Energy {} missing from domain {}".format(key[source][element], key["domain"]))

                    plt.figure(3)  # addback plot
                    try:
                        plt.scatter(x=key["fold"], y=key[source][element]["addback"][0], color=plot_color, label=f"{element}")
                        plt.errorbar(x=key["fold"], y=key[source][element]["addback"][0], yerr=key[source][element]["addback"][1], fmt='o', color=plot_color, ecolor=plot_color, capsize=5)
                    except:
                        print(f'{RED}Fold addback Plot for {element} keV FAILED{RESET}')
                        pass
                    #     # continue  # print("Energy {} missing from domain {}".format(key[source][element], key["domain"]))

    #Plot Res, Eff,  AddBack vs Eg
    palette_size = len(data)+1
    cmap = plt.cm.cividis  # You can use other colormaps like 'viridis', 'plasma', 'cividis', etc.
    my_colors = [cmap(i / palette_size) for i in range(palette_size)]

    Nfold = 1;
    for key in data:
        for gammakey in list_of_sources:  # browse through the list of sources
            if source == gammakey:  # if our source is in the list
                for element in gammatab[source]["gammas"]:  # for each gamma energy of the source
                    # Nfold = 10+key['fold']
                    # #individual plots
                    # plt.figure(10+key['fold'])
                    # try:
                    #     # plot_color = gammaset[source]['gammas'][element]
                    #     plt.scatter(x=float(element), y=key[source][element]["addback"])
                    # except:
                    #     print('Addback vs Energy Plot failed')
                    #     continue
                    try:
                        cc = my_colors[key['fold']]
                    except:
                        cc = 'black'
                    # one plots for all Folds
                    plt.figure(7)
                    try:
                        plt.scatter(x=float(element), y=key[source][element]["res"][0], color=cc)
                        plt.errorbar(x=float(element), y=key[source][element]["res"][0], yerr=key[source][element]["res"][1], color=cc, fmt='o', capsize=5)
                    except:
                        print(f'{RED}Resolution vs Energy Plot All for {element} keV FAILED {RESET}')
                        continue
                    plt.figure(6)
                    try:
                        plt.scatter(x=float(element), y=key[source][element]["eff"][0], color=cc)
                        plt.errorbar(x=float(element), y=key[source][element]["eff"][0], yerr=key[source][element]["eff"][1], color=cc, fmt='o', capsize=5)
                    except:
                        print('Eff vs Energy Plot All failed')
                        continue
                    if key['fold'] == 1:
                        continue
                    plt.figure(5)
                    try:
                        plt.scatter(x=float(element), y=key[source][element]["addback"][0],color=cc)
                        plt.errorbar(x=float(element), y=key[source][element]["addback"][0], yerr=key[source][element]["addback"][1], color=cc, fmt='o', capsize=5)
                    except:
                        print('Addback vs Energy Plot All failed')
                        continue
        if key['fold'] > 1:
            try:
                plt.figure(5)
                plt.scatter(x=float(element), y=key[source][element]["addback"][0], color=cc, label='Fold {}'.format(key['fold']))
                plt.legend(loc='upper left', fontsize='medium', shadow=False)
            except:
                print(f'{RED}AddBack plot is not updated. Probably becase fold1 data are missing.{RESET}')
                pass
        plt.figure(6)
        plt.scatter(x=float(element), y=key[source][element]["eff"][0], color=cc,label='Fold {}'.format(key['fold']))
        plt.legend(loc='upper left', fontsize='medium', shadow=False)
        plt.figure(7)
        plt.scatter(x=float(element), y=key[source][element]["res"][0], color=cc, label='Fold {}'.format(key['fold']))
        plt.legend(loc='upper left', fontsize='medium', shadow=False)

        plt.figure(0)
        plt.title(f'Peak To Total for Fold Spectra')
        plt.xlabel('Fold')
        plt.ylabel('PT')
        file_name_pt = 'fold_{}_peaktotal.{}'.format(key["fold"], opt)
        plt.savefig(save_results_to + file_name_pt, dpi = dpi )
        plt.close()

        plt.figure(1)
        plt.title(f'Efficiency Fold Spectra')
        plt.xlabel('Fold')
        plt.ylabel('Efficiency, %')
        file_name_eff = 'fold_{}_eff.{}'.format(key["fold"], opt)
        plt.savefig(save_results_to + file_name_eff, dpi = dpi)
        plt.close()

        plt.figure(2)
        plt.title(f'Resolution for Fold Spectra')
        plt.xlabel('Fold')
        plt.ylabel('Resolution, keV')
        file_name_res = 'fold_{}_res.{}'.format(key["fold"], opt)
        plt.savefig(save_results_to + file_name_res, dpi = dpi)
        plt.close()

        plt.figure(3)
        plt.title(f'Add Back Factor')
        plt.xlabel('Fold')
        plt.ylabel('Add Back factor')
        file_name_ab = 'fold_{}_ab.{}'.format(key["fold"], opt)
        plt.savefig(save_results_to + file_name_ab, dpi = dpi)
        plt.close()

        plt.figure(5)
        # plt.xticks(np.arange(0, 1500, 100))
        plt.title('Add Back Factor Fold {} {}'.format(meta_data, source))
        plt.xlabel('E$\gamma$')
        plt.ylabel('Add Back factor fold')
        file_name_ab = 'fold_ab_all.{}'.format(opt)
        plt.savefig(save_results_to + file_name_ab, dpi = dpi)
        plt.close()

        plt.figure(6)
        # plt.xticks(np.arange(0, 1500, 100))
        plt.title('Efficiency {} {}'.format(meta_data, source))
        plt.xlabel('E$\gamma$')
        plt.ylabel('Efficiency, %')
        file_name_ab = 'fold_eff_all.{}'.format(opt)
        plt.savefig(save_results_to + file_name_ab, dpi = dpi)
        plt.close()

        plt.figure(7)
        # plt.xticks(np.arange(0, 1500, 100))
        plt.title('Resolution {} {}'.format(meta_data, source))
        plt.xlabel('E$\gamma$')
        plt.ylabel('Resolution, keV')
        file_name_ab = 'fold_res_all.{}'.format(opt)
        plt.savefig(save_results_to + file_name_ab, dpi = dpi)
        plt.close()


    # for fold in range (11,Nfold+1):
    #     plt.figure(fold)
    #     # plt.xticks(np.arange(0, 1500, 100))
    #     plt.title('Add Back Factor Fold = {}'.format(fold-10))
    #     plt.xlabel('Eg')
    #     plt.ylabel('Add Back factor fold')
    #     file_name_ab = 'fold_{}_ab.{}'.format(fold, opt)
    #     plt.savefig(save_results_to + file_name_ab)
    #     plt.close()


    print('Finished Fold graphs')

    return True
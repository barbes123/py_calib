import json
import sys

import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from matplotlib import interactive
import numpy as np
import os
import matplotlib.colors as mcolors
from random import choice

opt = 'jpg'
# opt = 'eps'

# ourpath = '/data10/live/IT/py_calib'
ourpath = os.getenv('PY_CALIB')

current_directory = os.getcwd()
datapath = '{}/'.format(current_directory)


global save_results_to
# save_results_to = '/home/rmiron/Desktop/dir/python_exercises/calibrations/figures/'
save_results_to = '{}figures/'.format(datapath)
title_clover = ''
# list_of_clovers = {"CL29", "CL30", "CL31", "CL32", "CL33", "CL34", "CL35", "CL36", "HPGe", "SEG", "LaBr"}
# list_of_sources = {'60Co','60CoWeak', '152Eu','137Cs', '133Ba'}
# list_of_cebr = {"CEBR1","CEBR2","CEBR3","CEBR4"}
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
    meta_data='run_{}_eliaseS{}'.format(pars.runnbr,pars.server)
    print(meta_data)

    plt.figure(0)
    for key in data:
        plt.scatter(x=key["fold"], y=key["PT"], color='red')

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
                        plt.scatter(x=key["fold"], y=key[source][element]["eff"], color=plot_color,
                                    label=f"{element}")
                        plt.errorbar(x=key["fold"], y=key[source][element]["eff"],
                                     yerr=key[source][element]["err_eff"], fmt='o', color=plot_color,
                                     ecolor=plot_color, capsize=5)
                    except:
                        print('Fold efficiency Plot failed')
                        continue  # print("Energy {} missing from domain {}".format(key[source][element], key["domain"]))
                    plt.figure(2)  # resolution plot
                    try:
                        plt.scatter(x=key["fold"], y=key[source][element]["res"], color=plot_color,
                                    label=f"{element}")
                        plt.errorbar(x=key["fold"], y=key[source][element]["res"],
                                     yerr=key[source][element]["err_res"], fmt='o', color=plot_color,
                                     ecolor=plot_color, capsize=5)
                    except:
                        print('Fold resolution Plot failed')
                        continue  # print("Energy {} missing from domain {}".format(key[source][element], key["domain"]))

                    plt.figure(3)  # resolution plot
                    try:
                        plt.scatter(x=key["fold"], y=key[source][element]["addback"], color=plot_color,
                                    label=f"{element}")
                        # plt.errorbar(x=key["fold"], y=key[source][element]["addback"],
                        #              yerr=key[source][element]["err_ab"], fmt='o', color=plot_color,
                        #              ecolor=plot_color, capsize=5)
                    except:
                        print('Fold addback Plot failed')
                        continue  # print("Energy {} missing from domain {}".format(key[source][element], key["domain"]))

    plt.figure(1)
    plt.title(f'Efficiency Fold Spectra')
    plt.xlabel('Fold')
    plt.ylabel('Efficiency, %')
    file_name_eff = 'fold_{}_eff.{}'.format(key["fold"], opt)
    plt.savefig(save_results_to + file_name_eff)
    plt.close()

    plt.figure(2)
    plt.title(f'Resolution for Fold Spectra')
    plt.xlabel('Fold')
    plt.ylabel('Resolution, keV')
    file_name_res = 'fold_{}_res.{}'.format(key["fold"], opt)
    plt.savefig(save_results_to + file_name_res)
    plt.close()

    plt.figure(3)
    plt.title(f'Add Back Factor')
    plt.xlabel('Fold')
    plt.ylabel('Add Back factor')
    file_name_ab = 'fold_{}_ab.{}'.format(key["fold"], opt)
    plt.savefig(save_results_to + file_name_ab)
    plt.close()

    #Plot AB(Eg)
    palette_size = len(data)+1
    cmap = plt.cm.cividis  # You can use other colormaps like 'viridis', 'plasma', 'cividis', etc.
    my_colors = [cmap(i / palette_size) for i in range(palette_size)]

    # Nfold = 1;
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
                        plt.scatter(x=float(element), y=key[source][element]["res"], color=cc)
                    except:
                        print('Resolution vs Energy Plot All failed')
                        continue
                    plt.figure(6)
                    try:
                        plt.scatter(x=float(element), y=key[source][element]["eff"], color=cc)
                    except:
                        print('Eff vs Energy Plot All failed')
                        continue
                    if key['fold'] == 1:
                        continue
                    plt.figure(5)
                    try:
                        plt.scatter(x=float(element), y=key[source][element]["addback"],color=cc)
                    except:
                        print('Addback vs Energy Plot All failed')
                        continue
        if key['fold'] > 1:
            plt.figure(5)
            plt.scatter(x=float(element), y=key[source][element]["addback"], color=cc, label='Fold {}'.format(key['fold']))
            plt.legend(loc='upper left', fontsize='medium', shadow=False)
        plt.figure(6)
        plt.scatter(x=float(element), y=key[source][element]["eff"], color=cc,label='Fold {}'.format(key['fold']))
        plt.legend(loc='upper left', fontsize='medium', shadow=False)
        plt.figure(7)
        plt.scatter(x=float(element), y=key[source][element]["res"], color=cc, label='Fold {}'.format(key['fold']))
        plt.legend(loc='upper left', fontsize='medium', shadow=False)

    plt.figure(0)
    plt.title(f'Peak To Total for Fold Spectra')
    plt.xlabel('Fold')
    plt.ylabel('PT')
    file_name_pt = 'fold_{}_peaktotal.{}'.format(key["fold"], opt)
    plt.savefig(save_results_to + file_name_pt)
    plt.close()

    plt.figure(5)
    # plt.xticks(np.arange(0, 1500, 100))
    plt.title('Add Back Factor Fold {} {}'.format(meta_data, source))
    plt.xlabel('E$\gamma$')
    plt.ylabel('Add Back factor fold')
    file_name_ab = 'fold_ab_all.{}'.format(opt)
    plt.savefig(save_results_to + file_name_ab)
    plt.close()

    plt.figure(6)
    # plt.xticks(np.arange(0, 1500, 100))
    plt.title('Efficiency {} {}'.format(meta_data, source))
    plt.xlabel('E$\gamma$')
    plt.ylabel('Efficiency, %')
    file_name_ab = 'fold_eff_all.{}'.format(opt)
    plt.savefig(save_results_to + file_name_ab)
    plt.close()

    plt.figure(7)
    # plt.xticks(np.arange(0, 1500, 100))
    plt.title('Resolution {} {}'.format(meta_data, source))
    plt.xlabel('E$\gamma$')
    plt.ylabel('Resolution, keV')
    file_name_ab = 'fold_res_all.{}'.format(opt)
    plt.savefig(save_results_to + file_name_ab)
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
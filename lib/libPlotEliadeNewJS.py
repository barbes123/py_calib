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
# dpi = 300

##################################################################
# This library contains functions to plot results from data analysis.
# PlotJsondom - graphs for indvidual domains
# PlotJsonclover -  plots for all domains of a clover
# PlotJsoncore - plots only core 1
# PlotCalibration - plots calibration curves
##################################################################

# ourpath = '/data10/live/IT/py_calib'
ourpath = os.getenv('PY_CALIB')

current_directory = os.getcwd()
datapath = '{}/'.format(current_directory)

global save_results_to
# save_results_to = '/home/rmiron/Desktop/dir/python_exercises/calibrations/figures/'
save_results_to = '{}figures/'.format(datapath)
title_clover = ''
from libLists import list_of_sources
from libLists import list_of_clovers
from libLists import list_of_cebr

# list_of_clovers = {"CL29", "CL30", "CL31", "CL32", "CL33", "CL34", "CL35", "CL36", "HPGe", "SEG", "LaBr"}
# list_of_sources = {'60Co', '60CoWeak', '152Eu', '137Cs', '133Ba'}
# list_of_cebr = {"CEBR1", "CEBR2", "CEBR3", "CEBR4"}


# res and eff vs ener for each domain


def MakeDir(path):
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
        print("The new directory {} is created!".format(path))


def FinXlimGeneric(key, js_lut):
    list_domains = []
    for el in js_lut:
        if el["serial"].rstrip(el["serial"][-1]) == key:
            list_domains.append(el['domain'])
    # print(min(list_domains), max(list_domains))
    return min(list_domains), max(list_domains)


def FindXlim(name):
    if name == "CL29":  # according to the current LUT
        plt.xlim([100., 141.])
    elif name == "CL30":
        plt.xlim([200., 241.])
    elif name == "CL32":
        plt.xlim([300., 341.])
    elif name == "CL35":
        plt.xlim([400., 441.])
    elif name == "CL34":
        plt.xlim([500., 541.])
    elif name == "CL36":
        plt.xlim([600., 641.])
    elif name == "CL33":
        plt.xlim([700., 741.])
    elif name == "CL31":
        plt.xlim([800., 841.])


# lutfile =  'LUT_ELIADE.json'

def find_domain(domain, lutfile):
    # print("found {}".format(domain))
    for item in lutfile:
        if item["domain"] == domain:
            return True
    return False


def PlotJsondom(data, gammatab, source, lutfile, opt='eps'):
    MakeDir(save_results_to)

    for i in data:
        # print('checking type {}'.format(type(i['domain'])))
        dom = i["domain"]

        if find_domain(dom, lutfile) == False:
            continue
        else:
            # print('F1 ', i)
            # print('F2 ', i['60CoWeak'])
            # print('F3 ', i['60CoWeak'].keys())
            plt.figure(1)
            for key in i[source].keys():
                val_res = i[source][key]["res"][0]
                err_res_rel = i[source][key]["res"][1]
                res = val_res
                err_res = val_res * err_res_rel

                val_eff = i[source][key]["eff"][0]
                err_eff_rel = i[source][key]["eff"][1]
                eff = val_eff
                err_eff = val_eff * err_eff_rel

                plt.errorbar(x=float(key), y=res, yerr=err_res, fmt='o', color='b', ecolor='red', capsize=5)
            if source == "60Co":
                plt.xlim([1000., 1400.])
            elif source == "152Eu":
                plt.xlim([100, 1500])
            plt.ylim([2, 8])
            if i["detType"] == 3:
                plt.ylim([30, 50])
                # print('plt.ylim([40,45])')
            plt.title(f'Resolution for domain {dom}')
            plt.xlabel('Energy (keV)')
            plt.ylabel('Resolution (keV)')
            plt.grid(color='black', linestyle='--', linewidth=0.5)
            # plt.legend()
            interactive(True)
            # plt.show()
            file_name1 = 'dom_{}_res.{}'.format(dom, opt)
            plt.savefig(save_results_to + file_name1)
            plt.close()
            plt.figure(2)
            for key in i[source].keys():
                val_eff = i[source][key]["eff"][0]
                err_eff_rel = i[source][key]["eff"][1]
                eff = val_eff
                err_eff = val_eff * err_eff_rel

                plt.errorbar(x=float(key), y=eff, yerr=err_eff, fmt='o', color='b', ecolor='red', capsize=5)

            if source == "60Co":
                plt.xlim([1000., 1400.])
            elif source == "152Eu":
                plt.xlim([100, 1500])

            if (i["detType"] == 1 or i["detType"] == 10):
                if (int(i["domain"]) == 1):
                    # plt.ylim([0,2.5])
                    plt.ylim([0, 1])
                else:
                    plt.ylim([0, 0.1])
            elif i["detType"] == 2:
                if i["domain"] == 2:
                    plt.ylim([0.0, .5])
                else:
                    plt.ylim([0, 0.01])
            # if (i["domain"==1] or i["domain"]==2):
            #     plt.ylim([0.5, 2])
            # plt.ylim([0.0001,0.00015])
            plt.title(f'Efficiency for domain {dom}')
            plt.xlabel('Energy (keV)')
            plt.ylabel('Efficiency (%)')
            plt.grid(color='black', linestyle='--', linewidth=0.5)
            # plt.legend()

            plt.show()
            file_name2 = 'dom_{}_eff.{}'.format(dom, opt)
            plt.savefig(save_results_to + file_name2)
            interactive(False)
            plt.close()
    print("Finished domain graphs")
    return True


def legend_without_duplicate_labels(figure):
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    figure.legend(by_label.values(), by_label.keys(), loc='upper right')


def PlotJsonclover(data, gammatab, source, my_det_type, lutfile, opt='eps'):
    print('<<<<< I am in PlotJsonclover >>>>>')
    MakeDir(save_results_to)

    for cloverkey in list_of_clovers:
        #print(f"\nProcessing clover {cloverkey}")
        blCloverFound = False
        peaks_found = {}  # Store peaks for debugging
        
        for key in data:
            # Add debug print to see what we're getting
            #print(f"Debug - key type: {type(key)}")
            if isinstance(key, str):
                continue  # Skip if key is a string
                
            try:
                if find_domain(key["domain"], lutfile) == False:
                    continue
                
                if key["serial"].rstrip(key["serial"][-1]) == cloverkey and key["detType"] == my_det_type:
                    blCloverFound = True
                    dom = key["domain"]
                    #print(f"\nDomain {dom}:")

                    # Peak-to-total plot
                    plt.figure(0)
                    detector_type = "Core" if my_det_type == 1 else "Segments" if my_det_type == 2 else "CeBr"
                    plt.title(f'Peak-to-Total Ratio vs Domain\n{cloverkey} ({detector_type}) - {source}')
                    plt.xlabel('Domain Number')
                    plt.ylabel('Peak-to-Total Ratio')
                    plt.grid(True, alpha=0.3)
                    
                    try:
                        plt.errorbar(x=dom, y=key["PT"][0], yerr=key["PT"][1], 
                                   fmt='o', color='b', ecolor='red', capsize=5,
                                   label='Peak-to-Total')  # Use consistent legend label
                    except:
                        plt.scatter(x=dom, y=key["PT"][0], color='b',
                                  label='Peak-to-Total')  # Use consistent legend label
                    
                    # Process peaks for this domain
                    if source in key:
                        for energy in key[source]:
                            try:
                                val_eff = key[source][energy]["eff"][0]
                                err_eff_rel = key[source][energy]["eff"][1]
                                eff = val_eff
                                err_eff = val_eff * err_eff_rel

                                val_res = key[source][energy]["res"][0]
                                err_res_rel = key[source][energy]["res"][1]
                                res = val_res
                                err_res = val_res * err_res_rel
                                
                                #print(f"  Peak {energy} keV:")
                                #print(f"    Efficiency: {eff:.6f} ± {err_eff:.6f}")
                                #print(f"    Resolution: {res:.2f} ± {err_res:.6f}")
                                
                                # Store for plotting
                                if energy not in peaks_found:
                                    peaks_found[energy] = {'eff': [], 'res': [], 'domains': []}
                                peaks_found[energy]['eff'].append((dom, eff, err_eff))
                                peaks_found[energy]['res'].append((dom, res, err_res))
                                peaks_found[energy]['domains'].append(dom)
                                
                            except KeyError as e:
                                print(f"  Missing data for peak {energy}: {str(e)}")
                                continue
            except (TypeError, KeyError) as e:
                print(f"Warning: Could not process entry: {e}")
                continue

        if blCloverFound:
            # Plot efficiency vs domain for each peak
            plt.figure(1)
            for energy, data in peaks_found.items():
                domains = np.array([x[0] for x in data['eff']])
                effs = np.array([x[1] for x in data['eff']])
                errs = np.array([x[2] for x in data['eff']])
                
                # Removed '-' from fmt='o-' to remove connecting lines
                plt.errorbar(domains, effs, yerr=errs, fmt='o', label=f'{energy} keV',
                           capsize=5, markersize=4)

            plt.title(f'Efficiency for clover {cloverkey}')
            plt.xlabel('Domain')
            plt.ylabel('Efficiency (%)')
            plt.grid(True, alpha=0.3)
            plt.legend(fontsize=8, loc='upper right')
            
            # Plot resolution vs domain for each peak
            plt.figure(2)
            for energy, data in peaks_found.items():
                domains = np.array([x[0] for x in data['res']])
                res = np.array([x[1] for x in data['res']])
                errs = np.array([x[2] for x in data['res']])
                
                # Removed '-' from fmt='o-' to remove connecting lines
                plt.errorbar(domains, res, yerr=errs, fmt='o', label=f'{energy} keV',
                           capsize=5, markersize=4)

            plt.title(f'Resolution for clover {cloverkey}')
            plt.xlabel('Domain')
            plt.ylabel('Resolution (keV)')
            plt.grid(True, alpha=0.3)
            plt.legend(fontsize=8, loc='upper right')

            # Set axis limits and save plots
            xmin, xmax = FinXlimGeneric(cloverkey, lutfile)
            for fig in [0, 1, 2]:
                plt.figure(fig)
                plt.xlim(xmin-1, xmax+2)
                
                if fig == 1:  # Efficiency
                    if my_det_type in [1, 10]:
                        plt.ylim([0, 0.006])
                    elif my_det_type == 2:
                        plt.ylim([0, 0.01])
                    plt.savefig(save_results_to + f'eliade_{cloverkey}_efficiency.{opt}')
                elif fig == 2:  # Resolution
                    plt.ylim([0, 3])
                    plt.savefig(save_results_to + f'eliade_{cloverkey}_{my_det_type}_resolution.{opt}')
                elif fig == 0:  # Peak-to-total
                    if my_det_type in [1, 10]:
                        plt.ylim([0.0, 0.1])
                    elif my_det_type == 2:
                        plt.ylim([0, 0.25])
                    # Use legend_without_duplicate_labels for consistency with other plots
                    #legend_without_duplicate_labels(plt)
                    plt.savefig(save_results_to + f'eliade_{cloverkey}_{my_det_type}_peaktotal.{opt}')
                plt.close()

    print('\nFinished CLOVER graphs')
    return True

def PlotJsoncore(data, gammatab, source, lutfile, detKey=1, opt='eps'):
    debugPlotJsoncore = False

    MakeDir(save_results_to)
    CloverName = ''
    # my_det_type=1
    for key in data:
        # clover=i["serial"]
        if find_domain(key["domain"], lutfile) == False:
            continue
        if key["detType"] != detKey:
            continue
        if key["domain"] < 100:
            continue
        if debugPlotJsoncore:
            print('key["domain"]', key["domain"])

        for gammakey in list_of_sources:
            if source == gammakey:
                for element in gammatab[source]["gammas"]:
                    plot_color = "k"
                    with open('{}/json/gamma_set.json'.format(ourpath), 'r') as jason_file:
                        gammaset = json.load(jason_file)
                        plot_color = gammaset[source]['gammas'][element]  # using different colors for each energy
                    plt.figure(1)  # efficiency plot
                    try:
                        CloverName = key["serial"][:len(key["serial"]) - 1]  # for plotting
                        val_eff = key[source][element]["eff"][0]
                        err_eff_rel = key[source][element]["eff"][1]
                        eff = val_eff
                        err_eff = val_eff * err_eff_rel

                        plt.scatter(x=key["domain"], y=eff, color=plot_color,
                                    label=f"{element}")
                        plt.errorbar(x=key["domain"], y=eff,
                                     yerr=err_eff, fmt='o', color=plot_color, ecolor=plot_color,
                                     capsize=5)
                        if debugPlotJsoncore:
                            print('CloverName', CloverName, 'key["domain"]', key["domain"],
                                  'key[source][element]["eff"]', key[source][element]["eff"], 'plot_color', plot_color)
                    except:
                        print('Warining in PlotJsoncore y=key[source][element]["eff"] plot')
                        continue
                    plt.figure(2)  # resolution plot
                    try:
                        val_res = key[source][element]["res"][0]
                        err_res_rel = key[source][element]["res"][1]
                        res = val_res
                        err_res = val_res * err_res_rel

                        plt.scatter(x=key["domain"], y=res, color=plot_color,
                                    label=f"{element}")
                        plt.errorbar(x=key["domain"], y=res,
                                     yerr=err_res, fmt='o', color=plot_color, ecolor=plot_color,
                                     capsize=5)
                        if debugPlotJsoncore:
                            print('key["domain"]', key["domain"], 'key[source][element]["res"]',
                                  key[source][element]["res"], 'plot_color', plot_color)
                    except:
                        print('Warining in PlotJsoncore y=key[source][element]["res"] plot')
                        continue
    # FindXlim(clover)
    plt.figure(1)
    # xmin, xmax = FinXlimGeneric(clover, lutfile)
    # xmin -= 1
    # xmax += 1
    plt.xlim(100, 841)
    # plt.xlim(xmin, xmax)
    plt.ylim([0, 0.1])
    # title_clover=clover.rstrip(clover[-1])#CL29 instead of CL29G
    # CloverName = key["serial"][:len(key["serial"])-1]
    plt.title('Efficiency for core {} {}'.format(CloverName, detKey))
    # print('CloverName',CloverName, key['detType'])
    plt.xlabel('Domain')
    plt.ylabel('Efficiency (%)')
    plt.grid(color='black', linestyle='--', linewidth=0.5)
    legend_without_duplicate_labels(plt)

    plt.figure(2)
    # FindXlim(clover)
    # plt.xlim(xmin, xmax)
    plt.xlim(100, 841)
    plt.ylim([1, 5])
    # title_clover=clover.rstrip(clover[-1])#CL29 instead of CL29G
    plt.title('Resolution for core {} det key {}'.format(CloverName, detKey))
    plt.xlabel('Domain')
    plt.ylabel('Resolution (keV)')
    plt.grid(color='black', linestyle='--', linewidth=0.5)
    legend_without_duplicate_labels(plt)

    plt.figure(1)
    file_name5 = 'eliade_efficiency_{}_core{}.{}'.format(CloverName, detKey, opt)
    plt.savefig(save_results_to + file_name5)
    plt.close()

    plt.figure(2)
    file_name6 = 'eliade_resolution_{}_core{}.{}'.format(CloverName, detKey, opt)
    plt.savefig(save_results_to + file_name6)
    plt.close()

    print("PlotJsoncore: Finished graphs for all core{} {}".format(CloverName, detKey))
    return True


def PlotCalibration(data, gammatab, source, lutfile, my_det_type=2, opt='eps'):
    if my_det_type == 3:
        # To plot CeBr calib please use PlotCalibrationCeBr instead of PlotCalibration
        return True

    MakeDir(save_results_to)
    number_of_our_colors = 30
    our_color_plate = iter(cm.rainbow(np.linspace(0, 1, number_of_our_colors)))
    # niter = 0

    for cloverkey in list_of_clovers:
        number_of_our_colors = 40
        our_color_plate = iter(cm.rainbow(np.linspace(0, 1, number_of_our_colors)))
        blCloverFound = False
        for key in data:  # Browse through data in output file
            if find_domain(key["domain"], lutfile) == False:
                continue
            if key['detType'] != my_det_type:  # or key['detType'] == 3:
                continue
            else:
                if key["serial"].rstrip(key["serial"][-1]) == cloverkey:  # check if clover is found
                    if key["pol_list"]:
                        if key["detType"] == my_det_type:  # check if the detector is the type that we want
                            blCloverFound = True
                            dom = key["domain"]

                            try:
                                current_color = next(our_color_plate)
                            except:
                                current_color = 'red'

                            plt.plot([1, 2000], [float(key["pol_list"][0]) + float(key["pol_list"][1]) * 1,
                                                 float(key["pol_list"][0]) + float(key["pol_list"][1]) * 2000],
                                     color=current_color, label=f"{dom}", linewidth=1)

                            for gammakey in list_of_sources:  # browse through the list of sources
                                if source == gammakey:  # if our source is in the list
                                    for element in gammatab[source]["gammas"]:  # for each gamma energy of the source
                                        try:
                                            plt.scatter(x=key[source][element]["pos_ch"], y=float(element),
                                                        color=current_color)
                                        except:
                                            print(
                                                'Warning skipping plot domain {} for gamma {} because not fitted'.format(
                                                    key['domain'], element))
                                            # continue
                            max_energy = max([float(i) for i in list(gammatab[source]["gammas"].keys())])

        if blCloverFound == True:
            delta = 200
            # print("calib")
            plt.xlim([0, 1200])
            plt.ylim([0, max_energy + delta])  # maximum energy from source + delta: [0; max+delta]
            plt.xlabel('Channel')
            plt.ylabel('Energy (keV)')
            plt.title(f'Calibration for clover {cloverkey} {my_det_type}')
            # legend_without_duplicate_labels(plt)
            plt.legend(ncol=3, loc='lower right', prop={'size': 6})
            # plt.show()
            file_name = 'eliade_{}_{}_calibration.{}'.format(cloverkey, my_det_type, opt)
            file_name = 'eliade_{}_{}_calibration.{}'.format(cloverkey, my_det_type, opt)
            plt.savefig(save_results_to + file_name)
            plt.close()
            blCloverFound = False
    return True


def PlotCalibrationCeBr(data, gammatab, source, lutfile, my_det_type=3, opt='eps'):
    print('<<<<< I am in PlotCalibrationCeBr >>>>>')
    MakeDir(save_results_to)
    number_of_our_colors = 30
    our_color_plate = iter(cm.rainbow(np.linspace(0, 1, number_of_our_colors)))
    colors = ["red", "orange", "yellow", "green", "blue", "indigo",
              "violet"]  # in parallel to the rinbow which does not work
    color_index = 0

    for cebrkey in list_of_cebr:
        # my_det_type=2
        number_of_our_colors = 4
        our_color_plate = iter(cm.rainbow(np.linspace(0, 1, number_of_our_colors)))
        blCeBrFound = False
        for key in data:  # Browse through data in output file
            if find_domain(key["domain"], lutfile) == False:
                continue
            if key['detType'] != my_det_type:
                continue
            else:
                if key["serial"] == cebrkey:  # check if cebr is found
                    # print('key[detType]', key['detType'], 'key["serial"]', key["serial"])
                    if key["pol_list"]:
                        # if key["detType"] == my_det_type:  # check if the detector is the type that we want
                        blCeBrFound = True
                        dom = key["domain"]
                        try:
                            current_color = next(our_color_plate)
                        except:
                            current_color = 'red'
                            print('Warning in PlotCalibrationCeBr same plot color will be used')
                        # print('current_color', current_color)
                        # print('colors[color_index]',colors[color_index], color_index)
                        color_index += 1
                        current_color = colors[color_index]

                        plt.plot([1, 16000], [float(key["pol_list"][0]) + float(key["pol_list"][1]) * 1,
                                              float(key["pol_list"][0]) + float(key["pol_list"][1]) * 16000],
                                 color=current_color, label=f"{dom}", linewidth=1)

                        for gammakey in list_of_sources:  # browse through the list of sources
                            if source == gammakey:  # if our source is in the list
                                for element in gammatab[source]["gammas"]:  # for each gamma energy of the source
                                    try:
                                        plt.scatter(x=key[source][element]["pos_ch"], y=float(element),
                                                    color=current_color)
                                    except:
                                        print(
                                            'Warning skipping plot domain {} for gamma {} because not fitted'.format(
                                                key['domain'], element))
                                        # continue
                        max_energy = max([float(i) for i in list(gammatab[source]["gammas"].keys())])

    if blCeBrFound == True:
        delta = 200
        # print("calib")
        plt.xlim([0, 16000])
        plt.ylim([0, max_energy + delta])  # maximum energy from source + delta: [0; max+delta]
        plt.xlabel('Channel')
        plt.ylabel('Energy (keV)')
        plt.title(f'Calibration for CeBr {cebrkey} {my_det_type}')
        # legend_without_duplicate_labels(plt)
        plt.legend(ncol=3, loc='lower right', prop={'size': 6})
        # plt.show()
        file_name = 'eliade_{}_calibration.{}'.format(my_det_type, opt)
        file_name = 'eliade_{}_calibration.{}'.format(my_det_type, opt)
        plt.savefig(save_results_to + file_name)
        plt.close()
        blCloverFound = False
    return True


def PlotCeBr(data, gammatab, source, my_det_type, lutfile, opt='eps'):
    print('<<<<< I am in PlotCeBr >>>>>')
    MakeDir(save_results_to)

    # my_det_type = 2
    ### RESOLUTION, EFFICIENCY AND PEAK-TO-TOTAL RATIO FOR CLOVERS
    for cebrkey in list_of_cebr:
        blCeBrFound = False
        for key in data:  # Browse through data in output file
            if find_domain(key["domain"], lutfile) == False:
                continue
            else:
                if key["serial"] == cebrkey:  # check if clover is found
                    if key["detType"] == my_det_type:  # check if the detector is the type that we want
                        blCeBrFound = True
                        plt.figure(0)  # peak-to-total plot
                        plot_color = "b"

                        try:
                            plt.errorbar(x=key["domain"], y=key["PT"][0], yerr=key["PT"][1], fmt='o', color=plot_color,
                                         ecolor='red', capsize=5)
                        except:
                            plt.scatter(x=key["domain"], y=key["PT"][0], color=plot_color)
                        for gammakey in list_of_sources:  # browse through the list of sources
                            if source == gammakey:  # if our source is in the list
                                for element in gammatab[source]["gammas"]:  # for each gamma energy of the source
                                    plot_color = "k"
                                    with open('{}/json/gamma_set.json'.format(ourpath), 'r') as jason_file:
                                        gammaset = json.load(jason_file)
                                        plot_color = gammaset[source]['gammas'][
                                            element]  # using different colors for each energy
                                    plt.figure(1)  # efficiency plot
                                    try:
                                        val_eff = key[source][element]["eff"][0]
                                        err_eff_rel = key[source][element]["eff"][1]
                                        eff = val_eff
                                        err_eff = val_eff * err_eff_rel

                                        plt.scatter(x=key["domain"], y=eff, color=plot_color,
                                                    label=f"{element}")
                                        plt.errorbar(x=key["domain"], y=eff,
                                                     yerr=err_eff, fmt='o', color=plot_color,
                                                     ecolor=plot_color, capsize=5)
                                    except:
                                        continue  # print("Energy {} missing from domain {}".format(key[source][element], key["domain"]))
                                    plt.figure(2)  # resolution plot
                                    try:
                                        val_res = key[source][element]["res"][0]
                                        err_res_rel = key[source][element]["res"][1]
                                        res = val_res
                                        err_res = val_res * err_res_rel

                                        plt.scatter(x=key["domain"], y=res, color=plot_color,
                                                    label=f"{element}")
                                        plt.errorbar(x=key["domain"], y=res,
                                                     yerr=err_res, fmt='o', color=plot_color,
                                                     ecolor=plot_color, capsize=5)
                                    except:
                                        continue  # print("Energy {} missing from domain {}".format(key[source][element], key["domain"]))
    if blCeBrFound == True:
        plt.figure(0)
        plt.xlim(900, 1000)
        plt.ylim([0.01, 0.3])

        plt.title(f'Peak to Total ratio for CeBr {my_det_type}')
        plt.xlabel('Domain')
        plt.ylabel('Peak-to-total ratio')
        plt.grid(color='black', linestyle='--', linewidth=0.5)

        file_name0 = 'eliade_CEBR_{}_peaktotal.{}'.format(my_det_type, opt)
        plt.savefig(save_results_to + file_name0)
        plt.close()

        plt.figure(1)
        plt.xlim(900, 1000)
        plt.ylim([0.01, 0.4])

        plt.title(f'Efficiency for CeBr {my_det_type}')
        plt.xlabel('Domain')
        plt.ylabel('Efficiency')
        plt.grid(color='black', linestyle='--', linewidth=0.5)

        file_name1 = 'eliade_CEBR_{}_eff.{}'.format(my_det_type, opt)
        plt.savefig(save_results_to + file_name1)
        plt.close()

        plt.figure(2)
        plt.xlim(900, 1000)
        plt.ylim([0, 50])

        plt.title(f'Resolution for CeBr {my_det_type}')
        plt.xlabel('Domain')
        plt.ylabel('Resolution')
        plt.grid(color='black', linestyle='--', linewidth=0.5)

        file_name2 = 'eliade_CEBR_{}_res.{}'.format(my_det_type, opt)
        plt.savefig(save_results_to + file_name2)
        plt.close()

        blCeBrFound = False
    print('Finished CeBr graphs')

    return True


# def PlotJsonFold(data, gammatab, source, my_det_type, lutfile, opt='eps'):
def PlotJsonFold(data, gammatab, source, my_det_type, opt='eps'):
    print('<<<<< I am in PlotJsonFold >>>>>')
    MakeDir(save_results_to)

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
                        val_eff = key[source][element]["eff"][0]
                        err_eff_rel = key[source][element]["eff"][1]
                        eff = val_eff
                        err_eff = val_eff * err_eff_rel

                        plt.scatter(x=key["fold"], y=eff, color=plot_color,
                                    label=f"{element}")
                        plt.errorbar(x=key["fold"], y=eff,
                                     yerr=err_eff, fmt='o', color=plot_color,
                                     ecolor=plot_color, capsize=5)
                    except:
                        print('Fold efficiency Plot failed')
                        continue  # print("Energy {} missing from domain {}".format(key[source][element], key["domain"]))
                    plt.figure(2)  # resolution plot
                    try:
                        val_res = key[source][element]["res"][0]
                        err_res_rel = key[source][element]["res"][1]
                        res = val_res
                        err_res = val_res * err_res_rel

                        plt.scatter(x=key["fold"], y=res, color=plot_color,
                                    label=f"{element}")
                        plt.errorbar(x=key["fold"], y=res,
                                     yerr=err_res, fmt='o', color=plot_color,
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

    # Plot AB(Eg)
    palette_size = len(data) + 1
    cmap = plt.cm.cividis  # You can use other colormaps like 'viridis', 'plasma', 'cividis', etc.
    my_colors = [cmap(i / palette_size) for i in range(palette_size)]

    Nfold = 1;
    for key in data:
        for gammakey in list_of_sources:  # browse through the list of sources
            if source == gammakey:  # if our source is in the list
                for element in gammatab[source]["gammas"]:  # for each gamma energy of the source
                    Nfold = 10 + key['fold']
                    # individual plots
                    plt.figure(10 + key['fold'])
                    try:
                        # plot_color = gammaset[source]['gammas'][element]
                        plt.scatter(x=float(element), y=key[source][element]["addback"])
                    except:
                        print('Addback vs Energy Plot failed')
                        continue
                    # one plots for all Folds
                    if key['fold'] == 1:
                        continue
                    try:
                        cc = my_colors[key['fold']]
                    except:
                        cc = 'black'
                    plt.figure(5)
                    try:
                        plt.scatter(x=float(element), y=key[source][element]["addback"], color=cc)
                    except:
                        print('Addback vs Energy Plot All failed')
                        continue
        plt.figure(5)
        if key['fold'] > 1:
            plt.scatter(x=float(element), y=key[source][element]["addback"], color=cc,
                        label='Fold {}'.format(key['fold']))
            plt.legend(loc='upper left', fontsize='medium', shadow=False)

    plt.figure(0)
    plt.title(f'Peak To Total for Fold Spectra')
    plt.xlabel('Fold')
    plt.ylabel('PT')
    file_name_pt = 'fold_{}_peaktotal.{}'.format(key["fold"], opt)
    plt.savefig(save_results_to + file_name_pt)
    plt.close()

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

    plt.figure(5)
    # plt.xticks(np.arange(0, 1500, 100))
    plt.title('Add Back Factor Fold')
    plt.xlabel('E$\gamma$')
    plt.ylabel('Add Back factor fold')
    file_name_ab = 'fold_ab_all.{}'.format(opt)
    plt.savefig(save_results_to + file_name_ab)
    plt.close()

    for fold in range(11, Nfold + 1):
        plt.figure(fold)
        # plt.xticks(np.arange(0, 1500, 100))
        plt.title('Add Back Factor Fold = {}'.format(fold - 10))
        plt.xlabel('Eg')
        plt.ylabel('Add Back factor fold')
        file_name_ab = 'fold_{}_ab.{}'.format(fold, opt)
        plt.savefig(save_results_to + file_name_ab)
        plt.close()

    print('Finished Fold graphs')

    return True
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
list_of_clovers = {"CL29", "CL30", "CL31", "CL32", "CL33", "CL34", "CL35", "CL36", "HPGe", "SEG", "LaBr"}
list_of_sources = {"60Co", "152Eu","137Cs", "133Ba"}
list_of_cebr = {"CEBR1","CEBR2","CEBR3","CEBR4"}

#res and eff vs ener for each domain


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
    if name == "CL29": #according to the current LUT
            plt.xlim([100.,141.])
    elif name == "CL30":
        plt.xlim([200.,241.])
    elif name == "CL32":
        plt.xlim([300.,341.])
    elif name == "CL35":
        plt.xlim([400.,441.])
    elif name == "CL34":
        plt.xlim([500.,541.])
    elif name == "CL36":
        plt.xlim([600.,641.])
    elif name == "CL33":
        plt.xlim([700.,741.])
    elif name == "CL31":
        plt.xlim([800.,841.])



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

        if find_domain(dom, lutfile)==False:
            continue
        else:
        
            plt.figure(1)
            for key in i[source].keys():
                res=i[source][key]["res"]
                #plt.scatter(x=float(key), y=res, color='b')
                plt.errorbar(x=float(key), y=res, yerr=i[source][key]["err_res"], fmt='o', color='b', ecolor='red', capsize=5)
            if source=="60Co":
                plt.xlim([1000.,1400.])
            elif source=="152Eu":
                plt.xlim([100, 1500])
            plt.ylim([1,5])
            if i["detType"]==3:
                plt.ylim([30,50])
                # print('plt.ylim([40,45])')
            plt.title(f'Resolution for domain {dom}')
            plt.xlabel('Energy (keV)')
            plt.ylabel('Resolution (keV)')
            plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
            #plt.legend()
            interactive(True)
            #plt.show()
            file_name1 = 'dom_{}_res.{}'.format(dom, opt)
            plt.savefig(save_results_to + file_name1)
            plt.close()
            plt.figure(2)
            for key in i[source].keys():
                eff = i[source][key]["eff"]
                plt.errorbar(x=float(key), y=eff, yerr=i[source][key]["err_eff"], fmt='o', color='b', ecolor='red', capsize=5)
                #plt.scatter(x=float(key), y=eff, color='b')
                
            if source=="60Co":
                plt.xlim([1000.,1400.])
            elif source=="152Eu":
                plt.xlim([100, 1500])
            if (i["detType"]==1 or i["detType"]==10):
                if(int(i["domain"])==1):
                    plt.ylim([1,2.5])
                else:
                    plt.ylim([0, 0.1])
            elif i["detType"]==2:
                if(int(i["domain"])==2):
                    plt.ylim([0.5,1.5])
                else:
                    plt.ylim([0,0.01])
            # if (i["domain"==1] or i["domain"]==2):
            #     plt.ylim([0.5, 2])
            #plt.ylim([0.0001,0.00015])
            plt.title(f'Efficiency for domain {dom}')
            plt.xlabel('Energy (keV)')
            plt.ylabel('Efficiency (%)')
            plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
            #plt.legend()
            
            plt.show()
            file_name2 = 'dom_{}_eff.{}'.format(dom, opt)
            plt.savefig(save_results_to + file_name2)
            interactive(False)
            plt.close()
    print("Finished domain graphs")
    return  True

def legend_without_duplicate_labels(figure):
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    figure.legend(by_label.values(), by_label.keys(), loc='upper right')

def PlotJsonclover(data, gammatab, source, my_det_type, lutfile, opt='eps'):
    print('I am in PlotJsonclover')
    MakeDir(save_results_to)
    
    # my_det_type = 2
    ### RESOLUTION, EFFICIENCY AND PEAK-TO-TOTAL RATIO FOR CLOVERS
    for cloverkey in list_of_clovers:
        blCloverFound = False
        for key in data: # Browse through data in output file
            if find_domain(key["domain"], lutfile)==False:
                continue
            else:
                if key["serial"].rstrip(key["serial"][-1]) == cloverkey: #check if clover is found
                    if key["detType"] == my_det_type: #check if the detector is the type that we want
                        blCloverFound = True
                        plt.figure(0) #peak-to-total plot
                        plot_color = "b"
                        
                        try:
                            plt.errorbar(x=key["domain"], y=key["PT"], yerr=key["err_PT"],fmt='o', color=plot_color, ecolor='red', capsize=5)
                        except:
                            plt.scatter(x=key["domain"], y=key["PT"], color=plot_color)
                        for gammakey in list_of_sources: # browse through the list of sources
                            if source == gammakey: #if our source is in the list                                
                                for element in gammatab[source]["gammas"]: #for each gamma energy of the source
                                    plot_color="k"
                                    with open('{}/json/gamma_set.json'.format(ourpath), 'r') as jason_file:
                                        gammaset=json.load(jason_file)
                                        plot_color=gammaset[source]['gammas'][element] #using different colors for each energy
                                    plt.figure(1) #efficiency plot
                                    try:
                                        plt.scatter(x=key["domain"], y=key[source][element]["eff"], color=plot_color, label=f"{element}")
                                        plt.errorbar(x=key["domain"], y=key[source][element]["eff"], yerr=key[source][element]["err_eff"], fmt='o', color=plot_color, ecolor=plot_color, capsize=5)
                                    except:
                                        continue #print("Energy {} missing from domain {}".format(key[source][element], key["domain"]))
                                    plt.figure(2) #resolution plot
                                    try:
                                        plt.scatter(x=key["domain"], y=key[source][element]["res"], color=plot_color, label=f"{element}")
                                        plt.errorbar(x=key["domain"], y=key[source][element]["res"], yerr=key[source][element]["err_res"], fmt='o', color=plot_color, ecolor=plot_color, capsize=5)
                                    except:
                                        continue #print("Energy {} missing from domain {}".format(key[source][element], key["domain"]))
        if blCloverFound == True:

            # FindXlim(cloverkey) #each clover has a different x-axis interval
            xmin, xmax = FinXlimGeneric(cloverkey, lutfile)
            xmin-=1
            xmax+=1
            plt.xlim(xmin, xmax)

            plt.figure(1)
            plt.xlim(xmin, xmax)
            # FindXlim(cloverkey)  # efficiency #dt commented
            if my_det_type==1 or my_det_type==10:
                plt.ylim([0, 0.1])
            elif my_det_type==2: # (segments)
                plt.ylim([0,0.01])
            plt.title(f'Efficiency for clover {cloverkey}')
            plt.xlabel('Domain')
            plt.ylabel('Efficiency (%)')
            plt.grid(color='black', linestyle='--', linewidth=0.5)
            legend_without_duplicate_labels(plt)

            file_name1 = 'eliade_{}_efficiency.{}'.format(cloverkey, opt)
            plt.savefig(save_results_to + file_name1)
            plt.close()


            plt.figure(2)
            # FindXlim(cloverkey) #resolution
            plt.xlim(xmin, xmax)
            plt.ylim([1,5])
            plt.title(f'Resolution for clover {cloverkey}')
            plt.xlabel('Domain')
            plt.ylabel('Resolution (keV)')
            plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
            legend_without_duplicate_labels(plt)

            file_name2 = 'eliade_{}_{}_resolution.{}'.format(cloverkey, my_det_type, opt)
            plt.savefig(save_results_to + file_name2)
            plt.close()

            plt.figure(0)
            # FindXlim(cloverkey)  # Peak to Total
            plt.xlim(xmin, xmax)
            # plt.ylim([0.05,0.1])
            if my_det_type==1 or my_det_type==10:
                plt.ylim([0.15, 0.2])
            elif my_det_type==2: # (segments)
                plt.ylim([0,0.1])
            plt.title(f'Peak to Total ratio for clover {cloverkey} {my_det_type}')
            plt.xlabel('Domain')
            plt.ylabel('Peak-to-total ratio')
            plt.grid(color='black', linestyle='--', linewidth=0.5)

            file_name3 = 'eliade_{}_{}_peaktotal.{}'.format(cloverkey, my_det_type ,opt)
            plt.savefig(save_results_to + file_name3)
            plt.close()

            blCloverFound = False
    print('Finished CLOVER graphs')

    return True

   
def PlotJsoncore(data, gammatab, source, lutfile, detKey = 1, opt='eps'):

    MakeDir(save_results_to)
    CloverName=''
    #my_det_type=1
    for key in data:
        #clover=i["serial"]
        if find_domain(key["domain"], lutfile)==False:
            continue
        if key["detType"] != detKey:
            continue
        # if key["domain"] == 1:
        #     continue
        for gammakey in list_of_sources:
            if source == gammakey:
                for element in gammatab[source]["gammas"]:
                    plot_color="k"
                    with open('{}/json/gamma_set.json'.format(ourpath), 'r') as jason_file:
                                gammaset=json.load(jason_file)
                                plot_color=gammaset[source]['gammas'][element] #using different colors for each energy
                    plt.figure(1) #efficiency plot
                    try:
                        plt.scatter(x=key["domain"], y=key[source][element]["eff"], color=plot_color, label=f"{element}")
                        plt.errorbar(x=key["domain"], y=key[source][element]["eff"], yerr=key[source][element]["err_eff"], fmt='o', color=plot_color, ecolor=plot_color, capsize=5)
                    except:
                        continue
                    plt.figure(2) #resolution plot
                    try:
                        plt.scatter(x=key["domain"], y=key[source][element]["res"], color=plot_color, label=f"{element}")
                        plt.errorbar(x=key["domain"], y=key[source][element]["res"], yerr=key[source][element]["err_res"], fmt='o', color=plot_color, ecolor=plot_color, capsize=5)
                    except:
                        continue
        #FindXlim(clover)
        plt.figure(1)
        # xmin, xmax = FinXlimGeneric(clover, lutfile)
        # xmin -= 1
        # xmax += 1
        plt.xlim(100,841)
        # plt.xlim(xmin, xmax)
        plt.ylim([0,0.1])
        #title_clover=clover.rstrip(clover[-1])#CL29 instead of CL29G
        CloverName = key["serial"][:len(key["serial"])-1]
        plt.title('Efficiency for core {} {}'.format(CloverName, detKey))
        plt.xlabel('Domain')
        plt.ylabel('Efficiency (%)')
        plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
        legend_without_duplicate_labels(plt)

        plt.figure(2)
        # FindXlim(clover)
        # plt.xlim(xmin, xmax)
        plt.ylim([1,5])
        #title_clover=clover.rstrip(clover[-1])#CL29 instead of CL29G
        plt.title('Resolution for core {} {}'.format(CloverName,detKey))
        plt.xlabel('Domain')
        plt.ylabel('Resolution (keV)')
        plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
        legend_without_duplicate_labels(plt)


        plt.figure(1)
        file_name5 = 'eliade_efficiency_{}_core{}.{}'.format(CloverName, detKey, opt)
        plt.savefig(save_results_to + file_name5)
        plt.close()

        plt.figure(2)
        file_name6 = 'eliade_resolution_{}_core{}.{}'.format(CloverName, detKey, opt)
        plt.savefig(save_results_to + file_name6)
        plt.close()

    print("Finished graphs for all core{} {}".format(CloverName, detKey))
    return True

def PlotCalibration(data, gammatab, source, lutfile, my_det_type = 2, opt='eps'):
    if my_det_type == 3:
        #To plot CeBr calib please use PlotCalibrationCeBr instead of PlotCalibration
        return True

    MakeDir(save_results_to)
    number_of_our_colors = 30
    our_color_plate = iter(cm.rainbow(np.linspace(0, 1, number_of_our_colors)))
    # niter = 0

    for cloverkey in list_of_clovers:
        number_of_our_colors = 40
        our_color_plate = iter(cm.rainbow(np.linspace(0, 1, number_of_our_colors)))
        blCloverFound = False
        for key in data: # Browse through data in output file
            if find_domain(key["domain"], lutfile)==False:
                continue
            if key['detType'] != my_det_type: #or key['detType'] == 3:
                continue
            else:
                if key["serial"].rstrip(key["serial"][-1]) == cloverkey: #check if clover is found
                    if key["pol_list"]:
                        if key["detType"] == my_det_type: #check if the detector is the type that we want
                            blCloverFound = True
                            dom=key["domain"]

                            try:
                                current_color = next(our_color_plate)
                            except:
                                current_color = 'red'

                            plt.plot([1, 2000], [float(key["pol_list"][0])+float(key["pol_list"][1])*1,  float(key["pol_list"][0])+float(key["pol_list"][1])*2000], color = current_color, label=f"{dom}", linewidth=1)

                            for gammakey in list_of_sources: # browse through the list of sources
                                if source == gammakey: #if our source is in the list                                
                                    for element in gammatab[source]["gammas"]: #for each gamma energy of the source
                                        try:
                                            plt.scatter(x=key[source][element]["pos_ch"], y=float(element), color=current_color)
                                        except:
                                            print('Warning skipping plot domain {} for gamma {} because not fitted'.format(key['domain'], element))
                                            # continue
                            max_energy=max([float(i) for i in list(gammatab[source]["gammas"].keys())])

        if blCloverFound == True:
                delta=200
                #print("calib")
                plt.xlim([0,1200])
                plt.ylim([0,max_energy+delta])#maximum energy from source + delta: [0; max+delta]
                plt.xlabel('Channel')
                plt.ylabel('Energy (keV)')
                plt.title(f'Calibration for clover {cloverkey} {my_det_type}')
                #legend_without_duplicate_labels(plt)
                plt.legend(ncol=3,loc='lower right',prop={'size': 6})
                # plt.show()
                file_name='eliade_{}_{}_calibration.{}'.format(cloverkey,my_det_type, opt)
                file_name='eliade_{}_{}_calibration.{}'.format(cloverkey, my_det_type,opt)
                plt.savefig(save_results_to + file_name)
                plt.close()  
                blCloverFound=False
    return True


def PlotCalibrationCeBr(data, gammatab, source, lutfile, my_det_type=3, opt='eps'):
    MakeDir(save_results_to)
    number_of_our_colors = 30
    our_color_plate = iter(cm.rainbow(np.linspace(0, 1, number_of_our_colors)))

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
                    if key["pol_list"]:
                        # if key["detType"] == my_det_type:  # check if the detector is the type that we want
                        blCeBrFound = True
                        dom = key["domain"]
                        try:
                            current_color = next(our_color_plate)
                        except:
                            current_color = 'red'

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
            file_name = 'eliade_{}_{}_calibration.{}'.format(cebrkey, my_det_type, opt)
            file_name = 'eliade_{}_{}_calibration.{}'.format(cebrkey, my_det_type, opt)
            plt.savefig(save_results_to + file_name)
            plt.close()
            blCloverFound = False
    return True


def PlotCeBr(data, gammatab, source, my_det_type, lutfile, opt='eps'):
    print('I am in PlotPTCeBr')
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
                            plt.errorbar(x=key["domain"], y=key["PT"], yerr=key["err_PT"], fmt='o', color=plot_color,
                                         ecolor='red', capsize=5)
                        except:
                            plt.scatter(x=key["domain"], y=key["PT"], color=plot_color)
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
                                        plt.scatter(x=key["domain"], y=key[source][element]["eff"], color=plot_color,
                                                    label=f"{element}")
                                        plt.errorbar(x=key["domain"], y=key[source][element]["eff"],
                                                     yerr=key[source][element]["err_eff"], fmt='o', color=plot_color,
                                                     ecolor=plot_color, capsize=5)
                                    except:
                                        continue  # print("Energy {} missing from domain {}".format(key[source][element], key["domain"]))
                                    plt.figure(2)  # resolution plot
                                    try:
                                        plt.scatter(x=key["domain"], y=key[source][element]["res"], color=plot_color,
                                                    label=f"{element}")
                                        plt.errorbar(x=key["domain"], y=key[source][element]["res"],
                                                     yerr=key[source][element]["err_res"], fmt='o', color=plot_color,
                                                     ecolor=plot_color, capsize=5)
                                    except:
                                        continue  # print("Energy {} missing from domain {}".format(key[source][element], key["domain"]))
        if blCeBrFound == True:

            # FindXlim(cloverkey) #each clover has a different x-axis interval
            # xmin, xmax = FinXlimGeneric(cebrkey, lutfile)
            # xmin -= 1
            # xmax += 1
            # plt.xlim(xmin, xmax)
            #
            # plt.figure(1)
            # plt.xlim(xmin, xmax)
            # # FindXlim(cloverkey)  # efficiency #dt commented
            # if my_det_type == 1 or my_det_type == 10:
            #     plt.ylim([0, 0.1])
            # elif my_det_type == 2:  # (segments)
            #     plt.ylim([0, 0.01])
            # plt.title(f'Efficiency for {cebrkey}')
            # plt.xlabel('Domain')
            # plt.ylabel('Efficiency (%)')
            # plt.grid(color='black', linestyle='--', linewidth=0.5)
            # legend_without_duplicate_labels(plt)
            #
            # file_name1 = 'eliade_{}_efficiency.{}'.format(cloverkey, opt)
            # plt.savefig(save_results_to + file_name1)
            # plt.close()
            #
            # plt.figure(2)
            # # FindXlim(cloverkey) #resolution
            # plt.xlim(xmin, xmax)
            # plt.ylim([1, 5])
            # plt.title(f'Resolution for {cloverkey}')
            # plt.xlabel('Domain')
            # plt.ylabel('Resolution (keV)')
            # plt.grid(color='black', linestyle='--', linewidth=0.5)
            # legend_without_duplicate_labels(plt)
            #
            # file_name2 = 'eliade_{}_{}_resolution.{}'.format(cloverkey, my_det_type, opt)
            # plt.savefig(save_results_to + file_name2)
            # plt.close()

            plt.figure(0)
            # FindXlim(cloverkey)  # Peak to Total
            plt.xlim(980, 1100)
            # plt.ylim([0.05,0.1])
            if my_det_type == 1 or my_det_type == 10:
                plt.ylim([0.15, 0.2])
            elif my_det_type == 2:  # (segments)
                plt.ylim([0, 0.1])
            plt.title(f'Peak to Total ratio for {cebrkey} {my_det_type}')
            plt.xlabel('Domain')
            plt.ylabel('Peak-to-total ratio')
            plt.grid(color='black', linestyle='--', linewidth=0.5)

            file_name3 = 'eliade_{}_{}_peaktotal.{}'.format(cebrkey, my_det_type, opt)
            plt.savefig(save_results_to + file_name3)
            plt.close()

            blCeBrFound = False
    print('Finished CeBr graphs')

    return True
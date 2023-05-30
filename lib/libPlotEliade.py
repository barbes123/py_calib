import json
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from matplotlib import interactive
import numpy as np
import os
import matplotlib.colors as mcolors
from random import choice

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

#res and eff vs ener for each domain


def MakeDir(path):
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
        print("The new directory {} is created!".format(path))

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



def PlotJsondom(data, gammatab, source):

    MakeDir(save_results_to)

    for i in data:
        # print('checking type {}'.format(type(i['domain'])))
        dom = i["domain"]
        
        plt.figure(1)
        for key in i[source].keys():
            res=i[source][key]["res"]
            #plt.scatter(x=float(key), y=res, color='b')
            plt.errorbar(x=float(key), y=res, yerr=i[source][key]["err_res"], fmt='o', color='b', ecolor='red', capsize=5)
        plt.xlim([1000.,1400.])
        plt.ylim([1,5])
        plt.title(f'Resolution for domain {dom}')
        plt.xlabel('Energy (keV)')
        plt.ylabel('Resolution (keV)')
        plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
        #plt.legend()
        interactive(True)
        #plt.show()
        file_name1 = 'dom_{}_res.png'.format(dom)
        plt.savefig(save_results_to + file_name1)
        plt.close()
        plt.figure(2)
        for key in i[source].keys():
            eff = i[source][key]["eff"]
            plt.errorbar(x=float(key), y=eff, yerr=i[source][key]["err_eff"], fmt='o', color='b', ecolor='red', capsize=5)
            #plt.scatter(x=float(key), y=eff, color='b')
            
        plt.xlim([1000,1400])
        if (i["detType"]==1 or i["detType"]==10):
            plt.ylim([0, 0.1])
        elif i["detType"]==2:
            plt.ylim([0,0.01])
        #plt.ylim([0.0001,0.00015])
        plt.title(f'Efficiency for domain {dom}')
        plt.xlabel('Energy (keV)')
        plt.ylabel('Efficiency (%)')
        plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
        #plt.legend()
        
        plt.show()
        file_name2 = 'dom_{}_eff.png'.format(dom)
        plt.savefig(save_results_to + file_name2)
        interactive(False)
        plt.close()
    print("Finished domain graphs")
    return  True

def legend_without_duplicate_labels(figure):
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    figure.legend(by_label.values(), by_label.keys(), loc='lower right')

def PlotJsonclover(data, gammatab, source, my_det_type):
    print('I am in PlotJsonclover')
    MakeDir(save_results_to)
    
    # my_det_type = 2
    ### RESOLUTION, EFFICIENCY AND PEAK-TO-TOTAL RATIO FOR CLOVERS
    for cloverkey in list_of_clovers:
        blCloverFound = False
        for key in data: # Browse through data in output file
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

            FindXlim(cloverkey) #each clover has a different x-axis interval

            plt.figure(1)
            FindXlim(cloverkey)  # efficiency
            if my_det_type==1 or my_det_type==10:
                plt.ylim([0, 0.1])
            elif my_det_type==2: # (segments)
                plt.ylim([0,0.01])
            plt.title(f'Efficiency for clover {cloverkey}')
            plt.xlabel('Domain')
            plt.ylabel('Efficiency (%)')
            plt.grid(color='black', linestyle='--', linewidth=0.5)
            legend_without_duplicate_labels(plt)

            file_name1 = 'eliade_{}_efficiency.png'.format(cloverkey)
            plt.savefig(save_results_to + file_name1)
            plt.close()


            plt.figure(2)
            FindXlim(cloverkey) #resolution
            plt.ylim([1,5])
            plt.title(f'Resolution for clover {cloverkey}')
            plt.xlabel('Domain')
            plt.ylabel('Resolution (keV)')
            plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
            legend_without_duplicate_labels(plt)

            file_name2 = 'eliade_{}_resolution.png'.format(cloverkey)
            plt.savefig(save_results_to + file_name2)
            plt.close()

            plt.figure(0)
            FindXlim(cloverkey)  # Peak to Total
            plt.ylim([0.05,0.1])
            plt.title(f'Peak to Total ratio for clover {cloverkey}')
            plt.xlabel('Domain')
            plt.ylabel('Peak-to-total ratio')
            plt.grid(color='black', linestyle='--', linewidth=0.5)

            file_name3 = 'eliade_{}_peaktotal.png'.format(cloverkey)
            plt.savefig(save_results_to + file_name3)
            plt.close()

            blCloverFound = False
    print('Finished CLOVER graphs')

    return True

   
def PlotJsoncore(data, gammatab, source):

    MakeDir(save_results_to)
    #my_det_type=1
    for key in data:
        #clover=i["serial"]
        if key["detType"] == 1:
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
        #plt.xlim(100,841)
        plt.ylim([0,0.1])
        #title_clover=clover.rstrip(clover[-1])#CL29 instead of CL29G
        plt.title('Efficiency for core 1 ')
        plt.xlabel('Domain')
        plt.ylabel('Efficiency (%)')
        plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
        legend_without_duplicate_labels(plt)

        plt.figure(2)
        #FindXlim(clover)
        plt.ylim([1,5])
        #title_clover=clover.rstrip(clover[-1])#CL29 instead of CL29G
        plt.title(f'Resolution for core 1')
        plt.xlabel('Domain')
        plt.ylabel('Resolution (keV)')
        plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
        legend_without_duplicate_labels(plt)

        
    plt.figure(1)    
    file_name5 = 'eliade_efficiency_core1.png'
    plt.savefig(save_results_to + file_name5)
    plt.close()   

    plt.figure(2)
    file_name6 = 'eliade_resolution_core1.png'
    plt.savefig(save_results_to + file_name6)
    plt.close()

    print("Finished graphs for all core1")
    return  True

def PlotCalibration(data, gammatab, source):
    MakeDir(save_results_to)
    number_of_our_colors = 30
    our_color_plate = iter(cm.rainbow(np.linspace(0, 1, number_of_our_colors)))
    # niter = 0

    for cloverkey in list_of_clovers:
        my_det_type=2
        number_of_our_colors = 40
        our_color_plate = iter(cm.rainbow(np.linspace(0, 1, number_of_our_colors)))
        blCloverFound = False
        for key in data: # Browse through data in output file
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
                                        plt.scatter(x=key[source][element]["pos_ch"], y=float(element), color=current_color)
                        max_energy=max([float(i) for i in list(gammatab[source]["gammas"].keys())])

                 
        if blCloverFound == True:
                delta=200
                #print("calib")
                plt.xlim([0,1200])
                plt.ylim([0,max_energy+delta])#maximum energy from source + delta: [0; max+delta]
                plt.xlabel('Channel')
                plt.ylabel('Energy (keV)')
                plt.title(f'Calibration for clover {cloverkey}')
                #legend_without_duplicate_labels(plt)
                plt.legend(ncol=3,loc='lower right',prop={'size': 6})
                # plt.show()
                file_name='eliade_{}_calibration.png'.format(cloverkey)
                plt.savefig(save_results_to + file_name)
                plt.close()  
                blCloverFound=False
    return True


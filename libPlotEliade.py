import json
import matplotlib.pyplot as plt
from matplotlib import interactive
import os

global save_results_to
# save_results_to = '/home/rmiron/Desktop/dir/python_exercises/calibrations/figures/'
save_results_to = 'figures/'
title_clover = ''
#res and eff vs ener for each domain


def MakeDir(path):
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
        print("The new directory {} is created!".format(path))

def FindXlim(name):
    if name.rstrip(name[-1]) == "CL29": #according to the current LUT
            plt.xlim([100.,141.])
    elif name.rstrip(name[-1]) == "CL30":
        plt.xlim([200.,241.])
    elif name.rstrip(name[-1]) == "CL32":
        plt.xlim([300.,341.])
    elif name.rstrip(name[-1]) == "CL35":
        plt.xlim([400.,441.])
    elif name.rstrip(name[-1]) == "CL34":
        plt.xlim([500.,541.])
    elif name.rstrip(name[-1]) == "CL36":
        plt.xlim([600.,641.])
    elif name.rstrip(name[-1]) == "CL33":
        plt.xlim([700.,741.])



def PlotJsondom(data, source):

    MakeDir(save_results_to)

    for i in data:
        # print('checking type {}'.format(type(i['domain'])))
        dom = i["domain"]
        
        plt.figure(1)
        for key in i[source].keys():
            res=i[source][key]["res"]
            plt.scatter(x=float(key), y=res)
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
            plt.scatter(x=float(key), y=eff)
        plt.xlim([1000,1400])
        plt.ylim([0.0001,0.00015])
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
        
    return  True

def legend_without_duplicate_labels(figure):
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    figure.legend(by_label.values(), by_label.keys(), loc='lower right')

def PlotJsonclover(data, source):
    MakeDir(save_results_to)
    for i in data:
        
        clover=i["serial"]
        dom = i["domain"]
        
        
        for key in i[source].keys():
            res=i[source][key]["res"]
            if float(key)==1173.238:
                plt.scatter(x=dom, y=res, color='r', label=f"{key}")
            elif float(key)==1332.513:
                plt.scatter(x=dom, y=res, color='b', label=f"{key}")
            
        FindXlim(clover)
        plt.ylim([1,5])
        title_clover=clover.rstrip(clover[-1])#CL29 instead of CL29G
        plt.title(f'Resolution for clover {title_clover}')
        plt.xlabel('Domain')
        plt.ylabel('Resolution (keV)')
        plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
        legend_without_duplicate_labels(plt)
        
        
    file_name1 = 'eliade_{}_resolution.png'.format(title_clover)
    plt.savefig(save_results_to + file_name1)
    plt.close()

    for i in data:
        clover=i["serial"]
        dom = i["domain"]

        for key in i[source].keys():
            eff = i[source][key]["eff"]
            if float(key)==1173.238:
                plt.scatter(x=dom, y=eff, color='r', label=f"{key}")
            elif float(key)==1332.513:
                plt.scatter(x=dom, y=eff, color='b', label=f"{key}")
        FindXlim(clover)
        plt.ylim([0.0001,0.00015])
        title_clover=clover.rstrip(clover[-1])#CL29 instead of CL29G
        plt.title(f'Efficiency for clover {title_clover}')
        plt.xlabel('Domain')
        plt.ylabel('Efficiency (%)')
        plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
        legend_without_duplicate_labels(plt)
        
    file_name2 = 'eliade_{}_efficiency.png'.format(title_clover)
    plt.savefig(save_results_to + file_name2)
    plt.close()   
    return  True

with open('calib_res_1.json', 'r') as js_file:
    data=json.load(js_file)

# PlotJsondom(data, "60Co")
# PlotJsonclover(data, "60Co")


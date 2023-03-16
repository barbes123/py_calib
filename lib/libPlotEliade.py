import json
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from matplotlib import interactive
import numpy as np
import os
import matplotlib.colors as mcolors
from random import choice

global save_results_to
# save_results_to = '/home/rmiron/Desktop/dir/python_exercises/calibrations/figures/'
save_results_to = 'figures/'
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



def PlotJsondom(data, source):

    MakeDir(save_results_to)

    for i in data:
        # print('checking type {}'.format(type(i['domain'])))
        dom = i["domain"]
        
        plt.figure(1)
        for key in i[source].keys():
            res=i[source][key]["res"]
            plt.scatter(x=float(key), y=res, color='b')
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
            plt.scatter(x=float(key), y=eff, color='b')
        plt.xlim([1000,1400])
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

def PlotJsonclover(data, source):
    print('I am in PlotJsonclover')
    MakeDir(save_results_to)
    
    my_det_type = 1
        
    ### RESOLUTION, EFFICIENCY AND PEAK-TO-TOTAL RATIO FOR CLOVERS
    for cloverkey in list_of_clovers:
        blCloverFound = False
        for key in data: # Browse through data in output file
            if key["serial"].rstrip(key["serial"][-1]) == cloverkey: #check if clover is found
                if key["detType"] == my_det_type: #check if the detector is the type that we want
                    blCloverFound = True
                    plt.figure(0) #peak-to-total plot
                    plot_color = "b"
                    plt.scatter(x=key["domain"], y=key["PT"], color=plot_color)
                    for gammakey in list_of_sources: # browse through the list of sources
                        if source == gammakey: #if our source is in the list                                
                            for element in gammatab[source]["gammas"]: #for each gamma energy of the source
                                plot_color="k"
                                with open('json/gamma_set.json', 'r') as jason_file:
                                    gammaset=json.load(jason_file)
                                    plot_color=gammaset[source]['gammas'][element] #using different colors for each energy
                                plt.figure(1) #efficiency plot
                                plt.scatter(x=key["domain"], y=key[source][element]["eff"], color=plot_color, label=f"{element}")
                                plt.figure(2) #resolution plot
                                plt.scatter(x=key["domain"], y=key[source][element]["res"], color=plot_color, label=f"{element}")
        if blCloverFound == True:

            FindXlim(cloverkey) #each clover has a different x-axis interval
            plt.figure(1)  # efficiency
            if my_det_type==1 or my_det_type==10:
                plt.ylim([0.04, 0.1])
            elif my_det_type==2: # (segments)
                plt.ylim([0,0.01])
            plt.title(f'Efficiency for clover {cloverkey}')
            plt.xlabel('Domain')
            plt.ylabel('Efficiency (%)')
            plt.grid(color='black', linestyle='--', linewidth=0.5)
            legend_without_duplicate_labels(plt)

            file_name2 = 'eliade_{}_efficiency.png'.format(cloverkey)
            plt.savefig(save_results_to + file_name2)
            plt.close()


            plt.figure(2) #resolution
            plt.ylim([1,5])
            plt.title(f'Resolution for clover {cloverkey}')
            plt.xlabel('Domain')
            plt.ylabel('Resolution (keV)')
            plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
            legend_without_duplicate_labels(plt)

            file_name1 = 'eliade_{}_resolution.png'.format(cloverkey)
            plt.savefig(save_results_to + file_name1)
            plt.close()

            plt.figure(0)  # Peak to Total
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

   
def PlotJsoncore(data, source):

    MakeDir(save_results_to)
    #my_det_type=1
    for key in data:
        #clover=i["serial"]
        if key["detType"] == 1:
            for gammakey in list_of_sources:
                if source == gammakey:
                    for element in gammatab[source]["gammas"]:
                        plot_color="k"
                        with open('json/gamma_set.json', 'r') as jason_file:
                                    gammaset=json.load(jason_file)
                                    plot_color=gammaset[source]['gammas'][element] #using different colors for each energy
                        plt.figure(1) #efficiency plot
                        plt.scatter(x=key["domain"], y=key[source][element]["eff"], color=plot_color, label=f"{element}")
                        plt.figure(2) #resolution plot
                        plt.scatter(x=key["domain"], y=key[source][element]["res"], color=plot_color, label=f"{element}")
        #FindXlim(clover)
        plt.figure(1)
        plt.ylim([0.04,0.1])
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

def PlotCalibration(data,source):
    MakeDir(save_results_to)

    #variable n below should be number of curves to plot

    #version 1:

    # color = cm.rainbow(np.linspace(0, 1, n))
    # for i, c in zip(range(n), color):
    #     plt.plot(x, y, c=c)

    #or version 2:
    #n=40
    #color = cm.rainbow(np.linspace(0, 1, n))
    # for i in range(n):
    #     c = next(color)
    #     plt.plot(x, y, c=c)    

    

    # # 1000 distinct colors:
    # colors = [hsv_to_rgb([(i * 0.618033988749895) % 1.0, 1, 1])
    #         for i in range(1000)]
    # plt.rc('axes', prop_cycle=(cycler('color', colors)))


    '''
    from cycler import cycler

    # 1000 distinct colors:
    colors = [hsv_to_rgb([(i * 0.618033988749895) % 1.0, 1, 1])
            for i in range(1000)]
    plt.rc('axes', prop_cycle=(cycler('color', colors)))

    for i in range(20):
        plt.plot([1, 0], [i, i])

    plt.show()
    '''

    '''
    import matplotlib.pyplot as plt
import numpy as np

num_plots = 20

# Have a look at the colormaps here and decide which one you'd like:
# http://matplotlib.org/1.2.1/examples/pylab_examples/show_colormaps.html
colormap = plt.cm.gist_ncar
plt.gca().set_prop_cycle(plt.cycler('color', plt.cm.jet(np.linspace(0, 1, num_plots))))

# Plot several different functions...
x = np.arange(10)
labels = []
for i in range(1, num_plots + 1):
    plt.plot(x, i * x + 5 * i)
    labels.append(r'$y = %ix + %i$' % (i, 5*i))

# I'm basically just demonstrating several different legend options here...
plt.legend(labels, ncol=4, loc='upper center', 
           bbox_to_anchor=[0.5, 1.1], 
           columnspacing=1.0, labelspacing=0.0,
           handletextpad=0.0, handlelength=1.5,
           fancybox=True, shadow=True)

plt.show()

colors = hsv_to_rgb([(i * 0.618033988749895) % 1, 1, 1])
            default_cycler=(cycler('color', colors)+cycler(linestyle=['-', '--', '-.']))
            plt.rc('lines', linewidth=4)
            plt.rc('axes', prop_cycle=default_cycler)

    '''
    xmin=0
    xmax=1200
    steps=150
    step=(xmax-xmin)/steps
    dataplotx=[]
    dataploty=[]

    colours = mcolors._colors_full_map # This is a dictionary of all named colours
    # Turn the dictionary into a list
    color_lst = list(colours.values()) 

    #color_dict = {}

  



    for cloverkey in list_of_clovers:
        blCloverFound = False
        #i=1
        for key in data: # Browse through data in output file
            
            if key["serial"].rstrip(key["serial"][-1]) == cloverkey: #check if clover is found
                #if key["detType"] == my_det_type: #check if the detector is the type that we want
                blCloverFound = True
                dom=key["domain"]
            
                #i=i+1
                for s in range(steps):
                    xgrid=xmin+step*s
                    dataplotx.append(xgrid)
                    dataploty.append(float(key["pol_list"][0])+float(key["pol_list"][1])*xgrid)
                #c=(0, i / 20.0, 0, 1)
                c=choice(color_lst)                
                            

                for gammakey in list_of_sources: # browse through the list of sources
                    if source == gammakey: #if our source is in the list                                
                        for element in gammatab[source]["gammas"]: #for each gamma energy of the source
                            # for i, c in zip(range(n), color):      
                                
                                plt.plot(dataplotx, dataploty, color=c, label= f"{dom}")                                         
                                plt.scatter(x=key[source][element]["pos_ch"], y=float(element), color=c)
                 
        if blCloverFound == True:
                #print("calib")
                plt.xlim([0,1200])
                plt.ylim([0,1500])
                plt.xlabel('Channel')
                plt.ylabel('Energy (keV)')
                plt.title(f'Calibration for clover {cloverkey}')
                legend_without_duplicate_labels(plt)
                #plt.legend()
                #plt.show()
                file_name='eliade_{}_calibration.png'.format(cloverkey)
                plt.savefig(save_results_to + file_name)
                plt.close()  
                blCloverFound=False
                                
    return True

with open('calib_res_1.json', 'r') as js_file:
    data=json.load(js_file)

with open('json/gamma_sources.json', 'r') as jas_file:
    gammatab=json.load(jas_file)



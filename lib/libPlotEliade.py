import json
import matplotlib.pyplot as plt
from matplotlib import interactive
import os

global save_results_to
# save_results_to = '/home/rmiron/Desktop/dir/python_exercises/calibrations/figures/'
save_results_to = 'figures/'
title_clover = ''
list_of_clovers = {"CL29", "CL30", "CL31", "CL32", "CL33", "CL35", "CL36"}
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
        
    return  True

def legend_without_duplicate_labels(figure):
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    figure.legend(by_label.values(), by_label.keys(), loc='lower right')

def PlotJsonclover(data, source):
    print('I am in PlotJsonclover')
    MakeDir(save_results_to)
    #for i in data:
        
        #clover=i["serial"]
        #dom = i["domain"]

    my_det_type = 1
        
    ### RESOLUTION FOR CLOVERS
    for cloverkey in list_of_clovers:
        for key in data:
            # print(key["serial"])
            #print(key["serial"].rstrip(key["serial"][-1]))
            if key["serial"].rstrip(key["serial"][-1]) == cloverkey:
                if key["detType"] == my_det_type:
                    #print('wowo')
                    for gammakey in list_of_sources:
                        if source == gammakey:                                
                            for element in gammatab[source]["gammas"]:
                                plot_color="k"
                                with open('json/gamma_set.json', 'r') as jason_file:
                                    gammaset=json.load(jason_file)
                                    plot_color=gammaset[source]['gammas'][element]
                                plt.scatter(x=key["domain"], y=key[source][element]["res"], color =  plot_color,label=f"{element}")
        FindXlim(cloverkey)
        plt.ylim([1,5])
        #title_clover=clover.rstrip(clover[-1])#CL29 instead of CL29G
        plt.title(f'Resolution for clover {cloverkey}')
        plt.xlabel('Domain')
        plt.ylabel('Resolution (keV)')
        plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
        legend_without_duplicate_labels(plt)       


        file_name1 = 'eliade_{}_resolution.png'.format(cloverkey)
        plt.savefig(save_results_to + file_name1)
        plt.close()  

        
       
        # for key in data['serial']:
            # print(key)
        

        # for key in i[source].keys():
        #     res=i[source][key]["res"]
        #     if float(key)==1173.238:
        #         plt.scatter(x=dom, y=res, color='r', label=f"{key}")
        #     elif float(key)==1332.513:
        #         plt.scatter(x=dom, y=res, color='b', label=f"{key}")
        

            
        # FindXlim(clover)
        # plt.ylim([1,5])
        # title_clover=clover.rstrip(clover[-1])#CL29 instead of CL29G
        # plt.title(f'Resolution for clover {title_clover}')
        # plt.xlabel('Domain')
        # plt.ylabel('Resolution (keV)')
        # plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
        # legend_without_duplicate_labels(plt)

    # file_name1 = 'eliade_{}_resolution.png'.format(title_clover)
    # plt.savefig(save_results_to + file_name1)
    # plt.close()

    ### EFFICIENCY FOR CLOVERS
   
    for cloverkey in list_of_clovers:
        for key in data:
            # print(key["serial"])
            #print(key["serial"].rstrip(key["serial"][-1]))
            if key["serial"].rstrip(key["serial"][-1]) == cloverkey:
                if key["detType"] == my_det_type:
                    #print('wowo')
                    for gammakey in list_of_sources:
                        if source == gammakey:                                
                            for element in gammatab[source]["gammas"]:
                                plot_color="k"
                                with open('json/gamma_set.json', 'r') as jason_file:
                                    gammaset=json.load(jason_file)
                                    plot_color=gammaset[source]['gammas'][element]
                                plt.scatter(x=key["domain"], y=key[source][element]["eff"], color =  plot_color,label=f"{element}")
        FindXlim(cloverkey)
        #plt.ylim([1,5])
        plt.title(f'Efficiency for clover {cloverkey}')
        plt.xlabel('Domain')
        plt.ylabel('Efficiency (%)')
        plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
        legend_without_duplicate_labels(plt)       


        file_name2 = 'eliade_{}_efficiency.png'.format(cloverkey)
        plt.savefig(save_results_to + file_name2)
        plt.close()  
    
    ### PEAK TO TOTAL
    for cloverkey in list_of_clovers:
        for key in data:
            # print(key["serial"])
            #print(key["serial"].rstrip(key["serial"][-1]))
            if key["serial"].rstrip(key["serial"][-1]) == cloverkey:
                if key["detType"] == my_det_type:
                    #print('wowo')
                    for gammakey in list_of_sources:
                        if source == gammakey:                                
                            for element in gammatab[source]["gammas"]:
                                plot_color="b"
                                plt.scatter(x=key["domain"], y=key["PT"], color =  plot_color)
        FindXlim(cloverkey)
        #plt.ylim([1,5])
        plt.title(f'Peak to Total ratio for clover {cloverkey}')
        plt.xlabel('Domain')
        plt.ylabel('Peak-to-total ratio')
        plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
        

        file_name3 = 'eliade_{}_peaktotal.png'.format(cloverkey)
        plt.savefig(save_results_to + file_name3)
        plt.close()        

    ### EFFICIENCY FOR SEGMENTS

    # my_det_type=2

    # for cloverkey in list_of_clovers:
    #     for key in data:
    #         # print(key["serial"])
    #         #print(key["serial"].rstrip(key["serial"][-1]))
    #         if key["serial"].rstrip(key["serial"][-1]) == cloverkey:
    #             if key["detType"] == my_det_type:
    #                 #print('wowo')
    #                     for gammakey in list_of_sources:
    #                         if source == gammakey:                                
    #                             for element in gammatab[source]["gammas"]:
    #                                 plot_color="k"
    #                                 with open('json/gamma_set.json', 'r') as jason_file:
    #                                     gammaset=json.load(jason_file)
    #                                     plot_color=gammaset[source]['gammas'][element]
    #                                 #if((key["domain"]%10!=9) and (key["domain"]%10!=0)):
    #                                 print("segment")
    #                                 plt.scatter(x=key["domain"], y=key[source][element]["eff"], color =  plot_color,label=f"{element}")
    #     FindXlim(cloverkey)
    #     plt.ylim([0.0001, 0.00015])
    #     plt.title(f'Efficiency for clover {cloverkey} - segments')
    #     plt.xlabel('Domain')
    #     plt.ylabel('Efficiency (%)')
    #     plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
    #     legend_without_duplicate_labels(plt)       


    #     file_name4 = 'eliade_{}_efficiency_segments.png'.format(cloverkey)
    #     plt.savefig(save_results_to + file_name4)
    #     plt.close()  
    '''    
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
        #plt.ylim([0.00001,0.000013])
        title_clover=clover.rstrip(clover[-1])#CL29 instead of CL29G
        plt.title(f'Efficiency for clover {title_clover}')
        plt.xlabel('Domain')
        plt.ylabel('Efficiency (%)')
        plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
        legend_without_duplicate_labels(plt)
        
    file_name2 = 'eliade_{}_efficiency.png'.format(title_clover)
    plt.savefig(save_results_to + file_name2)
    plt.close()   

    for i in data:
        pt=i["PT"]
        clover=i["serial"]
        dom = i["domain"]

        plt.scatter(dom, pt, color='b')
        FindXlim(clover)
        #plt.ylim([0.1,0.15])
        title_clover=clover.rstrip(clover[-1])#CL29 instead of CL29G
        plt.title(f'Peak to Total ratio for clover {title_clover}')
        plt.xlabel('Domain')
        plt.ylabel('Peak-to-total ratio')
        plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
        

    file_name3 = 'eliade_{}_peaktotal.png'.format(title_clover)
    plt.savefig(save_results_to + file_name3)
    plt.close()   

    for i in data:
        clover=i["serial"]
        dom = i["domain"]
        if((dom%10!=9) and (dom%10!=0)):
            for key in i[source].keys():
                eff = i[source][key]["eff"]
                if float(key)==1173.238:
                    plt.scatter(x=dom, y=eff, color='r', label=f"{key}")
                elif float(key)==1332.513:
                    plt.scatter(x=dom, y=eff, color='b', label=f"{key}")
        FindXlim(clover)
        plt.ylim([0,0.01])
        title_clover=clover.rstrip(clover[-1])#CL29 instead of CL29G
        plt.title(f'Efficiency for clover {title_clover} - segments')
        plt.xlabel('Domain')
        plt.ylabel('Efficiency (%)')
        plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
        legend_without_duplicate_labels(plt)
        
    file_name4 = 'eliade_{}_efficiency_segments.png'.format(title_clover)
    plt.savefig(save_results_to + file_name4)
    plt.close() 
    '''
    return True

   
def PlotJsoncore(data, source):
    MakeDir(save_results_to)
    for i in data:
        #clover=i["serial"]
        dom = i["domain"]
        if(dom%10==9):
            for key in i[source].keys():
                eff = i[source][key]["eff"]
                if float(key)==1173.238:
                    plt.scatter(x=dom, y=eff, color='r', label=f"{key}")
                elif float(key)==1332.513:
                    plt.scatter(x=dom, y=eff, color='b', label=f"{key}")
        #FindXlim(clover)
        #plt.ylim([0.00001,0.000013])
        #title_clover=clover.rstrip(clover[-1])#CL29 instead of CL29G
        plt.title('Efficiency for core 1 ')
        plt.xlabel('Domain')
        plt.ylabel('Efficiency (%)')
        plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
        legend_without_duplicate_labels(plt)
        
        
    file_name5 = 'eliade_efficiency_core1.png'
    plt.savefig(save_results_to + file_name5)
    plt.close()   

    for i in data:
        
        dom = i["domain"]
        
        if(dom%10==9):
            for key in i[source].keys():
                res=i[source][key]["res"]
                if float(key)==1173.238:
                    plt.scatter(x=dom, y=res, color='r', label=f"{key}")
                elif float(key)==1332.513:
                    plt.scatter(x=dom, y=res, color='b', label=f"{key}")
            
        #FindXlim(clover)
        plt.ylim([1,5])
        #title_clover=clover.rstrip(clover[-1])#CL29 instead of CL29G
        plt.title(f'Resolution for core 1')
        plt.xlabel('Domain')
        plt.ylabel('Resolution (keV)')
        plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
        legend_without_duplicate_labels(plt)
        
        
    file_name6 = 'eliade_resolution_core1.png'
    plt.savefig(save_results_to + file_name6)
    plt.close()

    return  True

  

with open('calib_res_1.json', 'r') as js_file:
    data=json.load(js_file)

with open('json/gamma_sources.json', 'r') as jas_file:
    gammatab=json.load(jas_file)

# with open('json/gamma_set.json', 'r') as jason_file:
#     gammaset=json.load(jason_file)

# PlotJsondom(data, "60Co")
# PlotJsonclover(data, "60Co")


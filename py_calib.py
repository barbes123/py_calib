#! /usr/bin/python3

from os.path import exists #check if file exists

import os
import numpy as np
import matplotlib.pyplot as plt
import math, sys, os, json, subprocess
from pathlib import Path
from argparse import ArgumentParser
import inspect

try:
    ourpath = os.getenv('PY_CALIB')
    path='{}{}'.format(Path.home(),'/EliadeSorting/EliadeTools/RecalEnergy')
    print('PY_CALIB path: ', ourpath)
except:
    print('Cannont find environmental PY_CALIB variable, please, check')
    sys.exit()

sys.path.insert(1, 'lib')
sys.path.insert(1, '{}/lib'.format(ourpath))

from libCalib1 import TIsotope as TIso
from libCalib1 import TMeasurement as Tmeas
from libPlotEliade import PlotJsondom as PlotDomain
from libPlotEliade import PlotJsonclover as PlotClover
from libPlotEliade import PlotCeBr
from libPlotEliade import PlotJsoncore as PlotCore
from libPlotEliade import PlotCalibration
from libPlotEliade import PlotCalibrationCeBr
from TRecallEner import TRecallEner
from libSettings import SetUpRecallEner
from libSettings import SetUpRecallEnerFromJson
from utilities import *

current_directory = os.getcwd()

# print('Cur dir: ', current_directory)
if (current_directory == ourpath):
    print('Running directory is {}'.format(ourpath))
    datapath = '{}/data/'.format(current_directory)
else:
    datapath = '{}/'.format(current_directory)

print('Path to RecalEnergy {}'.format(path))
save_results_to = 'figures/'


print('Data path: ', datapath)

lutfile = 'LUT_ELIADE.json'
lutreallener = 'LUT_RECALL.json'
j_results = {}
list_results = []


# blPlot = True
debug = False
# OnlyCores = False
CalibDetType = 0

j_sources = None
blFirstElement = False




global my_params

class TStartParams:
    def __init__(self, server, runnbr, dom1, dom2, det_type, bg, grType, prefix):
        self.server = int(server)
        self.runnbr = runnbr
        self.dom1 = int(dom1)
        self.dom2 = int(dom2)
        self.det_type = det_type
        self.bg = bg
        self.grType = grType
        self.prefix = prefix

    def __repr__(self):
        print('=========================================')
        print('Server {}, Run {}, domFrom {}, domTo {}, bg {}'.format(self.server, self.runnbr, self.dom1, self.dom2, self.bg))
        print('=========================================')

class TPeak:
    def __init__(self, domain, line):
        self.domain  = domain
        self.area = float(line[3])
        self.Etable = line[7]
        # self.Etable = float(line[7])
        self.pos_ch = float(line [4])
        self.fwhm = float(line[5])
        self.Intensity = 0
        self.errIntesity = 0
        # self.eff = line[3]

    def __repr__(self):
        print('==============')
        print('dom {}, Etab {}, Area {}, Ch {}, fwhm {}'.format(self.domain, self.Etable, self.area, self.pos_ch, self.fwhm))
        print('==============')

# class TDetProperties:
#     def __init__(self, p2t):

def file_exists(myfile):
    if not exists(myfile):
        print('file_exists: File {} does not exist'.format(myfile))
        return False
    print('file_exists: File found {}'.format(myfile))
    return True
def MakeDir(path):
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
        print("The new directory {} is created!".format(path))

def MakeSymLink(file, link):
    # os.chdir('data')
    if file_exists(link):
        print('Link {} to file {} exists '.format(link, file))
        os.unlink(link)
    if file_exists(file):
        print(os.path.abspath(file))
        os.symlink(os.path.abspath(file), link)
        print('Link {} to file {} created '.format(link, file))

def ProcessFitDataStr(dom, my_source, lines, j_src, j_lut ):
    print('ProcessFitDataStr: now  split lines')

    if debug:
        print(lines)

    words = [s for s in lines.split('#2') if s]
    # del words[0]
    words.pop(0)

    PeakList = []
    cal = []
    for word in words:
        if 'Cal1' in word:#for poly3 change to Cal2
            cal = []
            temp = [t for t in word.split('[ ') if t]
            # print("#########",temp)
            # print("!!!!!temp[1]", temp[1])
            temp1 = [t1 for t1 in temp[1].split(' ') if t1]
            # print("#########",temp1)
            del temp1[len(temp1) -1]
            if my_params.bg == 1:
                del temp1[len(temp1) - 1]
            for s in temp1:
                cal.append(float(s))
            print('Calibration for domain {} {}'.format(dom, cal))
            for item in j_lut:
                if item['domain'] == dom:
                    # print('Old calibration {}'.format(item['pol_list']))
                    item['pol_list'] = cal
                    # print('New calibration {}'.format(item['pol_list']))

        for gamma in j_src[my_source]['gammas']:
            if gamma in word:
                print('Found ',gamma,' ', word)
                numbers = [s for s in word.split(' ') if s]
                peak = TPeak(dom, numbers)
                peak.Intensity = j_src[my_source]['gammas'][gamma][1]
                peak.errIntensity = j_src[my_source]['gammas'][gamma][2] #absolute or relative ?
                PeakList.append(peak)
                # peak.__str__()

    if len(PeakList) == 0:
        print('ProcessFitDataStr::: no peaks were found for dom {}'.format(dom))
    else:
        FillResults2json(dom, PeakList, cal)
        # print('Print PeakList {} elements'.format(len(PeakList)))
        for p in PeakList:
            p.__str__()

def FillResults2json(dom, list, cal):
    jsondata = {}
    content = {}
    source = {}
    jsondata['domain'] = dom


    for item in j_lut:
        if item['domain'] == dom:
            jsondata['serial'] = item['serial']
            jsondata['detType'] = item['detType']

    peaksum = 0
    for peak in list:
        content = {}
        content['eff'] = peak.area/(n_decays_int*peak.Intensity)  *100
        if peak.area and n_decays_int:
            try:
                content['err_eff'] = np.sqrt((1/peak.area + 1/n_decays_int + peak.errIntensity/peak.Intensity**2)*100)*peak.area/(n_decays_int*peak.Intensity)*100
            except: 
                content['err_eff'] = 0
        #print(n_decays_sum, 'this is sum of decays')
        content['res'] = peak.fwhm/peak.pos_ch*float(peak.  Etable)
        content['err_res'] = 0.1
        content['pos_ch'] = peak.pos_ch
        # jsondata[peak.Etable] = content
        source[peak.Etable] = content
        peaksum = peaksum + peak.area
        # print('Dump to json peak: {} {} {}'.format(peak.Etable, peak.pos_ch, peak.fwhm))
        # print(source)
        # print(source[peak.Etable])
        # print('Dump to json peak: {} {} {}'.format(source[peak.Etable].Etable, source[peak.Etable].pos_ch, source[peak.Etable].fwhm))

    if debug == True:
        print('source {}'.format(source))


    jsondata['PT'] = peaksum/total
    if peaksum and total:
        try:
            jsondata['err_PT'] = np.sqrt(1/peaksum+1/total)*peaksum/total
        except:
            jsondata['err_PT'] = 0
    jsondata['pol_list'] = cal

    jsondata[my_source.name] = source

    list_results.append(jsondata)
    if debug == True:
        print(list_results)
    return True

# def load_json(file):
#     fname = '{}'.format(file)
#     if not file_exists(fname):
#         print('load_json:: file {} is not found as called from {}'.format(file, inspect.stack()[1].function))
#         sys.exit()
#     with open(fname,'r') as myfile:
#         return json.load(myfile)

def SumAsci(file):
    sum = 0
    with open('{}'.format(file),'r') as ifile:
        for line in ifile:
            try:
                #num = int(line)
                num = float(line)
                sum+=num
            except ValueError:
                print('{} is not a number'.format(line.rstrip()))
                return 0
    if debug:
        print('Total sum: {}'.format(sum))
    return sum

def SumAsciLimits(file, lim1, lim2):
    sum = 0
    nnline = 0
    # lim1=400
    # lim2=3000
    with open('{}'.format(file),'r') as ifile:
        for line in ifile:
            if (nnline not in range(lim1,lim2)):
                nnline += 1
                continue
            try:
                num = float(line)
                sum+=num
            except ValueError:
                print('{} is not a number'.format(line.rstrip()))
                # return 0
            nnline+=1
    if debug:
        print('Total sum: {}'.format(sum))
    return sum


def main():

    # run = 1
    # server = 6

    if not file_exists('{}'.format(path)):
        print('RecalEnergy cannot be found. Ciao.')
        sys.exit()

    j_sources = load_json('{}/json/gamma_sources.json'.format(ourpath))
    #j_data = load_json('json/run_table.json')
    j_data = load_json('{}/json/run_table_S{}.json'.format(ourpath, my_params.server))
    global j_lut
    j_lut = load_json('{}/{}'.format(ourpath, lutfile))
    global  j_lut_recall
    j_lut_recall = load_json('{}/{}'.format(ourpath, lutreallener))

    # MakeSymLink('HPGe.spe','mDelila_raw_py_1.spe')
    # MakeSymLink('SEG.spe','mDelila_raw_py_2.spe')
    # MakeSymLink('LaBr.spe','mDelila_raw_py_3.spe')

    MakeSymLink('HPGe.spe','{}_py_1.spe'.format(prefix))
    MakeSymLink('SEG.spe', '{}_py_2.spe'.format(prefix))
    MakeSymLink('LaBr.spe','{}_py_3.spe'.format(prefix))

    # print('Printing source table')
    print('my_params.run', my_params.runnbr)

    my_run = Tmeas(None,None,None,None,None,None)
    my_run.setup_run_from_json(j_data, my_params.runnbr, my_params.server)
    print(my_run.__str__())

    global my_source
    my_source = TIso(None, None, None, None)
    my_source.setup_source_from_json(j_sources, my_run.source)
    if my_run.tstop < my_run.tstart:
        print("Check start and stop time of this run. Tstart must be bigger than Tstop")
        sys.exit()
    global n_decays_sum
    n_decays_sum, n_decays_err= my_source.GetNdecaysIntegral(my_run.tstart, my_run.tstop)
    global n_decays_int
    n_decays_int = my_source.GetNdecays(my_run.tstart, my_run.tstop)
    print(my_source.__str__())
    print('sum {}; err {}; int {}'.format(n_decays_sum, n_decays_err, n_decays_int))

    # blBackGround = False
    # print('!!!!!!',my_params.bg)
    # if my_params.bg > 0:
    #     blBackGround = True

    # print('Gammas ', j_sources['Co60']['gammas'])
    # global myCurrentSetting
    # myCurrentSetting = TRecallEner(800,1200,100,4, 200, 1500)

    for domain in range (my_params.dom1, my_params.dom2+1):
        current_det = 0
        if my_params.det_type != 0:
            for entry in j_lut:
                if entry['domain'] == domain:
                    current_det = entry['detType']
                    # print('~ ',domain  ,'!!!!!!!!!!!!!!!!!!!!!!!!!! ', entry['detType'], ' ' ,entry['channel'], ' ', entry['serial'], ' ', current_det, ' ',my_params.det_type)
                    break

        if my_params.det_type != current_det:
            continue

        # myCurrentSetting = SetUpRecallEner(j_lut, domain, my_source.name)
        myCurrentSetting = SetUpRecallEnerFromJson(domain, j_lut_recall)
        if debug:
            print('I am trying to do fit for domain {}'.format(domain))
        current_file = '{}{}_py_{}.spe'.format(datapath,prefix,domain)
        # current_file = '{}mDelila_raw_py_{}.spe'.format(datapath, domain)

        if file_exists(current_file):
            # if blBackGround:
            if my_params.bg == 1:
                src = '{} -ener 1460.82 -ener 2614.51'.format(my_source.name)
            else:
                src = my_source.name

            # print(prefix)
            # sys.exit()
            # command_line = '{} -spe {} -{} -lim {} {} -fmt A 16384 -dwa {} {} -poly2 -v 2'.format(path, current_file, my_source.name, myCurrentSetting.limDown, myCurrentSetting.limUp, myCurrentSetting.fwhm, myCurrentSetting.ampl)
            # command_line = '{} -spe {} -{} -ener {} -ener {} -lim {} {} -fmt A 16384 -dwa {} {} -poly2 -v 2'.format(path, current_file, my_source.name,'1460.82','2614.51', myCurrentSetting.limDown, myCurrentSetting.limUp, myCurrentSetting.fwhm, myCurrentSetting.ampl)
            #command_line = '{} -spe {} -{} -lim {} {} -fmt A 16384 -dwa {} {} -poly2 -v 2'.format(path, current_file, src, myCurrentSetting.limDown, myCurrentSetting.limUp, myCurrentSetting.fwhm, myCurrentSetting.ampl)
            command_line = '{} -spe {} -{} -lim {} {} -fmt A 16384 -dwa {} {} -poly1 -v 2'.format(path, current_file, src, myCurrentSetting.limDown, myCurrentSetting.limUp, myCurrentSetting.fwhm, myCurrentSetting.ampl)
            print('{}'.format(command_line))
            if debug:
                print('I am ready to do fit for domain {} : '.format(domain))

            result_scr = subprocess.run(['{}'.format(command_line)], shell=True, capture_output=True)
            # print(result_scr)
            fitdata = result_scr.stdout.decode()
            # print(fitdata)
            global total
            #total = SumAsci(current_file)
            total = SumAsciLimits(current_file, myCurrentSetting.limStart, myCurrentSetting.limStop)
            ProcessFitDataStr(domain, my_source.name, fitdata, j_sources, j_lut)


    # with open('new_{}'.format(lutfile), 'w') as ofile:
    #     js_tab = json.dump(j_lut, ofile, indent=3, default=str)

    # with open('calib_res_{}.json'.format(my_run.run), 'w') as ofile:
    #     ofile.write(j_results)

    with open('{}calib_res_{}.json'.format(datapath, my_run.run), 'w') as ofile:
        js_tab = json.dump(list_results, ofile, indent=3, default=str)


    with open('{}calib_res_{}.json'.format(datapath, my_run.run), 'r') as ifile:
        js_tab = json.load(ifile)
        # if blPlot == True:
        if my_params.grType != 'none':
            PlotDomain(js_tab, j_sources, my_source.name, j_lut, my_params.grType)

            PlotClover(js_tab, j_sources, my_source.name, 1, j_lut, my_params.grType)
            PlotClover(js_tab, j_sources, my_source.name, 2, j_lut, my_params.grType)

            PlotCore(js_tab, j_sources, my_source.name, j_lut, 1, my_params.grType)
            PlotCalibration(js_tab, j_sources, my_source.name, j_lut, 1, my_params.grType)
            PlotCalibration(js_tab, j_sources, my_source.name, j_lut, 2, my_params.grType)

            PlotCeBr(js_tab, j_sources, my_source.name, 3, j_lut, my_params.grType)
            PlotCalibrationCeBr(js_tab, j_sources, my_source.name, j_lut, 3, my_params.grType)



    # global j_res
    # with open('{}calib_res_{}.json'.format(datapath, my_run.run), 'r') as ifile:
        # j_res = json.load(ifile)

if __name__ == "__main__":
    dom1 = 100
    dom2 = 109
    server = 9
    runnbr = 63
    det_type = 0
    bg = 0
    grType = 'jpg'
    prefix = 'mDelila_raw'

    parser = ArgumentParser()

    parser.add_argument("-s", "--server", dest="server", default=server, type=int, choices=range(10),
                        help="DAQ ELIADE server, default = {}".format(server))
    parser.add_argument("-r", "--run", type=int,
                        dest="runnbr", default=runnbr,
                        help="Run number, default = {}".format(runnbr))
    parser.add_argument("-d", "--domains",  nargs=2,
                        dest="dom", default=[dom1, dom2],
                        help="from domain, default = {} {}".format(dom1, dom2))
    parser.add_argument("-t", "--type",
                        dest="det_type", default=det_type,  type=int,
                        help="type of detector to be calibrated; default = 0".format(det_type))
    parser.add_argument("-b", "--background",
                        dest="bg", default=bg, type=int,
                        help="to take in energy calib background lines; default = {}".format(bg))
    parser.add_argument("-gr", "--graphic type: eps, jpg or none ",
                        dest="grType", default=grType, type=str, choices=('eps', 'jpeg', 'jpg', 'png', 'svg', 'svgz', 'tif', 'tiff', 'webp','none'),
                        # eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff, webp
                        help="Available graphic output: eps, jpeg, jpg, png, svg, svgz, tif, tiff, webp or none (no graphs); default = {}".format(grType))
    parser.add_argument("-prefix", "--prefix to the files to be analyzed",
                        dest="prefix", default=grType, type=str,
                        help="Prefix for matrix (TH2) to be analyzed mDelila_raw or mDelila or ...".format(
                            prefix))


    config = parser.parse_args()

    print(config)

    if not file_exists('{}/{}'.format(ourpath, lutfile)):
        print('No LUT_ELIADE.json is given: {}. Cannot continue.'.format(lutfile))
        sys.exit()

    if not file_exists('{}/{}'.format(ourpath, lutreallener)):
        print('No LUT_RECALL.json is given: {}. Cannot continue.'.format(lutreallener))
        sys.exit()

    my_params = TStartParams(config.server, config.runnbr, config.dom[0], config.dom[1], config.det_type, config.bg, config.grType, config.prefix)


#     print('Input Parameters: server, run, domDown, domUp, detType')
#     n = len(sys.argv)
#     print('Number of arguments {}'.format(n))
#     if n == 1: #no arguments
#        print('Default input values')
#        my_params = TStartParams(6, 1, 109, 119)
#        # print('Start Params ', my_params.__str__())
#     elif n == 5 or n == 6: #2 arguments
#        print('Settings input values from arguments')
#        dom1 = int(sys.argv[3])
#        dom2 = int(sys.argv[4])
#        if dom1 >= dom2:
#            my_params = TStartParams(sys.argv[1], sys.argv[2], dom2, dom1)
#        else:
#            my_params = TStartParams(sys.argv[1], sys.argv[2], dom1, dom2)
#        if n == 6:
#             tmp = int(sys.argv[5])
#             if tmp >= 0 and tmp < 10:
#                 CalibDetType = tmp
#                 if CalibDetType == 1:
#                     OnlyCores = True #to be changed by Raluca or by me ;-)
#             else:
#                 print('CalibDetType is {} not known; setup default 0'.format(tmp))
#     else:
#        print('Wrong number of parameters, ciao')
#        sys.exit()
   
#     print('Start Params are set', my_params.__str__())
#    #
    main()

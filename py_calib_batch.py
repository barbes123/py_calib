#!/usr/bin/python3

# Calculate efficiency using n_decays_sum and relative intensities

import os
import numpy as np
import matplotlib.pyplot as plt
import math, sys, json, subprocess
from pathlib import Path
from argparse import ArgumentParser
from datetime import datetime
from os.path import exists
from math import log

try:
    ourpath = os.getenv('PY_CALIB')
    path = os.path.dirname(ourpath)+'/GammaSet'
    print('PY_CALIB path: ', ourpath)
    print('path for GammaSet: ', path)
except:
    print('Cannot find environmental PY_CALIB variable, please check')
    sys.exit()

# Add library paths
sys.path.insert(1, 'lib')
sys.path.insert(1, '{}/lib'.format(ourpath))

# Import required modules
from libCalib1 import TIsotope as TIso
from libCalib1 import TMeasurement as Tmeas
from libPlotEliadeAA import PlotJsondom as PlotDomain
from libPlotEliadeAA import PlotJsonclover as PlotClover
from libPlotEliadeAA import PlotCeBr
from libPlotEliadeAA import PlotCore as PlotCore
from libPlotEliadeAA import PlotCalibration
from libPlotEliadeAA import Save_results_to_path as save_results_to_path
from libPlotEliadeAA import PlotCalibrationCeBr
from TRecallEner import TRecallEner
from libSettings import SetUpRecallEner
from libSettings import SetUpRecallEnerFromJson
from utilities import *
from libLists import lists_of_gamma_background
from libCalibAA import IsotopeData
from plot_multiple_function import plot_peak_positions_vs_time

# Get current directory
current_directory = os.getcwd()
datapath = '{}/'.format(current_directory)

print('Path to RecalEnergy {}'.format(path))

# Configuration files
lutfile = 'LUT_ELIADE.json'
lutreallener = 'LUT_RECALL.json'
lut_recall_fname = '{}/{}'.format(ourpath, lutreallener)

# Global variables
j_results = {}
list_results = []
debug = False

# Initialize params globally to be accessible in functions
global my_params

class TStartParams:
    def __init__(self, server, runnbr, dom1, dom2, det_type, bg, grType, prefix, fitrange, peakthresh, vol0, vol1):
        self.server = int(server)
        self.runnbr = runnbr
        # self.volnbr = volnbr
        self.dom1 = int(dom1)
        self.dom2 = int(dom2)
        self.vol0 = int(vol0)
        self.vol1 = int(vol1)
        self.det_type = det_type
        self.bg = bg
        self.grType = grType
        self.prefix = prefix
        self.fitrange = fitrange
        self.peakthresh = peakthresh
        # self.start_vol = start_vol
        # self.end_vol = end_vol


    def __repr__(self):
        print('=========================================')
        print('Server {}, Run {}, domFrom {}, domTo {}, bg {}'.format(self.server, self.runnbr, self.dom1, self.dom2, self.bg))
        print('Fit Range {}, Peak Threshold {}'.format(self.fitrange, self.peakthresh))
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
    print('ProcessFitDataStr: now  split lines, source is',my_source)

    if debug:
        print(lines)

    words = [s for s in lines.split('#2') if s]
    # del words[0]
    words.pop(0)

    PeakList = []
    cal = []
    for word in words:
        #if 'Cal2' in word:#for poly3 change to Cal2
        #    cal = []
        #    temp = [t for t in word.split('Cal2=[ ') if t]
        if 'Cal' in word:#for poly3 change to Cal2
            cal = []
            temp = [t for t in word.split('[ ') if t]
            # print("#########",temp)
            # print("!!!!!temp[1]", temp[1])
            temp1 = [t1 for t1 in temp[1].split(' ') if t1]
            # print("#########",temp1)
            del temp1[len(temp1) -1]
            # if my_params.bg == 1:
                # del temp1[len(temp1) - 1]
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
        if my_params.bg == 1:
            for gamma_bg in lists_of_gamma_background:
                if gamma_bg in word:
                    print('Found BG ', gamma_bg, ' ', word)
                    numbers = [s for s in word.split(' ') if s]
                    peak = TPeak(dom, numbers)
                    # peak.Intensity = j_src[my_source]['gammas'][gamma][1]
                    # peak.errIntensity = j_src[my_source]['gammas'][gamma][2]  # absolute or relative ?
                    PeakList.append(peak)
                    # print('peak',peak)
                    # sys.exit()

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
    source_bg = {}
    jsondata['domain'] = dom


    for item in j_lut:
        if item['domain'] == dom:
            jsondata['serial'] = item['serial']
            jsondata['detType'] = item['detType']

    peaksum = 0
    for peak in list:
        if peak.Etable in lists_of_gamma_background:
            continue
        content = {}
        content['eff'] = peak.area/(n_decays_int*peak.Intensity)  *100
        if peak.area and n_decays_int:
            try:
                content['err_eff'] = np.sqrt((1/peak.area + 1/n_decays_int + peak.errIntensity/peak.Intensity**2)*100)*peak.area/(n_decays_int*peak.Intensity)*100
            except: 
                content['err_eff'] = 0
        #print(n_decays_sum, 'this is sum of decays')
        content['res'] = peak.fwhm/peak.pos_ch*float(peak.Etable)
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

    if my_params.bg == 1:
        for peak_bg in list:
            # print('ffff',type(peak_bg.Etable),peak_bg.Etable)
            if peak_bg.Etable in lists_of_gamma_background:
                print('BACK', peak_bg.pos_ch, peak_bg.fwhm)
                content = {}
                content['res'] = peak_bg.fwhm / peak_bg.pos_ch * float(peak_bg.Etable)
                content['err_res'] = 0.1
                content['pos_ch'] = peak_bg.pos_ch
                source_bg[str(peak_bg.Etable)] = content
        jsondata['bg'] = source_bg

    list_results.append(jsondata)
    if debug == True:
        print(list_results)
    return True

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

def read_gamma_sources():
    ourpath = os.getenv('PY_CALIB')
    print('read_gamma_sources: {}'.format(ourpath))
    if file_exists('{}/json/gamma_sources.json'.format(ourpath)):
        gamma_sources_json = load_json('{}/json/gamma_sources.json'.format(ourpath))
        return gamma_sources_json
    return None

def get_serial_detType(domain, lut_data):
    for entry in lut_data:
        if entry.get("domain") == domain:
            serial = entry.get("serial")
            detType = entry.get("detType")
            return serial, detType
    return None, None

def update_domain_serial(json_path, lut_data):
    with open(json_path, 'r') as file:
        data = json.load(file)

    for entry in data:
        serial, detType = get_serial_detType(entry['domain'], lut_data)
        entry['serial'] = serial
        entry['detType'] = detType

    with open(json_path, 'w') as file:
        json.dump(data, file, indent=3)

import math
from datetime import datetime

def calculateTotalActivity():
    print("///////////////////////////////////////////////////")
    #print("start", my_params.tstart)
    #print("stop", my_params.tstop)
    lambda_val =  log(2, math.e)  / (5.27 * 365.25 * 24 * 3600)  # Convert 5.27 years to seconds
    print("Lambda value: ", lambda_val)
    # Define moments t1 and t2
    t1 = "2024-10-15 17:31:45"
    t2 = "2024-10-28 11:02:24"
    t1 = datetime.strptime(t1, "%Y-%m-%d %H:%M:%S")
    t2 = datetime.strptime(t2, "%Y-%m-%d %H:%M:%S")
    # Calculate elapsed time in seconds
    time_elapsed = (t2 - t1).total_seconds()
    print("Time elapsed: ", time_elapsed)
    # Initial activity
    A0 = 92270  # Should be set according to your data
    # Activity at t2
    A_t = A0 * math.exp(-lambda_val * time_elapsed)
    # Total number of decays between t1 and t2
    N_decay = (A0 / lambda_val) * (1 - math.exp(-lambda_val * time_elapsed))
    return N_decay

def main():

    # run = 1
    # server = 6

    if not file_exists('{}'.format(path)):
        print('RecalEnergy cannot be found. Ciao.')
        sys.exit()

    j_sources = load_json('{}/json/gamma_sources.json'.format(ourpath))
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
    my_source = TIso(None, None, None, None, None)
    my_source.setup_source_from_json(j_sources, my_run.source)
    if my_run.tstop < my_run.tstart:
        print("Check start and stop time of this run. Tstart must be bigger than Tstop")
        sys.exit()
    global n_decays_sum
    n_decays_sum, n_decays_err, newt1, newt2, newa0, newdeccst= my_source.GetNdecaysIntegral2(my_run.tstart, my_run.tstop)
    global n_decays_int
    n_decays_int = my_source.GetNdecays(my_run.tstart, my_run.tstop)
    print(my_source.__str__())
    print('sum {}; err {}; int {}'.format(n_decays_sum, n_decays_err, n_decays_int))

    # Setup source for fitting
    source4Fit = my_source.name
    if '60Co' in source4Fit:
        source4Fit = '60Co'
    #elif '54Mn' in source4Fit:
    #    source4Fit = 'ener 834.848 -ener 511.006'
    src = source4Fit
    if my_params.bg == 1:
        src = '{}'.format(source4Fit)
        for gamma in lists_of_gamma_background:
            src = src + ' -ener {}'.format(gamma)

    #    path, my_params.runnbr, my_params.volnbr, my_params.server, lut_recall_fname, my_params.dom1, my_params.dom2, src, 1)
    for volnbr in range(my_params.vol0, my_params.vol1 + 1):
        command_line = (
            f"{path}/gammaset -f selected_run_{my_params.runnbr}_{volnbr}_eliadeS{my_params.server}.root "
            f"-rp {lut_recall_fname} -sc {my_params.dom1} -ec {my_params.dom2} -s {src} -fd 3 "
            f"-br {my_params.fitrange} -peakthresh {my_params.peakthresh} -rb 1 -hist {my_params.prefix}"
        )
        print("Command to run:")
        print(command_line)

        result_scr = subprocess.run(['{}'.format(command_line)], shell=True)

        result = plot_peak_positions_vs_time(
            target_run=my_params.runnbr,
            domain_start=my_params.dom1,
            domain_end=my_params.dom2,
            target_S=my_params.server,
            verbose=True,    # Set to False to suppress output
            create_plots=True  # Set to False to only extract data without creating plots
         )

    if result is None:
        print("Failed to process data")
        return
    
    # Access the extracted data
    print(f"Total data points: {len(result['y'])}")
    print(f"Time range: {min(result['x'])} - {max(result['x'])} ps")
    print(f"Position range: {min(result['y']):.2f} - {max(result['y']):.2f}")
    print(f"Unique isotopes: {sorted(result['unique_isotopes'])}")
    print(f"Unique domains: {sorted(set(result['domains']))}")
    
    if 'output_path' in result:
        print(f"Plots saved to: {result['output_path']}")
    
    #print('command_line////////////////////', command_line)

    #print('n_decays_sum', n_decays_sum)
    #print('I am ready to run c++')
    #json_path = '{}{}/{}_peaks_data.json'.format(datapath, my_run.run, my_run.run)
    #json_path = '{}selected_run_{}_{}_eliadeS{}_calib/selected_run_{}_{}_eliadeS{}.json'.format(datapath,my_params.runnbr, my_params.volnbr, my_params.server,my_params.runnbr, my_params.volnbr, my_params.server)
    #print('json_path.//////////////////////////////////////// ', json_path)
    #if not norun:
    #    result_scr = subprocess.run(['{}'.format(command_line)], shell=True)
    #print('I finished c++')

   

if __name__ == "__main__":
    dom1 = 100
    dom2 = 109
    vol0 = 0
    vol1 = 0
    server = 9
    runnbr = 63
    volnbr = 999
    det_type = 0
    bg = 0
    grType = 'jpg'
    prefix = 'mEliade'
    norun = False
    # lut_recall = '~/onlineEliade/LookUpTables/s1/LUT_RECALL_S1_CL29.json'

    parser = ArgumentParser()

    parser.add_argument("-s", "--server", dest="server", default=server, type=int, choices=range(10),
                        help="DAQ ELIADE server, default = {}".format(server))

    parser.add_argument("-r", "--run", type=int,
                        dest="runnbr", default=runnbr,
                        help="Run number, default = {}".format(runnbr))
    #
    # parser.add_argument("-recall", "--LUT_RECALL", type=int,
    #                     dest="lut_recall", default=lut_recall,
    #                     help="LUT_RECALL, default = {}".format(lut_recall))

    # parser.add_argument("-vol", "--volume", type=int,
    #                     dest="volnbr", default=volnbr,
    #                     help="volume number, default = {}".format(volnbr))



    parser.add_argument("-vol", "--volumes", nargs=2, type=int,
                        dest="vol", default=[vol0, vol1],
                        help="Volume range from start to end, default = {} {}".format(vol0, vol1))

    parser.add_argument('--norun', action='store_true', help="Do only plotting on already analyzed set")


    parser.add_argument("-d", "--domains",  nargs=2,
                        dest="dom", default=[dom1, dom2],
                        help="from domain, default = {} {}".format(dom1, dom2))

    parser.add_argument("-t", "--type",
                        dest="det_type", default=det_type,  type=int,
                        help="type of detector to be calibrated; default = 0".format(det_type))

    parser.add_argument("-b", "--background",
                        dest="bg", default=bg, type=int,
                        help="to take in energy calib background lines (1); default = {}".format(bg))
    parser.add_argument("-gr", "--graphic type: eps, jpg or none ",
                        dest="grType", default=grType, type=str, choices=('eps', 'jpeg', 'jpg', 'png', 'svg', 'svgz', 'tif', 'tiff', 'webp','none'),
                        # eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff, webp
                        help="Available graphic output: eps, jpeg, jpg, png, svg, svgz, tif, tiff, webp or none (no graphs); default = {}".format(grType))
    parser.add_argument("-prefix", "--prefix to the files to be analyzed",
                        dest="prefix", default=grType, type=str,
                        help="Prefix for matrix (TH2) to be analyzed mDelila_raw or mDelila or ...".format(
                            prefix))
    parser.add_argument("--fitrange", type=int, dest="fitrange", default=10,
                        help="Basic range (left/right) for C++ peak fitting, default = 10")
    parser.add_argument("--peakthresh", type=float, dest="peakthresh", default=0.0001,
                        help="Peak threshold for C++ analysis, default = 0.0001")
    parser.add_argument("--start_vol", type=int, default=1,
                    help="Start volume number for the loop, default = 1")

    parser.add_argument("--end_vol", type=int, default=1,
                    help="End volume number for the loop, default = 1")

    config = parser.parse_args()

    if config.norun:
        norun = True

    print(config)

    if not file_exists('{}/{}'.format(ourpath, lutfile)):
        print('No LUT_ELIADE.json is given: {}. Cannot continue.'.format(lutfile))
        sys.exit()

    if not file_exists('{}/{}'.format(ourpath, lutreallener)):
        print('No LUT_RECALL.json is given: {}. Cannot continue.'.format(lutreallener))
        sys.exit()

    my_params = TStartParams(
        server=config.server,
        runnbr=config.runnbr,
        dom1=config.dom[0],
        dom2=config.dom[1],
        det_type=config.det_type,
        bg=config.bg,
        grType=config.grType,
        prefix=config.prefix,
        fitrange=config.fitrange,
        peakthresh=config.peakthresh,
        vol0=config.vol[0],
        vol1=config.vol[1]
    )


    for name, value in vars(my_params).items():
        print(f"{name}: {value}")

# my_params = TStartParams(config.server, config.runnbr, config.volnbr, config.dom[0], config.dom[1],
#                             config.det_type, config.bg, config.grType, config.prefix, config.fitrange, config.peakthresh,
#                             config.start_vol, config.end_vol)


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

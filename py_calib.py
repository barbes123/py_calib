#! /usr/bin/python3

from os.path import exists #check if file exists
import numpy as np
import matplotlib.pyplot as plt
import math, sys, os, json, subprocess
from libCalib1 import TIsotope as TIso
from libCalib1 import TMeasurement as Tmeas
from libPlotEliade import PlotJsondom as PlotDomain
from libPlotEliade import PlotJsonclover as PlotClover
from pathlib import Path
from libSettings import run20Co60source

path='{}{}'.format(Path.home(),'/EliadeSorting/EliadeTools/RecalEnergy')
print('Path to RecalEnergy {}'.format(path))
save_results_to = 'figures/'

blPlot = True
debug = False

lutfile = 'LUT_ELIADE.json'
# lutfile = 'LUT_ELIADE_S9_run20_raluca.json'

j_results = {}

list_results = []

blFirstElement = False


j_sources = None

global my_params


# class TRecallEner:
#     def __init__(self, limDown, limUp, ampl, fwhm):
#         self.limDown = limDown
#         self.limUp = limUp
#         self.ampl = ampl
#         self.fwhm = fwhm

class TStartParams:
    def __init__(self, server, runnbr, dom1, dom2):
        self.server = int(server)
        self.runnbr = int(runnbr)
        self.dom1 = int(dom1)
        self.dom2 = int(dom2)

    def __repr__(self):
        print('=========================================')
        print('Server {}, Run {}, domFrom {}, domTo {}'.format(self.server, self.runnbr, self.dom1, self.dom2))
        print('=========================================')

class TPeak:
    def __init__(self, domain, line):
        self.domain  = domain
        self.area = float(line[3])
        self.Etable = float(line[7])
        self.pos_ch = float(line [4])
        self.fwhm = float(line[5])
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


def ProcessFitDataStr(dom, lines, j_src, j_lut ):
    print('ProcessFitDataStr: now  split lines')

    # print(lines)
    words = [s for s in lines.split('#2') if s]
    # del words[0]
    words.pop(0)

    PeakList = []
    cal = []

    for word in words:
        if 'Cal' in word:
            cal = []
            temp = [t for t in word.split('[ ') if t]
            temp1 = [t1 for t1 in temp[1].split(' ') if t1]
            del temp1[len(temp1) - 1]
            for s in temp1:
                cal.append(s)
            print('Calibration for domain {} {}'.format(dom, cal))
            for item in j_lut:
                if item['domain'] == dom:
                    # print('Old calibration {}'.format(item['pol_list']))
                    item['pol_list'] = cal
                    # print('New calibration {}'.format(item['pol_list']))

        for gamma in j_src['60Co']['gammas']:
            if gamma in word:
                print('Found ',gamma,' ', word)
                numbers = [s for s in word.split(' ') if s]
                peak = TPeak(dom, numbers)
                PeakList.append(peak)
                # peak.__str__()

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
        content['eff'] = peak.area/n_decays_sum*100
        content['res'] = peak.fwhm/peak.pos_ch*peak.Etable
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
    jsondata['pol_list'] = cal

    jsondata[my_source.name] = source

    list_results.append(jsondata)
    if debug == True:
        print(list_results)
    return True

def load_json(file):
    fname = '{}'.format(file)
    if not file_exists(fname):
        sys.exit()
    with open(fname,'r') as myfile:
        return json.load(myfile)

def SumAsci(file):
    sum = 0
    with open('{}'.format(file),'r') as ifile:
        for line in ifile:
            try:
                num = int(line)
                sum+=num
            except ValueError:
                print('{} is not a number'.format(line.rstrip()))
                return 0
    if debug:
        print('Total sum: {}'.format(sum))
    return sum

def SetUpRecallEner(dom):
<<<<<<< HEAD
    run20Co60source(dom)
=======
    pass
    # run22Co60source(dom)
>>>>>>> a292c9eb46989c5f9f87e3a1ba90f4a8cc8900b5

def main():

    # run = 1
    # server = 6

    if not file_exists('{}'.format(path)):
        print('RecalEnergy cannot be found. Ciao.')
        sys.exit()

    j_sources = load_json('gamma_sources.json')
    j_data = load_json('run_table.json')
    global j_lut
    j_lut = load_json('{}'.format(lutfile))

    # print('Printing source table')
    print('my_params.run', my_params.runnbr)

    my_run = Tmeas(None,None,None,None,None,None)
    my_run.setup_run_from_json(j_data, my_params.runnbr, my_params.server)
    print(my_run.__str__())

    global my_source
    my_source = TIso(None, None, None, None)
    my_source.setup_source_from_json(j_sources, my_run.source)
    global n_decays_sum
    n_decays_sum= my_source.GetNdecaysIntegral(my_run.tstart, my_run.tstop)
    global n_decays_int
    n_decays_int = my_source.GetNdecays(my_run.tstart, my_run.tstop)
    print(my_source.__str__())
    # print('sum {}; int {}'.format(n_decays_sum, n_decays_int))

    # print('Gammas ', j_sources['Co60']['gammas'])

    # limDown = 800
    # limUp = 1200

    global myCurrentSetting

<<<<<<< HEAD
    for domain in range (109,120):
        if (domain != 109) and (domain != 119):
            continue
        myCurrentSetting = run20Co60source(domain)
=======
    for domain in range (my_params.dom1, my_params.dom2):
        # if (domain != 109) and (domain != 119):
        #     continue
        SetUpRecallEner(domain)
>>>>>>> a292c9eb46989c5f9f87e3a1ba90f4a8cc8900b5
        if debug:
            print('I am trying to do fit for domain {}'.format(domain))
        current_file = 'data/mDelila_raw_py_{}.spe'.format(domain)
        if file_exists(current_file):
            command_line = '{} -spe {} -{} -lim {} {} -fmt A 16384 -dwa {} {} -poly2 -v 2'.format(path, current_file, my_source.name, myCurrentSetting.limDown, myCurrentSetting.limUp, myCurrentSetting.fwhm, myCurrentSetting.ampl)
            if debug:
                print('I am ready to do fit for domain {} : '.format(domain))
                print('{}'.format(command_line))
            result_scr = subprocess.run(['{}'.format(command_line)], shell=True, capture_output=True)
            # print(result_scr)
            fitdata = result_scr.stdout.decode()
            # print(fitdata)
            global total
            total = SumAsci(current_file)
            ProcessFitDataStr(domain, fitdata, j_sources, j_lut)


    with open('new_{}'.format(lutfile), 'w') as ofile:
        js_tab = json.dump(j_lut, ofile, indent=3, default=str)

    # with open('calib_res_{}.json'.format(my_run.run), 'w') as ofile:
    #     ofile.write(j_results)

    with open('calib_res_{}.json'.format(my_run.run), 'w') as ofile:
        js_tab = json.dump(list_results, ofile, indent=3, default=str)


    with open('calib_res_{}.json'.format(my_run.run), 'r') as ifile:
        js_tab = json.load(ifile)
        if blPlot == True:
            PlotDomain(js_tab, my_source.name)
            PlotClover(js_tab, my_source.name)

    global j_res
    with open('calib_res_{}.json'.format(my_run.run), 'r') as ifile:
        j_res = json.load(ifile)

if __name__ == "__main__":
   print('Input Parameters: server, run, domDown, domUp')
   n = len(sys.argv)
   print('Number of arguments {}'.format(n))
   if n == 1: #no arguments
       print('Default input values')
       my_params = TStartParams(6, 1, 109, 119)
       # print('Start Params ', my_params.__str__())
   elif n == 5: #2 arguments
       print('Settings input values from arguments')
       dom1 = int(sys.argv[3])
       dom2 = int(sys.argv[4])
       if dom1 >= dom2:
           my_params = TStartParams(sys.argv[1], sys.argv[2], dom2, dom1)
       else:
           my_params = TStartParams(sys.argv[1], sys.argv[2], dom1, dom2)
   else:
       print('Wrong number of parameters, ciao')
       sys.exit()

   print('Start Params are set', my_params.__str__())
   main()
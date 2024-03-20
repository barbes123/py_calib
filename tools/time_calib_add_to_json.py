#! /usr/bin/python3

import json
import sys
from os.path import exists
import os

file_lut = 'LUT_ELIADE_S1_CL31.json'
file_calib = 'TimeCalib.dat'

def file_exists(myfile):
    if not exists(myfile):
        print('file_exists: File {} does not exist'.format(myfile))
        return False
    print('file_exists: File found {}'.format(myfile))
    return True

def GetJSON_FILE(file_json):
    if file_exists(file_json):
        with open('{}'.format(file_json),'r') as fin:
            return json.load(fin)

def AddTimeCalib2LUT(js_lut, file_name):
    with open('{}'.format(file_name),'r') as fin:
        for line in fin:
            if line[0] == '#':
                continue

            lut_line = line.split()
            if not lut_line :
                continue

            for domain in js_lut:
                if int(domain['domain']) == int(lut_line[0]):
                    domain['TimeOffset'] = float(lut_line[1])
    return js_lut

if __name__ == "__main__":
   if (len(sys.argv) > 2):
       file_lut = sys.argv[1]
       file_calib = sys.argv[2]

   if not file_exists(file_calib):
       exit()

   j_lut = GetJSON_FILE(file_lut)

   newlut = AddTimeCalib2LUT(j_lut,'TimeCalib.dat')
   j_new_lut = json.dumps(newlut, indent=3)

   path = file_lut.split('LUT_')[0]
   file = file_lut.split('LUT_')[1]

   fullpath = path + 'new_ta_LUT_' + file

   # print('TEST',fullpath)


   # with open('new_ta_{}'.format(file_lut), 'w') as fout:
   with open(fullpath, 'w') as fout:
       fout.write(j_new_lut)

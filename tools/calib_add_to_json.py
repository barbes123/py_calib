#! /usr/bin/python3

import json
import sys
from os.path import exists

file_lut = 'LUT_ELIADE_S9_run20_raluca.json'
file_calib = 'calib_res_60.json'

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

def AddNewCalib(mylut, mycalib):
   print(mylut)
   for ch_lut in mylut:
       for ch_cal in mycalib:
           if int(ch_lut['domain'] )== int(ch_cal['domain']):
               ch_lut['pol_list'] = ch_cal['pol_list']
   # print(mylut)
   return  mylut

if __name__ == "__main__":
   print('Add new calib to JSON LUT')
   if (len(sys.argv) > 2):
       file_lut = sys.argv[1]
       file_calib = sys.argv[2]

   j_lut = GetJSON_FILE(file_lut)

   j_calib = GetJSON_FILE(file_calib)
   new_lut = AddNewCalib(j_lut, j_calib)
   j_new_lut = json.dumps(new_lut, indent=3)

   with open('new_{}'.format(file_lut), 'w') as fout:
       fout.write(j_new_lut)

   # main()

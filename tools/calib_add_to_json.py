#! /usr/bin/python3

import json
import sys
from os.path import exists
import os

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

   foutPath = '{}'.format(file_lut.split('LUT_')[0])
   foutName = 'newcalib_LUT_{}'.format(file_lut.split('LUT_')[1])
   foutNameOld = 'LUT_{}'.format(file_lut.split('LUT_')[1])

   print(foutPath, ' ', foutName)

   if file_exists(foutName):
       os.unlink(foutName)
   if file_exists(foutNameOld):
       os.unlink(foutNameOld)

   os.symlink('{}{}'.format(foutPath,foutNameOld),foutNameOld)
   os.symlink('{}{}'.format(foutPath, foutName), foutName)





   with open('{}{}'.format(foutPath, foutName), 'w') as fout:
       fout.write(j_new_lut)

   # main()

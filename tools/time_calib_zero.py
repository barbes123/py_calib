#! /usr/bin/python3

import json
import sys
from os.path import exists
import os

file_lut = 'LUT_ELIADE_S1_CL31.json'
offset = 0

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

def AddTimeCalib2LUT(js_lut, offset):
    for domain in js_lut:
        domain['TimeOffset'] = offset
    return js_lut

if __name__ == "__main__":
   if (len(sys.argv) > 2):
       file_lut = sys.argv[1]
       offset = sys.argv[2]
   elif (len(sys.argv) > 2):
       file_lut = sys.argv[1]


   print('Set offset = {} to all domains'.format(offset))
   j_lut = GetJSON_FILE(file_lut)

   newlut = AddTimeCalib2LUT(j_lut, offset)
   j_new_lut = json.dumps(newlut, indent=3)

   with open('zero_ta_{}'.format(file_lut), 'w') as fout:
       fout.write(j_new_lut)





   #
   # with open('{}{}'.format(foutPath, foutName), 'w') as fout:
   #     fout.write(j_new_lut)

   # main()

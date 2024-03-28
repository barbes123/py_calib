#! /usr/bin/python3
import os, sys
from pathlib import Path
from os.path import exists #check if file exists
from colorama import Fore, Back, Style

# https://www.geeksforgeeks.org/print-colors-python-terminal/

server = 4

ELIADE_LUT_source = 'LUT_ELIADE_S4_CL35_60Co.json'
LUT_RECALL_source = 'LUT_RECALL_S4_RUN52.json'

ELIADE_LUT_target = 'LUT_ELIADE.json'
LUT_RECALL_target = 'LUT_RECALL.json'

try:
    py_calib_path = os.getenv('PY_CALIB')
    print('PY_CALIB path: ', py_calib_path)
except:
    print('Cannont find environmental PY_CALIB variable, please, check')
    sys.exit()



#print("\033[1;32;40m Bright Green \n")

lut_path = '{}/onlineEliade/LookUpTables/s{}'.format(Path.home(),server)
ELIADE_LUT_source = '{}/{}'.format(lut_path, ELIADE_LUT_source)
ELIADE_LUT_target = '{}/{}'.format(py_calib_path, ELIADE_LUT_target)

LUT_RECALL_source = '{}/{}'.format(lut_path, LUT_RECALL_source)
LUT_RECALL_target = '{}/{}'.format(py_calib_path, LUT_RECALL_target)

#print('\033[1;32;40m ELIADE_LUT_source ', LUT_RECALL_source)
#print('\033[1;32;40m ELIADE_LUT_target', ELIADE_LUT_target, end='')

print('\033[32m ELIADE_LUT_source', ELIADE_LUT_source, '\033[0m')
print('\033[32m ELIADE_LUT_target', ELIADE_LUT_target, '\033[0m')

print('\033[32m ELIADE_LUT_source ', LUT_RECALL_source, '\033[0m')
print('\033[32m ELIADE_LUT_target ', LUT_RECALL_target, '\033[0m')

#print(Style.RESET_ALL)

print('LUT_RECALL_source ', LUT_RECALL_source)
print('LUT_RECALL_target', LUT_RECALL_target)


def file_exists(myfile):
    if not exists(myfile):
        print('file_exists(): File {} does not exist'.format(myfile))
        return False
    print('file_exists(): File found {}'.format(myfile))
    return True

if file_exists(ELIADE_LUT_target):
    os.unlink(ELIADE_LUT_target)

if file_exists(LUT_RECALL_target):
    os.unlink(LUT_RECALL_target)


try:
    os.symlink(ELIADE_LUT_source, ELIADE_LUT_target)
except:
    os.unlink(ELIADE_LUT_target)
    os.symlink(ELIADE_LUT_source, ELIADE_LUT_target)

try:
    os.symlink(LUT_RECALL_source, LUT_RECALL_target)
except:
    os.unlink(LUT_RECALL_target)
    os.symlink(LUT_RECALL_source, LUT_RECALL_target)


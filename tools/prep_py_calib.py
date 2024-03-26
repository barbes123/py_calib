#! /usr/bin/python3
import os, sys
from pathlib import Path
from os.path import exists #check if file exists

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


lut_path = '{}/onlineEliade/LookUpTables/s{}'.format(Path.home(),server)
ELIADE_LUT_source = '{}/{}'.format(lut_path, ELIADE_LUT_source)
ELIADE_LUT_target = '{}/{}'.format(py_calib_path, ELIADE_LUT_target)

LUT_RECALL_source = '{}/{}'.format(lut_path, LUT_RECALL_source)
LUT_RECALL_target = '{}/{}'.format(py_calib_path, LUT_RECALL_target)

print('ELIADE_LUT_source ', LUT_RECALL_source)
print('ELIADE_LUT_target', ELIADE_LUT_target)

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


os.symlink(ELIADE_LUT_source, ELIADE_LUT_target)
os.symlink(LUT_RECALL_source, LUT_RECALL_target)

# print(lut_path)

# if file_exists()


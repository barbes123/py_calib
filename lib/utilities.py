from os.path import exists #check if file exists
import math, sys, os, json, subprocess

def load_json(file):
    fname = '{}'.format(file)
    if not file_exists(fname):
        sys.exit()
    try:
        with open(fname,'r') as myfile:
            return json.load(myfile)
    except:
        print(f'\033[31m Error in unilities.py: I am not able to load json table from {fname}', '\033[0m')
        sys.exit()

def file_exists(myfile):
    if not exists(myfile):
        print('file_exists(): File {} does not exist'.format(myfile))
        return False
    print('file_exists(): File found {}'.format(myfile))
    return True
from os.path import exists #check if file exists
import math, sys, os, json, subprocess

def load_json(file):
    fname = '{}'.format(file)
    if not file_exists(fname):
        sys.exit()
    with open(fname,'r') as myfile:
        return json.load(myfile)
def file_exists(myfile):
    if not exists(myfile):
        print('file_exists(): File {} does not exist'.format(myfile))
        return False
    print('file_exists(): File found {}'.format(myfile))
    return True
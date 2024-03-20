#! /usr/bin/python3

import json
import sys
from os.path import exists
import os

file_master = '/data10/live/IT/py_calib/json/ES_2_log.json'
file_slave = '/data10/live/IT/py_calib/json/GetRunTable/data/tmp_ES_2_log.json'

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

def merge(js_master, js_slave):
    new_dic = []
    for slave in js_slave:
        blSlaveFound = False
        for master in js_master:
            if master['runNumber'] ==  slave['runNumber']:
                blSlaveFound = True
                # print('slave ', slave['runNumber'], 'master ',  master['runNumber'])
        if not blSlaveFound:
            new_dic.append(slave)
        new_dic.append(master)

    new_js_master = json.dumps(new_dic, indent=3)
    return new_js_master


if __name__ == "__main__":
   if (len(sys.argv) > 2):
       file_master = sys.argv[1]
       file_slave = sys.argv[2]

   if not file_exists(file_master) or not file_exists(file_slave):
       print('file_slave or file_master cannot be found')
       sys.exit()

   js_master = GetJSON_FILE(file_master)
   js_slave = GetJSON_FILE(file_slave)

   js_new = merge(js_master, js_slave)

   path = file_master.split('ES_')[0]
   file = file_master.split('ES_')[1]

   fullpath = path + 'new_ES_' + file

   with open(fullpath, 'w') as fout:
       fout.write(js_new)

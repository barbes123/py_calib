#! /usr/bin/python3

import json
import sys
from os.path import exists
import os
from datetime import datetime
time_format = "%Y-%m-%d %H:%M:%S"

update_time = "2022-06-01 12:00:00"


file_master = '/data10/live/IT/py_calib/json/AddDataToJson/ES_2_log.json'
file_slave = '/data10/live/IT/py_calib/json/AddDataToJson/tmp_ES_2_log.json'

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



def UpdateData(js_master, js_slave):
    # Update data1 with keys from data2 that don't already exist in data1
    for key, value in js_slave.items():
        if key not in js_master:  # Check for non-matching keys
            js_master[key] = value  # Add the key-value pair to data1

def merge(js_master, js_slave):
    new_dic = []
    for slave in js_slave:
        if slave['start'] < update_time:
            continue
        blSlaveFound = False
        for master in js_master:
            if master['runNumber'] == slave['runNumber']:
                blSlaveFound = True
                # print('slave ', slave['runNumber'], 'master ',  master['runNumber'])
        if not blSlaveFound:
            if slave['stop'] < slave['start']:
                print('Warning: Stop time: {} is before start time {} for run {} '.format(slave['stop'], slave['start'], slave['runNumber']))
            new_dic.append(slave)
        new_dic.append(master)

    new_js_master = json.dumps(new_dic, indent=3)
    return new_js_master

def SplitFullName(fullname, ext='.json'):
    split = fullname.split('/')
    file = split[len(split)-1]
    path = fullname.split(file)[0]
    return path, file


if __name__ == "__main__":
   if (len(sys.argv) > 2):
       file_master = sys.argv[1]
       file_slave = sys.argv[2]

   if not file_exists(file_master) or not file_exists(file_slave):
       print('file_slave or file_master cannot be found')
       sys.exit()

   js_master = GetJSON_FILE(file_master)
   js_slave = GetJSON_FILE(file_slave)

   # js_new = merge(js_master, js_slave)
   js_new = UpdateData(js_master, js_slave)

   path, file = SplitFullName(file_master)

   fullpath = path + 'new_' + file

   with open(fullpath, 'w') as fout:
       fout.write(js_new)

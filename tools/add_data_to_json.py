#! /usr/bin/python3

import json
import sys
from os.path import exists
import os
from datetime import datetime
time_format = "%Y-%m-%d %H:%M:%S"

# update_time = "2022-06-01 12:00:00"
update_time = "2024-08-01 12:00:00"


try:
    ourpath = os.getenv('PY_CALIB')
    # path='{}{}'.format(Path.home(),'/EliadeSorting/EliadeTools/RecalEnergy')
    print('PY_CALIB path: ', ourpath)
except:
    print('Cannont find environmental PY_CALIB variable, please, check')
    ourpath='/data10/live/IT/py_calib'
    # sys.exit()

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
        if slave['start'] < update_time:
            continue
        if slave not in js_master:
            blSlaveFound = False
            for el in js_master:
                if slave['runNumber'] == el['runNumber']:
                    blSlaveFound = True
            if (not blSlaveFound):
                print('Found new run ',slave['runNumber'])
                js_master.append(slave)
        else:
            blSlaveFound = True

    sorted_master = sorted(js_master, key=lambda x: x['runNumber'], reverse=True)
    new_js_master = json.dumps(sorted_master, indent=3)

    return new_js_master


def SplitFullName(fullname, ext='.json'):
    split = fullname.split('/')
    file = split[len(split)-1]
    path = fullname.split(file)[0]
    return path, file


if __name__ == "__main__":
   IDserver = 0
   if (len(sys.argv) > 1):
       IDserver = sys.argv[1]
   if IDserver == 0:
       print('Server ID is 0. Please specify srverID')
       sys.exit()
   print('ServerID is', IDserver)

   file_master_path = '{}/json/'.format(ourpath)
   file_slave_path = '{}/json/GetRunTable/'.format(ourpath)

   file_master = '{}/json/run_table_S{}.json'.format(ourpath, IDserver)
   file_slave = '{}/json/GetRunTable/data/tmp_ES_{}_log.json'.format(ourpath, IDserver)

   if not file_exists(file_master) or not file_exists(file_slave):
       print('file_slave or file_master cannot be found')
       sys.exit()

   js_master = GetJSON_FILE(file_master)
   js_slave = GetJSON_FILE(file_slave)

   js_new = merge(js_master, js_slave)

   # print(js_new)

   # path, file = SplitFullName(file_master)
   # fullpath = path + 'new_' + file

   outfile = '{}/json/run_table_S{}.json'.format(ourpath, IDserver)

   print(outfile)

   with open(outfile, 'w') as fout:
       fout.write(js_new)

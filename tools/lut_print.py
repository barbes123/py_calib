#! /usr/bin/python3
import json
import sys
from os.path import exists
from pathlib import Path

def sort_by_key(key):
    lut.sort(key=lambda x: x[key] )

if (len(sys.argv) == 1):
    file_lut = '{}/EliadeSorting/LUT_ELIADE.json'.format(Path.home())
    if (not exists(file_lut)):
        exit
elif (len(sys.argv) > 1):
    file_lut = sys.argv[1]
    if (not exists(file_lut)):
        print(file_lut)
        file_found = False
        for x in range(1,10):
            file_lut_full = '{}/onlineEliade/LookUpTables/s{}/{} not found'.format(Path.home(), x, file_lut)
            print(file_lut_full)
            if (exists(file_lut_full)):
                file_found = True
                file_lut = file_lut_full
                break;
        if (not file_found):
            exit()

print(file_lut)
with open ('{}'.format(file_lut)) as lutf:
    lut = json.load(lutf)

par_list = {'domain', 'channel', 'detType', 'serial', 'TimeOffset', 'theta', 'phi', 'threshold', 'cs_dom', 'enable', 'pol_order', 'pol_list'}
print()

sort_by_key('domain')

for domain in lut:
    for par in par_list:
        print(' {} {}'.format(par, domain[par]), end='')
    print(end='')
    print()
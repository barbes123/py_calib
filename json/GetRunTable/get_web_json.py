#! /usr/bin/python3
import os
#acronyms for servers are here:
# /var/www/html/controller/assets$
import json
import requests
from pathlib import Path
import datetime
time_format = "%Y-%m-%d %H:%M:%S"
# ip_delila_log = 'http://172.18.4.156:8081/ELIADE/GetAllRunList/ES'
ip_delila_log = 'http://172.18.4.156:8081/ELIADE/GetAllRunList/'
# data_folder = '{}/onlineEliade/tools/calibration/calib_py/data'.format(Path.home())
# data_folder = '/data/live/IT/Py/calib_py/data'

server_logs = {1, 2, 3, 4, 5, 6, 7, 8, 9}

directory = os.getcwd()
data_folder = '{}/data'.format(directory    )
print(data_folder)

for server in server_logs:
    if (server == 9):
        print('Requesting ES {}'.format(server))
        tmp_log = requests.get('{}{}'.format(ip_delila_log,'ELIADE_Gate')).json()
        print('validated {}{}'.format(ip_delila_log, 'ELIADE_Gate' ))
    else:
        print('Requesting ES {}'.format(server))
        tmp_log = requests.get('{}{}{}'.format(ip_delila_log, 'ES', server)).json()
        print('validated {}{}{}'.format(ip_delila_log, 'ES', server))

    for item in tmp_log:
        item['start'] = datetime.datetime.fromtimestamp(item['start'])
        item['stop'] = datetime.datetime.fromtimestamp(item['stop'])

    print('{}/tmp_ES_{}_log.json'.format(data_folder, server))
    # with open('{}/tmp_ES_{}_log.json'.format(data_folder, server), 'w') as fout:
    with open('{}/tmp_ES_{}_log.json'.format(data_folder, server), 'w') as fout:
        json.dump(tmp_log, fout, indent=4, default=str)

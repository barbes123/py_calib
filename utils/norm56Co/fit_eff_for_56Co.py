#! /usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np
import sys, json, os
from scipy.optimize import curve_fit
# from argparse import ArgumentParser
import argparse

# blCheckNorm = True

RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
RESET = '\033[0m'  # Reset to default color


def fitDebertin(E, a1,a2,a3,a4,a5):
    return a1 * np.log(E) + a2 * np.log(E) / E + a3 * np.log(E) ** 2 / E + a4 * np.log(E) ** 4 / E + a5 * np.log(E) ** 5 / E

# list_of_norm = {'S1':4.82863316066443,'S2':1,'S3':1}

my_colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'orange', 'purple', 'brown']
my_markers = ['o', 's', '^', 'v', 'x', '+', '*', 'D', 'p', ',']
list_of_lut_2024 = {"S1":"CL29", "S2":"CL30", "S6":"CL31", "S3":"CL32", "S7":"CL33", "S5":"CL34", "S4":"CL35", "S8":"CL36"}

list_of_runs_S1 = {'60Co': 161, '152Eu': 162, '22Na':163, '54Mn':165,'133Ba':166,'137Cs':167,'56Co':170}
list_of_runs_S2 = {'60Co': 157, '152Eu': 158, '22Na':160, '54Mn':162,'133Ba':163,'137Cs':164,'56Co':167}
list_of_runs_S3 = {'60Co':26, '152Eu':27, '22Na':29, '54Mn':31,'133Ba':32,'137Cs':33,'56Co':36}

log = {
    "S1": list_of_runs_S1,
    "S2": list_of_runs_S2,
    "S3": list_of_runs_S3
}


def get_source_name(server_number, run_number, data):
    server_key = f'S{server_number}'  # Convert to string to match JSON keys
    if server_key in data:
        for source, run in data[server_key].items():
            # print(source, run_number)
            if run == run_number:
                return source  # Return the isotope name
    return None  # Return None if not found


def Fit_Efficiency_Curve(server, run, vol, my_fold, js_norm):

    file = f'../s{server}/addback_run_{run}_{vol}_eliadeS{server}/addback_{run}.json'

    print(file)

    serverID=f'S{server}'
    source = get_source_name(server,run,log)
    clover = list_of_lut_2024[serverID]
    print(f'{BLUE}Source {source} Clover {clover}{RESET}')
    print(f'File {file}')
    fig, ax = plt.subplots(figsize=(8, 6))

    if source == None:
        print('Cannot identify the source')
        return


    if not os.path.exists(file):
        print(f'File not found {file}')
        return
    else:
        print(f'Taking data from file {file}')

    with open(file, 'r') as fin:
        js_data = json.load(fin)


    plot_index = 0

    for i, entry in enumerate(js_data):
        fold = entry['fold']
        if fold != my_fold:
            continue
        ener = []
        eff = []
        err = []
        # print(entry["56Co"].items())
        for key, values in entry[source].items():
            if plot_index > len(my_colors):
                plot_index = 0
            try:
                eff.append(values['eff'][0])
                err.append(values["eff"][1])
                ener.append(float(key))
            except:
                pass

        if source == '56Co' and js_norm != None:
            norm = js_norm[serverID][str(fold)]
            eff = [norm*key for key in eff]

        ax.errorbar(ener, eff, yerr=err, fmt='o', label=f'Fold {fold}', color=my_colors[plot_index])
        params, covariance = curve_fit(fitDebertin, ener, eff)

        a1f, a2f, a3f, a4f, a5f = params
        ener1 = np.linspace(min(ener), max(ener), 500)  # Generate 500 points for smoothness
        smooth_fit = fitDebertin(ener1, *params)  # Evaluate the fitted function on the generated points
        ax.plot(ener1, smooth_fit, color='red', linestyle='--', label='Debertin Fit')
        ax.set_title(f"Efficiency {serverID} for fold {fold} {source} ")
        ax.set_xlabel('Energy, keV', size=12)
        ax.set_ylabel('Efficiency, %', size=12)

        if not os.path.exists('figures'):
            os.makedirs('figures',exist_ok=True)

        plt.savefig(f"figures/eff_fit_fold_{serverID}_{fold}_{source}.jpg", dpi = 300)
        # plt.show()

        plot_index += 1

    return params

def Norm56Co152Eu(co, eu, js_norm=None):  #server run vol
    norm_fold = {}
    for ifold in range (1,5):
        params_56Co = Fit_Efficiency_Curve(co[0], co[1], co[2], ifold, js_norm)
        params_152Eu = Fit_Efficiency_Curve(eu[0], eu[1], eu[2], ifold, js_norm)
        eff_846kev_56Co = fitDebertin(846.772, *params_56Co)# for key in log:
        eff_846kev_152Eu = fitDebertin(846.772, *params_152Eu)# for key in log:
        ratio = eff_846kev_152Eu/eff_846kev_56Co
        print(f'eff for 846.772 (56Co) is {eff_846kev_56Co}')
        print(f'eff for 846.772 (152Eu) is {eff_846kev_152Eu}')
        print(f'ratio 846.772 is {ratio}')
        norm_fold[ifold] = ratio
    return norm_fold

def CheckNormalization(server, volnmbr):
    SN = f'S{server}'
    with open(f'norm_56Co_{SN}.json', 'r') as fin:

        js_norm = json.load(fin)
        norm_s = Norm56Co152Eu([server, log[SN]['56Co'], volnmbr], [server, log[SN]['152Eu'], volnmbr], js_norm)
        norm = {
            SN: norm_s
        }
        with open(f'norm_56Co_check_{SN}.json', 'w') as fout:
            json.dump(norm, fout, indent=4)

def main():

    parser = argparse.ArgumentParser(description="Process run and volume parameters.")
    parser.add_argument("-s", "--servers", nargs='*',
                        dest="servers", default=[1, 1],
                        help="from domain, default = {} {}".format(1, 1))
    parser.add_argument("-v", "--volume", type=int, default=999, help="Volume number (default: 999)")
    parser.add_argument("--check", action="store_true", help="CheckNorm")


    args = parser.parse_args()

    blCheckNorm = args.check

    print('ddddddd',blCheckNorm)


    volnmbr = args.volume

    if len(args.servers) == 1:
        args.servers.append(args.servers[0])

    s_start = int(args.servers[0])
    s_stop = int(args.servers[1])

    server = s_start
    SN = f'S{server}'

    norm_s = Norm56Co152Eu([server, log[SN]['56Co'], volnmbr], [server, log[SN]['152Eu'], volnmbr])

    sys.exit()

    for server in range(s_start, s_stop + 1):
        SN = f'S{server}'

        print(f"{BLUE}Normalization 56Co to 152Eu for server {server}{RESET}")

        if blCheckNorm:
            print(f"{BLUE}Checking Normalization 56Co to 152Eu for server {server}{RESET}")
            CheckNormalization(server, volnmbr)
        else:
            print(f"{GREEN}56Co: {server}, {log[SN]['56Co']}, {volnmbr}; 152Eu {server}, {log[SN]['152Eu']}, {volnmbr}{RESET}")
            norm_s = Norm56Co152Eu([server, log[SN]['56Co'], volnmbr], [server, log[SN]['152Eu'], volnmbr])
            norm = {
                SN: norm_s,
            }

        with open(f'norm_56Co_{SN}.json', 'w') as fout:
            json.dump(norm, fout, indent=4)


if __name__ == "__main__":
    main()




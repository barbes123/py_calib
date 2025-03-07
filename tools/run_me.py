#! /usr/bin/python3

import os, json, sys
import argparse

RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
RESET = '\033[0m'  # Reset to default color

# Set up argument parsing
parser = argparse.ArgumentParser(description="Process the LUT settings and run the selector.")
parser.add_argument("-r", "--run", type=int, nargs='+', default=[161,161], help="Run number(s). Specify one value for both or two values for range (start end).")
parser.add_argument("-v","--vol", type=int, nargs="+", default=[0,0], help="The starting volume number. Defaults to 0 if not provided.")
# parser.add_argument("vol", type=int, nargs="?", default=None, help="The ending volume number. Defaults to volume1 if not provided.")
parser.add_argument("nevents", type=int, nargs="?", default=0, help="Number of events. Defaults to 0 if not provided.")
parser.add_argument("AddBack", type=int, nargs="?", default=1, help="AddBack flag (1 or 0). Defaults to 1 if not provided.")
parser.add_argument("-s","--server", type=int, nargs="?", default=1, help="Server number. Defaults to 1 if not provided.")

# Parse arguments
args = parser.parse_args()

# Handle the "run" argument (which can be one or two values)
if len(args.run) == 1:
    runnb = runnb1 = args.run[0]  # If only one run number is provided, both start and end will be the same
elif len(args.run) == 2:
    runnb, runnb1 = args.run  # If two values are provided, use them as start and end
else:
    parser.error("The 'run' argument must have one or two values (start and end).")

if len(args.vol) == 1:
    volume1 = volume2 = args.vol[0]  # If only one run number is provided, both start and end will be the same
elif len(args.run) == 2:
    volume1, volume2 = args.vol  # If two values are provided, use them as start and end
else:
    parser.error("The 'run' argument must have one or two values (start and end).")

# Use parsed arguments for the rest
nevents = args.nevents
AddBack = args.AddBack
server = args.server

# Print the parameters for clarity
print("Put Parameters: AddBack (0 - if none); server_nbr (0 - if none); run_nbr; volume_from; volume_to;")

print(f"{BLUE} RUNfirst      {runnb}{RESET}")
print(f"{BLUE}RUNlast       {runnb1}{RESET}")
print(f"{BLUE}VOLUMEfirst   {volume1}{RESET}")
print(f"{BLUE}VOLUMElast    {volume2}{RESET}")
print(f"{BLUE}N EVENTS      {nevents}{RESET}")
print(f"{BLUE}AddBack       {AddBack}{RESET}")
print(f"{BLUE}SERVER ID     {server}{RESET}")

lut_path = os.path.expanduser(f"~/onlineEliade/LookUpTables/s{server}/")
lut_link = os.path.expanduser(f"~/EliadeSorting/")

lut_file = ""
lut_ta = ""
lut_conf = "LUT_CONF_S9_20221205.dat"
lut_json = "LUT_ELIADE_S9_20230523_DT.json"

with open(f'{lut_path}lut_s{server}_dmitry.json') as fin:
    js_lut = json.load(fin)

def get_lut_from_json(run, vol, js_lut=js_lut):
    if str(run) in js_lut:
        # Check if the volume exists for this run
        if str(vol) not in js_lut[str(run)]["volumes"]:
            vol = 999
        if str(vol) in js_lut[str(run)]["volumes"]:
                lut_data = js_lut[str(run)]["volumes"][str(vol)]
                lut_conf = lut_data["lut_conf"]
                lut_json = lut_data["lut_json"]
                lut_ta = lut_data["lut_ta"]
                lut_file = lut_data["lut_file"]
                print(f"LUT for volume {vol} will be used for run {run}")
                return lut_conf, lut_json, lut_file, lut_ta
        else:
            print(f"Volume {vol} not found for run {run}")
            return None
    else:
        print(f"Run {run} not found")
        return None

while runnb <= runnb1:
    volnb = volume1
    while volnb <= volume2:
        # Unlink files if they exist
        for filename in ["LUT_ELIADE.dat", "LUT_ELIADE.json", "LUT_TA.dat", "LUT_CONF.dat"]:
            file_path = os.path.join(lut_link, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            lut_conf, lut_json, lut_file, lut_ta = get_lut_from_json(runnb, volnb)





        # if str(runnb) in js_lut.keys():
        #     print(js_lut[str(runnb)]["volumes"])
        #     if 999 in js_lut[str(runnb)]["volumes"]:
        #         lut_conf = js_lut[str(runnb)]["lut_conf"]
        #         lut_json = js_lut[str(runnb)]["lut_json"]
        #         lut_ta = js_lut[str(runnb)]["lut_ta"]
        #         lut_file = ""
        # else:
        #     print(f"{YELLOW} no luts are defined for {runnb} in json. I will use defaults")


        # if runnb == 159:
        #     lut_conf = "coinc_gates_run_07.dat"
        #     lut_json = "LUT_ELIADE_S1_CL29_20241016_RUN159.json"
        #     lut_ta = "LUT_TA_TimeCalibGaussian_RUN159.dat"
        #     lut_file = ""
        # elif runnb == 160:
        #     lut_conf = "coinc_gates_run_07.dat"
        #     lut_ta = "LUT_TA_TimeCalibGaussian_RUN159.dat"
        #     lut_json = "LUT_ELIADE_S1_CL29_20241016_RUN160_V0.json"
        #     lut_file = ""
        #
        #     if volnb <= 89:
        #         lut_json = "LUT_ELIADE_S1_CL29_20241016_RUN160_V0.json"
        #     elif volnb >= 90:
        #         lut_json = "LUT_ELIADE_S1_CL29_20241016_RUN160_V100.json"
        # elif runnb == 161:
        #     lut_json = "LUT_ELIADE_S1_CL29_20241016_RUN160_V100.json"
        #     lut_conf = "coinc_gates_run_07.dat"
        #     lut_ta = "LUT_TA_TimeCalibGaussian_RUN161.dat"
        # elif runnb == 162:
        #     lut_json = "LUT_ELIADE_S1_CL29_RUN162_152Eu.json"
        #     lut_conf = "coinc_gates_run_07.dat"
        #     lut_ta = "LUT_TA_TimeCalibGaussian_RUN161.dat"
        # elif runnb == 163:
        #     lut_json = "LUT_ELIADE_S1_CL29_RUN162_152Eu.json"
        #     lut_conf = "coinc_gates_run_07.dat"
        #     lut_ta = "LUT_TA_TimeCalibGaussian_RUN161.dat"
        # elif runnb == 164:
        #     lut_json = "LUT_ELIADE_S1_CL29_RUN162_152Eu.json"
        #     lut_conf = "coinc_gates_run_07.dat"
        #     lut_ta = "LUT_TA_TimeCalibGaussian_RUN161.dat"
        # elif runnb == 165:
        #     lut_json = "LUT_ELIADE_S1_CL29_RUN162_152Eu.json"
        #     lut_conf = "coinc_gates_run_07.dat"
        #     lut_ta = "LUT_TA_TimeCalibGaussian_RUN161.dat"
        # elif runnb == 166:
        #     lut_json = "LUT_ELIADE_S1_CL29_RUN162_152Eu.json"
        #     lut_conf = "coinc_gates_run_07.dat"
        #     lut_ta = "LUT_TA_TimeCalibGaussian_RUN161.dat"
        # elif runnb == 167:
        #     lut_json = "LUT_ELIADE_S1_CL29_RUN162_152Eu.json"
        #     lut_conf = "coinc_gates_run_07.dat"
        #     lut_ta = "LUT_TA_TimeCalibGaussian_RUN161.dat"
        # elif runnb == 169:
        #     lut_json = "LUT_ELIADE_S1_CL29_RUN162_152Eu.json"
        #     lut_conf = "coinc_gates_run_07.dat"
        #     lut_ta = "LUT_TA_TimeCalibGaussian_RUN161.dat"
        # elif runnb >= 170:
        #     lut_json = "LUT_ELIADE_S1_CL29_20250113_56Co.json"
        #     lut_conf = "coinc_gates_run_07.dat"
        #     lut_ta = "LUT_TA_TimeCalibGaussian_RUN161.dat"

        # Handling the symbolic links
        if lut_file:
            if not os.path.exists(lut_path + lut_file):
                print("LUT_ELIADE.dat is missing")
            else:
                os.symlink(lut_path + lut_file, os.path.join(lut_link, "LUT_ELIADE.dat"))

        if lut_json:
            if not os.path.exists(lut_path + lut_json):
                print("LUT_ELIADE.json is missing")
            else:
                os.symlink(lut_path + lut_json, os.path.join(lut_link, "LUT_ELIADE.json"))

        if lut_ta:
            if not os.path.exists(lut_path + lut_ta):
                print("LUT_TA.dat is missing")
            else:
                os.symlink(lut_path + lut_ta, os.path.join(lut_link, "LUT_TA.dat"))

        if lut_conf:
            if not os.path.exists(lut_path + lut_conf):
                print("LUT_CONF.dat is missing")
            else:
                os.symlink(lut_path + lut_conf, os.path.join(lut_link, "LUT_CONF.dat"))

        # Display the LUT files in use
        print("--------------------------------------------------------")
        print(f"{GREEN}Setting of LUT(s){RESET}")
        print("--------------------------------------------------------")
        print(f"{GREEN}LUT_ELIADE file  : {lut_file}{RESET}")
        print(f"{GREEN}LUT_ELIADE json  : {lut_json}{RESET}")
        print(f"{GREEN}LUT_CONF file    : {lut_conf}{RESET}")
        print(f"{GREEN}LUT_TA file      : {lut_ta}{RESET}")
        print("--------------------------------------------------------")

        # Running the root command
        print(f"Now I am starting run the selector run{runnb}_{volnb}.root")
        root_command = f"start_me.C+({AddBack},{server},{runnb},{volnb},{nevents})"
        os.system(f'root -l -b -q "{root_command}"')
        print(f"I finished run{runnb}_{volnb}_eliadeS{server}.root")

        volnb += 1

    runnb += 1


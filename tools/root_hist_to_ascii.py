#!/usr/bin/env python3
from symbol import return_stmt

import ROOT
import os, sys, subprocess, json, shutil, argparse
from pathlib import Path
from os.path import exists
current_path = Path.cwd()

try:
    py_calib_path = os.getenv('PY_CALIB')
    path = os.path.dirname(py_calib_path)
    print('PY_CALIB PATH: ', py_calib_path)
except:
    print('Cannot find environmental PY_CALIB variable, please check')
    sys.exit()

class HistogramConverter:
    def __init__(self, file="toconvertfile.root", hname="mDelila_raw", maxbin=16384, 
                 rebin=0, foldername1="", foldername2="", fortkt=1):
        self.tkt = bool(fortkt)
        self.maxbin = maxbin
        self.rebin_const = rebin
        self.foldername = foldername1
        self.fout = ""
        
        # Process input filename
        if not Path(file).exists():
            raise FileNotFoundError(f"Input file {file} not found")
            
        self.frootname = Path(file).stem
        self.fout = str(Path(self.frootname) / self.foldername)
        
        # Create output directories
        os.makedirs(self.fout, exist_ok=True)
        
        if foldername2:
            self.foldername = str(Path(foldername1) / foldername2)
            self.fout = str(Path(self.frootname) / self.foldername)
            os.makedirs(self.fout, exist_ok=True)
        
        # Open ROOT file
        self.root_file = ROOT.TFile(file)
        if not self.root_file or self.root_file.IsZombie():
            raise RuntimeError(f"Could not open ROOT file {file}")
            
        # Process histograms
        self.process_histograms(hname)
        
    def process_histograms(self, hname):
        """Process all histograms matching the given name"""
        keys = self.root_file.GetListOfKeys()
        for key in keys:
            obj = key.ReadObj()
            if not obj:
                continue
                
            if isinstance(obj, (ROOT.TH1F, ROOT.TH1D)):
                print(f"TH1::{obj.GetName()}")
                self.convert_th1(obj)
            elif isinstance(obj, ROOT.TH2F):
                print(f"TH2::{obj.GetName()}")
                if hname == "all" or obj.GetName() == hname:
                    self.convert_th2(obj)
            else:
                print("Type of hist is unknown")
                
    def convert_th1(self, h):
        """Convert 1D histogram to ASCII"""
        hist_name = str(h.GetName()).replace("@", "_").replace("/", "_")
        output_path = str(Path(self.fout) / hist_name) + (".spe" if self.tkt else ".dat")
        
        if self.rebin_const != 0:
            h.Rebin(self.rebin_const)
            
        scale = 1  # Could be modified as in original code
            
        with open(output_path, 'w') as f:
            for i in range(1, h.GetNbinsX() + 1):
                if h.GetBinCenter(i) > self.maxbin:
                    continue
                    
                value = h.GetBinContent(i)
                if self.tkt:
                    f.write(f"{value}\n")
                else:
                    error = ROOT.TMath.Sqrt(value)
                    f.write(f"{h.GetBinCenter(i)*scale} {value} {error}\n")
                    
        print(f"Completed {output_path}")
        
    def convert_th2(self, m):
        """Convert 2D histogram to multiple 1D projections"""
        hist_name = str(m.GetName())
        n_bins_x = m.GetXaxis().GetNbins()
        
        for j in range(1, n_bins_x + 1):
            py = m.ProjectionY(f"_py_{j}", j, j)
            if py.GetEntries() == 0:
                continue
                
            domain = m.GetXaxis().GetBinCenter(j)
            output_path = str(Path(self.fout) / f"{hist_name}_py_{int(domain)}") + (".spe" if self.tkt else ".dat")
            
            with open(output_path, 'w') as f:
                for i in range(1, py.GetNbinsX() + 1):
                    if py.GetBinCenter(i) > self.maxbin:
                        continue
                        
                    value = py.GetBinContent(i)
                    if self.tkt:
                        f.write(f"{value}\n")
                    else:
                        error = ROOT.TMath.Sqrt(value)
                        f.write(f"{py.GetBinCenter(i)} {value} {error}\n")
                        
            print(f"Created projection {output_path}")

def do_calibration(dir, dom0, dom1):
    if os.path.isdir(dir):
        os.chdir(dir)
        # print(f"Directory found: {dir}")
    else:
        print(f"Directory does NOT exist: {dir}")
        return

    # Run the command and wait for it to finish
    cmd = ['pc', '-d', str(dom0), str(dom1)]  # Define the command list first
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Print stdout and stderr
    print("Output:")
    print(result.stdout)


    if result.stderr:
        print("Errors in fitting/calib:")
        print(result.stderr)
        return False
    else:
        return True


def AddNewCalib(mylut, mycalib):
    print(mylut)
    for ch_lut in mylut:
        for ch_cal in mycalib:
            if int(ch_lut['domain'] )== int(ch_cal['domain']):
                ch_lut['pol_list'] = ch_cal['pol_list']
    return  mylut

def add_calib_to_lut(dir, run, vol, server, lut_name):

    def AddNewCalib(mylut, mycalib):
        print(mylut)
        for ch_lut in mylut:
            for ch_cal in mycalib:
                if int(ch_lut['domain'] )== int(ch_cal['domain']):
                    ch_lut['pol_list'] = ch_cal['pol_list']
        return  mylut


    # lut_path = Path.home() / "onlineEliade" / "LookUpTables" / f"s{server}" / lut_name
    lut_path = py_calib_path + "/" + "LUT_ELIADE.json"
    print(f"Path for the LUT_ELIADE.json {lut_path}")
    if exists(lut_path):
       with open('{}'.format(lut_path),'r') as flut:

            j_lut = json.load(flut)
    else:
        print(f'File {lut_path} not found')
        sys.exit()
            
    calib_file = f'calib_res_{run}.json'
    if exists(calib_file):
         with open('{}'.format(calib_file),'r') as fcalib:
             j_calib = json.load(fcalib)
    else:
        print(f'File {calib_file} not found')

    new_lut = AddNewCalib(j_lut, j_calib)
    j_new_lut = json.dumps(new_lut, indent=3)
    new_lut_file = f'LUT_R{run}V{vol}S{server}.json'
    
    with open(new_lut_file, 'w') as fout:
        fout.write(j_new_lut)

    dir_path = f'{current_path}/LUT_R{run}S{server}'

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    if os.path.isfile(new_lut_file):
        dst_path = os.path.join(dir_path, os.path.basename(new_lut_file))
        print(f'file to be saved {dst_path}')

        # If destination file exists, remove it first to avoid shutil.Error
        if os.path.exists(dst_path):
            os.remove(dst_path)


        try:
            shutil.move(new_lut_file, dst_path)
            print(f"Moved {new_lut_file} to {dst_path}")
        except:
            print(f"Error moving {new_lut_file} to {dst_path}")


    else:
        print(f"File not found: {new_lut_file}")

def main():

    print('CURRENT PATH: ', current_path)

    parser = argparse.ArgumentParser(description="Convert ROOT histograms to ASCII format")
    parser.add_argument("--file", default="None", help="Input ROOT file")
    parser.add_argument("--hname", default="mDelila_raw", help="Histogram name to process (or 'all')")
    parser.add_argument("--maxbin", type=float, default=16384, help="Maximum bin value to export")
    parser.add_argument("--rebin", type=int, default=0, help="Rebin factor (0 for no rebinning)")
    parser.add_argument("--foldername1", default="", help="First output folder name")
    parser.add_argument("--foldername2", default="", help="Second output folder name")
    parser.add_argument("--fortkt", type=int, choices=[0,1], default=1, help="Output format (1 for .spe, 0 for .dat)")
    parser.add_argument('--noconvert', action='store_true', help="Do not convert root to ascii (ascii files are already here)")


    parser.add_argument("-r", "--runs", nargs='*', type=int,
                        dest="run", default=[0, 0],
                        help="Run range from start to end, default = {} {}".format(0, 0))

    parser.add_argument("-v", "--volumes", nargs=2, type=int,
                        dest="vol", default=[0, 0],
                        help="Volume range from start to end, default = {} {}".format(0, 0))

    parser.add_argument("-d", "--domain", nargs=2, type=int,
                        dest="domain", default=[100, 140],
                        help="Number of domains to be done")

    parser.add_argument("-prefix" "--prefix to the files to be analyzed",
                        dest="prefix", default='selected_run', type=str,
                        help="Prefix file, selected_run_...")

    parser.add_argument("-lut" "--LUT_ELIADE.json",
                        dest="lut", default=None, type=str,
                        help="main LUT_ELIADE.json for analysis")

    parser.add_argument("-s", "--server", dest="server", default=1, type=int, choices=range(10),
                        help="DAQ ELIADE server, default = 1")

    args = parser.parse_args()

    if len(args.run) == 1:
        args.run = [args.run[0], args.run[0]]

    ascii_convert = not args.noconvert
    # print(ascii_convert)
    # print(args.noconvert)
    # sys.exit()

    # if args.lut == None:
    #     print('Provide the lut table for analysis using -lut ')
    #     sys.exit()

    #To Convert once single file given by file name
    if args.file != "None":
        converter = HistogramConverter(
            file=args.file,
            hname=args.hname,
            maxbin=args.maxbin,
            rebin=args.rebin,
            foldername1=args.foldername1,
            foldername2=args.foldername2,
            fortkt=args.fortkt
        )

    if args.run[0] == 0:
        sys.exit()

    all_runs = range(args.run[0], args.run[1]+1)
    all_volumes = range(args.vol[0], args.vol[1]+1)

    for runnbr in all_runs:
        for volnbr in all_volumes:
            filename = f'{args.prefix}_{runnbr}_{volnbr}_eliadeS{args.server}'
            print(f'Converting {filename}')

            if  ascii_convert:
                converter = HistogramConverter(
                    file=filename+".root",
                    hname=args.hname,
                    maxbin=args.maxbin,
                    rebin=args.rebin,
                    foldername1=args.foldername1,
                    foldername2=args.foldername2,
                    fortkt=args.fortkt
                )
            do_calibration(filename, args.domain[0], args.domain[1])
            add_calib_to_lut(filename,runnbr,volnbr,args.server,args.lut)
            os.chdir(current_path)

        # add_calib_to_lut( filename,run =  runnbr,vol = volnbr, lut_name= args.lut, server = args.server)

if __name__ == "__main__":
    main()

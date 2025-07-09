#!/bin/bash


my_home=$HOME

echo "Home directory $my_home"


#run analysis

#------------------------------------------------------------------
link="/usr/local/bin/runme"
source="$PWD/run_me.py"
echo "source $source and link $link"

sudo unlink $link
sudo ln -s $source $link
#------------------------------------------------------------------



#AddBack

echo /usr/local/bin/ab.run
sudo unlink /usr/local/bin/ab.run
echo $HOME/onlineEliade/tools/AddBackSimTools/addback_run.py
sudo ln -s $HOME/onlineEliade/tools/AddBackSimTools/addback_run.py /usr/local/bin/ab.run

echo /usr/local/bin/ab.merge
sudo unlink /usr/local/bin/ab.merge
echo $PWD/merged_addback_plus.py
sudo ln -s $PWD/merged_addback_plus.py /usr/local/bin/ab.merge

echo /usr/local/bin/ab.addback
sudo unlink /usr/local/bin/ab.addback
echo $PY_CALIB/py_addback.py
sudo ln -s $PY_CALIB/py_addback.py /usr/local/bin/ab.addback


# Calibration

echo /usr/local/bin/pc
sudo unlink /usr/local/bin/pc
echo $PY_CALIB/py_calib.py
sudo ln -s $PY_CALIB/py_calib.py /usr/local/bin/pc

echo /usr/local/bin/py_aa
sudo unlink /usr/local/bin/py_aa
echo $PY_CALIB/py_calib_aa.py
sudo ln -s $PY_CALIB/py_calib_aa.py /usr/local/bin/py_aa

echo /usr/local/bin/calib.all
sudo unlink /usr/local/bin/calib.all
echo $HOME/onlineEliade/tools/root_hist_to_ascii.py
sudo ln -s $HOME/onlineEliade/tools/root_hist_to_ascii.py /usr/local/bin/calib.all



echo /usr/local/bin/py_b
sudo unlink /usr/local/bin/py_b
echo $PY_CALIB/py_calib_batch.py
sudo ln -s $PY_CALIB/py_calib_batch.py /usr/local/bin/py_b 


echo /usr/local/bin/lut.print
sudo unlink /usr/local/bin/lut.print
echo $PWD/lut_print.py
sudo ln -s $PWD/lut_print.py /usr/local/bin/lut.print

echo /usr/local/bin/lut.json
sudo unlink /usr/local/bin/lut.json
echo $PWD/lut_to_json.py
sudo ln -s $PWD/lut_to_json.py /usr/local/bin/lut.json

echo /usr/local/bin/lut.add.calib
sudo unlink /usr/local/bin/lut.add.calib
echo $PWD/calib_add_to_json.py
sudo ln -s $PWD/calib_add_to_json.py /usr/local/bin/lut.add.calib

echo /usr/local/bin/lut.add.zerocalib
sudo unlink /usr/local/bin/lut.add.zerocalib
echo $PWD/calib_add_zero_calib.py
sudo ln -s $PWD/calib_add_zero_calib.py /usr/local/bin/lut.add.zerocalib

echo /usr/local/bin/lut.add.ta
sudo unlink /usr/local/bin/lut.add.ta
echo $PWD/time_calib_add_to_json.py
sudo ln -s $PWD/time_calib_add_to_json.py /usr/local/bin/lut.add.ta

echo /usr/local/bin/lut.add.zerota
sudo unlink /usr/local/bin/lut.add.zerota
echo $PWD/time_calib_zero.py
sudo ln -s $PWD/time_calib_zero.py /usr/local/bin/lut.add.zerota



echo /usr/local/bin/lut.getdatafromserver
sudo unlink /usr/local/bin/lut.getdatafromserver
echo $PWD/get_web_json.py
sudo ln -s $PWD/get_web_json.py /usr/local/bin/lut.getdatafromserver

echo /usr/local/bin/lut.adddata2json
sudo unlink /usr/local/bin/lut.adddata2json
echo $PWD/add_data_to_json.py
sudo ln -s $PWD/add_data_to_json.py /usr/local/bin/lut.adddata2json



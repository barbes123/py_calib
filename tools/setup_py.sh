#!/bin/bash


my_home=$HOME

echo $my_home

echo /usr/local/bin/pc
sudo unlink /usr/local/bin/pc
echo $PY_CALIB/py_calib.py
sudo ln -s $PY_CALIB/py_calib.py /usr/local/bin/pc

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

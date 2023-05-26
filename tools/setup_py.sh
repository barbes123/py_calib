#!/bin/bash


my_home=$HOME

echo $my_home

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

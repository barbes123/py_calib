ELIADE DAQ&CALIBRATION 
by Teodora Sebe (2024)


# DATA ACQUISITION
  
1. Enable the DAQ on the server (s1-...s9)
- Connect to the server: 
ssh eliade@172.18.4.13X (where x is 1,2,3,4,5,6,7,8 or 9, x=the number of the server that you are using) or e1/e2/e3/e4

_TIP_:If you don't know what is the corresponding server for the detector that you are using, access Eliade Wiki, enter Look Up Tables and search for that detector. The corresponding server will be on the right side of the table.

- check you should be in ~/DELILA directory

-For Local DAQ edit StartMode in PHA.conf for s1-s8:

_StartMode SYNC_1ST_SW_

- For Global DAQ edit PHA.conf for s2-s8:
  
_StartMode SYNCIN_SLAVE_

for s1:

_StartMode SYNC_1ST_SW_

_TIP1:_ in order to access PHA.conf, use the _vim_ command in Terminal
_TIP2:_  you can exit PHA.conf by pressing _:q_

-run the program _run.py_

_run.py -l local.xml_

2. Open the daq GUI: Access 172.18.4.13X/controller (where x is 1,2,3,4,5,6,7,8 or 9,) on Firefox and press the "Configure" button. Fill in the type of source that you are using and press Start.

4. Press STOP and check if the data are on the disks (example /eliadedisks/s5/root_file)
i.e: Wait 10-15 mins so that enough data is taken then press Stop. Close the server (it appears as eliadeS5). Go to the machine that you want to use for the data analyse.
Mention: if you see that you are operating on S5, close the terminal and open a new one (you don't want your line to look like this eliade@eiadeS5, so when you open a new terminal, it will directly send you to the machine that you are using i.e eliade@eliade1 or eliade@eliade2).

In order to check if the data is saved, enter the path from above on Terminal (s5 corresponds to the server that we used earlier, so replace 5 with the corresponding number of the server). When you stopped the measurement, on the right side of the STOP button says "next measurement is 146..." (or something similar, I didn't check to take it word by word) which means that your measurement is 145 and you should look for the ROOT file with number 145.


# FOR CALIBRATION
-Update the database (json) with new enrties. For this, you have to access the json database from py_calib:

_cd ~/py_calib/json/GetRunTable_

Mention: You can open the folder one by one if you want to see what's in them

-Initiate the program get_web_json.py to start update-ing the list

_~/py_calib/json/GetRunTable ./get_web_json.py_

-Check if the update was done by accessint the data folder from GetRunTable

_cd ~/py_calib/json/GetRunTable/data_

-Check the file of you server to see if it updated (in this case, the file that has ES_5 and we should look for the last update to be 145)

_~/py_calib/json/GetRunTable/data less tmp_ES_5_log.json_
(Exit the file by pressing q)

-Go back to the database via the json folder

_cd ~/py_calib/json_

-Create a link with the actualized database

_~/py_calib/json ln -s GetRunTable/data/tmp_ES_5_log.json run_table_S5.json_
(Check if the file run_table_S5.json appeared in the json folder)

-Go one folder behind (py_calib) and repeat the last step for LUT and connect it to onlineEliade

_~/py_calib ln -s ~/onlineEliade/LookUpTables/s5/LUT_ELIADE_S1_CL34_60Co.json LUT_ELIADE.json_

(When you open the current folder via ls –ltr, you will see something like this if it worked
lrwxrwxrwx 1 eliade eliade 70 mar 14 13:12 LUT_ELIADE.json ->/home/eliade/onlineEliade/LookUpTables/s5/LUT_ELIADE_S1_CL34_60Co.json)

-Do the same thing for RECALL

_~/py_calib$ ln -s /home/eliade/onlineEliade/LookUpTables/s5/new_LUT_RECALL_RUN144.json LUT_RECALL.json_ 

IF IT DOESN'T WORK USE THE UNLINK FUNCTION FROM TERMINAL AND STARTOVER WITH THE LINKING

_unlink LUT_RECALL.json_

-Go to eliadedisks, select your server and choose selector_dmitry (if there is _selector_dmitry don't use it, it's outdated)

_/eliadedisks/s5/selector_dmitry_
(Look into the folder if you want to see what's in there)

-Use the code run_me.sh with the number of the current run (the current run is 145 so choose 145):

_/eliadedisks/s5/selector_dmitry$ ./run_me.sh 145_

You will obtain the root version.
(Before you start the program, check the run_me file to be sure that we are using the correct LUTs)

-Run the file in ROOT just to check the file

_/eliadedisks/s5/selector_dmitry$ root selected_run_144_0_eliadeS5.root_

-Use hconverter.C to get the folder with the spectra

_.L ~/onlineEliade/tools/hconverter.C+_
_hconverter("selected_run_145_0_eliadeS5.root")_
_.q_

-Go to the created folder /eliadedisks/s5/selector_dmitry/selected_run_145_0_eliadeS5

-Run py_calib.py for the current run, in the correct server, with the appropriate domain

_/eliadedisks/s5/selector_dmitry/selected_run_145_0_eliadeS5$ py_calib.py -s 5 -r 145 -d 100 140_

It has to find the peaks. If it doesn't find them, then go in the program and change the parameters (exp: change the domain limits so that the peaks are in them)

-Check if the results are saved in the calib_res_145.json file

_/eliadedisks/s5/selector_dmitry/selected_run_145_0_eliadeS5$ less calib_res_145.json_

TIP: you will see that there are to types- 1 is for the cores and 2 the ones for the segments
(First, check if the file actually exists with ls -ltr in the command line from the Terminal)

-Add the calibration to the LUT

_/eliadedisks/s5/selector_dmitry/selected_run_145_0_eliadeS5$ lut.add.calib ~/onlineEliade/LookUpTables/s5/LUT_ELIADE_S1_CL34_60Co.json calib_res_145.json_

-Check if the new LUT is correct by coparing the data from calib_res_145.json with the data from newcalib_LUT_ELIADE_S5_CL35_60Co.json. If the data is the same, then
everithing is alright.

_Mention_: calib_res is in eliadedisks/s5/selector_dmitry/selected_run_145_0_eliadeS5 and the newcalib_LUT file is in /onlineEliade/LookUpTables/s5

-Replace the old LUT with the new (so that it can be uploaded in the run_me.sh program) in the LookUpTables/s5 folder:

_mv newcalib_LUT_ELIADE_S5_CL34_60Co.json LUT_ELIADE_S5_CL34_60Co.json_

-Go back to the selector_dmitry folder (eliadedisks/s5/selector_dmitry) and run again the run_me.sh program

_./run_me.sh 145_

-Check if the calibration was applied by using ROOT

_root selected_run_145_0_eliadeS5.root_

*in ROOT
_root [1] .ls_

_root [2] mDelila->Draw("col")_

And you click right on the axis and select SetLogZ and you will see the spectras (if you want to see each spectra individuali, click right in the screen and choose SetShowProjection and move the mouse to a channel).
_Mention_: If you want to see the efficiency/resolution etc, go to the folder that contains the spectras (the one you obtain after you apply hconvertor, selected_run_145_0_eliadeS5) and enter the figures folder:

_/eliadedisks/s5/selector_dmitry/selected_run_145_0_eliadeS5/figures_

Then, to see the graphs use:

_/eliadedisks/s5/selector_dmitry/selected_run_145_0_eliadeS5/figures$ evince dom_123_res.eps dom_122_eff.eps_

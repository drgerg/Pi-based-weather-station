#!/usr/bin/env python3
#
#   rainMainDATA.py - do data logging of rainfall.

#     Copyright (c) 2019,2020 - Gregory Allen Sanders.

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import time
import os
import logging
from logging.handlers import WatchedFileHandler
import configparser
import argparse
import traceback
import signal
import sys
import pickle
#import statistics
from time import sleep
import RPi.GPIO as GPIO

#
## - - - - - RAIN CODE BELOW HERE - - - - These lines log to RMD.log
#
GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setwarnings(False)
rpulse = 0              # "reported pulse"
gppulse = 0             # "gotPulse pulse"
gpstart = time.time()   # "gotPulse start"
timeVal = time.time()   # time value holder
#
##  STARTING HERE WE ARE GETTING THE BUCKET TIP DATA READY FOR outMainDATA TO PICK IT UP AS IT GOES BY.
##  WE COLLECT IT, STACK IT UP FOR 60 SECONDS, AND LEAVE IT LAYING IN THE WORKING FOLDER IN A .pkl FILE.
#
iterList = []
rainList = []
#
## The only time this function is run is if the bucket tip is reported. This is the "callback".
def gotPulse(channel):          # 0.011" of rain causes one bucket-tip (1 pulse)
    global gppulse,gpstart      # use global variables for "gotPulse pulse", and "gotPulse start" values.
    if time.time() > gpstart:
        pDiff = time.time() - gpstart
        gppulse += 1
        logger.info('At {} we got a pulse. Total pulses this cycle: {}. pDiff is {}'.format(gpstart,gppulse,pDiff))
    gpstart = time.time()
    return gppulse,gpstart

GPIO.add_event_detect(26, GPIO.FALLING, callback=gotPulse, bouncetime=200)
# GPIO.add_event_detect(26, GPIO.FALLING, callback=gotPulse)
def main():
    global rpulse,gppulse,gpstart           # use global variables for "reported pulse", "gotPulse pulse", and "gotPulse start" values.
    checkit = GPIO.input(26)
    try:
        iterList = []                       # Zero out the list for intermediate data collection.
        rainList = []                       # Zero out the list for compiled data collection.
        cntCycle = time.time()              # Establish a counter variable for our 60-second loops.
# Part I
        while time.time() - cntCycle < 58:  # Run for 58 secs, leaving 2 secs for Part II.
            timeVal = time.time()           # current time of this pulse-check cycle.
            if gppulse >= 1:                # There was one or more pulses, so
                rpulse = gppulse            # hold on to number of pulses since last read.
            else:
                rpulse = 0                  # there were no pulses.
                gpstart=time.time()         # so reset pulse time logged value.
            iterList = [rpulse,timeVal,gpstart]     # fill the intermediate list with the current values.
            rainList.append(iterList)       # add the intermediate list values to the compiling list.
            gppulse = 0                     # reset base values for next iteration.
            gpstart = time.time()           # reset base values for next iteration.
            rpulse = 0                      # reset base values for next iteration. (this was missing, and causing inflated reports.)
            sleep(1)
        else:                               # After the 58 seconds passes, do part II.
#  Part II                                  # Part II ends with a file named rainData.pkl in our working folder.
            logger.debug(rainList)
                                            # That file is then snagged by outMainDATA.py and its contents are 
                                            # compiled into a record which is then added to mySQL on the indoor server.
                                            # If we are unable to connect with the indoor server, we retain the older data,
                                            # and the newer data is appened to the record in rainData.pkl so it can all be added 
                                            # once network connectivity is restored.  Once the data has been successfully uploaded to the 
                                            # indoor server, rainData.pkl is deleted by outMainDATA.py.
            if os.path.exists(RMDHome + '/rainData.pkl'):                                       # Check for .pkl file. One would exist if there had been network issues.
                with open(RMDHome + '/rainData.pkl', 'rb') as existpkl:
                    rainDataList = pickle.load(existpkl)                                        # Read the .pkl file contents into rainDataList.
                logger.info('rainDataList is '+ str(len(rainDataList)) + " records long.") 
                os.remove(RMDHome + '/rainData.pkl')                                            # delete the .pkl file after reading it.
                if not os.path.exists(RMDHome + '/rainData.pkl'):
                    logger.info("rainData.pkl Pickle file erased.")
                for row in rainList:                                                            # Append the contents of the new rainList to rainDataList.
                    rainDataList.append(row)
                logger.debug('Appended rainList to rainDataList.')
            else:                                                                               # There was no rainData.pkl file, so we are creating a new one here.
                logger.debug('Saving rainList to rainData.pkl.')
                rainDataList = rainList                                                         # Make rainDataList from rainList and move on.
        with open(RMDHome + '/rainData.pkl', 'wb+') as rdpkl:
            pickle.dump(rainDataList, rdpkl)                                                    # Save rainDataList to the .pkl file for outMainDATA.py.
        # logger.info('rainDataList is '+ str(len(rainDataList)) + " records. Saved to  /rainData.pkl.")
        lastTips = 0
        for lt in rainList:
            lastTips = lastTips + lt[0]
        if lastTips > 0:
            logger.info("There were {} tips counted in the last minute.".format(lastTips))
        rainList = []
        rainDataList = []
## We end up with a .pkl file that contains a list of 58 lists. Each of those contains tips,time at save,start time.
    except Exception as e:
        logger.info("Exception caught at bottom of try. Details: {}".format(e))
        pass
#
## outMainDATA takes it from there, resulting in another .pkl file that gets picked up by 
## allApp.py on Brilliant.
#
## = = = = = = = =  END OF RAIN CODE - START OF ERROR HANDLING, LOGGING AND WRAPUP CODE  = = = = = = = = =
#

def SignalHandler(signal, frame):
    if signal == 2:
        sigStr = 'CTRL-C'
        logger.info('* * * ' + sigStr + ' caught. * * * ')
    GPIO.cleanup()
    print("SignalHandler invoked")
    logger.info("Shutting down gracefully")
    logger.debug("Wrote to log in SignalHandler")
    logger.info("That's all folks.  Goodbye")
    logger.info(" - - - - rainMainDATA.py LOGGING STOPPED INTENTIONALLY - - - - ")
    sys.exit(0)

if __name__ == "__main__":
    #
    ## Arg parsing moved down here so we can use functions from this file as a module without conflicting the commandline arguments.
    #
    parserRMD = argparse.ArgumentParser()
    group = parserRMD.add_mutually_exclusive_group()
    group.add_argument('-d', '--debug', help="Turn on debugging output to log file.", action="store_true")
    group.add_argument('-f', '--func', help="Call the specified function.", action="store_true")
    RMDHome = os.getcwd()
  
    #
    config = configparser.RawConfigParser()
    config.read(RMDHome + '/out.conf')
    #
    argsRMD = parserRMD.parse_args()
    logger = logging.getLogger()
    log_file = RMDHome + '/RMD.log'
    log_handler = WatchedFileHandler(log_file)
    if argsRMD.debug:
        logger.setLevel(logging.DEBUG)
        log_handler.setLevel(logging.DEBUG)
        log_formatter = logging.Formatter('[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S')
        log_handler.setFormatter(log_formatter)
        logger.addHandler(log_handler)
        logger.info("--======================================================--")
        logger.info(" - - - - rainMainDATA.py LOGGING STARTED - - - - ")
        logger.info("Logging level set to DEBUG.")
    else:
        logger.setLevel(logging.INFO)
        log_handler.setLevel(logging.INFO)
        log_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
        log_handler.setFormatter(log_formatter)
        logger.addHandler(log_handler)
        logger.info("--======================================================--")
        logger.info(" - - - - rainMainDATA.py LOGGING STARTED - - - - ")
        logger.info("Logging level set to INFO.")
    #
    logger.info("  INITIAL CONFIGURATION COMPLETE  ")
    logger.debug("'HOME' path is: " + RMDHome)
    #
    ## END Args parsing and logging setup.
    #
    signal.signal(signal.SIGINT, SignalHandler)  ## This one catches CTRL-C from the local keyboard
    signal.signal(signal.SIGTERM, SignalHandler) ## This one catches the Terminate signal from the system    
    try:
        print(" Top of try")
        while True:
            main()
        pass
#                print("Bottom of try")
    except Exception:
        logger.info("Exception caught at bottom of try.", exc_info=True)
        GPIO.cleanup()
        error = traceback.print_exc()
        logger.info(error)
        logger.info("That's all folks.  Goodbye")
        logger.info(" - - - - rainMainDATA.py LOGGING STOPPED BY EXCEPTION - - - - ")

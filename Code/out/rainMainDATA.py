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

import time,os,logging,configparser,argparse,traceback,signal,sys,pickle,statistics
from time import sleep
import RPi.GPIO as GPIO

#
## - - - - - RAIN CODE BELOW HERE - - - - These lines log to RMD.log
#
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setwarnings(False)
rpulse = 0
#rstart = time.time()
gppulse = 0
gpstart = 0
timeVal = 0            
#                      # ('r' is for 'rain'.  rpulse is "rain pulse", rstart is "rain start", get it?)
##  STARTING HERE WE ARE GETTING THE BUCKET TIP DATA READY FOR outMainDATA TO PICK IT UP AS IT GOES BY.
##  WE COLLECT IT, STACK IT UP FOR 60 SECONDS, AND LEAVE IT LAYING IN THE WORKING FOLDER IN A .pkl FILE.
#
iterList = []
rainList = []
#
#
def gotPulse(channel):
    # 0.011" of rain causes one bucket-tip (1 pulse)
    global gppulse,gpstart
    gppulse =+ 1
    gpstart = time.time()
    logger.info('Got a pulse.')
    return gppulse,gpstart

GPIO.add_event_detect(12, GPIO.FALLING, callback=gotPulse, bouncetime=200)

def main():
    global rpulse,gppulse,gpstart
    digVal = GPIO.input(24)
#    if digVal == 0:
#        startCount = time.time()
#        endCount = startCount + 3600
    checkit = GPIO.input(12)
    # logger.info('Input pin 12 is :' + (str(checkit)))
    try:
        # logger.info('Top of main() try.')
#        while time.time() < endCount:
        iterList = []
        rainList = []
        cntCycle = time.time()
        # logger.info(int(cntCycle))
# Part I
        while time.time() - cntCycle < 58:
            timeVal = time.time()
            digVal = GPIO.input(24)
            if gppulse >= 1:
                rpulse = gppulse
            else:
                rpulse = 0
                gpstart=time.time()
            iterList = [rpulse,timeVal,gpstart,digVal]
            gppulse = 0
            gpstart = 0
            rainList.append(iterList)                                               ## add the most recent data to rainList.
            sleep(1)
        else:                                                                       ## After the 60 seconds (give or take) passes, do part II.
#  Part II
            if os.path.exists(RMDHome + '/rainData.pkl'):                           ## Check for .pkl file. One would exist if there had been network issues.
                rainDataList = pickle.load(open(RMDHome + '/rainData.pkl', 'rb'))   ## Read the .pkl file contents into rainDataList.
                logger.info('rainDataList variable was populated from rainData.pkl: ')
                os.remove(RMDHome + '/rainData.pkl')                                ## delete the .pkl file after reading it.
                # logger.info("rainData.pkl Pickle file erased.")
                for row in rainList:                                                ## Append the contents of the new rainList to rainDataList.
                    rainDataList.append(row)
                # logger.info('Appended rainList to rainDataList.')
            else:
                # logger.info('Saving rainList to rainData.pkl.')
                rainDataList = rainList                                             ## if there wasn't a .pkl file, make rainDataList from rainList and move on.
        pickle.dump(rainDataList, open(RMDHome + '/rainData.pkl', 'wb+'), pickle.HIGHEST_PROTOCOL) ## Save rainDataList to the .pkl file for outMainDATA.py.
        logger.debug('rainDataList is '+ str(len(rainDataList)) + " records long and was was saved in rainData.pkl.")
        rainList = []
        rainDataList = []
        pass

    except Exception:
        logger.info("Exception caught at bottom of try.", exc_info=True)
        pass
#

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
    logger = logging.getLogger(__name__)
    #
    config = configparser.RawConfigParser()
    config.read(RMDHome + '/out.conf')
    #
    argsRMD = parserRMD.parse_args()

    if argsRMD.debug:
        logging.basicConfig(filename=RMDHome + '/RMD.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
        logging.info("Debugging output enabled")
    else:
        logging.basicConfig(filename=RMDHome + '/RMD.log', format='%(asctime)s - %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
    #
    logger.info(" - - - - rainMainDATA.py LOGGING STARTED - - - - ")
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

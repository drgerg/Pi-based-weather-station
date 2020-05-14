#!/usr/bin/env python3

import time,os,logging,configparser,argparse,traceback,signal,sys
#from time import sleep
#import bme280
#import pickle
#import Adafruit_ADS1x15
#import RPi.GPIO as GPIO

parserTest = argparse.ArgumentParser()
group = parserTest.add_mutually_exclusive_group()
group.add_argument('-d', '--debug', help="Turn on debugging output to log file.", action="store_true")
group.add_argument('-f', '--func', help="Call the specified function.", action="store")
TestHome = os.getcwd()
logger = logging.getLogger(__name__)
#
config = configparser.RawConfigParser()
config.read(TestHome + '/out.conf')
#
argsTest = parserTest.parse_args()

if argsTest.func:
    Tfunc = argsTest.func
    print(Tfunc)

if argsTest.debug:
    logging.basicConfig(filename=TestHome + '/test.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
    logging.info("Debugging output enabled")
else:
    logging.basicConfig(filename=TestHome + '/test.log', format='%(asctime)s - %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
#
logger.info(" - - - - z-sysRunTest.py DATA LOGGING STARTED - - - - ")
#logger.info("         z-sysRunTest.py INITIAL CONFIGURATION COMPLETE  ")
#logger.info("'HOME' path is: " + TestHome)

#
## - - - - - TEST CODE BELOW HERE - - - -
#
#  Last time I checked, these were the systemctl .service files I've written.
#  They are located in /lib/systemd/system/ on these Raspbian OS Pi's around here.
#     outApp.service - old, formerly used to run Flask/Gunicorn on the WeatherPi
#     outBgFan.service - manages the system fan's speed based on CPU temp
#     outCam.service - serves a 640x480 image from the Pi Cam to Zoneminder on .22
#     outMainDATA.service - the main program for getting sensor data together and out to .150
#     outWPBoot.service - this and wPiBoot.py work together to reboot the pi when network is lost
#     rainMainDATA.py - acquires and formats rainfall data from sensors.  Presents it to outMainDATA.py.
#
def main():
    list = ['outBgFan.service','outCam.service','outMainDATA.service','outWPBoot.service','rainMainDATA.service']
    for item in list:
        status = os.system('systemctl is-active --quiet ' + item)
        if status == 0:
            strStat = 'OK'
        else:
            strStat = 'NOT OK'
        print('{:>14s} {:<22s}'.format(strStat + ' :', item))
        logger.info('{:>14s} {:<22s}'.format(strStat + ' :', item))
    logger.info(' End of Report ')

## - - - - - - END TEST CODE - - - - - - - 
#

def SignalHandler(signal, frame):
    if signal == 2:
        sigStr = 'CTRL-C'
        logger.info('* * * ' + sigStr + ' caught. * * * ')
    print("SignalHandler invoked")
    logger.info("Shutting down gracefully")
    logger.debug("Wrote to log in SignalHandler")
    logger.info("That's all folks.  Goodbye")
    logger.info(" - - - - z-RunTest.py DATA LOGGING STOPPED INTENTIONALLY - - - - ")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, SignalHandler)  ## This one catches CTRL-C from the local keyboard
    signal.signal(signal.SIGTERM, SignalHandler) ## This one catches the Terminate signal from the system    
    try:
#        print(" Top of try")
#        while True:
#            main()
        main()
        pass
#                print("Bottom of try")
    except Exception:
        logger.info("Exception caught at bottom of try.", exc_info=True)
        error = traceback.print_exc()
        logger.info(error)
        logger.info("That's all folks.  Goodbye")
        logger.info(" - - - - a-sysRunTest.py DATA LOGGING STOPPED BY EXCEPTION - - - - ")

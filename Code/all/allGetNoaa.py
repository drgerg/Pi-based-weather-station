#!/usr/bin/env python3
#
# allGetNoaa.py - Get the weather forecast for my location.
#  Zipcode and Country code are user-entered in allApp.conf.
# (c) 2020 - Gregory A. Sanders
#
"""
The ISO 8601 date-time value in the returned data from NOAA looks like this:
'2020-11-24T08:00:00-06:00'
This string is interpreted as: Year: 2020, Month: November, Day: 24th, Time: 08:00, Zulu Offset: -06:00 .

"""
import os, pickle, time, logging, argparse, signal, traceback, sys, configparser
from time import sleep
from noaa_sdk import noaa
n = noaa.NOAA()
noaaHome = os.path.abspath(os.path.dirname(__file__))
config = configparser.ConfigParser()
config.read(noaaHome + '/allApp.conf')

def main():
    logger = logging.getLogger(__name__)
    tnow = time.time()
    tnowHuman =  time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(tnow))
    nfdmtime = os.path.getmtime(noaaHome + '/noaaForecastData.pkl')                  ## nfdmtime is the .pkl file modification time from the OS.
    nfdmTHuman = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(nfdmtime))
    tdiff = tnow - nfdmtime                                                          ## difference between the mod time and now
    tdiffh = int(tdiff / 3600)                                                       ## difference boiled down to just the hours difference
    dateNow = time.strftime("%Y-%m-%d", time.localtime(tnow))
    if tdiffh >= 4:                                                                   ## every 4 hours, get a new forecast from NOAA
        zipc = config.get('NOAA','Zipcode')                                          ## get the zipcode out of allApp.conf
        cntc = config.get('NOAA','Country')                                          ## get the country code out of allApp.conf
        logger.info('Modification time of .pkl file is: ' + nfdmTHuman + '. Current time: ' + tnowHuman)
        logger.info('Requesting forecast for ' + str(zipc))
        res = n.get_forecasts(zipc, cntc, True)
        if dateNow in res[0]['startTime']:
            logger.info('Result of inquiry contains ' + str(dateNow))
            with open(noaaHome + '/noaaForecastData.pkl', 'wb') as dataFile:             ## dump the results of the request to the .pkl file
                pickle.dump(res, dataFile)
        else:
            logger.info('Something went wrong. The result data did not contain ' + str(dateNow))
    




def SignalHandler(signal, frame):
    if signal == 2:
        sigStr = 'CTRL-C'
        logger.info('* * * ' + sigStr + ' caught. * * * ')
    print("SignalHandler invoked")
    logger.info("Shutting down gracefully")
    logger.debug("Wrote to log in SignalHandler")
    logger.info("That's all folks.  Goodbye")
    logger.info(" - - - - allGetNoaa.py DATA LOGGING STOPPED INTENTIONALLY - - - - ")
    sys.exit(0)
#

if __name__ == "__main__":
    parserAGN = argparse.ArgumentParser(description = "Retrieves local weather forecast from NOAA every four hours.")
    parserAGN.add_argument('-d', '--debug', help="Turn on debugging output to log file.", action="store_true")


    # pklshwHome = os.getcwd()                              ## os.getcwd() give you the Current Working Directory.  If you run this from some other directory
    # print(pklshwHome)                                     ## then the test.log file (for example) gets written there, not in the directory where this 
    logger = logging.getLogger(__name__)                    ## python file lives.  

    argsAGN = parserAGN.parse_args()

    if argsAGN.debug:
        logging.basicConfig(filename=noaaHome + '/all.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
        logging.info("Debugging output enabled")
    else:
        logging.basicConfig(filename=noaaHome + '/all.log', format='%(asctime)s - %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
    #
    logger.info(" - - - - allGetNoaa.py DATA LOGGING STARTED - - - - ")
    signal.signal(signal.SIGINT, SignalHandler)  ## This one catches CTRL-C from the local keyboard
    signal.signal(signal.SIGTERM, SignalHandler) ## This one catches the Terminate signal from the system

    try:
        while True:                                                                  ## every minute, run the main() function
            main()
            sleep(60)
    except Exception:
        error = traceback.print_exc()
        logger.info(error)
        print('Goodbye')
        logger.info(" - - - - allGetNoaa.py DATA LOGGING STOPPED BY EXCEPTION - - - - ")
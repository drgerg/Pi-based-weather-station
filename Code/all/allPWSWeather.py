#!/usr/bin/env python3
#
#   allPWSWeather.py - Send logged data to AerisWeather's PWS Weather site.

#    2020 - Gregory Allen Sanders
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import time,os,logging,configparser,argparse,traceback,signal,sys,pickle,urllib
import allGetSQL
from time import sleep
from urllib.parse import quote
import urllib.request as request

#
## ConfigParser init area.  Get some info out of working.conf.
#
PWSHome = os.getcwd()
config = configparser.ConfigParser()
config.read(PWSHome + '/allApp.conf')
#
## End ConfigParser init

# recTime,pressure,outTemp,outTempC,outHumidity,windSpeed,winddir,wdirStr,extraHumid1,cpuTemp,recNum,fan1,rawRecTime

def main():
    global lastRecTime
    if lastRecTime == None:
        if os.path.isfile(PWSHome + '/LastRecTime.pkl'):
            lastRecTime = pickle.load(open(PWSHome + '/LastRecTime.pkl', 'rb'))
        else:
            lastRecTime = 0
    outData = allGetSQL.dataGrab()
    rawrectime = outData[12]
    if rawrectime > lastRecTime:
#        logger.info('This record is new: ' + str(rawrectime))
        recTime = outData[0]
        pressure = outData[1]
        pressNA = "{:.2f}".format(0.0295300 * pressure)
        outTemp = "{:.1f}".format(outData[2])
        outHumidity = str(outData[4])
        windSpeed = "{:.1f}".format(outData[5])
        winddir = str(outData[6])
        rawRecTime = outData[12]
        rain = str(outData[13])
#        logger.info(rain)
        url = config.get('PWS_Service','Service_URL')
        PID = config.get('PWS_Service','PWSID')
        PPW = config.get('PWS_Service','PWSPassword')
        softwaretype = 'custom_python'
        recordTime = time.strftime("%Y-%m-%d+%H:%M:%S",time.gmtime(rawRecTime))
        data_string = str(url+'?ID='+PID+'&PASSWORD='+PPW+'&dateutc='+recordTime+'&winddir='+winddir+'&windspeedmph='+windSpeed+'&tempf='+outTemp+'&baromin='+pressNA+'&humidity='+outHumidity+'&rainin='+rain+'&softwaretype='+softwaretype+'&action=updateraw')
        #data_string = str(url+'?ID='+PID+'&PASSWORD='+PPW+'&dateutc='+recordTime+'&winddir='+winddir+'&windspeedmph='+windSpeed+'&tempf='+outTemp+'&baromin='+pressNA+'&humidity='+outHumidity+'&softwaretype='+softwaretype+'&action=updateraw')
        try:
            with request.urlopen(data_string) as response:
                gotBack = response.read()
                if b'posted' in gotBack:
                    resp = 'Data logged and posted.'
                else:
                    resp = 'Data NOT logged and posted.'
#                logger.info(resp)
        except urllib.error.URLError as e: 
            ResponseData = e.reason
            logger.info('Error: ' + str(ResponseData))
            pass
        lastRecTime = rawrectime
    pickle.dump(lastRecTime, open(PWSHome + '/LastRecTime.pkl', 'wb+'), pickle.HIGHEST_PROTOCOL)
    sleep(10)
#
## = = = = = = = =  END OF MAIN CODE - START OF ERROR HANDLING, LOGGING AND WRAPUP CODE  = = = = = = = = =
#

def SignalHandler(signal, frame):
    if signal == 2:
        sigStr = 'CTRL-C'
        logger.info('* * * ' + sigStr + ' caught. * * * ')
    print("SignalHandler invoked")
    logger.info("Shutting down gracefully")
    logger.debug("Wrote to log in SignalHandler")
    logger.info("That's all folks.  Goodbye")
    logger.info(" - - - - DATA LOGGING STOPPED INTENTIONALLY - - - - ")
    sys.exit(0)

if __name__ == "__main__":
    #
    ## Arg parsing moved down here so we can use functions from this file as a module without conflicting the commandline arguments.
    #
    parserPWS = argparse.ArgumentParser()
    group = parserPWS.add_mutually_exclusive_group()
    group.add_argument('-d', '--debug', help="Turn on debugging output to log file.", action="store_true")
    group.add_argument('-f', '--func', help="Call the specified function.", action="store_true")
    logger = logging.getLogger(__name__)
    argsPWS = parserPWS.parse_args()

    if argsPWS.debug:
        logging.basicConfig(filename=PWSHome + '/PWS.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
        logging.info("Debugging output enabled")
    else:
        logging.basicConfig(filename=PWSHome + '/PWS.log', format='%(asctime)s - %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
    #
    logger.info(" - - - - DATA LOGGING STARTED - - - - ")
    logger.info("  INITIAL CONFIGURATION COMPLETE  ")
    logger.info("'HOME' path is: " + PWSHome)
    #
    ## END Args parsing and logging setup.
    #
    signal.signal(signal.SIGINT, SignalHandler)  ## This one catches CTRL-C from the local keyboard
    signal.signal(signal.SIGTERM, SignalHandler) ## This one catches the Terminate signal from the system    
    try:
#        print(" Top of try")
        lastRecTime = None
        while True:
            main()
        #main()
        pass
#                print("Bottom of try")
    except Exception:
        logger.info("Exception caught at bottom of try.", exc_info=True)
        error = traceback.print_exc()
        logger.info(error)
        logger.info("That's all folks.  Goodbye")
        logger.info(" - - - - DATA LOGGING STOPPED BY EXCEPTION - - - - ")



## = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
# SAMPLE STRING TO UPDATE DATA ON PWSWEATHER.com
#
# https://www.pwsweather.com/pwsupdate/pwsupdate.php?ID=STATIONID&PASSWORD=password&dateutc=2000-12-01+15%3A20%3A01&winddir=225&windspeedmph=0.0&windgustmph=0.0&tempf=34.88&rainin=0.06&dailyrainin=0.06&monthrainin=1.02&yearrainin=18.26&baromin=29.49&dewptf=30.16&humidity=83&weather=OVC&solarradiation=183&UV=5.28&softwaretype=Examplever1.1&action=updateraw
#
# All parameters are optional except for the ones marked with *.
# If your software or hardware doesn't support a parameter it can be omitted from the string.
#
# ID *		Station ID as registered
# PASSWORD *	Same password as used to login at http://www.pwsweather.com/login.php
# dateutc	*	Date and time in the format of year-mo-da+hour:min:sec
# winddir		Wind direction in degrees
# windspeedmph	Wind speed in miles per hour
# windgustmph	Wind gust in miles per hour
# tempf		Temperature in degrees fahrenheit
# rainin		Hourly rain in inches
# dailyrainin	Daily rain in inches
# monthrainin	Monthly rain in inches
# yearrainin	Seasonal rain in inches (usually local meteorological year)
# baromin		Barometric pressure in inches
# dewptf		Dew point in degrees fahrenheit
# humidity	Humidity in percent
# weather		Current weather or sky conditions using standard METAR abbreviations and intensity (e.g. -RA, +SN, SKC, etc.)
# solarradiation	Solar radiation
# UV		UV
# softwaretype *	Software type
#
# The string always concludes with action=updateraw to indicate the end of the readings
#
# For more information contact Joe Torsitano at jtorsitano@weatherforyou.com

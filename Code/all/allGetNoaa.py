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
import os, pickle, time, signal, traceback, sys, configparser
from time import sleep
from noaa_sdk import noaa
n = noaa.NOAA()
noaaHome = os.path.abspath(os.path.dirname(__file__))
config = configparser.ConfigParser()
config.read(noaaHome + '/allApp.conf')

def main():
    tnow = time.time()
    nfdmtime = os.path.getmtime(noaaHome + '/noaaForecastData.pkl')                  ## nfdmtime is the .pkl file modification time from the OS.
    nfdmTHuman = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(nfdmtime))
    tdiff = tnow - nfdmtime                                                          ## difference between the mod time and now
    tdiffh = int(tdiff / 3600)                                                       ## difference boiled down to just the hours difference
    if tdiffh > 4:                                                                   ## every 4 hours, get a new forecast from NOAA
        zipc = config.get('NOAA','Zipcode')                                          ## get the zipcode out of allApp.conf
        cntc = config.get('NOAA','Country')                                          ## get the country code out of allApp.conf
        if __name__ == "__main__":                                                   ## if run from command line, print stuff
            print('Retrieving data for ' + cntc + ' zip ' + zipc + '.')
        res = n.get_forecasts(zipc, cntc, True)
        with open(noaaHome + '/noaaForecastData.pkl', 'wb') as dataFile:             ## dump the results of the request to the .pkl file
            pickle.dump(res, dataFile)


def SignalHandler(signal, frame):
    if signal == 2:
        print("SignalHandler invoked")
    sys.exit(0)
#

if __name__ == "__main__":
    signal.signal(signal.SIGINT, SignalHandler)  ## This one catches CTRL-C from the local keyboard
    signal.signal(signal.SIGTERM, SignalHandler) ## This one catches the Terminate signal from the system    
    try:
        while True:                                                                  ## every minute, run the main() function
            main()
            sleep(60)
    except:
        error = traceback.print_exc()
        print(error)
        print('Goodbye')
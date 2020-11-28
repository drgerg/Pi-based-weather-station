#!/usr/bin/env python3
#
# noaaForecast.py - Get the weather forecast for my location.
# (c) 2020 - Gregory A. Sanders
#
"""
The ISO 8601 date-time value in the returned data from NOAA looks like this:
'2020-11-24T08:00:00-06:00'
This string is interpreted as: Year: 2020, Month: November, Day: 24th, Time: 08:00, Zulu Offset: -06:00 .

"""



import os, time, pickle, configparser
from noaa_sdk import noaa

n = noaa.NOAA()
noaaHome = os.path.abspath(os.path.dirname(__file__))
config = configparser.ConfigParser()
config.read(noaaHome + '/allApp.conf')
#

def pklChk():
    if not os.path.isfile(noaaHome + '/noaaForecastData.pkl'):
        zipc = config.get('NOAA','Zipcode')
        cntc = config.get('NOAA','Country')
        if __name__ == "__main__":
            print('\nnoaaForecastData.pkl does not exist.')
            print('Retrieving data for ' + cntc + ' zip ' + zipc + '.')
        res = n.get_forecasts(zipc, cntc, True)
        with open(noaaHome + '/noaaForecastData.pkl', 'wb') as dataFile:
            pickle.dump(res, dataFile)
    else:
        with open(noaaHome + '/noaaForecastData.pkl', 'rb') as existF:
            res = pickle.load(existF)
        if __name__ == "__main__":
            print('\nnoaaForecastData.pkl exists.  Proceeding.')
    return res
#
##
#
def fileAge():
    tnow = time.time()
    nfdmtime = os.path.getmtime(noaaHome + '/noaaForecastData.pkl')                  ## nfdmtime is the .pkl file modification time from the OS.
    nfdmTHuman = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(nfdmtime))
    tdiff = tnow - nfdmtime
    tdiffh = int(tdiff / 3600)
    tdiffm = int((tdiff - (tdiffh * 3600)) / 60)
    if tdiffh == 1:
        hplur = str(tdiffh) + ' hour '
    else: 
        hplur = str(tdiffh) + ' hours '

    if tdiffm == 1:
        mplur = str(tdiffm) + ' minute '
    else:
        mplur = str(tdiffm) + ' minutes '

    if __name__ == "__main__":
        stdPrint(tnow,nfdmTHuman,hplur,mplur)
    return(tdiff,tdiffh,tdiffm)
#
##
#
def stdPrint(tnow,nfdmTHuman,hplur,mplur):
    print('Data is ' + hplur + 'and ' + mplur + 'old.')
    print('Data last retrieved: ' + nfdmTHuman)
    print('       Current Time: ' + time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(tnow)))
#
##
#
def main():
    pklChk()
    fileAge()

if __name__ == "__main__":
    main()
# res = n.offices('MOB')
# print(res)
# # for i in res:
# #     print(i)
# for key, value in res.items():
#     print(key, '->', value)
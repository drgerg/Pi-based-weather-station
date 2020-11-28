#!/usr/bin/env python3
#
# allNoaaMain.py - Get the weather forecast for my location.
# (c) 2020 - Gregory A. Sanders
#
"""
The ISO 8601 date-time value in the returned data from NOAA looks like this:
'2020-11-24T08:00:00-06:00'
This string is interpreted as: Year: 2020, Month: November, Day: 24th, Time: 08:00, Zulu Offset: -06:00 .

Use 'test.html' to test this stuff out.  Render from allApp.py.

Let .service run to gather the forecast every x hours, from allApp.conf.

Get today's date
Assign today's DAY
Assign today's HOUR
Get today's forecast if we haven't yet.
dump to .pkl

Pull temperature, windSpeed, windDirection, shortForecast, icon for each day


"""
#
## 
#
import os, time, pickle, configparser, dateutil.parser, noaaForecast
from datetime import datetime, timedelta
from noaa_sdk import noaa
dutil = dateutil.parser
nf = noaaForecast
tnow = time.time()

def makeHourFC7():
    tnow = time.time()
    tdiff,tdiffh,tdiffm = nf.fileAge()
    dateNow = time.strftime("%Y-%m-%d", time.localtime(tnow))
    dayNow = time.strftime("%a", time.localtime(tnow))
    ThourNow = 'T' + time.strftime("%H", time.localtime(tnow))
    hourNow = time.strftime("%H"+'00', time.localtime(tnow))
    # while 
    fcrawdata = nf.pklChk()
    firstDay = datetime.strptime(fcrawdata[0]['startTime'][:10], '%Y-%m-%d')
    dayList = []
    dayMax = 0
    dayMin = 200
    fDay = firstDay
    lastDay = fDay + timedelta(days=7)
    while fDay < lastDay:
        for i in fcrawdata:
            if datetime.strptime(i['startTime'][:10], '%Y-%m-%d') == fDay:
                if i['temperature'] > dayMax:
                    dayMax = i['temperature']
                if i['temperature'] < dayMin:
                    dayMin = i['temperature']
            dayMMT = str(dayMax) + '/' + str(dayMin)
        dayList.append(str(fDay)[:10] + ',' + dayMMT)
        dayMax = 0
        dayMin = 200
        fDay = fDay + timedelta(days=1)

    hourFC7 = []
    for i in fcrawdata:
        if ThourNow in i['startTime']:
            iDay = datetime.strptime(i['startTime'][:10], '%Y-%m-%d')              ## 'startTime' is in ISO8601 format
            for d in dayList:
                if d[:10] == str(iDay)[:10]:
                    dayMMT = d.split(',')[1]
            idtDay = datetime.strftime(iDay, "%a")
            # hourFC7.append(idtDay + ',' + str(hourNow) + ',' + str(i['temperature']) + ',' + str(i['windSpeed']) + ',' + str(i['windDirection']) + ',' + str(i['shortForecast']))
            hourFC7.append(idtDay + ',' + str(dayMMT) + ',' + str(hourNow) + ',' + str(i['temperature']) + ',' + str(i['windSpeed']) + ',' + str(i['windDirection']) + ',' + str(i['shortForecast']))
    return hourFC7

if __name__ == "__main__":
    makeHourFC7()
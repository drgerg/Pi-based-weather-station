#!/usr/bin/env python3
#
#   outMainDATA.py - A working file to build the data logging parts of outMain.py.

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
import datetime
import time
import argparse
## July 2023 started using bme280.py from cmur2 at Github
## November 2025 shifted to RPi.bme280 by rm-hull.
import smbus2
# import bme680  ## BME680 died.  I had a 280 on hand.
import bme280  ## this module is RPi.bme280 from PyPI.
import os
import subprocess
import logging
import signal
import sys
import statistics
from statistics import mean
import mysql.connector
import configparser
import pickle
import windDir as wDirection
from time import sleep
import RPi.GPIO as GPIO
from mysql.connector import MySQLConnection, Error
import dht22  ## a different DHT22 module
DHT_SENSOR = dht22.DHT22(pin=24)  # for the different DHT22 module
# import Adafruit_DHT  ## Unloaded November 2025
# DHT_SENSOR = Adafruit_DHT.DHT22  # for the Adafruit module
# dht_pin = 24                     # for the Adafruit module

wsPin = 25
rps = 0
kph = 0
mph = 0
rpulse = 0
timeVal = 0
rstart = 0
accResults = []
pklData = []
tableData = []
numBadPings = 0
pressure = 0
outTemp = 0
outHumidity = 0
windSpeed = 0
winddir = 0
windGust = 0
windGustDir = 0
rainRate = 0
rain = 0
extraTemp1 = 0 # CPU temp
bustedLogged = 0 # log it once
#
    # MOVED GPIO SETUP LINES HERE attempting to reduce file handles. NOVEMBER 2025
    # That was the second move. We can leave it here.
GPIO.setmode(GPIO.BCM)
GPIO.setup(wsPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(dht_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) ## to support the ADAFruit DHT22 module
GPIO.setwarnings(False)
#
BMEport = 1
BMEaddress = 0x76
BMEbus = smbus2.SMBus(BMEport)

#
## GET TEMP FROM 1-WIRE PROBE
#
def getTemp(probe):
    probeSerial = config.get('Probes',probe)
    # probeName = config.get('ProbeNames',probe + 'Name')
    probeAdjust = float(config.get('ProbeAdjust',probe + 'Adjust'))
    def getRaw():
        with open('/sys/bus/w1/devices/' + probeSerial + '/w1_slave', 'r') as f:
            firLine = f.readline()                 # read 1st line
            time.sleep(1)
            # logger.info(str(firLine))
            secLine = f.readline()                 # read 2nd line
            time.sleep(1)
            # logger.info(str(secLine))
        return firLine,secLine

    try:
        lenLine = 0
        countdown = 3
        while lenLine == 0 and countdown != 0:
            firLine,secLine = getRaw()
            if countdown <= 2:
                logger.info("Countdown is: " + str(countdown))
            countdown = countdown - 1
            lenLine = len(firLine)
        if countdown == 0:
            logger.info("Never got a good value from the probe.")
            gettemp = 99999
            pass
        else:
            crc = firLine.rsplit(' ',1)
            crc = crc[1].replace('\n', '')
            if crc=='YES':
                # line = f.readline()             # read 2nd line
                gettemp = secLine.rsplit('t=',1)
                gettemp = gettemp[1]
            else:
                gettemp = 99999
    except IndexError:
        logger.info('Caught IndexError exception in getRaw().')
        gettemp = 99999
    tempC3 = (int(gettemp)/1000)
    tempF3 = float(9/5 * tempC3 + 32.00) + probeAdjust
    return tempC3,tempF3
#
#
## DHT22 SENSOR DATA GRABBER FUNCTION
#
def dht22Data():
    humidity = 0
    tempC = 0
    while humidity == 0 or tempC == 0:
        result = DHT_SENSOR.read()                           # for the 'dht22' module
        humidity = result.humidity                           # for the 'dht22' module
        tempC = result.temperature                           # for the 'dht22' module
        # result = Adafruit_DHT.read_retry(DHT_SENSOR,dht_pin)   # for Adafruit module
        # humidity = result[0]                                   # for Adafruit module
        # tempC = result[1]                                      # for Adafruit module
        time.sleep(.5)
        if tempC == None:
            tempC = -17.77778
            humidity = 50
    # logger.info("DHT22 tempC: {}, Humidity: {}".format(tempC,humidity))                 
    return humidity, tempC
#    
##      Setup for Sensor Data Logging.  Each parameter gets logged for a minute
##      then we run some stats, and share the output of that with the next step.
#
def datagrabber():
    global timeVal
    start = time.time()
    accPress = []
    accTemp = []
    accHum = []
    # accXhum = []
    accWspdK = []
    accWspdM = []
    accWdir = []
    accWdeg = []
    rain = 0
    rainRate = 0
    lastrps = 0

    while time.time() - start < 57:                       ## The plan here is to run this for a minute,
        #                                                 ## then get the median values to return.
        ## GET WIND SPEED
        #
        pstart = time.time()
        elapse = 0
        pulse = 0
        while elapse < 2:
            pRtn = GPIO.wait_for_edge(wsPin, GPIO.FALLING,timeout=1000)
            if pRtn != None:
                pulse += 1
            elapse = time.time() - pstart
        rps = pulse/elapse                              ## rps is Revolutions Per Second
        kph = '{:.2f}'.format(rps * 2.40114125)
        mph = '{:.2f}'.format(rps * 1.492)
        if float(mph) > 150.0: #                        ## The idea here is to discard outliers.
            rps = lastrps #                             ## use the last valid rps value.
            kph = '{:.2f}'.format(rps * 2.40114125) #   ## and recalculate
            mph = '{:.2f}'.format(rps * 1.492)
            logger.info("Dropped a bizarre wind speed. Bad pulse: {}".format(pulse))
        else:
            lastrps = rps #                             ## update rps to this cycle's value.
        #
        ## START TEMP, HUMIDITY, PRESSURE GATHERING
        #
        busted = bustedStuffHandler()
        if len(busted) > 0:
            print("busted: {}.".format(busted))
        if 'bmeoff' not in str(busted):
            outTemp2,pressure,outHumidity2 = bme()              ## ACQUIRE alternateTEMP,PRES from BME680
            if outTemp2 == -99.9:                               ## If there was an OSError, provide null values here.
                outTemp2 = -17.77778
                outHumidity2 = 0
                pressure = 0
            logger.debug("BME280 values: {}, {}, {}".format(outTemp2,pressure,outHumidity2))
            print("BME outTemp2 converted to F: {}.".format(float(9/5 * outTemp2 + 32.00)))

        else:  ## If something goes wrong with the BME sensor, these are like null values.
            outTemp2 = -17.77778
            outHumidity2 = 0
            pressure = 0
            # print("BME280 outTemp {}.".format(float(9/5 * outTemp2 + 32.00)))
        
        if 'dhtoff' not in str(busted):
            outHumidity,outTemp = dht22Data()                   ## ACQUIRE humidity and tempC from DHT22
            logger.debug("DHT22 values: {}, {}".format(outHumidity,outTemp))
            print("DHT  outTemp converted to F: {}.".format(float(9/5 * outTemp + 32.00)))
        #
        ## outTemp and outHumidity are required variables, so they must have some values.
        ## If both sensors are offline, we need to provide some zeros.
        #
        if 'dhtoff' in str(busted) and not 'bmeoff' in str(busted):
            outTemp = outTemp2                                  ## use BME values instead of DHT22
            outHumidity = outHumidity2                          ## use BME values instead of DHT22
        if 'dhtoff' in str(busted) and 'bmeoff' in str(busted):
            outTemp = -17.77778
            outHumidity = 0
        #
        ## Get temp from the 1-wire probe.
        #
        tempC3,tempF3 = getTemp("Probe1")
        print("PRB   tempC3 converted to F: {}.\n".format(tempF3))
        #
        ##
        #  
        if 'windoff' not in str(busted):
            wdir,wdeg = wDirection.main()                       ## ACQUIRE wdir (string) and wdeg (float) FROM windDir.py
            logger.debug("Wind values: {}, {}".format(wdir,wdeg))
#
##      WATCH OUT FOR WILD TEMPERATURE VALUES. Sometimes wierd shit happens.
        if outTemp is not None:
            if outTemp > 51.60 or outTemp < -31.60:
                outTemp = -17.777777777777778              ## Set to 0F, -17.7777777778C.
                logger.info("Wild temps reported. Set to zero.")
#
##      ACQUIRE rain, rainRate from .pkl file (if exists)
#          0.011" of rain causes one bucket-tip (1 pulse)
        if os.path.exists(OMDHome + '/rainData.pkl'):     ## Check for .pkl file from rainMainDATA.py
            try:
                timeVal = time.time()
                rainData = [0,timeVal,timeVal]                          ## Set rainData as an empty list in case loading the .pkl fails.
                with open(OMDHome + '/rainData.pkl', 'rb') as rdpkl:
                    rainData = pickle.load(rdpkl)
                if len(rainData) > 58:
                    logger.info('rainData variable was populated from rainData.pkl. ' + str(len(rainData)) + " records.")
            except EOFError:
                logger.debug("Encountered an empty .pkl file.  Moving on without it.")
                rainData = [0,0,0]
                rdpkl.close()
            os.remove(OMDHome + '/rainData.pkl')          ## delete the .pkl file after reading it.
            if not os.path.exists(OMDHome + '/rainData.pkl'):
                logger.debug("rainData.pkl Pickle file erased.")
            logger.debug('The rainData list has ' + str(len(rainData)) + ' records in it at datagrabber().')
            tips = 0
            for row in rainData:
                if type(row) is list:  ## added this to counter a random 'int object not subscriptable' error.
                    tips = tips + row[0]                               ## Add the 'tips' value for each row.
                    timeVal = row[1]
                else:
                     rain = 0
            # A relay was added to prevent inductive interference.  I think 1.0 pulses is now 0.5 pulses.
            # rain = rain + (tips * 0.011)                           ## 0.011 inches per tip was the original value
            # So, for each 'pulse' recorded there was twice as much rainfall.
            rain = rain + (tips * 0.022)                           ## rain in the last minute

            if rain > 0:
                logger.info("rainData.pkl brought us {} tips.".format(tips))
                logger.info('Calculated ' + str(rain) + ' inches from ' + str(tips) + ' tips from rainData.pkl.')
            rainRate = (rain * 60)                          ## rain variable times 60 gives us rain per hour
            
        accPress.append(pressure)
        accTemp.append(outTemp)    ## FYI: outTemp is in C, not F no matter what sensor generated it.
        accHum.append(outHumidity)
        accWspdK.append(float(kph))
        accWspdM.append(float(mph))
        accWdeg.append(wdeg)
        if argsOMD.debug:
            print(str(time.time() - start) + ': Wind Deg: ' + str(wdeg) + ' Wind Speed: ' + str(mph))
    logger.debug('outTemp: {}, outTemp2: {}'.format(float(9/5 * outTemp + 32.00),float(9/5 * outTemp2 + 32.00)))
    logger.debug('Humidity DHT22: {}'.format(outHumidity))
    logger.debug('BME280 temp: {}, Pressure: {}'.format(outTemp2,pressure))
    loopTimer = time.time() - start
    logger.debug('time.time() - start = ' + str(loopTimer))
    pressure = statistics.median(accPress)                ## Get the middle value in the list of values
    outTemp = statistics.median(accTemp)                  ## accumulated over the last 60 seconds (float type)
    outHumidity = statistics.median(accHum)
    windSpeed = statistics.median(accWspdM)
    windGust = max(accWspdM)
    if argsOMD.debug:
        print(accWspdM)
    winddir = statistics.median(accWdeg)
    wdirStr = wDirCvt(winddir)                            ## use the wDirCvt function to generate the string value for wind direction
#                                                         ## from the middle wind direction (in degrees) 
    logger.debug('outMainData.py datagrabber() has run and is returning values to mydb().')
    if rain > 0:
        logger.info('Reporting ' + str(rain) + ' inches of rain to mydb().')
    # logger.info("Windspeed: {}".format(windSpeed))
    return pressure,outTemp,outHumidity,windSpeed,winddir,wdirStr,rain,rainRate,timeVal,windGust
#
##
#
def bustedStuffHandler():
    global bustedLogged
    if os.path.exists(OMDHome + '/allbustedstuff.txt'):
        bustedstuff = []                                    ## allbustedstuff.txt is only worked when it contains these strings.
        with open(OMDHome + '/allbustedstuff.txt', 'r') as zd:
            bustedstuff = zd.readlines()
        zd.close()
        if "dhtoff" in str(bustedstuff):
            outHumidity = 0
            outTemp = -17.77778
            if "logged" not in str(bustedstuff):
                logger.info("Found 'dhtoff' in bustedstuff. THIS SHOULD ONLY BE LOGGED ONCE")
                bustedstuff.append("logged")
        if "bmeoff" in str(bustedstuff):
            pressure = 0
            outTemp2 = 0
            if "logged" not in str(bustedstuff):
                logger.info("Found 'bmeoff' in bustedstuff THIS SHOULD ONLY BE LOGGED ONCE.")
                bustedstuff.append("logged")
        if "windoff" in str(bustedstuff):
            windSpeed = 0
            winddir = 0
            wdirStr = "NA"
            windGust = 0
            if "logged" not in str(bustedstuff):
                logger.info("Found 'windoff' in bustedstuff THIS SHOULD ONLY BE LOGGED ONCE.")
                bustedstuff.append("logged")
        if "rainoff" in str(bustedstuff):
            rain = 0
            rainrate = 0
            if "logged" not in str(bustedstuff):
                logger.info("Found 'rainoff' in bustedstuff THIS SHOULD ONLY BE LOGGED ONCE.")
                bustedstuff.append("logged")
        with open("allbustedstuff.txt", "w") as abs:
                for bs in bustedstuff:
                    abs.write(bs)
                    print(bs)
        abs.close()
    else:
        bustedstuff = []
        bustedLogged = 0
    if len(bustedstuff) > 0 and bustedLogged == 0:
        logger.info("busted: {}".format(bustedstuff))
        bustedLogged = 1
    return bustedstuff
#
##
# 
def wDirCvt(wdegval):
    winddirS = "Not Connected"
    val = wdegval
    if val <= 11.25 or val == 0:
        val = val + 360
    if 348.76 <= val <= 371.25:
        winddirS = "N"
    if 11.26 <= val <= 33.75:
        winddirS = 'NNE'
    if 33.76 <= val <= 56.25:
        winddirS = 'NE'
    if 56.26 <= val <= 78.75:
        winddirS = 'ENE'
    if 78.76 <= val <= 101.25:
            winddirS = 'E'
    if 101.26 <= val <= 123.75:
            winddirS = 'ESE'
    if 123.76 <= val <= 146.25:
            winddirS = 'SE'
    if 146.26 <= val <= 168.75:
            winddirS = 'SSE'
    if 168.76 <= val <= 191.25:
            winddirS = 'S'
    if 191.26 <= val <= 213.75:
            winddirS = 'SSW'
    if 213.76 <= val <= 236.25:
            winddirS = 'SW'
    if 236.26 <= val <= 258.75:
            winddirS = 'WSW'
    if 258.76 <= val <= 281.25:
            winddirS = 'W'
    if 281.26 <= val <= 303.75:
            winddirS = 'WNW'
    if 303.76 <= val <= 326.25:
            winddirS = 'NW'
    if 326.26 <= val <= 348.75:
            winddirS = 'NNW'
    return winddirS
#
# A calculation to approximate the dewpoint when humidity is over 50%
# Td = T - ((100 - RH)/5.)
#   
#
## GRAB SENSOR DATA FROM THE BME MODULE. 
#
def bme():
    tlist = []
    plist = []
    hlist = []
    for iter in range(4):
        try:
            BMEcalibration_params = bme280.load_calibration_params(BMEbus, BMEaddress)
            data = bme280.sample(BMEbus, BMEaddress, BMEcalibration_params)
            tlist.append(data.temperature)
            plist.append(data.pressure)
            hlist.append(data.humidity)
            time.sleep(3)
        except OSError as e:
            logger.info("bme() experienced error on iter {}.\n{}".format(iter,e))
            time.sleep(3)
            if iter == 3:
                tlist = [-99.9]
                plist = [0]
                hlist = [0]
                logger.info("Supplied -99.9 value for tlist as an error flag.")
    if tlist[0] != -99.9:
        sdt = round(mean(tlist),2) - 1.11         ## tempC (The -1.11 is a compensation value.)
        sdp = round(mean(plist),2)                ## pressure
        sdh = round(mean(hlist),2)                ## humidity
        outTemp2 = sdt
        pressure = sdp
        outHumidity2 = sdh
    else:
        outTemp2 = tlist[0]
        pressure = plist[0]
        outHumidity2 = hlist[0]
    # logger.info("outTemp2 at bme(): {}.".format(outTemp2))
    return outTemp2,pressure,outHumidity2
#
## START WRITE-TO-DATABASE FUNCTION
# Be aware that because we are using WiFi to connect to the network, we have to make arrangements in case
# the connection drops.  It happens.  So we are getting sensor data, putting it in a list, checking for a .pkl file
# which will exist if the connection test failed last time around, appending our new data to the data from that .pkl file,
# ping the SQL server machine, if good: write rows of data from our list and delete the .pkl file. If not good: dump the appended list to 
# the .pkl file (which overwrites it if it existed) and then swing back around to do it all again.
#
def mydb():
    global pklData,numBadPings
    # Get current values from all the sensors.
    pressure,outTemp,outHumidity,windSpeed,winddir,wdirStr,rain,rainRate,timeVal,windGust = datagrabber()
    # Get the vent fan RPM from the pickle file.
    try:
        with open(OMDHome + '/fanSpd.pkl', 'rb') as fsp:
            fan1 = pickle.load(fsp)
    except EOFError:
        logger.debug("Encountered an empty .pkl file.  Moving on without it.")
        fan1 = 0
        fsp.close()
        pass
    # Get the CPU temperature from the system.
    cpuT = cpuTemp()[1]
    # Now make sure all the variables are of the right type.  Take no chances.
    prs = float(pressure)
    otmp = float(outTemp)
    ohmd = float(outHumidity)
    wspd = float(windSpeed)
    wgust = float(windGust)
    wdir = float(winddir)
    wdirStr = wdirStr
    if rain > 0:
        rain = float(rain)
        logger.info('inside mydb(), rain is: ' + str(rain))
    if rainRate > 0:
        rainRate = float(rainRate)
    dtNow = int(time.time())
    dataTable = [dtNow,prs,otmp,ohmd,wspd,wdir,wdirStr,cpuT,fan1,rain,rainRate,wgust]  # Put all the readings into a list.
    if os.path.exists(OMDHome + '/allData.pkl'):            ## This .pkl file will exist if the upcoming ping test failed last time around.
        try:
            with open(OMDHome + '/allData.pkl', 'rb') as adp:
                pklData = pickle.load(adp)
            pklData.append(dataTable)                               ## Merge the recent data with the .pkl file data just in case we are still offline
            logger.debug('dataTable was appended to pklData')
        except EOFError:                                    # EOFError happens when the file is a zero-length file. So we just delete it.
             os.remove(OMDHome + '/allData.pkl')
             adp.close()
    else:
         pklData.append(dataTable)
         logger.debug('No allData.pkl found. "dataTable" was appended to "pklData".')
    DBhost=config.get('mySQL','Address')                    # get the mySQL login data from our config file.
    DBuser=config.get('mySQL','User')
    DBpasswd=config.get('mySQL','Password')
    DBdatabase=config.get('mySQL','Database')
    DBtable=config.get('mySQL','Table1')
    # Don't stop now . . . keep going!!!
    ## Check to see if we can ping the machine mySQL is running on
    pingRes = subprocess.call(['/bin/ping', '-c', '1', DBhost], stdout=subprocess.DEVNULL)  ## Ping test to make sure the SQL machine is there.
    logger.debug("Ping for server returned: " + str(pingRes))
    if pingRes == 0:                                        # We are connected.  Move ahead.  If not, don't do any of this stuff.
        if numBadPings > 0:
            logger.info("Connection to SQL server machine restored.")
        numBadPings = 0                                     # Prep the data, and send it to the SQL machine.
        for row in pklData:                                 # Normally there will only be one row. UNLESS the network was down, 
            dtNow = row[0]                                  # in which case there can be many.
            prs = row[1]
            otmp = row[2]
            ohmd = row[3]
            wspd = row[4]
            wdir = row[5]
            wdirStr = row[6]
            # xohmd = row[7]
            cpuT = row[7]
            fan1 = row[8]
            rain = row[9]
            rainRate = row[10]
            wgust = row[11]
            try:
                # prepare the database connector 
                mydb = mysql.connector.connect(
                    host=DBhost,
                    user=DBuser,
                    passwd=DBpasswd,
                    database=DBdatabase
                )
                cursor = mydb.cursor()                      # Attempt a connection with the remote database. If it is not there, 
                cursor.execute("select database();")        # an exception will be logged and we will save our data for the 
                # cursor.execute("SELECT outHumidity2 FROM " + DBdatabase + '.' + DBtable + " where id=(select max(id) from " + DBdatabase + '.' + DBtable + ")")
                record = cursor.fetchone()                  # next go-round.
                # logger.debug("Got outHumidity2: " + str(record[0]))
                # outHum2 = record[0]
                addRecord = ('INSERT INTO ' + DBdatabase + '.' + DBtable + '' \
                    ' (dateTime,pressure,outTemp,outHumidity,windSpeed,winddir,wdirStr,cpuTemp,fan1,rain,rainRate,windGust)' \
                    ' VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)')
                addData = (dtNow,prs,otmp,ohmd,wspd,wdir,wdirStr,cpuT,fan1,rain,rainRate,wgust)
                logger.debug(addRecord %addData)
                cursor.execute(addRecord,addData)
                cursor.execute("SELECT * FROM " + DBdatabase + '.' + DBtable + " where id=(select max(id) from " + DBdatabase + '.' + DBtable + ")")
                record = cursor.fetchone()
                logger.debug('The last record contains: ' + str(record))
                mydb.commit()
                cursor.close()
                mydb.close()
                pklData = []                                ## RESET pklData to an empty list.
                if timeVal > 0:
                    elapsedTime = time.time() - timeVal
                    # logger.info('From last Rain tick check to writing the database record was ' + str(elapsedTime) + ' seconds.')
                if os.path.exists(OMDHome + '/allData.pkl'):
                    os.remove(OMDHome + '/allData.pkl')
                    logger.debug("allData.pkl Pickle file erased.")
            except Exception:
                logger.info('Unable to connect with mySQL database.  Details to follow: ', exc_info=True)
                pass
            funNStr = sys._getframe().f_code.co_name
            logger.debug("Finished the " + funNStr + " function")
    else:                                                           # We are NOT CONNECTED.  Save our readings to a .pkl file
        logger.info("Ping test for SQL server machine failed.")
        numBadPings += 1
        with open(OMDHome + '/allData.pkl', 'wb+') as adpd:
            pickle.dump(pklData, adpd, pickle.HIGHEST_PROTOCOL)
        logger.debug("allData.pkl updated.")
        logger.info ("Number of bad pings is: " + str(numBadPings) + ".")
        if numBadPings >= 3:
            logger.info("Too many bad pings.  Setting up to reboot.")
            os.mknod(OMDHome + '/rebootItNow')
    # logger.info("mydb(), write-to-database function has run.\nallData.pkl populated.")
#
##  END OF WRITE-TO-DATABASE FUNCTION
#

#
## Grab the CPU temperature while you're at it.
#
def cpuTemp():
# Return CPU temperature in C and F
    # ct = os.popen('vcgencmd measure_temp').readline()
    ct = subprocess.run(["/usr/bin/vcgencmd", "measure_temp"], capture_output=True)
    ct = ct.stdout.decode("utf-8")
    logger.debug(ct)
    cpuRtn = ct.replace("temp=","").replace("'C\n","")
    cpuT1=float(cpuRtn)
    cpuT2=float(9/5 * cpuT1 + 32.00)
    return cpuT1,cpuT2
#
## = = = = = = = =  END OF WEATHER CODE - START OF ERROR HANDLING, LOGGING AND WRAPUP CODE  = = = = = = = = =
#
def SignalHandler(signal, frame):
        if signal == 2:
            sigStr = 'CTRL-C'
            logger.info('* * * ' + sigStr + ' caught. * * * ')
        print("SignalHandler invoked")
        logger.info("Cleaning up")
        GPIO.cleanup()
        logger.info("Shutting down gracefully")
        logger.debug("Wrote to log in SignalHandler")
        logger.info("Finished SignalHandler")
        logger.info("That's all folks.  Goodbye")
        logger.info(" - - - - outMainDATA.py DATA LOGGING STOPPED INTENTIONALLY - - - - ")
        sys.exit(0)

if __name__ == "__main__":
    #
    ## Arg parsing moved down here so we can use functions from this file as a module without conflicting the commandline arguments.
    #
    parserOMD = argparse.ArgumentParser()
    parserOMD.add_argument("-d", "--debug", help="Turn on debugging output to log file.", action="store_true")
    OMDHome = os.getcwd()
    logger = logging.getLogger(__name__)
    #
    config = configparser.RawConfigParser()
    config.read(OMDHome + '/out.conf')
    #
    argsOMD = parserOMD.parse_args()

    if argsOMD.debug:
        import traceback
        logging.basicConfig(filename=OMDHome + '/outMainDATA.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
        logging.info("Debugging output enabled")
    else:
        logging.basicConfig(filename=OMDHome + '/outMainDATA.log', format='%(asctime)s - %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
    #
    logger.info(" - - - - outMainDATA.py DATA LOGGING STARTED - - - - ")
    logger.info("  INITIAL CONFIGURATION COMPLETE  ")
    logger.info("'HOME' path is: " + OMDHome)
    #
    ## END Args parsing and logging setup.
    #
    import traceback
    try:
        signal.signal(signal.SIGINT, SignalHandler)  ## This one catches CTRL-C from the local keyboard
        signal.signal(signal.SIGTERM, SignalHandler) ## This one catches the Terminate signal from the system
        logger.debug(" Top of try")
        while True:
            mydb()
        pass

        logger.debug("Bottom of try")
#            logger.flush()
    except Exception:
        logger.info("Exception caught at bottom of try.", exc_info=True)
        error = traceback.print_exc()
        logger.info(error)
        logger.info("That's all folks.  Goodbye")
        logger.info(" - - - - outMainDATA.py DATA LOGGING STOPPED BY EXCEPTION - - - - ")

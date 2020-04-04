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
import datetime,time,bme280,rainMain,windSpd,outFan,os,logging,signal,sys,statistics,mysql.connector,configparser,pickle
import windDir as wDirection
import argparse
from time import sleep
import RPi.GPIO as GPIO
from mysql.connector import MySQLConnection, Error

parserOm = argparse.ArgumentParser()
parserOm.add_argument("-d", "--debug", help="Turn on debugging output to log file.", action="store_true")
OmHome = os.getcwd()
logger = logging.getLogger(__name__)
#
config = configparser.RawConfigParser()
config.read(OmHome + '/out.conf')
#
argsOm = parserOm.parse_args()

if argsOm.debug:
    import traceback
    logging.basicConfig(filename=OmHome + '/outMain.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
    logging.info("Debugging output enabled")
else:
    logging.basicConfig(filename=OmHome + '/outMain.log', format='%(asctime)s - %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
#
logger.info(" - - - - DATA LOGGING STARTED - - - - ")
logger.info("  INITIAL CONFIGURATION COMPLETE  ")
logger.info("'HOME' path is: " + OmHome)




wsPin = 16
rps = 0
kph = 0
mph = 0
rpulse = 0
relapse = 0
rstart = 0
accResults = []

pressure = 0
outTemp = 0
outHumidity = 0
extraHumid1 = 0 # rawHumidity
windSpeed = 0
winddir = 0
windGust = 0
windGustDir = 0
rainRate = 0
rain = 0
extraTemp1 = 0 # CPU temp


def datagrabber():  # Setup for Data Logging
    start = time.time()
    accPress = []
    accTemp = []
    accHum = []
    accXhum = []
    accWspdK = []
    accWspdM = []
    accWdir = []
    accWdeg = []

    while time.time() - start < 60:
        GPIO.setmode(GPIO.BCM)                            ## THIS BEGINS WIND SPEED ACQUISITION
        GPIO.setup(wsPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setwarnings(False)
        pstart = time.time()
        elapse = 0
        pulse = 0
        while elapse < 2:                                 
            pRtn = GPIO.wait_for_edge(16, GPIO.FALLING,timeout=1000)
            if pRtn != None:
                pulse += 1
            elapse = time.time() - pstart
        rps = pulse/elapse
        kph = '{:.2f}'.format(rps * 2.40114125)
        mph = '{:.2f}'.format(rps * 1.492)
        outTemp,pressure,outHumidity,extraHumid1 = bme()  ## ACQUIRE TEMP,PRES,HUM 
        wdir,wdeg = wDirection.main()                     ## ACQUIRE wdir (string) and wdeg (float) FROM windDir.py
        accPress.append(pressure)
        accTemp.append(outTemp)
        accHum.append(outHumidity)
        accXhum.append(extraHumid1)
        accWspdK.append(float(kph))
        accWspdM.append(float(mph))
        accWdeg.append(wdeg)
        if argsOm.debug:
            print(str(time.time() - start) + ': Wind Deg: ' + str(wdeg) + ' Wind Speed: ' + str(mph))
    pressure = statistics.median(accPress)               ## Get the middle value in the list of values
    outTemp = statistics.median(accTemp)                 ## accumulated over the last 60 seconds
    outHumidity = statistics.median(accHum)
    extraHumid1 = statistics.median(accXhum)
    windSpeed = statistics.median(accWspdK)
    winddir = statistics.median(accWdeg)
    wdirStr = wDirCvt(winddir)                          ## use the wDirCvt function to generate the string value for wind direction
                                                        ## from the middle wind direction (in degrees) 
    return pressure,outTemp,outHumidity,extraHumid1,windSpeed,winddir,wdirStr 
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
#   THESE ARE THE FINAL VARIABLES WE WANT TO PASS TO THE DATABASE
#   The database name is 'weewx' and the table is 'archive'.
#   
#   pressure
#   outTemp
#   outHumidity
#   extraHumid1 = rawHumidity
#   windSpeed
#   winddir
#   windGust
#   windGustDir
#   rainRate
#   rain
#   extraTemp1 = CPU temp
#   
#   

#   
#   I'm going to use the prefix 's_' to indicate a 'samples' list variable.  So 'outTemp' becomes 's_outTemp'.
#   's_outTemp' contains the list of values accumulated during this one-shot gathering episode.
#
## GRAB SENSOR DATA FROM THE BME280 MODULE
#
def bme():

    s_outTemp = []
    s_pressure = []
    s_outHumidity = []
    s_rawHumidity = []
    tstart = time.time()

    while time.time() - tstart < 2:
        tempC,pres,humid,preHum = bme280.readBME280All()
        s_outTemp.append(tempC)
        s_pressure.append(pres)
        s_outHumidity.append(humid)
        s_rawHumidity.append(preHum)
    outTemp = statistics.mean(s_outTemp)
    pressure = statistics.mean(s_pressure)
    outHumidity = statistics.mean(s_outHumidity)
    extraHumid1 = statistics.mean(s_rawHumidity)

    return outTemp,pressure,outHumidity,extraHumid1
#
## START WRITE-TO-DATABASE FUNCTION
#
def mydb():
    pressure,outTemp,outHumidity,extraHumid1,windSpeed,winddir,wdirStr = datagrabber()
    fan1 = pickle.load(open(OmHome + '/fanSpd.pkl', 'rb'))
    cpuT = cpuTemp()[1]
    prs = float(pressure)
    otmp = float(outTemp)
    ohmd = float(outHumidity)
    xohmd = float(extraHumid1)
    wspd = float(windSpeed)
    wdir = float(winddir)
    wdirStr = wdirStr
    funNStr = sys._getframe().f_code.co_name
    logger.debug("Started the " + funNStr + " function")
    dtNow = int(time.time())
    DBhost=config.get('mySQL','Address')
    DBuser=config.get('mySQL','User')
    DBpasswd=config.get('mySQL','Password')
    DBdatabase=config.get('mySQL','Database')
    DBtable=config.get('mySQL','Table1')
    mydb = mysql.connector.connect(
        host=DBhost,
        user=DBuser,
        passwd=DBpasswd,
        database=DBdatabase
    )
    cursor = mydb.cursor()
    cursor.execute("select database();")
    record = cursor.fetchone()
    logger.debug("Got the database: " + str(record))
    try:
        addRecord = ('INSERT INTO ' + DBdatabase + '.' + DBtable + '' \
            ' (dateTime,pressure,outTemp,outHumidity,windSpeed,winddir,wdirStr,extraHumid1,cpuTemp,fan1)' \
            ' VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)')
        addData = (dtNow,prs,otmp,ohmd,wspd,wdir,wdirStr,xohmd,cpuT,fan1)
        logger.debug(addRecord %addData)
        cursor.execute(addRecord,addData)
        cursor.execute("SELECT * FROM " + DBdatabase + '.' + DBtable + " where id=(select max(id) from " + DBdatabase + '.' + DBtable + ")")
        record = cursor.fetchone()
        logger.debug('The last record contains: ' + str(record))
        mydb.commit()
        cursor.close()
        mydb.close()
    except Exception:
        logger.info('Fatal Error in mydb()', exc_info=True)
    funNStr = sys._getframe().f_code.co_name
    logger.debug("Finished the " + funNStr + " function")
#
##  END OF WRITE-TO-DATABASE FUNCTION
#
def windSpd():
    
    pulse,elapse,start = windSpd.wsPulse()
    if elapse !=0:
        rps = pulse/elapse
        kph = '{:.2f}'.format(rps * 2.40114125)
        mph = '{:.2f}'.format(rps * 1.492)
        tNow = time.time()
        if tNow - start > 15:
            kph = 0
            mph = 0
    print('Wind Speed: ' + str(mph))
    return kph,mph
# 1 Hz (rev/sec) = 1.492 mph = 2.40114125 kph = 2401.1 m/h
#
def rainFall():
#    print('RainFall')
    global rpulse,relapse,rstart
#    rpulse,relapse,rstart = rainMain.rPulse()
    if rpulse == 0:
        inHr = '0'
    if rpulse == 1:
        inHr = 'Trace'
    if rpulse > 1:
        inHr = str('{:2f}'.format(rpulse*.011)/(relapse/360))
    return inHr



#
## Grab the CPU temperature while you're at it.
#
def cpuTemp():
# Return CPU temperature in C and F
    ct = os.popen('vcgencmd measure_temp').readline()
    cpuRtn = ct.replace("temp=","").replace("'C\n","")
    cpuT1=float(cpuRtn)
    cpuT2=float(9/5 * cpuT1 + 32.00)
#    cpuT = "CPU: " + str(temp1) + "C" + " (" + str(temp2) + "F)"
    #logger.debug(cpuTemp)
    #functionNameAsString = sys._getframe().f_code.co_name
    #logger.debug("Finished the " + functionNameAsString + " function")
    return cpuT1,cpuT2

def SignalHandler(signal, frame):
        if signal == 2:
            sigStr = 'CTRL-C'
            logger.info('* * * ' + sigStr + ' caught. * * * ')
        print("SignalHandler invoked")
        logger.info("Cleaning up")
        logger.info("Shutting down gracefully")
        logger.debug("Wrote to log in SignalHandler")
        logger.info("Finished SignalHandler")
        logger.info("That's all folks.  Goodbye")
        logger.info(" - - - - DATA LOGGING STOPPED - - - - ")
        sys.exit(0)

if __name__ == "__main__":
        import traceback
        try:
            signal.signal(signal.SIGINT, SignalHandler)  ## This one catches CTRL-C from the local keyboard
            signal.signal(signal.SIGTERM, SignalHandler) ## This one catches the Terminate signal from the system
            logger.info(" Top of try")
            while True:
                mydb()
            pass

            logger.info("Bottom of try")
#            logger.flush()
        except Exception:
            logger.info("Exception caught at bottom of try.", exc_info=True)
            error = traceback.print_exc()
            logger.info(error)
            logger.info("That's all folks.  Goodbye")
            logger.info(" - - - - DATA LOGGING STOPPED BY EXCEPTION - - - - ")

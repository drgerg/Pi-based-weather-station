#!/usr/bin/env python3
#
#   allGetSQL.py - Retrieve logged data.

#    2019 - Gregory Allen Sanders
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

import os,sys,time,logging,signal,configparser,mysql.connector
from mysql.connector import MySQLConnection, Error
import numpy as np

#
## ConfigParser init area.  Get some info out of working.conf.
#
agSQLAppHome = os.getcwd()
#agSQLAppHome = os.path.abspath(os.path.dirname(__file__))
config = configparser.RawConfigParser()
config.read(agSQLAppHome + '/allApp.conf')
#
## End ConfigParser init
logger = logging.getLogger(__name__)
#
#
def shopDataGrab():
    dtNow = time.strftime('%Y-%m-%d %H:%M:%S')
    DBsock = config.get('mySQL','Socket')
    DBhost=config.get('mySQL','Address')
    DBuser=config.get('mySQL','User')
    DBpasswd=config.get('mySQL','Password')
    DBdatabase=config.get('mySQL','Database1')
    DBtable=config.get('mySQL','d1Table3')
#    mydb = MySQLConnection(user=DBuser,database=DBdatabase)
    mydb = mysql.connector.connect(
        #host=DBhost,
        unix_socket=DBsock,
        user=DBuser,
        passwd=DBpasswd,
        database=DBdatabase
    )
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("select database();")
    dbName = cursor.fetchone()
    logger.info("Got the database: " + str(dbName))
    #
    ## Grab the last row's data.    dateTime,pressure,outTemp,outHumidity,windSpeed,winddir,wdirStr,extraHumid1,cpuTemp
    #
    cursor.execute("SELECT * FROM " + DBdatabase + '.' + DBtable + " where id=(select max(id) from " + DBdatabase + '.' + DBtable + ")")
    record = cursor.fetchone()
    logger.info('The last record is number: ' + str(record['id']))
#    print('The last record is number: ' + str(record['id']))
    shopTemp = float("{0:.2f}".format(float(record['shopTemp'])))
    shopHumidity = float("{0:.2f}".format(float(record['shopHumidity'])))
    shopCPU = float("{0:.2f}".format(float(record['shopCPU'])))
    return shopTemp,shopHumidity,shopCPU
#
#
def dataGrab():
    funNStr = sys._getframe().f_code.co_name
    logger.debug("Started the " + funNStr + " function")
    dtNow = time.strftime('%Y-%m-%d %H:%M:%S')
    DBsock = config.get('mySQL','Socket')
    DBhost=config.get('mySQL','Address')
    DBuser=config.get('mySQL','User')
    DBpasswd=config.get('mySQL','Password')
    DBdatabase=config.get('mySQL','Database1')
    DBtable=config.get('mySQL','d1Table1')
#    mydb = MySQLConnection(user=DBuser,database=DBdatabase)
    mydb = mysql.connector.connect(
        #host=DBhost,
        unix_socket=DBsock,
        user=DBuser,
        passwd=DBpasswd,
        database=DBdatabase
    )
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("select database();")
    dbName = cursor.fetchone()
    logger.debug("Got the database: " + str(dbName))
    #
    ## Grab the last row's data.    dateTime,pressure,outTemp,outHumidity,windSpeed,winddir,wdirStr,extraHumid1,cpuTemp
    #
    cursor.execute("SELECT * FROM " + DBdatabase + '.' + DBtable + " where id=(select max(id) from " + DBdatabase + '.' + DBtable + ")")
    record = cursor.fetchone()
#    logger.debug('The last record is number: ' + str(record['id']))
#    print('The last record is number: ' + str(record['id']))
    rawRecTime = record['dateTime']
    recTime = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(record['dateTime']))
    pressure = float("{0:.2f}".format(float(record['pressure'])))
    outTemp = float("{outTemp:.2f}".format(outTemp=(9/5 * float(record['outTemp']) + 32.00)))
    outTempC = record['outTemp']
    outHumidity = float("{0:.2f}".format(float(record['outHumidity'])))
    windSpeed = float("{0:.2f}".format(float(record['windSpeed'])))
    winddir = float("{0:.2f}".format(float(record['winddir'])))
    wdirStr = record['wdirStr']
    extraHumid1 = float("{0:.2f}".format(float(record['extraHumid1'])))
    cpuTemp = float("{0:.2f}".format(float(record['cpuTemp'])))
    recNum = record['id']
    fan1 = int(record['fan1'])
    rain = record['rain']
    wetDry = record['wetDry']
    rainRate = record['rainRate']
    if rain != None:
        rain = float(record['rain'])
    else:
        rain = 0
    logger.debug('There are ' + str(recNum) + ' records here.')
    cursor.close()
    mydb.close()
    return recTime,pressure,outTemp,outTempC,outHumidity,windSpeed,winddir,wdirStr,extraHumid1,cpuTemp,recNum,fan1,rawRecTime,rain,wetDry,rainRate

def poolDataGrab(GD):
    GD=str(GD)
    print("GD comes here as: " + GD)
    funNStr = sys._getframe().f_code.co_name
    logger.debug("Started the " + funNStr + " function")
#    DBhost=config.get('mySQL','Address')
    DBsock = config.get('mySQL','Socket')
    DBuser=config.get('mySQL','User')
    DBpasswd=config.get('mySQL','Password')
    DBdatabase=config.get('mySQL','Database2')
    DBtable=config.get('mySQL','d2Table1')
    mydb = mysql.connector.connect(
#        host=DBhost,
        unix_socket=DBsock,
        user=DBuser,
        passwd=DBpasswd,
        database=DBdatabase
    )
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("select database();")
    dbName = cursor.fetchone()
    logger.debug("Got the database: " + str(dbName))
    cursor.execute("SELECT * FROM " + DBdatabase + '.' + DBtable + " where id=(select max(id) from " + DBdatabase + '.' + DBtable + ")")
    record = cursor.fetchone()
    logger.debug('The last record is number: ' + str(record['id']))
    lastPt1 = float("{pt1:.2f}".format(pt1=(9/5 * float(record['pt1']) + 32.00)))
    lastPt2 = float("{pt2:.2f}".format(pt2=(9/5 * float(record['pt2']) + 32.00)))
    cursor.close()
    mydb.close()
    return lastPt1, lastPt2

def inchRainGrab():
    DBsock = config.get('mySQL','Socket')
    DBuser=config.get('mySQL','User')
    DBpasswd=config.get('mySQL','Password')
    DBdatabase=config.get('mySQL','Database1')
    DBtable=config.get('mySQL','d1Table1')
    mydb = mysql.connector.connect(
        unix_socket=DBsock,
        user=DBuser,
        passwd=DBpasswd,
        database=DBdatabase
    )
    cursor = mydb.cursor()
    cursor.execute("select database();")
    dbName = cursor.fetchone()
    logger.debug("Got the database: " + str(dbName))
    cursor.execute("SELECT dateTime,rain FROM " + DBdatabase + '.' + DBtable + " where (dateTime>UNIX_TIMESTAMP(CURDATE()) AND rain>'0')")
    record = cursor.fetchall()
    logger.info('Retrieved ' + str(len(record)) + ' records.')
    cursor.close()
    mydb.close()
#    print(record)
    inchRain = sum(inR[1] for inR in record)
#    print(inchRain)
    logger.info('Reported ' + str(inchRain) + ' inches of rain.')
    return inchRain

def SignalHandler(signal, frame):
        logger.info("Cleaning up . . . \n = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =")
        logger.info("Shutting down gracefully")
        logger.debug("This is SignalHandler")
        logger.info("Displayed .info and .debug in SignalHandler")
        logger.info("Shutdown initiated")
        logger.debug("Wrote to log in SignalHandler")
        sys.exit(0)


if __name__ == "__main__":
        try:
            import argparse

            ## Command line arguments parsing
            #
            parsersm = argparse.ArgumentParser()
            parsersm.add_argument("-d", "--debug", help="Turn on debugging output to stderr", action="store_true")
            argssm = parsersm.parse_args()
            if argssm.debug:
                logging.basicConfig(filename=agSQLAppHome + '/test.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
                logging.info("Debugging output enabled")
            else:
                logging.basicConfig(filename=agSQLAppHome + '/test.log', format='%(asctime)s - %(message)s.', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
            #
            ## End Command line arguments parsing

            signal.signal(signal.SIGINT, SignalHandler)
            logger.debug("Top of try")
            dataGrab()
            logger.info("Bottom of try")

        except  ValueError as errVal:
            print(errVal)
            pass
        logger.info("That's all folks.  Goodbye")


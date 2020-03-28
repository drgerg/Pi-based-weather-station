#!/usr/bin/env python3

import threading,time,bme280,windDir,rainMain,windSpd,outFan,os,logging,signal,sys,statistics
import argparse
from time import sleep
import RPi.GPIO as GPIO

parserOm = argparse.ArgumentParser()
parserOm.add_argument("-d", "--debug", help="Turn on debugging output to log file.", action="store_true")
OmHome = os.getcwd()
logger = logging.getLogger(__name__)

#
argsOm = parserOm.parse_args()

if argsOm.debug:
    import traceback
    logging.basicConfig(filename=OmHome + '/outMain.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
    logging.info("Debugging output enabled")
else:
    logging.basicConfig(filename=OmHome + '/outMain.log', format='%(asctime)s - %(message)s : %(name)s.', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
#
logger.info(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
logger.info("  INITIAL CONFIGURATION COMPLETE  ")
logger.info("'HOME' path is: " + OmHome)


global pill2kill
wsPin = 16
pulse = 0
start = time.time()
elapse = 0
rps = 0
kph = 0
mph = 0
rpulse = 0
relapse = 0
rstart = 0

def main():  # Start Windspeed and RainMain functions in threads
    global pill2kill
    pill2kill = threading.Event()
    ptW = threading.Thread(target=windS, args=(pill2kill,))
    ptW.start()
                    #if "Thread-1" in str(threading.enumerate()):
                    #    pcT = "running"
                    #else:
                    #    pcT = "not running"
                    #print("The windS thread is " +  pcT)
    ptR = threading.Thread(target=rainS, args=(pill2kill,))
    ptR.start()

    logger.info(str(threading.enumerate()))
    while True: # This just gives outMain.py a reason to carry on, which seems stupid, but is necessary.
                # We'll add mySQL datalogging in here.  Then it'll make sense to have it.
        #sleep(1)
        tempC,tempF,pres,pressNA,humid,preHum,kph,mph,wd,rainF,cpuT = allSensors()
        #tempC,pres,humid = 0,0,0
        tempF = float(9/5 * tempC + 32.00)           # in degrees Farenheit
#        print(str("Temp: " + str(tempF) + " WDir: " + wd[0] + " Wspd: " + str(mph)))
#        print(str(threading.enumerate()))
#        logger.info(str(threading.enumerate()))
    else:
        pass
#
## START ALL-SENSORS ACCUMULATION
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
#   windSpeed
#   windDir
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
def bme():
    s_outTemp = []
    s_pressure = []
    s_outHumidity = []
    s_rawHumidity = []
    tstart = time.time()

    while time.time() - tstart < 10:
        tempC,pres,humid,preHum = bme280.readBME280All()
        s_outTemp.append(tempC)
        s_pressure.append(pres)
        s_outHumidity.append(humid)
        s_rawHumidity.append(preHum)
    outTemp = statistics.mean(s_outTemp)
    pressure = statistics.mean(s_pressure)
    outHumidity = statistics.mean(s_outHumidity)
    rawHumidity = statistics.mean(s_rawHumidity)
    print(str(outTemp) + ', ' + str(pressure) + ', ' + str(outHumidity) + ', ' + str(rawHumidity))
    return 


def allSensors():
    tempC,pres,humid,preHum = bme280.readBME280All()
    #tempC,pres,humid = 0,0,0
    tempF = float(9/5 * tempC + 32.00)           # in degrees Farenheit
    pressNA = 0.0295300 * pres               # in inHg
    kph,mph = calcSpd()
    wd = windDir.main()
#    rainF = rainFall()
    rainF = "Inevitable "
    cpuT = cpuTemp()
    return tempC,tempF,pres,pressNA,humid,preHum,kph,mph,wd,rainF,cpuT
#
## END OF ALL-SENSORS ACCUMULATION FUNCTION
#
def calcSpd():
#    print('Calc Speed')
#    global pulse,elapse,rps,kph,mph,start,pulse
    pulse,elapse,start = windSpd.wsPulse()
    if elapse !=0:
#        print('Pulses: ' + str(pulse) + ' Time: ' + str(elapse))
        rps = pulse/elapse
        #print(str(rps) + ' RPS')
        #print(str(rps * 60) + ' RPM')
        kph = '{:.2f}'.format(rps * 2.40114125)
        mph = '{:.2f}'.format(rps * 1.492)
        tNow = time.time()
#        print('Time between samples: ' + str('{:.2f}'.format(tNow - start)) + ' seconds.')
        if tNow - start > 15:
            kph = 0
            mph = 0
#        print('KpH:' + str(kph) + '  MpH:' + str(mph))
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
## These two functions get started as threads to continuously check the status of wind speed and rain sensors.
## This keeps the main function freed up and looping quickly, which enhances responsiveness.
#
def windS(stop_event):
    global pulse,elapse,start
    while not stop_event.wait(1):
        pulse,elapse,start = windSpd.wsPulse()
    else:
        print("windS of 'outMain' dropped out")
        pass

def rainS(stop_event):
    global rpulse,relapse,rstart
    while not stop_event.wait(1):
        rpulse,relapse,rstart = rainMain.main()
    else:
        print("rainS of 'outMain' dropped out")
        pass



#
## Grab the CPU temperature while you're at it.
#
def cpuTemp():
# Return CPU temperature as a character string
    ct = os.popen('vcgencmd measure_temp').readline()
    cpuRtn = ct.replace("temp=","").replace("'C\n","")
    temp1=float(cpuRtn)
    temp2= '{:.2f}'.format(float(9/5 * temp1 + 32.00))
    cpuT = "CPU: " + str(temp1) + "C" + " (" + str(temp2) + "F)"
    #logger.debug(cpuTemp)
    #functionNameAsString = sys._getframe().f_code.co_name
    #logger.debug("Finished the " + functionNameAsString + " function")
    return cpuT

def SignalHandler(signal, frame):
        global pill2kill
        print("SignalHandler invoked")
        pill2kill.set()
        logger.info(" - - - - - - - - - - - - - - - - - - - - - ")
        logger.info("Cleaning up")
        GPIO.cleanup()
        logger.debug("Finished GPIO.cleanup() in SignalHandler")
        logger.info("Shutting down gracefully")
        logger.debug("Sent 'Shutdown Now' message")
        logger.debug("Wrote to log in SignalHandler")
        logger.info("Finished SignalHandler")
        logger.info("That's all folks.  Goodbye")
        sys.exit(0)

if __name__ == "__main__":
        global pill2kill
        import traceback
        try:
            signal.signal(signal.SIGINT, SignalHandler)  ## This one catches CTRL-C from the local keyboard
            signal.signal(signal.SIGTERM, SignalHandler) ## This one catches the Terminate signal from the system
            logger.info(" Top of try")
            while True:
                bme()
            pass

            logger.info("Bottom of try")
#            logger.flush()
        except Exception:
#            pill2kill.set()
            error = traceback.print_exc()
            logger.debug(error)
            logger.info("That's all folks.  Goodbye")

#!/usr/bin/env python3
""" outBgFan.py - Manage the 4-Wire Delta Electronics KDB050510HB recycled laptop cooling fan.
        This is intended to run as a standalone service to manage the speed of the fan based on the 
        CPU temperature.
    2019,2020 - Gregory Allen Sanders."""

import time,os,logging,signal,sys,argparse,pickle
from time import sleep
import RPi.GPIO as GPIO

parserBGF = argparse.ArgumentParser()
parserBGF.add_argument("-d", "--debug", help="Turn on debugging output to log file.", action="store_true")
parserBGF.add_argument("-t", "--temperature", help="Set the temp to this value for testing.", action="store")
BGFHome = os.getcwd()
logger = logging.getLogger(__name__)
argsBGF = parserBGF.parse_args()
#
if argsBGF.debug:
    import traceback
    logging.basicConfig(filename=BGFHome + '/BGFan.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
    logger.info(" - - - - Starting Up - - - - - - - - - Starting Up - - - - - - - ")
    logging.info("Debugging output enabled")
else:
    logging.basicConfig(filename=BGFHome + '/BGFan.log', format='%(asctime)s - %(message)s : %(name)s.', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
    logger.info(" - - - - Starting Up - - - - - - - - - Starting Up - - - - - - - ")
#    #

if argsBGF.temperature:
    dTemp = float(argsBGF.temperature)
    logging.debug("Debug temp set to: " + str(dTemp))
else:
    dTemp = 60

logger.info("  INITIAL CONFIGURATION COMPLETE  ")
logger.info("'HOME' path is: " + BGFHome)

dc = 60                  ## setting the first dutyCycle value here gets the fan spinning no matter what.

logger.info('dc initial value set to: ' + str(dc) + '.')
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
# GPIO 23 set up as input. It is pulled up to stop false signals
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.OUT)  # Set GPIO pin 18 to output mode.
fanPwm = GPIO.PWM(18, 100)   # Initialize PWM on fanPwm @ specified frequency in hz
fanPwm.start(dc)

elapse = 0
# pElapse = 0
lastDc = dc
def main():
    global elapse,lastDc

#   Grab CPU temp and set fan accordingly
    if argsBGF.temperature:
        cpuRtn = str(dTemp)
    else:
        ct = os.popen('vcgencmd measure_temp').readline()
        cpuRtn = ct.replace("temp=","").replace("'C\n","")
    temp1=float(cpuRtn)
    if temp1 < 30.0:
        dc=0
    if temp1 >= 30 and temp1 <= 40:
        dc=10
    if temp1 > 40 and temp1 <= 50:
        dc=20
    if temp1 > 50 and temp1 <= 60:
        dc=30
    if temp1 > 60 and temp1 <= 62:
        dc=40
    if temp1 > 62 and temp1 <= 65:
        dc=50
    if temp1 > 65 and temp1 <= 67:
        dc=70
    if temp1 > 67 and temp1 <= 68:
        dc=90
    if temp1 > 68:
        dc=100
    fanPwm.ChangeDutyCycle(dc)
#   Setup to do some sort of output stuff
#    rpm = int((pulses / elapse) * 60)
    dataSet = fanSpd()
    pulses = dataSet[0]
    elapse = dataSet[1]
    rpm = dataSet[3]
    logger.debug('Raw CPU: ' + ct.replace("\n","") + '. CPU: ' + cpuRtn +  '. Fan RPM: ' + str(rpm) + '. dc reset to ' + str(dc))
    if lastDc != dc and not argsBGF.debug:
        logger.info('CPU tempC: ' + cpuRtn +  '. Fan RPM: ' + str(rpm) + '. dc reset to ' + str(dc))
        pickle.dump(rpm, open(BGFHome + '/fanSpd.pkl', 'wb+'), pickle.HIGHEST_PROTOCOL)
    lastDc = dc
#    pElapse = dataSet[1]
    return rpm



def fanSpd():
    global pulse,elapse,start
    GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    start = time.time()
    elapse = 0
    pulse = 0

#    while pulse < 600:
    while time.time() - start < 4:
        GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        fpRtn = GPIO.wait_for_edge(23, GPIO.RISING, timeout=50)
        if fpRtn is not None:
            pulse += 1
            tnow = time.time()
            elapse = tnow - start
        if fpRtn is None:
            pulse = 0
            tnow = time.time()
            elapse = tnow - start
    else:
        tnow = time.time()
        elapse = tnow - start
        if pulse == 0:
            rpm = 0
        else:
            rpm = int((pulse / elapse) * 60)
            pass
    return pulse,elapse,start,rpm


def SignalHandler(signal, frame):
        global pill2kill
        logger.info("SignalHandler invoked. dc=" + str(dc))
        logger.info(" - - - - - - - - - - - - - - - - - - - - - ")
        logger.info("Cleaning up")
        GPIO.cleanup()
        logger.debug("Finished GPIO.cleanup() in SignalHandler")
        logger.info("Shutting down gracefully")
        logger.debug("Wrote to log in SignalHandler")
        logger.info("Finished SignalHandler")
        logger.info("That's all folks.  Goodbye")
        print("Exiting.")
        sys.exit(0)

if __name__ == "__main__":
        import traceback
        try:
            signal.signal(signal.SIGINT, SignalHandler)  ## This one catches CTRL-C from the local keyboard
            signal.signal(signal.SIGTERM, SignalHandler) ## This one catches the Terminate signal from the system
            logger.info(" Top of try")
            while True:
                main()
            pass

            logger.info("Bottom of try")
            logger.flush()
        except Exception:
            error = traceback.print_exc()
            logger.debug(error)
            logger.info("That's all folks.  Goodbye")
            pass
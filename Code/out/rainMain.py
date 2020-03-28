#!/usr/bin/env python3
""" rainMain.py - Get rain rate from Sparkfun SEN-08942 Weather Meters' rain gauge.
    2019 - Gregory Allen Sanders."""

import time,math,os,csv
from time import sleep
import RPi.GPIO as GPIO

rPin = 12
rpulse = 0
rstart = time.time()
relapse = 0            # this is r-elapse, although it looks like someone fell off the wagon (relapse, get it?).
rainHome = os.path.abspath(os.path.dirname(__file__))

GPIO.setmode(GPIO.BCM)
GPIO.setup(rPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setwarnings(False)
#
# 0.011" of rain causes one bucket-tip (1 pulse)
#
def main():
    GPIO.remove_event_detect(12)
    global rpulse,relapse,rstart
    rstart = time.time()
    relapse = 0
    rpulse = 0
    #print("rPulse is intiated.")
    while rpulse == 0:
        GPIO.add_event_detect(12,GPIO.FALLING)
        cycle = 0
        while cycle < 2:
            sleep(2)
            if GPIO.event_detected(12):
                rpulse += 1
                relapse = time.time() - rstart
                cycle = relapse
            else:
                rpulse = 0
                cycle = time.time() - rstart
                pass
        GPIO.remove_event_detect(12)
#        print('Cycled. pulse= {0:} cycle= {1:}'.format(rpulse,cycle))

    return rpulse,relapse,rstart
''' the plan here is . . . evolving
    '''


if __name__ == "__main__":

    while True:
        main()
        if rpulse > 0:
            print('rainMain Pulse: {0:} Elapse : {1:}'.format(rpulse,relapse))
        
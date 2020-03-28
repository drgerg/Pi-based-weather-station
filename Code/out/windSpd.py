#!/usr/bin/env python3
""" windSpd.py - Get wind speed from Sparkfun SEN-08942 Weather Meters' anemometer.
    2019,2020 - Gregory Allen Sanders."""

import time,math
from time import sleep
import RPi.GPIO as GPIO

wsPin = 16
pulse = 0
start = time.time()
elapse = 0
rps = 0
kph = 0
mph = 0


GPIO.setmode(GPIO.BCM)
GPIO.setup(wsPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setwarnings(False)

''' The following code is what you get when you are sorta floundering around
    with no real idea of how you want to go about doing a thing.
    So you try something, then you go off and do something else, and come back
    and tweak what you did here just to make something work elsewhere.  What needs
    to happen here is a 'clearing of the baffles' or 'flushing of the buffers'.  
    I'll get to it in due course. '''

def main():
    pulse,elapse,start = wsPulse()
#    print('At Main: ' +str(pulse) + ' ' + str(elapse))
    return pulse,elapse

def wsPulse():
    global pulse,elapse,start
    start = time.time()
    elapse = 0
    pulse = 0
    #print("wsPulse is intiated.")
    while elapse < 3:                ## Changed value from 6 to 3 ##
        pRtn = GPIO.wait_for_edge(16, GPIO.FALLING,timeout=1000)
        if pRtn != None:
            pulse += 1
#        print(str(start) + ' ' + str(pulse) + ' ' + str(elapse))
        elapse = time.time() - start
#        print(str(elapse))
    return pulse,elapse,start



# 1 Hz (rev/sec) = 1.492 mph = 2.40114125 kph = 2401.1 m/h


if __name__ == "__main__":
#    initPins()
#    initInterrupt()
    while True:
        pulse,elapse,start = wsPulse()
#        print('ws3 Pulse: {0:} Elapse : {1:}'.format(pulse,elapse))
#        sleep(0.1)
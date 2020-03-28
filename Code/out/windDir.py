#!/usr/bin/env python3
""" windDir.py - Get wind direction from Sparkfun SEN-08942 Weather Meters' vane.
    Reads voltage variance by means of a ADS1115 16-bit ADC.
    2019 - Gregory Allen Sanders."""

def main():
    #    wspdret = wspd()
    import time
    import Adafruit_ADS1x15
    import RPi.GPIO as GPIO

    adc = Adafruit_ADS1x15.ADS1115()

    interval = 2   # Time between loops (seconds)

    # Set GPIO pins to use BCM pin numbers
    GPIO.setmode(GPIO.BCM)

    time.sleep(interval)

    # Calculate wind direction based on ADC reading
    #   Read ADC channel 0 with a gain of 2/3
    #val = adc.read_adc(0, gain=2/3)
    val = adc.read_adc(0, gain=1)
    windDir = "Not Connected" # In case wind sensor not connected
    windDeg = 0

#    if 19600 <= val <= 20999:
    if 19000 <= val <= 20999:
        windDir = "N"
        windDeg = 0

    if 10000 <= val <= 10800:
        windDir = "NNE"
        windDeg = 22.5

    if 11000 <= val <= 12400:
        windDir = "NE"
        windDeg = 45

    if 2000 <= val <= 2299:
        windDir = "ENE"
        windDeg = 67.5

    if 2300 <= val <= 2999:
        windDir = "E"
        windDeg = 90

    if 1000 <= val <= 1999:
        windDir = "ESE"
        windDeg = 112.5

    if 4000 <= val <= 4999:
        windDir = "SE"
        windDeg = 135

    if 3000 <= val <= 3999:
        windDir = "SSE"
        windDeg = 157.5

    if 6600 <= val <= 8999:
        windDir = "S"
        windDeg = 180

    if 5000 <= val <= 6599:
        windDir = "SSW"
        windDeg = 202.5

    if 15900 <= val <= 16800:
        windDir = "SW"
        windDeg = 225

    if 15000 <= val <= 15800:
        windDir = "WSW"
        windDeg = 247.5

    if 23000 <= val <= 25000:
        windDir = "W"
        windDeg = 270

    if 21000 <= val <= 22000:
        windDir = "WNW"
        windDeg = 292.5

    if 22001 <= val <= 22999:
        windDir = "NW"
        windDeg = 315

    if 18000 <= val <= 18900:
        windDir = "NNW"
        windDeg = 337.5

    # Print results
#    print('Dir ADC val: ' + str(val))
#    print('Wind Dir   : '+ windDir)
#    print('Wind Degree: ' + str(windDeg))
#    print(' ')
    return windDir,windDeg

if __name__ == "__main__":
    import traceback
    try:
    #    main()
        while True:  # the 'while' loop will keep printing over and over
            main()   # if you want a continuous reading
        pass

    except Exception:
        error = traceback.print_exc()
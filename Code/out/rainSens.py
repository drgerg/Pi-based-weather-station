#!/usr/bin/env python3
""" rainSens.py - Get rainfall data from Sparkfun SEN-08942 Weather Meters' sensor.
    .
    2019 - Gregory Allen Sanders."""



def main():
    wspdret = wspd()
        # Print results
    print 'Temperature: ', temperature, 'C'
    print 'Humidity:    ', humidity, '%'
    print 'Case Temp:   ', case_temp, 'C'
    print 'Pressure:    ', pressure, 'kPa'
    print 'Dir ADC val: ', val
    print 'Wind Dir:    ', windDir
    print 'Wind Speed:  ', windSpeed, 'km/h'
    print 'Rainfall:    ', rainFall, 'mm'
    print ' '
    

    def wspd():
        import time,Adafruit_ADS1x15,
import RPi.GPIO as GPIO

interval = 2   # Time between loops (seconds)
windTick = 0   # Count of the wind speed input trigger
rainTick = 0   # Count of the rain input trigger

# Set GPIO pins to use BCM pin numbers
GPIO.setmode(GPIO.BCM)

# Set digital pin 17 to an input and enable the pullup (wind speed)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set digital pin 23 to an input and enable the pullup (rain)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Event to detect wind (4 ticks per revolution)
GPIO.add_event_detect(17, GPIO.BOTH)
def windtrig(self):
    global windTick
    windTick += 1
GPIO.add_event_callback(17, windtrig)

# Event to detect rain (0.2794mm per tick)
GPIO.add_event_detect(23, GPIO.FALLING)
def raintrig(self):
    global rainTick
    rainTick += 1
GPIO.add_event_callback(23, raintrig)
    time.sleep(interval)

    # Calculate the average wind speed over 
    #   this 'interval' in km/h
    windSpeed = (windTick * 1.2) / interval
    windTick = 0

    #Calculate the rainfall over this 'interval' in mm
    rainFall = rainTick * 0.2794
    rainTick = 0
    

if __name__ == "__main__":
    import traceback
    try:
        main()
    #    while True:  # the 'while' loop will keep printing over and over
    #        main()   # if you want a continuous reading
    #    pass

    except Exception:
        error = traceback.print_exc()
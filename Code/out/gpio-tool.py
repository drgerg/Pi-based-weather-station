#!/usr/bin/env python3
import RPi.GPIO as gpio
#gpio.setmode(gpio.BOARD)
gpio.setmode(gpio.BCM)

ver = gpio.VERSION
mode = gpio.getmode()
if mode == 11:
    mode = 'BCM'
if mode == 10:
    mode = 'BOARD'
if mode == None:
    mode = 'not set'
board_info = gpio.RPI_INFO



print('RPi.GPIO Version: ' + ver)
print('GPIO mode: ' + str(mode))
print('Raspberry Pi information:')
print('Type: ' + board_info['TYPE'])
print('Revision: ' + board_info['REVISION'])
print('Processor: ' + board_info['PROCESSOR'])
print('Memory: ' + board_info['RAM'])

#    BCM = 11
#    BOARD = 10
#    BOTH = 33
#    FALLING = 32
#    HARD_PWM = 43
#    HIGH = 1
#    I2C = 42
#    IN = 1
#    LOW = 0
#    OUT = 0
#    PUD_DOWN = 21
#    PUD_OFF = 20
#    PUD_UP = 22
#    RISING = 31
#    RPI_INFO = {'MANUFACTURER': 'Sony', 'P1_REVISION': 3, 'PROCESSOR': 'BC...
#    RPI_REVISION = 3
#    SERIAL = 40
#    SPI = 41
#    UNKNOWN = -1


for i in range(27):
    pinFunc = gpio.gpio_function(i)
    print('Pin ' + str(i) + ' function: ' + str(pinFunc))
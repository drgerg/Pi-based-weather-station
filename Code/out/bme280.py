#!/usr/bin/python
# coding: latin-1
#
## Greg Sanders' modified version Feb. 2020.
##  Used by outMainDATA.py
#
#--------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#           bme280.py
#  Read data from a digital pressure sensor.
#
#  Official datasheet available from :
#  https://www.bosch-sensortec.com/bst/products/all_products/bme280
#
# Author : Matt Hawkins
# Date   : 21/01/2018
#
# https://www.raspberrypi-spy.co.uk/
#
#--------------------------------------
import smbus
import time
from ctypes import c_short
from ctypes import c_byte
from ctypes import c_ubyte

DEVICE = 0x76 # Default device I2C address


bus = smbus.SMBus(1) # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1
                     # Rev 1 Pi uses bus 0

def getShort(data, index):
  # return two bytes from data as a signed 16-bit value
  return c_short((data[index+1] << 8) + data[index]).value

def getUShort(data, index):
  # return two bytes from data as an unsigned 16-bit value
  return (data[index+1] << 8) + data[index]

def getChar(data,index):
  # return one byte from data as a signed char
  result = data[index]
  if result > 127:
    result -= 256
  return result

def getUChar(data,index):
  # return one byte from data as an unsigned char
  result =  data[index] & 0xFF
  return result

def readBME280ID(addr=DEVICE):
  # Chip ID Register Address
  REG_ID     = 0xD0
  (chip_id, chip_version) = bus.read_i2c_block_data(addr, REG_ID, 2)
  return (chip_id, chip_version)

def readBME280All(addr=DEVICE):
  # Register Addresses
  REG_DATA = 0xF7
  REG_CONTROL = 0xF4
  REG_CONFIG  = 0xF5

  REG_CONTROL_HUM = 0xF2
  REG_HUM_MSB = 0xFD
  REG_HUM_LSB = 0xFE

  # Oversample setting - page 27
  OVERSAMPLE_TEMP = 2
  OVERSAMPLE_PRES = 4
  MODE = 1

  # Oversample setting for humidity register - page 26
  OVERSAMPLE_HUM = 2
  bus.write_byte_data(addr, REG_CONTROL_HUM, OVERSAMPLE_HUM)

  control = OVERSAMPLE_TEMP<<5 | OVERSAMPLE_PRES<<2 | MODE
  bus.write_byte_data(addr, REG_CONTROL, control)

  # Read blocks of calibration data from EEPROM
  # See Page 22 data sheet
  cal1 = bus.read_i2c_block_data(addr, 0x88, 24)
  cal2 = bus.read_i2c_block_data(addr, 0xA1, 1)
#  print("cal2:")
#  print(cal2)
  cal3 = bus.read_i2c_block_data(addr, 0xE1, 7)
#  print("cal3:")
#  print(cal3)

  # Convert byte data to word values
  dig_T1 = getUShort(cal1, 0)
  dig_T2 = getShort(cal1, 2)
  dig_T3 = getShort(cal1, 4)

  dig_P1 = getUShort(cal1, 6)
  dig_P2 = getShort(cal1, 8)
  dig_P3 = getShort(cal1, 10)
  dig_P4 = getShort(cal1, 12)
  dig_P5 = getShort(cal1, 14)
  dig_P6 = getShort(cal1, 16)
  dig_P7 = getShort(cal1, 18)
  dig_P8 = getShort(cal1, 20)
  dig_P9 = getShort(cal1, 22)

  dig_H1 = getUChar(cal2, 0)
  dig_H2 = getShort(cal3, 0)
  dig_H3 = getUChar(cal3, 2)

  dig_H4 = getChar(cal3, 3)
  dig_H4 = (dig_H4 << 24) >> 20
  dig_H4 = dig_H4 | (getChar(cal3, 4) & 0x0F)

  dig_H5 = getChar(cal3, 5)
  dig_H5 = (dig_H5 << 24) >> 20
  dig_H5 = dig_H5 | (getUChar(cal3, 4) >> 4 & 0x0F)

  dig_H6 = getChar(cal3, 6)

  # Wait in ms (Datasheet Appendix B: Measurement time and current calculation)
  wait_time = 1.25 + (2.3 * OVERSAMPLE_TEMP) + ((2.3 * OVERSAMPLE_PRES) + 0.575) + ((2.3 * OVERSAMPLE_HUM)+0.575)
  time.sleep(wait_time/1000)  # Wait the required time

  # Read temperature/pressure/humidity
  data = bus.read_i2c_block_data(addr, REG_DATA, 8)
  pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
  temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
  hum_raw = (data[6] << 8) | data[7]
  #
  ## trying a compensation value here.  My humidity readings are consistently low
  # hum_raw = hum_raw + 3880.0  ## the comp value may be ill-advised.
  #

  #Refine temperature
  var1 = ((((temp_raw>>3)-(dig_T1<<1)))*(dig_T2)) >> 11
  var2 = (((((temp_raw>>4) - (dig_T1)) * ((temp_raw>>4) - (dig_T1))) >> 12) * (dig_T3)) >> 14
  t_fine = var1+var2
  temperature = float(((t_fine * 5) - 60000) >> 8)
  # temperature = float(((t_fine * 5) -  32768) >> 8)  ## another adjustment to the defaults.
  # print("  t_fine @ line 142: " + str(t_fine))
  # print("           t_fine*5: " + str(t_fine*5))
  # gimme = 60000
  # print("              gimme: " + str(gimme))
  # tfshift8 = float(((t_fine*5) - gimme) >> 8)
  # print("           tfshift8: " + str(tfshift8))
  # print("   temperature @144: " + str(temperature))

  # Refine pressure and adjust for temperature
  var1 = t_fine / 2.0 - 64000.0
#  var1 = t_fine / 2.0 - 65536.0       ##  a mod I tried
  var2 = var1 * var1 * dig_P6 / 32768.0
  var2 = var2 + var1 * dig_P5 * 2.0
  var2 = var2 / 4.0 + dig_P4 * 65536.0
  var1 = (dig_P3 * var1 * var1 / 524288.0 + dig_P2 * var1) / 524288.0
  var1 = (1.0 + var1 / 32768.0) * dig_P1
  if var1 == 0:
    pressure=0
  else:
    pressure = 1048576.0 - pres_raw
    pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
    var1 = dig_P9 * pressure * pressure / 2147483648.0
    var2 = pressure * dig_P8 / 32768.0
    pressure = pressure + (var1 + var2 + dig_P7) / 16.0
    pressure = pressure + 240                 ##  compensation factor for Milton, FL - Greg Sanders

#   # Refine humidity
#   #  humidity = t_fine - 76800.0   # original setting
#   #
# #  print(str("  t_fine @ line 155: " + str(t_fine)))
#   humidity = t_fine - 76800.0                 ## DEFAULT VALUE
#   # print('     First humidity: ' + str(humidity))
#   humidity = (hum_raw - (dig_H4 * 64.0 + dig_H5 / 16384.0 * humidity)) * (dig_H2 / 65536.0 * (1.0 + dig_H6 / 67108864.0 * humidity * (1.0 + dig_H3 / 67108864.0 * humidity)))
#   # print("    Second Humidity: " + str(humidity))
# #  humidity = humidity * (1.0 - dig_H1 * humidity / 524288.0)  # DEFAULT VALUE. SMALLER NUMBERS CAUSE THE READING TO GO DOWN
# #  humidity = humidity * (0.5 - dig_H1 * humidity / 262144.0)  # 88% reference from local PWS's.  result: 88.12%
#   # H1Cal = 0.46                               ## another manual calibration attempt.
#   H1Cal = 1                                  ## the above attempt was bust.  Don't do that again.
#   hcp2Var = 30100                           ## 524288 is the divisor from the original.
#   # print('              H1Cal: ' + str(H1Cal))
#   # print('   hcp2Var (524288): ' + str(hcp2Var))
#   # print('     default dig_H1: ' + str(dig_H1))
#   H1CalThum = dig_H1 * humidity               ## multiplication step.
#   # print('  dig_H1 * humidity: ' + str(H1CalThum))
#   humCalP2 = H1CalThum / hcp2Var              ## division step.
#   # print('    humidity/' + str(hcp2Var) + ': ' + str(humCalP2))
#   humidity = humidity * (H1Cal - humCalP2)
# #  humidity = humidity * (1.0 - dig_H1 * humidity / hcp2Var)  # 88% reference from local PWS's.  result: 93.75%
# #  humidity = humidity * (1.0 - dig_H1 * humidity / 32000.0) # 88% reference from local PWS's.  result: 106.6%
# #  humidity = humidity * (1.0 - dig_H1 * humidity / 30000.0) # 88% reference from local PWS's.  result: 99.13%
# #  humidity = humidity * (1.0 - dig_H1 * humidity / 29500.0) # 88% reference from local PWS's.  result: 97.11%
# #  humidity = humidity * (1.0 - dig_H1 * humidity / 28000.0)  # result: max reading of 93%
#   # print(' Third humidity: ' + str(humidity))
#   preHum = humidity
#   # print("          Humidity2: " + str(humidity))
#   if humidity > 100:
#     humidity = 100
#   elif humidity < 0:
#     humidity = 0

  # return temperature/100.0,pressure/100.0,humidity,preHum
  return temperature/100.0,pressure/100.0

def main():

  (chip_id, chip_version) = readBME280ID()
#  print("       Chip ID     : " + str(chip_id))
#  print("       Version     : " + str(chip_version))

  # temperature,pressure,humidity,preHum = readBME280All()
  temperature,pressure = readBME280All()
  tempF = float((temperature * 1.8) + 32.00)
  print('      Temperature C: {:.2f}°'.format(temperature)) 
  print('      Temperature F: {:.2f}°'.format(tempF)) 
  print('          Pressure : {:.2f}hPa'.format(pressure))
  print('          Pressure : {:.2f}inHg'.format(pressure * 0.0295300))
  # print('          PreHum   : {:.2f}%'.format(preHum))
  # print('          Humidity : {:.2f}%'.format(humidity))

if __name__=="__main__":
   main()

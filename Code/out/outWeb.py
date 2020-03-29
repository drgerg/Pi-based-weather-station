#!/usr/bin/env python3
# out.py - (What's it like out?) Check the outdoor weather sensors with a browser.
#    Copyright (c) 2019 - Gregory Allen Sanders
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


#import RPi.GPIO as GPIO
import os,logging,pickle,re,time,datetime,requests,subprocess,configparser,signal,threading
from outMain import allSensors
#from collections import OrderedDict
from flask import Flask, render_template, request, flash, url_for
from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, BooleanField, StringField, IntegerField, SubmitField, validators
from wtforms.validators import Length, DataRequired, NumberRange
#from graph import build_graph

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d341f27d241f27567d241f4b6176a'
#app.config['SECRET_KEY'] = 'thesKywastheblUeoFAwArmeasTereGg@730intHeafterNOON'
#print(app)
#print(__name__)
#
## Get the HOME environment variable
#
outHome = os.path.abspath(os.path.dirname(__file__))
#
## ConfigParser init area.  Get some info out of 'out.conf'.
#
config = configparser.RawConfigParser()
config.read(outHome + '/out.conf')
#
## End ConfigParser init
#
#
##
####  PINS INITIAL SETUP
#
#GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(True)
#
'''
####  I'M SAVING THIS FOR LATER REFERENCE
# Grab list of pins and status from .pkl file. Set Output pins as an output and make them high (high = off):
#for pin in Spins:
#   GPIO.setup(pin, GPIO.OUT)
#   GPIO.output(pin, Spins[pin]['state'])
#
'''

## BEYOND HERE LIE THE OUTPUT GENERATION SECTIONS
#
## THESE BLOCKS THAT START WITH A '@app.route()' LINE ARE CALLED 'VIEWS'
## THIS BLOCK OF CODE DETERMINES WHAT HAPPENS WHEN A BROWSER REQUESTS A CERTAIN URL
## THIS ONE IS FOR THE ROOT, WHAT WE USED TO THINK OF AS 'INDEX.HTML'
#
@app.template_filter()  # A template filter allows us to bring data back from the .html files for further
def dec2(value):        # processing before is is displayed.  In this case, change it to a float w/ 2 decimal places.
    value = float(value)
    return "{:.2f}".format(value)

@app.route('/')
def main():
#    global kph,mph
    #Pin = config.get('Pins','PinA')
    #temperature,pressure,humidity = bme280.readBME280All()
    tempC,tempF,pres,pressNA,humid,preHum,kph,mph,wd,rainF,cpuT = allSensors()
    fanSpd = pickle.load(open(outHome + '/fanSpd.pkl', 'rb'))
    # Put it into the template data dictionary:
    templateData = {
      'bmpTempC' : tempC,
      'bmpTempF' : tempF,
      'bmpPressRaw' : pres,
      'bmpPressNA' : pressNA,  # NA stands for North America, fyi.
      'bmpHumid' : humid,
      'bmpPreHum' : preHum,
      'windDir' : wd[0],
      'windDeg' : wd[1],
      'wsK' : kph,
      'wsM' : mph,
      'rf' : rainF,
      'cpuTemp' : cpuT,
      'fanSpd' : fanSpd,
      'capTime' : '{0:%H:%M:%S - %A, %b %d, %Y}'.format(datetime.datetime.now())
      }
    # 
    # Pass the template data into the template main.html and return it to the user
    return render_template('main.html', **templateData)
#
#   pickle.dump(Spins, open(outHome + '/CurrentState.pkl', 'wb'), pickle.HIGHEST_PROTOCOL)
    # Save the current schedule to our .pkl file.


if __name__ == "__main__":
    app.run(host='0.0.0.0')
    #app.run(host='0.0.0.0', port=5010, debug=True)
    #app.run(host='0.0.0.0', port=5010)

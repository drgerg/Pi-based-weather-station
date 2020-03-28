#!/usr/bin/env python3
# out.py - (What's it like out?) Check the outdoor weather sensors.
#    2019,20 - Gregory Allen Sanders
# This code is VERY alpha, but it works.  Don't expect much, and for god's sake, don't 
# lose any money by using any of this!
# 
# 
# 
import RPi.GPIO as GPIO
import os,logging,pickle,re,time,datetime,requests,subprocess,configparser,signal,threading,bme280,windDir
from flask import Flask, render_template, request, flash, url_for
from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, BooleanField, StringField, IntegerField, SubmitField, validators
from wtforms.validators import Length, DataRequired, NumberRange

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d341f27d241f27567d241f4b6176a'
print(app)
print(__name__)
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
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(True)
#

## THESE BLOCKS THAT START WITH A '@app.route()' LINE ARE CALLED 'VIEWS'
## THIS BLOCK OF CODE DETERMINES WHAT HAPPENS WHEN A BROWSER REQUESTS A CERTAIN URL
## THIS ONE IS FOR THE ROOT, WHAT WE USED TO THINK OF AS 'INDEX.HTML'
#
@app.template_filter()  # A template filter allows us to send data back from the .html files for further
def dec2(value):        # processing before is is displayed.  In this case, change it to a float w/ 2 decimal places.
    value = float(value)
    return "{:.2f}".format(value)

@app.route('/')
def main():
    #
    temperature,pressure,humidity = bme280.readBME280All()
    TempF = float(9/5 * temperature + 32.00)           # in degrees Farenheit
    PressNA = 0.0295300 * pressure               # in inHg
    wd = windDir.main()
    # Put it into the template data dictionary:
    templateData = {
      'bmpTempC' : temperature,
      'bmpTempF' : TempF,
      'bmpPressRaw' : pressure,
      'bmpPressNA' : PressNA,  # NA stands for North America, fyi.
      'bmpHumid' : humidity,
      'windDir' : wd[0],
      'windDeg' : wd[1],
      'capTime' : '{0:%H:%M:%S - %A, %b %d, %Y}'.format(datetime.datetime.now())
      }
    # 
    # Pass the template data into the template main.html and return it to the user
    return render_template('main.html', **templateData)
#

if __name__ == "__main__":
    app.run(host='0.0.0.0')
    #app.run(host='0.0.0.0', port=5010, debug=True)
    #app.run(host='0.0.0.0', port=5010)

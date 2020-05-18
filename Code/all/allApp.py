#!/usr/bin/env python3
#
#allApp.py
#
#Cobbled together by Greg Sanders 2020 to be the central point for everything.
#   
#     Copyright (c) 2019,2020 - Gregory Allen Sanders.

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import os, pickle, re, time, datetime, requests, subprocess, configparser, signal, socket, random, allGetSQL
from time import sleep
from collections import OrderedDict
from flask import Flask, render_template, request, flash, url_for
from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, BooleanField, StringField, IntegerField, SubmitField, validators
from wtforms.validators import Length, DataRequired, NumberRange
from user_agents import parse

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'nowhereISanothers3cre7keyforyaharry'
#
## Get the HOME environment variable
#
allAppHome = os.path.abspath(os.path.dirname(__file__))

#
## ConfigParser init area.  Get some info out of 'allApp.conf'.
#
config = configparser.RawConfigParser()
config.read(allAppHome + '/allApp.conf')
#
## End ConfigParser init
#
##
####  INITIALIZE OR LOAD STATUS PICKLE FILE
##
# Check for a 'CurrentState.pkl' file.  If one exists, load it.
if os.path.isfile(allAppHome + '/CurrentStatus.pkl'):
   loadStatus = pickle.load(open(allAppHome + '/CurrentStatus.pkl', 'rb'))
# Otherwise:   
# Create a dictionary called loadStatus to store the index number, name, and state:
else:
   loadStatus = {
       1 : {'sort' : '1', 'name' : 'all', 'state' : 'off'},
       2 : {'sort' : '2', 'name' : 'undefined', 'state' : 'undefined'},
       3 : {'sort' : '3', 'name' : 'undefined', 'state' : 'undefined'},
       4 : {'sort' : '4', 'name' : 'undefined', 'state' : 'undefined'},
       5 : {'sort' : '5', 'name' : 'undefined', 'state' : 'undefined'},
       6 : {'sort' : '6', 'name' : 'undefined', 'state' : 'undefined'}
       
       }
   loadStatus = OrderedDict(sorted(loadStatus.items(), key=lambda kv: kv[1]['sort']))
 # Save the current status to a .pkl file.
   pickle.dump(loadStatus, open(allAppHome + '/CurrentStatus.pkl', 'wb+'), pickle.HIGHEST_PROTOCOL)
#
## THESE BLOCKS THAT START WITH A '@app.route()' LINE ARE CALLED 'VIEWS'
## THIS BLOCK OF CODE DETERMINES WHAT HAPPENS WHEN A BROWSER REQUESTS A CERTAIN URL
## THIS ONE IS FOR THE ROOT, WHAT WE USED TO THINK OF AS 'INDEX.HTML'
#
@app.route('/')
def main():
   # Retrieve previous state settings from the .pkl file made by 
   loadStatus = pickle.load(open(allAppHome + '/CurrentStatus.pkl', 'rb'))
   recStat = str(loadStatus[1]['state']) # Was recording left on when main.html was last seen?
   outData = allGetSQL.dataGrab()        # Grab the bulk of the current data
   inchRain = allGetSQL.inchRainGrab()
   shopTemp,shopHumidity,shopCPU = allGetSQL.shopDataGrab()
   recTime = outData[0]
   outTemp = outData[2]
   wsM = outData[5]
   windDir = outData[7]
   outHumidity = outData[4]
   rainRate = outData[15]
   wetDry = outData[14]
   poolTempIn,poolTempOut = allGetSQL.poolDataGrab(0)
   # Put our variables into the template data dictionary:
   templateData = {
       'recTime' : recTime,
       'outTemp' : outTemp,
       'outHumidity' : outHumidity,
       'wsM' : wsM,
       'windDir' : windDir,
       'inchRain' : inchRain,
       'poolTempIn' : poolTempIn,
       'poolTempOut' : poolTempOut,
       'shopTemp' : shopTemp,
       'shopHumidity' : shopHumidity,
       'shopCPU' : shopCPU,
       'rainRate' : rainRate,
       'wetDry' : wetDry,
       'recStat' : recStat
      }
   # 
   # Pass the template data into the template main.html and show it to the user
   return render_template('main.html', **templateData)
#
## 
#
@app.route('/mon1/')
def mon1():
    zmURL = config.get('ZMCams','zm_URL')
    c1m = str(config.get('ZMCams','Cam1Monitor'))
    conKey = random.randint(111111,999999)
    ua_string = request.headers.get('User-Agent')
    user_agent = parse(ua_string)
    if user_agent.is_mobile:
        url1 = "http://" + zmURL + "/cgi-bin/nph-zms?scale=25&mode=jpeg&maxfps=10&monitor=" + c1m + "&connkey=" + str(conKey)
    else:
        url1 = "http://" + zmURL + "/cgi-bin/nph-zms?scale=44&mode=jpeg&maxfps=10&monitor=" + c1m + "&connkey=" + str(conKey)

    templateData = {
        'url1' : url1
        }
   # 
   # Pass the template data into the template mon1.html and return it to the user
    return render_template('mon1.html', **templateData)
#
@app.route('/mon2/')
def mon2():
    zmURL = config.get('ZMCams','zm_URL')
    c2m = str(config.get('ZMCams','Cam2Monitor'))
    conKey = random.randint(111111,999999)
    ua_string = request.headers.get('User-Agent')
    user_agent = parse(ua_string)
    if user_agent.is_mobile:
        url2 = "http://" + zmURL + "/cgi-bin/nph-zms?scale=25&mode=jpeg&maxfps=10&monitor=" + c2m + "&connkey=" + str(conKey)
    else:
        url2 = "http://" + zmURL + "/cgi-bin/nph-zms?scale=44&mode=jpeg&maxfps=10&monitor=" + c2m + "&connkey=" + str(conKey)
    templateData = {
        'url2' : url2
        }
   # 
   # Pass the template data into the template mon2.html and return it to the user
    return render_template('mon2.html', **templateData)
#
@app.route('/mon3/')
def mon3():
    zmURL = config.get('ZMCams','zm_URL')
    c3m = str(config.get('ZMCams','Cam3Monitor'))
    conKey = random.randint(111111,999999)
    ua_string = request.headers.get('User-Agent')
    user_agent = parse(ua_string)
    if user_agent.is_mobile:
        url3 = "http://" + zmURL + "/cgi-bin/nph-zms?scale=25&mode=jpeg&maxfps=10&monitor=" + c3m + "&connkey=" + str(conKey)
    else:
        url3 = "http://" + zmURL + "/cgi-bin/nph-zms?scale=44&mode=jpeg&maxfps=10&monitor=" + c3m + "&connkey=" + str(conKey)
    templateData = {
        'url3' : url3
        }
   # 
   # Pass the template data into the template mon3.html and return it to the user
    return render_template('mon3.html', **templateData)
#
@app.route('/mon4/')
def mon4():
    zmURL = config.get('ZMCams','zm_URL')
    c4m = str(config.get('ZMCams','Cam4Monitor'))
    conKey = random.randint(111111,999999)
    ua_string = request.headers.get('User-Agent')
    user_agent = parse(ua_string)
    if user_agent.is_mobile:
        url4 = "http://" + zmURL + "/cgi-bin/nph-zms?scale=25&mode=jpeg&maxfps=10&monitor=" + c4m + "&connkey=" + str(conKey)
    else:
        url4 = "http://" + zmURL + "/cgi-bin/nph-zms?scale=44&mode=jpeg&maxfps=10&monitor=" + c4m + "&connkey=" + str(conKey)
    templateData = {
        'url4' : url4
        }
   # 
   # Pass the template data into the template mon4.html and return it to the user
    return render_template('mon4.html', **templateData)
#
@app.route('/mon5/')
def mon5():
    zmURL = config.get('ZMCams','zm_URL')
    c5m = str(config.get('ZMCams','Cam5Monitor'))
    conKey = random.randint(111111,999999)
    ua_string = request.headers.get('User-Agent')
    user_agent = parse(ua_string)
    if user_agent.is_mobile:
        url5 = "http://" + zmURL + "/cgi-bin/nph-zms?scale=75&mode=jpeg&maxfps=15&monitor=" + c5m + "&connkey=" + str(conKey)
    else:
        url5 = "http://" + zmURL + "/cgi-bin/nph-zms?scale=100&mode=jpeg&maxfps=15&monitor=" + c5m + "&connkey=" + str(conKey)
    templateData = {
        'url5' : url5
        }
   # 
   # Pass the template data into the template mon5.html and return it to the user
    return render_template('mon5.html', **templateData)
#
@app.route('/monQuad/')
def monQuad():
    zmURL = config.get('ZMCams','zm_URL')
    c1m = str(config.get('ZMCams','Cam1Monitor'))
    c2m = str(config.get('ZMCams','Cam2Monitor'))
    c3m = str(config.get('ZMCams','Cam3Monitor'))
    c4m = str(config.get('ZMCams','Cam4Monitor'))
    conKey = random.randint(111111,999999)
    ua_string = request.headers.get('User-Agent')
    user_agent = parse(ua_string)
    if user_agent.is_mobile:
        url1 = "http://" + zmURL + "/cgi-bin/nph-zms?scale=14&mode=jpeg&maxfps=5&monitor=" + c1m + "&connkey=" + str(conKey)
        url2 = "http://" + zmURL + "/cgi-bin/nph-zms?scale=14&mode=jpeg&maxfps=5&monitor=" + c2m + "&connkey=" + str(conKey+1)
        url3 = "http://" + zmURL + "/cgi-bin/nph-zms?scale=14&mode=jpeg&maxfps=5&monitor=" + c3m + "&connkey=" + str(conKey+2)
        url4 = "http://" + zmURL + "/cgi-bin/nph-zms?scale=14&mode=jpeg&maxfps=5&monitor=" + c4m + "&connkey=" + str(conKey+3)
    else:
        url1 = "http://" + zmURL + "/cgi-bin/nph-zms?scale=25&mode=jpeg&maxfps=5&monitor=" + c1m + "&connkey=" + str(conKey)
        url2 = "http://" + zmURL + "/cgi-bin/nph-zms?scale=25&mode=jpeg&maxfps=5&monitor=" + c2m + "&connkey=" + str(conKey+1)
        url3 = "http://" + zmURL + "/cgi-bin/nph-zms?scale=25&mode=jpeg&maxfps=5&monitor=" + c3m + "&connkey=" + str(conKey+2)
        url4 = "http://" + zmURL + "/cgi-bin/nph-zms?scale=44&mode=jpeg&maxfps=5&monitor=" + c4m + "&connkey=" + str(conKey+3)
    templateData = {
        'url1' : url1,
        'url2' : url2,
        'url3' : url3,
        'url4' : url4
        }
   # 
   # Pass the template data into the template monQuad.html and return it to the user
    return render_template('monQuad.html', **templateData)

# 
## REBOOT WEATHERPI - sends a command URL to another computer to trigger a relay that powercycles the weather Pi.
#
@app.route('/RBWP/') ## 'RBWP' = Re-Boot Weather Pi
def rbwp():
    return render_template('RBWP.html')
#
@app.route('/RBWPResp/<response>/')
def rbwpresp(response):
    if response == 'YES':
        message = requests.get("http://192.168.1.11/reset")
        if "200" in (str(message)):
            message = "Remote Reset of WeatherPi was triggered."
    else:
        message = "Canceled"
        pass
    templateData = {
        'message' : message

    }
   # 
   # Pass the template data into the template RBWPResp.html and return it to the user
    return render_template('RBWPResp.html', **templateData)
#
## TURN ON RECORDING FOR ALL CAMERAS
#
@app.route('/<recCtrl>/<action>/')
def action(recCtrl, action):
    # LOAD CURRENT STATUS FROM THE .PKL FILE
#    loadStatus = pickle.load(open(allAppHome + '/CurrentStatus.pkl', 'rb'))
#    recStat = str(loadStatus[1]['state']) # 
    if recCtrl == 'all' and action == 'on':
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('192.168.1.22', 6802))
        sock.send(b'6|on|25|Manual_Start|allApp|allApp \n7|on|25|Manual_Start|allApp|allApp \n8|on|25|Manual_Start|allApp|allApp \n9|on|25|Manual_Start|allApp|allApp \n10|on|25|Manual_Start|allApp|allApp')
        recStat = "on"
    if recCtrl == 'all' and action == 'off':
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('192.168.1.22', 6802))
        sock.send(b'6|cancel|||| \n7|cancel|||| \n8|cancel|||| \n9|cancel|||| \n10|cancel||||')
        recStat = "off"
    loadStatus[1]['state'] = recStat
    templateData = {
        'recStat' : recStat
        }
    # Save the current status of all pins to a .pkl file.
    pickle.dump(loadStatus, open(allAppHome + '/CurrentStatus.pkl', 'wb+'), pickle.HIGHEST_PROTOCOL)
    # 
    # Pass the template data into the template main.html and return it to the user
    return render_template('main.html', **templateData)
#
##  GET CURRENT WEATHER DATA FROM THE OUTRAW TABLE AND LET FLASK SERVE IT UP
#
@app.template_filter()  # A template filter allows us to bring data back from the .html files for further
def dec2(value):        # processing before is is displayed.  In this case, change it to a float w/ 2 decimal places.
    value = float(value)
    return "{:.2f}".format(value)

@app.route('/outStats/')
def outstats():
    recTime,pressure,outTemp,outTempC,outHumidity,windSpeed,winddir,wdirStr,extraHumid1,cpuTemp,recNum,fan1,rawRecTime,rain,wetDry,rainRate = allGetSQL.dataGrab()
    inchRain = allGetSQL.inchRainGrab()
    #fanSpd = pickle.load(open(outHome + '/fanSpd.pkl', 'rb'))
    pressNA = 0.0295300 * pressure
    # Put it into the template data dictionary:
    templateData = {
      'bmpTempC' : outTempC,
      'bmpTempF' : outTemp,
      'bmpPressRaw' : pressure,
      'bmpPressNA' : pressNA,  # NA stands for North America, fyi.
      'bmpHumid' : outHumidity,
      'bmpPreHum' : extraHumid1,
      'windDir' : wdirStr,
      'windDeg' : winddir,
      'wsM' : windSpeed,
      'inchRain' : inchRain,
      'rainRate' : rainRate,
      'wetDry' : wetDry,
      'cpuTemp' : cpuTemp,
#      'fanSpd' : fanSpd,
      'recNum' : recNum,
      'fan1' : fan1,
      'capTime' : recTime
      }
    # 
    # Pass the template data into the template outStats.html and return it to the user
    return render_template('outStats.html', **templateData)
#
## This is a catch-all function to get whatever sort of stats you want from whatever various computers
## you want stats from.  We're starting with output of z-sysRunTest.py which checks the running status 
## of the .service files in /lib/systemd/system/ .
#
@app.route('/stats/')
def stats():
    HOST = '192.168.1.12'                                           # We're using Unix sockets to get this data.
    PORT = 64444                                                    # Choose a weird port way high in the ports range.
    statusResp = []                                                 # Initialize an empty list
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:    # Setup a stream IP socket. I think this uses TCP
        s.connect((HOST, PORT))                                     # Connect to the remote machine.
        data = s.recv(1024)                                         # Create a receptacle for initial connection info.
        reply = data.decode('utf-8')                                # It comes in as bytes type.  Make it UTF-8 so we can play.
        if 'Welcome' in reply:                                      # A simple test to make sure I'm in the right place.
            sleep(1)                                                # Hold up a sec.
            s.sendall(b'sysStat')                                   # Send the command to start the data-gathering on the other end.
            llen = s.recv(2)                                        # I want to know how many items are in the list of .service files.
            listLen = llen.decode('utf-8').strip('\n')              # It comes in as bytes type.  Make it UTF-8 and strip line feeds.
            howMany = int(listLen)                                  # Turn the string into an integer
            sleep(1)                                                # Hold up a sec.
            replyStat = s.recv(1024)                                # Create another receptacle for the actual data.
            statResp = replyStat.decode('utf-8')                    # yeah, once again.  Bytes to utf-8.
            statusResp = statResp.split(':')                        # I know my incoming data is delineated with colons. Use that.
            statusResp.remove('')                                   # I know there will be an empty list item.  Get rid of it.
            s.sendall(b'quit')                                      # Tell the remote machine I'm finished.
            sleep(1)                                                # Hold up a sec.
            lastReply = s.recv(1024)                                # Create a receptacle for the response to our 'quit'.
            lastReply = lastReply.decode('utf-8')                   # Bytes to utf-8.
            if 'quit' in lastReply:                                 # Test for proper last response.
                pass                                                # It's all good, so wrap things up.
        else:                                                       # A 'just in case' check . . . not sure if it's needed.
            s.sendall(b'quit')                                      # last-ditch effort to quit smoothly. May be a waste.
    templateData = {                                                # Create the templateData dictionary.
      'listLen' : listLen,                                          # Add our 'how many items are there' entry
      'statResp' : statusResp                                       # Add our raw data from the remote machine.
      }
    return render_template('stats.html', **templateData)            # Return all this goodness and render stats.html using it.
    



if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5050, debug=True)


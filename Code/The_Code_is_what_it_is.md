# No more apologies for my code.  I think it's fine.

This file is here out of respect for any degreed SysAdmin who has ventured here and is curious.

This code was all written by a self-taught geek.  It works and does exactly what I wanted it to do.  So, in that respect, it's perfect.

The WeatherPi is talking to the mySQL machine, which in turn is talking to [www.pwsweather.com](https://www.pwsweather.com/station/pws/kflmilto35).  It's pretty cool to see the data there.

There are two folders in the Code repo folder: the **all** folder and the **out** folder.  The **out** folder contains code for the WeatherPi (RRRRPWS).  The **all** folder contains code that runs on a Linux box inside the house.  That computer runs mySQL, and the Python/Flask/Gunicorn/nginx browser interface for the whole shooting match.

There is the question of all the prerequisites for getting all this running, and that requires a bit of writing and editing I haven't done yet.  However, nearly all of those prerequisites are covered in the Pool Controls project. [link](https://github.com/casspop/PoolControls/blob/master/Docs/2020%20Rebuild%20Process%20Documentation.md)  I'm using the same sort of Python, Flask, Gunicorn, nginx setup for this project that I used for that one.

03-28-2020 - In spite of the fact that my code is still VERY trashy, it is working as I intended, and for that reason I'm going ahead and putting it up here.  
05/13/2020 - Things are getting a bit less trashy.  It's a slow process.  I have a day job.
05/17/2020 - Actually, now I'm feeling pretty good about this.  The weather station is chugging along happily.  I've added some long-awaited touches to my interface, which makes me feel good.
11/28/2020 - OK.  I've finally gotten to the point where I think what I've done is worthy.  No more apologies.  It works. It works consistently and correctly.  
07/11/2021 - WeatherPi has been running flawlessly now for many months.  I did upgrade it yesterday with a DHT22 Temp/Humidity sensor, and gave it a annual physical checkup while it was down.  I found no problems.  Sweet!

## Necessary files from the 'out' directory (WEATHER STATION CODE)

### These are the basis of the system

- bme280.py - module that gets data from the temperature, humidity, pressure sensor.
- outMainDATA.py - this is the core of the data gathering system. It is run by outMainDATA.service at boot.
- rainMainDATA.py - this handles the rainfall measuring and logging. It is run by rainMainDATA.service at boot.
- outBgFan.py - this handles the variable speed system ventilation fan. It is run by outBgFan.service at boot.
- camStream.py - this sets up and serves the PiCamera's stream. It is run by outCam.service at boot.
- wPiBoot.py - this monitors wifi connectivity and reboots the Pi cleanly if needed. It is run by rainMainDATA.service at boot.
- out.conf - contains configuration options, mostly having to do with the mySQL database on the remote server.
- windDir.py - just like the name says, gets the wind direction. Loaded as a module in outMainDATA.py.
- windSpd.py - counts pulses and calculates the wind speed. Loaded as a module in outMainDATA.py.

## Accessory utility files

- gpio-tool.py - provides a little useful info about the Pi it's running on.
- z-sysRunTest.py - quickly shows you an OK or NOT OK status of the *.system files.

## Inside the _lib_systemd_system_ folder

These files live in /lib/systemd/system and are owned by root:root .  Just copying them there is not enough.  You need to edit them to
get your own system's data in them first, Then there are proper steps you need to follow to use them.
[Learn More](https://www.raspberrypi.org/documentation/linux/usage/systemd.md)(THIS LINK IS BROKEN. I NEED TO FIND OR MAKE A NEW ONE.)

- outBgFan.service - starts the vent fan on boot.
- outCam.service - starts the eye-on-the-sky cam on boot.
- outMainDATA.service - starts the main routines on boot.
- outWPBoot.service - starts the connnectivity monitor on boot.
- rainMainDATA.service - starts collecting rainfall data on boot.
- outSocket.service - runs a socket to allow for simple local diagnosics.

## Information on files in the 'all' directory (HTTP USER INTERFACE SYSTEM CODE)

[Output as seen in browser.](https://github.com/casspop/Pi-based-weather-station/blob/master/Pics/mother_main_screen.png)

In a desktop browser or on my phone, this is the screen I go to first when I want to interact with my pool controls, my security cameras, or the RRRRPWS (WeatherPi).

Here are the files that live on the little Intel i3 Lenovo in my office.  I did this to take as much processing pressure off of the Raspberry Pi as possible.  I want all of its resources to be focused on gathering data from the sensors, collating it and delivering it to this little guy.  He can take it from there.

- allApp.conf - configuration options live here.
- allGetNoaa.py - runs as a service (allGetNoaa.service)
- allApp.py - the Flask front-end file, this is the central hub.
- allGetSQL.py - the name says it all.  This program pulls data from the mySQL database and feeds it to allApp.py for you.
- allPWSWeather.py - this one sets up the regular reports to PWSWeather.com.
- z-sysRunTest.py - a utility that checks the status of the two system services we run on this machine.

##  The .service files: 

These files are in the _lib_systemd_system_ folder as a reference.  You will need to recreate them in the <code>/lib/systemd/system/</code> folder on your "all" computer.

- allApp.service - This is the main backbone of the user-interface system for the Pi-Net.
- allGetNoaa.service - this gets a fresh weather forecast from NOAA National Weather Service every 4 hours.
- allPWS.service - this sends our weather station report to PWSweather.com every minute.
- allSysReport.service - this runs zAllSysChk.py every 10 minutes to keep track of the overall health of the Pi-Net.

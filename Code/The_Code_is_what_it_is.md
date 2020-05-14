# Today's Code is Rudimentary - understand that.

This file is here out of respect for anyone who has ventured here and is actually interested.

This code is really rough.  But it works and does exactly what I wanted it to do.  So, in that respect, it's perfect. 

The Pi is talking to the mySQL machine, which in turn is talking to www.pwsweather.com.  It's pretty cool to see the data there.

There's also the question of all the prerequisites for getting all this running, and that will require a bit of time writing and editing.  Nearly all of them are covered in the Pool Controls project.  I'm using the same sort of Python, Flask, Gunicorn, nginx setup for this project that I used for that one.

Getting the hardware put together is not a trivial process, so the code I have is quite rudimentary (almost embarrassingly so).

03-28-2020 - In spite of the fact that my code is still VERY trashy, it is working as I intended, and for that reason I'm going ahead and putting it up here.  
05/13/2020 - Things are getting a bit less trashy.  It's a slow process.  I have a day job.

# Necessary files from the 'out' directory.  
## These are the basis of the system:

- bme280.py - module that gets data from the temperature, humidity, pressure sensor.
- outMainDATA.py - this is the core of the data gathering system. It is run by outMainDATA.service at boot.
- rainMainDATA.py - this handles the rainfall measuring and logging. It is run by rainMainDATA.service at boot.
- outBgFan.py - this handles the variable speed system ventilation fan. It is run by outBgFan.service at boot.
- camStream.py - this sets up and serves the PiCamera's stream. It is run by outCam.service at boot.
- wPiBoot.py - this monitors wifi connectivity and reboots the Pi cleanly if needed. It is run by rainMainDATA.service at boot.
- out.conf - contains configuration options, mostly having to do with the mySQL database on the remote server.
- windDir.py - just like the name says, gets the wind direction. Loaded as a module in outMainDATA.py.
- windSpd.py - counts pulses and calculates the wind speed. Loaded as a module in outMainDATA.py.

# Accessory utility files

- gpio-tool.py - provides a little useful info about the Pi it's running on.
- z-sysRunTest.py - quickly shows you an OK or NOT OK status of the *.system files.

# Inside the _lib_systemd_system_ folder:

These files live in /lib/systemd/system and are owned by root:root .  Just copying them there is not enough.  You need to edit them to
get your own system's data in them first, Then there are proper steps you need to follow to use them.
[Learn More](https://www.raspberrypi.org/documentation/linux/usage/systemd.md)

- outBgFan.service - starts the vent fan on boot.
- outCam.service - starts the eye-on-the-sky cam on boot.
- outMainDATA.service - starts the main routines on boot.
- outWPBoot.service - starts the connnectivity monitor on boot.
- rainMainDATA.service - starts collecting rainfall data on boot.

# The Quest for a Reliable, Robust, Repairable Raspberry Pi-based Weather Station
Project Initialized October 2019
Project opened to public on Github February 2020

### A bit of History

After throwing away my second Acurite weather station in only two years I decided I would build my own.  It may be cheaper to buy a more expensive commercial brand like Davis, but honestly, I'm sick of the throw-away culture when I can do something about it.

The goal of this project is to take advantage of the availability of the modular Pi and Arduino sensors and boards to create a weather station that I could repair when something died.  The Pi lives on the pole with the sensors, and communicates over WiFi.

The project is being written in Python 3. Flask, Gunicorn and nginx are used to display info to users. Everything stays here, this is not ever going to be on the web, although I do intend to eventually upload data to a PWS site like [this one](https://beta.pwsweather.com/). 

I am making every attempt to provide enough documentation and schematics for anyone else to duplicate what I've done.

I am a self-taught rank amateur coder, as anyone with experience can plainly see.  What I know is what I've done so far works here, and provides me with reliable and accurate data as compared to all the local commercial and government data sources.  

I use Visual Studio Code in Windows.  I use Microsoft's Remote-SSH extensions to work with my code on the weather station Pi out on the pole in the backyard.
I use Filezilla to keep local copies of that code when I'm done editing and testing.

The system runs on a Pi 4 Model B.  Rather than re-invent the wheel on environmental sensors, I bought [Sparkfun's SEN-08942 Weather Meters](https://www.sparkfun.com/products/8942). I have a [DROK buck-converter](./Pics/DROK Buck Converter mount.jpg) DC-to-DC power board, a real-time clock module, a analog-to-digital module, and a BME280 temperature, pressure, humidity sensor module all living in the box on the pole.  A Pi Camera v2 provides a 640x480 view of the outdoor conditions.  I incorporated the solar cell powered fan from one of the dead Acurite stations.  There are other ways to accomplish the job it does, but I had it, and I used it.

The station is powered from a remotely located 120V to 12VDC power supply which was designed for use with controlled access electric door locks.  It has a built-in gel-cell charger and a time-adjustable relay.  That gives me the benefit of a battery backup, and the ability to power-cycle the Pi easily.  

I ran 3/4" conduit underground to house 14AWG Romex for the 12VDC.  I installed lightning arrestors on both ends of that 12VDC line tied to a solid ground.  I had some personal experience with nearby lightning strikes inducing a damaging spike on buried CAT5 recently, and so I've taken measures to avoid a repeat of that embarrassment.

I own a Prusa MK3S 3D printer which I use to make mounts and other custom parts for assembling the whole thing.  Unlike many people who seem to think you can't use Sketchup for modeling for printing, I do it all the time with no problem.  The .skp and .stl files are here for you to use as you see fit.



[RRRRPWS on the pole.](./Pics/RRRRPWS-on-the-pole.jpg)




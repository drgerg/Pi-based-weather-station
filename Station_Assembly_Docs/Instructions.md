# Instructions (as they become available)

Turn off power save mode on the Pi's built-in Wifi radio.  You can see the status of this mode with:

`sudo iw wlan0 get power_save`

Turn it off with:

`sudo iw wlan0 set power_save off`

I'll post something here about making that permanent in the future.

UPDATE: It's been two years, and I still haven't posted anything here about making that setting permanent.  But I thought about it.

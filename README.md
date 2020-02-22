# The Quest for a Reliable, Robust, Reproducable Raspberry Pi-based Weather Station
Project Initialized October 2019

### A bit of History

After throwing away my second Acurite weather station in only two years I decided I would build my own.

The goal of this project is to take advantage of the availability of the modular Pi and Arduino sensors and boards to create a weather station that I could repair when something died.

The project is being written in Python 3.  I am making every attempt to provide enough documentation and schematics for anyone else to duplicate what I've done.

I am a self-taught rank amateur coder, as anyone with experience can plainly see.  What I know is what I've done so far works here, and provides me with reliable and accurate data as compared to all the local commercial and government data sources.  

I use Visual Studio Code in Windows.  I use Microsoft's Remote-SSH extensions to work with my code on the weather station Pi out on the pole in the backyard.
I use Filezilla to keep local copies of that code when I'm done editing and testing.

The system runs on a Pi 4 Model B.  I have a real-time clock module, a analog-to-digital module, and a BME280 temperature, pressure, humidity sensor module.

I incorporated the solar cell powered fan from one of the dead Acurite stations.  There are other ways to accomplish the job it does, but I had it, and I used it.



![The front page of controls on my phone.](./Pics/Screenshot_20191031-171240_DuckDuckGo.jpg)


The front page of controls on my phone.

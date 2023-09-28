# rpi-eclipse
This is a collection of scripts to automate camera exposures via a USB connected camera on a raspberry pi. It's built around the idea of "I want to take a picture at a precise time with precise settings." A lot of existing astrophotography software exists to do this sort of thing, but aren't raspberry pi friendly.

As of September 2023 I'm doing some rewriting for the pending annular eclipse. It's slightly less messy but not done yet. Due to difficulties of running Solar Eclipse Maestro on modern hardware, I've switched to using Eclipse Orchestrator. Parsing the scripts is kind of weird so instead I'm relying on the output of EO's "View Exposure Sequence.." menu option. It prints out all exposure events with nice timestamps.

The software relies on python's APScheduler module to allow restarting the script if something goes wrong. All events are scheduled with a timestamp, which means if the script is re-executed it won't try to repeat exposures that happened in the past.

It controls the camera shutter using the raspberry's GPIO pins. At least with Canon cameras, there is a quirk with taking pictures over USB where you can only take one exposure at a time and are unable to send any more commands until the buffer is cleared. My testing indicated that on average it takes 2 seconds to configure a picture, take it, and save it to SD over USB. With a serial shutter you can make use of the camera's full buffer and the time for a single exposure drops to fractions of a second. So I dug around online for how to craft a trigger cable for my cameras with the raspberry pi and it's proven fairly reliable.

## Other Software

For eclipse specific planning, I can't reccomend Solar Eclipse Maestro enough. It only runs under OSX but is by far the most comprehensive planning tool I've found so far. It can tell you everything you need to know.. it'll give you the precise time of every event of the eclipse, has a simulator for visualizing baily's beads and also has a tool for planning exposure settings for every phase of the eclipse.

http://xjubier.free.fr/en/site_pages/solar_eclipses/Solar_Eclipse_Maestro_Photography_Software.html

(the software is donationware)

If you can't run the software, some of the tools are available as a web version on the author's website.

## Required Dependencies

### Non-Python:

- libgphoto2 

### Python Modules:

- APScheduler
- RPi.GPIO
- gphoto2

## Optional Dependencies

### Python Modules:
- matplotlib
- pandas
- numpy

## Cheatsheet

### Install Packages

```apt install gphoto2 python3-gphoto2 python3-apscheduler python3-matplotlib python3-pandas python3-numpy```

### Confirm Camera Connectivity

```
gphoto2 --summary
```


The optional dependencies are used only to build a gantt plot of the exposure sequence. I found it useful for visualizing gaps in my exposure sequence.

## Included Scripts, with a brief explanation of each

- **CameraSettings.py** - class that uses gphoto2 to pull a list of capabilities from a usb attached camera and provides the results to eclipse.py

- **EOseq.py** -- class that parases the output of Eclipse Orchestrator's "View Exposure Sequence.." menu option into data that APScheduler can parse into jobs.

- **performancetest.py** - This script can be used to verify you can take pictures on the camera. It is also useful for timing how long it takes the camera to perform various tasks (configure exposure, take a picture, take several pictures, etc) which is data you'll need when scripting exposures. Take note of the configure_custom function, as these values are camera model specific. The options specified in there right now are used to configure bracket ordering and the number of AEB exposures for my 80d.

- **gantt.py** - Makes an ugly matplotlib gantt plot of all events during totality. This is a decent visuzaliztion of how busy the camera will be and to spot gaps and overlaps in the sequences where you might need to adjust timing.

- **eclipse.py** - The script that will actually be run during the eclipse. It reads in the CSV file that was produced with scheduler.py, schedules those events with APScheduler, and tries to take pictures when told to.

- **shutter_circuit.png** - png of the small circuit I used to hook the raspberry pi to the shutter release port on my cameras.

- **ATTIC/** - old scripts that will eventually get deleted when I'm done testing the new flow

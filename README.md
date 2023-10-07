# rpi-eclipse
This is a collection of scripts to automate camera exposures via a USB connected camera on a raspberry pi. It's built around the idea of "I want to take a picture at a precise time with precise settings." A lot of existing astrophotography software exists to do this sort of thing, but aren't raspberry pi friendly.

It controls the camera shutter using the raspberry's GPIO pins. At least with Canon cameras, there is a quirk with taking pictures over USB where you can only take one exposure at a time and are unable to send any more commands until the buffer is cleared. My testing indicated that on average it takes 2 seconds to configure a picture, take it, and save it to SD over USB. With a serial shutter you can make use of the camera's full buffer and the time for a single exposure drops to fractions of a second. So after some internet digging I came up with a cable I can run from the remote trigger port to the rpi's GPIO pins.

## Other Software

For eclipse specific planning, Solar Eclipse Maestro is the way to go. Unfortunately it's OSX only and doesn't run on modern hardware. Fortunately there are sufficient tools on the author's website to get the info you need. Head here:

http://xjubier.free.fr/en/site_pages/SolarEclipseCalc_Diagram.html

And input your location and select an event. Note the timestamps and altitude and stash that all in a text file. 

Also visit here to pick exposure settings for your sequence:

http://xjubier.free.fr/en/site_pages/SolarEclipseExposure.html

## Required Dependencies

### Non-Python:

- libgphoto2 

### Python Modules:

- RPi.GPIO
- gphoto2

## Cheatsheet

### Install Packages

```apt install gphoto2 python3-gphoto2 python3-setuptools```

### Confirm Camera Connectivity

```
gphoto2 --summary
```


## Included Scripts, with a brief explanation of each

- **CameraSettings.py** - class that uses gphoto2 to pull a list of capabilities from a usb attached camera and provides the results to eclipse.py

- **EOseq.py** -- class that parases the output of Eclipse Orchestrator's "View Exposure Sequence.." menu option into data that APScheduler can parse into jobs. Not using this anymore but it's still in the repo.

- **SEseq.py** -- class that parses my own exposure sequence script. Look at scripts/oct14.se for an example. Of note is the 'Repeat' and 'Interval' columns, this allows setting up a string of many photos with the same settings until the next event. 

- **tools/performancetest.py** - Use this script to determine how fast your camera can take photos. The defaults are a config cycle time of 0 seconds and an explosure/buffer clear time of 1 seconds. The script will increment the config time by a tenth of a second on each loop if it sees I/O errors on the camera. The shutter delay time must be manually set. After each run, re-run the script with --config-delay set to the generated value and decrement --shutter-delay  by a tenth of a second until the camera is unable to keep up (you get fewer images on the SD card than the script attempted to capture). The values produced by this script can be used to inform eclipse.py or Eclipse Orchestrator how fast your camera can take images.

- **tools/bursttest.py** - Confirms whether or not putting the camera into high speed continuous mode works okay. 

- **eclipse.py** - The script that will actually be run during the eclipse. It reads in the CSV file that was produced with scheduler.py, schedules those events with APScheduler, and tries to take pictures when told to.

- **99-camera.rules** - udev config to detect when the camera is plugged in via USB. Used to start the systemd service that runs through the photo sequence.

- **rpi-eclipse.service** - systemd unit to run the photo sequence. Note you will need to edit this unit to point to your exposure sequence config. 

- **install.sh** - installs the udev rules, the systemd unit, the python classes, and eclipse.py

- **uninstall.sh** - the opposite of install. Note it doesn't delete the python module. 

- **shutter_circuit.png** - png of the small circuit I used to hook the raspberry pi to the shutter release port on my cameras.

- **ATTIC/** - old scripts that will eventually get deleted when I'm done testing the new flow

# rpi-eclipse
This is a collection of scripts to automate camera exposures via a USB connected camera on a raspberry pi. It's built around the idea of "I want to take a picture at a precise time with precise settings." A lot of existing astrophotography software exists to do this sort of thing, but aren't raspberry pi friendly.

At this stage the implementation is quite a mess and needs too much manual fiddling, but it works with my equipment. Long term I'll probably fix that but that because I can think of many other interesting uses for scripted camera exposures, but will be well after the August 21 eclipse.  Currently the scripts are only known to work with a Canon 80D and 500D (T1i), the bodies I happen to own. Theoretically they can be made to work with any camera that libgphoto2 supports, but it depends on the configurable options that the camera's PTP interface provides and one's willingness to hack my python code. 

The software relies on python's APScheduler module to allow restarting the script if something goes wrong. All events are scheduled with a timestamp, which means if the script is re-executed it won't try to repeat exposures that happened in the past.

It controls the camera shutter using the raspberry's GPIO pins. At least with Canon cameras, there is a quirk with taking pictures over USB where you can only take one exposure at a time and are unable to send any more commands until the buffer is cleared. My testing indicated that on average it takes 2 seconds to configure a picture, take it, and save it to SD over USB. With a serial shutter you can make use of the camera's full buffer and the time for a single exposure drops to fractions of a second. So I dug around online for how to craft a trigger cable for my cameras with the raspberry pi and it's proven fairly reliable.

## Other Software

For eclipse specific planning, I can't reccomend Solar Eclipse Maestro enough. It only runs under OSX but is by far the most comprehensive planning tool I've found so far. It can tell you everything you need to know.. it'll give you the precise time of every event of the eclipse, has a simulator for visualizing baily's beads and also has a tool for planning exposure settings for every phase of the eclipse.

http://xjubier.free.fr/en/site_pages/solar_eclipses/Solar_Eclipse_Maestro_Photography_Software.html

(the software is donationware)

If you can't run the software, some of the tools are available as a web version on the author's website.

## Required Dependencies

### Non-Python:

- libgphoto2 (with most distributions installing gphoto2 will bring in this library, and you'll want the gphoto2 command line tool to confirm communication with your camera anyway)

### Python Modules:

- APScheduler
- RPi.GPIO
- gphoto2

## Optional Dependencies

### Python Modules:
- matplotlib
- pandas
- numpy

The optional dependencies are used only to build a gantt plot of the exposure sequence. I found it useful for visualizing gaps in my exposure sequence.

## Included Scripts, with a brief explanation of each

- **getoptions.py** - The first script to be used, this one uses gphoto2 to probe the attached camera for a number of configurable options and scrapes all valid settings for those options (such as aperture, shutterspeed, etc). It pretty prints the results into an importable python class that every other script uses. I'm not proud of this scheme but it works. Redirect stdout into something like optionsMYCAMERA.py and edit all other scripts to import that file.

- **options80d.py** - Sample output of the getoptions.py script. This one was produced by a Canon 80d.

- **performancetest.py** - This script can be used to verify you can take pictures on the camera. It is also useful for timing how long it takes the camera to perform various tasks (configure exposure, take a picture, take several pictures, etc) which is data you'll need when scripting exposures. Take note of the configure_custom function, as these values are camera model specific. The options specified in there right now are used to configure bracket ordering and the number of AEB exposures for my 80d.

- **mtjerferson.py** - Another python class used as a config file. It stores evertying needed to plan out exposures.. latitude, longitude, date, time, eclipse events, camera exposure settings.. you name it. Filling out these events is a manual process, I spent a lot of time tinkering in Solar Eclipse Mestro and reading around online to figure out how to photograph an eclipse. **NOTE:** it is much easier if you base all times off UTC+0. Time zones for astrophotography get annoying fast.

- **scheduler.py** - Parses the mtjefferson.py class and dumps to stdout out a CSV of all exposures to be taken, along with timing and settings. This is the easiest format I could come up with for manually reviewing the results. The script has some logic to be "smart" where it will estimate how long it will take for your camera to finish a task and fit as many pictures into the sequence as possible. If the script detects an overlap of two exposures it will mark this in the first column with triple asteriks.

- **gantt.py** - Makes an ugly matplotlib gantt plot of all events during totality. This is a decent visuzaliztion of how busy the camera will be and to spot gaps and overlaps in the sequences where you might need to adjust timing.

- **eclipsesettings.py** - Base class that gets inherited by the eclipse config class (ie, mtjefferson.py). Provides some convenience methods.

- **eclipse.py** - The script that will actually be run during the eclipse. It reads in the CSV file that was produced with scheduler.py, schedules those events with APScheduler, and tries to take pictures when told to.

- **testrun.sh** - A shell script that sets the system time to the date of the eclipse (uses timedatectl) and fires up eclipse.py to make it easy to test the eclipse script in real time.

- **shutter_circuit.png** - png of the small circuit I used to hook the raspberry pi to the shutter release port on my cameras.

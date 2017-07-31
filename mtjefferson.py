# probably offending the python gods by using a class as a configuration
# file, but it works. 

# this file is built by picking a location on the earth and loading it into
# eclipse maestro:

# http://xjubier.free.fr/en/site_pages/solar_eclipses/Solar_Eclipse_Maestro_Photography_Software.html

# and playing around to figure out when the various events of an eclipse 
# take place. it also has a nice exposure calculator to help configure
# the camera

# also of note are the "config_time", "exposure_time" and "aeb" fields,
# which indicate how fast the camera can complete various tasks. The 
# scheduler script will use these values to sequence exposures

# my method for testing this configuration is to set the system clock to 
# a few seconds before the eclipse starts, then running eclipse.py against
# it

from eclipsesettings import EclipseSettings
from datetime import timedelta

class Eclipse(EclipseSettings):

  lat = 44.706473
  lng = -121.844751
  alt = 1679
  date = '2017/08/21'

  # camera specifics
  config_time = 0.15

  exposure_time = 1.2 # includes flushing to SD
  aeb3 = 2.3
  aeb7 = 4.6

  config_delay = timedelta(seconds=config_time)
  aeb3_delay = timedelta(seconds=aeb3)
  aeb7_delay = timedelta(seconds=aeb7)
  exposure_delay = timedelta(seconds=exposure_time)

  C1 = {
    'start': '16:06:08.8',
    'end': '17:18:39.3',
    'interval': 300,
    'iso': '100',
    'aperture': 16,
    'shutterspeed': '1/1600'
  }

  C2 = {
    'start': '17:18:39.3',
    'end': '17:20:41.2',
  }

  MX = {
    'start': '17:19:40.1',
  }

  Earthshine = {
    'start': '17:19:36.0',
    'end': '17:19:44.0',
    'iso': 6400,
    'aperture': '5.6',
    'shutterspeed': '1/15',
    'aeb' : 3,
    'aebdir': 'over-under',
  }

  CORONA1 = {
    'start': '17:18:59.1',
    'end': '17:19:38.0',
    'aeb': 3,
  }
  CORONA2 = {
    'start': '17:19:44.0',
    'end': '17:20:20.6',
    'aeb': 3,
  }

  SR01 = {
    'iso': 400,
    'aperture': 8,
    'shutterspeed': '1/1250',
    'aeb' : 3,
    'aebdir': 'under-over',
  }
  SR02 = {
    'iso': 1600,
    'aperture': 8,
    'shutterspeed': '1/640',
    'aeb' : 3,
    'aebdir': 'under-over',
  }
  SR05 = {
    'iso': 1600,
    'aperture': 8,
    'shutterspeed': '1/320',
    'aeb': 3,
    'aebdir': 'under-over',
  }
  SR1 = {
    'iso': 1600,
    'aperture': 8,
    'shutterspeed': '1/80',
    'aeb': 3,
    'aebdir': 'under-over',
  }
  SR2 = {
    'iso': 3200,
    'aperture': 8,
    'shutterspeed': '1/80',
    'aeb': 3,
    'aebdir': 'under-over',
  }
  SR3 = {
    'iso': 3200,
    'aperture': 5.6,
    'shutterspeed': '1/80',
    'aeb': 3,
    'aebdir': 'under-over',
  }

  C3 = {
    'start': '17:20:41.2',
    'end': '18:39:49.9',
    'interval': 300,
    'iso': 100,
    'aperture': 16,
    'shutterspeed': '1/1600'
  }
  
  C4 = { 
    'start': '18:39:49.9',
    'end': '19:39:49.9',
    'iso': 100,
    'aperture': 16,
    'shutterspeed': '1/1600'
  }

  BB1 = {
    'start': '17:18:22.1',
    'end': '17:18:40.0',
    'iso': 100,
    'aperture': 16,
    'shutterspeed': '1/1600',
    'aeb': 7,
    'aebdir': 'under-over',
  }

  CH1 = {
    'start': '17:18:40.1',
    'end': '17:18:49.6',
    'iso': 100,
    'aperture': 11,
    'shutterspeed': '1/1600',
    'aeb': 7,
    'aebdir': 'under-over',
  }

  PR1 = {
    'start': '17:18:49.6',
    'end': '17:18:59.1',
    'iso': 100,
    'aperture': 11,
    'shutterspeed': '1/800',
    'aeb': 7,
    'aebdir': 'under-over',
  }

  PR2 = {
    'start': '17:20:20.6',
    'end': '17:20:30.1',
    'iso': 100,
    'aperture': 11,
    'shutterspeed': '1/800',
    'aeb': 7,
    'aebdir': 'over-under',
  }

  CH2 = {
    'start': '17:20:30.1',
    'end': '17:20:39.6',
    'iso': 100,
    'aperture': 11,
    'shutterspeed': '1/1600',
    'aeb': 7,
    'aebdir': 'over-under',
  }

  BB2 = {
    'start': '17:20:39.6',
    'end': '17:21:00.4',
    'iso': 100,
    'aperture': 16,
    'shutterspeed': '1/1600',
    'aeb': 7,
    'aebdir': 'over-under',
  }

if __name__ == "__main__":
  buf = Eclipse()
  buf.dump_event(buf.event_block('PR2',backwards=True))
  buf.dump_event(buf.event_block('CH2',backwards=True))

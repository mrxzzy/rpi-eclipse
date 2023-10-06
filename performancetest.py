#!/usr/bin/python

# this script can be used to test overall functionality.. that is,
# can a picture be taken? 

# it's also useful for benchmarking how quickly the gphoto2 and rpi
# libraries can configure an exposure and fire the shutter

import sys, argparse
import gphoto2 as gp
import RPi.GPIO as GPIO
import time
import random
from datetime import datetime,timedelta
import CameraSettings

def elapsed():
  global event_time
  return "+%fs" % ((datetime.now() - event_time).total_seconds())

def set_base_camera_settings(context,camera,settings):
  config = camera.get_config(context)
  configure_option(config,'capturetarget', settings.capturetarget['Memory card'])
  camera.set_config(config,context)

def configure_option(config,name,value):
  #print("option: %s value: %s" % (name, value))
  buf = config.get_child_by_name(name)
  try:
    setting = buf.get_choice(value)
  except:
    print("failed to get array entry for option %s and value %s" % (name,value))

  try:
    buf.set_value(setting)
  except:
    print("failed to set option %s to value %s" % (name,value))

  buf.set_changed(1)
  return 0

def configpic(context,camera,settings):
  config = camera.get_config(context)

  configure_option(config,'shutterspeed',settings.shutterspeed['1/125'])
  configure_option(config,'aperture',random.choice(list(settings.aperture.values())))
  configure_option(config,'iso',random.choice(list(settings.iso.values())))

  try:
    camera.set_config(config,context)
  except Exception as ex:
    if type(ex) == gp.GPhoto2Error:
      raise Exception('set_config',ex)

def takepic(pin,shutter_hold):
  try:
    GPIO.output(pin, True)
    time.sleep(shutter_hold)
    GPIO.output(pin, False)
    print("%s shutter fired and released" % (elapsed()))
  except Exception as ex:
    raise Exception('shutter_fire', ex)

parser = argparse.ArgumentParser()
parser.add_argument('--config-delay', dest='config_delay', type=float, default=0.1, help='initial delay to use for configuring an exposure')
parser.add_argument('--shutter-hold', dest='shutter_hold', type=float, default=0.11, help='how long to hold the shutter button.')
parser.add_argument('--buffer-clear', dest='buffer_clear', type=float, default=1, help='how long to wait for buffer to clear after taking image')
args = parser.parse_args()

try: 
  context = gp.Context()
  camera = gp.Camera()
  camera.init(context)
  time.sleep(args.config_delay)
  settings = CameraSettings.CameraSettings(camera,context)
except:
  print("Could not init camera.")
  sys.exit(1)

set_base_camera_settings(context,camera,settings)
time.sleep(args.config_delay)

try:
  pin = 12
  GPIO.setmode(GPIO.BOARD)
  GPIO.setwarnings(False)
  GPIO.setup(pin, GPIO.OUT)
except:
  print("initializing GPIO failed")
  sys.exit(1)

attempts = 0
event_time = datetime.now()
while attempts < 10:
  attempts = attempts + 1

  print("\n%s starting attempts #%d" % (elapsed(),attempts))
  try:
    try:
      configpic(context,camera,settings)
      time.sleep(args.config_delay)
    except Exception as ex: 
      if ex.args[0] == 'set_config':
        print("%s set_config failed: %s" % (elapsed(),ex.args[1]))
      else:
        print("unhandled exception in configpic (%s)" % (ex))

      time.sleep(args.config_delay)
      continue

    try:
      print("%s takepic starting" % (elapsed()))
      takepic(pin,args.shutter_hold)
      time.sleep(args.buffer_clear)
    except:
      print("%s exception in takepic" % (elapsed()))
      continue

  except (KeyboardInterrupt, SystemExit):
    print("caught interrupt, cleaning up and exiting")
    GPIO.cleanup()
    camera.exit()
    sys.exit(1)

print("\nAll done. Check camera. If you have %s images then success." % (attempts))

GPIO.cleanup()
camera.exit(context)

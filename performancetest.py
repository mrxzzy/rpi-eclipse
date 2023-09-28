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

def timeck(info):
  global timestamp

  now = datetime.now()

  new = now - timestamp

  print("elapsed time: %s (%s)" % (new,info))
  timestamp = now



def configure_option(config,name,value):
  #print("option: %s value: %s" % (name, value))
  buf = config.get_child_by_name(name)
  setting = buf.get_choice(value)
  buf.set_value(setting)
  buf.set_changed(1)
  return 0

def configure_toggle(config,name,value):
  buf = config.get_child_by_name(name)
  buf.set_value(value)
  buf.set_changed(1)
  return 0

def configure_aeb(config,aeb,drive):
  buf = config.get_child_by_name('aeb')
  setting = buf.get_choice(aeb)
  buf.set_value(setting)
  buf.set_changed(1)

  buf = config.get_child_by_name('drivemode')
  setting = buf.get_choice(drive)
  buf.set_value(setting)
  buf.set_changed(1)
  return 0

def configure_custom(config,order,aebct):
  buf = config.get_child_by_name('customfuncex')

  if order == 'm0p':
    order_option = '105,1,1'
  elif order == 'p0m':
    order_option = '105,1,2'
  else:
    order_option = '105,1,0'

  if aebct == 7:
    aeb_option = '106,2,7,3'
  else:
    aeb_option = '106,2,3,0'

  option_string = "60,1,1,54,6,101,1,0,102,1,0,104,1,0,%s,%s,108,1,0," % (order_option, aeb_option)

  buf.set_value(option_string)
  buf.set_changed(1)

def dump_option(config,name):
  buf = config.get_child_by_name(name)
  print(buf.get_value())


parser = argparse.ArgumentParser()
parser.add_argument('--aeb', action='store_true')
args = parser.parse_args()

aeb_state = args.aeb

try: 
  context = gp.Context()
  camera = gp.Camera()
  camera.init(context)
except:
  print("Could not init camera.")
  sys.exit(1)

settings = CameraSettings.CameraSettings(camera,context)

try:
  #GPIO.setmode(GPIO.BCM)
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(24, GPIO.OUT)
except:
  print("initializing GPIO failed")
  sys.exit(1)

timestamp = datetime.now()
timeck("init:")
config = camera.get_config(context)
timeck("config:")

#configure_toggle(config,'viewfinder',0)
configure_option(config,'capturetarget',settings.capturetarget['Memory card'])

print("aeb_state: %s" % (aeb_state))

configure_option(config,'shutterspeed',settings.shutterspeed['1/100'])
configure_option(config,'aperture',random.choice(list(settings.aperture.values())))
configure_option(config,'iso',random.choice(list(settings.iso.values())))
if aeb_state:
  configure_aeb(config,settings.aeb['+/- 1'],settings.drivemode['Continuous high speed'])

  configure_custom(config,'m0p',3)
  trigger_lag = 0.8

  #configure_custom(config,'m0p',3)
  #trigger_lag = 1.4
else:
  configure_aeb(config,settings.aeb['off'],settings.drivemode['Single'])
  trigger_lag = 0.05

timeck("about to save")
camera.set_config(config,context)
timeck("saved")

timeck("triggering shutter..")
GPIO.setup(12, GPIO.OUT)
GPIO.output(12, True)
time.sleep(trigger_lag)
GPIO.output(12, False)
timeck("..done")

GPIO.cleanup()
camera.exit(context)
timeck("program done")

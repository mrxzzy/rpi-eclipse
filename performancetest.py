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


def configpic(context,settings,aeb_set):
  config = camera.get_config(context)
  configure_option(config,'shutterspeed',settings.shutterspeed['1/125'])
  configure_option(config,'aperture',random.choice(list(settings.aperture.values())))
  configure_option(config,'iso',random.choice(list(settings.iso.values())))
  if aeb_state:
    configure_aeb(config,settings.aeb['+/- 1'],settings.drivemode['Continuous high speed'])
    configure_custom(config,'m0p',3)
  else:
    configure_aeb(config,settings.aeb['off'],settings.drivemode['Single'])

  try:
    camera.set_config(config,context)
  except Exception as ex:
    if type(ex) == gp.GPhoto2Error:
      print("set_config failed: %s" % (ex))
      return False

  return True

def takepic(pin,trigger_delay):
  GPIO.output(pin, True)
  time.sleep(trigger_delay)
  GPIO.output(pin, False)
  print(" ..shutter fired.")

parser = argparse.ArgumentParser()
parser.add_argument('--aeb', action='store_true')
parser.add_argument('--config-delay', dest='config_delay', type=float, help='initial delay to use for configuring an exposure')
parser.add_argument('--shutter-delay', dest='shutter_delay', type=float, help='additional gap to add to shutter to give camera time to flush buffer')
args = parser.parse_args()
aeb_state = args.aeb

if args.config_delay:
	config_delay = args.config_delay
else:
	config_delay = 0.0

if args.shutter_delay:
	shutter_delay = args.shutter_delay
else:
	shutter_delay = 1.0

try: 
  context = gp.Context()
  camera = gp.Camera()
  camera.init(context)
except:
  print("Could not init camera.")
  sys.exit(1)

settings = CameraSettings.CameraSettings(camera,context)

try:
  pin = 12
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(pin, GPIO.OUT)
except:
  print("initializing GPIO failed")
  sys.exit(1)


print("aeb_state: %s" % (aeb_state))
trigger_delay = 0.01 + shutter_delay # 1/100 plus user specified value
images_to_take = 10
success_count = 0
success = False

while not success:
  print("New loop, config_delay is %s" % (config_delay))
  time.sleep(config_delay)
  if not configpic(context,settings,aeb_state):
    config_delay = config_delay + 0.1
  else:
    takepic(pin,trigger_delay)
    success_count = success_count + 1

  if success_count >= images_to_take:
    success = True

print("All done. Check camera. If you have %s images then success. You can set these values for eclipse.py:" % (images_to_take))
print("--config-delay=%s --exposure-delay=%s" % (config_delay, shutter_delay))

GPIO.cleanup()
camera.exit(context)

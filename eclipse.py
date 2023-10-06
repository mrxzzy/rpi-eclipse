#!/usr/bin/python

# this script does the actual shooting of photos. It reads in a csv manifest
# of pictures to take, schedules them, and loops until exit with a ctrl+c

# the use of apscheduler allows the script to be restarted mid-run if needed,
# photos already in the past won't be reattempted.

import os, sys, signal, argparse
import gphoto2 as gp
import RPi.GPIO as GPIO
import time
import csv
import CameraSettings
import EOseq
from datetime import datetime, timedelta

class Camera:
  global debug

  def __init__(self,shutter_hold):
    self.shutter_hold = shutter_hold

    try:
      self.context = gp.Context()
      self.camera = gp.Camera()
      self.camera.init(self.context)
    except:
      print("could not initialize camera")
      sys.exit(1)

    self.settings = CameraSettings.CameraSettings(self.camera,self.context)

    try:
      self.pin = 12
      GPIO.setup(self.pin, GPIO.OUT)
    except:
      print("initializing GPIO failed")
      sys.exit(1)

    self.config = None
    self.old_config = []
    self.trigger_lag = 0.05
    self.init_camera()
    print("Camera init successful!")

  def exit(self):
    self.camera.exit(self.context)

  def get_config(self):
    try:
      self.config = self.camera.get_config(self.context)
    except:
      print("failed to fetch config from the camera")
      sys.exit(1)

  def set_config(self):
    try:
      self.camera.set_config(self.config,self.context)
    except:
      print("setting camera config failed")

  def config_option(self,name,value):
    buf = self.config.get_child_by_name(name)
    setting = buf.get_choice(value)
    buf.set_value(setting)
    buf.set_changed(1)

  def init_camera(self):
    self.get_config()
    self.config_option('capturetarget', self.settings.capturetarget['Memory card'])
    #self.config_option('drivemode', self.settings.drivemode['Super high speed continuous shooting'])
    self.set_config()

  def set_exposure(self,shutterspeed,aperture,iso,aeb,aebdir):
    if [shutterspeed,aperture,iso,aeb,aebdir] == self.old_config:
      print("\t%s Got request to save config but config is not changing, skipping." % (elapsed()))
      return

    self.get_config()

    self.config_option('shutterspeed', self.settings.shutterspeed[shutterspeed])
    buf = aperture.rstrip('.0')
    self.config_option('aperture', self.settings.aperture[buf])
    self.config_option('iso', self.settings.iso[iso])
    if not aeb:
      self.config_aeb(self.settings.aeb['off'], self.settings.drivemode['Single'])
      self.trigger_lag = 0.05
    else:
      self.config_aeb(self.settings.aeb['+/- 1'], self.settings.drivemode['Continuous high speed'])
      self.config_custom(aeb,aebdir)

    self.set_config()
    self.old_config = [shutterspeed,aperture,iso,aeb,aebdir]

  def trigger_shutter(self,aeb=False):

    print("\t%s pressing shutter" % (elapsed()))
    GPIO.output(self.pin, True)

    if aeb is True:
      time.sleep(1.4)
    else:
      print("\t%s pausing for shutter open" % (elapsed()))
      time.sleep(self.shutter_hold)

    GPIO.output(self.pin, False)
    print("\t%s released" % (elapsed()))

  def config_aeb(self,aeb,drive):
    buf = self.config.get_child_by_name('aeb')
    setting = buf.get_choice(aeb)
    buf.set_value(setting)

    buf = self.config.get_child_by_name('drivemode')
    setting = buf.get_choice(drive)
    buf.set_value(setting)

    buf.set_changed(1)

  def config_custom(self,aebct,order):
    # http://gphoto-software.10949.n7.nabble.com/Canon-EOS-custom-functions-td6944.html
    buf = self.config.get_child_by_name('customfuncex')

    if order == 'under-over':
      order_option = '105,1,1'
    elif order == 'over-under':
      order_option = '105,1,2'
    else:
      order_option = '105,1,0'

    if aebct == '7':
      aeb_option = '106,2,7,3'
      self.trigger_lag = 1.4
    else:
      aeb_option = '106,2,3,0'
      self.trigger_lag = 0.8

    option_string = "60,1,1,54,6,101,1,0,102,1,0,104,1,0,%s,%s,108,1,0," % (order_option, aeb_option)

    buf.set_value(option_string)
    buf.set_changed(1)

def ledon():
  GPIO.output(33,GPIO.HIGH)

def ledoff():
  GPIO.output(33,GPIO.LOW)

def elapsed():
  global event_time
  return "+%fs" % ((datetime.now() - event_time).total_seconds())

def set_date(date):
  print("TEST RUN: Setting date to %s" % (date))
  setdate = date - timedelta(seconds=2)
  os.system('timedatectl set-ntp 0')
  os.system("timedatectl set-time '%s'" % (setdate.strftime("%Y-%m-%d %H:%M:%S.%f")))

def unset_date():
  os.system('timedatectl set-ntp 1')

if __name__ == '__main__':
  global debug

  GPIO.setmode(GPIO.BOARD)
  GPIO.setwarnings(False)
  GPIO.setup(33,GPIO.OUT)

  parser = argparse.ArgumentParser()
  parser.add_argument('-d', '--debug', dest='debug', action='store_true')
  parser.add_argument('-s', '--script', required=True, help='Path to file of camera events.')
  parser.add_argument('-r', '--run-now', action='store_true', help='Set system clock to time of first event to test script now.')
  parser.add_argument('-t', '--set-time', help='Set system clock to this value for test runs.')
  parser.add_argument('--config-delay', type=float, default=0.15, help='Float, sets a delay in seconds for setting config on the camera.')
  parser.add_argument('--shutter-hold', type=float, default=0.2, help='Float, how long to hold the shutter button before releasing.')
  parser.add_argument('--buffer-clear', type=float, default=0.4, help='Float, how long to pause after exposure to flush buffer.')
  args = parser.parse_args()

  debug = args.debug

  print("INFO: fastest cycle time with configured delays is %.02f seconds." % (args.config_delay + args.shutter_hold + args.buffer_clear))

  if not os.getuid() == 0 and args.run_now is True:
    print("The -r/--run-now option requires running this script as root so it can set the system time.")
    sys.exit(1)

  if args.run_now and args.set_time:
    print("Cannot set both -r and -t at the same time.")
    sys.exit(1)

  camera_events = EOseq.EOseq(args.script)

  if os.getuid() == 0 and args.run_now is True:
    set_date(camera_events.first)

  if os.getuid() == 0 and args.set_time:
    set_date(datetime.strptime(args.set_time, '%Y/%m/%d %H:%M:%S'))

  cam = Camera(args.shutter_hold)

  try:
    for event in camera_events:
      now = datetime.now()

      if (now - event['start']).total_seconds() > 0.5:
        print("PAST EVENT, rejecting. %s" % (event['start']))
        continue

      # pause until our scheduled moment of exposure
      wait_for_event = (event['start'] - now).total_seconds()
      if wait_for_event > 0:
        time.sleep(wait_for_event)

      ledon()
      event_time = datetime.now()
      print("NEW EVENT scheduled for %s\n\t%s start time (%ss @ %s ISO %s [%s/%s])" % (event['start'],event_time,event['shutterspeed'],event['aperture'],event['iso'],event['aeb'],event['aebdir']))
      cam.set_exposure(event['shutterspeed'],event['aperture'],event['iso'],event['aeb'],event['aebdir'])
      time.sleep(args.config_delay)
      print("\t%s camera configured" % (elapsed()))
      if event['aeb'] is True:
        cam.trigger_shutter(aeb=True)
      else:
        cam.trigger_shutter(args.shutter_hold)
        time.sleep(args.buffer_clear)

      print("\n")
      ledoff()

    print("Sequence complete, cleaning up and exiting.")
    if os.getuid() == 0 and args.run_now is True:
      unset_date()
    GPIO.cleanup()
    cam.exit()

  except (KeyboardInterrupt, SystemExit):
    print("caught interrupt, cleaning up and exiting")
    if os.getuid() == 0 and args.run_now is True:
      unset_date()
    GPIO.cleanup()
    cam.exit()



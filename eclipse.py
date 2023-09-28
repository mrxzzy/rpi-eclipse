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
from apscheduler.schedulers.blocking import BlockingScheduler

class Camera:
  global debug

  def __init__(self):
    try:
      self.context = gp.Context()
      self.camera = gp.Camera()
      self.camera.init(self.context)
    except:
      print("could not initialize camera")
      sys.exit(1)

    self.settings = CameraSettings.CameraSettings(self.camera,self.context)
    print(self.settings.aperture)

    try:
      self.pin = 12
      GPIO.setmode(GPIO.BOARD)
      GPIO.setup(self.pin, GPIO.OUT)
    except:
      print("initializing GPIO failed")
      sys.exit(1)

    self.config = None
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

  def init_camera(self):
    self.get_config()

    # viewfinder 0 is "normal" mode
    # viewfinder 1 shuts off LCD and viewfinder, live view can easily be enabled
    #   by pressing button on camera. NO PICTURES TAKEN when this is set and live
    #   view is off

    # output 0 is "normal" mode
    # output 1 turns on LCD w/liveview

    #self.config_toggle('viewfinder', 0) # 0 is on, 1 is off. is this mirror lockup?
    #self.config_option('output', 1) # 0 = disables live view. 1 = enables live view

    self.config_option('capturetarget', self.settings.capturetarget['Memory card'])

    self.set_config()

  def set_exposure(self,shutterspeed,aperture,iso,aeb,aebdir):
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

  def fire_exposure(self,aeb=False,count=1):

    time.sleep(0.10)

    for pic in range(count):

      sys.stdout.write("pressing shutter.. ")
      sys.stdout.flush()
      GPIO.output(self.pin, True)

      if aeb is True:
        time.sleep(1.4)
      else:
        time.sleep(0.05)

      GPIO.output(self.pin, False)
      print("..released.")
      if count > 1:
        time.sleep(0.25)

  def config_option(self,name,value):
    buf = self.config.get_child_by_name(name)
    setting = buf.get_choice(value)
    buf.set_value(setting)
    buf.set_changed(1)

  def config_toggle(self,name,value):
    buf = self.config.get_child_by_name(name)
    buf.set_value(value)
    buf.set_changed(1)

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

def schedule_alerts(events):
  for event in events:
    cron.add_job(print_alert, 'date', next_run_time=events[event], args=[event])

def print_alert(string):
  print("Event %s happening now!" % (string))

def take_picture(start, duration, iso, aperture, shutterspeed, aeb, aebdir):
  now = datetime.now()

  print("%s: taking picture (%s,%s,%s,%s,%s) (%s seconds estimated)" % (now,shutterspeed,aperture,iso,aeb,aebdir,duration) )
  cam.set_exposure(shutterspeed,aperture,iso,aeb,aebdir)
  if aeb is not None:
    cam.fire_exposure(aeb=True)
  else:
    cam.fire_exposure()

def set_date(date):
  print("TEST RUN: Setting date to %s" % (date))
  setdate = date - timedelta(seconds=2)
  os.system('timedatectl set-ntp 0')
  os.system("timedatectl set-time '%s'" % (setdate.strftime("%Y-%m-%d %H:%M:%S.%f")))

def unset_date():
  os.system('timedatectl set-ntp 1')

if __name__ == '__main__':
  global debug

  parser = argparse.ArgumentParser()
  parser.add_argument('-d', '--debug', dest='debug', action='store_true')
  parser.add_argument('-s', '--script', required=True, help='Path to file of camera events.')
  parser.add_argument('-r', '--run-now', action='store_true', help='Set system clock to time of first event to test script now.')
  args = parser.parse_args()

  debug = args.debug

  if not os.getuid() == 0 and args.run_now is True:
    print("The -r/--run-now option requires running this script as root so it can set the system time.")
    sys.exit(1)

  camera_events = EOseq.EOseq(args.script)

  if os.getuid() == 0 and args.run_now is True:
    set_date(camera_events.first)

  cam = Camera()
  cron = BlockingScheduler()
  #schedule_alerts(eclipse)

  for event in camera_events:
    cron.add_job(take_picture, 'date', next_run_time=event['start'], kwargs=event)

  for job in cron.get_jobs():
    print(job)

  try:
    print("begin at: %s" % (datetime.now()))
    cron.start()
  except (KeyboardInterrupt, SystemExit):
    print("caught interrupt, cleaning up and exiting")
    if os.getuid() == 0 and args.run_now is True:
      unset_date()
    GPIO.cleanup()
    cam.exit()
    sys.exit(0)


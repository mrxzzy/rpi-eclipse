#!/usr/bin/python

import os, sys, signal, argparse
import gphoto2 as gp
import RPi.GPIO as GPIO
import time
import logging
from rpieclipse import CameraSettings
from rpieclipse import SEseq
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
      logging.error("could not initialize camera")
      sys.exit(1)

    self.settings = CameraSettings.CameraSettings(self.camera,self.context)

    try:
      self.pin = 12
      GPIO.setup(self.pin, GPIO.OUT)
    except:
      logging.error("initializing GPIO failed")
      sys.exit(1)

    self.config = None
    self.old_config = []
    self.init_camera()
    logging.info("Camera init successful!")

  def exit(self):
    self.camera.exit(self.context)

  def get_config(self):
    try:
      self.config = self.camera.get_config(self.context)
    except:
      logging.error("failed to fetch config from the camera")
      sys.exit(1)

  def set_config(self):
    success = False
    while success is False:
      try:
        self.camera.set_config(self.config,self.context)
        success = True
      except Exception as ex:
        logging.error("%s setting camera config failed: %s" % (elapsed(),ex))
        time.sleep(0.05)

    return

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

  def set_exposure(self,settings):
    if [settings['shutterspeed'],settings['aperture'],settings['iso'],settings['type']] == self.old_config:
      logging.debug("%s Got request to save config but config is not changing, skipping." % (elapsed()))
      return

    self.get_config()

    self.config_option('shutterspeed', self.settings.shutterspeed[settings['shutterspeed']])
    buf = settings['aperture'].rstrip('.0')
    self.config_option('aperture', self.settings.aperture[buf])
    self.config_option('iso', self.settings.iso[settings['iso']])
    if settings['type'] == 'BURST':
      self.config_option('drivemode', self.settings.drivemode['Continuous high speed'])
    else:
      self.config_option('drivemode', self.settings.drivemode['Single'])

    self.set_config()
    self.old_config = [settings['shutterspeed'],settings['aperture'],settings['iso'],settings['type']]

  def trigger_shutter(self,burst=False):

    logging.debug("%s pressing shutter" % (elapsed()))
    GPIO.output(self.pin, True)

    if burst is False:
      logging.debug("%s pausing for shutter open" % (elapsed()))
      time.sleep(self.shutter_hold)
    else:
      time.sleep(burst)

    GPIO.output(self.pin, False)
    logging.debug("%s released" % (elapsed()))

def ledon():
  GPIO.output(33,GPIO.HIGH)

def ledoff():
  GPIO.output(33,GPIO.LOW)

def elapsed():
  global event_time
  return "+%fs" % ((datetime.now() - event_time).total_seconds())

def set_date(date):
  logging.info("TEST RUN: Setting date to %s" % (date))
  setdate = date - timedelta(seconds=2)
  os.system('timedatectl set-ntp 0')
  os.system("timedatectl set-time '%s'" % (setdate.strftime("%Y-%m-%d %H:%M:%S.%f")))

def unset_date():
  os.system('timedatectl set-ntp 1')

if __name__ == '__main__':
  global debug

  if os.getuid() == 0:
    file_log = logging.FileHandler(filename='/var/log/rpi-eclipse.log')
  else:
    file_log = logging.FileHandler(filename='./rpi-eclipse.log')
  std_log = logging.StreamHandler(stream=sys.stdout)
  log_handlers = [ file_log, std_log ]

  logging.basicConfig(
    level=logging.DEBUG, 
    handlers=log_handlers,
    format='[%(asctime)s] {%(filename)s:%(lineno)3d} %(levelname)05s - %(message)s',
  )

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

  logging.info("INFO: fastest cycle time with configured delays is %.02f seconds." % (args.config_delay + args.shutter_hold + args.buffer_clear))

  if not os.getuid() == 0 and args.run_now is True:
    logging.error("The -r/--run-now option requires running this script as root so it can set the system time.")
    sys.exit(1)

  if args.run_now and args.set_time:
    logging.error("Cannot set both -r and -t at the same time.")
    sys.exit(1)

  camera_events = SEseq.SEseq(args.script)

  if os.getuid() == 0 and args.run_now is True:
    set_date(camera_events.first)

  if os.getuid() == 0 and args.set_time:
    set_date(datetime.strptime(args.set_time, '%Y/%m/%d %H:%M:%S'))

  cam = Camera(args.shutter_hold)

  try:
    for event in camera_events:
      now = datetime.now()

      if (now - event['start']).total_seconds() > 0.5:
        logging.info("PAST EVENT, rejecting. %s" % (event['start']))
        continue

      # pause until our scheduled moment of exposure
      wait_for_event = (event['start'] - now).total_seconds()
      if wait_for_event > 0:
        logging.info("Sleeping until next event in %.02f seconds." % (wait_for_event))
        time.sleep(wait_for_event)

      ledon()
      event_time = datetime.now()
      logging.info("%s EVENT at %s (scheduled) %s (actual) (%ss @ %s ISO %s)" % (event['type'],event['start'],event_time,event['shutterspeed'],event['aperture'],event['iso']))
      cam.set_exposure(event)
      time.sleep(args.config_delay)
      logging.debug("%s camera configured" % (elapsed()))
      if event['type'] == 'BURST':
        cam.trigger_shutter(burst=event['duration'])
      else:
        cam.trigger_shutter(args.shutter_hold)
        time.sleep(args.buffer_clear)

      ledoff()

    logging.info("Sequence complete, cleaning up and exiting.")
    if os.getuid() == 0 and args.run_now is True:
      unset_date()
    GPIO.cleanup()

  except (KeyboardInterrupt, SystemExit):
    logging.error("caught interrupt, cleaning up and exiting")
    if os.getuid() == 0 and args.run_now is True:
      unset_date()
    GPIO.cleanup()



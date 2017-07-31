#!/usr/bin/python

# this script will use gphoto2 to scrape available configuration options
# from the usb attached camera. The script will dump to stdout a python
# class that can be imported into other scripts

import sys
import gphoto2 as gp
import pprint as pp

try: 
  context = gp.Context()
  camera = gp.Camera()
  camera.init(context)
except:
  print("Could not init camera.")
  sys.exit(0)

def build_dict(field):

  try:
    buf = camera.get_config(context).get_child_by_name(field).get_choices()
  except:
    print("failed to get config for field " + field)
    sys.exit(1)
  index = 0
  output = {}
  for choice in buf:
    output[choice] = index
    index += 1

  sys.stdout.write('  ' + field + ' = ')
  pp.pprint(output, indent=4)

  return output

print("class CameraSettings:")

shutterspeed = build_dict('shutterspeed')
remoterelease = build_dict('eosremoterelease')
drivemode = build_dict('drivemode')
aperture = build_dict('aperture')
aeb = build_dict('aeb')
capturetarget = build_dict('capturetarget')
iso = build_dict('iso')

camera.exit(context)

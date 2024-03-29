# this class will use gphoto2 to scrape available configuration options
# from the usb attached camera. The script will dump to stdout a python
# class that can be imported into other scripts

import sys
import gphoto2 as gp
import pprint as pp

class CameraSettings:
  def __init__(self,camera,context):
    self.camera = camera
    self.context = context

    self.iso = self.build_dict('iso')
    self.shutterspeed = self.build_dict('shutterspeed')
    self.aperture = self.build_dict('aperture')

    self.remote = self.build_dict('eosremoterelease')
    self.drivemode = self.build_dict('drivemode')
    self.aeb = self.build_dict('aeb')
    self.capturetarget = self.build_dict('capturetarget')
    self.drivemode = self.build_dict('drivemode')

  def build_dict(self,field):

    try:
      buf = self.camera.get_config(self.context).get_child_by_name(field)
    except:
      print("failed to get config for field " + field)
      sys.exit(1)

    options = [str(x) for x in buf.get_choices()]
    index = 0
    output = {}
    for choice in options:
      output[choice] = index
      index += 1

    return output


if __name__ == '__main__':
  try: 
    context = gp.Context()
    camera = gp.Camera()
    camera.init(context)
  except:
    print("Could not init camera.")
    sys.exit(0)

  config = CameraSettings(camera, context)
  
  print("Exposure Options:")
  print(config.shutterspeed)

  print("Aperture Options:")
  print(config.aperture)

  print("ISO Options:")
  print(config.iso)
  camera.exit(context)



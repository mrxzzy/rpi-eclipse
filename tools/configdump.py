#!/usr/bin/python

# this dumps everything gphoto2 can find about an attached camera

# functions stolen from python-gphoto2 / examples / cam-conf-view.gui.py

import sys
import gphoto2 as gp
import pprint as pp
import time, tzlocal
from datetime import datetime

try: 
  context = gp.Context()
  camera = gp.Camera()
  camera.init(context)
except:
  print("Could not init camera.")
  sys.exit(0)

def get_gphoto2_CameraWidgetType_string(innumenum):
    switcher = {
        0: "GP_WIDGET_WINDOW",
        1: "GP_WIDGET_SECTION",
        2: "GP_WIDGET_TEXT",
        3: "GP_WIDGET_RANGE",
        4: "GP_WIDGET_TOGGLE",
        5: "GP_WIDGET_RADIO",
        6: "GP_WIDGET_MENU",
        7: "GP_WIDGET_BUTTON",
        8: "GP_WIDGET_DATE"
    }
    return switcher.get(innumenum, "Invalid camwidget type")

class PropCount(object):
    def __init__(self):
        self.numro = 0
        self.numrw = 0
        self.numtot = 0
        self.numexc = 0
    def __str__(self):
        return "{},{},{},{}".format(self.numtot,self.numrw,self.numro,self.numexc)

def get_camera_model(camera_config):
    # get the camera model
    OK, camera_model = gp.gp_widget_get_child_by_name(
        camera_config, 'cameramodel')
    if OK < gp.GP_OK:
        OK, camera_model = gp.gp_widget_get_child_by_name(
            camera_config, 'model')
    if OK >= gp.GP_OK:
        camera_model = camera_model.get_value()
    else:
        camera_model = ''
    return camera_model


def get_formatted_ts(inunixts=None):
    if inunixts is None:
        unixts = time.time()
    else:
        unixts = inunixts
    unixts = round(unixts,6)
    tzlocalts = tzlocal.get_localzone().localize(datetime.utcfromtimestamp(unixts), is_dst=None).replace(microsecond=0)
    isots = tzlocalts.isoformat(' ')
    fsuffts = tzlocalts.strftime('%Y%m%d_%H%M%S') # file suffix timestamp
    return (unixts, isots, fsuffts)

def get_camera_config_children(childrenarr, savearr, propcount):
    for child in childrenarr:
        tmpdict = {}
        propcount.numtot += 1
        if child.get_readonly():
            propcount.numro += 1
        else:
            propcount.numrw += 1
        tmpdict['idx'] = str(propcount)
        tmpdict['ro'] = child.get_readonly()
        tmpdict['name'] = child.get_name()
        tmpdict['label'] = child.get_label()
        tmpdict['type'] = child.get_type()
        tmpdict['typestr'] = get_gphoto2_CameraWidgetType_string( tmpdict['type'] )
        if ((tmpdict['type'] == gp.GP_WIDGET_RADIO) or (tmpdict['type'] == gp.GP_WIDGET_MENU)):
            tmpdict['count_choices'] = child.count_choices()
            tmpchoices = []
            for choice in child.get_choices():
                tmpchoices.append(choice)
            tmpdict['choices'] = ",".join(tmpchoices)
        if (child.count_children() > 0):
            tmpdict['children'] = []
            get_camera_config_children(child.get_children(), tmpdict['children'], propcount)
        else:
            # NOTE: camera HAS to be "into preview mode to raise mirror", otherwise at this point can get "gphoto2.GPhoto2Error: [-2] Bad parameters" for get_value
            try:
                tmpdict['value'] = child.get_value()
            except Exception as ex:
                tmpdict['value'] = "{} {}".format( type(ex).__name__, ex.args)
                propcount.numexc += 1
        savearr.append(tmpdict)

def get_camera_config_object(camera_config):
    retdict = {}
    retdict['camera_model'] = get_camera_model(camera_config)
    propcount = PropCount()
    retarray = []
    retdict['children'] = []
    get_camera_config_children(camera_config.get_children(), retdict['children'], propcount)
    excstr = "no errors - OK." if (propcount.numexc == 0) else "{} errors - bad (please check if camera mirror is up)!".format(propcount.numexc)
    print("Parsed camera config: {} properties total, of which {} read-write and {} read-only; with {}".format(propcount.numtot, propcount.numrw, propcount.numro, excstr))
    return retdict

config = get_camera_config_object(camera.get_config())
pp.pprint(config)


#!/usr/bin/python

# this script will dump a csv manifest of all exposures configured in 
# the Eclipse class, which can then be imported by eclipse.py to actually
# execute the exposures. 

# the script has some logic to cram in as many exposures as possible in the
# allotted time, but it's not perfect. massaging start/end times will be
# necessary

import sys
from datetime import datetime, timedelta
from mtjefferson import Eclipse

eclipse = Eclipse()

last_ending = None
graph = []

def output_csv(timestamp,settings):
  global last_ending
  global graph

  if 'aeb' in settings:
    aeb = eclipse.aeb_calc(settings['label'])
    duration = eclipse.config_time + aeb['time']
    end = timestamp + eclipse.config_delay + aeb['delta']
    aeb_out = aeb['type']
    aeb_dir = settings['aebdir']
  else:
    aeb_out = "Off"
    aeb_dir = "None"
    duration = eclipse.config_time + eclipse.exposure_time
    end = timestamp + eclipse.config_delay + eclipse.exposure_delay

  if last_ending is None:
    last_ending = end
    label = settings['label']
  else:
    if last_ending > timestamp:
      label = "***%s" % (settings['label'])
    else:
      label = settings['label']
    last_ending = end

  date_format = '%Y-%m-%d %H:%M:%S.%f'
  start = timestamp.strftime(date_format)
  end = end.strftime(date_format)
  print("%s,%s,%s,%0.2f,%s,%s,%s,%s,%s" % (label,start,end,duration,settings['iso'],settings['aperture'],settings['shutterspeed'],aeb_out,aeb_dir))

def take_picture(label, shutterspeed, aperture, iso, aeb=None):
  return 1

event = eclipse.get_date('C1','start')

output = {}

# first job is to determine end of C1 phase (read: baily's beads about to 
# start.
c1_end = eclipse.get_date('BB1','start') - eclipse.exposure_delay - eclipse.config_delay

settings_c1 = {
  'label': 'C1',
  'iso': eclipse.C1['iso'],
  'shutterspeed': eclipse.C1['shutterspeed'],
  'aperture': eclipse.C1['aperture'],
}
settings_c3 = {
  'label': 'C3',
  'iso': eclipse.C3['iso'],
  'shutterspeed': eclipse.C3['shutterspeed'],
  'aperture': eclipse.C3['aperture'],
}
# now iterate backwards queuing exposures until we go beyond c1[start] 
while c1_end > (eclipse.get_date('C1','start') - timedelta(seconds=300)):
  output[c1_end] = settings_c1
  c1_end -= timedelta(seconds=eclipse.C1['interval'])

# C1 done. Let's do the C3 partial phase as well. 
c3_begin = eclipse.get_date('BB2','end')
c3_end = eclipse.event_block('C3')['end']
while c3_begin < c3_end:
  output[c3_begin] = settings_c3
  c3_begin += timedelta(seconds=eclipse.C3['interval'])

bb1 = eclipse.event_block('BB1',backwards=True)
for i in bb1['triggers']:
  output[i] = {
    'label': 'BB1',
    'iso': eclipse.BB1['iso'],
    'aperture': eclipse.BB1['aperture'],
    'shutterspeed': eclipse.BB1['shutterspeed'],
    'aeb': eclipse.BB1['aeb'],
    'aebdir': eclipse.BB1['aebdir'],
  }

bb2 = eclipse.event_block('BB2')
for i in bb2['triggers']:
  output[i] = {
    'label': 'BB2',
    'iso': eclipse.BB2['iso'],
    'aperture': eclipse.BB2['aperture'],
    'shutterspeed': eclipse.BB2['shutterspeed'],
    'aeb': eclipse.BB2['aeb'],
    'aebdir': eclipse.BB2['aebdir'],
  }

ch1 = eclipse.event_block('CH1')
for i in ch1['triggers']:
  output[i] = {
    'label': 'CH1',
    'iso': eclipse.CH1['iso'],
    'aperture': eclipse.CH1['aperture'],
    'shutterspeed': eclipse.CH1['shutterspeed'],
    'aeb': eclipse.CH1['aeb'],
    'aebdir': eclipse.CH1['aebdir'],
  }

ch2 = eclipse.event_block('CH2')
for i in ch2['triggers']:
  output[i] = {
    'label': 'CH2',
    'iso': eclipse.CH2['iso'],
    'aperture': eclipse.CH2['aperture'],
    'shutterspeed': eclipse.CH2['shutterspeed'],
    'aeb': eclipse.CH2['aeb'],
    'aebdir': eclipse.CH2['aebdir'],
  }

pr1 = eclipse.event_block('PR1')
for i in pr1['triggers']:
  output[i] = {
    'label': 'PR1',
    'iso': eclipse.PR1['iso'],
    'aperture': eclipse.PR1['aperture'],
    'shutterspeed': eclipse.PR1['shutterspeed'],
    'aeb': eclipse.PR1['aeb'],
    'aebdir': eclipse.PR1['aebdir'],
  }

pr2 = eclipse.event_block('PR2')
for i in pr2['triggers']:
  output[i] = {
    'label': 'PR2',
    'iso': eclipse.PR2['iso'],
    'aperture': eclipse.PR2['aperture'],
    'shutterspeed': eclipse.PR2['shutterspeed'],
    'aeb': eclipse.PR2['aeb'],
    'aebdir': eclipse.PR1['aebdir'],
  }

# corona sequences function differently: 6 possible bracketed 
# exposures to attempt to capture varying levels of the corona
# fit as many as we can into a specified block of time
def schedule_corona(events):
  global output

  for i in events['triggers'][0::6]:
    output[i] = {
      'label': 'SR01',
      'iso': eclipse.SR01['iso'],
      'aperture': eclipse.SR01['aperture'],
      'shutterspeed': eclipse.SR01['shutterspeed'],
      'aeb': eclipse.SR01['aeb'],
      'aebdir': eclipse.SR01['aebdir']
    }
  for i in events['triggers'][1::6]:
    output[i] = {
      'label': 'SR02',
      'iso': eclipse.SR02['iso'],
      'aperture': eclipse.SR02['aperture'],
      'shutterspeed': eclipse.SR02['shutterspeed'],
      'aeb': eclipse.SR02['aeb'],
      'aebdir': eclipse.SR02['aebdir']
    }
  for i in events['triggers'][2::6]:
    output[i] = {
      'label': 'SR05',
      'iso': eclipse.SR05['iso'],
      'aperture': eclipse.SR05['aperture'],
      'shutterspeed': eclipse.SR05['shutterspeed'],
      'aeb': eclipse.SR05['aeb'],
      'aebdir': eclipse.SR05['aebdir']
    }
  for i in events['triggers'][3::6]:
    output[i] = {
      'label': 'SR1',
      'iso': eclipse.SR1['iso'],
      'aperture': eclipse.SR1['aperture'],
      'shutterspeed': eclipse.SR1['shutterspeed'],
      'aeb': eclipse.SR1['aeb'],
      'aebdir': eclipse.SR1['aebdir']
    }
  for i in events['triggers'][4::6]:
    output[i] = {
      'label': 'SR2',
      'iso': eclipse.SR2['iso'],
      'aperture': eclipse.SR2['aperture'],
      'shutterspeed': eclipse.SR2['shutterspeed'],
      'aeb': eclipse.SR2['aeb'],
      'aebdir': eclipse.SR2['aebdir']
    }
  for i in events['triggers'][5::6]:
    output[i] = {
      'label': 'SR3',
      'iso': eclipse.SR3['iso'],
      'aperture': eclipse.SR3['aperture'],
      'shutterspeed': eclipse.SR3['shutterspeed'],
      'aeb': eclipse.SR3['aeb'],
      'aebdir': eclipse.SR3['aebdir']
  } 

corona1 = eclipse.event_block('CORONA1')
schedule_corona(corona1)

corona2 = eclipse.event_block('CORONA2')
schedule_corona(corona2)

earthshine = eclipse.event_block('Earthshine')
for i in earthshine['triggers']:
  output[i] = {
    'label': 'Earthshine',
    'iso': eclipse.Earthshine['iso'],
    'aperture': eclipse.Earthshine['aperture'],
    'shutterspeed': eclipse.Earthshine['shutterspeed'],
    'aeb': eclipse.Earthshine['aeb'],
    'aebdir': eclipse.Earthshine['aebdir'],
  }

print("label,start,end,duration,iso,aperture,shutterspeed,aeb,aebdir")
for key in sorted(output):
  output_csv(key,output[key])

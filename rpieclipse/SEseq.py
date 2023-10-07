# this class reads in a script produced by yours truly to build
# out a sequence of exposures that eclipse.py consumes

#YYYY/MM/DD HH:MM:SS.SS,Repeat,Duration,   Shot,Shutter,Aperture,  ISO, Comment
#2023/10/14 15:00:00.00,  True,       0, SINGLE,  1/800,   f/8.0,  400, Pre Eclipse

import os, sys
import re
import csv
import copy
import pprint as pp
from datetime import datetime
from datetime import timedelta

class SEseq:
  def __init__(self,config_file,cycle_time=1):
    self.first = False
    self.last = False
    self.events = []
    self.input = config_file

    # the fastest the camera in use can apply settings, fire shutter, 
    # and clear buffer for a single image
    self.cycle_time = cycle_time

    self.parse()

    self.current = 0
    self.eventcount = len(self.events)

  def __iter__(self):
    return iter(self.events)

  def __next__(self):
    self.current += 1
    if self.current < self.eventcount:
      return self.current
    raise StopIteration

  def repeat_exposure(self,until,settings):

    start = settings['start']
    interval = settings['interval']
    minimum = timedelta(seconds=self.cycle_time)
    until = until - minimum

    if interval < minimum:
      cycle_time = minimum
    else:
      cycle_time = interval

    output = []
    while start < until:
      start = start + interval

      if start > until:
        return output

      settings['start'] = start

      output.append(copy.copy(settings))

  def parse(self):

    if not os.path.isfile(self.input):
      print("Script not found (%s)" % (self.input))
      sys.exit(1)

    in_repeat = False
    repeated_exposure = []
    
    with open(self.input) as f:
      reader = csv.reader(f, skipinitialspace=True, delimiter=',')

      for line in reader:
        #print(line)
        if len(line) == 0:
          continue

        if re.match("^\d{4}/\d{2}/\d{2}",line[0]):

          if line[4] == "MARK":
            continue

          when = datetime.strptime(line[0], '%Y/%m/%d %H:%M:%S.%f')
          if not self.first:
            self.first = when
          self.last = when

          if in_repeat:
            self.events = self.events + self.repeat_exposure(when,repeated_exposure)
            in_repeat = False

          exposure = {
            'aeb'         : False,
            'aebdir'      : 'None',
            'type'        : line[4],
            'interval'    : timedelta(seconds=float(line[3])),
            'duration'    : float(line[2]),
            'shutterspeed': line[5],
            'aperture'    : line[6].split('/')[1],
            'iso'         : line[7],
            'start'       : when,
            'comment'     : line[8],
          }
          self.events.append(exposure)

          if line[1] == 'True':
            in_repeat = True
            repeated_exposure = copy.copy(exposure)


if __name__ == '__main__':
  test = SEseq('oct14.se',0.75) 
  for event in test:
    print("%s %s (%ss @ %s ISO %s) duration: %s (%s)" % (event['start'], event['type'], event['shutterspeed'], event['aperture'], event['iso'], event['duration'], event['comment']))


# this class reads a script produces by Eclipse Orchestrator's 
# "View Exposure Sequence" menu option and parses it into
# scheduler commands.

#YYYY/MM/DD HH:MM:SS.S,IncrTime,  Cam, Action Shutter Aperture  ISO  Q    MLU  Filetype, Comment
#2023/10/14 17:19:04.0,    55.7, asdf,    PIC  1/1500    f/8.0  400  7.9  0.0  RAW,      Partials C3-C4, filter on 45.0%

import os, sys
import re
import pprint as pp
from datetime import datetime

class EOseq:
  def __init__(self,config_file):
    self.first = False
    self.last = False
    self.events = []
    self.input = config_file
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

  def parse(self):

    if not os.path.isfile(self.input):
      print("Script not found (%s)" % (self.input))
      sys.exit(1)

    with open(self.input) as f:
      inloop = False
      startsat = False

      for line in f:
        if line in  ['\n','\r\n']:
          continue

        if re.match("^\d{4}/\d{2}/\d{2}",line):
          fields = re.split(",",line)

          when = datetime.strptime(fields[0], '%Y/%m/%d %H:%M:%S.%f')
          if not self.first:
            self.first = when
          self.last = when
          duration = [1]
          action = ' '.join(fields[3].split()).split()

          shutterspeed = action[1]
          aperture = action[2].split('/')[1]
          iso = action[3]

          exposure = {
            'aeb'         : False,
            'aebdir'      : 'None',
            'aperture'    : aperture,
            'duration'    : duration,
            'iso'         : iso,
            'shutterspeed': shutterspeed,
            'start'       : when,
          }
          self.events.append(exposure)



if __name__ == '__main__':
  test = EOseq('oct14.eo') 
  pp.pprint(test.events)




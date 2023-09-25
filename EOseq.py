# this class reads a script produces by Eclipse Orchestrator's 
# "View Exposure Sequence" menu option and parses it into
# scheduler commands.

#YYYY/MM/DD HH:MM:SS.S,IncrTime,  Cam, Action Shutter Aperture  ISO  Q    MLU  Filetype, Comment
#2023/10/14 17:19:04.0,    55.7, asdf,    PIC  1/1500    f/8.0  400  7.9  0.0  RAW,      Partials C3-C4, filter on 45.0%

import re

class EOseq:
  def __init__(self,config_file):
    self.input = config_file
    self.parse()

  def parse(self):

    with open(self.input) as f:
      inloop = False
      startsat = False

      for line in f:
        if line in  ['\n','\r\n']:
          continue

        if re.match("^\d{4}/\d{2}/\d{2}",line):
          fields = re.split(",",line)

          when = fields[0]
          action = ' '.join(fields[3].split()).split()

          exposure = action[1]
          aperture = action[2].split('/')[1]
          iso = action[3]

          print("takepic at %s: (f/%s @ %s %s)" % (when,aperture,exposure,iso))


if __name__ == '__main__':
  test = EOseq('oct14.eo') 




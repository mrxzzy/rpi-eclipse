# this class reads a script produced by Solar Eclipse Maestro (and probably 
# Eclipse Orchestrator) and parses it into scheduler commands.


#label,start,                      end,                        duration, iso, aperture, shutterspeed, aeb, aebdir
#C1,   2017-08-21 16:03:20.750000, 2017-08-21 16:03:22.100000, 1.35,     100, 16,       1/1600,       Off, None

import re

class SEM:
  def __init__(self,config_file):
    self.input = config_file
    self.parse()

  def parse(self):

    with open(self.input) as f:
      inloop = False
      startsat = False

      for line in f:
        if re.match("^#",line):
          continue
        if line in  ['\n','\r\n']:
          continue

        if re.match("^FOR",line):
          inloop = True
          fields = re.split(',',line)
          
          if fields[1] == '(INTERVALOMETER)':
            type = 'Intervalometer'
            if fields[2] == '0':
              startsat = True
            interval = fields[3]
            count = int(fields[4])

          print("intervals: startsat: %s interval: %s count: %s" % (startsat, interval, count))

        if re.match("^TAKEPIC",line):
          fields = re.split(",",line)
          event = fields[1]
          offset = fields[2]
          time = fields[3]
          exposure = fields[5]
          aperture = fields[6]
          iso = fields[7]
          incremental = fields[11]

          if inloop:
            for i in range(count):
              print("takepic at %s: @ %s%s, (f/%s@%ss ISO%s) %s" % (event,offset,time,aperture,exposure,iso,incremental))




if __name__ == '__main__':
  test = SEM('oct14.sem') 




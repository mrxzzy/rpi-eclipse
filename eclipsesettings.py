# just a parent class inherited by the Eclipse class, has
# methods to do some useful calculations

import sys
from datetime import datetime,timedelta

class EclipseSettings:

  def get_date(self,event,tag,offset=None):
    date_format = '%Y/%m/%d %H:%M:%S.%f'
    time = getattr(self, event)

    if offset is not None:
      return datetime.strptime(self.date + ' ' + time[tag], date_format) - timedelta(seconds=offset)
    else:
      return datetime.strptime(self.date + ' ' + time[tag], date_format)

  def dump_event(self,event):
    print("start: %s" % (event['start']))
    print("  end: %s" % (event['end']))
    for cur in event['triggers']:
      print("      exposure: %s " % (cur))

  def aeb_calc(self,event):
    inf = getattr(self,event)

    if 'aeb' in inf:
      if inf['aeb'] is not False:
        aeb_delay = getattr(self,'aeb' + str(inf['aeb']))
        aeb_delta = timedelta(seconds=aeb_delay)
        aeb_type = inf['aeb'] 

        return {'time': aeb_delay, 'delta': aeb_delta, 'type': aeb_type}

    return False

  def event_block(self,event,backwards=False):
    inf = getattr(self,event)

    start = self.get_date(event,'start')
    end = self.get_date(event,'end')
    span = end - start

    aeb_cfg = self.aeb_calc(event)

    if aeb_cfg is False:
      overhead = self.config_delay + self.exposure_delay
    else:
      overhead = self.config_delay + aeb_cfg['delta']

    possible_loops = int(span / overhead)
    time_taken = possible_loops * overhead

    triggers = []
    if backwards is False: 
      for i in range(possible_loops):
        triggers.append(start + (overhead * i))
      soft_end = start + time_taken
      return { 'start': start, 'end': soft_end, 'triggers': triggers }
    else:
      for i in range(possible_loops):
        triggers.append(end - (overhead * (i+1)))
      soft_start = end - time_taken
      return { 'start': soft_start, 'end': end, 'triggers': triggers }

    #print(inf,start,end,span,overhead)
    #print(end,':',soft_end)

if __name__ == "__main__":
  sys.exit(0)

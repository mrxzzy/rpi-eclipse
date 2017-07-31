#!/usr/bin/python

# script will read in a csv file produced by scheduler.py and build a
# crude gantt plot, allowing visualization of how busy the camera is

# filters out C1/C3 events because the graph gets really hideous with
# those events included

import pandas
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.dates
from matplotlib.dates import MINUTELY, SECONDLY, DateFormatter, rrulewrapper, RRuleLocator
import numpy as np

from datetime import datetime

date_format = '%Y-%m-%d %H:%M:%S.%f'

def create_date(date):
  global date_format

  date = datetime.strptime(date,date_format)
  mdate = matplotlib.dates.date2num(date)
  return mdate

ylabels = []
customDates = []

df = pandas.read_csv('./mtjefferson.csv', header=0)

cur = ''
count = 0
for i,row in df.iterrows():
  if row['label'] == 'C1' or row['label'] == 'C3':
    continue
  ylabels.append(row['label'] + '.' + str(count))
  customDates.append( [ create_date(row['start']), create_date(row['end'])])
  count += 1

ilen = len(ylabels)
pos = np.arange(0.5, ilen * 0.5 + 0.5, 0.5)
task_dates = {}

for i,task in enumerate(ylabels):
  task_dates[task] = customDates[i]

fig = plt.figure(figsize=(30,20))

ax = fig.add_subplot(111)

for i in range(len(ylabels)):
  start_date, end_date = task_dates[ylabels[i]]
  ax.barh((i*0.5)+0.5, end_date - start_date, left=start_date, height=0.3, align='center', edgecolor='lightgreen', color='orange', alpha = 0.8)

locsy, labelsy = plt.yticks(pos,ylabels)
plt.setp(labelsy,fontsize=14)
#ax.axis('tight')
ax.set_ylim(ymin = -0.1, ymax = ilen * 0.5 + 0.5)
ax.grid(color = 'g', linestyle = ':')
ax.xaxis_date()

rule = rrulewrapper(SECONDLY, interval=3)
loc = RRuleLocator(rule)
formatter = DateFormatter(date_format)

ax.xaxis.set_major_locator(loc)
ax.xaxis.set_major_formatter(formatter)
labelsx = ax.get_xticklabels()
plt.setp(labelsx, rotation=30, fontsize=10)

font = font_manager.FontProperties(size='small')
ax.legend(loc=1,prop=font)

ax.invert_yaxis()
fig.autofmt_xdate()

plt.savefig('mtjefferson.png')


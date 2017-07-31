#!/bin/bash

# run as root!

date
timedatectl set-ntp 0

#before C1:
#timedatectl set-time '2017-08-21 16:03:13'

#before C2:
timedatectl set-time '2017-08-21 17:18:10.0'

echo "totally testing the eclipse script now"
date
./eclipse.py

echo "done with eclipse"

timedatectl set-ntp 1
sleep 2
date

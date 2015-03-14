#!/usr/bin/python
#===========================================================================
# watchdog.py
#
# A safety watchdog to turn off the servo power if idle for a period of
# time. Basically watches a file and turns servo power off if file is
# older than specified time interval. Add a cron entry to run this.
#
# 2014-10-11
# Carter Nelson
#===========================================================================
import lasercam
theBox = lasercam.LaserCamBox()

import os.path
import time

#-------------------------------
# set up
#-------------------------------
WATCHDOG_FILE = "/home/pi/rpi-laser/servo.wd" # file to watch
MAX_IDLE_TIME = 600                           # time in seconds

#-------------------------------
# run the check
#-------------------------------
if os.path.exists(WATCHDOG_FILE):
  ctime = time.time()                         # current time
  mtime = os.path.getmtime(WATCHDOG_FILE)     # time of last modification
  dtime = ctime - mtime                       # delta time in seconds
  if dtime>MAX_IDLE_TIME:
    theBox.disablePWM()                       # disable if max time reached
else:
  theBox.disablePWM()                         # disable if watchdog file is missing

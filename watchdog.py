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

#-------------------------------
# import modules
#-------------------------------
import os.path
import time
import RPi.GPIO as io
io.setmode(io.BCM)

#-------------------------------
# set up
#-------------------------------
OE_PIN = 4                  # pin that controls servo power
WATCHDOG_FILE = "/home/pi/rpi-laser/servo.wd"  # file to watch
MAX_IDLE_TIME = 600         # time in seconds

io.setup(OE_PIN, io.OUT)

#-------------------------------
# run the check
#-------------------------------
if os.path.exists(WATCHDOG_FILE):
  ctime = time.time()
  mtime = os.path.getmtime(WATCHDOG_FILE)
  dtime = ctime - mtime
  if dtime>MAX_IDLE_TIME:
    io.output(OE_PIN, io.HIGH)
else:
  io.output(OE_PIN, io.HIGH)

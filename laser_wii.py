#!/usr/bin/python
#===========================================================================
# laser_wii.py
#
# Control laser with Wii remote over bluetooth.
#  * bluetooth via USB dongle and standard linux BT stack
#  * Wii remote control using Cwiid (http://abstrakraft.org/cwiid/)
#       sudo apt-get install python-cwiid 
#
# 2015-03-09
# Carter Nelson
#===========================================================================
import lasercam
import cwiid
import time

# Does python not have a built in for this?
def interp(xval, xmin, xmax, ymin, ymax):
    xval = xmin if (xval<xmin) else xval
    xval = xmax if (xval>xmax) else xval
    xv = float(xval)
    xn = float(xmin)
    xx = float(xmax)
    yn = float(ymin)
    yx = float(ymax)
    xi = yn + (xv-xn) * ((yx-yn)/(xx-xn))
    return int(xi)
    
# Setup laser cam box
lasercambox = lasercam.LaserCamBox()
lasercambox.enablePWM(update=True)

# Sync wiimote
for x in xrange(1,5):
    lasercambox.statusLEDOn(2)
    time.sleep(0.5)
    lasercambox.statusLEDOff(2)
    time.sleep(0.5)
print "Press 1+2 on Wiimote now."
wiimote = cwiid.Wiimote()  
wiimote.led = 9
wiimote.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_EXT
time.sleep(1)
print "Connected"
lasercambox.statusLEDOn(2)

abort = False
    
# Loop until something
while not abort:
    buttons = wiimote.state['buttons']
    nunchuk_buttons = wiimote.state['nunchuk']['buttons']
    nunchuk_stick = wiimote.state['nunchuk']['stick']   
    if (buttons & cwiid.BTN_A):
        abort = True
    if (nunchuk_buttons & cwiid.NUNCHUK_BTN_Z):
        lasercambox.laserOn()
    else:
        lasercambox.laserOff()
    sx = interp(nunchuk_stick[0],31,229,205,410)
    sy = interp(nunchuk_stick[1],31,229,205,410)
    print "%i\t%i\t\t%i\t%i" % (nunchuk_stick[0], nunchuk_stick[1], sx, sy)
    lasercambox.laserSetPosition( (sx,sy) )
    time.sleep(0.1)

# Clean up
lasercambox.laserOff()
lasercambox.statusLEDOff(2)
lasercambox.disablePWM()


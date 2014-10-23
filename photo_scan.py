#!/usr/bin/python
#===========================================================================
# photo_scan.py
#
# Move camera to multipe position and take photo at each.
#
# 2014-10-11
# Carter Nelson
#===========================================================================

#-------------------------------
# import modules
#-------------------------------
from Adafruit_Raspberry_Pi_Python_Code.Adafruit_PWM_Servo_Driver.Adafruit_PWM_Servo_Driver import PWM
import RPi.GPIO as io
io.setmode(io.BCM)
import time
import picamera

#-------------------------------
# setup
#-------------------------------
OE_PIN      = 4          # servo output control
OE_State    = io.HIGH    # LOW=ON  HIGH=OFF
cameraXChan = 0          # left/right
cameraYChan = 1          # up/down
servoMin    = 205        # min pulse length out of 4096 (linear range)
servoMax    = 410        # max pulse length out of 4096 (linear range)
#servoMin    = 130        # min pulse length out of 4096 (max range)
#servoMax    = 600        # max pulse length out of 4096 (max range)
servoStep   = 1          # step value for servo moves
cameraXVal  = (servoMin+servoMax)/2
cameraYVal  = (servoMin+servoMax)/2

io.setup(OE_PIN, io.OUT)
io.output(OE_PIN, OE_State)

#-------------------------------
# define locations
#-------------------------------
camera_locations = [ (205, 205),
                     (205, 285),
                     (285, 205),
                     (285, 285),
                     (375, 205),
                     (375, 285) ]

#-------------------------------
# initialise the camera
#-------------------------------
camera = picamera.PiCamera()
camera.hflip = True
camera.vflip = True
camera.resolution = (2592, 1944)

#-------------------------------
# initialise PWM device
#-------------------------------
pwm = PWM(0x40, debug=False)
pwm.setPWMFreq(50)   # pulse frequency in Hz

#-------------------------------
# servo power control
#-------------------------------
def toggleServoPower():
  global OE_State
  OE_State = not OE_State
  io.output(OE_PIN, OE_State)

def servosOff():
  global OE_State
  OE_State = io.HIGH
  io.output(OE_PIN, OE_State)

def servosOn():
  global OE_State
  OE_State = io.LOW
  io.output(OE_PIN, OE_State)

#-----------------------------------------------------------------------------
#   M A I N
#-----------------------------------------------------------------------------
servosOn()
for location in camera_locations:
  x = location[0]
  y = location[1]
  pwm.setPWM(cameraXChan, 0, x)
  pwm.setPWM(cameraYChan, 0, y)
  filename = "capx{0}y{1}.jpg".format(x,y)
  print "capturing {0}...".format(filename)
  camera.capture(filename)  
servosOff()
camera.close()

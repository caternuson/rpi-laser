#!/usr/bin/python
#===========================================================================
# laser_curses.py
#
# Curses interface to drive laser and camera.
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
import curses
#import picamera

#-------------------------------
# setup
#-------------------------------
OE_PIN      = 4          # servo output control
OE_State    = io.HIGH    # LOW=ON  HIGH=OFF
LASER_PIN   = 16         # servo output control
LASER_State = io.LOW     # LOW=OFF  HIGH=ON
laserXChan  = 2          # left/right
laserYChan  = 3          # up/down
cameraXChan = 0          # left/right
cameraYChan = 1          # up/down
servoMin    = 205        # min pulse length out of 4096 (linear range)
servoMax    = 410        # max pulse length out of 4096 (linear range)
#servoMin    = 130        # min pulse length out of 4096 (max range)
#servoMax    = 600        # max pulse length out of 4096 (max range)
servoStep   = 1          # step value for servo moves
laserXVal   = (servoMin+servoMax)/2
laserYVal   = (servoMin+servoMax)/2
cameraXVal  = (servoMin+servoMax)/2
cameraYVal  = (servoMin+servoMax)/2

cameraS1 = ( (servoMin+servoMax)/2, (servoMin+servoMax)/2 )
cameraS2 = ( (servoMin+servoMax)/2, (servoMin+servoMax)/2 )
cameraS3 = ( (servoMin+servoMax)/2, (servoMin+servoMax)/2 )
cameraS4 = ( (servoMin+servoMax)/2, (servoMin+servoMax)/2 )

laserS1 = ( (servoMin+servoMax)/2, (servoMin+servoMax)/2 )
laserS2 = ( (servoMin+servoMax)/2, (servoMin+servoMax)/2 )
laserS3 = ( (servoMin+servoMax)/2, (servoMin+servoMax)/2 )
laserS4 = ( (servoMin+servoMax)/2, (servoMin+servoMax)/2 )

io.setup(OE_PIN, io.OUT)
io.output(OE_PIN, OE_State)
io.setup(LASER_PIN, io.OUT)
io.output(LASER_PIN, LASER_State)

#-------------------------------
# initialise the camera
#-------------------------------
#camera = picamera.PiCamera()
#camera.hflip = True
#camera.vflip = True
#camera.resolution = (2592, 1944)

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

#-------------------------------
# laser power control
#-------------------------------
def toggleLaserPower():
  global LASER_State
  LASER_State = not LASER_State
  io.output(LASER_PIN, LASER_State)

def laserOff():
  global LASER_State
  LASER_State = io.LOW
  io.output(LASER_PIN, LASER_State)

def laserOn():
  global LASER_State
  LASER_State = io.HIGH
  io.output(LASER_PIN, LASER_State)

#-----------------------------------------------------------------------------
#   M A I N
#-----------------------------------------------------------------------------
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
curses.curs_set(0)
stdscr.keypad(1)
stdscr.resize(24,75)

while 1:
  #--------------------------
  # update display
  #--------------------------
  stdscr.clear()
  stdscr.border(0,0,0,0)
  
  stdscr.addstr(13,2,"q - quit")
  stdscr.addstr(14,2,"w,s,a,d - camera up,down,left,right ")
  stdscr.addstr(15,2,"i,k,j,l - laser up,down,left,right")
  stdscr.addstr(16,2,"[,] - servo step decrease,increase")
  stdscr.addstr(17,2,"p - toggle servo power")
  stdscr.addstr(18,2,"o - toggle laser power")
  stdscr.addstr(19,2,"e - toggle camera LED power")
  stdscr.addstr(20,2,"x - take a photo")
  stdscr.addstr(21,2,"` - store location in 1,2,3,4 (camera) 7,8,9,0 (laser)")  
  
  stdscr.addstr(1,1,"CAMERA X = {0}  ".format(cameraXVal))
  stdscr.addstr(2,1,"       Y = {0}  ".format(cameraYVal))
  stdscr.addstr(1,25,"LASER X = {0}  ".format(laserXVal))
  stdscr.addstr(2,25,"      Y = {0}  ".format(laserYVal))
  
  stdscr.addstr(1,50,"SERVO STEP = {0}  ".format(servoStep))
  if OE_State == io.LOW:
    stdscr.addstr(2,50,"SERVOS ON ")
  else:
    stdscr.addstr(2,50,"SERVOS OFF")
  if LASER_State == io.HIGH:
    stdscr.addstr(4,25,"LASER ON ")
  else:
    stdscr.addstr(4,25,"LASER OFF")
  stdscr.addstr(4,1,"LED OFF")  
   
  stdscr.refresh()
  #--------------------------
  # output to servos
  #--------------------------
  pwm.setPWM(laserXChan, 0, laserXVal)
  pwm.setPWM(laserYChan, 0, laserYVal)
  pwm.setPWM(cameraXChan, 0, cameraXVal)
  pwm.setPWM(cameraYChan, 0, cameraYVal)
  #--------------------------
  # get keypress and act on it
  #--------------------------
  c = stdscr.getch()
  if c == ord('q'):
    break
  if c == ord('p'):
    toggleServoPower()
  if c == ord('o'):
    toggleLaserPower()
  if c == ord('x'):
    stdscr.addstr(6,1,"taking photo...")
#    camera.capture('blah.jpg') 
  if c == ord('['):
    servoStep -= 1
    servoStep = servoStep if servoStep > 1 else 1
  if c == ord(']'):
    servoStep += 1
    servoStep = servoStep if servoStep <= 50 else 50
  if OE_State == io.LOW:
    if c == ord('i'):
      laserYVal -= servoStep
      laserYVal = laserYVal if laserYVal > servoMin else servoMin
    if c == ord('k'):
      laserYVal += servoStep
      laserYVal = laserYVal if laserYVal < servoMax else servoMax
    if c == ord('j'):
      laserXVal -= servoStep
      laserXVal = laserXVal if laserXVal > servoMin else servoMin
    if c == ord('l'):
      laserXVal += servoStep
      laserXVal = laserXVal if laserXVal < servoMax else servoMax
    if c == ord('s'):
      cameraYVal -= servoStep
      cameraYVal = cameraYVal if cameraYVal > servoMin else servoMin
    if c == ord('w'):
      cameraYVal += servoStep
      cameraYVal = cameraYVal if cameraYVal < servoMax else servoMax
    if c == ord('a'):
      cameraXVal -= servoStep
      cameraXVal = cameraXVal if cameraXVal > servoMin else servoMin
    if c == ord('d'):
      cameraXVal += servoStep
      cameraXVal = cameraXVal if cameraXVal < servoMax else servoMax
    if c == ord('1'):
      cameraXVal = cameraS1[0]
      cameraYVal = cameraS1[1]
    if c == ord('2'):
      cameraXVal = cameraS2[0]
      cameraYVal = cameraS2[1]
    if c == ord('3'):
      cameraXVal = cameraS3[0]
      cameraYVal = cameraS3[1]
    if c == ord('4'):
      cameraXVal = cameraS4[0]
      cameraYVal = cameraS4[1]
    if c == ord('7'):
      laserXVal = laserS1[0]
      laserYVal = laserS1[1]
    if c == ord('8'):
      laserXVal = laserS2[0]
      laserYVal = laserS2[1]
    if c == ord('9'):
      laserXVal = laserS3[0]
      laserYVal = laserS3[1]
    if c == ord('0'):
      laserXVal = laserS4[0]
      laserYVal = laserS4[1]
    if c == ord('`'):
      c2 = stdscr.getch()
      if c2 == ord('1'):
        cameraS1 = (cameraXVal,cameraYVal)
      if c2 == ord('2'):
        cameraS2 = (cameraXVal,cameraYVal)
      if c2 == ord('3'):
        cameraS3 = (cameraXVal,cameraYVal)
      if c2 == ord('4'):
        cameraS4 = (cameraXVal,cameraYVal)
      if c2 == ord('7'):
        laserS1 = (laserXVal,laserYVal)
      if c2 == ord('8'):
        laserS2 = (laserXVal,laserYVal)
      if c2 == ord('9'):
        laserS3 = (laserXVal,laserYVal)
      if c2 == ord('0'):
        laserS4 = (laserXVal,laserYVal)

curses.nocbreak()
stdscr.keypad(0)
curses.echo()
curses.endwin()
#camera.close()

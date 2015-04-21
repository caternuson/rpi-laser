#!/usr/bin/python
#===========================================================================
# lasercam.py
#
# Class to represent the laser camera box.
#
# 2014-10-21
# Carter Nelson
#===========================================================================
import os
from Adafruit_Raspberry_Pi_Python_Code.Adafruit_PWM_Servo_Driver.Adafruit_PWM_Servo_Driver import PWM
import RPi.GPIO as GPIO
import picamera

class LaserCamBox():
    
    AMP_PIN             =   18      # GPIO pin for enabling audio amp
    OE_PIN              =   4       # GPIO pin for PWM enable(LOW)/disable(HIGH)
    LASER_PIN           =   16      # GPIO pin for laser on(HIGH)/off(LOW)
    CAM_LED_PIN         =   20      # white LED for camera
    LED1_PIN            =   26      # front status LED 1 - TOP : GREEN
    LED2_PIN            =   19      # front status LED 2 - MID : BLUE
    LED3_PIN            =   13      # front status LED 3 - BOT : GREEN
    LASER_X_CHAN        =   2       # PWM channel for laser X
    LASER_Y_CHAN        =   3       # PWM channel for laser Y
    CAMERA_X_CHAN       =   0       # PWM channel for camera X
    CAMERA_Y_CHAN       =   1       # PWM channel for camera Y   
    #SERVO_MIN           =   205     # minimum PWM value for servo
    #SERVO_MAX           =   410     # maximum PWM value for servo
    SERVO_MIN           =   130     # minimum PWM value for servo
    SERVO_MAX           =   600     # maximum PWM value for servo 
    DEF_STEP            =   10      # default servo step
    PWM_I2C             =   0x40    # i2c address for PWM controller
    PWM_FREQ            =   50      # frequency in Hz for PWM controller
    
    def __init__(self):
        # setup GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LaserCamBox.AMP_PIN,     GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(LaserCamBox.OE_PIN,      GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(LaserCamBox.LASER_PIN,   GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(LaserCamBox.CAM_LED_PIN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(LaserCamBox.LED1_PIN,    GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(LaserCamBox.LED2_PIN,    GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(LaserCamBox.LED3_PIN,    GPIO.OUT, initial=GPIO.LOW)
        
        # the PWM controller
        self.PWM = PWM(LaserCamBox.PWM_I2C, debug=False)
        self.PWM.setPWMFreq(LaserCamBox.PWM_FREQ)
        
        # the camera
        self.camera = picamera.PiCamera()
        
        # default values
        self.laserXVal = (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2
        self.laserYVal = (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2
        self.laserStep = self.DEF_STEP
        self.cameraXVal = (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2
        self.cameraYVal = (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2
        self.cameraStep = self.DEF_STEP
    
    def checkServoValues(self):
        self.laserXVal = self.laserXVal if (self.laserXVal>LaserCamBox.SERVO_MIN) else LaserCamBox.SERVO_MIN
        self.laserXVal = self.laserXVal if (self.laserXVal<LaserCamBox.SERVO_MAX) else LaserCamBox.SERVO_MAX
        self.laserYVal = self.laserYVal if (self.laserYVal>LaserCamBox.SERVO_MIN) else LaserCamBox.SERVO_MIN
        self.laserYVal = self.laserYVal if (self.laserYVal<LaserCamBox.SERVO_MAX) else LaserCamBox.SERVO_MAX
        self.cameraXVal = self.cameraXVal if (self.cameraXVal>LaserCamBox.SERVO_MIN) else LaserCamBox.SERVO_MIN
        self.cameraXVal = self.cameraXVal if (self.cameraXVal<LaserCamBox.SERVO_MAX) else LaserCamBox.SERVO_MAX
        self.cameraYVal = self.cameraYVal if (self.cameraYVal>LaserCamBox.SERVO_MIN) else LaserCamBox.SERVO_MIN
        self.cameraYVal = self.cameraYVal if (self.cameraYVal<LaserCamBox.SERVO_MAX) else LaserCamBox.SERVO_MAX
        
    def updatePWM(self):
        self.checkServoValues()
        self.PWM.setPWM(LaserCamBox.LASER_X_CHAN, 0, self.laserXVal)
        self.PWM.setPWM(LaserCamBox.LASER_Y_CHAN, 0, self.laserYVal)
        self.PWM.setPWM(LaserCamBox.CAMERA_X_CHAN, 0, self.cameraXVal)
        self.PWM.setPWM(LaserCamBox.CAMERA_Y_CHAN, 0, self.cameraYVal)
        
    def enablePWM(self, update=False):
        GPIO.output(LaserCamBox.OE_PIN, GPIO.LOW)
        if update:
            self.updatePWM()
        
    def disablePWM(self):
        GPIO.output(LaserCamBox.OE_PIN, GPIO.HIGH)
        
    def getPWMState(self):
        return GPIO.input(LaserCamBox.OE_PIN)
    
    def isPWMEnabled(self):
        state = GPIO.input(LaserCamBox.OE_PIN)
        if (0==state):
            return True
        elif (1==state):
            return False
        else:
            return None
     
    def cameraUp(self, step=None):
        if step==None:
            step=self.cameraStep
        self.cameraYVal -= step
        self.updatePWM()
        
    def cameraDown(self, step=None):
        if step==None:
            step=self.cameraStep
        self.cameraYVal += step
        self.updatePWM()
        
    def cameraLeft(self, step=None):
        if step==None:
            step=self.cameraStep
        self.cameraXVal -= step
        self.updatePWM()
        
    def cameraRight(self, step=None):
        if step==None:
            step=self.cameraStep
        self.cameraXVal += step
        self.updatePWM()
        
    def cameraHome(self):
        self.cameraSetPosition(
            ( (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2 ,
               LaserCamBox.SERVO_MIN )
            )
        
    def cameraSetPosition(self, position=None):
        if position==None:
            return
        if not isinstance(position, tuple):
            return
        if not len(position)==2:
            return
        self.cameraXVal=position[0]
        self.cameraYVal=position[1]
        self.updatePWM()
        
    def cameraGetPosition(self):
        return (self.cameraXVal, self.cameraYVal)
        
    def laserUp(self, step=None):
        if step==None:
            step=self.laserStep
        self.laserYVal += step
        self.updatePWM()
        
    def laserDown(self, step=None):
        if step==None:
            step=self.laserStep
        self.laserYVal -= step
        self.updatePWM()
        
    def laserLeft(self, step=None):
        if step==None:
            step=self.laserStep
        self.laserXVal -= step
        self.updatePWM()
        
    def laserRight(self, step=None):
        if step==None:
            step=self.laserStep
        self.laserXVal += step
        self.updatePWM()

    def laserHome(self):
        self.laserSetPosition(
            ( (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2 ,
               LaserCamBox.SERVO_MAX )
            )
        
    def laserSetPosition(self, position=None):
        if position==None:
            return
        if not isinstance(position, tuple):
            return
        if not len(position)==2:
            return
        self.laserXVal=position[0]
        self.laserYVal=position[1]
        self.updatePWM()
        
    def laserGetPosition(self):
        return (self.laserXVal, self.laserYVal)
        
    def laserOn(self):
        GPIO.output(LaserCamBox.LASER_PIN, GPIO.HIGH)
        
    def laserOff(self):
        GPIO.output(LaserCamBox.LASER_PIN, GPIO.LOW)
        
    def getLaserState(self):
        return GPIO.input(LaserCamBox.LASER_PIN)
    
    def cameraLEDOn(self):
        GPIO.output(LaserCamBox.CAM_LED_PIN, GPIO.HIGH)
        
    def cameraLEDOff(self):
        GPIO.output(LaserCamBox.CAM_LED_PIN, GPIO.LOW)
        
    def getCamLEDState(self):
        return GPIO.input(LaserCamBox.CAM_LED_PIN)
    
    def statusLEDOn(self, led):
        if   (led==1):
            GPIO.output(LaserCamBox.LED1_PIN, GPIO.HIGH)
        elif (led==2):
            GPIO.output(LaserCamBox.LED2_PIN, GPIO.HIGH)
        elif (led==3):
            GPIO.output(LaserCamBox.LED3_PIN, GPIO.HIGH)
        else:
            pass

    def statusLEDOff(self, led):
        if   (led==1):
            GPIO.output(LaserCamBox.LED1_PIN, GPIO.LOW)
        elif (led==2):
            GPIO.output(LaserCamBox.LED2_PIN, GPIO.LOW)
        elif (led==3):
            GPIO.output(LaserCamBox.LED3_PIN, GPIO.LOW)
        else:
            pass

    def statusLEDAllOff(self):
        self.statusLEDOff(1)
        self.statusLEDOff(2)
        self.statusLEDOff(3)
        
    def enableAudio(self):
        GPIO.output(LaserCamBox.AMP_PIN, GPIO.HIGH)
        
    def disableAudio(self):
        GPIO.output(LaserCamBox.AMP_PIN, GPIO.LOW)
        
    def speak(self, msg=None):
        self.enableAudio()
        opt = '-p 20 -s 100'  # espeak options
        if (msg==None):
            msg = 'who has my block rockin beets?'
        os.system('espeak '+opt+' "%s"' % msg)
        self.disableAudio()
       
#===========================================================
# MAIN
#===========================================================
if __name__ == '__main__':
    print "I'm just a class, not a program."

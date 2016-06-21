#===========================================================================
# lasercam.py
#
# Class to represent the laser camera box.
#
# 2014-10-21
# Carter Nelson
#===========================================================================
import os

import RPi.GPIO as GPIO
import picamera
from Adafruit_PCA9685 import PCA9685 as PWM

class LaserCamBox():
    """Provides hardware interface to laser/camera box."""
    
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
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LaserCamBox.AMP_PIN,     GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(LaserCamBox.OE_PIN,      GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(LaserCamBox.LASER_PIN,   GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(LaserCamBox.CAM_LED_PIN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(LaserCamBox.LED1_PIN,    GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(LaserCamBox.LED2_PIN,    GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(LaserCamBox.LED3_PIN,    GPIO.OUT, initial=GPIO.LOW)
        
        self.PWM = PWM(LaserCamBox.PWM_I2C)
        self.PWM.set_pwm_freq(LaserCamBox.PWM_FREQ)
        
        self.camera = picamera.PiCamera()
        
        self.laserXVal = (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2
        self.laserYVal = (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2
        self.laserStep = self.DEF_STEP
        self.cameraXVal = (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2
        self.cameraYVal = (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2
        self.cameraStep = self.DEF_STEP
    
    def checkServoValues(self):
        """Bound the PWM values to MIN and MAX."""
        self.laserXVal = self.laserXVal if (self.laserXVal>LaserCamBox.SERVO_MIN) else LaserCamBox.SERVO_MIN
        self.laserXVal = self.laserXVal if (self.laserXVal<LaserCamBox.SERVO_MAX) else LaserCamBox.SERVO_MAX
        self.laserYVal = self.laserYVal if (self.laserYVal>LaserCamBox.SERVO_MIN) else LaserCamBox.SERVO_MIN
        self.laserYVal = self.laserYVal if (self.laserYVal<LaserCamBox.SERVO_MAX) else LaserCamBox.SERVO_MAX
        self.cameraXVal = self.cameraXVal if (self.cameraXVal>LaserCamBox.SERVO_MIN) else LaserCamBox.SERVO_MIN
        self.cameraXVal = self.cameraXVal if (self.cameraXVal<LaserCamBox.SERVO_MAX) else LaserCamBox.SERVO_MAX
        self.cameraYVal = self.cameraYVal if (self.cameraYVal>LaserCamBox.SERVO_MIN) else LaserCamBox.SERVO_MIN
        self.cameraYVal = self.cameraYVal if (self.cameraYVal<LaserCamBox.SERVO_MAX) else LaserCamBox.SERVO_MAX
        
    def updatePWM(self):
        """Send current PWM values to PWM device."""
        self.checkServoValues()
        self.PWM.set_pwm(LaserCamBox.LASER_X_CHAN, 0, self.laserXVal)
        self.PWM.set_pwm(LaserCamBox.LASER_Y_CHAN, 0, self.laserYVal)
        self.PWM.set_pwm(LaserCamBox.CAMERA_X_CHAN, 0, self.cameraXVal)
        self.PWM.set_pwm(LaserCamBox.CAMERA_Y_CHAN, 0, self.cameraYVal)
        
    def enablePWM(self, update=False):
        """Enable power to the servos."""
        GPIO.output(LaserCamBox.OE_PIN, GPIO.LOW)
        if update:
            self.updatePWM()
        
    def disablePWM(self):
        """Disable power to the servos."""
        GPIO.output(LaserCamBox.OE_PIN, GPIO.HIGH)
        
    def getPWMState(self):
        """Return 0 if servos are enabled or 1 if disabled."""
        return GPIO.input(LaserCamBox.OE_PIN)
    
    def isPWMEnabled(self):
        """Return True if servos are enabled, otherwise False."""
        state = GPIO.input(LaserCamBox.OE_PIN)
        if (0==state):
            return True
        elif (1==state):
            return False
        else:
            return None
     
    def cameraUp(self, step=None):
        """Move the camera up the specified number of steps."""
        if step==None:
            step=self.cameraStep
        self.cameraYVal -= step
        self.updatePWM()
        
    def cameraDown(self, step=None):
        """Move the camera down the specified number of steps."""
        if step==None:
            step=self.cameraStep
        self.cameraYVal += step
        self.updatePWM()
        
    def cameraLeft(self, step=None):
        """Move the camera left the specified number of steps."""
        if step==None:
            step=self.cameraStep
        self.cameraXVal -= step
        self.updatePWM()
        
    def cameraRight(self, step=None):
        """Move the camera right the specified number of steps."""
        if step==None:
            step=self.cameraStep
        self.cameraXVal += step
        self.updatePWM()
        
    def cameraMoveRelative(self, amount=(0,0)):
        """Move the camera the amount specified in the tuple."""
        self.cameraXVal += amount[0]
        self.cameraYVal += amount[1]
        self.updatePWM()
        
    def cameraHome(self):
        """Move the camera to the home positon."""
        self.cameraSetPosition(
            ( (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2 ,
               LaserCamBox.SERVO_MIN )
            )
        
    def cameraSetPosition(self, position=None):
        """Move the camera to the absolute position."""
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
        """Return the current camera position."""
        return (self.cameraXVal, self.cameraYVal)
        
    def laserUp(self, step=None):
        """Move the laser up the specified number of steps."""
        if step==None:
            step=self.laserStep
        self.laserYVal += step
        self.updatePWM()
        
    def laserDown(self, step=None):
        """Move the laser down the specified number of steps."""
        if step==None:
            step=self.laserStep
        self.laserYVal -= step
        self.updatePWM()
        
    def laserLeft(self, step=None):
        """Move the laser left the specified number of steps."""
        if step==None:
            step=self.laserStep
        self.laserXVal -= step
        self.updatePWM()
        
    def laserRight(self, step=None):
        """Move the laser right the specified number of steps."""
        if step==None:
            step=self.laserStep
        self.laserXVal += step
        self.updatePWM()

    def laserHome(self):
        """Move the laser to the home positon."""
        self.laserSetPosition(
            ( (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2 ,
               LaserCamBox.SERVO_MAX )
            )
        
    def laserSetPosition(self, position=None):
        """Move the laser to the absolute position."""
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
        """Return the current laser position."""
        return (self.laserXVal, self.laserYVal)
        
    def laserOn(self):
        """Turn the laser on."""
        GPIO.output(LaserCamBox.LASER_PIN, GPIO.HIGH)
        
    def laserOff(self):
        """Turn the laser off."""
        GPIO.output(LaserCamBox.LASER_PIN, GPIO.LOW)
        
    def getLaserState(self):
        """Return current laser state."""
        return GPIO.input(LaserCamBox.LASER_PIN)
    
    def cameraLEDOn(self):
        """Turn camera LED on."""
        GPIO.output(LaserCamBox.CAM_LED_PIN, GPIO.HIGH)
        
    def cameraLEDOff(self):
        """Turn camera LED off."""
        GPIO.output(LaserCamBox.CAM_LED_PIN, GPIO.LOW)
        
    def getCamLEDState(self):
        """Return current LED state."""
        return GPIO.input(LaserCamBox.CAM_LED_PIN)
    
    def statusLEDOn(self, led):
        """Turn on the specified front panel status LED."""
        if   (led==1):
            GPIO.output(LaserCamBox.LED1_PIN, GPIO.HIGH)
        elif (led==2):
            GPIO.output(LaserCamBox.LED2_PIN, GPIO.HIGH)
        elif (led==3):
            GPIO.output(LaserCamBox.LED3_PIN, GPIO.HIGH)
        else:
            pass

    def statusLEDOff(self, led):
        """Turn off the specified front panel status LED."""
        if   (led==1):
            GPIO.output(LaserCamBox.LED1_PIN, GPIO.LOW)
        elif (led==2):
            GPIO.output(LaserCamBox.LED2_PIN, GPIO.LOW)
        elif (led==3):
            GPIO.output(LaserCamBox.LED3_PIN, GPIO.LOW)
        else:
            pass

    def statusLEDAllOff(self):
        """Turn off all of the front panel status LEDs."""
        self.statusLEDOff(1)
        self.statusLEDOff(2)
        self.statusLEDOff(3)
        
    def enableAudio(self):
        """Enable the audio amplifier."""
        GPIO.output(LaserCamBox.AMP_PIN, GPIO.HIGH)
        
    def disableAudio(self):
        """Disable the audio amplifier."""
        GPIO.output(LaserCamBox.AMP_PIN, GPIO.LOW)
        
    def speak(self, msg=None):
        """Output the supplied message on the speaker."""
        self.enableAudio()
        opt = '-p 45 -s 165'  # espeak options
        if (msg==None):
            msg = 'who has my block rockin beets?'
        os.system('espeak '+opt+' "%s"' % msg)
        self.disableAudio()
       
#===========================================================
# MAIN
#===========================================================
if __name__ == '__main__':
    print "I'm just a class, not a program."

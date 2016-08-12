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
from Adafruit_PCA9685 import PCA9685 as PWM

import picamera
import mjpegger

class LaserCamBox():
    """Provides hardware interface to laser/camera box."""
    
    AMP_PIN             =   18      # GPIO pin for enabling audio amp
    OE_PIN              =   4       # GPIO pin for PWM enable(LOW)/disable(HIGH)
    LASER_PIN           =   16      # GPIO pin for laser on(HIGH)/off(LOW)
    CAM_LED_PIN         =   20      # white LED for camera
    TOP_BTN_PIN         =   23      # GPIO pin for button on top
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
        GPIO.setup(LaserCamBox.TOP_BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(LaserCamBox.TOP_BTN_PIN,
                              GPIO.RISING,
                              bouncetime=500,
                              callback=self.btn_callback)
        
        self.top_btn_func = None
        
        self.PWM = PWM(LaserCamBox.PWM_I2C)
        self.PWM.set_pwm_freq(LaserCamBox.PWM_FREQ)
        
        #self.camera = picamera.PiCamera(sensor_mode=5)
        self.camera = None
        self._mjpegger = None        
        
        self.laserXVal = (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2
        self.laserYVal = (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2
        self.laserStep = self.DEF_STEP
        self.cameraXVal = (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2
        self.cameraYVal = (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2
        self.cameraStep = self.DEF_STEP
    
    def register_btn_func(self, f):
        self.top_btn_func = f
        
    def btn_callback(self, chan):
        if chan == LaserCamBox.TOP_BTN_PIN:
            if not self.top_btn_func == None:
                self.top_btn_func()
        
    def check_servo_values(self):
        """Bound the PWM values to MIN and MAX."""
        self.laserXVal = self.laserXVal if (self.laserXVal>LaserCamBox.SERVO_MIN) else LaserCamBox.SERVO_MIN
        self.laserXVal = self.laserXVal if (self.laserXVal<LaserCamBox.SERVO_MAX) else LaserCamBox.SERVO_MAX
        self.laserYVal = self.laserYVal if (self.laserYVal>LaserCamBox.SERVO_MIN) else LaserCamBox.SERVO_MIN
        self.laserYVal = self.laserYVal if (self.laserYVal<LaserCamBox.SERVO_MAX) else LaserCamBox.SERVO_MAX
        self.cameraXVal = self.cameraXVal if (self.cameraXVal>LaserCamBox.SERVO_MIN) else LaserCamBox.SERVO_MIN
        self.cameraXVal = self.cameraXVal if (self.cameraXVal<LaserCamBox.SERVO_MAX) else LaserCamBox.SERVO_MAX
        self.cameraYVal = self.cameraYVal if (self.cameraYVal>LaserCamBox.SERVO_MIN) else LaserCamBox.SERVO_MIN
        self.cameraYVal = self.cameraYVal if (self.cameraYVal<LaserCamBox.SERVO_MAX) else LaserCamBox.SERVO_MAX
        
    def update_pwm(self):
        """Send current PWM values to PWM device."""
        self.check_servo_values()
        self.PWM.set_pwm(LaserCamBox.LASER_X_CHAN, 0, self.laserXVal)
        self.PWM.set_pwm(LaserCamBox.LASER_Y_CHAN, 0, self.laserYVal)
        self.PWM.set_pwm(LaserCamBox.CAMERA_X_CHAN, 0, self.cameraXVal)
        self.PWM.set_pwm(LaserCamBox.CAMERA_Y_CHAN, 0, self.cameraYVal)
        
    def enable_pwm(self, update=False):
        """Enable power to the servos."""
        GPIO.output(LaserCamBox.OE_PIN, GPIO.LOW)
        if update:
            self.update_pwm()
        
    def disable_pwm(self):
        """Disable power to the servos."""
        GPIO.output(LaserCamBox.OE_PIN, GPIO.HIGH)
        
    def get_pwm_state(self):
        """Return 0 if servos are enabled or 1 if disabled."""
        return GPIO.input(LaserCamBox.OE_PIN)
    
    def is_pwm_enabled(self):
        """Return True if servos are enabled, otherwise False."""
        state = GPIO.input(LaserCamBox.OE_PIN)
        if (0==state):
            return True
        elif (1==state):
            return False
        else:
            return None
     
    def camera_up(self, step=None):
        """Move the camera up the specified number of steps."""
        if step==None:
            step=self.cameraStep
        self.cameraYVal -= step
        self.update_pwm()
        
    def camera_down(self, step=None):
        """Move the camera down the specified number of steps."""
        if step==None:
            step=self.cameraStep
        self.cameraYVal += step
        self.update_pwm()
        
    def camera_left(self, step=None):
        """Move the camera left the specified number of steps."""
        if step==None:
            step=self.cameraStep
        self.cameraXVal -= step
        self.update_pwm()
        
    def camera_right(self, step=None):
        """Move the camera right the specified number of steps."""
        if step==None:
            step=self.cameraStep
        self.cameraXVal += step
        self.update_pwm()
        
    def camera_move_relative(self, amount=(0,0)):
        """Move the camera the amount specified in the tuple."""
        self.cameraXVal += amount[0]
        self.cameraYVal += amount[1]
        self.update_pwm()
        
    def camera_home(self):
        """Move the camera to the home positon."""
        self.camera_set_position(
            ( (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2 ,
               LaserCamBox.SERVO_MIN )
            )
        
    def camera_set_position(self, position=None):
        """Move the camera to the absolute position."""
        if position==None:
            return
        if not isinstance(position, tuple):
            return
        if not len(position)==2:
            return
        self.cameraXVal=position[0]
        self.cameraYVal=position[1]
        self.update_pwm()
        
    def mjpegstream_start(self, port=8081, resize=(640,360)):
        """Start thread to serve MJPEG stream on specified port."""
        if not self._mjpegger == None:
            return
        camera = picamera.PiCamera(sensor_mode=5)
        camera.hflip = True
        camera.vflip = True
        kwargs = {'camera':camera, 'port':port, 'resize':resize}
        self._mjpegger = mjpegger.MJPEGThread(kwargs=kwargs)
        self._mjpegger.start()
        while not self._mjpegger.streamRunning:
            pass
    
    def mjpegstream_stop(self, ):
        """Stop the MJPEG stream, if running."""
        if not self._mjpegger == None:
            if self._mjpegger.is_alive():
                self._mjpegger.stop()
            self._mjpegger = None
                
    def mjpgstream_is_alive(self, ):
        """Return True if stream is running, False otherwise."""
        if self._mjpegger == None:
            return False
        else:
            return self._mjpegger.is_alive()
        
    def camera_get_position(self):
        """Return the current camera position."""
        return (self.cameraXVal, self.cameraYVal)
        
    def laser_up(self, step=None):
        """Move the laser up the specified number of steps."""
        if step==None:
            step=self.laserStep
        self.laserYVal += step
        self.update_pwm()
        
    def laser_down(self, step=None):
        """Move the laser down the specified number of steps."""
        if step==None:
            step=self.laserStep
        self.laserYVal -= step
        self.update_pwm()
        
    def laser_left(self, step=None):
        """Move the laser left the specified number of steps."""
        if step==None:
            step=self.laserStep
        self.laserXVal -= step
        self.update_pwm()
        
    def laser_right(self, step=None):
        """Move the laser right the specified number of steps."""
        if step==None:
            step=self.laserStep
        self.laserXVal += step
        self.update_pwm()

    def laser_home(self):
        """Move the laser to the home positon."""
        self.laserSetPosition(
            ( (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2 ,
               LaserCamBox.SERVO_MAX )
            )
        
    def laser_set_position(self, position=None):
        """Move the laser to the absolute position."""
        if position==None:
            return
        if not isinstance(position, tuple):
            return
        if not len(position)==2:
            return
        self.laserXVal=position[0]
        self.laserYVal=position[1]
        self.update_pwm()
        
    def laser_get_position(self):
        """Return the current laser position."""
        return (self.laserXVal, self.laserYVal)
        
    def laser_on(self):
        """Turn the laser on."""
        GPIO.output(LaserCamBox.LASER_PIN, GPIO.HIGH)
        
    def laser_off(self):
        """Turn the laser off."""
        GPIO.output(LaserCamBox.LASER_PIN, GPIO.LOW)
        
    def get_laser_state(self):
        """Return current laser state."""
        return GPIO.input(LaserCamBox.LASER_PIN)
    
    def camera_led_on(self):
        """Turn camera LED on."""
        GPIO.output(LaserCamBox.CAM_LED_PIN, GPIO.HIGH)
        
    def camera_led_off(self):
        """Turn camera LED off."""
        GPIO.output(LaserCamBox.CAM_LED_PIN, GPIO.LOW)
        
    def get_camera_led_state(self):
        """Return current LED state."""
        return GPIO.input(LaserCamBox.CAM_LED_PIN)
    
    def status_led_on(self, led):
        """Turn on the specified front panel status LED."""
        if   (led==1):
            GPIO.output(LaserCamBox.LED1_PIN, GPIO.HIGH)
        elif (led==2):
            GPIO.output(LaserCamBox.LED2_PIN, GPIO.HIGH)
        elif (led==3):
            GPIO.output(LaserCamBox.LED3_PIN, GPIO.HIGH)
        else:
            pass

    def status_led_off(self, led):
        """Turn off the specified front panel status LED."""
        if   (led==1):
            GPIO.output(LaserCamBox.LED1_PIN, GPIO.LOW)
        elif (led==2):
            GPIO.output(LaserCamBox.LED2_PIN, GPIO.LOW)
        elif (led==3):
            GPIO.output(LaserCamBox.LED3_PIN, GPIO.LOW)
        else:
            pass

    def status_led_all_off(self):
        """Turn off all of the front panel status LEDs."""
        self.statusLEDOff(1)
        self.statusLEDOff(2)
        self.statusLEDOff(3)
        
    def enable_audio(self):
        """Enable the audio amplifier."""
        GPIO.output(LaserCamBox.AMP_PIN, GPIO.HIGH)
        
    def disable_audio(self):
        """Disable the audio amplifier."""
        GPIO.output(LaserCamBox.AMP_PIN, GPIO.LOW)
        
    def speak(self, msg=None):
        """Output the supplied message on the speaker."""
        self.enable_audio()
        opt = '-p 45 -s 165'  # espeak options
        if (msg==None):
            msg = 'who has my block rockin beets?'
        os.system('espeak '+opt+' "%s"' % msg)
        self.disable_audio()
       
#===========================================================
# MAIN
#===========================================================
if __name__ == '__main__':
    print "I'm just a class, not a program."

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

    TOP_BTN_PIN         =   23      # GPIO pin for button on top    
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
    CAMERA_HOME         =   (290,100)
    LASER_HOME          =   (320,490)
    DEF_STEP            =   10      # default servo step
    PWM_I2C             =   0x40    # i2c address for PWM controller
    PWM_FREQ            =   50      # frequency in Hz for PWM controller
    
    def __init__(self, ):
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
                                GPIO.FALLING,
                                bouncetime=500,
                                callback=self.btn_callback)
        
        self.top_btn_func = None
        
        self.PWM = PWM(LaserCamBox.PWM_I2C)
        self.PWM.set_pwm_freq(LaserCamBox.PWM_FREQ)
        
        self.camera = None
        self._mjpegger = None        
        
        self.laser_x = (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2
        self.laser_y = (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2
        self.laser_step = self.DEF_STEP
        self.camera_x = (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2
        self.camera_y = (LaserCamBox.SERVO_MIN + LaserCamBox.SERVO_MAX)/2
        self.camera_step = self.DEF_STEP
    
    def register_btn_func(self, func):
        self.top_btn_func = func
        
    def btn_callback(self, chan):
        if chan == LaserCamBox.TOP_BTN_PIN:
            if not self.top_btn_func == None:
                self.top_btn_func()
        
    def _bound(self, val, val_min, val_max):
        val = val if val > val_min else val_min
        val = val if val < val_max else val_max
        return val
    
    def check_servo_values(self, ):
        """Bound the PWM values to MIN and MAX."""
        self.laser_x = self._bound(self.laser_x, LaserCamBox.SERVO_MIN, LaserCamBox.SERVO_MAX)
        self.laser_y = self._bound(self.laser_y, LaserCamBox.SERVO_MIN, LaserCamBox.SERVO_MAX)
        self.camera_x = self._bound(self.camera_x, LaserCamBox.SERVO_MIN, LaserCamBox.SERVO_MAX)
        self.camera_y = self._bound(self.camera_y, LaserCamBox.SERVO_MIN, LaserCamBox.SERVO_MAX)
        '''
        self.laser_x = self.laser_x if (self.laser_x>LaserCamBox.SERVO_MIN) else LaserCamBox.SERVO_MIN
        self.laser_x = self.laser_x if (self.laser_x<LaserCamBox.SERVO_MAX) else LaserCamBox.SERVO_MAX
        self.laser_y = self.laser_y if (self.laser_y>LaserCamBox.SERVO_MIN) else LaserCamBox.SERVO_MIN
        self.laser_y = self.laser_y if (self.laser_y<LaserCamBox.SERVO_MAX) else LaserCamBox.SERVO_MAX
        self.camera_x = self.camera_x if (self.camera_x>LaserCamBox.SERVO_MIN) else LaserCamBox.SERVO_MIN
        self.camera_x = self.camera_x if (self.camera_x<LaserCamBox.SERVO_MAX) else LaserCamBox.SERVO_MAX
        self.camera_y = self.camera_y if (self.camera_y>LaserCamBox.SERVO_MIN) else LaserCamBox.SERVO_MIN
        self.camera_y = self.camera_y if (self.camera_y<LaserCamBox.SERVO_MAX) else LaserCamBox.SERVO_MAX
        '''
        
    def update_pwm(self, ):
        """Send current PWM values to PWM device."""
        self.check_servo_values()
        self.PWM.set_pwm(LaserCamBox.LASER_X_CHAN, 0, self.laser_x)
        self.PWM.set_pwm(LaserCamBox.LASER_Y_CHAN, 0, self.laser_y)
        self.PWM.set_pwm(LaserCamBox.CAMERA_X_CHAN, 0, self.camera_x)
        self.PWM.set_pwm(LaserCamBox.CAMERA_Y_CHAN, 0, self.camera_y)
        
    def enable_pwm(self, update=False):
        """Enable power to the servos."""
        GPIO.output(LaserCamBox.OE_PIN, GPIO.LOW)
        if update:
            self.update_pwm()
        
    def disable_pwm(self, ):
        """Disable power to the servos."""
        GPIO.output(LaserCamBox.OE_PIN, GPIO.HIGH)
        
    def get_pwm_state(self, ):
        """Return 0 if servos are enabled or 1 if disabled."""
        return GPIO.input(LaserCamBox.OE_PIN)
    
    def is_pwm_enabled(self, ):
        """Return True if servos are enabled, otherwise False."""
        state = GPIO.input(LaserCamBox.OE_PIN)
        if state == 0:
            return True
        elif state == 1:
            return False
        else:
            return None
     
    def camera_up(self, step=None):
        """Move the camera up the specified number of steps."""
        if step == None:
            step = self.camera_step
        self.camera_y -= step
        self.update_pwm()
        
    def camera_down(self, step=None):
        """Move the camera down the specified number of steps."""
        if step == None:
            step = self.camera_step
        self.camera_y += step
        self.update_pwm()
        
    def camera_left(self, step=None):
        """Move the camera left the specified number of steps."""
        if step == None:
            step = self.camera_step
        self.camera_x -= step
        self.update_pwm()
        
    def camera_right(self, step=None):
        """Move the camera right the specified number of steps."""
        if step == None:
            step = self.camera_step
        self.camera_x += step
        self.update_pwm()
        
    def camera_move_relative(self, amount):
        """Move the camera the amount specified in the tuple."""
        self.camera_x += amount[0]
        self.camera_y += amount[1]
        self.update_pwm()
        
    def camera_home(self, ):
        """Move the camera to the home positon."""
        self.camera_set_position(LaserCamBox.CAMERA_HOME)
        
    def camera_set_position(self, position):
        """Move the camera to the absolute position."""
        if not isinstance(position, tuple):
            return
        if not len(position) == 2:
            return
        self.camera_x = position[0]
        self.camera_y = position[1]
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
        
    def camera_get_position(self, ):
        """Return the current camera position."""
        return (self.camera_x, self.camera_y)
        
    def laser_up(self, step=None):
        """Move the laser up the specified number of steps."""
        if step == None:
            step = self.laser_step
        self.laser_y += step
        self.update_pwm()
        
    def laser_down(self, step=None):
        """Move the laser down the specified number of steps."""
        if step == None:
            step = self.laser_step
        self.laser_y -= step
        self.update_pwm()
        
    def laser_left(self, step=None):
        """Move the laser left the specified number of steps."""
        if step == None:
            step = self.laser_step
        self.laser_x -= step
        self.update_pwm()
        
    def laser_right(self, step=None):
        """Move the laser right the specified number of steps."""
        if step == None:
            step = self.laser_step
        self.laser_x += step
        self.update_pwm()

    def laser_home(self, ):
        """Move the laser to the home positon."""
        self.laser_set_position(LaserCamBox.LASER_HOME)
        
    def laser_set_position(self, position):
        """Move the laser to the absolute position."""
        if not isinstance(position, tuple):
            return
        if not len(position) == 2:
            return
        self.laser_x = position[0]
        self.laser_y = position[1]
        self.update_pwm()
        
    def laser_get_position(self, ):
        """Return the current laser position."""
        return (self.laser_x, self.laser_y)
        
    def laser_on(self, ):
        """Turn the laser on."""
        GPIO.output(LaserCamBox.LASER_PIN, GPIO.HIGH)
        
    def laser_off(self, ):
        """Turn the laser off."""
        GPIO.output(LaserCamBox.LASER_PIN, GPIO.LOW)
        
    def get_laser_state(self, ):
        """Return current laser state."""
        return GPIO.input(LaserCamBox.LASER_PIN)
    
    def camera_led_on(self, ):
        """Turn camera LED on."""
        GPIO.output(LaserCamBox.CAM_LED_PIN, GPIO.HIGH)
        
    def camera_led_off(self, ):
        """Turn camera LED off."""
        GPIO.output(LaserCamBox.CAM_LED_PIN, GPIO.LOW)
        
    def get_camera_led_state(self, ):
        """Return current LED state."""
        return GPIO.input(LaserCamBox.CAM_LED_PIN)
    
    def status_led_on(self, led):
        """Turn on the specified front panel status LED."""
        if led == 1:
            GPIO.output(LaserCamBox.LED1_PIN, GPIO.HIGH)
        elif led == 2:
            GPIO.output(LaserCamBox.LED2_PIN, GPIO.HIGH)
        elif led == 3:
            GPIO.output(LaserCamBox.LED3_PIN, GPIO.HIGH)
        else:
            pass

    def status_led_off(self, led):
        """Turn off the specified front panel status LED."""
        if led == 1:
            GPIO.output(LaserCamBox.LED1_PIN, GPIO.LOW)
        elif led == 2:
            GPIO.output(LaserCamBox.LED2_PIN, GPIO.LOW)
        elif led == 3:
            GPIO.output(LaserCamBox.LED3_PIN, GPIO.LOW)
        else:
            pass

    def status_led_all_off(self, ):
        """Turn off all of the front panel status LEDs."""
        self.statusLEDOff(1)
        self.statusLEDOff(2)
        self.statusLEDOff(3)
        
    def enable_audio(self, ):
        """Enable the audio amplifier."""
        GPIO.output(LaserCamBox.AMP_PIN, GPIO.HIGH)
        
    def disable_audio(self, ):
        """Disable the audio amplifier."""
        GPIO.output(LaserCamBox.AMP_PIN, GPIO.LOW)
        
    def speak(self, msg="hello world"):
        """Output the supplied message on the speaker."""
        self.enable_audio()
        opt = '-p 45 -s 165'  # espeak options
        os.system('espeak '+opt+' "%s"' % msg)
        self.disable_audio()
       
#===========================================================
# MAIN
#===========================================================
if __name__ == '__main__':
    print "I'm just a class, not a program."

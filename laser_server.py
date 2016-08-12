#!/usr/bin/env python
#===========================================================================
# laser_server.py
#
# Web server to run on laser camera box.
#
# 2014-10-22
# Carter Nelson
#===========================================================================
import time
import pickle
import os.path

import tornado.httpserver
import tornado.websocket
import tornado.web
import tornado.ioloop

import lasercam

# location storeage pickle file
LOCATIONS_PKL = '/home/pi/rpi-laser/locations.pkl'

# define port server will listen to
PORT = 8080

# a single global instance to be used by the server
theBox = lasercam.LaserCamBox()

# status LEDs for server
STREAM_STATUS_LED   = 1     # blinks if camera stream is running
CONNECT_STATUS_LED  = 1     # on if someone is accessing webpage
SERVER_STATUS_LED   = 3     # on if server is running

# dictionary of phrases for audio output
sound = {}
sound['S1'] = 'hey cat!'
sound['S2'] = 'meow meow meow'
sound['S3'] = 'kitty! kitty! kitty!'
sound['S4'] = 'shall we play a game?'
sound['S5'] = 'sound 5'
sound['S6'] = 'sound 6'
sound['S7'] = 'sound 7'
sound['S8'] = 'sound 8'
sound['S9'] = 'sound 9'

#-------------------------------------------------------------------------
# Tornado Server Setup
#-------------------------------------------------------------------------   
class KillHandler(tornado.web.RequestHandler):
    """RequestHandler that stops the server."""
    
    def get(self):
        print "KILL Request from {}".format(self.request.remote_ip)
        tornado.ioloop.IOLoop.instance().stop()

class LaserCamHandler(tornado.web.RequestHandler):
    """RequestHandlder for main page."""
    
    def get(self):
        print "GET Request from {}".format(self.request.remote_ip)
        self.render("lasercam.html")
        
class WebSocketHandler(tornado.websocket.WebSocketHandler):
    """WebSocketHandler for web socket communications."""
    
    def initialize(self, lasercambox):
        self.lasercambox = lasercambox
        self.lasercambox.enable_pwm(update=True)

        self.cameraLocation = [None,None,None,None,None]
        self.laserLocation = [None,None,None,None,None]
        self.__loadLocations()
        self.storeCamera = False
        self.storeLaser = False
        self.camera_loop = None
        
        self._stream_LED_state = 0
        self._blink_rate = 1
        self._blink_count = 0
            
    def open(self):
        print "WS open from {}".format(self.request.remote_ip)
        self.lasercambox.status_led_on(CONNECT_STATUS_LED)
    
    def on_close(self):
        print "WS close"
        self.__shutDown()
    
    def on_message(self, message):
        print "WS message: {} = ".format(message),
        MSG = message.strip().upper()
        if (MSG=='LU'):
            print "laser up"
            self.lasercambox.laser_up()
        elif (MSG=='LD'):
            print "laser down"
            self.lasercambox.laser_down()
        elif (MSG=='LL'):
            print "laser left"
            self.lasercambox.laser_left()
        elif (MSG=='LR'):
            print "laser right"
            self.lasercambox.laser_right()
        elif (MSG=='LN'):
            print "laser on"
            self.lasercambox.laser_on()
        elif (MSG=='LO'):
            print "laser off"
            self.lasercambox.laser_off()
        elif (MSG=='L!'):
            print "laser storage armed"
            self.storeLaser=True
        elif (MSG=='L1'):
            self.__laserPreset(0)
        elif (MSG=='L2'):
            self.__laserPreset(1)
        elif (MSG=='L3'):
            self.__laserPreset(2)
        elif (MSG=='L4'):
            self.__laserPreset(3)
        elif (MSG=='L5'):
            self.__laserPreset(4)
        elif (MSG=='CU'):
            print "camera up"
            self.lasercambox.camera_up()
        elif (MSG=='CD'):
            print "camera down"
            self.lasercambox.camera_down()
        elif (MSG=='CL'):
            print "camera left"
            self.lasercambox.camera_left()
        elif (MSG=='CR'):
            print "camera right"
            self.lasercambox.camera_right()
        elif (MSG=='CN'):
            print "camera start stream"
            self.__startStream()
        elif (MSG=='CO'):
            print "camera stop stream"
            self.__stopStream()
        elif (MSG=='C!'):
            print "camera storage armed"
            self.storeCamera=True
        elif (MSG=='C1'):
            self.__cameraPreset(0)
        elif (MSG=='C2'):
            self.__cameraPreset(1)
        elif (MSG=='C3'):
            self.__cameraPreset(2)
        elif (MSG=='C4'):
            self.__cameraPreset(3)
        elif (MSG=='C5'):
            self.__cameraPreset(4)
        elif (MSG=='QN'):
            print "camera LED on"
            self.lasercambox.camera_led_on()
        elif (MSG=='QO'):
            print "camera LED off"
            self.lasercambox.camera_led_off()
        elif (MSG=='SN'):
            print "servos on"
            self.lasercambox.enable_pwm()
        elif (MSG=='SO'):
            print "servos off"
            self.lasercambox.disable_pwm()
        elif (MSG.startswith("CM")):
            x = int(float(MSG.split(":")[1]))
            y = int(float(MSG.split(":")[2]))
            self.lasercambox.camera_move_relative((x,y))           
            print "camera relative move %i, %i" % (x,y)
        elif (MSG in ['S1','S2','S3','S4','S5','S6','S7','S8','S9']):
            print "playing sound"
            self.lasercambox.speak(sound[MSG])
        else:
            print "unknown command"
              
    def __startStream(self):
        self.lasercambox.mjpegstream_start()
        addr = self.request.host.partition(":")[0]
        self.write_message("http://" + addr + ":8081/")
        
    def __stopStream(self):
        self.write_message("")
        self.lasercambox.mjpegstream_stop()
        
    def __cameraPreset(self, position=None):
        if position==None:
            return
        if self.storeCamera:
            print "storing camera location %i" % (position+1)
            self.cameraLocation[position]=(self.lasercambox.camera_get_position())
            self.storeCamera = False
        else:
            print "goto camera store %i" % (position+1)
            self.lasercambox.camera_set_position(self.cameraLocation[position])
            
    def __laserPreset(self, position=None):
        if position==None:
            return
        if self.storeLaser:
            print "storing laser location %i" % (position+1)
            self.laserLocation[position]=(self.lasercambox.laser_get_position())
            self.storeLaser = False
        else:
            print "goto laser store %i" % (position+1)
            self.lasercambox.laser_set_position(self.laserLocation[position])
            
    def __loadLocations(self):
        if os.path.isfile(LOCATIONS_PKL):
            with open(LOCATIONS_PKL,'rb') as PKL:
                temp = pickle.load(PKL)
            self.cameraLocation = temp[0]
            self.laserLocation = temp[1]
            print "locations loaded"
            
    def __saveLocations(self):
        temp = [self.cameraLocation,self.laserLocation]
        with open(LOCATIONS_PKL,'wb') as PKL:
            pickle.dump(temp, PKL)
        print "locations saved"
                
    def __shutDown(self):
        self.lasercambox.mjpegstream_stop()
        self.lasercambox.enable_pwn()
        self.lasercambox.camera_home()
        self.lasercambox.laser_home()  
        self.lasercambox.camera_led_ff()
        self.lasercambox.laser_off()
        self.lasercambox.status_led_off(CONNECT_STATUS_LED)
        self.__saveLocations()
        time.sleep(1) # give servos time to move
        self.lasercambox.disable_pwm()
        
    def __toggle_stream_LED(self):
        self._blink_count += 1
        if (self._blink_count >= self._blink_rate):
            self._blink_count = 0
            if (self._stream_LED_state == 0):
                self._stream_LED_state = 1
                self.lasercambox.status_led_on(STREAM_STATUS_LED)
            else:
                self._stream_LED_state = 0
                self.lasercambox.status_led_off(STREAM_STATUS_LED)

class MainServerApp(tornado.web.Application):
    """Main Server application."""
    
    def __init__(self):
        handlers = [
            (r"/kill",              KillHandler),
            (r"/lasercam",          LaserCamHandler),
            (r"/ws",                WebSocketHandler, dict(lasercambox=theBox)),             
        ]
        
        settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        }
        
        tornado.web.Application.__init__(self, handlers, **settings)

#===========================================================
# MAIN
#===========================================================
if __name__ == '__main__':
    tornado.httpserver.HTTPServer(MainServerApp()).listen(PORT)
    print "Server started on port {}...".format(PORT)
    theBox.status_led_on(SERVER_STATUS_LED)
    tornado.ioloop.IOLoop.instance().start()
    theBox.status_led_off(SERVER_STATUS_LED)
    print "i guess we're done then."       
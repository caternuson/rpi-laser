#!/usr/bin/python
#===========================================================================
# laser_server.py
#
# Web server to run on laser camera box.
#  * Uses Tornado framework (http://www.tornadoweb.org/en/stable)
#  * WebSockets, as supported in Tornado, are used to send commands
#  * WebSockets also used to send camera stream
#  * JavaScript (found in .html file) ties it togeter
#
# 2014-10-22
# Carter Nelson
#===========================================================================
import lasercam

import cStringIO as io
import base64

import tornado.httpserver
import tornado.websocket
import tornado.web
import tornado.ioloop

import time
import pickle
import os.path
# location storeage pickle file
LOCATIONS_PKL = 'locations.pkl'

# define port server will listen to
PORT = 8008

# a single global instance to be used by the server
theBox = lasercam.LaserCamBox()

# dictionary of phrases for audio output
sound = {}
sound['S1'] = 'hey cat!'
sound['S2'] = 'kitty! kitty! kitty!'
sound['S3'] = 'meeyow'
sound['S4'] = 'hey, wake up'
sound['S5'] = 'heres johhny'
sound['S6'] = 'ha ha ha space cadet'
sound['S7'] = 'intruder alert! intruder alert! intruder alert!'
sound['S8'] = 'is any body there?'
sound['S9'] = 'hello?'

#-------------------------------------------------------------------------
# Tornado Server Setup
#-------------------------------------------------------------------------   
# this will handle HTTP requests
class KillHandler(tornado.web.RequestHandler):
    def get(self):
        print "KILL Request from {}".format(self.request.remote_ip)
        tornado.ioloop.IOLoop.instance().stop()

# this will handle HTTP requests
class LaserCamHandler(tornado.web.RequestHandler):
    def get(self):
        print "GET Request from {}".format(self.request.remote_ip)
        self.render("lasercam.html")
        
# this will handle WebSockets requests
class WebSocketHandler(tornado.websocket.WebSocketHandler):
    
    def initialize(self, lasercambox):
        self.lasercambox = lasercambox
        self.lasercambox.enablePWM(update=True)
        self.lasercambox.camera.hflip=True
        self.lasercambox.camera.vflip=True
        
        self.STREAM_STATUS_LED = 1

        self.cameraLocation = [None,None,None,None,None]
        self.laserLocation = [None,None,None,None,None]
        self.__loadLocations__()
        self.storeCamera = False
        self.storeLaser = False
        self.camera_loop = None
       
    def open(self):
        print "WS open from {}".format(self.request.remote_ip)
    
    def on_close(self):
        print "WS close"
        self.__shutDown__()
    
    def on_message(self, message):
        print "WS message: {} = ".format(message),
        MSG = message.strip().upper()
        if (MSG=='LU'):
            print "laser up"
            self.lasercambox.laserUp()
        elif (MSG=='LD'):
            print "laser down"
            self.lasercambox.laserDown()
        elif (MSG=='LL'):
            print "laser left"
            self.lasercambox.laserLeft()
        elif (MSG=='LR'):
            print "laser right"
            self.lasercambox.laserRight()
        elif (MSG=='LN'):
            print "laser on"
            self.lasercambox.laserOn()
        elif (MSG=='LO'):
            print "laser off"
            self.lasercambox.laserOff()
        elif (MSG=='L!'):
            print "laser storage armed"
            self.storeLaser=True
        elif (MSG=='L1'):
            self.__laserPreset__(0)
        elif (MSG=='L2'):
            self.__laserPreset__(1)
        elif (MSG=='L3'):
            self.__laserPreset__(2)
        elif (MSG=='L4'):
            self.__laserPreset__(3)
        elif (MSG=='L5'):
            self.__laserPreset__(4)
        elif (MSG=='CU'):
            print "camera up"
            self.lasercambox.cameraUp()
        elif (MSG=='CD'):
            print "camera down"
            self.lasercambox.cameraDown()
        elif (MSG=='CL'):
            print "camera left"
            self.lasercambox.cameraLeft()
        elif (MSG=='CR'):
            print "camera right"
            self.lasercambox.cameraRight()
        elif (MSG=='CN'):
            print "camera start stream"
            self.__startStream__()
        elif (MSG=='CO'):
            print "camera stop stream"
            self.__stopStream__()
        elif (MSG=='C!'):
            print "camera storage armed"
            self.storeCamera=True
        elif (MSG=='C1'):
            self.__cameraPreset__(0)
        elif (MSG=='C2'):
            self.__cameraPreset__(1)
        elif (MSG=='C3'):
            self.__cameraPreset__(2)
        elif (MSG=='C4'):
            self.__cameraPreset__(3)
        elif (MSG=='C5'):
            self.__cameraPreset__(4)
        elif (MSG=='QN'):
            print "camera LED on"
            self.lasercambox.cameraLEDOn()
        elif (MSG=='QO'):
            print "camera LED off"
            self.lasercambox.cameraLEDOff()
        elif (MSG=='SN'):
            print "servos on"
            self.lasercambox.enablePWM()
        elif (MSG=='SO'):
            print "servos off"
            self.lasercambox.disablePWM()
        elif (MSG in ['S1','S2','S3','S4','S5','S6','S7','S8','S9']):
            print 'playing sound %s' % (MSG)
            self.lasercambox.speak(sound[MSG])
        else:
            print "unknown commad"
    
    def loop(self):
        iostream = io.StringIO()
        self.lasercambox.camera.capture(iostream, 'jpeg', use_video_port=True, resize=(320,240))
        try:
            self.write_message(base64.b64encode(iostream.getvalue()))
        except tornado.websocket.WebSocketClosedError:
            self.__stopStream__()
            
    def __startStream__(self):
        self.lasercambox.camera.start_preview()
        self.camera_loop = tornado.ioloop.PeriodicCallback(self.loop, 1000)
        self.camera_loop.start()
        self.lasercambox.statusLEDOn(self.STREAM_STATUS_LED)
    
    def __stopStream__(self):
        if (self.lasercambox.camera.previewing):
            self.lasercambox.camera.stop_preview()
        if (self.camera_loop != None):
            self.camera_loop.stop()
            self.camera_loop = None
        self.lasercambox.statusLEDOff(self.STREAM_STATUS_LED)
        
    def __cameraPreset__(self, position=None):
        if position==None:
            return
        if self.storeCamera:
            print "storing camera location %i" % (position+1)
            self.cameraLocation[position]=(self.lasercambox.cameraGetPosition())
            self.storeCamera = False
        else:
            print "goto camera store %i" % (position+1)
            self.lasercambox.cameraSetPosition(self.cameraLocation[position])
            
    def __laserPreset__(self, position=None):
        if position==None:
            return
        if self.storeLaser:
            print "storing laser location %i" % (position+1)
            self.laserLocation[position]=(self.lasercambox.laserGetPosition())
            self.storeLaser = False
        else:
            print "goto laser store %i" % (position+1)
            self.lasercambox.laserSetPosition(self.laserLocation[position])
            
    def __loadLocations__(self):
        if os.path.isfile(LOCATIONS_PKL):
            with open(LOCATIONS_PKL,'rb') as PKL:
                temp = pickle.load(PKL)
            self.cameraLocation = temp[0]
            self.laserLocation = temp[1]
            print "locations loaded"
            
    def __saveLocations__(self):
        temp = [self.cameraLocation,self.laserLocation]
        with open(LOCATIONS_PKL,'wb') as PKL:
            pickle.dump(temp, PKL)
        print "locations saved"
                
    def __shutDown__(self):
        self.__stopStream__()
        self.lasercambox.cameraHome()
        self.lasercambox.laserHome()  
        self.lasercambox.cameraLEDOff()
        self.lasercambox.laserOff()
        self.lasercambox.statusLEDAllOff()
        self.__saveLocations__()
        time.sleep(1)
        self.lasercambox.disablePWM()
                
# request handler mapping
handlers = ([
    (r"/kill",          KillHandler),
    (r"/lasercam",      LaserCamHandler),
    (r"/ws",            WebSocketHandler, dict(lasercambox=theBox))
])

#===========================
# MAIN
#===========================
print "create app..."
app = tornado.web.Application(handlers)
print "create http server..."
server = tornado.httpserver.HTTPServer(app)
print "start listening on port {}...".format(PORT)
server.listen(PORT)
print "start ioloop..."
tornado.ioloop.IOLoop.instance().start()
print "i guess we're done then."       
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

# define port server will listen to
PORT = 8008

#-------------------------------------------------------------------------
# Tornado Server Setup
#-------------------------------------------------------------------------
# this will handle HTTP requests
class MyRequestHandler(tornado.web.RequestHandler):
    def get(self):
        print "GET Request from {}".format(self.request.remote_ip)
        self.render("lasercam.html")
        
# this will handle WebSockets requests
class MyWebSocketHandler(tornado.websocket.WebSocketHandler):
    
    def initialize(self, lasercambox):
        self.lasercambox = lasercambox
        self.lasercambox.enablePWM(update=True)
        self.lasercambox.camera.hflip=True
        self.lasercambox.camera.vflip=True
       
    def open(self):
        print "WS open from {}".format(self.request.remote_ip)
    
    def on_close(self):
        print "WS close"
    
    def on_message(self, message):
        print "WS message: {} = ".format(message),
        MSG = message.strip().upper()
        if (MSG=='LU'):
            print "laser up"
            self.lasercambox.laserYVal -= self.lasercambox.servoStep
        elif (MSG=='LD'):
            print "laser down"
            self.lasercambox.laserYVal += self.lasercambox.servoStep
        elif (MSG=='LL'):
            print "laser left"
            self.lasercambox.laserXVal -= self.lasercambox.servoStep
        elif (MSG=='LR'):
            print "laser right"
            self.lasercambox.laserXVal += self.lasercambox.servoStep
        elif (MSG=='LN'):
            print "laser on"
            self.lasercambox.laserOn()
        elif (MSG=='LO'):
            print "laser off"
            self.lasercambox.laserOff() 
        elif (MSG=='CU'):
            print "camera up"
            self.lasercambox.cameraYVal += self.lasercambox.servoStep
        elif (MSG=='CD'):
            print "camera down"
            self.lasercambox.cameraYVal -= self.lasercambox.servoStep
        elif (MSG=='CL'):
            print "camera left"
            self.lasercambox.cameraXVal -= self.lasercambox.servoStep
        elif (MSG=='CR'):
            print "camera right"
            self.lasercambox.cameraXVal += self.lasercambox.servoStep
        elif (MSG=='CN'):
            print "camera start stream"
            self.lasercambox.camera.start_preview()
            self.camera_loop = tornado.ioloop.PeriodicCallback(self.loop, 100)
            self.camera_loop.start()
        elif (MSG=='CO'):
            print "camera stop stream"
            if (self.lasercambox.camera.previewing):
                self.lasercambox.camera.stop_preview()            
            self.camera_loop.stop()           
        elif (MSG=='SN'):
            print "servos on"
            self.lasercambox.enablePWM()
        elif (MSG=='SO'):
            print "servos off"
            self.lasercambox.disablePWM()
        else:
            print "unknown commad"
        self.lasercambox.updatePWM()
    
    def loop(self):
        iostream = io.StringIO()
        self.lasercambox.camera.capture(iostream, 'jpeg', use_video_port=True, resize=(640,480))
        try:
            self.write_message(base64.b64encode(iostream.getvalue()))
        except tornado.websocket.WebSocketClosedError:
            self.camera_loop.stop()
    
        
# separate HTTP and WebSockets based on URL
handlers = ([
    (r"/", MyRequestHandler),
    (r"/ws", MyWebSocketHandler, dict(lasercambox=lasercam.LaserCamBox()))
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
print "should never get here"       
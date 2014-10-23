rpi-laser
=========

Python code for the laser camera box.

The server has three main parts:
* laser_server.py = the actual server, which uses the Tornado web framework
* index.html = the main web page which include JavaScript to communicate via WebSocket
* lasercam.py = defines a class with methods for controlling the laser camera box hardware

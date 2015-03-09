rpi-laser
=========
Python code for the laser camera box.

Laser Cam Box
=============
This is main class to be included by all others.
* **lasercam.py** = defines a class with methods for controlling the laser camera box hardware

Web Interface
=============
Provides a camera video stream and control through a web browser. The set up has three parts:
* **laser_server.py** = the actual server, which uses the Tornado web framework
* **lasercam.html** = the main web page which includes JavaScript to communicate via WebSocket

Wiimote
=======
Control the laser with wiimote nunchuk.
* **laser_wii.py** = pretty simple

watchdog
========
This is a safety mechanism to disable the servo controller after a period of time. The python program **watchdog.py** is run
periodically from a cron job. It looks at the file **servo.wd** and disables the servo controller if that file has not been
touched for a period of time.
* **watchdog.py**
* **servo.wd**

Other
=====
* **laser_curses.py** = a curses interface for control
* **photo_scan.py** = takes a series of photos over the range of servo motion


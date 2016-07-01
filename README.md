# rpi-laser
Domo R.E. Gato - the cat friend roboto
![thumbnail](http://caternuson.github.io/rpi-laser-thumb.jpg)<br/>
Python 2.7 code for the laser camera box.

# Hardware
* Raspberry Pi Model B+
* Raspberry Pi camera module
* USB wifi dongle
* USB bluetooth dongle
* 4 hobby servos
* laser
* Adafruit I2C PWM servo board
* audio amp
* speaker
* some custom boards
* LEDs
* cigar box

# Software
A brief description of the various software components.
* ```lasercam.py``` - defines a class for interfacing with the laser camera box hardware
* ```laser_server.py``` - Tornado based web server
* ```lasercam.html``` - web page interface used by server
* ```laser_wii.py``` - provides Wiimote control of camera and laser
* ```watchdog.py``` - watchdog to turn off servo power
* ```servo.wd``` - file watched by watchdog
* ```laser_curses.py``` - a curses interface for control
* ```photo_scan.py``` - takes a series of photos over the range of servo motion

# Dependencies
* Tornado Web Framework
* Adafruit I2C PWM servo controller Python code
* picamera
* espeak

# Install
Simply clone this repo and run the server:
```
$ git clone https://github.com/caternuson/rpi-laser.git
$ cd rpi-laser
$ sudo python laser_server.py
```

# Configure
Set the ```PORT``` to desired port to be used by server:
```python
PORT = 8008
```
Set the phrases output on the speaker:
```python
sound = {}
sound['S1'] = 'hello world'
sound['S2'] = 'halt! who goes there?'
```

# Watchdog
This is a safety mechanism to disable the servo controller after a period of time.
The python program ```watchdog.py``` is run periodically from a ```cron``` job.
It looks at the file ```servo.wd``` and disables the servo controller if that file has not been
touched for a period of time.

# Automation
Follow [this](https://learn.adafruit.com/running-programs-automatically-on-your-tiny-computer/overview)
tutorial for setting up SysV or systemd to run the server at boot.

# Domo R.E. Gato - the cat friend roboto

![thumbnail](http://caternuson.github.io/rpi-laser-thumb.jpg)<br/>
Python 2.7 code for the laser camera box.

# Hardware
* Raspberry Pi Model B+
* Raspberry Pi camera module
* [Adafruit USB wifi dongle](https://www.adafruit.com/products/2810)
* [Adafruit USB bluetooth dongle](https://www.adafruit.com/products/1327) (for Wii Remote control)
* [Adafruit Diode Laser](https://www.adafruit.com/products/1054)
* [Adafruit I2C PWM Servo Board](https://www.adafruit.com/products/815)
* [Adafruit Audio Amp](https://www.adafruit.com/products/1552)
* [Adafruit Enclosed Speakers](https://www.adafruit.com/product/1669)
* [Adafruit 1 Watt White LED](https://www.adafruit.com/products/518)
* [Adafruit 5V 2A Power Supply](https://www.adafruit.com/product/276)
* [Adafruit Panel Mount 2.1mm DC Barrel Jack](https://www.adafruit.com/products/610)
* Standard size hobby servos x 4
* some custom boards
* various LEDs
* current limiting resistors
* trim pots
* transistors
* switches
* cables
* cigar box
* cat (optional)

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
* [Tornado Web Framework](https://pypi.python.org/pypi/tornado)
* [Adafruit PCA9685 Python library](https://github.com/adafruit/Adafruit_Python_PCA9685)
* [eSpeak](http://espeak.sourceforge.net/) multi-lingual software speech synthesizer
    * ```sudo apt-get install espeak```

# Install
Simply clone this repo and run the server:
```
$ git clone https://github.com/caternuson/rpi-laser.git
$ cd rpi-laser
$ sudo python laser_server.py
```
This will start a server which you can access via a web browser.

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
  :
sound['S9'] = 'im the last word'
```

# Watchdog
This is a safety mechanism to disable the servo controller after a period of time.
The python program ```watchdog.py``` is run periodically from a ```cron``` job.
It looks at the file ```servo.wd``` and disables the servo controller if that file has not been
touched for a period of time.

# Automation
Follow [this](https://learn.adafruit.com/running-programs-automatically-on-your-tiny-computer/overview)
tutorial for setting up SysV or systemd to run the server at boot.

#!/usr/bin/env python
# Home_Weather_Display.py
#
# This is an project for using the Grove RGB LCD Display and the Grove DHT Sensor from the GrovePi starter kit
#
# In this project, the Temperature and humidity from the DHT sensor is printed on the RGB-LCD Display
#
#
# Note the dht_sensor_type below may need to be changed depending on which DHT sensor you have:
#  0 - DHT11 - blue one - comes with the GrovePi+ Starter Kit
#  1 - DHT22 - white one, aka DHT Pro or AM2302
#  2 - DHT21 - black one, aka AM2301
#
# For more info please see: http://www.dexterindustries.com/topic/537-6c-displayed-in-home-weather-project/
#
# The MIT License (MIT)
#
# GrovePi for the Raspberry Pi: an open source platform for connecting Grove Sensors to the Raspberry Pi.
# Copyright (C) 2017  Dexter Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from grovepi import *
from grove_rgb_lcd import *
from time import sleep
from math import isnan
import paho.mqtt.client as mqtt
import json
import grovepi

# Define a class NanError derived from super class Exception for use in raising Nan errors.


class NanError(Exception):
    pass


# Define a class ZeroError derived from super class Exception for use in raising errors when
# temp/humidity both return 0.


class ZeroError(Exception):
    pass


# Set to True to see debug statements like nan error, False to hide.
debug = False

# Setup DHT sensor.
dht_sensor_port = 7     # connect the DHt sensor to port 7
dht_sensor_type = 0     # use 0 for the blue-colored sensor and 1 for the white-colored sensor

scale = 'F'         # Scale for temperature, C or F.
symbol = u'\u2103'  # Unicode degrees C.


# Setup Rotary Angle Sensor
potentiometer = 0   # Connect the Grove Rotary Angle Sensor to analog port A0
led = 8             # Connect the LED to digital port D8
grovepi.pinMode(potentiometer, 'INPUT')
grovepi.pinMode(led, "OUTPUT")
sleep(1)            # Not sure it's needed, but leave for now.
adc_ref = 5         # Reference voltage of ADC is 5v
grove_vcc = 5       # Vcc of the grove interface is normally 5v
full_angle = 300    # Full value of the rotary angle is 300 degrees, as per it's specs (0 to 300)

# Setup Ultrasonic Ranger
ultrasonic_ranger = 3

# Initialize MQTT connections.
local_client = mqtt.Client()
local_client.connect('localhost')
local_client.loop_start()
remote_client = mqtt.Client()
remote_client.connect('test.mosquitto.org')
remote_client.loop_start()

try:
    while True:
        # Read Ultrasonic Ranger
        ranger = grovepi.ultrasonicRead(ultrasonic_ranger)

        # Read sensor value from potentiometer
        angle_sensor = grovepi.analogRead(potentiometer)

        # DHT in it's own try except to handle nan errors.
        try:
            # get the temperature and Humidity from the DHT sensor
            [tempc, hum] = dht(dht_sensor_port, dht_sensor_type)

            # check if we have nans
            # if so, then raise a locally defined NanError exception
            if isnan(tempc) is True or isnan(hum) is True:
                raise NanError('nan error')

            # Check if both temp and humidity are zero
            # if so, the raise a locally defined ZeroError exception
            if tempc == 0.0 and hum == 0.0:
                raise ZeroError('zero error')

        except (NanError, ZeroError) as e:
            if debug:
                print str(e)
            # Do nothing and retry after short delay.
            sleep(0.25)
            continue

        if tempc <= 5:
            setRGB(0, 0, 255)
        elif 5 < tempc < 20:
            setRGB(0, 255, 0)
        else:
            setRGB(255, 0, 0)

        print '\nTemp:', str(tempc) + u'\u2103'  # Unicode degrees C.

        if scale == 'F':
            temp = tempc * 9 / 5 + 32
            symbol = u'\u2109'  # Unicode degrees F.
            print 'Temp:', str(temp) + symbol
        else:
            temp = tempc

        print 'Humi:', str(hum) + '%'

        # Calculate voltage
        voltage = round(float(angle_sensor) * adc_ref / 1023, 2)

        # Calculate rotation in degrees (0 to 300)
        degrees = round((voltage * full_angle) / grove_vcc, 2)

        # Calculate LED brightess (0 to 255) from degrees (0 to 300)
        brightness = int(degrees / full_angle * 255)

        # Give PWM output to LED
        grovepi.analogWrite(led, brightness)

        print "Ranger:", ranger

        print("Angle: %d, Voltage: %.2f, degrees: %.1f, brightness: %d" % (angle_sensor, voltage, degrees, brightness))

        # instead of inserting a bunch of whitespace, we can just insert a \n
        # we're ensuring that if we get some strange strings on one line, the 2nd one won't be affected
        setText_norefresh("Temp: " + str(temp) + scale + '\n' + "Humidity: " + str(hum) + '%')

        # Publish to MQTT.
        # local_client.publish('SNHU/IT697/sensor/data', 'Temp: ' + str(temp) + scale + ', Humi: ' + str(hum) + '%')
        # local_client.publish('SNHU/IT697/sensor/data', 'Ranger: ' + str(ranger))
        # local_client.publish('SNHU/IT697/sensor/data', 'Degrees: ' + str(degrees))
        publish_data = {"timestamp": int(time.time() * 1000),
                        "data": {"temperature": tempc, "humidity": hum, "range": ranger, "degrees": degrees}}
        local_client.publish('SNHU/IT697/sensor/data/json', json.dumps(publish_data))
        # remote_client.publish('SNHU/IT697/jeffrey_cutter_snhu_edu/sensor/data/json', json.dumps(publish_data))

        # Delay between updates.
        sleep(3)

        # Keep line spacing consistent in debug mode.
        if debug:
            print

except KeyboardInterrupt as e:
    if debug:
        print type(e)

finally:
    print "Turning display off"
    # since we're exiting the program
    # it's better to leave the LCD with a blank text
    setText('')
    # And turn off the display.
    setRGB(0, 0, 0)
    print "Turning LED off"
    grovepi.analogWrite(led,0)

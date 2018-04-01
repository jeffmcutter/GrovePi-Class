#!/usr/bin/python

import sys
import Adafruit_DHT
import paho.mqtt.client as mqtt
import json
import math
import time
import uuidgen


# Define a class NanError derived from super class Exception for use in raising Nan errors.


class NanError(Exception):
    pass


# Define a class ZeroError derived from super class Exception for use in raising errors when
# temp/humidity both return 0.


class ZeroError(Exception):
    pass


sensor = Adafruit_DHT.AM2302
pin = 4

# Set to True to see debug statements like nan error, False to hide.
debug = False

uuid = uuidgen.generateUuid()

scale = 'F'         # Scale for temperature, C or F.
symbol = u'\u2103'  # Unicode degrees C.

# Initialize MQTT connections.
remote_client = mqtt.Client()
remote_client.loop_start()
remote_client.connect('test.mosquitto.org')

try:
    while True:

        try:
            # Try to grab a sensor reading.  Use the read_retry method which will retry up
            # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
            hum, tempc = Adafruit_DHT.read_retry(sensor, pin)

            # check if we have nans
            # if so, then raise a locally defined NanError exception
            # if math.isnan(tempc) is True or math.isnan(hum) is True:
            #    raise NanError('nan error')

            # Note that sometimes you won't get a reading and
            # the results will be null (because Linux can't
            # guarantee the timing of calls to read the sensor).
            # If this happens try again!
            if hum is None and tempc is None:
                raise NanError('none error')

            # Check if both temp and humidity are zero
            # if so, the raise a locally defined ZeroError exception
            if tempc == 0.0 and hum == 0.0:
                raise ZeroError('zero error')

        except (NanError, ZeroError) as e:
            if debug:
                print str(e)
            # Do nothing and retry after short delay.
            time.sleep(0.25)
            continue

        print '\nTemp:', "{0:.1f}".format(tempc) + u'\u2103'  # Unicode degrees C.

        if scale == 'F':
            temp = tempc * 9 / 5 + 32
            symbol = u'\u2109'  # Unicode degrees F.
            print 'Temp:', "{0:.1f}".format(temp) + symbol
        else:
            temp = tempc

        print 'Humi:', "{0:.1f}".format(hum) + '%'

        # Publish to MQTT.
        publish_data = {"timestamp": int(time.time() * 1000),
                        "data": {"temperature": "{0:.1f}".format(tempc), "humidity": "{0:.1f}".format(hum)}}
        remote_client.publish('SNHU/IT697/sensor/data/' + uuid, json.dumps(publish_data))

        # Delay between updates.
        time.sleep(60)

        # Keep line spacing consistent in debug mode.
        if debug:
            print

except KeyboardInterrupt as e:
    if debug:
        print type(e)

finally:
    print "Exiting"

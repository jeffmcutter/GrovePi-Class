"""
A GroveDevice abstraction is created for each Grove Pi sensor and actuator. The
GroveDevice provides a uniform read and write interface to each component and
maintains a representation of each component's state. Additionally, each
GroveDevice configures the underlying hardware as necessary for proper device
operation.
"""

import grovepi
import grove_rgb_lcd
import ports
import math


class GroveDevice(object):
    def __init__(self, port=None, value=0):
        self.port = port
        self.value = value

    def read(self):
        return self.value

    def write(self, value):
        self.value = value


class LED(GroveDevice):
    def __init__(self, port=ports.D5):
        GroveDevice.__init__(self, port)
        grovepi.pinMode(port, ports.OUTPUT)

    def write(self, value):
        self.value = int(value)
        grovepi.analogWrite(self.port, self.value)


class LCD(GroveDevice):
    def write(self, value):
        self.value = value
        try:
            r, g, b = value["rgb"]
            grove_rgb_lcd.setRGB(r, g, b)
        except KeyError:
            pass
        try:
            text = value["text"]
            grove_rgb_lcd.setText(text)
        except KeyError:
            pass


class DHTSensor(GroveDevice):
    DHT11 = 0
    DHT22 = 1
    DHT21 = 2

    def __init__(self, port=ports.D7, dht_type=DHT11):
        GroveDevice.__init__(self, port)
        self.dht_type = dht_type

    def read(self):
        while True:
            temperature, humidity = grovepi.dht(self.port, self.dht_type)
            # Sit here until we don't get NaN's.
            if math.isnan(temperature) is False and math.isnan(humidity) is False:
                break
        self.value = {
            "temperature": temperature,
            "humidity": humidity
        }
        return self.value


class AnalogSensor(GroveDevice):
    def __init__(self, port):
        GroveDevice.__init__(self, port)

        def read(self):
            self.value = grovepi.analogRead(self.port)
            return self.value


class Potentiometer(AnalogSensor):
    def __init__(self, port=ports.A2):
        AnalogSensor.__init__(self, port)


class LightSensor(AnalogSensor):
    def __init__(self, port=ports.A1):
        AnalogSensor.__init__(self, port)


class SoundSensor(AnalogSensor):
    def __init__(self, port=ports.A0):
        AnalogSensor.__init__(self, port)


class Button(GroveDevice):
    def __init__(self, port=ports.D3):
        GroveDevice.__init__(self, port)
        grovepi.pinMode(port, ports.INPUT)

    def read(self):
        self.value = grovepi.digitalRead(self.port)
        return self.value


class Buzzer(GroveDevice):
    def __init__(self, port=ports.D2):
        GroveDevice.__init__(self, port)
        grovepi.pinMode(port, ports.OUTPUT)

    def write(self, value):
        self.value = value
        grovepi.digitalWrite(self.port, value)


class Relay(GroveDevice):
    def __init__(self, port=ports.D6):
        GroveDevice.__init__(self, port)
        grovepi.pinMode(port, ports.OUTPUT)

    def write(self, value):
        self.value = value
        grovepi.digitalWrite(self.port, value)


class UltrasonicRanger(GroveDevice):
    def __init__(self, port=ports.D4):
        GroveDevice.__init__(self, port)

        def read(self):
            self.value = grovepi.ultrasonicRead(self.port)
            return self.value
"""
Implements a generalized IoT Device architecture and main loop. This IoT device
receives actuator control messages over MQTT and publishes changing sensor and
actuator data over MQTT. The default configuration utilizes all Grove Pi
interfaces and demonstrates all sensor and actuator types provided in the
starter kit.
"""

import GroveDevices
import ports
import paho.mqtt.client as mqtt
import time
import json
import uuidgen
import Queue
import grove_rgb_lcd

debug = False

DEVICE_UUID = uuidgen.generateUuid()
SENSOR_DATA_TOPIC = "SNHU/IT697/sensor/data/"+DEVICE_UUID
ACTUATOR_TOPIC = "SNHU/IT697/actuator/control/"+DEVICE_UUID

# Actuators
BUZZER = GroveDevices.Buzzer(ports.D2)
BLUE_LED = GroveDevices.LED(ports.D5)
RELAY = GroveDevices.Relay(ports.D6)
RED_LED = GroveDevices.LED(ports.D8)
LCD = GroveDevices.LCD() # I2C-1 port

ACTUATORS = {
    "blue_led": BLUE_LED,
    "red_led": RED_LED,
    "lcd": LCD,
    "buzzer": BUZZER,
    "relay": RELAY
}

# Sensors
SOUND_SENSOR = GroveDevices.SoundSensor(ports.A0)
LIGHT_SENSOR = GroveDevices.LightSensor(ports.A1)
POTENTIOMETER = GroveDevices.Potentiometer(ports.A2)
BUTTON = GroveDevices.Button(ports.D3)
ULTRASONIC_RANGER = GroveDevices.UltrasonicRanger(ports.D4)
DHT_SENSOR = GroveDevices.DHTSensor(ports.D7)

SENSORS = [
    ("potentiometer", POTENTIOMETER, 1),
    ("light_sensor", LIGHT_SENSOR, 5),
    ("sound_sensor", SOUND_SENSOR, 5),
    ("button", BUTTON, 1),
    ("ultrasonic_ranger", ULTRASONIC_RANGER, 5),
    ("dht_sensor", DHT_SENSOR, 100)
]


def on_connect(client, userdata, flags, rc):
    """Called each time the client connects to the message broker
    :param client: The client object making the connection
    :param userdata: Arbitrary context specified by the user program
    :param flags: Response flags sent by the message broker
    :param rc: the connection result
    :return: None
    """
    # subscribe to the ACTUATOR topic when connected
    client.subscribe(ACTUATOR_TOPIC)

# A message queue is required to coordinate reads and writes from/to
# the GrovePi
MSG_QUEUE = Queue.Queue()


def on_message(client, userdata, msg):
    """Called for each message received
    :param client: The client object making the connection
    :param userdata: Arbitrary context specified by the user program
    :param msg: The message from the MQTT broker
    :return: None
    """
    MSG_QUEUE.put(msg.payload)


def calculate_delta(sensor_name, value, last_values, changed_values):
    """Determine which values have changed from their last values
    :param sensor_name: The sensor name the value was read from
    :param value: The new value
    :param last_values: The last set of checked values
    :param changed_values: The set of values that have changed
    """
    try:
        if last_values[sensor_name] == value:
            return
    except KeyError:
        pass
    changed_values[sensor_name] = value
    last_values[sensor_name] = value


read_count = 0
last_values = {}


def read_sensors_and_actuators():
    """ Reads sensors and actuators and returns the values that have changed
    since last read
    :return: The changed values since last read
    """
    global read_count
    changed_values = {}
    for sensor_name, sensor, priority in SENSORS:
        if not (read_count % priority):
            calculate_delta(sensor_name, sensor.read(), last_values,
                            changed_values)
    read_count += 1
    for actuator_name, actuator in ACTUATORS.iteritems():
        calculate_delta(actuator_name, actuator.read(), last_values,
                        changed_values)
    return changed_values


def publish_sensor_data(values):
    """ Publishes data over MQTT to the sensor data topic
    :param values: The sensor values to send
    :return: None
    """
    values["timestamp"] = int(time.time()*1000)
    out_str = json.dumps(values)
    mqtt_client.publish(SENSOR_DATA_TOPIC, out_str)
    print("==>> " + out_str)


def process_received_messages():
    """ Processes all MQTT messages placed in the message queue.
    :return: None
    """
    while True:
        try:
            payload = MSG_QUEUE.get(False)
            print("<<== " + payload)
            payload = json.loads(payload)
            for actuator, msg in payload.iteritems():
                try:
                    ACTUATORS[actuator].write(msg)
                except KeyError:
                    pass
        except Queue.Empty:
            break


MESSAGE_BROKER_URI = "localhost"
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MESSAGE_BROKER_URI)
mqtt_client.loop_start()

time.sleep(1)  # give the hardware time to initialize

try:
    while True:
        try:
            changedValues = read_sensors_and_actuators()

            if changedValues:
                publish_sensor_data(changedValues)

            process_received_messages()

        except (IOError, TypeError) as e:
            print("Error", e)

except KeyboardInterrupt as e:
    if debug:
        print type(e)

finally:
    print "Turning display off"
    grove_rgb_lcd.setText('')
    grove_rgb_lcd.setRGB(0, 0, 0)
    #print "Turning LEDs off"
    #grovepi.analogWrite(RED_LED,0)
    #grovepi.analogWrite(GREEN_LED,0)
    #grovepi.analogWrite(BLUE_LED,0)
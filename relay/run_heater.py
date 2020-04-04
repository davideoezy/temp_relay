from gpiozero import LED
from mqtt_helper import mqtt_helper
import paho.mqtt.client as mqtt
import json

relay = LED(17)
location = "heater_relay"

server_address = "192.168.0.10"

mqtt_helper = mqtt_helper(location)

topic_run_heater = "home/inside/control/heater"
topic_heater_running = "home/inside/control/heater_running"

heater_on = 0


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe([(topic_run_heater,0)])


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global heater_on

    data = str(msg.payload.decode("utf-8"))
    jsonData=json.loads(data)    

    heater_on = jsonData["heater_on"]

    if heater_on == 1:
        relay.on()
    else:
        relay.off()

    dict_msg = {"heater_running": heater_on}
    mqtt_helper.publish_generic_message(topic_heater_running, dict_msg)

    mqtt_helper.publish_status()


client1 = mqtt.Client()
client1.on_connect = on_connect
client1.on_message = on_message

client1.connect(server_address)

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)
# client.enable_logger(logger)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client1.loop_forever()

        

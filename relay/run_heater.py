from gpiozero import LED
from mqtt_helper import mqtt_helper
import paho.mqtt.client as mqtt
import json
from datetime import datetime

relay = LED(17)
location = "heater_relay"

server_address = "192.168.0.10"

mqtt_helper = mqtt_helper(location)

topic_run_heater = "home/inside/control/heater"
topic_heater_running = "home/inside/control/heater_running"

heater_on_curr = 0


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe([(topic_run_heater,0)])


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global heater_on_curr

    data = str(msg.payload.decode("utf-8"))
    jsonData=json.loads(data)    

    heater_on_new = jsonData["heater_on"]
    time_running = 0

    if heater_on_new == 1:
        if heater_on_curr == 0:
            time_start = datetime.now()

        relay.on()

    else:
        if heater_on_curr == 1:
            time_end = datetime.now()
            time_running = (time_end - time_start).total_seconds()
  
        relay.off()
    
    heater_on_curr = heater_on_new

    dict_msg = {"heater_running": heater_on_curr, 'time_running': time_running}
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

        


import paho.mqtt.client as mqtt
import json
import datetime
from rules import rules
from mqtt_helper import mqtt_helper

location = "heater_backend"

rules = rules()
mqtt_helper = mqtt_helper(location)

MorningOn = datetime.time(6, 00)
NightOff = datetime.time(22, 30)

server_address = "192.168.0.10"

topic_temp = "home/inside/sensor/lounge"

topic_anybody_home = "home/inside/sensor/presence"

topic_heater_controls = "home/inside/heater_control"

topic_run_heater = "home/inside/control/heater"

CurrentTemp = 21

somebody_home = 0

power = 0

TargetTemperature = 20


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe([(topic_temp,0),(topic_anybody_home,0),(topic_heater_controls,0)])

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global CurrentTemp
    global TargetTemperature
    global power
    global somebody_home
    
    topic = msg.topic
    data = str(msg.payload.decode("utf-8"))
    jsonData=json.loads(data)    

    
    if topic == topic_temp:
        CurrentTemp = jsonData["temperature"]

    elif topic == topic_anybody_home:
        somebody_home = jsonData["somebody_home"]

    elif topic == topic_heater_controls:
        TargetTemperature = jsonData["TargetTemp"]
        power = jsonData["power"]
    
 
#------- Rules
    
    temp_low = rules.temp_trigger(CurrentTemp, TargetTemperature)

    operating_hours = rules.hours_operation(MorningOn, NightOff)

    turn_heater_on = rules.aggregate_rules(
        power, somebody_home, operating_hours, temp_low)


##### Need to publish power on message for relay to pick up #####

    dict_msg = {"heater_on": turn_heater_on, "power": power, "somebody_home":somebody_home, "operating_hours": operating_hours, "temp_low":temp_low}
    mqtt_helper.publish_generic_message(topic_run_heater, dict_msg)

    mqtt_helper.publish_status()


client1 = mqtt.Client()
client1.on_connect = on_connect
client1.on_message = on_message

client1.connect(server_address)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client1.loop_forever()
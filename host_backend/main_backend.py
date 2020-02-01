from db_helper import db_helper
from rules import rules
from somebody_home import anybody_home
import datetime
import time
import paho.mqtt.client as mqtt
import json

db_helper = db_helper()
rules = rules()
anybody_home = anybody_home()

## Initialise variables

server_address = "192.168.0.10"
topic = "home/inside/sensor/lounge"
#heater_rules = "home/heater/control/rules"
#heater_rule_detail = "home/heater/control/details"



MorningOn = datetime.time(6, 00)
NightOff = datetime.time(22, 30)

def publish_message(key, value):

	topic = "home/inside/heater/control"

	server_address="192.168.0.10" 

	client_label = "docker_heater_control"
	client = mqtt.Client(client_label)
	client.connect(server_address, keepalive=60)

	dict_msg = {str(key):value}
	msg = json.dumps(dict_msg)

	client.publish(topic,msg)	

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    topic = msg.topic
    print(topic)
    data = str(msg.payload.decode("utf-8"))
    jsonData=json.loads(data)
    currentTemperature = jsonData["temperature"]

    try:
        manual_controls = db_helper.get_control_settings()

        # Target Temperature
        TargetTemperature = manual_controls[0]

        # power switch
        power = manual_controls[1]

        ## Derive

        home_list_curr = anybody_home.whos_home()

        last_seen_curr = anybody_home.last_time_seen(home_list_curr)

        time_since_connected = anybody_home.time_since_seen(last_seen_curr)

    except:
        print("error")


    try:
        ## Rules

        temp_low = rules.temp_trigger(currentTemperature, TargetTemperature)

        somebody_home = rules.anybody_home(time_since_connected)

        operating_hours = rules.hours_operation(MorningOn, NightOff)
        
        print(temp_low, somebody_home, operating_hours)


        # run all rules

        turn_heater_on = rules.aggregate_rules(
            power, somebody_home, operating_hours, temp_low)

        print(turn_heater_on)

        ## Reset variables

    except:
        print("error_2")

    try:
        anybody_home.last_seen_prev = last_seen_curr[:]      

        #heater_rules_str = "rules, , power=%s,temp_low=%s,operating_hours=%s,somebody_home,=%s,turn_heater_on=%s".format(power, temp_low, operating_hours, somebody_home, turn_heater_on)
        #heater_rule_detail_str = "rule_detail, ,temp_low=%s,currentTemperature=%s,TargetTemperature=%s,somebody_home=%s,dev_1=%s,dev_2=%s,dev_3=%s,dev_4=%s,operating_hours=%s,MorningOn=%s,NightOff=%s",format(
        #    temp_low, currentTemperature, TargetTemperature, somebody_home, time_since_connected[0], time_since_connected[1], 
        #    time_since_connected[2], time_since_connected[3], operating_hours, MorningOn, NightOff)

        #print(heater_rules_str)
        #print(heater_rule_detail_str)

        #client.publish(heater_rules,str(heater_rules_str))
        #client.publish(heater_rule_detail, str(heater_rule_detail_str))
        publish_message("turn_heater_on", turn_heater_on)

        
    except:
        print("error_3")

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(server_address)

client.loop_start()

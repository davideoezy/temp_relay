
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, \
    flash, jsonify
from db_helper import db_helper
from mqtt_helper import mqtt_helper
import gviz_api
import json
import paho.mqtt.client as mqtt


location = "app_front_end"

server_address = "192.168.0.10"

topic_heater_controls = "home/inside/heater_control"
topic_current_temp = "home/inside/sensor/CurrentTemp"
topic_heater_power = "home/inside/control/heater"
topic_outside_conditions = "home/outside/sensor"

currentTemperature = 99
currentTarget = 99
power = 0
heatRunning = 0
outside_temp = 99
feels_like = 99

db_helper = db_helper()
mqtt_helper = mqtt_helper(location)

app = Flask(__name__)

# prepare method to call when / is navigated to
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.args.get("power") is not None and request.args.get("temperature"):
        power = request.args.get("power")
        temperature = round(float(request.args.get("temperature")),0)

    if 'POST' == request.method:
        data = request.form
        power = data["power"]
        temperature = round(float(data["temperature"]),0)

        db_helper.insert_control_settings(temperature=temperature, power = power)
        mqtt_helper.publish_controls(temperature, power)
        mqtt_helper.publish_status()

    return webpage_helper(render_template, 'request')

@app.route("/update")
def update():
    return webpage_helper(jsonify, 'update')

@app.route("/temps")
def temp_data():
    temps = db_helper.get_temps()
    

    temps_desc = {"time": ("datetime", "Timestamp"),
                "temp": ("number", "Inside Temperature"),
                "air_temp": ("number", "Outside Temperature"),
                "feels_like": ("number", "Feels Like")}

    data_table_temp = gviz_api.DataTable(temps_desc)
    data_table_temp.LoadData(temps)

    return data_table_temp.ToJSon(columns_order=("time", "temp", "air_temp", "feels_like"),
                                           order_by="time")



# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe([(topic_heater_controls,0),(topic_current_temp,0),
                        (topic_heater_power,0),(topic_outside_conditions,0)])

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global currentTemperature
    global currentTarget
    global power
    global heatRunning
    global outside_temp
    global feels_like

    topic = msg.topic
    data = str(msg.payload.decode("utf-8"))
    jsonData=json.loads(data)    

    if topic == topic_heater_controls:
        power = jsonData["power"]
        currentTarget = int(jsonData["TargetTemperature"])

    elif topic == topic_current_temp:
        currentTemperature = round(float(jsonData["CurrentTemp"]),1)

    elif topic == topic_heater_power:
        heatRunning = jsonData["heater_on"]
    
    elif topic == topic_outside_conditions:
        outside_temp = int(jsonData["temperature"])
        feels_like = int(jsonData["feels_like"])

     
# take a function and gather necessary data for the web ui, then call the function
# with the gathered data an an input and return the result
def webpage_helper(function, type):

# check if we should include 'index.html' in the function call
    if 'update' == type:
        return function(heatRunning = heatRunning,
                        currentTemperature=currentTemperature,
                        currentTarget = currentTarget,
                        powerMode = power,
                        outside_temp = outside_temp,
                        feels_like = feels_like)

    return function('index.html',
                    heatRunning = heatRunning,
                    currentTemperature=currentTemperature,
                    currentTarget = currentTarget,
                    powerMode=power,
                    outside_temp=outside_temp,
                    feels_like=feels_like)


if __name__ == "__main__":

    client1 = mqtt.Client()
    client1.on_connect = on_connect
    client1.on_message = on_message
    client1.connect(server_address)
    client1.loop_start()    

    app.run('0.0.0.0', port='8600')

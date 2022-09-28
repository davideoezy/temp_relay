from flask import Flask, request, session, g, redirect, url_for, abort, render_template, \
    flash, jsonify
from db_helper import db_helper
from mqtt_helper import mqtt_helper
import paho.mqtt.client as mqtt
#import gviz_api
import json

db_helper = db_helper()

pwr = 0
TargetTemp = 20

def on_message(client, userdata, message):
    global TargetTemp
    global pwr
    msg = json.loads(message.payload.decode())
    TargetTemp = round(float(msg["TargetTemp"]),0)
    pwr = msg["power"]
 
broker_address="192.168.0.115"

client = mqtt.Client("heater_control") 
client.on_message=on_message #attach function to callback
client.connect(broker_address) #connect to broker
client.loop_start() #start the loop

client.subscribe("home/inside/control/heater_control")

app = Flask(__name__)

# prepare method to call when / is navigated to
@app.route("/", methods=['GET', 'POST'])
def index():
    global pwr
    global TargetTemp
    if request.args.get("power") is not None and request.args.get("temperature"):
        power = pwr
        temperature = TargetTemp
        #db_helper.insert_control_settings(temperature=temperature, power=power)

    if 'POST' == request.method:
        data = request.form
        power = data["power"]
        TargetTemp = round(float(data["temperature"]),0)

        #db_helper.insert_control_settings(temperature=temperature, power = power)
        #mqtt_helper.publish_controls(temperature,power)
        control_msg = json.dumps({"power":power, "TargetTemp": TargetTemp})

        client = mqtt.Client("heater_control")
        client.connect("192.168.0.115", keepalive=60)
        client.publish("home/inside/control/heater_control", payload = control_msg, qos = 0, retain = True)

    return webpage_helper(render_template, 'request')

@app.route("/update")
def update():
    return webpage_helper(jsonify, 'update')

@app.route("/inside_temp")
def inside_temp_data():
    inside_temp = db_helper.get_inside_temp_chartjs()

    inside_temp_json = json.dumps(inside_temp)
    return inside_temp_json

@app.route("/outside_temp")
def outside_temp_data():
    outside_temp = db_helper.get_outside_temp_chartjs()

    outside_temp_json = json.dumps(outside_temp)
    return outside_temp_json

@app.route("/outside_feels_like")
def outside_feels_like_data():
    outside_feels_like = db_helper.get_outside_feels_like_chartjs()

    outside_feels_like_json = json.dumps(outside_feels_like)
    return outside_feels_like_json

@app.route("/temps")
def temp_data():
    inside_temp = db_helper.get_inside_temp_chartjs()
    outside_temp = db_helper.get_outside_temp_chartjs()
    outside_feels_like = db_helper.get_outside_feels_like_chartjs()
    temps = {
        'inside_temp': inside_temp,
        'outside_temp': outside_temp,
        'outside_feels_like': outside_feels_like
    }

    temps_json = json.dumps(temps)
    return temps_json


# take a function and gather necessary data for the web ui, then call the function
# with the gathered data an an input and return the result
def webpage_helper(function, type):
    global pwr
    global TargetTemp
# get current settings and house temperature
#    current = db_helper.get_control_settings() # influx
    currentTemperature = round(float(db_helper.get_inside_temp()),1) # influx
    heatRunning = db_helper.get_heat_indicator() # influx
    currentTarget = TargetTemp 
    power = pwr
    outside = db_helper.get_outside_temp() # influx
    outside_temp = int(outside['temperature'])
    feels_like = int(outside['feels_like'])


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
    app.run('0.0.0.0', port='8600')

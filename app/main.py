from flask import Flask, request, session, g, redirect, url_for, abort, render_template, \
    flash, jsonify
from db_helper import db_helper
#import gviz_api
import json

db_helper = db_helper()

app = Flask(__name__)

# prepare method to call when / is navigated to
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.args.get("power") is not None and request.args.get("temperature"):
        power = request.args.get("power")
        temperature = round(float(request.args.get("temperature")),0)
        #db_helper.insert_control_settings(temperature=temperature, power=power)

    if 'POST' == request.method:
        data = request.form
        power = data["power"]
        temperature = round(float(data["temperature"]),0)

        db_helper.insert_control_settings(temperature=temperature, power = power)

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
    outside_temp = db_helper.get_outside_temp_chartjs

    outside_temp_json = json.dumps(outside_temp)
    return outside_temp_json

@app.route("/outside_feels_like")
def outside_feels_like_data():
    outside_feels_like = db_helper.get_outside_feels_like_chartjs()

    outside_feels_like_json = json.dumps(outside_feels_like)
    return outside_feels_like_json


# take a function and gather necessary data for the web ui, then call the function
# with the gathered data an an input and return the result
def webpage_helper(function, type):
# get current settings and house temperature
    current = db_helper.get_control_settings() # mariadb
    currentTemperature = round(float(db_helper.get_inside_temp()),1) # influx
    heatRunning = db_helper.get_heat_indicator() # influx
    currentTarget = int(current[0]) 
    power = current[1]
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
    app.run('0.0.0.0', port='8500')

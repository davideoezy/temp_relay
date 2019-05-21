
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, \
    flash, jsonify
from db_helper import db_helper
import gviz_api

db_helper = db_helper()

app = Flask(__name__)

# prepare method to call when / is navigated to
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.args.get("power") is not None and request.args.get("temperature"):
        power = request.args.get("power")
        temperature = round(float(request.args.get("temperature")),0)
        db_helper.insert_control_settings(temperature=temperature, power=power)

    if 'POST' == request.method:
        data = request.form
        power = data["power"]
        temperature = round(float(data["temperature"]),0)

        db_helper.insert_control_settings(temperature=temperature, power = power)

    return webpage_helper(render_template, 'request')

@app.route("/update")
def update():
    return webpage_helper(jsonify, 'update')

@app.route("/temps")
def temp_data():
    inside = db_helper.get_temps()
    

    temps_desc = {"ts": ("datetime", "Timestamp"),
                "temp": ("number", "Inside Temperature"),
                "air_temp": ("number", "Outside Temperature"),
                "feels_like": ("number", "Feels Like")}

    data_table_temp = gviz_api.DataTable(temps_desc)
    data_table_temp.LoadData(temps)

    return data_table_temp.ToJSonResponse(columns_order=("ts", "temp", "air_temp", "feels_like"),
                                           order_by="ts")




@app.route("/outside")
def outside_data():
    outside = db_helper.get_outside_temps()

    outs_desc = {"ts": ("datetime", "Timestamp"),
                 "air_temp": ("number", "Outside Temperature"),
                 "feels_like": ("number", "Feels Like")}


    data_table_outside = gviz_api.DataTable(outs_desc)
    data_table_outside.LoadData(outside)

    return data_table_outside.ToJSon(columns_order=("ts", "air_temp", "feels_like"),
                                                    order_by="ts")



# take a function and gather necessary data for the web ui, then call the function
# with the gathered data an an input and return the result
def webpage_helper(function, type):
# get current settings and house temperature
    current = db_helper.get_control_settings()
    currentTemperature = round(float(db_helper.get_temp()),1)
    heatRunning = db_helper.get_heat_indicator()
    currentTarget = round(float(current[0]),0)
    power = current[1]

# check if we should include 'index.html' in the function call
    if 'update' == type:
        return function(heatRunning = heatRunning,
                        currentTemperature=currentTemperature,
                        currentTarget = currentTarget,
                        powerMode = power)

    return function('index.html',
                    heatRunning = heatRunning,
                    currentTemperature=currentTemperature,
                    currentTarget = currentTarget,
                    powerMode = power)


if __name__ == "__main__":
    app.run(host="0.0.0.0")


from flask import Flask, request, session, g, redirect, url_for, abort, render_template, \
    flash, jsonify

class ThermostatWeb():
    def __init__(self, db_helper):

        self.db_helper = db_helper
        self.app = Flask(__name__)

        # prepare method to call when / is navigated to
        @self.app.route("/", methods=['GET', 'POST'])
        def index():
            if request.args.get("mode") is not None \
                    and request.args.get("temperature"):
                manual_on = request.args.get("manual_on")
                manual_off = request.args.get("manual_off")
                #temperature = round(float(request.args.get("temperature")), 1)
                temperature = request.args.get("temperature")
                self.db_helper.insert_control_settings(
                    temperature=temperature, manual_on=manual_on, manual_off=manual_off)

            if 'POST' == request.method:
                data = request.form
                manual_on = data["manual_on"]
                manual_off = data["manual_off"]
                #temperature = round(float(data["temperature"]), 1)
                temperature = data["temperature"]

                self.db_helper.insert_control_settings(
                    temperature=temperature, manual_on=manual_on, manual_off=manual_off)

            return self.webpage_helper(render_template, 'request')

        @self.app.route("/update")
        def update():
            return self.webpage_helper(jsonify, 'update')

    # take a function and gather necessary data for the web ui, then call the function
    # with the gathered data an an input and return the result
    def webpage_helper(self, function, type):
        # get current settings and house temperature
        current = self.db_helper.get_control_settings()
        currentTemperature = self.db_helper.get_temp()
        heatRunning = self.db_helper.get_heat_indicator()
        currentTarget = current[0]
        manual_on = current[1]
        manual_off = current[2]



        # check if we should include 'index.html' in the function call
        if 'update' == type:
            return function(heatRunning = heatRunning,
                            currentTemperature=currentTemperature,
                            currentTarget = currentTarget,
                            manual_on = manual_on,
                            manual_off = manual_off)

        return function('index.html',
                        heatRunning = heatRunning,
                        currentTemperature=currentTemperature,
                        currentTarget = currentTarget,
                        manual_on = manual_on,
                        manual_off = manual_off)

    def run(self):
        self.app.run(host='0.0.0.0')

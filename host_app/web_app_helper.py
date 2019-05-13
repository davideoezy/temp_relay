
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
                power = request.args.get("power")
                temperature = round(float(request.args.get("temperature")),0)
                #temperature = request.args.get("temperature")
                self.db_helper.insert_control_settings(
                    temperature=temperature, power=power)

            if 'POST' == request.method:
                data = request.form
                power = data["power"]
                temperature = round(float(data["temperature"]),0)
                #temperature = data["temperature"]

                self.db_helper.insert_control_settings(
                    temperature=temperature, power = power)

            return self.webpage_helper(render_template, 'request')

        @self.app.route("/update")
        def update():
            return self.webpage_helper(jsonify, 'update')

    # take a function and gather necessary data for the web ui, then call the function
    # with the gathered data an an input and return the result
    def webpage_helper(self, function, type):
        # get current settings and house temperature
        current = self.db_helper.get_control_settings()
        currentTemperature = round(float(self.db_helper.get_temp()),1)
        heatRunning = self.db_helper.get_heat_indicator()
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

    def run(self):
        self.app.run(host='0.0.0.0')

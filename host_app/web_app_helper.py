
import threading
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, \
    flash, jsonify

class ThermostatWeb():
    def __init__(self, db_helper):

        self.db_helper = db_helper
        self.app = Flask(__name__)
        self.insert_statement = """
                                INSERT into heater_controls
                                (temp_setting,
                                bedtime,
                                awake,
                                manual_on,
                                manual_off)
                                VALUES
                                ({},{},{},{},{})""".format(temperature, bedtime, awake, manual_on, manual_off)


        # prepare method to call when / is navigated to
        @self.app.route("/", methods=['GET', 'POST'])
        def index():
            if request.args.get("mode") is not None \
                    and request.args.get("temperature"):
                manual_on = request.args.get("manual_on")
                manual_off = request.args.get("manual_off")
                awake = request.args.get("awake")
                bedtime = = request.args.get("bedtime")
                temperature = round(float(request.args.get("temperature")), 1)
                self.db_helper.insert_db_data(insert_statement)

            if 'POST' == request.method:
                data = request.form
                manual_on = data["manual_on"]
                manual_off = data["manual_off"]
                awake = data["awake"]
                bedtime = data["bedtime"]
                temperature = round(float(data["temperature"]), 1)

                self.db_helper.insert_db_data(insert_statement)

            return self.webpage_helper(render_template, 'request')

        @self.app.route("/update")
        def update():
            return self.webpage_helper(jsonify, 'update')

    # take a function and gather necessary data for the web ui, then call the function
    # with the gathered data an an input and return the result
    def webpage_helper(self, function, type):
        # get current settings and house temperature
        current = self.db_helper.get_control_settings()
        currentTemperature = self.get_temp()
        heatRunning = self.get_heat_indicator()
        CurrentTarget = current[0]
        manual_on = current[3]
        manual_off = current[4]
        awake = current[2]
        bedtime = current[1]


        # check if we should include 'index.html' in the function call
        if 'update' == type:
            return function(heatRunning = heatRunning,
                            currentTemperature=currentTemperature,
                            currentTarget = currentTarget,
                            manual_on = manual_on,
                            manual_off = manual_off,
                            awake = awake,
                            bedtime = bedtime)

        return function('index.html',
                        heatRunning = heatRunning,
                        currentTemperature=currentTemperature,
                        currentTarget = currentTarget,
                        manual_on = manual_on,
                        manual_off = manual_off,
                        awake = awake,
                        bedtime = bedtime)

    def run(self):
        self.app.run()

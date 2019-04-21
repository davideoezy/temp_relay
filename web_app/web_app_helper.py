
import threading
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, \
    flash, jsonify

def get_db_data(query, host, port, user, passwd, db):
    con = mariadb.connect(host=host, port=port, user=user,
                          password=passwd, database=db)
    cur = con.cursor()
    cur.execute(query)

    output = -999

    for row in cur:
        output = row[0]

    return output

def get_db_data_multiple(query, host, port, user, passwd, db):
    con = mariadb.connect(host=host, port=port, user=user,
                          password=passwd, database=db)
    cur = con.cursor()
    cur.execute(query)

    output = [-999,0,0,0,0]

    for row in cur:
        output = [row[0], row[1], row[2], row[3], row[4], row[5]]

    return output


# manual controls

        query_manual_controls = """
        SELECT
        temp_setting,
        bedtime,
        awake,
        manual_on,
        manual_off
        FROM heater_controls 
        ORDER BY ts ASC
        """

        
        #### in development - remove comments when heater_controls table setup in prod
        manual_controls = get_db_data_multiple(query_manual_controls, db_host, db_host_port, db_user, db_pass, db)

# temp setting
        target_temp = manual_controls[0]

# bedtime
        bedtime = manual_controls[1]

# awake
        awake = manual_controls[2]

# manual overide - turn on
        manual_on = manual_controls[3]

# manual overide - turn off
        manual_off = manual_controls[4]

# room temperature
        query = """
        SELECT
        avg(temp)
        FROM temperature 
        WHERE ts > DATE_SUB(now(), INTERVAL 90 second)
        ORDER BY ts ASC
        """

        CurrentTemperature = get_db_data(query, db_host, db_host_port, db_user, db_pass, db)

# running

        query_heater_on = """
        SELECT
        heater_on
        FROM heater_log 
        ORDER BY ts ASC
        """

        heater_on = get_db_data(query_heater_on, db_host, db_host_port, db_user, db_pass, db)

class ThermostatWeb(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

        self.app = Flask(__name__)

        # prepare method to call when / is navigated to
        @self.app.route("/", methods=['GET', 'POST'])
        def index():
            if request.args.get("mode") is not None \
                    and request.args.get("temperature"):
                mode = request.args.get("mode")
                temperature = round(float(request.args.get("temperature")), 1)
                self.fileManager.write_current(mode, temperature)

            if 'POST' == request.method:
                data = request.form
                mode = data["mode"]
                temperature = round(float(data["temperature"]), 1)

                self.fileManager.write_current(mode, temperature)

            return self.webpage_helper(render_template, 'request')

        @self.app.route("/update")
        def update():
            return self.webpage_helper(jsonify, 'update')

    # take a function and gather necessary data for the web ui, then call the function
    # with the gathered data an an input and return the result
    def webpage_helper(self, function, type):
        # get current settings and house temperature
        current = self.fileManager.read_current()
        currentTemperature = currentTemperature
        heatRunning = heater_on
        CurrentTarget = target_temp
        manual_on = manual_on
        manual_off = manual_off
        awake = awake
        bedtime = bedtime


        # get weather
        currentWeather = self.weather.current_weather()
        today = self.weather.today_forecast()

        # handle a lack of weather api data
        if currentWeather is None or today is None:
            currentWeatherTemp = currentWeatherSummary = todaySummary = todayMax =\
                todayMin = todayPrecipProbability = None
        else:
            currentWeatherTemp = currentWeather['temperature']
            currentWeatherSummary = currentWeather['summary']

            todaySummary = today['summary']
            todayMax = today['apparentTemperatureMax']
            todayMin = today['apparentTemperatureMin']
            todayPrecipProbability = today['precipProbability']

        # check if we should include 'index.html' in the function call
        if 'update' == type:
            return function(heater_on = heater_on,
                            currentTemperature=currentTemperature,
                            currentTarget = currentTarget
                            manual_on = manual_on
                            manual_off = manual_off,
                            awake = awake,
                            bedtime = bedtime,
                            currentWeatherTemp=currentWeatherTemp,
                            currentWeatherSummary=currentWeatherSummary,
                            todaySummary=todaySummary,
                            todayMax=todayMax,
                            todayMin=todayMin,
                            todayPrecipProbability=todayPrecipProbability)

        return function('index.html',
                        heater_on = heater_on,
                        currentTemperature=currentTemperature,
                        currentTarget = currentTarget
                        manual_on = manual_on
                        manual_off = manual_off,
                        awake = awake,
                        bedtime = bedtime,
                        currentWeatherTemp=currentWeatherTemp,
                        currentWeatherSummary=currentWeatherSummary,
                        todaySummary=todaySummary,
                        todayMax=todayMax,
                        todayMin=todayMin,
                        todayPrecipProbability=todayPrecipProbability)

    def run(self):
        self.app.run()

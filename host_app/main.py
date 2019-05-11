from db_helper import db_helper
from rules import rules
from rules_aggregator import rules_aggregator
from somebody_home import anybody_home
from web_app_helper import ThermostatWeb
import datetime
import time

db_helper = db_helper()
rules_aggregator = rules_aggregator()
rules = rules()
anybody_home = anybody_home()


## Get data

web = ThermostatWeb(db_helper)

web.run()

while True:

    currentTemperature = db_helper.get_temp()

    manual_controls = db_helper.get_control_settings()

    # On/off time in DB?
    # Can then create function to update times based on calcs/manual update

    MorningOn = datetime.time(6, 00)
    NightOff = datetime.time(22, 30)

    # Target Temperature
    TargetTemperature = manual_controls[0]

    # Bedtime switch
    bedtime = manual_controls[1]

    # awake switch
    awake = manual_controls[2]

    # manual overide - turn on
    manual_on = manual_controls[3]

    # manual overide - turn off
    manual_off = manual_controls[4]


    ## Derive
   
    home_list_curr = anybody_home.whos_home()

    last_seen_curr = anybody_home.last_time_seen(home_list_curr)

    time_since_connected = anybody_home.time_since_seen(last_seen_curr)


    ## Rules

    temp_low = rules.temp_trigger(currentTemperature, TargetTemperature)

    somebody_home = rules.anybody_home(time_since_connected)

    operating_hours = rules.hours_operation(MorningOn, NightOff)


    # run all rules

    turn_heater_on = rules_aggregator.aggregate_rules(
        manual_on, manual_off, somebody_home, operating_hours, temp_low)


    ## Reset variables

    anybody_home.last_seen_prev = last_seen_curr[:]


    ## Insert logs

    insert_manual_controls = """
            INSERT into heater_controls
            (temp_setting,
            manual_on,
            manual_off)
            VALUES
            ({},{},{})""".format(TargetTemperature, manual_on, manual_off)

    db_helper.insert_db_data(statement=insert_manual_controls)

    insert_rule_info = """
            INSERT INTO rule_info
            (temp_low, temp, threshold, 
            anybody_home, dev_1, dev_2, dev_3, dev_4, 
            operating_hours, MorningOn, NightOff)
            VALUES
            ({},{},{},{},{},{},{},{},{},'{}','{}')""".format(temp_low, currentTemperature, 
                                                        TargetTemperature, somebody_home, 
                                                        time_since_connected[0], time_since_connected[1], 
                                                        time_since_connected[2], time_since_connected[3], 
                                                        operating_hours, MorningOn, NightOff)

    db_helper.insert_db_data(statement=insert_rule_info)

    insert_heater_rules = """
            INSERT INTO heater_rules
            (manual_on, manual_off, temp_low, operating_hours, anybody_home, heater_on)
            VALUES
            ({},{},{},{},{},{})""".format(manual_on, manual_off, temp_low, operating_hours, somebody_home, turn_heater_on)

    db_helper.insert_db_data(statement=insert_heater_rules)


    time.sleep(30)

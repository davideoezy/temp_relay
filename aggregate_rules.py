import mysql.connector as mariadb
import time
from db_helper import db_helper


db_host = '192.168.0.10'
db_host_port = '3306'
db_user = 'rpi'
db_pass = 'warm_me'
db = 'temp_logger'

class rules_aggregator():

    def __init__(self):
        self.override_off_rules = []
        self.override_on_rules = []
        self.manual_on_rule_list = []
        self.automated_rule_list = []


    def aggregate_rules(bedtime, awake, manual_on, manual_off, somebody_home, operating_hours, temp_low):

        self.override_off_rules.extend([bedtime, manual_off])
        self.override_on_rules.extend([awake, manual_on])

        if any(i is 1 for i in self.override_off_rules):
            override_off = 1
        else:
            override_off = 0

        if any(i is 1 for i in self.override_on_rules):
            override_on = 1
        else:
            override_on = 0

        self.manual_on_rule_list.extend([override_on, somebody_home, temp_low])
        self.automated_rule_list.extend([somebody_home, operating_hours, temp_low])

        if all(i is 1 for i in self.override_off_rules):
            heater_on = 0
        elif all(i is 1 for i in self.manual_on_rule_list):
            heater_on = 1
        elif all(i is 1 for i in self.automated_rule_list):
            heater_on = 1
        else:
            heater_on = 0

        return heater_on


if __name__ == "__main__":

    while True:
        db_helper = db_helper()
        rules_aggregator = rules_aggregator()

        query_manual_controls = """
        SELECT
        bedtime,
        awake,
        manual_on,
        manual_off
        FROM heater_controls 
        ORDER BY ts ASC
        """

        
        #### in development - remove comments when heater_controls table setup in prod
        manual_controls = db_helper.db_data(query_type = "select", n_variables = 4, statemment  = query_manual_controls, default = 0)

# bedtime
        bedtime = manual_controls[0]

# awake
        awake = manual_controls[1]

# manual overide - turn on
        manual_on = manual_controls[2]

# manual overide - turn off
        manual_off = manual_controls[3]

# somebody_home check

        query_anybody_home = """
        SELECT
        anybody_home,
        FROM anybody_home
        where WHERE ts > DATE_SUB(now(), INTERVAL 90 second)
        ORDER BY ts ASC
        """

        somebody_home = db_helper.db_data(
            query_type="select", n_variables=1, statement=query_anybody_home, default=0)
        

# operating_hours check

        query_operating_hours = """
        SELECT
        operating_hours,
        FROM operating_hours
        where WHERE ts > DATE_SUB(now(), INTERVAL 90 second)
        ORDER BY ts ASC
        """
        operating_hours = db_helper.db_data(
            query_type="select", n_variables=1, statement=query_operating_hours, default=0)


# check temperature rule
        query_temp_rule = """
        SELECT
        temp_low,
        FROM temp_rule
        where WHERE ts > DATE_SUB(now(), INTERVAL 90 second)
        ORDER BY ts ASC
        """
        temp_low = db_helper.db_data(
            query_type="select", n_variables=1, statement=query_temp_rule, default=0)


# run all rules

        turn_heater_on = aggregate_rules(bedtime, awake, manual_on, manual_off, somebody_home, operating_hours, temp_low)

# update db

        insert_stmt = """
        INSERT INTO heater_rules
        (bedtime, awake, manual_on, manual_off, temp_low, operating_hours, anybody_home, heater_on)
        VALUES
        ({},{},{},{},{},{},{},{})""".format(bedtime, awake, manual_on, manual_off, temp_low, operating_hours, somebody_home, turn_heater_on)

        db_helper.db_data(
            query_type="insert", statement=query_operating_hours)
        
        time.sleep(30)

# create table heater_rules (bedtime int, awake int, manual_on int, manual_off int, temp_low int, operating_hours int, anybody_home int, heater_on int, ts timestamp);

import mysql.connector as mariadb
import time
import datetime
import subprocess
import arpreq
import os


db_host = '192.168.0.10'
db_host_port = '3306'
db_user = 'rpi'
db_pass = 'warm_me'
db = 'temp_logger'

wifi_interface = "enp3s0"

MorningOn = datetime.time(6, 30)
NightOff = datetime.time(22, 56)


def whos_home(devices):

    home_list = [(time.time(), 0)] * devices

    for ip in range(0, devices):
        test = arpreq.arpreq('192.168.0.' + str(ip+51))
        if test is not None:
            home_list[ip] = time.time(), 1

    return home_list


def last_time_seen(current_reading, prev_log, devices):

    last_seen = [0] * devices

    for ip in range(0, devices):
        if current_reading[ip][1] == 1:
            last_seen[ip] = time.time()
        elif current_reading[ip][1] == 0:
            last_seen[ip] = prev_log[ip]

    return last_seen


def time_since_seen(last_seen, devices):

    duration = [0] * devices

    for ip in range(0, devices):
        duration[ip] = round((time.time() - last_seen[ip])/60)
        if duration[ip] > 999:
            duration[ip] = 999

    return duration


def anybody_home(time_since_connected):
    somebody_home = 0

    if any(t < 20 for t in time_since_connected):
        somebody_home = 1

    return somebody_home


def hours_operation(on_time, off_time):

    CurrentTime = datetime.datetime.now()

    MorningOnTime = CurrentTime.replace(
        hour=on_time.hour, minute=on_time.minute, second=on_time.second)

    NightOffTime = CurrentTime.replace(
        hour=off_time.hour, minute=off_time.minute, second=off_time.second)

    operating_hours = 0

    if(CurrentTime > MorningOnTime and CurrentTime < NightOffTime):
        operating_hours = 1

    return operating_hours



def get_db_data(query, host, port, user, passwd, db):
    con = mariadb.connect(host=host, port=port, user=user,
                          password=passwd, database=db)
    cur = con.cursor()
    cur.execute(query)

    output = 999

    for row in cur:
        output = row[0]

    return output


def get_db_data_multiple(query, host, port, user, passwd, db):
    con = mariadb.connect(host=host, port=port, user=user,
                          password=passwd, database=db)
    cur = con.cursor()
    cur.execute(query)

    output = [999,0,0,0]

    for row in cur:
        output = [row[0], row[1], row[2], row[3], row[4]]

    return output


def temp_trigger(temp):

    temp_low = 0

    if temp < 20:
        temp_low = 1

    return temp_low


def insert_results(query, db_host, db_host_port, db_user, db_pass, db):

    con = mariadb.connect(host=db_host, port=db_host_port,
                          user=db_user, password=db_pass, database=db)
    cur = con.cursor()
    try:
        cur.execute(insert_stmt)
        con.commit()
    except:
        con.rollback()
    con.close()
    return

def aggregate_rules(bedtime, awake, manual_on, manual_off, somebody_home, operating_hours, temp_low):
    override_off_rules = []
    override_on_rules = []
    manual_on_rule_list = []
    automated_rule_list = []

    override_off_rules.extend([bedtime, manual_off])
    override_on_rules.extend([awake, manual_on])

    if any(i is 1 for i in override_off_rules):
        override_off = 1
    else:
        override_off = 0

    if any(i is 1 for i in override_on_rules):
        override_on = 1
    else:
        override_on = 0

    manual_on_rule_list.extend([override_on, somebody_home, temp_low])
    automated_rule_list.extend([somebody_home, operating_hours, temp_low])

    if all(i is 1 for i in override_off_rules):
        heater_on = 0
    elif all(i is 1 for i in manual_on_rule_list):
        heater_on = 1
    elif all(i is 1 for i in automated_rule_list):
        heater_on = 1
    else:
        heater_on = 0

    return heater_on


if __name__ == "__main__":

    devices = 4
    last_seen_prev = [(time.time() - 7200)] * devices

    while True:
# check if we're home

        home_list_curr = whos_home(devices)

        last_seen_curr = last_time_seen(
            home_list_curr, last_seen_prev, devices)

        time_since_connected = time_since_seen(last_seen_curr, devices)

        somebody_home = anybody_home(time_since_connected)

        last_seen_prev = last_seen_curr[:]

# check if we're within operating hours

        operating_hours = hours_operation(MorningOn, NightOff)

# check lounge temp
        query = """
        SELECT
        avg(temp)
        FROM temperature 
        WHERE ts > DATE_SUB(now(), INTERVAL 90 second)
        ORDER BY ts ASC
        """

        temp = get_db_data(query, db_host, db_host_port, db_user, db_pass, db)

# temp threshold rule

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
        #manual_controls = get_db_data_multiple(query_manual_controls, db_host, db_host_port, db_user, db_pass, db)

        threshold = manual_controls[0]

        temp_low = temp_trigger(temp, threshold)

# bedtime
        bedtime = manual_controls[1]

# awake
        awake = manual_controls[2]

# manual overide - turn on
        manual_on = manual_controls[3]

# manual overide - turn off
        manual_off = manual_controls[4]


# run all rules
        turn_heater_on = aggregate_rules(bedtime, awake, manual_on, manual_off, somebody_home, operating_hours, temp_low)


# update db
        insert_stmt = """
        INSERT INTO heater_rules
        (dev_1, dev_2, dev_3, dev_4, temp, temp_low, operating_hours, anybody_home, heater_on)
        VALUES
        ({},{},{},{},{},{},{},{},{})""".format(time_since_connected[0], time_since_connected[1], time_since_connected[2], time_since_connected[3], temp, temp_low, operating_hours, somebody_home, turn_heater_on)

        insert_results(insert_stmt, db_host, db_host_port, db_user, db_pass, db)

        end = time.time()
        print(end-start)
#sleep
        time.sleep(30)

#### Need to update heater_rules table with additional override logic
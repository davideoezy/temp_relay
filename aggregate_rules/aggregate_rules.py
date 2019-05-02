
import time


db_host = '192.168.0.10'
db_host_port = '3306'
db_user = 'rpi'
db_pass = 'warm_me'
db = 'temp_logger'

def get_db_data(query, default, host, port, user, passwd, db):
    con = mariadb.connect(host=host, port=port, user=user,
                          password=passwd, database=db)
    cur = con.cursor()
    cur.execute(query)

    output = default

    for row in cur:
        output = row[0]

    return output

def get_db_data_multiple(query, host, port, user, passwd, db):
    con = mariadb.connect(host=host, port=port, user=user,
                          password=passwd, database=db)
    cur = con.cursor()
    cur.execute(query)

    output = [0,0,0,0]

    for row in cur:
        output = [row[0], row[1], row[2], row[3], row[4]]

    return output


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


# Below deprecated

if __name__ == "__main__":

    while True:
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
        manual_controls = get_db_data_multiple(query_manual_controls, db_host, db_host_port, db_user, db_pass, db)

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

        somebody_home = get_db_data(query_anybody_home, 0, db_host, db_host_port, db_user, db_pass, db)

# operating_hours check

        query_operating_hours = """
        SELECT
        operating_hours,
        FROM operating_hours
        where WHERE ts > DATE_SUB(now(), INTERVAL 90 second)
        ORDER BY ts ASC
        """

        operating_hours = get_db_data(query_operating_hours, 0, db_host, db_host_port, db_user, db_pass, db)

# check temperature rule
        query_temp_rule = """
        SELECT
        temp_low,
        FROM temp_rule
        where WHERE ts > DATE_SUB(now(), INTERVAL 90 second)
        ORDER BY ts ASC
        """

        temp_low = get_db_data(query_temp_rule, 0, db_host, db_host_port, db_user, db_pass, db)

# run all rules

        turn_heater_on = aggregate_rules(bedtime, awake, manual_on, manual_off, somebody_home, operating_hours, temp_low)

# update db

        insert_stmt = """
        INSERT INTO heater_rules
        (bedtime, awake, manual_on, manual_off, temp_low, operating_hours, anybody_home, heater_on)
        VALUES
        ({},{},{},{},{},{},{},{})""".format(bedtime, awake, manual_on, manual_off, temp_low, operating_hours, somebody_home, turn_heater_on)

<<<<<<< Updated upstream:aggregate_rules/aggregate_rules.py
        insert_results(insert_stmt, db_host, db_host_port, db_user, db_pass, db)

=======
        db_helper.db_data(
            query_type="insert", statement=insert_stmt)
        
>>>>>>> Stashed changes:aggregate_rules.py
        time.sleep(30)

# create table heater_rules (bedtime int, awake int, manual_on int, manual_off int, temp_low int, operating_hours int, anybody_home int, heater_on int, ts timestamp);
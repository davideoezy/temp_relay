#!/usr/bin/python3
import mysql.connector as mariadb
import numpy as np

def read_DB(*args):

    temperature = []
    query_string = """
    select temp
    from temp_logger.temperature
    where device in ("RPi_0","RPi_2")
    and ts > date_sub(now(), interval 60 second)
    """

    con = mariadb.connect(host='192.168.0.10', port='3306', user='pi_test', database='temp_logger')

    cur = con.cursor()

    cur.execute(query_string)

    for row in cur:
        temperature.append(row[0])

    con.close()

    return np.mean(temperature)

print(read_DB())

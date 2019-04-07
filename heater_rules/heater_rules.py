import mysql.connector as mariadb
import time
import datetime
import time

db_host = '192.168.0.10'
db_host_port = '3306'
db_user = 'rpi'
db_pass = 'warm_me'
db = 'temp_logger'

MorningOn = datetime.time(6, 30)
NightOff = datetime.time(22, 56)


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



while True:
    
    operating_hours = hours_operation(MorningOn, NightOff)

    query = """
    SELECT
    avg(temp)
    FROM temperature 
    WHERE ts > DATE_SUB(now(), INTERVAL 90 second)
    ORDER BY ts ASC
    """

    temp = get_db_data(query, db_host, db_host_port, db_user, db_pass, db)
    
    temp_low = temp_trigger(temp)
    
    insert_stmt = """
    INSERT INTO temp_rule (
    temp,
    temp_low,
    operating_hours)
    VALUES
    ({},{},{})""".format(
        temp,
        temp_low,
        operating_hours)

    insert_results(insert_stmt, db_host, db_host_port, db_user, db_pass, db)
    
    time.sleep(30)

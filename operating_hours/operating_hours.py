import datetime
import mysql.connector as mariadb
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

if __name__ == "__main__":

    while True:

        operating_hours = hours_operation(MorningOn, NightOff)

        insert_stmt = """
        insert into operating_hours
        (operating_hours, MorningOn, NightOff) values
        ({}, '{}', '{}')""".values(operating_hours, MorningOn, NightOff)

        insert_results(insert_stmt, db_host, db_host_port, db_user, db_pass, db)

        time.sleep(30)

## Create db table in temp_logger
# create table operating_hours (operating_hours int, MorningOn varchar(20), NightOff varchar(20), ts timestamp); 

import mysql.connector as mariadb
import time

db_host = '192.168.0.10'
db_host_port = '3306'
db_user = 'rpi'
db_pass = 'warm_me'
db = 'temp_logger'

def get_db_data(query, host, port, user, passwd, db):
    con = mariadb.connect(host=host, port=port, user=user,
                          password=passwd, database=db)
    cur = con.cursor()
    cur.execute(query)

    output = 999

    for row in cur:
        output = row[0]

    return output

def temp_trigger(temp, threshold):

    temp_low = 0

    if temp < threshold:
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


if __name__ == "__main__":

    while True:
        query = """
        SELECT
        avg(temp)
        FROM temperature 
        WHERE ts > DATE_SUB(now(), INTERVAL 90 second)
        ORDER BY ts ASC
        """

        temp = get_db_data(query, db_host, db_host_port, db_user, db_pass, db)

        query_manual_temp = """
        SELECT
        temp_setting,
        FROM manual_temp 
        ORDER BY ts ASC
        """

        manual_temp = get_db_data(query_manual_temp, db_host, db_host_port, db_user, db_pass, db)

        temp_low = temp_trigger(temp, manual_temp)

        insert_stmt = """
        INSERT INTO temp_rule
        (temp_low, temp, threshold)
        VALUES
        ({},{},{})""".format(temp_low, temp, threshold)

        insert_results(insert_stmt, db_host, db_host_port, db_user, db_pass, db)

        time.sleep(30)

## create table temp_rule (temp_low int, temp float, threshold float, ts timestamp);

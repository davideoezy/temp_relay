from gpiozero import LED
from time import sleep
import mysql.connector as mariadb
import time

db_host = '192.168.0.10'
db_host_port = '3306'
db_user = 'rpi'
db_pass = 'warm_me'
db = 'temp_logger'


relay = LED(17)


def get_db_data(query, host, port, user, passwd, db):
    con = mariadb.connect(host=host, port=port, user=user,
                          password=passwd, database=db)
    cur = con.cursor()
    cur.execute(query)

    output = 999

    for row in cur:
        output = row[0]

    return output


if __name__ == "__main__":
    while True:

        query = """
        SELECT
        heater_on
        FROM heater_rules; 
        WHERE ts > DATE_SUB(now(), INTERVAL 60 second)
        ORDER BY ts ASC
        """

        operate = get_db_data(query, db_host, db_host_port, db_user, db_pass, db)

        if operate = 1:
            relay.on()
        else:
            relay.off()
        
        time.sleep(30)

        
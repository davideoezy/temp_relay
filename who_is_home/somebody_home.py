import subprocess
import arpreq
import time
import mysql.connector as mariadb

db_host = '192.168.0.10'
db_host_port = '3306'
db_user = 'rpi'
db_pass = 'warm_me'
db = 'temp_logger'

wifi_interface = "enp3s0"

def whos_home(devices):
    
    home_list = [(time.time(),0)] * devices

    for ip in range(0,devices):
        test = arpreq.arpreq('192.168.0.' + str(ip+51))
        if test is not None:
            home_list[ip] = time.time(),1

    return home_list

def last_time_seen(current_reading, prev_log, devices):

    last_seen = [0] * devices

    for ip in range(0,devices):
        if current_reading[ip][1] == 1:
            last_seen[ip] = time.time()
        elif current_reading[ip][1] == 0:
            last_seen[ip] = prev_log[ip]

    return last_seen                

def time_since_seen(last_seen, devices):

    duration = [0] * devices

    for ip in range(0,devices):
        duration[ip] = round((time.time() - last_seen[ip])/60)
        if duration[ip] > 999: duration[ip] = 999

    return duration

def anybody_home(time_since_connected):
    somebody_home = 0

    if any(t < 20 for t in time_since_connected):
        somebody_home = 1
    
    return somebody_home

if __name__ == "__main__":

    devices = 4
    last_seen_prev = [(time.time() - 7200)] * devices

    while True:
        
        home_list_curr = whos_home(devices)

        last_seen_curr = last_time_seen(home_list_curr, last_seen_prev, devices)

        time_since_connected = time_since_seen(last_seen_curr, devices)

        somebody_home = anybody_home(time_since_connected)

        last_seen_prev = last_seen_curr[:]

        insert_stmt = """
        INSERT INTO somebody_home
        (dev_1, dev_2, dev_3, dev_4, anybody_home)
        VALUES
        ({},{},{},{},{})""".format(time_since_connected[0], time_since_connected[1], time_since_connected[2], time_since_connected[3], somebody_home)

        con = mariadb.connect(host=db_host, port=db_host_port,
                              user=db_user, password=db_pass, database=db)
        cur = con.cursor()
        try:
            cur.execute(insert_stmt)
            con.commit()
        except:
            con.rollback()
        con.close()

        # Every 20 iterations run nmap to remove entries not present

        if counter == 20:
            os.system("nmap -sn 192.168.0.51-54")
            counter = 0

        counter += 1
        
        time.sleep(30)

    

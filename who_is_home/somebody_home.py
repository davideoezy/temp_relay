import os
import time

db_host = '192.168.0.10'
db_host_port = '3306'
db_user = 'rpi'
db_pass = 'warm_me'
db = 'temp_logger'


def last_seen(time_last_seen):

    for ip in range(0,3):
        hostname = '192.168.0.'+str(ip+51)
        response = os.system("ping -c 1 " + hostname)

        if response == 0:
            time_last_seen[ip] = time.time()

    return time_last_seen


def time_since(time_last_seen):
    
    time_last_seen = last_seen(time_last_seen)

    for ip in range(0, 3):
        time_since_last_seen[ip] = (time.time() - time_last_seen[ip])/60

    return time_since_last_seen

def anybody_home(time_last_seen):
    somebody_home = False

    check = time_since(time_last_seen)

    if any(t < 20 for t in check):
        somebody_home = True

    return somebody_home

if __name__ == "__main__":
    
    time_last_seen = [time.time()-7200] * 3
    
    while True:
        
        time_since_last_seen = time_since(time_last_seen)
        somebody_home = anybody_home(time_last_seen)
        
        insert_stmt = """
        INSERT INTO somebody_home
        (dev_1, dev_2, dev_3, anybody_home)
        VALUES
        ({},{},{},{})""".format(time_since_last_seen[0], time_since_last_seen[1], time_since_last_seen[2], somebody_home)

        con = mariadb.connect(host=db_host, port=db_host_port,
                              user=db_user, password=db_pass, database=db)
        cur = con.cursor()
        try:
            cur.execute(insert_stmt)
            con.commit()
        except:
            con.rollback()
        con.close()
        time.sleep(30)

    






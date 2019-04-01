import os
import time


def last_seen(time_last_seen):

    time_since_last_seen = [999]*9

    for ip in range(0,9):
        hostname = '192.168.0.'+str(ip+51)
        response = os.system("ping -c 1 " + hostname)

        if response == 0:
            time_last_seen[ip] = time.time()

            time_since_last_seen[ip] = (time.time() - time_last_seen[ip])/60

    return time_since_last_seen

def anybody_home(time_last_seen):
    somebody_home = False

    check = last_seen(time_last_seen)

    if any(t < 20 for t in time_last_seen):
        somebody_home = True

    return somebody_home

if __name__ == "__main__":
    
    time_last_seen_init = [time.time()-7200] * 10
    
    while True:
        somebody_home = anybody_home(time_last_seen_init)
        time.sleep(60)

    






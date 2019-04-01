import os
import time


def last_seen():

    time_last_seen = [time.time()-7200] * 10
    last_seen = [999] * 10

    for ip in range(1:10):
        hostname = '192.168.0.'+str(ip+50)
        response = os.system("ping -c 1 " + hostname)

        if response == 0:
            time_last_seen[ip] = time.time()

        last_seen[ip] = (time.time() - time_last_seen[ip])/60

    return last_seen

def anybody_home():
    somebody_home = False

    check = last_seen()

    if any(t < 20 for t in check):
        somebody_home = True

    return somebody_home

if __name__ == "__main__":
    somebody_home = anybody_home()

    






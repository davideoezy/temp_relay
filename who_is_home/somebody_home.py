import os
import time


def last_seen(time_last_seen):

    for ip in range(1,10):
        hostname = '192.168.0.'+str(ip+50)
        response = os.system("ping -c 1 " + hostname)

        list_item = (ip - 1)
        
        if response == 0:
            time_last_seen[list_item] = time.time()

        last_seen[list_item] = (time.time() - time_last_seen[list_item])/60

    return last_seen

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

    






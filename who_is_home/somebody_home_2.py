import subprocess
import arpreq
import time

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
        duration[ip] = round(((time.time() - last_seen[ip])/60),1)

    return duration

def anybody_home(time_since_connected):
    somebody_home = False

    if any(t < 20 for t in time_since_connected):
        somebody_home = True
    
    return somebody_home

if __name__ == "__main__":

    devices = 3
    last_seen_prev = [(time.time() - 10)] * devices

    while True:
        home_list_curr = whos_home(devices)

        last_seen_curr = last_time_seen(home_list_curr, last_seen_prev, devices)

        time_since_connected = time_since_seen(last_seen_curr, devices)

        somebody_home = anybody_home(time_since_connected)

        print(home_list_curr, time_since_connected, somebody_home)

        last_seen_prev = last_seen_curr
        time.sleep(30)

    

import subprocess
import arpreq
import time

wifi_interface = "enp3s0"

def whos_home(devices):
    
    home_list = [time.time(),0] * devices

    for ip in range(0,devices):
        test = arpreq.arpreq('192.168.0.' + str(ip+51))
        if test is not None:
            home_list[ip] = time.time(),1

    return home_list

def time_since_seen(prev_reading, current_reading, prev_log, devices):

    last_seen = [0] * devices

    for ip in range(0,devices):
        if current_reading[ip][1] == 1:
            last_seen[ip] = time.time()
        elif current_reading[ip][1] == 0:
            last_seen[ip] = prev_log[ip]
    return last_seen                

if __name__ == "__main__":

    devices = 1

    home_list_prev = [0] * devices
    home_list_curr = whos_home(devices)

    prev_log = (time.time() - 10) * devices

    curr_log = time_since_seen(home_list_prev, home_list_curr, prev_log, devices)




    #prev_log = curr_log

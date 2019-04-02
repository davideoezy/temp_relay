import subprocess
import arpreq
import time

wifi_interface = "enp3s0"
devices = 4

def whos_home(devices):
    home_list = [False] * devices

    for ip in range(0,devices):
        test = arpreq.arpreq("'192.168.0." + str(ip+51) + "'")
        if test is None = False:
            home_list[ip] = True

    return time.time(), home_list


import subprocess
interface = "wlp3s0"

try:
    proc = subprocess.Popen(["iwconfig",interface],stdout=subprocess.PIPE, universal_newlines=True)
    out, err = proc.communicate()
    WIFI = 0
    wifi_ssid = ""
    for line in out.split("\n"):
        if("Quality" in line):
            line = line.replace("Link Quality=","")
            quality = line.split()[0].split('/')
            WIFI = int(round(float(quality[0]) / float(quality[1]) * 100))
            CurrentWIFI = WIFI
    for line in out.split("\n"):
        if("ESSID" in line):
            line = line.replace("wlp3s0    IEEE 802.11  ESSID:","")
            wifi_ssid = line.replace('"',"")
except:
    print("WIFI READOUT ERROR!")

try:
    proc = subprocess.Popen(["ifconfig",interface],stdout=subprocess.PIPE, universal_newlines=True)
    out, err = proc.communicate()
    IP = ""
    for line in out.split("\n"):
        if("192.168" in line):
            strings = line.split(" ")
            IP = strings[9]
except:
    print("WIFI READOUT ERROR!")

print(CurrentWIFI,wifi_ssid,IP)

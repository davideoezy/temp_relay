from gpiozero import LED
from time import sleep
from db_helper import db_helper
import time

db_helper = db_helper()

relay = LED(17)

if __name__ == "__main__":
    while True:

        operate = db_helper.get_operate()

        if operate == 1:
            relay.on()
        else:
            relay.off()

        db_helper.insert_log()
        
        time.sleep(10)

        

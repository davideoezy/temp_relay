from gpiozero import LED
from time import sleep
from db_helper import db_helper
from mqtt_helper import mqtt_helper
import time

relay = LED(17)
location = "heater_relay"

db_helper = db_helper()
mqtt_helper = mqtt_helper(location)

if __name__ == "__main__":
    while True:

        operate = db_helper.get_operate()

        if operate == 1:
            relay.on()
        else:
            relay.off()

        statement = """
                    INSERT INTO heater_log
                    (heater_on)
                    VALUES
                    ({})""".format(operate)

        db_helper.insert_db_data(statement)

        mqtt_helper.publish_status()
        
        time.sleep(10)

        

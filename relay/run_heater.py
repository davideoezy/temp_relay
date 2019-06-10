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

        statement = """
                    INSERT INTO heater_log
                    (heater_on)
                    VALUES
                    ({})""".format(operate)

        db_helper.insert_db_data(statement)
        
        time.sleep(10)

        

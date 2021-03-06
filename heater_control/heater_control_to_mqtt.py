from mqtt_helper import mqtt_helper
from db_helper import db_helper
import time

location = "heater_controls"

mqtt_helper = mqtt_helper(location)
db_helper = db_helper()

topic_heater_controls = "home/inside/heater_control"

while True:

    controls = db_helper.get_control_settings()

    power = controls[1]
    TargetTemp = controls[0]

    mqtt_helper.publish_controls(TargetTemp,power)
    mqtt_helper.publish_status()

    time.sleep(30)

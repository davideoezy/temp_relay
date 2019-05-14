import datetime
import time
from db_helper import db_helper

MorningOn = datetime.time(6, 30)
NightOff = datetime.time(22, 56)

class rules():

    def hours_operation(self, on_time, off_time):

        CurrentTime = datetime.datetime.now()

        MorningOnTime = CurrentTime.replace(
            hour=on_time.hour, minute=on_time.minute, second=on_time.second)

        NightOffTime = CurrentTime.replace(
            hour=off_time.hour, minute=off_time.minute, second=off_time.second)

        operating_hours = 0

        if(CurrentTime > MorningOnTime and CurrentTime < NightOffTime):
            operating_hours = 1

        return operating_hours
    
    def temp_trigger(self, temp, threshold):

        temp_low = 0

        if temp < threshold:
            temp_low = 1

        return temp_low

    def anybody_home(self, time_since_connected):
        somebody_home = 0

        if any(t < 20 for t in time_since_connected):
            somebody_home = 1

        return somebody_home
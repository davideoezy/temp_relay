import datetime
import time
from db_helper import db_helper

MorningOn = datetime.time(6, 30)
NightOff = datetime.time(22, 56)

class operating_hours():

    def hours_operation(on_time, off_time):

        CurrentTime = datetime.datetime.now()

        MorningOnTime = CurrentTime.replace(
            hour=on_time.hour, minute=on_time.minute, second=on_time.second)

        NightOffTime = CurrentTime.replace(
            hour=off_time.hour, minute=off_time.minute, second=off_time.second)

        operating_hours = 0

        if(CurrentTime > MorningOnTime and CurrentTime < NightOffTime):
            operating_hours = 1

        return operating_hours


if __name__ == "__main__":

    operating_hours = operating_hours()
    db_helper = db_helper()

    while True:

        operating_hours = operating_hours.hours_operation(MorningOn, NightOff)

        insert_stmt = """
        insert into operating_hours
        (operating_hours, MorningOn, NightOff) values
        ({}, '{}', '{}')""".values(operating_hours, MorningOn, NightOff)

        db_helper.db_data(query_type="insert", statement=insert_stmt)

        time.sleep(30)

## Create db table in temp_logger
# create table operating_hours (operating_hours int, MorningOn varchar(20), NightOff varchar(20), ts timestamp); 

# Will probably need to strftime the MorningOn, NightOff times for sql insert

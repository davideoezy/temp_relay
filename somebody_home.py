
import time
import arpreq
from db_helper import db_helper


class anybody_home():
    def __init__(self):
        self.devices = 4
        self.last_seen_prev = [(time.time() - 7200)] * self.devices

    def whos_home(self):

        home_list = [(time.time(), 0)] * self.devices

        for ip in range(0, self.devices):
            test = arpreq.arpreq('192.168.0.' + str(ip+51))
            if test is not None:
                home_list[ip] = time.time(), 1

        return home_list

    def last_time_seen(self, current_reading, prev_log):

        last_seen = [0] * self.devices

        for ip in range(0, self.devices):
            if current_reading[ip][1] == 1:
                last_seen[ip] = time.time()
            elif current_reading[ip][1] == 0:
                last_seen[ip] = self.last_seen_prev[ip]

        return last_seen

    def time_since_seen(self, last_seen):

        duration = [0] * self.devices

        for ip in range(0, self.devices):
            duration[ip] = round((time.time() - last_seen[ip])/60)
            if duration[ip] > 999:
                duration[ip] = 999

        return duration

    def anybody_home(self, time_since_connected):
        somebody_home = 0

        if any(t < 20 for t in time_since_connected):
            somebody_home = 1

        return somebody_home


if __name__ == "__main__":

    db_helper = db_helper()
    anybody_home = anybody_home()

    while True:
        home_list_curr = anybody_home.whos_home()

        last_seen_curr = anybody_home.last_time_seen(
            home_list_curr)

        time_since_connected = anybody_home.time_since_seen(last_seen_curr)

        somebody_home = anybody_home.anybody_home(time_since_connected)

        anybody_home.last_seen_prev = last_seen_curr[:]

        insert_stmt = """
        INSERT INTO somebody_home
        (dev_1, dev_2, dev_3, dev_4, anybody_home)
        VALUES
        ({},{},{},{},{})""".format(time_since_connected[0], time_since_connected[1], time_since_connected[2], time_since_connected[3], somebody_home)

        db_helper.db_data(query_type="insert", statement=insert_stmt)

        time.sleep(30)

# create table anybody_home (anybody_home int, dev_1 float, dev_2 float, dev_3 float, dev_4 float, ts timestamp);

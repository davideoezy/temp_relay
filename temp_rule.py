from db_helper import db_helper
import time

def temp_trigger(temp, threshold):

    temp_low = 0

    if temp < threshold:
        temp_low = 1

    return temp_low




if __name__ == "__main__":

    db_helper = db_helper()

    while True:
        query = """
        SELECT
        avg(temp)
        FROM temperature 
        WHERE ts > DATE_SUB(now(), INTERVAL 90 second)
        ORDER BY ts ASC
        """

        temp = db_helper.db_data(
            query_type="select", n_variables=1, statemment=query, default=-999)

        query_manual_temp = """
        SELECT
        temp_setting,
        FROM heater_controls 
        ORDER BY ts ASC
        """

        manual_temp = db_helper.db_data(
            query_type="select", n_variables=1, statemment=query_manual_temp, default=0)

        temp_low = temp_trigger(temp, manual_temp)

        insert_stmt = """
        INSERT INTO temp_rule
        (temp_low, temp, threshold)
        VALUES
        ({},{},{})""".format(temp_low, temp, manual_temp)

        db_helper.db_data(query_type="insert", statemment=insert_stmt)
        
        time.sleep(30)

## create table temp_rule (temp_low int, temp float, threshold float, ts timestamp);

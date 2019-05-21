import mysql.connector as mariadb
import datetime
import tzlocal

####### TO_DO ########

# change select statement to get most recent record
# select top 1/limit 1
# order by DESC

class db_helper():
    def __init__(self):
        self.db_host = '192.168.0.10'
        self.db_host_port = '3306'
        self.db_user = 'rpi'
        self.db_pass = 'warm_me'
        self.db = 'temp_logger'
        self.local_timezone = tzlocal.get_localzone()

    def db_data(self, n_variables, statement, default):

        con = mariadb.connect(host=self.db_host, port=self.db_host_port, user=self.db_user,
                              password=self.db_pass, database=self.db)
        cur = con.cursor()

        cur.execute(statement)

        if n_variables == 1:
            output = default

            for row in cur:
                output = row[0]
            
            return output

        elif n_variables > 1:
            output = [default] * n_variables

            for row in cur:
                output = row

            return output
    
    def insert_db_data(self, statement):

        con = mariadb.connect(host=self.db_host, port=self.db_host_port, user=self.db_user,
                              password=self.db_pass, database=self.db)
        cur = con.cursor()

        try:
            cur.execute(statement)
            con.commit()
        except:
            con.rollback()
        con.close()

        return

    def get_temp(self):
        n_variables = 1
        statement = """
                        SELECT
                        avg(temp)
                        FROM temperature 
                        WHERE ts > DATE_SUB(now(), INTERVAL 90 second)
                        ORDER BY ts ASC
                        """
        default = 99

        return self.db_data(n_variables = n_variables, statement = statement, default = default)

    def get_control_settings(self):
        n_variables = 2
        statement = """
                    SELECT
                    temp_setting,
                    power
                    FROM heater_controls 
                    ORDER BY ts DESC
                    limit 1
                    """

        default = 0

        return self.db_data(n_variables = n_variables, statement = statement, default = default)

    def get_heat_indicator(self):
        n_variables = 1
        statement = """
                    SELECT
                    heater_on
                    FROM heater_log
                    ORDER BY ts DESC
                    limit 1
                    """
        default = 0

        return self.db_data(n_variables = n_variables, statement = statement, default = default)

    def insert_control_settings(self, temperature, power):
        statement = """
                    INSERT into heater_controls
                    (temp_setting,
                    power)
                    VALUES
                    ({},{})""".format(temperature, power)
        
        self.insert_db_data(statement)

        return

    def get_temps(self):
        statement1 = """
                    SELECT
                    UNIX_TIMESTAMP(ts) as time,
                    temp as value,
                    device as metric
                    FROM temperature
                    where ts > DATE_SUB(now(), INTERVAL 12 hour)
                    and device = 'RPi_1'
                    ORDER BY ts asc
                    """
    
        statement2 = """
                    SELECT
                    UNIX_TIMESTAMP(ts) as time,
                    air_temp,
                    apparent_t as feels_like
                    FROM outside_conditions
                    where ts > DATE_SUB(now(), INTERVAL 12 hour)
                    ORDER BY ts ASC
                    """
        
        con = mariadb.connect(host=self.db_host, port=self.db_host_port, user=self.db_user,
                              password=self.db_pass, database=self.db)
        cur = con.cursor()

        cur.execute(statement1)

        temps = []

        for row in cur:
            unix_timestamp = row[0]
            local_time = datetime.datetime.fromtimestamp(
                unix_timestamp, self.local_timezone)

            ins = {
                'ts': local_time,
                'temp': row[1],
                'air_temp': None,
                'feels_like': None}
            temps.append(ins)
        
        cur = con.cursor()

        cur.execute(statement2)

        for row in cur:
            unix_timestamp = row[0]
            local_time = datetime.datetime.fromtimestamp(
                unix_timestamp, self.local_timezone)

            outs = {
                'ts': local_time,
                'temp': None,
                'air_temp': row[1],
                'feels_like': row[2]}
            temps.append(outs)

        return temps





    def get_outside_temps(self):
        statement = """
                SELECT
                UNIX_TIMESTAMP(ts) as time,
                air_temp,
                apparent_t as feels_like
                FROM outside_conditions
                where ts > DATE_SUB(now(), INTERVAL 12 hour)
                ORDER BY ts ASC
                """

        con = mariadb.connect(host=self.db_host, port=self.db_host_port, user=self.db_user,
                            password=self.db_pass, database=self.db)
        cur = con.cursor()

        cur.execute(statement)

        outside = []
        for row in cur:
            unix_timestamp = row[0]
            local_time = datetime.datetime.fromtimestamp(
                unix_timestamp, self.local_timezone)

            outs = {
                'ts': local_time,
                'air_temp': row[1],
                'feels_like': row[2]}
            outside.append(outs)
        return outside


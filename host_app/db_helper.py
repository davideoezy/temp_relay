import mysql.connector as mariadb

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
        default = 0

        return self.db_data(n_variables = n_variables, statement = statement, default = default)

    def get_control_settings(self):
        n_variables = 5
        statement = """
                    SELECT
                    temp_setting,
                    manual_on,
                    manual_off
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

    def insert_control_settings(self, temperature, manual_on, manual_off):
        statement = """
                    INSERT into heater_controls
                    (temp_setting,
                    manual_on,
                    manual_off)
                    VALUES
                    ({},{},{},{},{})""".format(temperature, manual_on, manual_off)
        
        self.insert_db_data(statement)

        return



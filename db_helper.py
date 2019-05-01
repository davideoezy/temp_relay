
import mysql.connector as mariadb

class db_helper():
    def __init__(self):
        self.db_host = '192.168.0.10'
        self.db_host_port = '3306'
        self.db_user = 'rpi'
        self.db_pass = 'warm_me'
        self.db = 'temp_logger'

    def db_data(self, query_type, n_variables, statement, default):

        con = mariadb.connect(host=self.db_host, port=self.db_host_port, user=self.db_user,
                            password=self.db_pass, database=self.db)
        cur = con.cursor()
        
        if query_type == 'select':

            cur.execute(statement)

            if n_variables == 1:
                output = default

                for row in cur:
                    output = row[0]

            else:
                output = [default] * n_variables
            
                for row in cur:
                    for item in row:
                        output = [row[item]]
            
            return output

        elif query_type == 'insert':
            try:
                cur.execute(statement)
                con.commit()
            except:
                con.rollback()
            con.close()
        
            return




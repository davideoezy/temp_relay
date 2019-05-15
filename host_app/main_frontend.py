from db_helper import db_helper
from web_app_helper import ThermostatWeb

db_helper = db_helper()

web = ThermostatWeb(db_helper)

web.run()

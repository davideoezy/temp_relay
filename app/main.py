from db_helper import db_helper
from web_app_helper import ThermostatWeb

db_helper = db_helper()

app = ThermostatWeb(db_helper)


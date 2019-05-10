

class rules_aggregator():

    def __init__(self):
        self.on_rule_list = []

    def aggregate_rules(self, manual_on, manual_off, somebody_home, operating_hours, temp_low):

        self.on_rule_list.extend([manual_on, somebody_home, temp_low, operating_hours])

        if manual_off == 1:
            heater_on = 0
        elif all(i is 1 for i in self.on_rule_list):
            heater_on = 1
        else:
            heater_on = 0

        return heater_on


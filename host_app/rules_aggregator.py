

class rules_aggregator():

    def __init__(self):
        self.on_rule_list = []

    def aggregate_rules(self, power, somebody_home, operating_hours, temp_low):

         self.on_rule_list.extend(
             [power, somebody_home, operating_hours, temp_low])

        heater_on = 0
        
        if all(i is 1 for i in self.on_rule_list):
            heater_on = 1


        return heater_on


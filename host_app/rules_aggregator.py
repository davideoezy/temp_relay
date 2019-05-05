

class rules_aggregator():

    def __init__(self):
        self.override_off_rules = []
        self.override_on_rules = []
        self.manual_on_rule_list = []
        self.automated_rule_list = []

    def aggregate_rules(self, bedtime, awake, manual_on, manual_off, somebody_home, operating_hours, temp_low):

        self.override_off_rules.extend([bedtime, manual_off])
        self.override_on_rules.extend([awake, manual_on])

        if any(i is 1 for i in self.override_off_rules):
            override_off = 1
        else:
            override_off = 0

        if any(i is 1 for i in self.override_on_rules):
            override_on = 1
        else:
            override_on = 0

        self.manual_on_rule_list.extend([override_on, somebody_home, temp_low])
        self.automated_rule_list.extend(
            [somebody_home, operating_hours, temp_low])

        if all(i is 1 for i in self.override_off_rules):
            heater_on = 0
        elif all(i is 1 for i in self.manual_on_rule_list):
            heater_on = 1
        elif all(i is 1 for i in self.automated_rule_list):
            heater_on = 1
        else:
            heater_on = 0

        return heater_on


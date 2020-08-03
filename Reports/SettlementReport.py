class SettlementReport:

    def generate_report_data(self, report_group, expenses_list):
        users = {}

        for expense in expenses_list:
            payer_id = expense[0]
            group = expense[1]
            amount = expense[2]
            settlement_id = expense[3]

            if settlement_id == 1:
                to_settle = self.settle_by_percent(report_group, payer_id, group, amount)

            elif settlement_id == 2:
                to_settle = self.settle_by_amount(report_group, payer_id, group, amount)
            else:
                raise
            for k in to_settle:
                if k in users:
                    for m in to_settle[k]:
                        if m in users[k]:
                            users[k][m] = users[k][m] + to_settle[k][m]
                        else:
                            users[k][m] = to_settle[k][m]
                else:
                    users[k] = to_settle[k]
        users = self.clean_up_dict_of_dicts(users)
        for k in users:
            for m in users[k]:
                users[k][m] = round(users[k][m], 2)
        return users

    def settle_by_percent(self, report_group, payer_id, group, amount):
        group.sort(key=lambda tup: tup[0])
        to_settle = {}

        for member in group:
            member_id = member[1]
            member_percent = member[2]

            if payer_id in report_group and member_id != payer_id:
                outcome = member_percent * amount / 100
                to_settle = self.add_element_to_dict_of_dicts(payer_id, member_id, outcome, to_settle)
            elif payer_id not in report_group and member_id in report_group:
                outcome = member_percent * amount / 100
                to_settle = self.add_element_to_dict_of_dicts(payer_id, member_id, outcome, to_settle)
                break
        return to_settle

    def settle_by_amount(self, report_group, payer_id, group, amount):
        group.sort(key=lambda tup: tup[0])
        to_settle = {}

        for i, member in enumerate(group):
            member_id = member[1]
            member_amount = member[2]

            if amount <= 0:
                break
            if payer_id in report_group:
                if (i == len(group) - 1) or member_amount >= amount:
                    outcome = amount
                    amount = 0
                else:
                    outcome = member_amount
                    amount = amount - member_amount
                if member_id != payer_id:
                    to_settle = self.add_element_to_dict_of_dicts(payer_id, member_id, outcome, to_settle)
            elif payer_id not in report_group:
                if i == len(group) - 1 or member_amount >= amount:
                    outcome = amount
                    amount = 0
                else:
                    outcome = member_amount
                    amount = amount - member_amount
                if member_id in report_group:
                    to_settle = self.add_element_to_dict_of_dicts(payer_id, member_id, outcome, to_settle)
        return to_settle

    def add_element_to_dict_of_dicts(self, first_key, second_key, element, dictionary):
        if first_key in dictionary:
            if second_key in dictionary[first_key]:
                dictionary[first_key][second_key] = dictionary[first_key][second_key] + element
            else:
                dictionary[first_key][second_key] = element
        else:
            dictionary[first_key] = {}
            dictionary[first_key][second_key] = element
        return dictionary

    def clean_up_dict_of_dicts(self, dictionary):
        cleaned_dictionary = dictionary
        for key in cleaned_dictionary:
            for first_key in dictionary:
                if key in dictionary[first_key] and first_key in cleaned_dictionary[key]:
                    if cleaned_dictionary[key][first_key] > dictionary[first_key][key]:
                        cleaned_dictionary = \
                            self.add_element_to_dict_of_dicts(key, first_key,
                                                              dictionary[first_key][key] * -1, cleaned_dictionary)
                        cleaned_dictionary[first_key].pop(key)
                    elif cleaned_dictionary[key][first_key] < dictionary[first_key][key]:
                        cleaned_dictionary = \
                            self.add_element_to_dict_of_dicts(first_key, key,
                                                              cleaned_dictionary[key][first_key] * -1, dictionary)
                        cleaned_dictionary[key].pop(first_key)
                    else:
                        cleaned_dictionary[first_key].pop(key)
                        cleaned_dictionary[key].pop(first_key)
        return cleaned_dictionary

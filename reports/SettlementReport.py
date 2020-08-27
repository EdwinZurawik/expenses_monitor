from database_manager.DatabaseManager import DatabaseManager


class SettlementReport:
    manager = DatabaseManager()

    def get_data_from_db(self, account_id, report_group_id, date_from, date_to):
        expenses_list = self.manager.get_all_expenses_between_dates(account_id, date_from, date_to)
        report_group = self.manager.get_all_users_from_group(report_group_id)
        report_data = {'report_group': report_group, 'expenses': []}

        for expense in expenses_list:
            group = self.manager.get_all_users_from_group(expense['group_id'])

            report_data['expenses'].append(
                {
                    'payer_id': expense['user_id'],
                    'group': group,
                    'amount': expense['amount'],
                    'settlement_type_id': expense['settlement_type_id']
                }
            )
        return report_data

    def generate_report_data(self, account_id, report_group_id, date_from, date_to):
        users = {}
        report_data = self.get_data_from_db(account_id, report_group_id, date_from, date_to)
        for row in report_data['expenses']:
            if row['settlement_type_id'] == 1:
                to_settle = self.settle_by_percent(report_data['report_group'], row['payer_id'], row['group'], row['amount'])
            elif row['settlement_type_id'] == 2:
                to_settle = self.settle_by_amount(report_data['report_group'], row['payer_id'], row['group_id'], row['amount'])
            else:
                continue
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
        to_settle = {}

        for member in group:
            member_id = member['user_id']
            member_percent = member['amount']

            member_ids = []
            for report_group_member in report_group:
                member_ids.append(report_group_member['user_id'])
            if payer_id in member_ids and member_id != payer_id:
                outcome = member_percent * amount / 100
                to_settle = self.add_element_to_dict_of_dicts(payer_id, member_id, outcome, to_settle)
            elif payer_id not in member_ids and member_id in member_ids:
                outcome = member_percent * amount / 100
                to_settle = self.add_element_to_dict_of_dicts(payer_id, member_id, outcome, to_settle)
                break
        return to_settle

    def settle_by_amount(self, report_group, payer_id, group, amount):
        to_settle = {}

        for i, member in enumerate(group):
            member_id = member[1]
            member_amount = member[2]

            member_ids = []
            for report_group_member in report_group:
                member_ids.append(report_group_member['user_id'])

            if amount <= 0:
                break
            if payer_id in member_ids:
                if (i == len(group) - 1) or member_amount >= amount:
                    outcome = amount
                    amount = 0
                else:
                    outcome = member_amount
                    amount = amount - member_amount
                if member_id != payer_id:
                    to_settle = self.add_element_to_dict_of_dicts(payer_id, member_id, outcome, to_settle)
            elif payer_id not in member_ids:
                if i == len(group) - 1 or member_amount >= amount:
                    outcome = amount
                    amount = 0
                else:
                    outcome = member_amount
                    amount = amount - member_amount
                if member_id in member_ids:
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

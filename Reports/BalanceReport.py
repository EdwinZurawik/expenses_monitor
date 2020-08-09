from DatabaseManagement.DatabaseManager import DatabaseManager

class BalanceReport:
    manager = DatabaseManager()

    def get_data_from_db(self, account_id, report_group_id, date_from, date_to):
        operations_list = self.manager.get_all_expenses_between_dates(account_id, date_from, date_to)
        operations_list.extend(self.manager.get_all_incomes_between_dates(account_id, date_from, date_to))
        report_group = self.manager.get_all_users_from_group(report_group_id)
        report_data = {'report_group': report_group, 'operations': []}

        for operation in operations_list:
            settlement_type_id = operation['settlement_type_id']
            group = self.manager.get_settlement_rule_users(operation['settlement_rule_id'])
            category_type_id = self.manager.get_category(operation['category_id'])['category_type_id']

            report_data['operations'].append(
                {
                    'category_id': operation['category_id'],
                    'category_type_id': category_type_id,
                    'group': group,
                    'amount': operation['amount'],
                    'settlement_type_id': settlement_type_id
                }
            )
        return report_data

    def generate_report_data(self, account_id, report_group_id, date_from, date_to):
        categories = {}  # categories[category_type] = (category_id, amount)
        report_data = self.get_data_from_db(account_id, report_group_id, date_from, date_to)

        for operation in report_data['operations']:
            category_type = operation['category_type_id']
            category_id = operation['category_id']
            group = operation['group']
            amount = operation['amount']
            settlement_type_id = operation['settlement_type_id']

            member_ids = []
            for report_group_member in report_data['report_group']:
                member_ids.append(report_group_member['user_id'])

            for user_id in member_ids:
                if category_type in [1, 2]:
                    if settlement_type_id == 1:
                        balance = self.calculate_by_percent(user_id, group, amount)
                    elif settlement_type_id == 2:
                        balance = self.calculate_by_amount(user_id, group, amount)
                    else:
                        continue
                else:
                    continue
                if balance != 0:
                    category_list = [category_type, balance]
                    if category_id in categories:
                        categories[category_id][1] = categories[category_id][1] + balance
                    else:
                        categories[category_id] = category_list
        for k, v in categories.items():
            v[1] = round(v[1], 2)
        return categories

    def calculate_by_percent(self, user_id, group, amount):  # for expenses and incomes
        balance = 0

        for member in group:
            member_id = member['user_id']
            member_percent = member['amount']

            if user_id == member_id:
                balance = member_percent * amount / 100
                break

        return balance

    def calculate_by_amount(self, user_id, group, amount):
        balance = 0

        for i, member in enumerate(group):
            member_id = member['user_id']
            member_amount = member['amount']

            if amount <= 0:
                break

            if i == len(group) - 1 or member_amount >= amount:
                outcome = amount
                amount = 0
            else:
                outcome = member_amount
                amount = amount - member_amount
            if user_id == member_id:
                balance = outcome
                break
        return balance

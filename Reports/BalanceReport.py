class BalanceReport:

    def generate_report_data(self, report_group, operations_list):
        categories = {}  # categories[category_type] = (category_id, amount)

        for operation in operations_list:
            category_type = operation[0]
            category_id = operation[1]
            group = operation[2]
            amount = operation[3]
            settlement_type = operation[4]

            for user_id in report_group:
                if category_type in [1, 2]:
                    if settlement_type == 1:
                        balance = self.calculate_by_percent(user_id, group, amount)
                    elif settlement_type == 2:
                        balance = self.calculate_by_amount(user_id, group, amount)
                    else:
                        raise
                else:
                    raise
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

        group.sort(key=lambda tup: tup[0])
        balance = 0

        for member in group:
            member_id = member[1]
            member_percent = member[2]

            if user_id == member_id:
                balance = member_percent * amount / 100
                break

        return balance

    def calculate_by_amount(self, user_id, group, amount):

        group.sort(key=lambda tup: tup[0])
        balance = 0

        for i, member in enumerate(group):
            member_id = member[1]
            member_amount = member[2]

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

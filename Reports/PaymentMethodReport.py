from DatabaseManagement.DatabaseManager import DatabaseManager


class PaymentMethodReport:
    manager = DatabaseManager()

    def get_data_from_db(self, account_id, report_group_id, date_from, date_to):
        expenses_list = self.manager.get_all_expenses_between_dates(account_id, date_from, date_to)
        report_group = self.manager.get_all_users_from_group(report_group_id)
        report_data = {'report_group': report_group, 'payment_methods': []}

        for expense in expenses_list:
            report_data['payment_methods'].append(
                {
                    'payer_id': expense['user_id'],
                    'payment_method_id': expense['payment_method_id'],
                    'amount': expense['amount']
                }
            )
        return report_data

    def generate_report_data(self, account_id, report_group_id, date_from, date_to):
        report_data = self.get_data_from_db(account_id, report_group_id, date_from, date_to)
        return self.sum_payments(report_data['report_group'], report_data['payment_methods'])

    def sum_payments(self, report_group, payments_list):
        payments_summary = {}
        for payment in payments_list:
            payer_id = payment['payer_id']
            payment_method_id = payment['payment_method_id']
            payment_amount = payment['amount']

            member_ids = []
            for report_group_member in report_group:
                member_ids.append(report_group_member['user_id'])

            if payer_id in member_ids:
                if payer_id in payments_summary:
                    if payment_method_id in payments_summary[payer_id]:
                        payments_summary[payer_id][payment_method_id] = payments_summary[payer_id][payment_method_id] \
                                                                        + payment_amount
                    else:
                        payments_summary[payer_id][payment_method_id] = payment_amount
                else:
                    payments_summary[payer_id] = {}
                    payments_summary[payer_id][payment_method_id] = payment_amount
        for k in payments_summary:
            for m in payments_summary[k]:
                payments_summary[k][m] = round(payments_summary[k][m], 2)
        return payments_summary

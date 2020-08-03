class PaymentMethodReport:

    def generate_report_data(self, report_group, payments_list):
        return self.sum_payments(report_group, payments_list)

    def sum_payments(self, report_group, payments_list):
        payments_summary = {}
        for payment in payments_list:
            payer_id = payment[0]
            payment_method_id = payment[1]
            payment_amount = payment[2]
            if payer_id in report_group:
                if payer_id in payments_summary:
                    if payment_method_id in payments_summary[payer_id]:
                        payments_summary[payer_id][payment_method_id] = payments_summary[payer_id][payment_method_id] + payment_amount
                    else:
                        payments_summary[payer_id][payment_method_id] = payment_amount
                else:
                    payments_summary[payer_id] = {}
                    payments_summary[payer_id][payment_method_id] = payment_amount
        for k in payments_summary:
            for m in payments_summary[k]:
                payments_summary[k][m] = round(payments_summary[k][m], 2)
        return payments_summary

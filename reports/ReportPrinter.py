from datetime import datetime

from reports.SettlementReport import SettlementReport
from reports.BalanceReport import BalanceReport
from reports.PaymentMethodReport import PaymentMethodReport
from database_manager.DatabaseManager import DatabaseManager


class ReportPrinter:

    def print_settlement_report(self, account_id, report_group_id, date_from, date_to):
        report = SettlementReport()
        report_data = report.generate_report_data(account_id, report_group_id, date_from, date_to)
        print(
            f'\nRaport należności generowany dla okresu: '
            f'{date_from.date()} - {date_to.date()} dla użytkowników z grupy: {report_group_id}:\n')
        for k in report_data:
            for m in report_data[k]:
                print(f'Użytkownik {m} ma oddać użytkownikowi {k} kwotę w wysokości: {report_data[k][m]} zł.')
        print()

    def print_balance_report(self, account_id, report_group_id, date_from, date_to):
        report = BalanceReport()
        report_data = report.generate_report_data(account_id, report_group_id, date_from, date_to)
        print(
            f'Raport bilansu generowany dla okresu: '
            f'{date_from.date()} - {date_to.date()} dla użytkowników z grupy: {report_group_id}:\n')
        for k in report_data:
            if report_data[k][0] == 1:
                print(f'Kategoria: {k} - wydatek na kwotę: {report_data[k][1]} zł')
            elif report_data[k][0] == 2:
                print(f'Kategoria: {k} - przychód na kwotę: {report_data[k][1]} zł')
        print()

    def print_payment_method_report(self, account_id, report_group_id, date_from, date_to):
        report = PaymentMethodReport()
        report_data = report.generate_report_data(account_id, report_group_id, date_from, date_to)
        print(
            f'Raport metod płatniczych generowany dla okresu: '
            f'{date_from.date()} - {date_to.date()} dla użytkowników z grupy: {report_group_id}:\n')
        for k in report_data:
            print(f'Użytkownik: {k}')
            for m in report_data[k]:
                print(f'Metoda płatności: {m} | Kwota: {report_data[k][m]} zł.')
        print()

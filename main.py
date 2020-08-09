from Reports.SettlementReport import SettlementReport
from Reports.BalanceReport import BalanceReport
from Reports.PaymentMethodReport import PaymentMethodReport
from DatabaseManagement.DatabaseManager import DatabaseManager
from datetime import datetime


def print_settlement_report(account_id, report_group_id, date_from, date_to):
    report = SettlementReport()
    report_data = report.generate_report_data(account_id, report_group_id, date_from, date_to)
    print(
        f'\nRaport należności generowany dla okresu: '
        f'{date_from.date()} - {date_to.date()} dla użytkowników z grupy: {report_group_id}:\n')
    for k in report_data:
        for m in report_data[k]:
            print(f'Użytkownik {m} ma oddać użytkownikowi {k} kwotę w wysokości: {report_data[k][m]} zł.')
    print()


def print_balance_report(account_id, report_group_id, date_from, date_to):
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


def print_payment_method_report(account_id, report_group_id, date_from, date_to):
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


def main():

    manager = DatabaseManager()

    report_group = 11

    date_from = datetime(2005, 2, 1)
    date_to = datetime(2050, 10, 1)
    print_settlement_report(4, report_group, date_from, date_to)
    print_balance_report(4, report_group, date_from, date_to)
    print_payment_method_report(4, report_group, date_from, date_to)


if __name__ == '__main__':
    main()

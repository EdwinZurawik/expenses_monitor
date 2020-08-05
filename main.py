from Reports.SettlementReport import SettlementReport
from Reports.BalanceReport import BalanceReport
from Reports.PaymentMethodReport import PaymentMethodReport
from DatabaseManagement.DatabaseManager import DatabaseManager
from datetime import datetime


def print_settlement_report(account_id, report_group, date_from, date_to):
    report = SettlementReport()
    report_data = report.generate_report_data(account_id, report_group, date_from, date_to)
    print(
        f'\nRaport należności generowany dla okresu: '
        f'{date_from.date()} - {date_to.date()} dla użytkowników: {report_group}:\n')
    for k in report_data:
        for m in report_data[k]:
            print(f'Użytkownik {m} ma oddać użytkownikowi {k} kwotę w wysokości: {report_data[k][m]} zł.')
    print()


def print_balance_report(report_group, operations_list, date_from, date_to):
    report = BalanceReport()
    report_data = report.generate_report_data(report_group, operations_list)
    print(
        f'Raport bilansu generowany dla okresu: '
        f'{date_from.date()} - {date_to.date()} dla użytkowników: {report_group}:\n')
    for k in report_data:
        if report_data[k][0] == 1:
            print(f'Kategoria: {k} - wydatek na kwotę: {report_data[k][1]} zł')
        elif report_data[k][0] == 2:
            print(f'Kategoria: {k} - przychód na kwotę: {report_data[k][1]} zł')
    print()


def print_payment_method_report(report_group, payments_list, date_from, date_to):
    report = PaymentMethodReport()
    report_data = report.generate_report_data(report_group, payments_list)
    print(
        f'Raport metod płatniczych generowany dla okresu: '
        f'{date_from.date()} - {date_to.date()} dla użytkowników: {report_group}:\n')
    for k in report_data:
        print(f'Użytkownik: {k}')
        for m in report_data[k]:
            print(f'Metoda płatności: {m} | Kwota: {report_data[k][m]} zł.')
    print()


def main():

    manager = DatabaseManager()

    #expenses_list = manager.get_all_expenses()

    # manager.create_expense(datetime.now(), 'Lidl', '', 11, 3, 29.47, 6, 11)
    # manager.create_expense(datetime.now(), 'Biedronka', '', 11, 3, 2.99, 6, 11)
    # manager.create_expense(datetime.now(), 'Tesco', '', 11, 3, 137.44, 6, 11)
    expenses_list = manager.get_all_expenses(4)
    for expense in expenses_list:
        print(expense)

    report_group = [11]

    expenses_list = [
        ['Edwin', [(1, 'Ola', 50), (2, 'Edwin', 50)], 24.04, 1],
        ['Edwin', [(1, 'Ola', 50), (1, 'Edwin', 50)], 0.99, 1],
        ['Edwin', [(1, 'Ola', 50), (1, 'Edwin', 50)], 13, 1],
        ['Edwin', [(1, 'Ola', 50), (1, 'Edwin', 50)], 6.16, 1],
        ['Edwin', [(1, 'Ola', 50), (1, 'Edwin', 50)], 5, 1],
        ['Edwin', [(1, 'Ola', 50), (1, 'Edwin', 50)], 25, 1],
        ['Edwin', [(1, 'Ola', 250), (2, 'Edwin', 550)], 800, 2],
        ['Edwin', [(1, 'Ola', 50), (2, 'Edwin', 100)], 145.95, 2]

    ]

    operations_list = [
        [1, 'Jedzenie', [(1, 'Edwin', 50), (2, 'Ola', 50)], 24.04, 1],
        [1, 'Jedzenie', [(1, 'Edwin', 50), (1, 'Ola', 50)], 0.99, 1],
        [1, 'Jedzenie', [(1, 'Edwin', 50), (1, 'Ola', 50)], 13, 1],
        [1, 'Jedzenie', [(1, 'Edwin', 50), (1, 'Ola', 50)], 6.16, 1],
        [1, 'Jedzenie', [(1, 'Edwin', 50), (1, 'Ola', 50)], 5, 1],
        [1, 'Jedzenie', [(1, 'Edwin', 50), (1, 'Ola', 50)], 25, 1],
        [1, 'Czynsz', [(1, 'Ola', 250), (2, 'Edwin', 550)], 800, 2],
        [1, 'Paliwo', [(1, 'Edwin', 50), (2, 'Edwin', 100)], 145.95, 2]

    ]

    payments_list = [
        ['Edwin', 'Karta debetowa', 24.04],
        ['Edwin', 'Karta debetowa', 0.99],
        ['Edwin', 'Karta debetowa', 13],
        ['Edwin', 'Karta debetowa', 6.16],
        ['Edwin', 'Karta debetowa', 5],
        ['Edwin', 'Karta debetowa', 25],
        ['Edwin', 'Przelew', 800],
        ['Ola', 'Gotówka', 145.95],

    ]

    date_from = datetime(2020, 2, 1)
    date_to = datetime(2020, 9, 1)
    print_settlement_report(4, report_group, date_from, date_to)
    # print_balance_report(report_group, operations_list, date_from, date_to)
    # print_payment_method_report(report_group, payments_list, date_from, date_to)


if __name__ == '__main__':
    main()

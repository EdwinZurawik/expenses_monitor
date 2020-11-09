import datetime
import re

from kivy.app import App
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import Screen

from database_manager.DatabaseManager import DatabaseManager
from main import ButtonWithData
from reports import PaymentMethodReport, BalanceReport, SettlementReport
from screens.gui_elements import CenteredLabel


class ReportsListScreen(Screen):
    pass


class ReportScreen(Screen):
    group_id = NumericProperty(0)
    category_id = NumericProperty(0)
    groups_dropdown = DropDown()
    report_name = StringProperty('Raport')

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def on_pre_enter(self, *args):
        self.add_groups_dropdown()
        self.ids.report_name.text = self.report_name

    def add_groups_dropdown(self):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()
        groups_list = db_manager.get_all_groups(app.root.account_id)

        for group in groups_list:
            btn = ButtonWithData(text=group['name'],
                                 size_hint_y=None,
                                 height='30',
                                 button_data={'text': group['name'], 'id': group['group_id']})
            btn.bind(on_release=lambda btn: self.groups_dropdown.select(btn.button_data))
            self.groups_dropdown.add_widget(btn)
        groups_btn = self.ids.groups_btn
        groups_btn.bind(on_release=self.groups_dropdown.open)
        self.groups_dropdown.bind(on_select=lambda instance, x: setattr(groups_btn, 'button_data', x))

    def set_group_id(self):
        self.group_id = self.ids.groups_btn.button_data['id']

    def clear_message(self):
        self.ids.message.text = ''

    def validate_input(self, date_from, date_to):
        return self.validate_dates(date_from, date_to) \
               and self.validate_group_id()

    def validate_dates(self, date_from, date_to):
        valid = False

        if self.validate_date(date_from) and self.validate_date(date_to):
            d_from = datetime.datetime.strptime(date_from, '%d.%m.%Y')
            d_to = datetime.datetime.strptime(date_to, '%d.%m.%Y')
            if d_from > d_to:
                self.show_message('Końcowa data nie może być wcześniejsza niż początkowa.')
            else:
                valid = True
        return valid

    def validate_date(self, date):
        valid = False
        date_regex = re.compile(r'([0-9]{2}\.[0-9]{2}\.[0-9]{4})')
        date_match = re.search(date_regex, date)
        if date == '':
            self.show_message('Data jest polem wymaganym.')
        elif date_match is None or date_match.group(1) != date:
            self.show_message('Błędny format daty. (DD.MM.RRRR)')
        else:
            valid = True
        return valid

    def validate_group_id(self):
        valid = False
        self.set_group_id()
        if self.group_id == 0:
            self.show_message('Wybór grupy jest obowiązkowy.')
        else:
            valid = True
        return valid

    def clear_input_fields(self):
        self.clear_message()
        self.ids.date_from.text = ''
        self.ids.date_to.text = ''
        self.ids.summary.text = ''
        self.ids.groups_btn.button_data = {'text': 'Wybierz', 'id': 0}
        self.groups_dropdown.clear_widgets()
        self.ids.box.clear_widgets()

    def show_message(self, message):
        self.ids.message.text = message

    def print_report(self, date_from_field, date_to_field):
        pass

    def generate_report(self, date_from, date_to):
        pass


class SettlementReportScreen(ReportScreen):
    report_name = 'Raport rozliczenia'

    def print_report(self, date_from_field, date_to_field):
        box = self.ids.box
        self.ids.box.clear_widgets()
        date_from = date_from_field.text
        date_to = date_to_field.text

        if self.validate_input(date_from, date_to):
            date_from = datetime.datetime.strptime(date_from, '%d.%m.%Y')
            date_to = datetime.datetime.strptime(date_to, '%d.%m.%Y')

            report_data = self.generate_report(date_from, date_to)

            for item in report_data:
                box.add_widget(CenteredLabel(text=item))
            self.show_message('')

    def generate_report(self, date_from, date_to):
        account_id = App.get_running_app().root.account_id
        db_manager = DatabaseManager()
        report = SettlementReport.SettlementReport()
        data = report.generate_report_data(account_id, self.group_id, date_from, date_to)
        report_lines = []
        for lender in data:
            lender_name = db_manager.get_user(lender)['username']
            for debtor in data[lender]:
                debtor_name = db_manager.get_user(debtor)['username']

                report_lines.append(f'{debtor_name} jest winien/winna {lender_name} kwotę: {data[lender][debtor]} zł.')

        report_data = report_lines
        return report_data


class BalanceReportScreen(ReportScreen):
    report_name = 'Raport bilansu'

    def print_report(self, date_from_field, date_to_field):
        box = self.ids.box
        self.ids.box.clear_widgets()
        date_from = date_from_field.text
        date_to = date_to_field.text

        if self.validate_input(date_from, date_to):
            date_from = datetime.datetime.strptime(date_from, '%d.%m.%Y')
            date_to = datetime.datetime.strptime(date_to, '%d.%m.%Y')

            report_data = self.generate_report(date_from, date_to)
            balance = report_data["summary"]["incomes"] - report_data["summary"]["expenses"]

            for item in report_data['expenses']:
                box.add_widget(CenteredLabel(text=item))
            for item in report_data['incomes']:
                box.add_widget(CenteredLabel(text=item))

            self.ids.summary.text = f'Wydatki: {report_data["summary"]["expenses"]} zł ' \
                                    f'| Przychody: {report_data["summary"]["incomes"]} zł ' \
                                    f'| Bilans: {balance} zł.'
            self.show_message('')

    def generate_report(self, date_from, date_to):
        account_id = App.get_running_app().root.account_id
        db_manager = DatabaseManager()
        report = BalanceReport.BalanceReport()
        data = report.generate_report_data(account_id, self.group_id, date_from, date_to)
        expenses = ['Wydatki:']
        incomes = ['Przychody:']
        summary = {'expenses': 0, 'incomes': 0}
        for item in data:
            category_name = db_manager.get_category(item)['name']

            if data[item][0] == 1:
                expenses.append(f'{category_name}: {data[item][1]} zł.')
                summary['expenses'] = summary['expenses'] + data[item][1]
            elif data[item][0] == 2:
                incomes.append(f'{category_name}: {data[item][1]} zł.')
                summary['incomes'] = summary['incomes'] + data[item][1]

        report_data = {'expenses': expenses, 'incomes': incomes, 'summary': summary}
        return report_data


class PaymentMethodReportScreen(ReportScreen):
    report_name = 'Raport metod płatności'

    def print_report(self, date_from_field, date_to_field):
        box = self.ids.box
        self.ids.box.clear_widgets()
        date_from = date_from_field.text
        date_to = date_to_field.text

        if self.validate_input(date_from, date_to):
            date_from = datetime.datetime.strptime(date_from, '%d.%m.%Y')
            date_to = datetime.datetime.strptime(date_to, '%d.%m.%Y')

            report_data = self.generate_report(date_from, date_to)

            for item in report_data:
                box.add_widget(CenteredLabel(text=item))
            self.show_message('')

    def generate_report(self, date_from, date_to):
        account_id = App.get_running_app().root.account_id
        db_manager = DatabaseManager()
        report = PaymentMethodReport.PaymentMethodReport()
        data = report.generate_report_data(account_id, self.group_id, date_from, date_to)
        report_lines = []
        for user in data:
            user_name = db_manager.get_user(user)['username']
            report_lines.append(f'Użytkownik: {user_name}')
            for payment_method in data[user]:
                payment_method_name = db_manager.get_payment_method(payment_method)['name']

                report_lines.append(f'{payment_method_name} | kwota: {data[user][payment_method]} zł.')

        report_data = report_lines
        return report_data

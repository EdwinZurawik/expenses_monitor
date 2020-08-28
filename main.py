import re
import datetime
import math

from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput

from database_manager.DatabaseManager import DatabaseManager
from reports import BalanceReport, PaymentMethodReport, SettlementReport
from configuration_data import ConfigurationData
import mysql.connector

from kivy.app import App

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.properties import NumericProperty, ObjectProperty, ListProperty, DictProperty
from kivy.properties import StringProperty
from kivy.uix.button import Button


class MyScreenManager(ScreenManager):
    account_id = NumericProperty(None)
    label_id = NumericProperty(None)

    def label_clicked(self, label_id):
        self.label_id = label_id
        destination_screen = self.current_screen.name
        print(self.current_screen.name)
        if self.current_screen.name == 'expenses_list_screen':
            destination_screen = 'expense_details_screen'
        elif self.current_screen.name == 'incomes_list_screen':
            destination_screen = 'income_details_screen'
        else:
            pass
        self.change_screen(destination_screen)

    def change_screen(self, destination_screen='login_screen'):
        self.current = destination_screen

    def logout(self):
        self.account_id = 0
        self.change_screen()
        print(self.account_id)


class MenuScreen(Screen):
    pass


class ReportsListScreen(Screen):
    pass


class BalanceReportScreen(Screen):
    group_id = NumericProperty(0)
    category_id = NumericProperty(0)
    groups_dropdown = DropDown()

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def on_pre_enter(self, *args):
        self.add_groups_dropdown()

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
        self.ids.groups_btn.button_data = {'text': 'Wybierz', 'id': 0}
        self.groups_dropdown.clear_widgets()
        self.ids.box.clear_widgets()
        self.ids.summary.text = ''

    def show_message(self, message):
        self.ids.message.text = message

    def print_balance_report(self, date_from_field, date_to_field):
        box = self.ids.box
        self.ids.box.clear_widgets()
        date_from = date_from_field.text
        date_to = date_to_field.text

        if self.validate_input(date_from, date_to):
            date_from = datetime.datetime.strptime(date_from, '%d.%m.%Y')
            date_to = datetime.datetime.strptime(date_to, '%d.%m.%Y')

            report_data = self.generate_balance_report(date_from, date_to)
            balance = report_data["summary"]["incomes"] - report_data["summary"]["expenses"]

            for item in report_data['expenses']:
                box.add_widget(Label(text=item, halign='left'))
            for item in report_data['incomes']:
                box.add_widget(Label(text=item, halign='left'))

            self.ids.summary.text = f'Wydatki: {report_data["summary"]["expenses"]} zł ' \
                                    f'| Przychody: {report_data["summary"]["incomes"]} zł ' \
                                    f'| Bilans: {balance} zł.'
            self.show_message('')

    def generate_balance_report(self, date_from, date_to):
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


class ButtonWithData(Button):
    button_data = ObjectProperty({'text': '', 'id': 0})

    def on_button_data(self, *args):
        self.text = self.button_data['text']


class SettlementReportScreen(Screen):
    group_id = NumericProperty(0)
    category_id = NumericProperty(0)
    groups_dropdown = DropDown()

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def on_pre_enter(self, *args):
        self.add_groups_dropdown()

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
        self.ids.groups_btn.button_data = {'text': 'Wybierz', 'id': 0}
        self.groups_dropdown.clear_widgets()
        self.ids.box.clear_widgets()

    def show_message(self, message):
        self.ids.message.text = message

    def print_settlement_report(self, date_from_field, date_to_field):
        box = self.ids.box
        self.ids.box.clear_widgets()
        date_from = date_from_field.text
        date_to = date_to_field.text

        if self.validate_input(date_from, date_to):
            date_from = datetime.datetime.strptime(date_from, '%d.%m.%Y')
            date_to = datetime.datetime.strptime(date_to, '%d.%m.%Y')

            report_data = self.generate_settlement_report(date_from, date_to)

            for item in report_data:
                box.add_widget(Label(text=item, halign='left'))
            self.show_message('')

    def generate_settlement_report(self, date_from, date_to):
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


class PaymentMethodReportScreen(Screen):
    group_id = NumericProperty(0)
    category_id = NumericProperty(0)
    groups_dropdown = DropDown()

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def on_pre_enter(self, *args):
        self.add_groups_dropdown()

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
        self.ids.groups_btn.button_data = {'text': 'Wybierz', 'id': 0}
        self.groups_dropdown.clear_widgets()
        self.ids.box.clear_widgets()

    def show_message(self, message):
        self.ids.message.text = message

    def print_payment_method_report(self, date_from_field, date_to_field):
        box = self.ids.box
        self.ids.box.clear_widgets()
        date_from = date_from_field.text
        date_to = date_to_field.text

        if self.validate_input(date_from, date_to):
            date_from = datetime.datetime.strptime(date_from, '%d.%m.%Y')
            date_to = datetime.datetime.strptime(date_to, '%d.%m.%Y')

            report_data = self.generate_payment_method_report(date_from, date_to)

            for item in report_data:
                box.add_widget(Label(text=item, halign='left'))
            self.show_message('')

    def generate_payment_method_report(self, date_from, date_to):
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


class FloatInput(TextInput):
    pat = re.compile('[^0-9]')

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super(FloatInput, self).insert_text(s, from_undo=from_undo)


class IntegerInput(TextInput):
    pat = re.compile('[^0-9]')

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        s = re.sub(pat, '', substring)
        return super(IntegerInput, self).insert_text(s, from_undo=from_undo)


class CreateExpenseScreen(Screen):
    payer_id = NumericProperty(0)
    group_id = NumericProperty(0)
    category_id = NumericProperty(0)
    payment_method_id = NumericProperty(0)
    payers_dropdown = DropDown()
    groups_dropdown = DropDown()
    categories_dropdown = DropDown()
    payment_methods_dropdown = DropDown()

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def on_pre_enter(self, *args):
        self.payers_dropdown.clear_widgets()
        self.groups_dropdown.clear_widgets()
        self.categories_dropdown.clear_widgets()
        self.payment_methods_dropdown.clear_widgets()
        self.add_payers_dropdown()
        self.add_groups_dropdown()
        self.add_categories_dropdown()
        self.add_payment_methods_dropdown()

    def add_payers_dropdown(self):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()

        users_list = db_manager.get_all_users(app.root.account_id)

        for user in users_list:
            btn = ButtonWithData(text=user['username'],
                                 size_hint_y=None,
                                 height='30',
                                 button_data={'text': user['username'], 'id': user['user_id']})
            btn.bind(on_release=lambda btn: self.payers_dropdown.select(btn.button_data))
            self.payers_dropdown.add_widget(btn)
        payers_btn = self.ids.payers_btn
        payers_btn.bind(on_release=self.payers_dropdown.open)
        self.payers_dropdown.bind(on_select=lambda instance, x: setattr(payers_btn, 'button_data', x))

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

    def add_categories_dropdown(self):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()

        categories_list = db_manager.get_all_categories(app.root.account_id)

        for category in categories_list:
            if category['category_type_id'] == 1:
                btn = ButtonWithData(text=category['name'],
                                     size_hint_y=None,
                                     height='30',
                                     button_data={'text': category['name'], 'id': category['category_id']})
                btn.bind(on_release=lambda btn: self.categories_dropdown.select(btn.button_data))
                self.categories_dropdown.add_widget(btn)
        categories_btn = self.ids.categories_btn
        categories_btn.bind(on_release=self.categories_dropdown.open)
        self.categories_dropdown.bind(on_select=lambda instance, x: setattr(categories_btn, 'button_data', x))

    def add_payment_methods_dropdown(self):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()

        payment_methods_list = db_manager.get_all_payment_methods(app.root.account_id)

        for payment_method in payment_methods_list:
            btn = ButtonWithData(text=payment_method['name'],
                                 size_hint_y=None,
                                 height='30',
                                 button_data={'text': payment_method['name'],
                                              'id': payment_method['payment_method_id']})
            btn.bind(on_release=lambda btn: self.payment_methods_dropdown.select(btn.button_data))
            self.payment_methods_dropdown.add_widget(btn)
        payment_methods_btn = self.ids.payment_methods_btn
        payment_methods_btn.bind(on_release=self.payment_methods_dropdown.open)
        self.payment_methods_dropdown.bind(on_select=lambda instance, x: setattr(payment_methods_btn, 'button_data', x))

    def set_payer_id(self):
        self.payer_id = self.ids.payers_btn.button_data['id']

    def set_group_id(self):
        self.group_id = self.ids.groups_btn.button_data['id']

    def set_category_id(self):
        self.category_id = self.ids.categories_btn.button_data['id']

    def set_payment_method_id(self):
        self.payment_method_id = self.ids.payment_methods_btn.button_data['id']

    def clear_message(self):
        self.ids.message.text = ''

    def validate_input(self, name, date, description, amount):
        return self.validate_name(name) \
               and self.validate_date(date) \
               and self.validate_description(description) \
               and self.validate_payer_id() \
               and self.validate_group_id() \
               and self.validate_category_id() \
               and self.validate_amount(amount) \
               and self.validate_payment_method_id()

    def validate_name(self, name):
        valid = False
        if len(name) < 3:
            self.show_message('Nazwa wydatku powinna składać się z co najmniej 3 znaków.')
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

    def validate_description(self, description):
        valid = False
        if len(description) > 255:
            self.show_message('Maksymalna długość opisu to 255 znaków.')
        else:
            valid = True
        return valid

    def validate_payer_id(self):
        valid = False
        print(self.payer_id)
        print(self.ids.payers_btn.button_data)
        print(self.ids.payers_btn.button_data['id'])
        self.set_payer_id()
        if self.payer_id == 0:
            self.show_message('Wybór osoby płacącej jest obowiązkowy.')
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

    def validate_category_id(self):
        valid = False
        self.set_category_id()
        if self.category_id == 0:
            self.show_message('Wybór kategorii jest obowiązkowy.')
        else:
            valid = True
        return valid

    def validate_payment_method_id(self):
        valid = False
        self.set_payment_method_id()
        if self.payment_method_id == 0:
            self.show_message('Wybór metody płatniczej jest obowiązkowy.')
        else:
            valid = True
        return valid

    def validate_amount(self, amount):
        valid = False
        amount_regex = re.compile(r'([0-9]+\.?[0-9]{0,2})')
        amount_match = re.search(amount_regex, amount)
        if amount == '':
            self.show_message('Kwota jest polem wymaganym.')
        elif amount_match is None or amount_match.group(1) != amount:
            self.show_message('Błędna kwota.')
        else:
            valid = True
        return valid

    def check_in_database(self, name, date, description, amount):
        db_manager = App.get_running_app().db_manager
        date = datetime.datetime.strptime(date, '%d.%m.%Y')
        formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
        app = App.get_running_app()
        print('Próbuję dodać wydatek')
        user_id = db_manager.create_expense(formatted_date, name, description, self.payer_id,
                                            self.category_id, amount, self.payment_method_id,
                                            self.group_id)
        print(app.root.account_id, name)
        print(user_id)
        return user_id

    def clear_input_fields(self):
        self.clear_message()
        self.ids.name.text = ''
        self.ids.date.text = ''
        self.ids.description.text = ''
        self.ids.amount.text = ''
        self.ids.payers_btn.button_data = {'text': 'Wybierz', 'id': 0}
        self.ids.groups_btn.button_data = {'text': 'Wybierz', 'id': 0}
        self.ids.categories_btn.button_data = {'text': 'Wybierz', 'id': 0}
        self.ids.payment_methods_btn.button_data = {'text': 'Wybierz', 'id': 0}

    def show_message(self, message):
        self.ids.message.text = message

    def add_expense(self, name_field, date_field, description_field, amount_field):
        name = name_field.text
        date = date_field.text
        description = description_field.text
        amount = amount_field.text

        if self.validate_input(name, date, description, amount):
            expense_id = self.check_in_database(name, date, description, amount)
            if expense_id != {}:
                print('expense succesfully added')
                self.clear_input_fields()
                self.show_message(f'Wydatek {name} został dodany.')
            else:
                self.show_message('Błąd, skontaktuj się z administratorem.')


class EditExpenseScreen(Screen):
    expense = ObjectProperty(None)
    payer_id = NumericProperty(0)
    group_id = NumericProperty(0)
    category_id = NumericProperty(0)
    payment_method_id = NumericProperty(0)
    payers_dropdown = DropDown()
    groups_dropdown = DropDown()
    categories_dropdown = DropDown()
    payment_methods_dropdown = DropDown()

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def populate_fields(self):
        self.payer_id = self.expense['user_id']
        self.group_id = self.expense['group_id']
        self.category_id = self.expense['category_id']
        self.payment_method_id = self.expense['payment_method_id']
        self.ids.payers_btn.button_data = {'text': self.expense['username'], 'id': self.expense['user_id']}
        self.ids.groups_btn.button_data = {'text': self.expense['group_name'], 'id': self.expense['group_id']}
        self.ids.categories_btn.button_data = {'text': self.expense['category_name'], 'id': self.expense['category_id']}
        self.ids.payment_methods_btn.button_data = {'text': self.expense['payment_method_name'],
                                                    'id': self.expense['payment_method_id']}
        self.ids.name.text = self.expense['expense_name']
        self.ids.date.text = self.expense['operation_date'].strftime('%d.%m.%Y')
        self.ids.description.text = self.expense['description']
        self.ids.amount.text = str(round(self.expense['amount'], 2))

    def on_pre_enter(self, *args):
        self.expense = self.load_expense(App.get_running_app().root.label_id)
        self.add_payers_dropdown()
        self.add_groups_dropdown()
        self.add_categories_dropdown()
        self.add_payment_methods_dropdown()
        self.populate_fields()

    def add_payers_dropdown(self):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()

        users_list = db_manager.get_all_users(app.root.account_id)

        for user in users_list:
            btn = ButtonWithData(text=user['username'],
                                 size_hint_y=None,
                                 height='30',
                                 button_data={'text': user['username'], 'id': user['user_id']})
            btn.bind(on_release=lambda btn: self.payers_dropdown.select(btn.button_data))
            self.payers_dropdown.add_widget(btn)
        payers_btn = self.ids.payers_btn
        payers_btn.bind(on_release=self.payers_dropdown.open)
        self.payers_dropdown.bind(on_select=lambda instance, x: setattr(payers_btn, 'button_data', x))

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

    def add_categories_dropdown(self):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()

        categories_list = db_manager.get_all_categories(app.root.account_id)

        for category in categories_list:
            if category['category_type_id'] == 1:
                btn = ButtonWithData(text=category['name'],
                                     size_hint_y=None,
                                     height='30',
                                     button_data={'text': category['name'], 'id': category['category_id']})
                btn.bind(on_release=lambda btn: self.categories_dropdown.select(btn.button_data))
                self.categories_dropdown.add_widget(btn)
        categories_btn = self.ids.categories_btn
        categories_btn.bind(on_release=self.categories_dropdown.open)
        self.categories_dropdown.bind(on_select=lambda instance, x: setattr(categories_btn, 'button_data', x))

    def add_payment_methods_dropdown(self):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()

        payment_methods_list = db_manager.get_all_payment_methods(app.root.account_id)

        for payment_method in payment_methods_list:
            btn = ButtonWithData(text=payment_method['name'],
                                 size_hint_y=None,
                                 height='30',
                                 button_data={'text': payment_method['name'],
                                              'id': payment_method['payment_method_id']})
            btn.bind(on_release=lambda btn: self.payment_methods_dropdown.select(btn.button_data))
            self.payment_methods_dropdown.add_widget(btn)
        payment_methods_btn = self.ids.payment_methods_btn
        payment_methods_btn.bind(on_release=self.payment_methods_dropdown.open)
        self.payment_methods_dropdown.bind(on_select=lambda instance, x: setattr(payment_methods_btn, 'button_data', x))

    def set_payer_id(self):
        self.payer_id = self.ids.payers_btn.button_data['id']

    def set_group_id(self):
        self.group_id = self.ids.groups_btn.button_data['id']

    def set_category_id(self):
        self.category_id = self.ids.categories_btn.button_data['id']

    def set_payment_method_id(self):
        self.payment_method_id = self.ids.payment_methods_btn.button_data['id']

    def clear_message(self):
        self.ids.message.text = ''

    def validate_input(self, name, date, description, amount):
        return self.validate_name(name) \
               and self.validate_date(date) \
               and self.validate_description(description) \
               and self.validate_payer_id() \
               and self.validate_group_id() \
               and self.validate_category_id() \
               and self.validate_amount(amount) \
               and self.validate_payment_method_id()

    def validate_name(self, name):
        valid = False
        if len(name) < 3:
            self.show_message('Nazwa wydatku powinna składać się z co najmniej 3 znaków.')
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

    def validate_description(self, description):
        valid = False
        if len(description) > 255:
            self.show_message('Maksymalna długość opisu to 255 znaków.')
        else:
            valid = True
        return valid

    def validate_payer_id(self):
        valid = False
        print(self.payer_id)
        print(self.ids.payers_btn.button_data)
        print(self.ids.payers_btn.button_data['id'])
        self.set_payer_id()
        if self.payer_id == 0:
            self.show_message('Wybór osoby płacącej jest obowiązkowy.')
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

    def validate_category_id(self):
        valid = False
        self.set_category_id()
        if self.category_id == 0:
            self.show_message('Wybór kategorii jest obowiązkowy.')
        else:
            valid = True
        return valid

    def validate_payment_method_id(self):
        valid = False
        self.set_payment_method_id()
        if self.payment_method_id == 0:
            self.show_message('Wybór metody płatniczej jest obowiązkowy.')
        else:
            valid = True
        return valid

    def validate_amount(self, amount):
        valid = False
        amount_regex = re.compile(r'([0-9]+\.?[0-9]{0,2})')
        amount_match = re.search(amount_regex, amount)
        if amount == '':
            self.show_message('Kwota jest polem wymaganym.')
        elif amount_match is None or amount_match.group(1) != amount:
            self.show_message('Błędna kwota.')
        else:
            valid = True
        return valid

    def load_expense(self, expense_id):
        db_manager = App.get_running_app().db_manager
        print('Próbuję wczytać wydatek')
        expense = db_manager.get_expense(expense_id)
        print(expense)
        return expense

    def check_in_database(self, name, date, description, amount):
        db_manager = App.get_running_app().db_manager
        date = datetime.datetime.strptime(date, '%d.%m.%Y')
        formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
        app = App.get_running_app()
        print('Próbuję edytować wydatek')
        expense_id = db_manager.edit_expense(self.expense['expense_id'], formatted_date, name, description,
                                             amount, self.ids.payers_btn.button_data['id'],
                                             self.ids.categories_btn.button_data['id'],
                                             self.ids.groups_btn.button_data['id'],
                                             self.ids.payment_methods_btn.button_data['id'])
        print(app.root.account_id, name)
        print(expense_id)
        return expense_id

    def clear_input_fields(self):
        self.clear_message()
        self.ids.name.text = ''
        self.ids.date.text = ''
        self.ids.description.text = ''
        self.ids.amount.text = ''
        self.ids.payers_btn.button_data = {'text': 'Wybierz', 'id': 0}
        self.ids.groups_btn.button_data = {'text': 'Wybierz', 'id': 0}
        self.ids.categories_btn.button_data = {'text': 'Wybierz', 'id': 0}
        self.ids.payment_methods_btn.button_data = {'text': 'Wybierz', 'id': 0}
        self.payers_dropdown.clear_widgets()
        self.groups_dropdown.clear_widgets()
        self.categories_dropdown.clear_widgets()
        self.payment_methods_dropdown.clear_widgets()

    def show_message(self, message):
        self.ids.message.text = message

    def compare_changes(self, name, date, description, amount):
        print('Comparing changes in expense:')
        print(self.expense)
        has_changed = False
        if self.expense['operation_date'] != datetime.datetime.strptime(date, '%d.%m.%Y'):
            has_changed = True
            print(self.expense['operation_date'], '!=', datetime.datetime.strptime(date, '%d.%m.%Y'))
        elif self.expense['expense_name'] != name:
            has_changed = True
            print(self.expense['expense_name'], '!=', name)
        elif self.expense['description'] != description:
            has_changed = True
            print(self.expense['description'], '!=', description)
        elif float(self.expense['amount']) != float(amount):
            has_changed = True
            print(self.expense['amount'], '!=', amount)
        elif self.expense['user_id'] != self.ids.payers_btn.button_data['id']:
            has_changed = True
            print(self.expense['user_id'], '!=', self.ids.payers_btn.button_data['id'])
        elif self.expense['group_id'] != self.ids.groups_btn.button_data['id']:
            has_changed = True
            print(self.expense['group_id'], '!=', self.ids.groups_btn.button_data['id'])
        elif self.expense['category_id'] != self.ids.categories_btn.button_data['id']:
            has_changed = True
            print(self.expense['category_id'], '!=', self.ids.categories_btn.button_data['id'])
        elif self.expense['payment_method_id'] != self.ids.payment_methods_btn.button_data['id']:
            has_changed = True
            print(self.expense['payment_method_id'], '!=', self.ids.payment_methods_btn.button_data['id'])
        return has_changed

    def update_expense(self, name_field, date_field, description_field, amount_field):
        name = name_field.text
        date = date_field.text
        description = description_field.text
        amount = amount_field.text

        if self.validate_input(name, date, description, amount) \
                and self.compare_changes(name, date, description, amount):

            expense_id = self.check_in_database(name, date, description, amount)
            if expense_id is None:
                print('expense succesfully updated')
                self.show_message(f'Zmiany w {name} zostały zapisane.')
            else:
                self.show_message('Błąd, skontaktuj się z administratorem.')


class EditIncomeScreen(Screen):
    income = ObjectProperty(None)
    group_id = NumericProperty(0)
    category_id = NumericProperty(0)
    groups_dropdown = DropDown()
    categories_dropdown = DropDown()

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def on_pre_enter(self, *args):
        self.income = self.load_income(App.get_running_app().root.label_id)
        self.add_groups_dropdown()
        self.add_categories_dropdown()
        self.populate_fields()

    def populate_fields(self):
        self.group_id = self.income['group_id']
        self.category_id = self.income['category_id']
        self.ids.groups_btn.button_data = {'text': self.income['group_name'], 'id': self.income['group_id']}
        self.ids.categories_btn.button_data = {'text': self.income['category_name'], 'id': self.income['category_id']}
        self.ids.name.text = self.income['income_name']
        self.ids.date.text = self.income['operation_date'].strftime('%d.%m.%Y')
        self.ids.description.text = self.income['description']
        self.ids.amount.text = str(round(self.income['amount'], 2))

    def add_groups_dropdown(self):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()

        groups_list = db_manager.get_all_groups(app.root.account_id)

        for group in groups_list:
            if group['is_main_group']:
                btn = ButtonWithData(text=group['name'],
                                     size_hint_y=None,
                                     height='30',
                                     button_data={'text': group['name'], 'id': group['group_id']})
                btn.bind(on_release=lambda btn: self.groups_dropdown.select(btn.button_data))
                self.groups_dropdown.add_widget(btn)
        groups_btn = self.ids.groups_btn
        groups_btn.bind(on_release=self.groups_dropdown.open)
        self.groups_dropdown.bind(on_select=lambda instance, x: setattr(groups_btn, 'button_data', x))

    def add_categories_dropdown(self):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()

        categories_list = db_manager.get_all_categories(app.root.account_id)

        for category in categories_list:
            if category['category_type_id'] == 2:
                btn = ButtonWithData(text=category['name'],
                                     size_hint_y=None,
                                     height='30',
                                     button_data={'text': category['name'], 'id': category['category_id']})
                btn.bind(on_release=lambda btn: self.categories_dropdown.select(btn.button_data))
                self.categories_dropdown.add_widget(btn)
        categories_btn = self.ids.categories_btn
        categories_btn.bind(on_release=self.categories_dropdown.open)
        self.categories_dropdown.bind(on_select=lambda instance, x: setattr(categories_btn, 'button_data', x))

    def set_group_id(self):
        self.group_id = self.ids.groups_btn.button_data['id']

    def set_category_id(self):
        self.category_id = self.ids.categories_btn.button_data['id']

    def clear_message(self):
        self.ids.message.text = ''

    def validate_input(self, name, date, description, amount):
        return self.validate_name(name) \
               and self.validate_date(date) \
               and self.validate_description(description) \
               and self.validate_group_id() \
               and self.validate_category_id() \
               and self.validate_amount(amount)

    def validate_name(self, name):
        valid = False
        if len(name) < 3:
            self.show_message('Nazwa przychodu powinna składać się z co najmniej 3 znaków.')
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
            self.show_message('Błędny format day. (DD.MM.RRRR')
        else:
            valid = True
        return valid

    def validate_description(self, description):
        valid = False
        if len(description) > 255:
            self.show_message('Maksymalna długość opisu to 255 znaków.')
        else:
            valid = True
        return valid

    def validate_group_id(self):
        valid = False
        self.set_group_id()
        if self.group_id == 0:
            self.show_message('Wybór osoby, która otrzymała środki jest obowiązkowy.')
        else:
            valid = True
        return valid

    def validate_category_id(self):
        valid = False
        self.set_category_id()
        if self.category_id == 0:
            self.show_message('Wybór kategorii jest obowiązkowy.')
        else:
            valid = True
        return valid

    def validate_amount(self, amount):
        valid = False
        amount_regex = re.compile(r'([0-9]+\.?[0-9]{0,2})')
        amount_match = re.search(amount_regex, amount)
        if amount == '':
            self.show_message('Kwota jest polem wymaganym.')
        elif amount_match is None or amount_match.group(1) != amount:
            self.show_message('Błędna kwota.')
        else:
            valid = True
        return valid

    def load_income(self, income_id):
        db_manager = App.get_running_app().db_manager
        print(f'Próbuję wczytać przychód {income_id}')
        income = db_manager.get_income(income_id)
        print(income)
        return income

    def check_in_database(self, name, date, description, amount):
        db_manager = App.get_running_app().db_manager
        date = datetime.datetime.strptime(date, '%d.%m.%Y')
        formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
        app = App.get_running_app()
        print('Próbuję edytować wpływ')
        income_id = db_manager.edit_income(self.income['income_id'], formatted_date, name, description,
                                           amount, self.ids.categories_btn.button_data['id'], self.ids.groups_btn.button_data['id'])
        print(app.root.account_id, name)
        print(income_id)
        return income_id

    def clear_input_fields(self):
        self.clear_message()
        self.ids.name.text = ''
        self.ids.date.text = ''
        self.ids.description.text = ''
        self.ids.amount.text = ''
        self.ids.groups_btn.button_data = {'text': 'Wybierz', 'id': 0}
        self.ids.categories_btn.button_data = {'text': 'Wybierz', 'id': 0}
        self.groups_dropdown.clear_widgets()
        self.categories_dropdown.clear_widgets()

    def show_message(self, message):
        self.ids.message.text = message

    def compare_changes(self, name, date, description, amount):
        print('Comparing changes in income:')
        print(self.income)
        has_changed = False
        if self.income['operation_date'] != datetime.datetime.strptime(date, '%d.%m.%Y'):
            has_changed = True
            print(self.income['operation_date'], '!=', datetime.datetime.strptime(date, '%d.%m.%Y'))
        elif self.income['income_name'] != name:
            has_changed = True
            print(self.income['income_name'], '!=', name)
        elif self.income['description'] != description:
            has_changed = True
            print(self.income['description'], '!=', description)
        elif float(self.income['amount']) != float(amount):
            has_changed = True
            print(self.income['amount'], '!=', amount)
        elif self.income['group_id'] != self.ids.groups_btn.button_data['id']:
            has_changed = True
            print(self.income['group_id'], '!=', self.ids.groups_btn.button_data['id'])
        elif self.income['category_id'] != self.ids.categories_btn.button_data['id']:
            has_changed = True
            print(self.income['category_id'], '!=', self.ids.categories_btn.button_data['id'])
        return has_changed

    def update_income(self, name_field, date_field, description_field, amount_field):
        name = name_field.text
        date = date_field.text
        description = description_field.text
        amount = amount_field.text

        if self.validate_input(name, date, description, amount) \
                and self.compare_changes(name, date, description, amount):
            income_id = self.check_in_database(name, date, description, amount)
            if income_id != {}:
                print('income succesfully updated')
                self.show_message(f'Zmiany w {name} zostały zapisane.')
            else:
                self.show_message('Błąd, skontaktuj się z administratorem.')


class CreateIncomeScreen(Screen):
    group_id = NumericProperty(0)
    category_id = NumericProperty(0)
    groups_dropdown = DropDown()
    categories_dropdown = DropDown()

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def on_pre_enter(self, *args):
        self.groups_dropdown.clear_widgets()
        self.categories_dropdown.clear_widgets()
        self.add_groups_dropdown()
        self.add_categories_dropdown()


    def add_groups_dropdown(self):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()

        groups_list = db_manager.get_all_groups(app.root.account_id)

        for group in groups_list:
            if group['is_main_group']:
                btn = ButtonWithData(text=group['name'],
                                     size_hint_y=None,
                                     height='30',
                                     button_data={'text': group['name'], 'id': group['group_id']})
                btn.bind(on_release=lambda btn: self.groups_dropdown.select(btn.button_data))
                self.groups_dropdown.add_widget(btn)
        groups_btn = self.ids.groups_btn
        groups_btn.bind(on_release=self.groups_dropdown.open)
        self.groups_dropdown.bind(on_select=lambda instance, x: setattr(groups_btn, 'button_data', x))

    def add_categories_dropdown(self):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()

        categories_list = db_manager.get_all_categories(app.root.account_id)

        for category in categories_list:
            if category['category_type_id'] == 2:
                btn = ButtonWithData(text=category['name'],
                                     size_hint_y=None,
                                     height='30',
                                     button_data={'text': category['name'], 'id': category['category_id']})
                btn.bind(on_release=lambda btn: self.categories_dropdown.select(btn.button_data))
                self.categories_dropdown.add_widget(btn)
        categories_btn = self.ids.categories_btn
        categories_btn.bind(on_release=self.categories_dropdown.open)
        self.categories_dropdown.bind(on_select=lambda instance, x: setattr(categories_btn, 'button_data', x))

    def set_group_id(self):
        self.group_id = self.ids.groups_btn.button_data['id']

    def set_category_id(self):
        self.category_id = self.ids.categories_btn.button_data['id']

    def clear_message(self):
        self.ids.message.text = ''

    def validate_input(self, name, date, description, amount):
        return self.validate_name(name) \
               and self.validate_date(date) \
               and self.validate_description(description) \
               and self.validate_group_id() \
               and self.validate_category_id() \
               and self.validate_amount(amount)

    def validate_name(self, name):
        valid = False
        if len(name) < 3:
            self.show_message('Nazwa przychodu powinna składać się z co najmniej 3 znaków.')
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
            self.show_message('Błędny format day. (DD.MM.RRRR')
        else:
            valid = True
        return valid

    def validate_description(self, description):
        valid = False
        if len(description) > 255:
            self.show_message('Maksymalna długość opisu to 255 znaków.')
        else:
            valid = True
        return valid

    def validate_group_id(self):
        valid = False
        self.set_group_id()
        if self.group_id == 0:
            self.show_message('Wybór osoby, która otrzymała środki jest obowiązkowy.')
        else:
            valid = True
        return valid

    def validate_category_id(self):
        valid = False
        self.set_category_id()
        if self.category_id == 0:
            self.show_message('Wybór kategorii jest obowiązkowy.')
        else:
            valid = True
        return valid

    def validate_amount(self, amount):
        valid = False
        amount_regex = re.compile(r'([0-9]+\.?[0-9]{0,2})')
        amount_match = re.search(amount_regex, amount)
        if amount == '':
            self.show_message('Kwota jest polem wymaganym.')
        elif amount_match is None or amount_match.group(1) != amount:
            self.show_message('Błędna kwota.')
        else:
            valid = True
        return valid

    def check_in_database(self, name, date, description, amount):
        db_manager = App.get_running_app().db_manager
        date = datetime.datetime.strptime(date, '%d.%m.%Y')
        formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
        app = App.get_running_app()
        print('Próbuję dodać wpływ')
        user_id = db_manager.create_income(formatted_date, name, description,
                                           self.category_id, amount, self.group_id)
        print(app.root.account_id, name)
        print(user_id)
        return user_id

    def clear_input_fields(self):
        self.clear_message()
        self.ids.name.text = ''
        self.ids.date.text = ''
        self.ids.description.text = ''
        self.ids.amount.text = ''
        self.ids.groups_btn.button_data = {'text': 'Wybierz', 'id': 0}
        self.ids.categories_btn.button_data = {'text': 'Wybierz', 'id': 0}

    def show_message(self, message):
        self.ids.message.text = message

    def add_income(self, name_field, date_field, description_field, amount_field):
        name = name_field.text
        date = date_field.text
        description = description_field.text
        amount = amount_field.text

        if self.validate_input(name, date, description, amount):
            income_id = self.check_in_database(name, date, description, amount)
            if income_id != {}:
                print('income succesfully added')
                self.clear_input_fields()
                self.show_message(f'Przychód {name} został dodany.')
            else:
                self.show_message('Błąd, skontaktuj się z administratorem.')


class LoginScreen(Screen):

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def clear_message(self):
        self.ids.message.text = ''

    def validate_input(self, username, password):
        return self.validate_username(username) and self.validate_password(password)

    def validate_username(self, username):
        valid = False
        if len(username) < 3:
            self.show_message('Nazwa konta powinna składać się z co najmniej 3 znaków.')
        else:
            valid = True
        return valid

    def validate_password(self, password):
        valid = False
        if len(password) < 5:
            self.show_message('Hasło powinno składać się z co najmniej 5 znaków.')
        else:
            valid = True
        return valid

    def check_in_database(self, username, password):
        db_manager = App.get_running_app().db_manager
        print('jeah')
        account = db_manager.get_account(username, password)
        print(account)
        if account == {}:
            account_id = account
        else:
            account_id = account['account_id']
        return account_id

    def clear_input_fields(self):
        self.clear_message()
        self.ids.username.text = ''
        self.ids.password.text = ''

    def show_message(self, message):
        self.ids.message.text = message

    def login(self, username_field, password_field):
        username = username_field.text
        password = password_field.text

        if self.validate_input(username, password):
            account_id = self.check_in_database(username, password)
            if account_id != {}:
                print('logged in')
                App.get_running_app().root.account_id = account_id
                App.get_running_app().root.current = 'menu_screen'
            else:
                self.show_message('Nieprawidłowa nazwa użytkownika lub hasło.')


class CustomDropdown(DropDown):
    pass


class CreateAccountScreen(Screen):

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def print_confirmation(self):
        self.show_message('Konto zostało utworzone')

    def clear_message(self):
        self.ids.message.text = ''

    def validate_input(self, username, password, email):
        return self.validate_username(username) \
               and self.validate_password(password) \
               and self.validate_email(email)

    def validate_username(self, username):
        valid = False
        if len(username) < 3:
            self.show_message('Nazwa konta powinna składać się z co najmniej 3 znaków.')
        else:
            valid = True
        return valid

    def validate_password(self, password):
        valid = False
        if len(password) < 5:
            self.show_message('Hasło powinno składać się z co najmniej 5 znaków.')
        else:
            valid = True
        return valid

    def validate_email(self, email):
        valid = False
        email_regex = re.compile(r'([a-zA-Z0-9_]+@[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+)')
        email_match = re.search(email_regex, email)
        if len(email) == 0:
            self.show_message('Pole "Adres e-mail" nie może być puste.')
        elif email_match is None or email_match.group(1) != email:
            self.show_message('Nieprawidłowy adres e-mail.')
        else:
            valid = True
        return valid

    def check_in_database(self, username, password, email):
        db_manager = App.get_running_app().db_manager
        print('jeah')
        account_id = db_manager.create_account(username, password, email)
        print(account_id)
        return account_id

    def clear_input_fields(self):
        self.clear_message()
        self.ids.username.text = ''
        self.ids.password.text = ''
        self.ids.email.text = ''

    def show_message(self, message):
        self.ids.message.text = message

    def create_account(self, username_field, password_field, email_field):
        username = username_field.text
        password = password_field.text
        email = email_field.text

        if self.validate_input(username, password, email):
            account_id = self.check_in_database(username, password, email)
            if account_id != {}:
                self.clear_input_fields()
                self.print_confirmation()
                print('account created')


class ExpensesListScreen(Screen):
    def on_pre_enter(self, *args):
        box = self.ids.box
        expenses_list = self.get_expenses_list()
        for expense in expenses_list:
            box.add_widget(SelectableLabel(text=f"{expense['expense_name']} - "
                                                f"{round(expense['amount'], 2)} zł - "
                                                f"{expense['operation_date'].strftime('%d.%m.%Y')}",
                                           label_id=expense['expense_id']))

    def on_pre_leave(self, *args):
        self.ids.box.clear_widgets()

    def get_expenses_list(self):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()
        print('Próbuję pobrać listę wydatków')
        expenses_list = db_manager.get_all_expenses(app.root.account_id)
        print(expenses_list)
        return expenses_list


class IncomesListScreen(Screen):
    def on_pre_enter(self, *args):
        box = self.ids.box
        incomes_list = self.get_incomes_list()
        for income in incomes_list:
            box.add_widget(SelectableLabel(text=f"{income['group_name']}: "
                                                f"{income['income_name']} - "
                                                f"{round(income['amount'], 2)} zł - "
                                                f"{income['operation_date'].strftime('%d.%m.%Y')}",
                                           label_id=income['income_id']))

    def on_pre_leave(self, *args):
        self.ids.box.clear_widgets()

    def get_incomes_list(self):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()
        print('Próbuję pobrać listę wpływów')
        incomes_list = db_manager.get_all_incomes(app.root.account_id)
        print(incomes_list)
        return incomes_list


class CreateGroupScreen(Screen):
    users_dropdowns = DictProperty({})
    highest_id = 0

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def add_user_field(self):
        self.highest_id += 1
        deletebtn = ButtonWithData(text='-', size_hint_x=0.25, id=f'delete{self.highest_id}')
        userbtn = ButtonWithData(button_data={'text': 'Wybierz', 'id': 0},
                                 size_hint_x=0.35, id=f'user{self.highest_id}')
        widgets = [userbtn,
                   FloatInput(text='', font_size=18, size_hint_x=0.30, id=f'amount{self.highest_id}'),
                   IntegerInput(text='', font_size=18, size_hint_x=0.10, id=f'priority{self.highest_id}'),
                   deletebtn]
        deletebtn.bind(on_release=lambda btn: self.remove_user_field(btn.id))

        for widget in widgets:
            self.ids.box.add_widget(widget)

        new_dropdown = DropDown()
        self.users_dropdowns[f'{self.highest_id}'] = new_dropdown
        self.populate_users_dropdown(str(self.highest_id))
        userbtn.bind(on_release=self.users_dropdowns[str(self.highest_id)].open)
        self.users_dropdowns[str(self.highest_id)].bind(
            on_select=lambda instance, x: setattr(userbtn, 'button_data', x))

    def remove_user_field(self, id):
        id_regex = re.compile(r'([0-9]+)')
        id_match = re.search(id_regex, id)

        names = ['user', 'amount', 'priority', 'delete']

        for i in range(len(names)):
            names[i] = names[i] + str(id_match.group(1))
        box = self.ids.box

        for child in box.children[:]:
            if child.id in names:
                box.remove_widget(child)

        self.users_dropdowns.pop(str(id_match.group(1)))

    def populate_users_dropdown(self, id):

        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()
        self.users_dropdowns[id].clear_widgets()
        users_list = db_manager.get_all_users(app.root.account_id)

        for user in users_list:
            btn = ButtonWithData(text=user['username'],
                                 size_hint_y=None,
                                 height='30',
                                 button_data={'text': user['username'], 'id': user['user_id']})
            btn.bind(on_release=lambda btn: self.users_dropdowns[id].select(btn.button_data))
            self.users_dropdowns[id].add_widget(btn)

    def clear_message(self):
        self.ids.message.text = ''

    def validate_input(self, name, description, settlement_percent, settlement_value):
        return self.validate_name(name) \
               and self.validate_description(description) \
               and self.validate_type(settlement_percent, settlement_value) \
               and self.validate_users_list(settlement_percent)

    def validate_name(self, name):
        valid = False
        if len(name) < 3:
            self.show_message('Nazwa grupy powinna składać się z co najmniej 3 znaków.')
        else:
            valid = True
        return valid

    def validate_description(self, description):
        valid = False
        if len(description) > 255:
            self.show_message('Opis nie powinien przekroczyć 255 znaków.')
        else:
            valid = True
        return valid

    def validate_type(self, settlement_percent, settlement_value):
        valid = False
        if settlement_percent.state == 'normal' and settlement_value.state == 'normal':
            self.show_message('Wybierz typ rozliczenia dla grupy.')
        elif settlement_percent.state == 'down' and settlement_value.state == 'down':
            self.show_message('Można wybrać tylko jeden typ rozliczenia.')
        else:
            valid = True
        return valid

    def validate_users_list(self, settlement_percent):
        valid = False
        all_users_valid = True
        number_of_users = 0
        users_list = []
        priority_list = []
        total_amount = 0
        box = self.ids.box

        for child in box.children[:]:
            if child.id is not None and 'user' in child.id:
                if self.validate_user(child, users_list):
                    users_list.append(child.button_data['id'])
                    number_of_users = number_of_users + 1
                else:
                    all_users_valid = False
                    break
            elif child.id is not None and 'amount' in child.id:
                if self.validate_amount(child):
                    total_amount = total_amount + float(child.text)
                else:
                    all_users_valid = False
                    break
            elif child.id is not None and 'priority' in child.id:
                if self.validate_priority(child, priority_list):
                    priority_list.append(int(child.text))
                else:
                    all_users_valid = False
                    break

        if not all_users_valid:
            pass
        elif number_of_users < 1:
            self.show_message('Nie można utworzyć pustej grupy.')
        elif settlement_percent.state == 'down' and total_amount != 100:
            self.show_message('Dla rozliczenia procentowego suma procent członków grupy musi wynosić 100.')

        else:
            valid = True
        return valid

    def validate_user(self, user, users_list):
        user_valid = False
        print(users_list)
        print('Validating user:', user.button_data)
        if user.button_data['id'] == 0:
            self.show_message('Uzupełnij dane wszystkich członków grupy.')
            print('user id', user.button_data['id'])
        elif user.button_data['id'] in users_list:
            self.show_message('Wykryto zduplikowaną wartość "Użytkownik".')
        else:
            user_valid = True
        return user_valid

    def validate_amount(self, amount):
        amount_valid = False
        if amount.text == '':
            self.show_message('Uzupełnij dane wszystkich członków grupy.')
            print('amount', amount.text)
        else:
            amount_valid = True
        return amount_valid

    def validate_priority(self, priority, priority_list):
        priority_valid = False
        if priority.text == '':
            self.show_message('Uzupełnij dane wszystkich członków grupy.')
            print('priority', priority.text)
        elif int(priority.text) in priority_list:
            self.show_message('Wykryto zduplikowaną wartość "priorytet".')
        else:
            priority_valid = True
        return priority_valid

    def check_in_database(self, name, description, settlement_percent):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()
        settlement_type_id = 1 if settlement_percent.state == 'down' else 2
        print('Próbuję dodać grupę')
        group_id = db_manager.create_group(app.root.account_id, name, description, settlement_type_id,
                                           is_main_group=False)
        print(app.root.account_id, name, description, settlement_type_id)
        print(group_id)

        # adding users to user_group_tbl
        box = self.ids.box
        child_id_regex = re.compile(r'([0-9])+')

        # collecting data

        data = {}

        for child in box.children:
            if child.id is None:
                pass
            elif 'user' in child.id:
                print('CHILD ID:', child.id)
                id = re.search(child_id_regex, child.id).group(1)
                if id in data:
                    data[id]['user'] = int(child.button_data['id'])
                else:
                    data[id] = {}
                    data[id]['user'] = int(child.button_data['id'])
            elif 'amount' in child.id:
                print('CHILD ID:', child.id)
                id = re.search(child_id_regex, child.id).group(1)
                if id in data:
                    data[id]['amount'] = int(child.text)
                else:
                    data[id] = {}
                    data[id]['amount'] = int(child.text)
            elif 'priority' in child.id:
                print('CHILD ID:', child.id)
                id = re.search(child_id_regex, child.id).group(1)
                if id in data:
                    data[id]['priority'] = int(child.text)
                else:
                    data[id] = {}
                    data[id]['priority'] = int(child.text)

        # adding users to group
        print('data:', data)
        for k, v in data.items():
            print(f'Próbuję dodać usera: {v["user"]} do grupy')
            db_manager.add_user_to_group(v['user'], group_id, v['amount'], v['priority'])

        return group_id

    def clear_input_fields(self):
        self.clear_message()
        self.ids.name.text = ''
        self.ids.description.text = ''
        self.ids.settlement_percent.state = 'down'
        self.ids.settlement_value.state = 'normal'
        self.highest_id = 0
        self.ids.box.clear_widgets()
        self.users_dropdowns = {}

    def show_message(self, message):
        self.ids.message.text = message

    def add_group(self, name_field, description_field, settlement_percent, settlement_value):
        name = name_field.text
        description = description_field.text

        if self.validate_input(name, description, settlement_percent, settlement_value):
            group_id = self.check_in_database(name, description, settlement_percent)
            if group_id != {}:
                print('group succesfully added')
                self.clear_input_fields()
                self.show_message(f'Grupa {name} została dodana.')
            else:
                self.show_message('Błąd, skontaktuj się z administratorem.')


class ExpenseDetailsScreen(Screen):
    expense = ObjectProperty(None)

    def on_pre_enter(self, *args):
        self.expense = self.check_in_database(App.get_running_app().root.label_id)
        self.populate_fields()

    def on_pre_leave(self, *args):
        self.clear_fields()

    def check_in_database(self, expense_id):
        db_manager = App.get_running_app().db_manager
        print('Próbuję wczytać wydatek')
        expense = db_manager.get_expense(expense_id)
        print(expense)
        return expense

    def populate_fields(self):
        self.ids.name.text = self.expense['expense_name']
        self.ids.date.text = self.expense['operation_date'].strftime('%d.%m.%Y')
        self.ids.description.text = self.expense['description']
        self.ids.payer.text = self.expense['username']
        self.ids.group.text = self.expense['group_name']
        self.ids.category.text = self.expense['category_name']
        self.ids.amount.text = str(round(self.expense['amount'], 2)) + ' zł'
        self.ids.payment_method.text = self.expense['payment_method_name']

    def clear_fields(self):
        self.ids.name.text = ''
        self.ids.date.text = ''
        self.ids.description.text = ''
        self.ids.payer.text = ''
        self.ids.group.text = ''
        self.ids.category.text = ''
        self.ids.amount.text = ''
        self.ids.payment_method.text = ''


class IncomeDetailsScreen(Screen):
    income = ObjectProperty(None)

    def on_pre_enter(self, *args):
        print(App.get_running_app().root.label_id)
        self.income = self.check_in_database(App.get_running_app().root.label_id)
        self.populate_fields()

    def on_pre_leave(self, *args):
        self.clear_fields()

    def check_in_database(self, income_id):
        db_manager = App.get_running_app().db_manager
        print(f'Próbuję wczytać przychód {income_id}')
        income = db_manager.get_income(income_id)
        print(income)
        return income

    def populate_fields(self):
        self.ids.name.text = self.income['income_name']
        self.ids.date.text = self.income['operation_date'].strftime('%d.%m.%Y')
        self.ids.description.text = self.income['description']
        self.ids.group.text = self.income['group_name']
        self.ids.category.text = self.income['category_name']
        self.ids.amount.text = str(round(self.income['amount'], 2)) + ' zł'

    def clear_fields(self):
        self.ids.name.text = ''
        self.ids.date.text = ''
        self.ids.description.text = ''
        self.ids.group.text = ''
        self.ids.category.text = ''
        self.ids.amount.text = ''


class CreateCategoryScreen(Screen):
    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def clear_message(self):
        self.ids.message.text = ''

    def validate_input(self, name, description, expense_category, income_category):
        return self.validate_name(name) \
               and self.validate_description(description) \
               and self.validate_type(expense_category, income_category)

    def validate_name(self, name):
        valid = False
        if len(name) < 3:
            self.show_message('Nazwa kategorii powinna składać się z co najmniej 3 znaków.')
        else:
            valid = True
        return valid

    def validate_description(self, description):
        valid = False
        if len(description) > 255:
            self.show_message('Opis nie powinien przekroczyć 255 znaków.')
        else:
            valid = True
        return valid

    def validate_type(self, expense_category, income_category):
        valid = False
        if expense_category.state == 'normal' and income_category.state == 'normal':
            self.show_message('Wybierz typ kategorii.')
        elif expense_category.state == 'down' and income_category.state == 'down':
            self.show_message('Można wybrać tylko jeden typ kategorii.')
        else:
            valid = True
        return valid

    def check_in_database(self, name, description, expense_category):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()
        category_type_id = 1 if expense_category.state == 'down' else 2
        print('Próbuję dodać kategorię')
        category_id = db_manager.create_category(app.root.account_id, name, description, category_type_id)
        print(app.root.account_id, name, description, category_type_id)
        print(category_id)
        return category_id

    def clear_input_fields(self):
        self.clear_message()
        self.ids.name.text = ''
        self.ids.description.text = ''
        self.ids.expense_category.state = 'down'
        self.ids.income_category.state = 'normal'

    def show_message(self, message):
        self.ids.message.text = message

    def add_category(self, name_field, description_field, expense_category, income_category):
        name = name_field.text
        description = description_field.text

        if self.validate_input(name, description, expense_category, income_category):
            category_id = self.check_in_database(name, description, expense_category)
            if category_id != {}:
                print('category succesfully added')
                self.clear_input_fields()
                self.show_message(f'Kategoria {name} została dodana.')
            else:
                self.show_message('Błąd, skontaktuj się z administratorem.')


class CreateUserScreen(Screen):
    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def clear_message(self):
        self.ids.message.text = ''

    def validate_input(self, name):
        return self.validate_name(name)

    def validate_name(self, name):
        valid = False
        if len(name) < 3:
            self.show_message('Nazwa użytkownika powinna składać się z co najmniej 3 znaków.')
        else:
            valid = True
        return valid

    def check_in_database(self, name):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()
        print('Próbuję dodać użytkownika')
        user_id = db_manager.create_user(app.root.account_id, name)
        print(app.root.account_id, name)
        print(user_id)
        return user_id

    def clear_input_fields(self):
        self.clear_message()
        self.ids.name.text = ''

    def show_message(self, message):
        self.ids.message.text = message

    def add_user(self, name_field):
        name = name_field.text

        if self.validate_input(name):
            user_id = self.check_in_database(name)
            if user_id != {}:
                print('user succesfully added')
                self.clear_input_fields()
                self.show_message(f'Użytkownik {name} został dodany.')
            else:
                self.show_message('Błąd, skontaktuj się z administratorem.')


class CreatePaymentMethodScreen(Screen):

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def clear_message(self):
        self.ids.message.text = ''

    def validate_input(self, name):
        return self.validate_name(name)

    def validate_name(self, name):
        valid = False
        if len(name) < 3:
            self.show_message('Nazwa metody płatności powinna składać się z co najmniej 3 znaków.')
        else:
            valid = True
        return valid

    def check_in_database(self, name):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()
        print('Próbuję dodać metodę płatności')
        payment_method_id = db_manager.create_payment_method(app.root.account_id, name)
        print(app.root.account_id, name)
        print(payment_method_id)
        return payment_method_id

    def clear_input_fields(self):
        self.clear_message()
        self.ids.name.text = ''

    def show_message(self, message):
        self.ids.message.text = message

    def add_payment_method(self, name_field):
        name = name_field.text

        if self.validate_input(name):
            payment_method_id = self.check_in_database(name)
            if payment_method_id != {}:
                print('payment method succesfully added')
                self.clear_input_fields()
                self.show_message(f'Metoda płatności {name} została dodana.')
            else:
                self.show_message('Błąd, skontaktuj się z administratorem.')


class IpAddressScreen(Screen):
    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def clear_message(self):
        self.ids.message.text = ''

    def validate_input(self, address):
        return self.validate_address(address)

    def validate_address(self, address):
        valid = False
        address_regex = re.compile(r'([0-9]+.[0-9]+.[0-9]+.[0-9]+)')
        address_match = re.search(address_regex, address)
        if address != 'localhost' and (address_match is None or address_match.group(1) != address):
            self.show_message('Błędny format adresu ip (przykładowy adres: 192.168.1.1).')
        else:
            valid = True
        return valid

    def check_in_database(self, address):
        db_manager = App.get_running_app().db_manager

        print(address)
        print('Próbuję dodać połączyć się z bazą')
        ConfigurationData.db_config['host'] = address
        connected = False
        try:
            connection_check = db_manager.connect_to_db()
            connected = connection_check.is_connected()
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            db_manager.close_connection()
        print(connected)

        return connected

    def clear_input_fields(self):
        self.clear_message()
        self.ids.address.text = ''

    def show_message(self, message):
        self.ids.message.text = message

    def check_connection(self, address_field):
        address = address_field.text
        app = App.get_running_app()

        if self.validate_input(address):
            connected = self.check_in_database(address)
            if connected:
                print('Successfully connected to the database')
                self.show_message(f'Połączono z adresem {address}.')
                app.root.change_screen()
            else:
                self.show_message('Błąd, skontaktuj się z administratorem.')


class SelectableLabel(Label):
    label_id = NumericProperty()

    def __init__(self, **kwargs):
        super(SelectableLabel, self).__init__(**kwargs)
        self.label_id = kwargs['label_id']

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            app = App.get_running_app()
            app.root.label_clicked(self.label_id)
            print('label id: ', self.label_id)


class ScrollableLabel(ScrollView):
    text = StringProperty('')


class MyApp(App):
    db_manager = DatabaseManager()

    def build(self):
        self.title = "Menedżer wydatków"
        return MyScreenManager()


if __name__ == "__main__":
    MyApp().run()

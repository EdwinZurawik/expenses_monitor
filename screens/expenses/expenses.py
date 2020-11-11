import datetime
import re

from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.dropdown import DropDown
from kivy.app import App

from main import ButtonWithData
from screens.gui_elements import SelectableListItem


class ExpensesListScreen(Screen):
    def on_pre_enter(self, *args):
        box = self.ids.box
        expenses_list = self.get_expenses_list()
        for expense in expenses_list:
            expense_str = "".join([f"{expense['operation_date'].strftime('%d.%m.%Y')} --- ",
                                   f"{round(expense['amount'], 2)} zł --- ",
                                   f"{expense['expense_name']} ",
                                   f"[{expense['category_name']}]"
                                   ])
            box.add_widget(SelectableListItem(text=expense_str,
                                              item_id=expense['expense_id']))

    def on_pre_leave(self, *args):
        self.ids.box.clear_widgets()

    def get_expenses_list(self):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()
        print('Próbuję pobrać listę wydatków')
        expenses_list = db_manager.get_all_expenses(app.root.account_id)
        print(expenses_list)
        return expenses_list


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
        self.expense = self.load_expense(App.get_running_app().root.item_id)
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
        self.clear_message()
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

            errors = self.check_in_database(name, date, description, amount)
            if errors is None:
                print('expense succesfully updated')
                self.show_message(f'Zmiany w {name} zostały zapisane.')
                self.expense = self.load_expense(self.expense['expense_id'])
            else:
                self.show_message('Błąd, skontaktuj się z administratorem.')


class ExpenseDetailsScreen(Screen):
    expense = ObjectProperty(None)

    def on_pre_enter(self, *args):
        self.expense = self.check_in_database(App.get_running_app().root.item_id)
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
        self.ids.payer.text = ' '.join(['Zapłacone przez:', self.expense['username']])
        self.ids.group.text =  ' '.join(['Grupa:', self.expense['group_name']])
        self.ids.category.text = ' '.join(['Kategoria:', self.expense['category_name']])
        self.ids.amount.text = ' '.join(['Kwota:', str(round(self.expense['amount'], 2)) + ' zł'])
        self.ids.payment_method.text = ' '.join(['Metoda płatności:', self.expense['payment_method_name']])

    def clear_fields(self):
        self.ids.name.text = ''
        self.ids.date.text = ''
        self.ids.description.text = ''
        self.ids.payer.text = ''
        self.ids.group.text = ''
        self.ids.category.text = ''
        self.ids.amount.text = ''
        self.ids.payment_method.text = ''

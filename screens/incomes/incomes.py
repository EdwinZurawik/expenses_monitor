import datetime
import re

from kivy.app import App
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import Screen

from main import ButtonWithData
from screens.gui_elements import SelectableListItem


class IncomesListScreen(Screen):
    def on_pre_enter(self, *args):
        box = self.ids.box
        incomes_list = self.get_incomes_list()
        for income in incomes_list:
            income_str = "".join([f"{income['group_name']}: ",
                                  f"{income['income_name']} - ",
                                  f"{round(income['amount'], 2)} zł - ",
                                  f"{income['operation_date'].strftime('%d.%m.%Y')}"
                                  ])
            box.add_widget(SelectableListItem(text=income_str,
                                              item_id=income['income_id']))

    def on_pre_leave(self, *args):
        self.ids.box.clear_widgets()

    def get_incomes_list(self):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()
        print('Próbuję pobrać listę wpływów')
        incomes_list = db_manager.get_all_incomes(app.root.account_id)
        print(incomes_list)
        return incomes_list


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


class EditIncomeScreen(Screen):
    income = ObjectProperty(None)
    group_id = NumericProperty(0)
    category_id = NumericProperty(0)
    groups_dropdown = DropDown()
    categories_dropdown = DropDown()

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def on_pre_enter(self, *args):
        self.income = self.load_income(App.get_running_app().root.item_id)
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
                                           amount, self.ids.categories_btn.button_data['id'],
                                           self.ids.groups_btn.button_data['id'])
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
        self.clear_message()
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
            errors = self.check_in_database(name, date, description, amount)
            if errors is None:
                print('income succesfully updated')
                self.show_message(f'Zmiany w {name} zostały zapisane.')
                self.income = self.load_income(self.income['income_id'])
            else:
                self.show_message('Błąd, skontaktuj się z administratorem.')


class IncomeDetailsScreen(Screen):
    income = ObjectProperty(None)

    def on_pre_enter(self, *args):
        print(App.get_running_app().root.item_id)
        self.income = self.check_in_database(App.get_running_app().root.item_id)
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
